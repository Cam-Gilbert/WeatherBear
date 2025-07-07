import { enableExplanation } from "./explainer.js";

function fetchTropicalSummary(region, expertise) {
  console.log(`Fetching: ${region} | Expertise: ${expertise}`);

  fetch("/get-tropical-summary", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ region, expertise })
  })
    .then(response => response.json())
    .then(data => {
      if (data.summary) {
        const panel = document.querySelector(`#summary-${region}`);
        if (!panel) {
          console.warn(`Panel not found for #summary-${region}`);
          return;
        }
        const summaryPara = panel.querySelector("p");
        if (!summaryPara) {
          console.warn(`No <p> in #summary-${region}`);
          return;
        }
        summaryPara.textContent = data.summary;
        enableExplanation({
          containerSelector: `#summary-${region} p`,
          toggleSelector: `#explain-toggle-${region}`,
          getContextData: () => ({
            summary: summaryPara.textContent,
            afd: data.afd || "",
            expertise: expertise
          })
        });
        const explainToggle = document.querySelector(`#explain-toggle-${region}`);
        if (explainToggle) {
          explainToggle.checked = false;
          explainToggle.nextElementSibling.textContent =
            "💡 Confused? Click here and select text for an in-depth explanation.";
        }

      } else {
        console.warn("No summary found:", data.error);
      }
    })
    .catch(error => console.error("Error fetching summary:", error));
}

document.querySelectorAll(".summary-button").forEach(button => {
  button.addEventListener("click", () => {
    const region = button.getAttribute("data-region");
    const expertise = button.getAttribute("data-expertise");
    fetchTropicalSummary(region, expertise);
  });
});

// i deadass dont know why this is being put here I cannot get these damn buttons to work 
window.fetchTropicalSummary = fetchTropicalSummary;
window.enableExplanation = enableExplanation;
