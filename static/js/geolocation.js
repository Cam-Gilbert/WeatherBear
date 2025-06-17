/** 
 * Code to get users locations from browser
 */ 
window.addEventListener("DOMContentLoaded", () => {
  const statusText = document.getElementById("geo-status");
  const latitudeInput = document.getElementById("latitude");
  const longitudeInput = document.getElementById("longitude");
  const manualInputDiv = document.getElementById("manual-location");

  if ("geolocation" in navigator) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;

        // Fill hidden inputs
        latitudeInput.value = latitude;
        longitudeInput.value = longitude;

        // Hide manual input
        manualInputDiv.style.display = "none";

        // Update status
        statusText.textContent = "Location auto-detected!";
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