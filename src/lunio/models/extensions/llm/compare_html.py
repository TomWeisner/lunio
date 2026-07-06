"""HTML report rendering for LLM-vs-rules comparison outputs."""

import html
from pathlib import Path

import pandas as pd


def build_html_report(
    comparison: pd.DataFrame,
    *,
    rules_count: int,
    llm_count: int,
    comparison_output_path: Path,
) -> str:
    """Build a static, filterable HTML report from comparison data."""

    total_rows = len(comparison)
    matched_rows = int(comparison["decision_match"].sum()) if total_rows else 0
    match_rate = matched_rows / total_rows if total_rows else 0
    mismatched_rows = total_rows - matched_rows

    topic_options = _select_options(comparison, "topic")
    advertiser_options = _select_options(comparison, "company_name")
    rules_options = _select_options(comparison, "safety_decision")
    llm_options = _select_options(comparison, "llm_safety_decision")
    decision_matrix = _decision_matrix(comparison)
    prediction_distribution = _prediction_distribution(
        _normalized_comparison(comparison)
    )
    confidence_matrix = _confidence_matrix(comparison)
    confidence_distribution_chart = _prediction_confidence_distribution(comparison)
    discrepancies = _discrepancies_section(comparison)

    rows = "\n".join(
        _comparison_html_row(row, detail_prefix="comparison")
        for row in comparison.sort_values("placement_id").itertuples(index=False)
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>LLM vs Rules Report</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --text: #1f2328;
      --muted: #667085;
      --border: #d0d7de;
      --safe: #1a7f37;
      --review: #9a6700;
      --unsafe: #cf222e;
    }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }}
    main {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 32px 24px 48px;
    }}
    h1, h2 {{ margin: 0; }}
    h1 {{
      font-size: 32px;
      margin-bottom: 8px;
    }}
    h2 {{
      font-size: 20px;
      margin-bottom: 16px;
    }}
    .subtitle {{
      color: var(--muted);
      margin: 0 0 24px;
    }}
    .contents-nav {{
      background: #eef6ff;
      border: 1px solid #b6d4fe;
      border-radius: 8px;
      margin-bottom: 24px;
      padding: 16px 18px;
    }}
    .contents-title {{
      font-size: 14px;
      font-weight: 700;
      margin: 0 0 10px;
    }}
    .contents-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px 16px;
      list-style: none;
      margin: 0;
      padding: 0;
    }}
    .contents-list a {{
      color: #0969da;
      font-weight: 600;
      text-decoration: none;
    }}
    .contents-list a:hover {{
      text-decoration: underline;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-bottom: 24px;
    }}
    .card, .panel {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
    }}
    .card {{ padding: 16px; }}
    .card-label {{
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 6px;
    }}
    .card-value {{
      font-size: 28px;
      font-weight: 700;
    }}
    .panel {{
      margin-top: 24px;
      padding: 18px;
    }}
    .filters {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-bottom: 16px;
    }}
    label {{
      display: grid;
      gap: 6px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 600;
    }}
    input, select {{
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 9px 10px;
      font: inherit;
      background: #fff;
      color: var(--text);
    }}
    .table-wrap {{
      overflow: auto;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: #fff;
    }}
    .matrix-table {{
      border-collapse: collapse;
      font-size: 14px;
      table-layout: fixed;
      width: 100%;
    }}
    .matrix-table th,
    .matrix-table td {{
      border-bottom: 1px solid var(--border);
      max-width: none;
      overflow: visible;
      padding: 10px 12px;
      text-align: right;
      text-overflow: clip;
      vertical-align: middle;
      white-space: nowrap;
    }}
    .matrix-table th:first-child,
    .matrix-table td:first-child {{
      text-align: left;
    }}
    .axis-label {{
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
      margin: 0 0 8px;
    }}
    .matrix-note {{
      color: var(--muted);
      margin: 8px 0 0;
    }}
    .simple-table {{
      border-collapse: collapse;
      font-size: 14px;
      width: 100%;
    }}
    .simple-table th,
    .simple-table td {{
      border-bottom: 1px solid var(--border);
      max-width: none;
      overflow: visible;
      padding: 10px 12px;
      text-align: left;
      text-overflow: clip;
      vertical-align: top;
      white-space: normal;
    }}
    .simple-table th {{
      background: #f6f8fa;
      font-weight: 700;
    }}
    .subsection {{
      margin-top: 18px;
    }}
    .subsection h3 {{
      font-size: 16px;
      margin: 0 0 10px;
    }}
    .bar-legend {{
      display: flex;
      gap: 16px;
      margin: 8px 0 16px;
    }}
    .legend-item {{
      align-items: center;
      color: var(--muted);
      display: inline-flex;
      font-size: 13px;
      gap: 6px;
    }}
    .legend-swatch {{
      border-radius: 3px;
      display: inline-block;
      height: 10px;
      width: 10px;
    }}
    .rules-bar {{ background: #0969da; }}
    .llm-bar {{ background: #8250df; }}
    .confidence-low {{ background: #cf222e; }}
    .confidence-medium {{ background: #fb8500; }}
    .confidence-high {{ background: #2da44e; }}
    .confidence-unassessed {{ background: #8c959f; }}
    .vertical-chart {{
      align-items: end;
      border-bottom: 1px solid var(--border);
      display: grid;
      gap: 18px;
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
      min-height: 220px;
      padding: 12px 0 0;
    }}
    .bar-group {{
      align-items: end;
      display: grid;
      gap: 8px;
      grid-template-columns: 1fr 1fr;
      height: 180px;
    }}
    .bar-column {{
      display: flex;
      flex-direction: column;
      height: 100%;
      justify-content: flex-end;
    }}
    .vertical-bar {{
      align-self: end;
      border-radius: 6px 6px 0 0;
      min-height: 2px;
    }}
    .bar-label {{
      font-weight: 700;
      margin-top: 8px;
      text-align: center;
    }}
    .bar-value {{
      color: var(--muted);
      font-size: 12px;
      text-align: center;
    }}
    .stacked-vertical-bar {{
      align-items: end;
      background: #f6f8fa;
      border: 1px solid var(--border);
      border-radius: 8px;
      display: flex;
      flex-direction: column-reverse;
      overflow: hidden;
      width: 100%;
    }}
    .stacked-bar-track {{
      align-items: end;
      display: flex;
      flex: 0 0 188px;
    }}
    .stacked-bar-wrapper {{
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      height: 100%;
      width: 100%;
    }}
    .stacked-bar-value {{
      margin-bottom: 6px;
    }}
    .stack-segment {{
      min-height: 0;
      width: 100%;
    }}
    .bar-sub-label {{
      color: var(--muted);
      font-size: 12px;
      text-align: center;
    }}
    .analysis-box {{
      background: #f0f9ff;
      border: 1px solid #bfdbfe;
      border-radius: 8px;
      margin-top: 16px;
      padding: 14px 16px;
    }}
    .analysis-title {{
      font-size: 14px;
      font-weight: 700;
      margin: 0 0 6px;
    }}
    .analysis-body {{
      color: var(--muted);
      margin: 0;
    }}
    .commentary-copy {{
      color: var(--muted);
      display: grid;
      gap: 12px;
    }}
    .commentary-copy p {{
      margin: 0;
    }}
    .commentary-subsection {{
      border-top: 1px solid var(--border);
      margin-top: 4px;
      padding-top: 14px;
    }}
    .commentary-subsection h3 {{
      color: var(--text);
      font-size: 16px;
      margin: 0 0 8px;
    }}
    .comparison-like-table {{
      min-width: 1040px;
      table-layout: fixed;
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--border);
      max-width: 0;
      overflow: hidden;
      text-align: left;
      text-overflow: ellipsis;
      vertical-align: top;
      white-space: nowrap;
    }}
    th {{
      position: sticky;
      top: 0;
      background: #f6f8fa;
      z-index: 1;
      white-space: nowrap;
    }}
    th button {{
      all: unset;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font: inherit;
      font-weight: 700;
    }}
    th button::after {{
      color: var(--muted);
      content: "sort";
      font-size: 12px;
    }}
    th button[data-sort-direction="asc"]::after {{ content: "asc"; }}
    th button[data-sort-direction="desc"]::after {{ content: "desc"; }}
    tr[data-match="false"] {{ background: #fff8f7; }}
    tr.detail-row {{
      background: #fff;
    }}
    tr.detail-row[hidden] {{
      display: none;
    }}
    .expand-button {{
      all: unset;
      cursor: pointer;
      color: #0969da;
      font-weight: 700;
    }}
    .details {{
      display: grid;
      gap: 10px;
      white-space: normal;
    }}
    .detail-label {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      margin-bottom: 2px;
    }}
    .detail-value {{
      overflow-wrap: anywhere;
    }}
    .pill {{
      display: inline-block;
      border-radius: 999px;
      padding: 2px 8px;
      font-size: 12px;
      font-weight: 700;
      background: #f6f8fa;
    }}
    .decision-safe {{ color: var(--safe); }}
    .decision-review {{ color: var(--review); }}
    .decision-unsafe {{ color: var(--unsafe); }}
    .toolbar {{
      align-items: center;
      display: flex;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }}
    .muted {{ color: var(--muted); }}
    a {{ color: #0969da; }}
  </style>
</head>
<body>
  <main>
    <h1>LLM vs Rules Report</h1>
    <p class="subtitle">
      Interactive comparison of rule-based and LLM placement safety decisions.
    </p>

    {_contents_list()}

    <section class="cards" id="summary" aria-label="Summary">
      {_metric_card("Rule-based rows", rules_count)}
      {_metric_card("LLM rows", llm_count)}
      {_metric_card("Compared rows", total_rows)}
      {_metric_card("Matches", matched_rows)}
      {_metric_card("Mismatches", mismatched_rows)}
      {_metric_card("Match rate", f"{match_rate:.1%}")}
    </section>

    <section class="panel" id="decisions">
      <h2>Decisions</h2>
      <p class="axis-label">Rows: rules based decision. Columns: LLM decision.</p>
      {_decision_matrix_table(decision_matrix)}
      {prediction_distribution}
      {
        _analysis_box(
            "The LLM is more likely to designate placements as safe and less "
            "likely to label them unsafe. This may be because it "
            "can recognise when content is non-inflammatory in context and is "
            "less likely to be tripped up by overly broad regex-style "
            "matching."
        )
    }
    </section>

    <section class="panel" id="confidences">
      <h2>Confidences</h2>
      <p class="axis-label">Rows: rules based confidence. Columns: LLM confidence.</p>
      {_confidence_matrix_table(confidence_matrix)}
      {confidence_distribution_chart}
      {
        _analysis_box(
            "The fact that the LLM never assigns low confidence is a cause for "
            "concern, because it suggests the model may not be expressing real "
            "uncertainty even when evidence is weak. It would be useful to test "
            "this explicitly on synthetic or real examples where the language is "
            "genuinely ambiguous. There are also a large number of review calls, "
            "which may be operationally unhelpful if too many placements end up in "
            "manual triage. One possible improvement would be to provide much more "
            "verbose scoring guidance in the prompt, since the current prompt only "
            "gives fairly high-level judging instructions rather than a detailed "
            "confidence scoring framekwork. Another option would be to fine-tune a "
            "model on labelled examples so it sees clearer patterns of when to be "
            "decisive versus when to express uncertainty."
        )
    }
    </section>

    <section class="panel" id="discrepancies">
      <h2>Discrepancies</h2>
      {discrepancies}
      {
        _analysis_box(
            "Across the discrepancies, the LLM appears more likely to recognise "
            "humour and opinionated content as potentially risky. Outside of those "
            "cases, it is more likely to recognise when content is not actually "
            "risky, which suggests some of the remaining disagreement may come from "
            "rules firing on surface-level signals that the model can interpret more "
            "contextually."
        )
    }
    </section>

    <section class="panel" id="commentary">
      <h2>Commentary</h2>
      <div class="commentary-copy">
        <p>
          Accuracy is not the same thing as agreement with the rules engine. This
          report is most useful as a comparison of system behaviour, not as a final
          measure of policy correctness, so the next step should be to build an
          adjudicated set that tells us which judgments are actually right.
        </p>
        <p>
          The LLM seems most useful where it can disambiguate brittle lexical
          triggers, such as words like &quot;war&quot; appearing in an obviously benign
          sports context. At the same time, there is still a lot of overlap where
          both systems agree on clear safe and clear unsafe cases, which is a good
          reminder that the rules model still has value as a fast, cheap first-pass
          check.
        </p>
        <p>
          The cost of mistakes is also asymmetric. A direct unsafe-to-safe miss
          matters much more than a safe-to-review escalation, so the evaluation
          should not optimise for raw agreement alone. It should pay more attention
          to the high-cost error types and treat review-boundary disagreements
          differently from genuinely dangerous misses.
        </p>
        <p>
          Some of the LLM's more cautious calls also look like evidence problems
          rather than model failures. Missing titles, sparse page metadata, and
          limited surrounding context make it harder to classify UGC or ambiguous
          placements confidently, so improving metadata retrieval would likely help
          before any major model change.
        </p>
        <div class="commentary-subsection">
          <h3>Productionising</h3>
          <p>
            In production, a hybrid design is likely to work better than a clean
            replacement of rules with an LLM. Deterministic rules can stay as the
            first layer for obvious hard-unsafe or clearly safe cases, while the
            LLM is used for context-heavy borderline placements and for cases where
            the evidence is too weak for automation alone. Decisions should be
            cached at the page level so the same URL does not trigger repeated
            model calls, and ambiguous cases should first try to pull in richer
            page context such as titles, snippets, or other metadata before paying
            for inference. Higher-value or higher-risk placements can then escalate
            to a stronger model when a cheap pass is still uncertain, and the final
            decision should be stored with its evidence so it can be reused,
            audited, and refreshed when policy changes.
          </p>
        </div>
      </div>
    </section>

    <section class="panel" id="raw-predictions">
      <div class="toolbar">
        <h2>Raw Predictions</h2>
        <span class="muted">
          <span id="visible-count">{total_rows:,}</span>
          visible of {total_rows:,} rows
        </span>
      </div>
      <div class="filters">
        <label>Search
          <input
            id="search"
            type="search"
            placeholder="Topic, advertiser, rationale..."
          >
        </label>
        <label>Advertiser
          <select id="advertiser-filter">{advertiser_options}</select>
        </label>
        <label>Topic
          <select id="topic-filter">{topic_options}</select>
        </label>
        <label>Rules decision
          <select id="rules-filter">{rules_options}</select>
        </label>
        <label>LLM decision
          <select id="llm-filter">{llm_options}</select>
        </label>
        <label>Match
          <select id="match-filter">
            <option value="">All</option>
            <option value="true">Matches only</option>
            <option value="false">Mismatches only</option>
          </select>
        </label>
      </div>
      <p class="muted">
        Raw comparison CSV: {html.escape(str(comparison_output_path))}
      </p>
      <div class="table-wrap">
        <table id="comparison-table" class="comparison-like-table">
          {_comparison_colgroup()}
          <thead>
            <tr>
              <th>Details</th>
              <th><button data-sort-column="1">Placement ID</button></th>
              <th><button data-sort-column="2">URL</button></th>
              <th><button data-sort-column="3">Rules</button></th>
              <th><button data-sort-column="4">LLM</button></th>
              <th><button data-sort-column="5">Match</button></th>
            </tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </table>
      </div>
    </section>
  </main>
  <script>
    const filters = {{
      search: document.getElementById("search"),
      topic: document.getElementById("topic-filter"),
      advertiser: document.getElementById("advertiser-filter"),
      rules: document.getElementById("rules-filter"),
      llm: document.getElementById("llm-filter"),
      match: document.getElementById("match-filter"),
    }};
    const rows = Array.from(
      document.querySelectorAll("#comparison-table tbody tr.data-row")
    );
    const tbody = document.querySelector("#comparison-table tbody");
    const sortButtons = Array.from(document.querySelectorAll("[data-sort-column]"));
    const visibleCount = document.getElementById("visible-count");

    function applyFilters() {{
      const query = filters.search.value.trim().toLowerCase();
      let visible = 0;
      for (const row of rows) {{
        const matchesQuery = !query || row.textContent.toLowerCase().includes(query);
        const matchesTopic =
          !filters.topic.value ||
          row.dataset.topic === filters.topic.value;
        const matchesAdvertiser =
          !filters.advertiser.value ||
          row.dataset.advertiser === filters.advertiser.value;
        const matchesRules =
          !filters.rules.value ||
          row.dataset.rules === filters.rules.value;
        const matchesLlm = !filters.llm.value || row.dataset.llm === filters.llm.value;
        const matchesMatch =
          !filters.match.value ||
          row.dataset.match === filters.match.value;
        const shouldShow =
          matchesQuery &&
          matchesTopic &&
          matchesAdvertiser &&
          matchesRules &&
          matchesLlm &&
          matchesMatch;
        row.hidden = !shouldShow;
        const detailRow = document.getElementById(row.dataset.detailId);
        if (!shouldShow) detailRow.hidden = true;
        if (shouldShow) visible += 1;
      }}
      visibleCount.textContent = visible.toLocaleString();
    }}

    Object.values(filters).forEach((element) => {{
      element.addEventListener("input", applyFilters);
      element.addEventListener("change", applyFilters);
    }});

    function sortRows(columnIndex, direction) {{
      const multiplier = direction === "asc" ? 1 : -1;
      rows.sort((left, right) => {{
        const leftValue = left.children[columnIndex].textContent.trim();
        const rightValue = right.children[columnIndex].textContent.trim();
        const leftNumber = Number(leftValue.replaceAll(",", ""));
        const rightNumber = Number(rightValue.replaceAll(",", ""));
        const bothNumeric = !Number.isNaN(leftNumber) && !Number.isNaN(rightNumber);
        if (bothNumeric) return (leftNumber - rightNumber) * multiplier;
        return leftValue.localeCompare(
          rightValue,
          undefined,
          {{ sensitivity: "base" }}
        ) * multiplier;
      }});
      rows.forEach((row) => {{
        tbody.appendChild(row);
        tbody.appendChild(document.getElementById(row.dataset.detailId));
      }});
    }}

    sortButtons.forEach((button) => {{
      button.addEventListener("click", () => {{
        const columnIndex = Number(button.dataset.sortColumn);
        const currentDirection = button.dataset.sortDirection;
        const nextDirection = currentDirection === "asc" ? "desc" : "asc";
        sortButtons.forEach((otherButton) => {{
          delete otherButton.dataset.sortDirection;
        }});
        button.dataset.sortDirection = nextDirection;
        sortRows(columnIndex, nextDirection);
        applyFilters();
      }});
    }});

    document.querySelectorAll(".expand-button").forEach((button) => {{
      button.addEventListener("click", () => {{
        const detailRow = document.getElementById(button.dataset.detailId);
        if (!detailRow) return;
        const isExpanded = button.getAttribute("aria-expanded") === "true";
        detailRow.hidden = isExpanded;
        button.setAttribute("aria-expanded", String(!isExpanded));
        button.textContent = isExpanded ? "Show" : "Hide";
      }});
    }});
  </script>
</body>
</html>
"""


def _contents_list() -> str:
    links = [
        ("summary", "Summary"),
        ("decisions", "Decisions"),
        ("confidences", "Confidences"),
        ("discrepancies", "Discrepancies"),
        ("commentary", "Commentary"),
        ("raw-predictions", "Raw Predictions"),
    ]
    items = "\n".join(
        (f'<li><a href="#{html.escape(anchor)}">{html.escape(label)}</a></li>')
        for anchor, label in links
    )
    return f"""<nav class="contents-nav" aria-label="Contents">
  <p class="contents-title">Contents</p>
  <ul class="contents-list">
    {items}
  </ul>
</nav>"""


def _analysis_box(placeholder_text: str) -> str:
    return f"""<div class="analysis-box">
  <p class="analysis-title">Analysis</p>
  <p class="analysis-body">{html.escape(placeholder_text)}</p>
</div>"""


def _metric_card(label: str, value: int | str) -> str:
    return (
        '<div class="card">'
        f'<div class="card-label">{html.escape(label)}</div>'
        f'<div class="card-value">{html.escape(_format_value(value))}</div>'
        "</div>"
    )


def _format_value(value: int | str) -> str:
    if isinstance(value, int):
        return f"{value:,}"
    return value


def _select_options(comparison: pd.DataFrame, column: str) -> str:
    values = sorted(
        str(value) for value in comparison[column].dropna().unique() if str(value)
    )
    options = ['<option value="">All</option>']
    options.extend(
        f'<option value="{html.escape(value)}">{html.escape(value)}</option>'
        for value in values
    )
    return "\n".join(options)


def _decision_matrix(comparison: pd.DataFrame) -> pd.DataFrame:
    decisions = ["safe", "review", "unsafe", "unassessed"]
    normalized = comparison.assign(
        safety_decision=_normalize_decisions(comparison["safety_decision"]),
        llm_safety_decision=_normalize_decisions(comparison["llm_safety_decision"]),
    )
    matrix = pd.crosstab(
        normalized["safety_decision"],
        normalized["llm_safety_decision"],
        dropna=False,
    )
    return matrix.reindex(index=decisions, columns=decisions, fill_value=0)


def _normalize_decisions(decisions: pd.Series) -> pd.Series:
    return decisions.fillna("unassessed").replace("", "unassessed")


def _decision_matrix_table(matrix: pd.DataFrame) -> str:
    matrix_with_totals = matrix.copy()
    matrix_with_totals["total"] = matrix_with_totals.sum(axis=1)
    matrix_with_totals.loc["total"] = matrix_with_totals.sum(axis=0)
    headers = "\n".join(
        f"<th>{html.escape(column)}</th>" for column in matrix_with_totals.columns
    )
    rows = "\n".join(
        _decision_matrix_row(label, values)
        for label, values in matrix_with_totals.iterrows()
    )
    return f"""<table class="matrix-table" aria-label="Decision matrix">
  <thead>
    <tr>
      <th>Rules \\ LLM</th>
      {headers}
    </tr>
  </thead>
  <tbody>
    {rows}
  </tbody>
</table>"""


def _confidence_matrix(comparison: pd.DataFrame) -> pd.DataFrame:
    confidence_levels = ["low", "medium", "high", "unassessed"]
    normalized = comparison.assign(
        safety_confidence=_normalize_confidences(comparison["safety_confidence"]),
        llm_safety_confidence=_normalize_confidences(
            comparison["llm_safety_confidence"]
        ),
    )
    matrix = pd.crosstab(
        normalized["safety_confidence"],
        normalized["llm_safety_confidence"],
        dropna=False,
    )
    return matrix.reindex(
        index=confidence_levels,
        columns=confidence_levels,
        fill_value=0,
    )


def _normalize_confidences(confidences: pd.Series) -> pd.Series:
    return confidences.fillna("unassessed").replace("", "unassessed")


def _confidence_matrix_table(matrix: pd.DataFrame) -> str:
    matrix_with_totals = matrix.copy()
    matrix_with_totals["total"] = matrix_with_totals.sum(axis=1)
    matrix_with_totals.loc["total"] = matrix_with_totals.sum(axis=0)
    headers = "\n".join(
        f"<th>{html.escape(column)}</th>" for column in matrix_with_totals.columns
    )
    rows = "\n".join(
        _decision_matrix_row(label, values)
        for label, values in matrix_with_totals.iterrows()
    )
    return f"""<table class="matrix-table" aria-label="Confidence matrix">
  <thead>
    <tr>
      <th>Rules \\ LLM</th>
      {headers}
    </tr>
  </thead>
  <tbody>
    {rows}
  </tbody>
</table>"""


def _prediction_confidence_distribution(comparison: pd.DataFrame) -> str:
    normalized = comparison.assign(
        safety_confidence=_normalize_confidences(comparison["safety_confidence"]),
        llm_safety_confidence=_normalize_confidences(
            comparison["llm_safety_confidence"]
        ),
    )
    decisions = ["safe", "review", "unsafe"]
    levels = ["low", "medium", "high", "unassessed"]
    legend = "\n".join(
        (
            '<span class="legend-item">'
            f'<span class="legend-swatch confidence-{level}"></span>'
            f"{html.escape(level)}</span>"
        )
        for level in levels
    )
    max_count = max(
        [
            1,
            *[
                int((normalized["safety_decision"] == decision).sum())
                for decision in decisions
            ],
            *[
                int((normalized["llm_safety_decision"] == decision).sum())
                for decision in decisions
            ],
        ]
    )
    groups = "\n".join(
        _prediction_confidence_group(normalized, decision, levels, max_count)
        for decision in decisions
    )
    return f"""<div class="subsection">
  <h3>Prediction distribution by confidence</h3>
  <div class="bar-legend">
    {legend}
  </div>
  <div class="vertical-chart">
    {groups}
  </div>
</div>"""


def _prediction_confidence_group(
    comparison: pd.DataFrame,
    decision: str,
    levels: list[str],
    max_count: int,
) -> str:
    rules_rows = comparison[comparison["safety_decision"] == decision]
    llm_rows = comparison[comparison["llm_safety_decision"] == decision]
    return f"""<div>
  <div class="bar-group">
    <div class="bar-column">
      <div class="stacked-bar-track">
        <div class="stacked-bar-wrapper">
          <div class="bar-value stacked-bar-value">{len(rules_rows):,}</div>
          {
        _stacked_vertical_bar(
            rules_rows["safety_confidence"].value_counts(),
            total_rows=len(rules_rows),
            levels=levels,
            max_count=max_count,
        )
    }
        </div>
      </div>
      <div class="bar-sub-label">Rules</div>
    </div>
    <div class="bar-column">
      <div class="stacked-bar-track">
        <div class="stacked-bar-wrapper">
          <div class="bar-value stacked-bar-value">{len(llm_rows):,}</div>
          {
        _stacked_vertical_bar(
            llm_rows["llm_safety_confidence"].value_counts(),
            total_rows=len(llm_rows),
            levels=levels,
            max_count=max_count,
        )
    }
        </div>
      </div>
      <div class="bar-sub-label">LLM</div>
    </div>
  </div>
  <div class="bar-label">{html.escape(decision)}</div>
</div>"""


def _stacked_vertical_bar(
    counts: pd.Series,
    *,
    total_rows: int,
    levels: list[str],
    max_count: int,
) -> str:
    total_height = _bar_height_px(total_rows, max_count, 160)
    segments = "\n".join(
        _stacked_confidence_segment(
            level,
            int(counts.get(level, 0)),
            total_rows,
        )
        for level in levels
    )
    return f"""<div class="stacked-vertical-bar" style="height: {total_height}px;">
    {segments}
</div>"""


def _stacked_confidence_segment(level: str, count: int, total_rows: int) -> str:
    if total_rows <= 0 or count <= 0:
        return ""

    grow = max(1, count)
    return (
        f'<div class="stack-segment confidence-{html.escape(level)}" '
        f'style="flex-grow: {grow};" '
        f'title="{html.escape(level)}: {count:,} row(s)"></div>'
    )


def _decision_matrix_row(label: str, values: pd.Series) -> str:
    cells = "\n".join(f"<td>{int(value):,}</td>" for value in values)
    return f"""<tr>
  <th>{html.escape(label)}</th>
  {cells}
</tr>"""


def _discrepancies_section(comparison: pd.DataFrame) -> str:
    normalized = _normalized_comparison(comparison)
    safe_unsafe = normalized[
        (
            (normalized["safety_decision"] == "safe")
            & (normalized["llm_safety_decision"] == "unsafe")
        )
        | (
            (normalized["safety_decision"] == "unsafe")
            & (normalized["llm_safety_decision"] == "safe")
        )
    ]
    other_discrepancies = normalized[
        (normalized["safety_decision"] != normalized["llm_safety_decision"])
        & ~normalized.index.isin(safe_unsafe.index)
    ]
    topic_summary = _topic_discrepancy_summary(other_discrepancies)

    return "\n".join(
        [
            _safe_unsafe_table(safe_unsafe),
            _topic_discrepancy_counts(topic_summary),
        ]
    )


def _normalized_comparison(comparison: pd.DataFrame) -> pd.DataFrame:
    return comparison.assign(
        safety_decision=_normalize_decisions(comparison["safety_decision"]),
        llm_safety_decision=_normalize_decisions(comparison["llm_safety_decision"]),
    )


def _safe_unsafe_table(discrepancies: pd.DataFrame) -> str:
    rows = "\n".join(
        _comparison_html_row(row, detail_prefix="safe-unsafe")
        for row in discrepancies.sort_values(
            ["company_name", "topic", "placement_id"]
        ).itertuples(index=False)
    )
    if not rows:
        rows = '<tr><td colspan="6">No safe versus unsafe conflicts.</td></tr>'

    return f"""<div class="subsection">
  <h3>MAJOR: Safe vs unsafe</h3>
  <div class="table-wrap">
  <table class="comparison-like-table">
    {_comparison_colgroup()}
    <thead>
      <tr>
        <th>Details</th>
        <th>Placement ID</th>
        <th>URL</th>
        <th>Rules</th>
        <th>LLM</th>
        <th>Match</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
  </div>
</div>"""


def _topic_discrepancy_summary(discrepancies: pd.DataFrame) -> pd.DataFrame:
    if discrepancies.empty:
        return pd.DataFrame(
            columns=[
                "topic",
                "rows",
                "llm_safer",
                "llm_stricter",
                "decision_pairs",
            ]
        )

    severity = {"safe": 0, "review": 1, "unsafe": 2}
    scored = discrepancies.assign(
        rules_severity=discrepancies["safety_decision"].map(severity),
        llm_severity=discrepancies["llm_safety_decision"].map(severity),
    )
    scored = scored.assign(
        llm_safer=scored["llm_severity"] < scored["rules_severity"],
        llm_stricter=scored["llm_severity"] > scored["rules_severity"],
        decision_pair=(
            scored["safety_decision"] + " -> " + scored["llm_safety_decision"]
        ),
    )

    summary = (
        scored.groupby("topic", dropna=False)
        .agg(
            rows=("placement_id", "size"),
            llm_safer=("llm_safer", "sum"),
            llm_stricter=("llm_stricter", "sum"),
        )
        .reset_index()
    )
    pairs = (
        scored.groupby(["topic", "decision_pair"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values(["topic", "rows", "decision_pair"], ascending=[True, False, True])
    )
    pair_text = (
        pairs.assign(
            pair_count=pairs["decision_pair"] + " (" + pairs["rows"].astype(str) + ")"
        )
        .groupby("topic", dropna=False)["pair_count"]
        .apply(", ".join)
        .reset_index(name="decision_pairs")
    )
    return summary.merge(pair_text, on="topic", how="left").sort_values(
        ["rows", "topic"], ascending=[False, True]
    )


def _topic_discrepancy_counts(topic_counts: pd.DataFrame) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(row.topic))}</td>"
        f"<td>{int(row.rows):,}</td>"
        f"<td>{int(row.llm_safer):,}</td>"
        f"<td>{int(row.llm_stricter):,}</td>"
        f"<td>{html.escape(str(row.decision_pairs))}</td>"
        "</tr>"
        for row in topic_counts.itertuples(index=False)
    )
    if not rows:
        rows = '<tr><td colspan="5">No other discrepancies.</td></tr>'

    return f"""<div class="subsection">
  <h3>MINOR: Other discrepancies (by topic)</h3>
  <table class="simple-table">
    <thead>
      <tr>
        <th>Topic</th>
        <th>Rows</th>
        <th>LLM safer</th>
        <th>LLM stricter</th>
        <th>Decision pairs</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</div>"""


def _prediction_distribution(comparison: pd.DataFrame) -> str:
    decisions = ["safe", "review", "unsafe"]
    rules_counts = comparison["safety_decision"].value_counts()
    llm_counts = comparison["llm_safety_decision"].value_counts()
    max_count = max(
        [
            1,
            *[int(rules_counts.get(decision, 0)) for decision in decisions],
            *[int(llm_counts.get(decision, 0)) for decision in decisions],
        ]
    )
    groups = "\n".join(
        _prediction_distribution_group(
            decision,
            int(rules_counts.get(decision, 0)),
            int(llm_counts.get(decision, 0)),
            max_count,
        )
        for decision in decisions
    )
    safe_comment = _safe_prediction_comment(
        int(rules_counts.get("safe", 0)),
        int(llm_counts.get("safe", 0)),
    )

    return f"""<div class="subsection">
  <h3>Prediction distribution</h3>
  <div class="bar-legend">
    <span class="legend-item">
      <span class="legend-swatch rules-bar"></span>Rules based
    </span>
    <span class="legend-item">
      <span class="legend-swatch llm-bar"></span>LLM
    </span>
  </div>
  <div class="vertical-chart">
    {groups}
  </div>
  <p class="matrix-note">{safe_comment}</p>
</div>"""


def _prediction_distribution_group(
    decision: str,
    rules_count: int,
    llm_count: int,
    max_count: int,
) -> str:
    max_height_px = 160
    rules_height = _bar_height_px(rules_count, max_count, max_height_px)
    llm_height = _bar_height_px(llm_count, max_count, max_height_px)
    return f"""<div>
  <div class="bar-group">
    <div>
      <div class="bar-value">{rules_count:,}</div>
      <div
        class="vertical-bar rules-bar"
        style="height: {rules_height}px;"
      ></div>
    </div>
    <div>
      <div class="bar-value">{llm_count:,}</div>
      <div
        class="vertical-bar llm-bar"
        style="height: {llm_height}px;"
      ></div>
    </div>
  </div>
  <div class="bar-label">{html.escape(decision)}</div>
</div>"""


def _bar_height_px(count: int, max_count: int, max_height_px: int) -> int:
    if count == 0:
        return 0
    return max(2, round((count / max_count) * max_height_px))


def _safe_prediction_comment(rules_safe: int, llm_safe: int) -> str:
    if rules_safe > llm_safe:
        return "Rules based scoring assigns safe more readily than the LLM."
    if llm_safe > rules_safe:
        return "The LLM assigns safe more readily than rules based scoring."
    return "Rules based scoring and the LLM assign safe equally often."


def _comparison_colgroup() -> str:
    return """<colgroup>
  <col style="width: 12%;">
  <col style="width: 12%;">
  <col style="width: 44%;">
  <col style="width: 11%;">
  <col style="width: 11%;">
  <col style="width: 10%;">
</colgroup>"""


def _comparison_html_row(row, *, detail_prefix: str) -> str:
    match = str(bool(row.decision_match)).lower()
    rules_decision = str(row.safety_decision)
    llm_decision = str(row.llm_safety_decision)
    detail_id = f"{detail_prefix}-details-{html.escape(str(row.placement_id))}"
    topic = html.escape(str(row.topic))
    advertiser = html.escape(str(row.company_name))
    placement_id = html.escape(str(row.placement_id))
    url = html.escape(str(row.url))
    rules_confidence = _escaped_optional_value(row.safety_confidence, fallback="None")
    rules_risks = _escaped_optional_value(row.risk_categories)
    rules_signals = _escaped_optional_value(row.matched_signals)
    rules_signal_explanations = _escaped_optional_value(
        getattr(row, "rules_signal_explanations", "")
    )
    llm_confidence = _escaped_optional_value(
        row.llm_safety_confidence,
        fallback="None",
    )
    llm_risks = _escaped_optional_value(row.llm_risk_categories, fallback="None")
    llm_rationale = _escaped_optional_value(row.llm_safety_rationale)
    match_label = html.escape("yes" if row.decision_match else "no")
    return f"""<tr class="data-row" data-topic="{topic}" data-advertiser="{advertiser}"
  data-rules="{html.escape(rules_decision)}"
  data-llm="{html.escape(llm_decision)}" data-match="{match}"
  data-detail-id="{detail_id}">
  <td>
    <button
      class="expand-button"
      data-detail-id="{detail_id}"
      aria-expanded="false"
    >Show</button>
  </td>
  <td title="{placement_id}">{placement_id}</td>
  <td title="{url}"><a href="{url}" target="_blank" rel="noreferrer">{url}</a></td>
  <td title="{html.escape(rules_decision)}">{_decision_pill(rules_decision)}</td>
  <td title="{html.escape(llm_decision)}">{_decision_pill(llm_decision)}</td>
  <td title="{match_label}">{match_label}</td>
</tr>
<tr class="detail-row" id="{detail_id}" hidden>
  <td colspan="6">
    <div class="details">
      {_detail_item("Advertiser", advertiser)}
      {_detail_item("Topic", topic)}
      {_detail_item("URL", _external_link(url))}
      {_detail_item("Rules confidence", rules_confidence)}
      {_detail_item("Rules risks", rules_risks)}
      {
        _detail_item(
            "Rules trigger evidence",
            rules_signal_explanations or rules_signals,
        )
    }
      {_detail_item("LLM confidence", llm_confidence)}
      {_detail_item("LLM risks", llm_risks)}
      {_detail_item("LLM rationale", llm_rationale)}
    </div>
  </td>
</tr>"""


def _detail_item(label: str, value: str) -> str:
    return (
        "<div>"
        f'<div class="detail-label">{html.escape(label)}</div>'
        f'<div class="detail-value">{value}</div>'
        "</div>"
    )


def _escaped_optional_value(value: object, *, fallback: str = "") -> str:
    if pd.isna(value):
        return html.escape(fallback)

    text = str(value)
    if not text:
        return html.escape(fallback)

    return html.escape(text)


def _external_link(url: str) -> str:
    return f'<a href="{url}" target="_blank" rel="noreferrer">{url}</a>'


def _decision_pill(decision: str) -> str:
    css_class = "decision-" + "".join(
        character for character in decision.lower() if character.isalnum()
    )
    return f'<span class="pill {css_class}">{html.escape(decision)}</span>'
