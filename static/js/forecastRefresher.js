/** Import the fetchAndRenderForecast method from forecastRender. Used to fetch the current forecast and render the forecase panels */
import { fetchAndRenderForecast } from "./forecastRender.js";

/**
 * Handles listening for the main form being filled out, upon submission this script catches the data from the form and passes it into
 * the fetch and render forecast method that gets forecast data using the params from the form and renders forecast panels
 */
document.addEventListener("DOMContentLoaded", function () {
  
  // select important form elements
  const form = document.getElementById("location-form");
  const locationInput = document.getElementById("location");
  const expertiseInput = document.getElementById("expertise");
  const unitsInput = document.getElementById("units");
  const latInput = document.getElementById("latitude");
  const lonInput = document.getElementById("longitude");

  // if the form successfully loaded, have a submit listner
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault(); // dont reload the page

      // grab important input data and pass to the fetchAndRenderForecast function
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
