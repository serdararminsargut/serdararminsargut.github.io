(() => {
  const link = document.getElementById("pdf-download");
  const status = document.getElementById("download-status");
  const fileName = "Serdar-Armin-Sargut-Comp-Card-EN-AR.pdf";

  if (!link || !status) return;

  link.addEventListener("click", async (event) => {
    event.preventDefault();
    if (link.dataset.busy === "true") return;

    link.dataset.busy = "true";
    link.setAttribute("aria-busy", "true");
    link.textContent = "PDF hazırlanıyor…";
    status.textContent = "Dosya indirilmeye hazırlanıyor.";

    try {
      const response = await fetch(link.href, { cache: "no-store", credentials: "same-origin" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const source = await response.blob();
      const downloadBlob = new Blob([source], { type: "application/octet-stream" });
      const objectUrl = URL.createObjectURL(downloadBlob);
      const trigger = document.createElement("a");

      trigger.href = objectUrl;
      trigger.download = fileName;
      trigger.style.display = "none";
      document.body.appendChild(trigger);
      trigger.click();
      trigger.remove();
      window.setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);

      status.textContent = "İndirme isteği gönderildi. Dosya İndirilenler klasörüne kaydedilmelidir.";
    } catch (error) {
      status.textContent = "İndirme başlatılamadı. Lütfen sayfayı yenileyip tekrar deneyin.";
      console.error("Comp Card PDF download failed:", error);
    } finally {
      link.dataset.busy = "false";
      link.removeAttribute("aria-busy");
      link.textContent = "PDF İndir";
    }
  });
})();
