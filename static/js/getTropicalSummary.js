function fetchTropicalSummary(region, expertise) {
  const regionMap = {
    "atlantic": "Atlantic",
    "central": "Central_Pacific",
    "eastern": "Eastern_Pacific"
  };

  const jsonRegion = regionMap[region] || region;

  const panelIdMap = {
    "Atlantic": "atlantic",
    "Central_Pacific": "central",
    "Eastern_Pacific": "eastern"
  };

  const panelRegion = panelIdMap[jsonRegion];

  console.log(`Fetching: ${jsonRegion} | Expertise: ${expertise}`);

  fetch("/get-tropical-summary", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ region: jsonRegion, expertise })
  })
  .then(response => response.json())
  .then(data => {
    if (data.summary) {
      const panel = document.querySelector(`#summary-${panelRegion}`);
      if (!panel) {
        console.warn(`Could not find summary panel for: #summary-${panelRegion}`);
        return;
      }
      const summaryPara = panel.querySelector("p");
      if (!summaryPara) {
        console.warn(`No <p> tag found inside panel #summary-${panelRegion}`);
        return;
      }
      summaryPara.textContent = data.summary;
    } else {
      console.warn("No summary found:", data.error);
    }
  })
  .catch(error => console.error("Error fetching summary:", error));
}



document.addEventListener("DOMContentLoaded", () => {
  // Auto-fetch default summaries for each region
  fetchTropicalSummary("atlantic", "no_summary");
  fetchTropicalSummary("eastern", "no_summary");
  fetchTropicalSummary("central", "no_summary");

  // Hook up all expertise tab groups
  const allExpertiseGroups = document.querySelectorAll('[id^="expertise-tabs"]');

  allExpertiseGroups.forEach(group => {
    const region = group.id.replace("expertise-tabs-", "").toLowerCase();

    group.querySelectorAll("button").forEach(button => {
      button.addEventListener("click", () => {
        let expertiseText = button.textContent.trim().toLowerCase().replace(" ", "_");
        if (expertiseText === "novice") {
        expertiseText = "none";
        }
        const expertise = expertiseText;
        fetchTropicalSummary(region, expertise);
      });
    });
  });
});
