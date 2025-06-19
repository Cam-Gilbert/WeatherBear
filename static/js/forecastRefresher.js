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

      const payload = {
        location: locationInput.value,
        expertise: expertiseInput?.value || "intermediate",
        units: unitsInput?.value || "imperial",
        latitude: latInput?.value,
        longitude: lonInput?.value
      };

      fetch("/get-forecast", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          console.error("Forecast Error:", data.error);
          return;
        }

        // Need to design panels in this section.
        document.querySelector(".summary-panel").innerHTML = `
          <h2 class="text-xl font-semibold mb-4">Forecast Summary</h2>
          <p class="mb-4">${data.summary.text}</p>
        `;

        document.querySelector(".current-panel").innerHTML = `
          <h3 class="text-lg font-semibold mb-2">Current Conditions</h3>
          <p>${data.current.temperature}° ${payload.units === "metric" ? "C" : "F"}</p>
          <p>${data.current.conditions}</p>
        `;

        document.querySelector(".tonight-panel").innerHTML = `
          <h3 class="text-lg font-semibold mb-2">Tonight</h3>
          <p>${data.tonight.text}</p>
        `;

        document.querySelector(".tomorrow-panel").innerHTML = `
          <h3 class="text-lg font-semibold mb-2">Tomorrow</h3>
          <p>${data.tomorrow.text}</p>
        `;
      })
      .catch(err => console.error("Fetch Error:", err));
    });
  }
});
