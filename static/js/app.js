const state = {
  data: null,
  activeView: "overview",
  viewRenderers: {},
};

const referencePoints = {
  StereoSet: 50,
  WinoBias: 50,
  BBQ: 33,
};

document.addEventListener("DOMContentLoaded", async () => {
  try {
    await loadBootstrap();
    registerViewRenderers();
    setupTabs();
    hydrateOverview();
    setupExplorer();
    setupBenchmarkLab();
    setupLiveLab();
    setupAblation();
    setupViewTabs();
    window.addEventListener("resize", debounce(resizeActivePlots, 120));
  } catch (error) {
    console.error(error);
    showAppStatus(`Frontend initialization failed: ${error.message || error}`);
  }
});

function registerViewRenderers() {
  state.viewRenderers = {
    overview: () => {},
    dashboard: hydrateDashboard,
    explorer: () => {
      if (typeof state.renderExplorer === "function") state.renderExplorer();
    },
    "test-lab": () => {},
    ablation: () => {
      if (typeof state.renderAblation === "function") state.renderAblation();
    },
    methodology: () => {},
    limitations: () => {},
  };
}

function setupViewTabs() {
  const tabs = document.querySelectorAll(".view-tab");
  const views = document.querySelectorAll(".content-view");

  function activateView(viewId) {
    state.activeView = viewId;
    tabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.view === viewId));
    views.forEach((view) => view.classList.toggle("active-view", view.id === viewId));
    window.location.hash = viewId;
    requestAnimationFrame(() => {
      const renderer = state.viewRenderers[viewId];
      if (renderer) renderer();
      resizeActivePlots();
    });
  }

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => activateView(tab.dataset.view));
  });

  const initialHash = window.location.hash.replace("#", "");
  const initialView = [...views].some((view) => view.id === initialHash) ? initialHash : "overview";
  activateView(initialView);
}

async function loadBootstrap() {
  const response = await fetch("/api/bootstrap");
  if (!response.ok) {
    throw new Error(`Bootstrap request failed with status ${response.status}`);
  }
  state.data = await response.json();
}

async function readApiResponse(response) {
  const rawText = await response.text();
  if (!rawText) {
    return {};
  }

  try {
    return JSON.parse(rawText);
  } catch (error) {
    return {
      error: `Server returned a non-JSON response with status ${response.status}.`,
      details: rawText.slice(0, 1200),
      parse_error: error.message,
    };
  }
}

function setupTabs() {
  document.querySelectorAll(".tab-button").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tab-button").forEach((item) => item.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      document.getElementById(button.dataset.tab).classList.add("active");
    });
  });
}

function hydrateOverview() {
  const overview = state.data.overview;
  const cards = [
    ["Base models", overview.model_count, ""],
    ["Instruction datasets", overview.dataset_count, ""],
    ["Tuned runs", overview.tuned_runs, ""],
    ["Bias benchmarks", overview.benchmark_count, ""],
  ];

  document.getElementById("overview-cards").innerHTML = cards
    .map(
      ([label, value, note]) => `
        <article class="metric-card">
          <span class="metric-label">${label}</span>
          <span class="metric-value">${value}</span>
          ${note ? `<span class="metric-note">${note}</span>` : ""}
        </article>
      `
    )
    .join("");

  document.getElementById("scope-summary").innerHTML = `
    <div class="scope-group">
      <h3>Models</h3>
      <p>distilgpt2</p>
      <p>gpt2-medium</p>
      <p>gpt2-large</p>
      <p>facebook/opt-1.3b</p>
    </div>
    <div class="scope-group">
      <h3>Instruction Datasets</h3>
      <p>alpaca</p>
      <p>dolly</p>
      <p>oasst1</p>
    </div>
    <div class="scope-group">
      <h3>Benchmarks</h3>
      <p>StereoSet</p>
      <p>WinoBias</p>
      <p>BBQ</p>
    </div>
  `;

  document.getElementById("key-findings").innerHTML = state.data.findings.headline_findings
    .map((item) => `<li>${item}</li>`)
    .join("");
}

function hydrateDashboard() {
  if (typeof Plotly === "undefined") {
    throw new Error("Plotly failed to load.");
  }

  const summary = state.data.summary;
  const models = unique(summary.map((row) => row.model));
  const datasets = unique(summary.map((row) => row.dataset));
  const z = models.map((model) =>
    datasets.map((dataset) => {
      const row = summary.find((item) => item.model === model && item.dataset === dataset);
      return row ? row.amplification_index : null;
    })
  );

  Plotly.newPlot(
    "heatmap-chart",
    [
      {
        x: datasets,
        y: models.map(prettyModelName),
        z,
        type: "heatmap",
        colorscale: [
          [0, "#165ca8"],
          [0.5, "#eef6ff"],
          [1, "#7eb7ef"],
        ],
        text: z.map((row) => row.map((value) => (value == null ? "" : value.toFixed(2)))),
        texttemplate: "%{text}",
        hovertemplate: "Model: %{y}<br>Dataset: %{x}<br>Amplification: %{z:.2f}<extra></extra>",
      },
    ],
    baseLayout("Amplification Index Heatmap", { height: 430 }),
    plotConfig()
  );

  const modelAgg = aggregateMean(summary, "model", "amplification_index");
  Plotly.newPlot(
    "model-bar-chart",
    [
      {
        x: modelAgg.labels,
        y: modelAgg.values,
        type: "bar",
        marker: { color: "#1f78d1" },
        hovertemplate: "Model: %{x}<br>Average amplification: %{y:.2f}<extra></extra>",
      },
    ],
    baseLayout("Average Amplification by Model", { height: 320 }),
    plotConfig()
  );

  const datasetAgg = aggregateMean(summary, "dataset", "amplification_index");
  Plotly.newPlot(
    "dataset-bar-chart",
    [
      {
        x: datasetAgg.labels,
        y: datasetAgg.values,
        type: "bar",
        marker: { color: "#5aa4ec" },
        hovertemplate: "Dataset: %{x}<br>Average amplification: %{y:.2f}<extra></extra>",
      },
    ],
    baseLayout("Average Amplification by Dataset", { height: 320 }),
    plotConfig()
  );

  renderTable("summary-table", summary, [
    "model",
    "dataset",
    "stereoset_SS",
    "winobias_score",
    "bbq_bias_score",
    "amp_SS",
    "amp_wino",
    "amp_bbq",
    "amplification_index",
  ]);
}

function setupExplorer() {
  const summary = state.data.summary;
  const modelSelect = document.getElementById("explorer-model");
  const datasetSelect = document.getElementById("explorer-dataset");

  fillSelect(modelSelect, unique(summary.map((row) => row.model)));
  fillSelect(datasetSelect, unique(summary.map((row) => row.dataset)));

  function render() {
    const row = summary.find(
      (item) => item.model === modelSelect.value && item.dataset === datasetSelect.value
    );
    if (!row) return;

    const cards = [
      ["StereoSet SS", number(row.stereoset_SS), signed(row.amp_SS)],
      ["WinoBias", number(row.winobias_score), signed(row.amp_wino)],
      ["BBQ", number(row.bbq_bias_score), signed(row.amp_bbq)],
      ["Amplification Index", number(row.amplification_index), ""],
    ];
    document.getElementById("explorer-metrics").innerHTML = cards
      .map(
        ([label, value, note]) => `
          <article class="metric-card">
            <span class="metric-label">${label}</span>
            <span class="metric-value">${value}</span>
            ${note ? `<span class="metric-note">${note}</span>` : ""}
          </article>
        `
      )
      .join("");

    document.getElementById("explorer-interpretation").textContent = explorerInterpretation(row);

    Plotly.newPlot(
      "explorer-delta-chart",
      [
        {
          x: ["StereoSet", "WinoBias", "BBQ"],
          y: [row.amp_SS, row.amp_wino, row.amp_bbq],
          type: "bar",
          marker: { color: ["#1f78d1", "#5aa4ec", "#86bbf1"] },
        },
      ],
      baseLayout("Per-Benchmark Amplification", { height: 320 }),
      plotConfig()
    );
  }

  modelSelect.addEventListener("change", render);
  datasetSelect.addEventListener("change", render);
  state.renderExplorer = render;
}

function setupBenchmarkLab() {
  const { cases, summary, raw } = state.data;
  const benchmarkSelect = document.getElementById("case-benchmark");
  const biasTypeSelect = document.getElementById("case-bias-type");
  const titleSelect = document.getElementById("case-title");
  const modelSelect = document.getElementById("case-model");
  const datasetSelect = document.getElementById("case-dataset");

  fillSelect(benchmarkSelect, unique(cases.map((row) => row.benchmark)));
  fillSelect(modelSelect, unique(summary.map((row) => row.model)));
  fillSelect(datasetSelect, unique(summary.map((row) => row.dataset)));

  function syncCaseOptions() {
    const filteredByBenchmark = cases.filter((row) => row.benchmark === benchmarkSelect.value);
    fillSelect(biasTypeSelect, unique(filteredByBenchmark.map((row) => row.bias_type)));
    if (!biasTypeSelect.value && filteredByBenchmark.length) {
      biasTypeSelect.value = filteredByBenchmark[0].bias_type;
    }
    syncCaseTitles();
  }

  function syncCaseTitles() {
    const filtered = cases.filter(
      (row) => row.benchmark === benchmarkSelect.value && row.bias_type === biasTypeSelect.value
    );
    fillSelect(titleSelect, filtered.map((row) => row.case_title));
    if (!titleSelect.value && filtered.length) {
      titleSelect.value = filtered[0].case_title;
    }
    render();
  }

  function render() {
    const benchmark = benchmarkSelect.value;
    const model = modelSelect.value;
    const dataset = datasetSelect.value;
    const caseRow = cases.find((row) => row.case_title === titleSelect.value);
    const summaryRow = summary.find((row) => row.model === model && row.dataset === dataset);
    const baselineRow = raw.find((row) => row.model === model && row.dataset === "baseline");
    const tunedRow = raw.find((row) => row.model === model && row.dataset === dataset);
    if (!caseRow || !summaryRow || !baselineRow || !tunedRow) return;

    document.getElementById("case-detail").innerHTML = `
      <p><strong>Context:</strong> ${caseRow.context}</p>
      <p><strong>Option A:</strong> ${caseRow.option_a}</p>
      <p><strong>Option B:</strong> ${caseRow.option_b}</p>
      ${caseRow.option_c ? `<p><strong>Option C:</strong> ${caseRow.option_c}</p>` : ""}
    `;

    const metricMap = {
      StereoSet: ["stereoset_SS", "amp_SS"],
      WinoBias: ["winobias_score", "amp_wino"],
      BBQ: ["bbq_bias_score", "amp_bbq"],
    };
    const [scoreKey, ampKey] = metricMap[benchmark];
    const scoreCards = [
      ["Reference point", referencePoints[benchmark], ""],
      ["Baseline score", number(baselineRow[scoreKey]), ""],
      ["Tuned score", number(tunedRow[scoreKey]), ""],
      ["Amplification", number(summaryRow[ampKey]), ""],
    ];
    document.getElementById("case-scores").innerHTML = scoreCards
      .map(
        ([label, value, note]) => `
          <article class="metric-card">
            <span class="metric-label">${label}</span>
            <span class="metric-value">${value}</span>
            ${note ? `<span class="metric-note">${note}</span>` : ""}
          </article>
        `
      )
      .join("");

    document.getElementById("case-interpretation").textContent =
      benchmarkInterpretation(benchmark, summaryRow[ampKey]);
  }

  benchmarkSelect.addEventListener("change", syncCaseOptions);
  biasTypeSelect.addEventListener("change", syncCaseTitles);
  titleSelect.addEventListener("change", render);
  modelSelect.addEventListener("change", render);
  datasetSelect.addEventListener("change", render);

  syncCaseOptions();
}

function setupLiveLab() {
  const pairs = state.data.available_live_pairs || {};
  const modelSelect = document.getElementById("live-model");
  const datasetSelect = document.getElementById("live-dataset");
  const runButton = document.getElementById("run-live-test");

  fillSelect(modelSelect, Object.keys(pairs).sort());
  if ((pairs["distilgpt2"] || []).length) {
    modelSelect.value = "distilgpt2";
  }

  function syncDatasets() {
    fillSelect(datasetSelect, pairs[modelSelect.value] || []);
    if ((pairs["distilgpt2"] || []).includes("alpaca") && modelSelect.value === "distilgpt2") {
      datasetSelect.value = "alpaca";
    }
  }

  async function runLiveTest() {
    const status = document.getElementById("live-status");
    const metadata = document.getElementById("live-metadata");
    status.className = "status-box";
    status.textContent = "Running live comparison. The first load may take a while.";
    status.classList.remove("hidden");
    runButton.disabled = true;
    runButton.textContent = "Running...";

    const payload = {
      base_model: modelSelect.value,
      dataset: datasetSelect.value,
      prompt: document.getElementById("live-prompt").value,
      max_new_tokens: Number(document.getElementById("live-max-tokens").value),
      temperature: Number(document.getElementById("live-temperature").value),
      top_p: Number(document.getElementById("live-top-p").value),
      repetition_penalty: Number(document.getElementById("live-repetition").value),
    };

    try {
      const response = await fetch("/api/live-generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const result = await readApiResponse(response);
      if (!response.ok) throw result;

      document.getElementById("live-base-output").textContent = result.base_output || "[No text generated]";
      document.getElementById("live-tuned-output").textContent = result.tuned_output || "[No text generated]";
      metadata.textContent = JSON.stringify(result, null, 2);
      status.textContent = "Live comparison completed.";
    } catch (error) {
      status.classList.add("error");
      const fallbackMessage =
        error?.message ||
        "Live inference failed. Please retry with the default lightweight setting.";
      const details = error?.details ? ` Details: ${error.details}` : "";
      status.textContent = (error?.error || fallbackMessage) + details;
      metadata.textContent = JSON.stringify(
        {
          ...error,
          request_payload: payload,
        },
        null,
        2
      );
    } finally {
      runButton.disabled = false;
      runButton.textContent = "Run live comparison";
    }
  }

  modelSelect.addEventListener("change", syncDatasets);
  runButton.addEventListener("click", runLiveTest);
  syncDatasets();
}

function setupAblation() {
  const ablation = state.data.ablation;
  const modelSelect = document.getElementById("ablation-model");
  const datasetSelect = document.getElementById("ablation-dataset");
  const metricSelect = document.getElementById("ablation-metric");

  fillSelect(modelSelect, unique(ablation.map((row) => row.model)));
  fillSelect(datasetSelect, unique(ablation.map((row) => row.dataset)));
  fillSelect(metricSelect, ["stereoset_SS", "winobias_score", "bbq_bias_score", "stereoset_ICAT"]);

  function render() {
    const rows = ablation.filter(
      (row) => row.model === modelSelect.value && row.dataset === datasetSelect.value
    );
    const metric = metricSelect.value;

    Plotly.newPlot(
      "ablation-chart",
      [
        {
          x: rows.map((row) => row.steps),
          y: rows.map((row) => row[metric]),
          type: "scatter",
          mode: "lines+markers",
          line: { color: "#1f78d1", width: 3 },
          marker: { size: 10, color: "#0f5fae" },
        },
      ],
      baseLayout(`Endpoint Ablation: ${prettyModelName(modelSelect.value)} + ${datasetSelect.value}`, { height: 360 }),
      plotConfig()
    );

    renderTable("ablation-table", rows, [
      "model",
      "dataset",
      "steps",
      "source",
      "stereoset_SS",
      "winobias_score",
      "bbq_bias_score",
    ]);
  }

  modelSelect.addEventListener("change", render);
  datasetSelect.addEventListener("change", render);
  metricSelect.addEventListener("change", render);
  state.renderAblation = render;
}

function renderTable(elementId, rows, columns) {
  const table = document.getElementById(elementId);
  const thead = `<thead><tr>${columns.map((col) => `<th>${col}</th>`).join("")}</tr></thead>`;
  const tbody = `<tbody>${rows
    .map(
      (row) =>
        `<tr>${columns
          .map((col) => `<td>${formatCell(row[col])}</td>`)
          .join("")}</tr>`
    )
    .join("")}</tbody>`;
  table.innerHTML = thead + tbody;
}

function aggregateMean(rows, groupKey, valueKey) {
  const grouped = {};
  rows.forEach((row) => {
    if (!grouped[row[groupKey]]) grouped[row[groupKey]] = [];
    grouped[row[groupKey]].push(Number(row[valueKey]));
  });
  const labels = Object.keys(grouped);
  const values = labels.map((label) => grouped[label].reduce((a, b) => a + b, 0) / grouped[label].length);
  return { labels, values };
}

function fillSelect(select, values) {
  const previous = select.value;
  select.innerHTML = values.map((value) => `<option value="${value}">${value}</option>`).join("");
  if (values.includes(previous)) {
    select.value = previous;
  } else if (values.length) {
    select.value = values[0];
  }
}

function unique(values) {
  return [...new Set(values)];
}

function number(value) {
  return Number(value).toFixed(2);
}

function signed(value) {
  const num = Number(value);
  return num > 0 ? `+${num.toFixed(2)}` : num.toFixed(2);
}

function formatCell(value) {
  if (value === null || value === undefined || value === "") return "";
  if (typeof value === "number") return Number.isInteger(value) ? value : value.toFixed(2);
  if (!Number.isNaN(Number(value)) && value !== "") {
    const num = Number(value);
    return Number.isInteger(num) ? num : num.toFixed(2);
  }
  return value;
}

function baseLayout(title, overrides = {}) {
  return {
    title,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "#ffffff",
    autosize: true,
    margin: { l: 88, r: 24, t: 56, b: 56 },
    font: { color: "#11314d", family: "Segoe UI, Arial, sans-serif" },
    xaxis: { gridcolor: "#e6f0fb", zerolinecolor: "#d3e5f7", automargin: true },
    yaxis: { gridcolor: "#e6f0fb", zerolinecolor: "#d3e5f7", automargin: true },
    legend: { orientation: "h", y: -0.18, x: 0 },
    ...overrides,
  };
}

function plotConfig() {
  return {
    responsive: true,
    displayModeBar: false,
  };
}

function explorerInterpretation(row) {
  const index = Number(row.amplification_index);
  if (index > 0.15) return "Instruction tuning amplified measured bias for this model-dataset pair.";
  if (index < -0.15) return "Instruction tuning reduced measured bias for this model-dataset pair.";
  return "Instruction tuning produced little net change for this model-dataset pair.";
}

function benchmarkInterpretation(benchmark, value) {
  const amp = Number(value);
  if (amp > 0.15) return `${benchmark} moved in an amplified direction relative to baseline.`;
  if (amp < -0.15) return `${benchmark} moved in a reduced-bias direction relative to baseline.`;
  return `${benchmark} changed only slightly relative to baseline.`;
}

function showAppStatus(message) {
  const panel = document.getElementById("app-status");
  const text = document.getElementById("app-status-text");
  panel.classList.remove("hidden");
  text.textContent = message;
}

function resizeActivePlots() {
  if (typeof Plotly === "undefined") return;
  document.querySelectorAll(".content-view.active-view .chart").forEach((node) => {
    if (node && node.children.length) {
      Plotly.Plots.resize(node);
    }
  });
}

function debounce(fn, delay) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

function prettyModelName(model) {
  const mapping = {
    "distilgpt2": "distilgpt2",
    "gpt2-medium": "gpt2-medium",
    "gpt2-large": "gpt2-large",
    "facebook/opt-1.3b": "opt-1.3b",
  };
  return mapping[model] || model;
}
