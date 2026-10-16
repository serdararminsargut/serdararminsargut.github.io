(() => {
  const button = document.getElementById("comp-card-pdf-download");
  if (!button) return;

  const lang = (document.documentElement.lang || "tr").toLowerCase().split("-")[0];
  const supported = ["tr", "en", "ar", "ru"];
  const activeLang = supported.includes(lang) ? lang : "tr";
  const code = activeLang.toUpperCase();
  const sourceUrl = `/downloads/Serdar-Armin-Sargut-Comp-Card-${code}.pdf`;
  const fileName = `Serdar-Armin-Sargut-Comp-Card-${code}.pdf`;

  // Keep the page language authoritative and use a real same-origin PDF URL.
  // Direct navigation is more reliable on Android Chrome/WebView than
  // fetch -> Blob -> object URL -> synthetic click.
  button.dataset.downloadUrl = sourceUrl;
  button.dataset.filename = fileName;

  // A single direct navigation lets Android Chrome open/save the real PDF.
  // Do not combine a synthetic download click and a delayed second request:
  // that sequence triggers Chrome's "multiple file downloads" permission.
  button.addEventListener("click", () => {
    if (button.disabled) return;
    button.disabled = true;
    window.location.assign(sourceUrl);
  });
})();
