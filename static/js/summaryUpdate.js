import { fetchAndRenderForecast } from "./forecastRender.js";

let fullAfdText = "";
let currentExpertiseLevel = "";

window.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("location-form");
  const summaryPanel = document.querySelector(".summary-panel");
  const summaryText = document.getElementById("summary-text");
  const submitButton = form.querySelector("button[type='submit']");
  const locationInput = document.getElementById("location");
  const unitsInput = document.getElementById("units");
  const latInput = document.getElementById("latitude");
  const lonInput = document.getElementById("longitude");

  // Create a spinner
  const spinner = document.createElement("img");
  spinner.src = "/static/assets/tornado_loading.gif";
  spinner.alt = "Loading...";
  spinner.className = "w-8 h-8 mx-auto mt-4";
  spinner.style.display = "none";
  form.appendChild(spinner);

  let lastSubmitTime = 0;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const now = Date.now();
    if (now - lastSubmitTime < 30000) {
      alert("Please wait at least 30 seconds before submitting again.");
      return;
    }
    lastSubmitTime = now;

    const forecastData = {
        location: locationInput.value,
        units: unitsInput?.value || "imperial",
        latitude: locationInput.value && locationInput.value.trim() !== "" ? "" : latInput?.value,
        longitude: locationInput.value && locationInput.value.trim() !== "" ? "" : lonInput?.value
    };

    fetchAndRenderForecast(forecastData);

    const formData = new FormData(form);

    // Show spinner and disable button
    spinner.style.display = "block";
    submitButton.disabled = true;
    submitButton.textContent = "Loading...";

    try {
      const response = await fetch("/get-summary", {
        method: "POST",
        body: formData
      });

      const data = await response.json();

      // Animate form shrinking and moving upward
      form.classList.add("opacity-80", "scale-95", "-translate-y-4");

      // Capture afd and expertise vals from frontend
      fullAfdText = data.afd;
      currentExpertiseLevel = document.getElementById("expertise").value;

      // Show summary
      summaryText.textContent = data.summary;
      summaryPanel.classList.remove("hidden");

      if (!document.getElementById("explain-toggle")) {
        const toggle = document.createElement("div");
        toggle.id = "explain-toggle";
        toggle.className = "mt-2 text-sm text-blue-600 cursor-pointer hover:underline";
        toggle.textContent = "💡 Confused? Click here and select text for an explanation.";
        summaryPanel.appendChild(toggle);
      }

    } catch (error) {
      console.error("Summary fetch error:", error);
    } finally {
      spinner.style.display = "none";
      submitButton.disabled = false;
      submitButton.textContent = "Get Forecast";
    }
  });
});


// Logic for additional explanation feature
let explanationEnabled = false;

document.addEventListener("click", (event) => {
  const toggle = event.target.closest("#explain-toggle");
  if (toggle) {
    explanationEnabled = !explanationEnabled;
    toggle.textContent = explanationEnabled
      ? "🟢 Explanation mode enabled. Select text to get help (click to disable)."
      : "💡 Confused? Click here and select text for more information.";
  }
});

document.addEventListener("mouseup", async (event) => {
  if (!explanationEnabled) return;

  const selection = window.getSelection();
  const selectedText = selection.toString().trim();
  const summaryText = document.getElementById("summary-text");

  if (selectedText && summaryText.contains(selection.anchorNode)) {
    const rect = selection.getRangeAt(0).getBoundingClientRect();

    // Remove any existing popup
    const oldPopup = document.getElementById("explanation-popup");
    if (oldPopup) oldPopup.remove();

    // Create popup
    const popup = document.createElement("div");
    popup.id = "explanation-popup";
    popup.className =
      "absolute z-50 bg-white text-sm text-gray-800 border border-gray-300 rounded-xl shadow-lg p-2 max-w-xs";
    popup.style.top = `${rect.bottom + window.scrollY + 5}px`;
    popup.style.left = `${rect.left + window.scrollX}px`;
    popup.textContent = "Loading explanation...";

    document.body.appendChild(popup);

    try {
      const response = await fetch("/explain-text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: selectedText,
          summary: summaryText.textContent,
          afd: fullAfdText,
          expertise: currentExpertiseLevel
        })
      });

      const data = await response.json();
      popup.textContent = data.explanation || "No explanation found.";
    } catch (error) {
      console.error("Error fetching explanation:", error);
      popup.textContent = "Error getting explanation.";
    }

    // Remove the popup when clicking outside
    const handleClickOutside = (e) => {
      if (!popup.contains(e.target)) {
        popup.remove();
        document.removeEventListener("mousedown", handleClickOutside);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
  }
});
