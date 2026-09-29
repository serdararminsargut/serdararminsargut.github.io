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

  button.addEventListener("click", () => {
    const link = document.createElement("a");
    link.href = sourceUrl;
    link.download = fileName;
    link.rel = "noopener";
    document.body.appendChild(link);
    link.click();
    link.remove();

    // Android/WebView may ignore the download attribute. If the document
    // remains visible, navigate to the PDF so the browser can open/save it.
    window.setTimeout(() => {
      if (document.visibilityState === "visible") {
        window.location.assign(sourceUrl);
      }
    }, 350);
  });
})();
