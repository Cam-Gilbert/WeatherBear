
const hourlyData = {
  first: [],
  second: [],
  third: []
};

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

      // Clear old alerts
      const alertsContainer = document.getElementById("alerts_container");
      alertsContainer.innerHTML = "";

      if (data.alerts && data.alerts.length > 0) {
        data.alerts.forEach((alert, index) => {
          const alertBox = document.createElement("div");
          alertBox.className = "w-full bg-red-500 text-white px-3 rounded-md shadow-lg cursor-pointer transition-all duration-300 hover:bg-red-700 hover:shadow-xl mb-2";

          alertBox.innerHTML = `
            <div class="font-bold text-md">${alert.headline}</div>
            <div id="alert-detail-${index}" class="hidden mt-2 space-y-2 text-sm">
              <div>${alert.description}</div>
              <div>${alert.instruction}</div>
            </div>
          `;

          alertBox.addEventListener("click", () => {
            const detail = document.getElementById(`alert-detail-${index}`);
            detail.classList.toggle("hidden");
          });

          alertsContainer.appendChild(alertBox);
        });
      }

      // Current Conditions
      document.querySelector(".current-panel").innerHTML = `
        <h2 class="text-xl font-bold mb-2">Current Conditions</h2>
        <div class="flex items-center gap-4">
          <img src="${data.current.icon}" alt="weather icon" class="w-16 h-16">
          <div>
            <p class="text-4xl font-semibold">${data.current.temperature}°${unit}</p>
            <p>${data.current.clouds}</p>
            <p>${data.current.text}</p>
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

      // Re-add the chart containers after wiping them out
      document.querySelector(".firstPeriod-panel").insertAdjacentHTML("beforeend", `
        <div id="first-chart-container" class="hidden mt-4">
          <canvas id="first-chart" class="w-full h-64"></canvas>
        </div>
      `);

      document.querySelector(".secondPeriod-panel").insertAdjacentHTML("beforeend", `
        <div id="second-chart-container" class="hidden mt-4">
          <canvas id="second-chart" class="w-full h-64"></canvas>
        </div>
      `);

      document.querySelector(".thirdPeriod-panel").insertAdjacentHTML("beforeend", `
        <div id="third-chart-container" class="hidden mt-4">
          <canvas id="third-chart" class="w-full h-64"></canvas>
        </div>
      `);

      // save hourly data to global list so chart function can see it
      hourlyData.first = data.first_period.hourly_forecast;
      hourlyData.second = data.second_period.hourly_forecast;
      hourlyData.third = data.third_period.hourly_forecast;
    })
    .catch(err => console.error("Fetch Error:", err));
}


export function toggleChart(id, variable) {
  const container = document.getElementById(`${id}-chart-container`);
  container.classList.toggle("hidden");

  if (container.dataset.rendered) {
    return;
  }

  let plot_color;

  if (variable === "temperature") {
    plot_color = "#c10007";
  } else if (variable === "probabilityOfPrecipitation") {
    plot_color = "#155dfc";
  } else if (variable === "relativeHumidity") {
    plot_color = "#008236";
  } else if (variable === "windSpeed") {
    plot_color = "#9f2d00";
  } else if (variable === "dewpoint") {
    plot_color = "#004f3b";
  } else {
    plot_color = "#3b82f6";
  }

  const hourly = hourlyData[id]
  if (!hourly || hourly.length === 0) return;

  const labels = hourly.map(h => new Date(h.startTime).toLocaleTimeString([], {hour: 'numeric'}));
  const values = hourly.map(h => h[variable]);

  console.log(`Rendering chart for ${id}`, { labels, values });
  const ctx = document.getElementById(`${id}-chart`).getContext("2d");
  new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: variable.charAt(0).toUpperCase() + variable.slice(1),
        data: values,
        borderColor: plot_color,
        tension: 0.4,
        fill: true,
        pointRadius: 3,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          labels: {
            color: "#1f2937", // text-gray-800
            font: {
              size: 14,
              family: "'Inter', sans-serif", // match Tailwind body
              weight: "600"
            }
          }
        },
        tooltip: {
          backgroundColor: "#1f2937", // dark gray
          titleColor: "#fff",
          bodyColor: "#d1d5db", // gray-300
          borderColor: "#3b82f6",
          borderWidth: 1,
          titleFont: {
            family: "'Inter', sans-serif",
            weight: "700"
          },
          bodyFont: {
            family: "'Inter', sans-serif",
            weight: "400"
          }
        }
      },
      scales: {
        x: {
          ticks: {
            color: "#6b7280", // text-gray-500
            font: {
              family: "'Inter', sans-serif"
            }
          },
        },
        y: {
          beginAtZero: false,
          ticks: {
            color: "#6b7280",
            callback: value => `${value}°`,
            font: {
              family: "'Inter', sans-serif"
            }
          },
        }
      }
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const bindings = [
    { panel: "firstPeriod-panel", id: "first", variable: "temperature" },
    { panel: "secondPeriod-panel", id: "second", variable: "temperature" },
    { panel: "thirdPeriod-panel", id: "third", variable: "temperature" }
  ];

  bindings.forEach(({ panel, id, variable }) => {
    const element = document.querySelector(`.${panel}`);
    if (element) {
      element.addEventListener("click", () => toggleChart(id, variable));
    }
  });
});