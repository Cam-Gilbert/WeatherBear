import { fetchAndRenderForecast } from "./forecastRender.js";

function showErrorMessage(msg) {
  const errorBox = document.getElementById("error-box");
  if (errorBox) {
    errorBox.textContent = msg;
    errorBox.style.display = "block";
  }
}

function clearErrorMessage() {
  const errorBox = document.getElementById("error-box");
  if (errorBox) {
    errorBox.textContent = "";
    errorBox.style.display = "none";
  }
}

async function handleTextExplanation() {
  if (!explanationEnabled) return;

  const selection = window.getSelection();
  const selectedText = selection.toString().trim();
  const summaryText = document.getElementById("summary-text");

  if (selectedText && summaryText.contains(selection.anchorNode)) {
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

    const handleClickOutside = (e) => {
      if (!popup.contains(e.target)) {
        popup.remove();
        document.removeEventListener("mousedown", handleClickOutside);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
  }
}


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
    if (now - lastSubmitTime < 15000) {
      alert("Please wait at least 15 seconds before submitting again.");
      return;
    }
    lastSubmitTime = now;

    if (locationInput.value && locationInput.value.trim() !== "") {
      // User typed a location → clear lat/lon so they aren't accidentally submitted
      latInput.value = "";
      lonInput.value = "";
    } else if (!latInput.value || !lonInput.value) {
      // User didn’t type a location AND geolocation didn’t populate
      showErrorMessage("No location provided");
      return;
    }

    const forecastData = {
      location: locationInput.value,
      units: unitsInput?.value || "imperial",
      latitude: latInput?.value,
      longitude: lonInput?.value
    };

    spinner.style.display = "block";
    submitButton.disabled = true;
    submitButton.textContent = "Loading...";

    // wait for a success or failed return val from fetchAndRenderForecast
    const forecastSuccess = await fetchAndRenderForecast(forecastData);
    if (!forecastSuccess) {
      // Don't try to get summary if forecast failed
      spinner.style.display = "none";
      submitButton.disabled = false;
      submitButton.textContent = "Get Forecast";
      return;
    }

    const formData = new FormData();
    formData.append("location", forecastData.location);
    formData.append("latitude", forecastData.latitude);
    formData.append("longitude", forecastData.longitude);
    formData.append("units", forecastData.units);
    formData.append("expertise", document.getElementById("expertise").value);

    // Show spinner and disable button
    spinner.style.display = "block";
    submitButton.disabled = true;
    submitButton.textContent = "Loading...";

    try {
      const response = await fetch("/get-summary", {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        // Get error as text and attempt to parse
        const errorText = await response.text();
        try {
          const errorJson = JSON.parse(errorText);
          showErrorMessage(errorJson.error || "Something went wrong.");
        } catch {
          showErrorMessage("Unexpected response from server.");
        }
        return;
      }

      clearErrorMessage(); // Clear any prior error
      const data = await response.json();

      // Animate form shrinking and moving upward
      form.classList.add("opacity-80", "scale-95", "-translate-y-4");

      // Capture afd and expertise vals from frontend
      fullAfdText = data.afd;
      currentExpertiseLevel = document.getElementById("expertise").value;

      // Show summary
      summaryText.textContent = data.summary;
      summaryPanel.classList.remove("hidden");

      // reset explain toggle
      const explainToggle = document.getElementById("explain-toggle");
      if (explainToggle) explainToggle.checked = false;
      explanationEnabled = false;

      document.addEventListener("change", (event) => {
        if (event.target.id === "explain-toggle") {
          explanationEnabled = event.target.checked;
        }
      });

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

document.addEventListener("mouseup", handleTextExplanation);
document.addEventListener("selectionchange", () => {
  if (!explanationEnabled) return;

  // Delay to allow selection to finish
  clearTimeout(window.__explanationDelay);
  window.__explanationDelay = setTimeout(() => {
    const summaryText = document.getElementById("summary-text");
    const selection = window.getSelection();
    if (
      selection &&
      selection.toString().trim().length > 0 &&
      summaryText.contains(selection.anchorNode)
    ) {
      handleTextExplanation();
    }
  }, 300);
});