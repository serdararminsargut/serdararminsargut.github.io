(() => {
  const button = document.getElementById("comp-card-pdf-download");
  if (!button) return;

  const lang = (document.documentElement.lang || "tr").toLowerCase().split("-")[0];
  const supported = ["tr", "en", "ar", "ru"];
  const activeLang = supported.includes(lang) ? lang : "tr";
  const code = activeLang.toUpperCase();

  const sourceUrl = `/downloads/Serdar-Armin-Sargut-Comp-Card-${code}.pdf`;
  const fileName = `Serdar-Armin-Sargut-Comp-Card-${code}.pdf`;

  const copy = {
    tr: { preparing: "PDF hazırlanıyor…", error: "PDF indirilemedi. Lütfen tekrar deneyin." },
    en: { preparing: "Preparing download…", error: "The PDF could not be downloaded. Please try again." },
    ar: { preparing: "جارٍ تجهيز ملف PDF…", error: "تعذر تنزيل ملف PDF. يرجى المحاولة مرة أخرى." },
    ru: { preparing: "Подготовка PDF…", error: "Не удалось скачать PDF. Пожалуйста, попробуйте ещё раз." }
  }[activeLang];

  // The page language is authoritative: never reuse a PDF URL from another language.
  button.dataset.downloadUrl = sourceUrl;
  button.dataset.filename = fileName;
  const originalLabel = button.textContent.trim();

  button.addEventListener("click", async () => {
    if (button.dataset.busy === "true") return;

    button.dataset.busy = "true";
    button.disabled = true;
    button.setAttribute("aria-busy", "true");
    button.textContent = copy.preparing;

    try {
      const response = await fetch(sourceUrl, { cache: "no-store", credentials: "same-origin" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const source = await response.blob();
      const downloadBlob = new Blob([source], { type: "application/pdf" });
      const objectUrl = URL.createObjectURL(downloadBlob);
      const link = document.createElement("a");

      link.href = objectUrl;
      link.download = fileName;
      link.style.display = "none";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.setTimeout(() => URL.revokeObjectURL(objectUrl), 1500);
    } catch (error) {
      console.error("Comp Card PDF download failed:", error);
      window.alert(copy.error);
    } finally {
      button.dataset.busy = "false";
      button.disabled = false;
      button.removeAttribute("aria-busy");
      button.textContent = originalLabel;
    }
  });
})();
