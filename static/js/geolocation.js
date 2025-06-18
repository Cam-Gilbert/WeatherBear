/** 
 * Code to get users locations from browser
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

        // Fill hidden inputs
        latitudeInput.value = latitude;
        longitudeInput.value = longitude;

        // Remove required attribute from manual input (since it's now optional)
        locationInput.removeAttribute("required");

        // (Optional) Try to reverse geocode to fill in the city name
        try {
          const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`);
          const data = await response.json();
          const city = data.address.city || data.address.town || data.address.village || data.address.state || '';
          locationInput.value = city;
        } catch (error) {
          console.warn("Reverse geocoding failed:", error.message);
        }

        // Update status
        statusText.textContent = "Location auto-detected! You may edit it if needed.";
      },
      (error) => {
        statusText.textContent = "Unable to auto-detect location. Please enter manually.";
        console.warn("Geolocation error:", error.message);
      }
    );
  } else {
    statusText.textContent = "Geolocation not supported. Please enter location manually.";
  }
});
