import { fetchAndRenderForecast } from "./forecastRender.js";

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

      // Show summary
      summaryText.textContent = data.summary;
      summaryPanel.classList.remove("hidden");

    } catch (error) {
      console.error("Summary fetch error:", error);
    } finally {
      spinner.style.display = "none";
      submitButton.disabled = false;
      submitButton.textContent = "Get Forecast";
    }
  });
});
