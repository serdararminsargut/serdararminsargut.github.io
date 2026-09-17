(() => {
  const button = document.getElementById("comp-card-pdf-download");
  if (!button) return;

  const fileName = button.dataset.filename || "Serdar-Armin-Sargut-Comp-Card-EN-AR.pdf";
  const sourceUrl = button.dataset.downloadUrl;
  const originalLabel = button.textContent.trim();

  button.addEventListener("click", async () => {
    if (button.dataset.busy === "true" || !sourceUrl) return;

    button.dataset.busy = "true";
    button.disabled = true;
    button.setAttribute("aria-busy", "true");
    button.textContent = "Preparing download…";

    try {
      const response = await fetch(sourceUrl, { cache: "no-store", credentials: "same-origin" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const source = await response.blob();
      const downloadBlob = new Blob([source], { type: "application/octet-stream" });
      const objectUrl = URL.createObjectURL(downloadBlob);
      const link = document.createElement("a");

      link.href = objectUrl;
      link.download = fileName;
      link.style.display = "none";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
    } catch (error) {
      console.error("Comp Card PDF download failed:", error);
      window.alert("The PDF could not be downloaded. Please try again.");
    } finally {
      button.dataset.busy = "false";
      button.disabled = false;
      button.removeAttribute("aria-busy");
      button.textContent = originalLabel;
    }
  });
})();
