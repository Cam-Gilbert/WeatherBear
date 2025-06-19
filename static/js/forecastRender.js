export function fetchAndRenderForecast(payload) {
  console.log("fetch initiated with data:", payload);
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

      const unit = payload.units === "metric" ? "C" : "F";

      // Current Conditions
      document.querySelector(".current-panel").innerHTML = `
        <h2 class="text-xl font-bold mb-2">Current Conditions</h2>
        <div class="flex items-center gap-4">
          <img src="${data.current.icon}" alt="weather icon" class="w-16 h-16">
          <div>
            <p class="text-4xl font-semibold">${data.current.temperature}°${unit}</p>
            <p>${data.current.clouds}</p>
          </div>
        </div>
        <p class="mt-2">Dewpoint: ${data.current.dewpoint}°${unit}</p>
        ${data.current.windChill ? `<p>Feels Like: ${data.current.windChill}°${unit}</p>` : ""}
        ${data.current.heatIndex ? `<p>Heat Index: ${data.current.heatIndex}°${unit}</p>` : ""}
        <p class="text-sm text-gray-500 mt-2">${data.current.station}</p>
      `;

      // Shared rendering function for forecast periods
      const formatPeriod = (period) => `
        <h3 class="text-xl font-bold mb-2">${period.title}</h3>
        <div class="flex items-center gap-4">
          <img src="${period.icon}" alt="forecast icon" class="w-16 h-16">
          <div>
            <p class="text-4xl font-semibold">${period.temperature}°${unit}</p>
            <p>${period.text}</p>
          </div>
        </div>
        <p class="text-sm text-gray-500 mt-2">Wind: ${period.wind_speed} ${period.wind_dir}</p>
        <p class="text-sm text-gray-500">Precipitation Chances: ${period.precip_chance}%</p>
      `;

      document.querySelector(".firstPeriod-panel").innerHTML = formatPeriod(data.first_period);
      document.querySelector(".secondPeriod-panel").innerHTML = formatPeriod(data.second_period);
      document.querySelector(".thirdPeriod-panel").innerHTML = formatPeriod(data.third_period);
    })
    .catch(err => console.error("Fetch Error:", err));
}
