/** Import the fetchAndRenderForecast method from forecastRender. Used to fetch the current forecast and render the forecase panels */
import { fetchAndRenderForecast } from "./forecastRender.js";

/** 
 * Code to attempt to get users locations from browser. If it is allowed the site will not wait for form submission and grab forecast data
 * using the location provided. 
 */ 
window.addEventListener("DOMContentLoaded", () => {
  const statusText = document.getElementById("geo-status");
  const latitudeInput = document.getElementById("latitude");
  const longitudeInput = document.getElementById("longitude");
  const locationInput = document.getElementById("location");

  if ("geolocation" in navigator) {
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;

        // hidden inputs
        latitudeInput.value = latitude;
        longitudeInput.value = longitude;

        //remove required attribute from manual input (since it's now optional)
        locationInput.removeAttribute("required");

        let city = ""

        // See if we can grab the city name if possible for most simple nws api interactions
        try {
          const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`);
          const data = await response.json();
          const city = data.address.city || data.address.town || data.address.village || data.address.state || '';
          locationInput.value = city;
        } catch (error) {
          console.warn("city finding failed:", error.message);
        }

        // update page
        statusText.textContent = "Location auto-detected! You may edit it if needed.";

        const data = {
          location: city,
          latitude: latitude,
          longitude: longitude,
          units: "imperial"
        }
        // fetch forecast data and render the forecast panels on the webpage now that we have the users location
        fetchAndRenderForecast(data)
      },
      (error) => {
        statusText.textContent = "Unable to detect location. Please enter manually.";
        console.warn("Geolocation error:", error.message);
      }
    );
  } else {
    statusText.textContent = "Not able to get geolocation. Please enter location manually.";
  }
});
