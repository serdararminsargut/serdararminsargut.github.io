#!/usr/bin/env python3
"""Fail-closed tests for the isolated, no-deploy HugoBlox release handoff."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

mod_path=Path(__file__).with_name('verify_frozen_release_handoff.py')
spec=importlib.util.spec_from_file_location('handoff',mod_path)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestHandoff(unittest.TestCase):
    def test_safe_paths(self):
        for good in ('index.html','rehber/index.html','comp-card/ur/file.pdf'):
            self.assertTrue(mod.path_safe(good),good)
        for bad in ('../index.html','rehber/../../secret','/etc/passwd',
                    r'C:\Windows\example','./index.html','foo\\bar',''):
            self.assertFalse(mod.path_safe(bad),bad)
    def test_fail_closed(self):
        with self.assertRaises(AssertionError): mod.ensure(False,'forced')
    def test_manifest_fails_on_staging_publish_authorization(self):
        for project in ('SERDAR','DURU'):
            cfg=mod.CONFIG[project]
            original={'project':project,'cloudflare_project':cfg['project'],
                      'site':cfg['site'],'kind':'IMMUTABLE_OFFLINE_RELEASE_EVIDENCE_NOT_DEPLOYED',
                      'production_publish_authorized':True,'production_published':False,
                      'file_count':cfg['files'],'files':[],'old_files_preserved':cfg['old_files'],
                      'merged_sitemap_urls':cfg['urls'],'new_rehber_pages':5,
                      'archive_sha256':'0'*64,'archive':'bundle.tar.gz','staging_commit':'1'*40}
            with self.assertRaisesRegex(AssertionError,'NO_GO'):
                mod.validate_manifest(original,project)
    def test_release_paths_are_distinct(self):
        serdar=set(mod.release_paths('SERDAR')); duru=set(mod.release_paths('DURU'))
        self.assertEqual(len(serdar),5)
        self.assertEqual(len(duru),5)
        self.assertEqual(2,len(serdar & duru))
        self.assertTrue(all(x.startswith('rehber/') for x in serdar|duru))

if __name__=='__main__':unittest.main()