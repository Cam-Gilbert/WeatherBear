// explainer.js
export function enableExplanation({ containerSelector, getContextData, toggleSelector = "#explain-toggle" }) {
  let explanationEnabled = false;
  let mouseUpTimeout = null;

  const toggleEl = document.querySelector(toggleSelector);

  if (toggleEl) {
    toggleEl.addEventListener("click", () => {
      explanationEnabled = toggleEl.checked || !explanationEnabled;
      toggleEl.nextElementSibling.textContent = explanationEnabled
        ? "🟢 Explanation mode enabled. Select text to get an explanation (click to disable)."
        : "Enable explanation mode and select a portion of text for an in-depth explanation";
    });
  }

  async function handleTextExplanation() {
    if (!explanationEnabled) return;

    const selection = window.getSelection();
    const selectedText = selection.toString().trim();
    const container = document.querySelector(containerSelector);

    if (selectedText && container.contains(selection.anchorNode)) {
      const rect = selection.getRangeAt(0).getBoundingClientRect();

      const oldPopup = document.getElementById("explanation-popup");
      if (oldPopup) oldPopup.remove();

      const popup = document.createElement("div");
      popup.id = "explanation-popup";
      popup.className =
        "absolute z-50 bg-white text-sm text-gray-800 border border-gray-300 rounded-xl shadow-lg p-2 max-w-xs";
      popup.style.top = `${rect.bottom + window.scrollY + 5}px`;
      popup.style.left = `${rect.left + window.scrollX}px`;
      popup.textContent = "Loading explanation...";
      document.body.appendChild(popup);

      const context = getContextData();

      try {
        const response = await fetch("/explain-text", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text: selectedText,
            summary: context.summary,
            afd: context.afd,
            expertise: context.expertise
          })
        });

        const data = await response.json();
        popup.textContent = data.explanation || "No explanation found.";
      } catch (error) {
        console.error("Error fetching explanation:", error);
        popup.textContent = "Error getting explanation.";
      }

      const handleClickOutside = (e) => {
        if (!popup.contains(e.target)) {
          popup.remove();
          document.removeEventListener("mousedown", handleClickOutside);
        }
      };
      document.addEventListener("mousedown", handleClickOutside);
    }
  }

  document.addEventListener("mouseup", () => {
    if (!explanationEnabled) return;

    // the goal of this section is to allow for smooth selection, I worry that the event is getting triggered halfway thru selections
    clearTimeout(mouseUpTimeout);
    mouseUpTimeout = setTimeout(() => {
        const container = document.querySelector(containerSelector);
        const selection = window.getSelection();
        const selectedText = selection.toString().trim();

        if (
        selectedText &&
        selectedText.length > 0 &&
        container.contains(selection.anchorNode)
        ) {
        handleTextExplanation();
        }
    }, 400); // delay for user to complete selection
  });
  document.addEventListener("selectionchange", () => {
    if (!explanationEnabled) return;

      clearTimeout(window.__explanationDelay);

      window.__explanationDelay = setTimeout(() => {
        const container = document.querySelector(containerSelector);
        const selection = window.getSelection();
        if (
          selection &&
          selection.toString().trim().length > 0 &&
          container.contains(selection.anchorNode)
        ) {
        handleTextExplanation();
      }
    }, 1000); // longer delay for mobile drag 
  });
}
