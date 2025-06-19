import { fetchAndRenderForecast } from "./forecastRender.js";

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("location-form");
  const locationInput = document.getElementById("location");
  const expertiseInput = document.getElementById("expertise");
  const unitsInput = document.getElementById("units");
  const latInput = document.getElementById("latitude");
  const lonInput = document.getElementById("longitude");

  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      const data = {
        location: locationInput.value,
        units: unitsInput?.value || "imperial",
        latitude: latInput?.value,
        longitude: lonInput?.value
      };

      fetchAndRenderForecast(data);
    })
  }
});
