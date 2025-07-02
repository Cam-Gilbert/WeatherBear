
const hourlyData = {
  first: [],
  second: [],
  third: [],
  fourth: [],
  fifth: [],
  sixth: [],
  units: []
};

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


export function fetchAndRenderForecast(payload) {
  console.log("fetch initiated with data:", payload);
  return fetch("/get-forecast", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  })
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        console.error("Forecast Error:", data.error);
        showErrorMessage(data.error); // pls show up on webpage
        return false;
      }

      clearErrorMessage();

      const unit = payload.units === "metric" ? "C" : "F";
      console.log(data.fifth_period);      
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
        <div class="flex justify-between items-start mb-2">
          <h3 class="text-xl font-bold">${period.title}</h3>
          <p class="text-xs text-gray-400">Click for more information!</p>
        </div>
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
      document.querySelector(".fourthPeriod-panel").innerHTML = formatPeriod(data.fourth_period);
      document.querySelector(".fifthPeriod-panel").innerHTML = formatPeriod(data.fifth_period);
      document.querySelector(".sixthPeriod-panel").innerHTML = formatPeriod(data.sixth_period);


      // Re-add the chart containers after wiping them out
      document.querySelector(".firstPeriod-panel").insertAdjacentHTML("beforeend", `
        <div id="first-chart-container" class="hidden mt-4">
          <div class="flex flex-col md:flex-row gap-4">
            <div class="w-full md:w-1/2">
              <canvas id="first-chart" class="w-full h-48"></canvas>
            </div>
            <div class="w-full md:w-1/2">
              <canvas id="first-chart-a" class="w-full h-48"></canvas>
            </div>
          </div>
        </div>
      `);

      document.querySelector(".secondPeriod-panel").insertAdjacentHTML("beforeend", `
        <div id="second-chart-container" class="hidden mt-4">
          <div class="flex flex-wrap gap-4">
            <div class="w-full md:w-1/2">
              <canvas id="second-chart" class="w-full h-48"></canvas>
            </div>
            <div class="w-full md:w-1/2">
              <canvas id="second-chart-a" class="w-full h-48"></canvas>
            </div>
          </div>
        </div>
      `);

      document.querySelector(".thirdPeriod-panel").insertAdjacentHTML("beforeend", `
        <div id="third-chart-container" class="hidden mt-4">
          <div class="flex flex-wrap gap-4">
            <div class="w-full md:w-1/2">
              <canvas id="third-chart" class="w-full h-48"></canvas>
            </div>
            <div class="w-full md:w-1/2">
              <canvas id="third-chart-a" class="w-full h-48"></canvas>
            </div>
          </div>
        </div>
      `);
      
      document.querySelector(".fourthPeriod-panel").insertAdjacentHTML("beforeend", `
        <div id="fourth-chart-container" class="hidden mt-4">
          <div class="flex flex-wrap gap-4">
            <div class="w-full md:w-1/2">
              <canvas id="fourth-chart" class="w-full h-48"></canvas>
            </div>
            <div class="w-full md:w-1/2">
              <canvas id="fourth-chart-a" class="w-full h-48"></canvas>
            </div>
          </div>
        </div>
      `);

      document.querySelector(".fifthPeriod-panel").insertAdjacentHTML("beforeend", `
        <div id="fifth-chart-container" class="hidden mt-4">
          <div class="flex flex-wrap gap-4">
            <div class="w-full md:w-1/2">
              <canvas id="fifth-chart" class="w-full h-48"></canvas>
            </div>
            <div class="w-full md:w-1/2">
              <canvas id="fifth-chart-a" class="w-full h-48"></canvas>
            </div>
          </div>
        </div>
      `);

      document.querySelector(".sixthPeriod-panel").insertAdjacentHTML("beforeend", `
        <div id="sixth-chart-container" class="hidden mt-4">
          <div class="flex flex-wrap gap-4">
            <div class="w-full md:w-1/2">
              <canvas id="sixth-chart" class="w-full h-48"></canvas>
            </div>
            <div class="w-full md:w-1/2">
              <canvas id="sixth-chart-a" class="w-full h-48"></canvas>
            </div>
          </div>
        </div>
      `);
      // save hourly data to global list so chart function can see it
      hourlyData.first = data.first_period.hourly_forecast;
      hourlyData.second = data.second_period.hourly_forecast;
      hourlyData.third = data.third_period.hourly_forecast;
      hourlyData.fourth = data.fourth_period.hourly_forecast;
      hourlyData.fifth = data.fifth_period.hourly_forecast;
      hourlyData.sixth = data.sixth_period.hourly_forecast;
      hourlyData.units = payload.units;

      return true;
    })
    .catch(err => {
      console.error("Fetch Error:", err);
      showErrorMessage("Could not load forecast. Please check your connection or try a different location.");
      return false;
    });
}

/**
 * Makes a hex code into an rgb val. Also can make the color lighter.
 * 
 * @param hex color hex code
 * @param alpha transparency value, closer to 0 = more transparent
 * @returns 
 */
function hexToRGBA(hex, alpha) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/**
 * 
 * @param {*} id 
 * @param  {...any} initialVariables 
 * @returns 
 */
export function toggleChart(id, ...initialVariables) {
  const container = document.getElementById(`${id}-chart-container`);
  container.classList.toggle("hidden");

  // Avoid rendering twice
  if (container.dataset.rendered) return;

  const hourly = hourlyData[id];
  if (!hourly || hourly.length === 0) return;

  // Variables available
  const variableOptions = [
    { key: "temperature", label: "Temperature" },
    { key: "probabilityOfPrecipitation", label: "Precipitation Chance" },
    { key: "relativeHumidity", label: "Relative Humidity" },
    { key: "windSpeed", label: "Wind Speed" },
    { key: "dewpoint", label: "Dewpoint" }
  ];

  // Color map
  const colorMap = {
    temperature: "#c10007",
    probabilityOfPrecipitation: "#155dfc",
    relativeHumidity: "#008236",
    windSpeed: "#ff7300",
    dewpoint: "#004f3b"
  };

  // Clear chart container
  container.innerHTML = "";

  // --- CREATE SELECTOR ---
  const selectorRow = document.createElement("div");
  selectorRow.className = "mb-4 flex flex-wrap gap-2";

  variableOptions.forEach(({ key, label }) => {
    const btn = document.createElement("button");
    const isSelected = initialVariables.includes(key);
    btn.className = `selector-btn px-3 py-1 rounded-full text-sm font-medium transition`;
    btn.style.backgroundColor = isSelected ? colorMap[key] : "#e5e7eb";  // Tailwind gray-200
    btn.style.color = isSelected ? "#ffffff" : "#1f2937"; 
    btn.dataset.var = key;
    btn.textContent = label;

    btn.addEventListener("click", () => {
      const selectedBtns = [...selectorRow.querySelectorAll(".selector-btn")]
        .filter(b => b.style.backgroundColor !== "rgb(229, 231, 235)"); // gray-200

      const isSelected = btn.style.backgroundColor !== "rgb(229, 231, 235)";

      if (isSelected) {
        btn.style.backgroundColor = "#e5e7eb";  // deselect
        btn.style.color = "#1f2937";
      } else {
        if (selectedBtns.length >= 2) {
          const first = selectedBtns[0];
          first.style.backgroundColor = "#e5e7eb";
          first.style.color = "#1f2937";
        }
        btn.style.backgroundColor = colorMap[key];
        btn.style.color = "#ffffff";
      }

      const newSelected = [...selectorRow.querySelectorAll(".selector-btn")]
        .filter(b => b.style.backgroundColor !== "rgb(229, 231, 235)")  // not gray-200
        .map(b => b.dataset.var);
        
      renderCharts(newSelected);
    });

    selectorRow.appendChild(btn);
  });

  // --- CREATE CHART ROW CONTAINER ---
  const chartRow = document.createElement("div");
  chartRow.className = "flex flex-col md:flex-row gap-4";

  container.appendChild(selectorRow);
  container.appendChild(chartRow);
  container.dataset.rendered = true;

  // --- INITIAL RENDER ---
  renderCharts(initialVariables);

  // --- CHART RENDER FUNCTION ---
  function renderCharts(variables) {
    chartRow.innerHTML = "";

    variables.slice(0, 2).forEach(variable => {
      const labels = hourly.map(h =>
        new Date(h.startTime).toLocaleTimeString([], { hour: "numeric" })
      );

      const values = hourly.map(h => {
        let val = h[variable];

        // Change wind speed from "9 km/h" to just the int 9"
        if (variable === "windSpeed" && typeof val === "string") {
          const parsed = parseFloat(val);
          return isNaN(parsed) ? 0 : parsed;
        }

        // exact the values out of the value field within the values that are not temperature
        if (typeof val === "object" && val !== null && "value" in val) {
          val =  val.value;
        }

        // Not sure why but dewpoint seems to always be in celcius so must change it if units are not metric
        if (variable === "dewpoint" && hourlyData.units !== "metric") {
          val = Math.round((val * 9/5) + 32);
        }

        return val;      
      });

      const wrapper = document.createElement("div");
      wrapper.className = "w-full md:w-1/2";

      const canvas = document.createElement("canvas");
      canvas.className = "w-full h-48";
      canvas.style.maxWidth = "100%";

      wrapper.appendChild(canvas);
      chartRow.appendChild(wrapper);

      const ctx = canvas.getContext("2d");

      new Chart(ctx, {
        type: "line",
        data: {
          labels,
          datasets: [
            {
              label: variable.charAt(0).toUpperCase() + variable.slice(1),
              data: values,
              borderColor: colorMap[variable] || "#3b82f6",
              backgroundColor: hexToRGBA(colorMap[variable] || "#3b82f6", 0.1),
              fill: true,
              tension: 0.4,
              pointRadius: 3,
              pointHoverRadius: 6
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: "#1f2937",
              titleColor: "#fff",
              bodyColor: "#d1d5db",
              borderColor: colorMap[variable] || "#3b82f6",
              borderWidth: 1,
              titleFont: { family: "'Inter', sans-serif", weight: "700" },
              bodyFont: { family: "'Inter', sans-serif", weight: "400" }
            }
          },
          scales: {
            x: {
              ticks: {
                color: "#6b7280",
                font: { family: "'Inter', sans-serif" }
              },
              grid: { display: false }
            },
            y: {
              beginAtZero: variable === "probabilityOfPrecipitation",
              min:
                variable === "probabilityOfPrecipitation"
                  ? 0
                  : variable === "windSpeed"
                    ? Math.max(0, Math.floor(Math.min(...values) - 5))
                    : Math.floor(Math.min(...values) - 5),
              max: variable === "probabilityOfPrecipitation"
                ? 100
                : Math.ceil(Math.max(...values) + 5),
              ticks: {
                color: "#6b7280",
                callback: value => {
                  if (variable === "probabilityOfPrecipitation" || variable === "relativeHumidity") {
                    return `${value}%`;
                  } else if (variable === "windSpeed") {
                    const unit = hourlyData.units === "metric" ? "km/h" : "mph";
                    return `${value} ${unit}`;
                  } else {
                    return `${value}°`;
                  }
                },
                font: { family: "'Inter', sans-serif" }
              },
              grid: { display: false }
            }
          }
        }
      });
    });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const bindings = [
    { panel: "firstPeriod-panel", id: "first", variable: ["temperature", "probabilityOfPrecipitation"] },
    { panel: "secondPeriod-panel", id: "second", variable: ["temperature", "probabilityOfPrecipitation"] },
    { panel: "thirdPeriod-panel", id: "third", variable: ["temperature", "probabilityOfPrecipitation"] },
    { panel: "fourthPeriod-panel", id: "fourth", variable: ["temperature", "probabilityOfPrecipitation"] },
    { panel: "fifthPeriod-panel", id: "fifth", variable: ["temperature", "probabilityOfPrecipitation"] },
    { panel: "sixthPeriod-panel", id: "sixth", variable: ["temperature", "probabilityOfPrecipitation"] }
  ];

  bindings.forEach(({ panel, id, variable }) => {
    const element = document.querySelector(`.${panel}`);
    if (element) {
      element.addEventListener("click", (e) => {
        if (e.target.closest(".selector-btn") || e.target.tagName === "CANVAS") return;
        toggleChart(id, ...variable);
      });
    }
  });
});