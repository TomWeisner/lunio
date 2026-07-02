"""Generate focused EDA tables for the placement safety task.

Run from the project root with:

    poetry run python -m lunio.data.analysis.eda
"""

import pandas as pd

from lunio.paths import CLEAN_DATA_DIR, REPORTS_DIR

FULL_DATA_PATH = CLEAN_DATA_DIR / "full_data.csv"
EDA_OUTPUT_PATH = REPORTS_DIR / "eda_raw_data_summary.md"


def build_eda_summary() -> str:
    """Return a compact Markdown EDA summary."""

    data = pd.read_csv(FULL_DATA_PATH)
    data["invalid_click_rate"] = data["invalid_clicks"] / data["clicks"]

    company_summary = _summarise(
        data,
        by="company_name",
        sort_column="invalid_click_rate",
        include_click_share=True,
    )
    channel_summary = _summarise(
        data,
        by="channel_type",
        sort_column="rows",
    )
    topic_summary = _summarise(
        data,
        by="topic",
        sort_column="invalid_click_rate",
    ).head(7)
    company_topic_concentrations = _company_topic_click_concentrations(data)
    highest_company_topic_concentrations = company_topic_concentrations.head(7)
    lowest_company_topic_concentrations = company_topic_concentrations.sort_values(
        ["company_adjusted_topic_click_index", "invalid_click_index", "rows"],
        ascending=[True, True, False],
    ).head(7)
    topic_company_click_share = _topic_company_click_share(data)

    return "\n\n".join(
        [
            "# Raw Data: Placement Safety EDA",
            "## Objective",
            (
                "This EDA focuses on the advertiser, topic, channel, and "
                "click-quality signals that matter for advertiser-specific "
                "placement safety."
            ),
            "## Dataset Shape",
            f"- Rows: {len(data):,}",
            f"- Columns: {len(data.columns):,}",
            "## Advertiser Summary",
            _to_markdown_table(company_summary.reset_index()),
            "## Channel Summary",
            _to_markdown_table(channel_summary.reset_index()),
            "## Highest Invalid-Click-Rate Topics",
            _to_markdown_table(topic_summary.reset_index()),
            "## Advertiser x Topic Click Concentration",
            (
                "This table normalises topic-level click volume against each "
                "advertiser's average placement. `click_index` above 1 means the "
                "topic receives more clicks per placement than that advertiser "
                "usually receives; `invalid_click_index` does the same for invalid "
                "click volume. `topic_click_index` compares the advertiser-topic "
                "average with the average clicks per placement for that same topic "
                "across every advertiser in the dataset; above 1 means this "
                "advertiser is over-indexing on that topic. "
                "`company_adjusted_topic_click_index` compares the advertiser-topic "
                "average with the expected average after accounting for both the "
                "advertiser's baseline click volume and the topic's baseline click "
                "volume."
            ),
            ("Sorted by highest `company_adjusted_topic_click_index`."),
            _to_markdown_table(highest_company_topic_concentrations),
            "## Advertiser x Topic Low Click Concentration",
            (
                "The same normalised view, sorted by lowest "
                "`company_adjusted_topic_click_index`. These rows show topics "
                "receiving fewer clicks per placement than expected after accounting "
                "for both advertiser and topic baselines."
            ),
            _to_markdown_table(lowest_company_topic_concentrations),
            "## Topic x Advertiser Click Share",
            (
                "This table flips the perspective from advertiser-first to "
                "topic-first. Each row is a topic, each advertiser column is that "
                "advertiser's share of clicks for the topic, and `topic_clicks` is "
                "the total click volume for that topic. Rows are sorted by highest "
                "topic click volume."
            ),
            _to_markdown_table(topic_company_click_share),
        ]
    )


def write_eda_summary() -> None:
    """Write the EDA summary to reports."""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    EDA_OUTPUT_PATH.write_text(build_eda_summary(), encoding="utf-8")


def _summarise(
    data: pd.DataFrame,
    *,
    by: str,
    sort_column: str,
    include_click_share: bool = False,
) -> pd.DataFrame:
    summary = data.groupby(by).agg(
        rows=("placement_id", "count"),
        clicks=("clicks", "sum"),
        invalid_clicks=("invalid_clicks", "sum"),
    )
    summary["invalid_click_rate"] = summary["invalid_clicks"] / summary["clicks"]
    if include_click_share:
        summary["click_share"] = summary["clicks"] / summary["clicks"].sum()
    return summary.sort_values(sort_column, ascending=False)


def _company_topic_click_concentrations(data: pd.DataFrame) -> pd.DataFrame:
    global_avg_clicks = data["clicks"].mean()
    company_baseline = (
        data.groupby("company_name")
        .agg(
            company_avg_clicks=("clicks", "mean"),
            company_avg_invalid_clicks=("invalid_clicks", "mean"),
        )
        .reset_index()
    )
    topic_baseline = (
        data.groupby("topic")
        .agg(
            topic_avg_clicks=("clicks", "mean"),
            topic_avg_invalid_clicks=("invalid_clicks", "mean"),
        )
        .reset_index()
    )
    topic_summary = (
        data.groupby(["company_name", "topic"])
        .agg(
            rows=("placement_id", "count"),
            avg_clicks=("clicks", "mean"),
            avg_invalid_clicks=("invalid_clicks", "mean"),
            invalid_click_rate=("invalid_click_rate", "mean"),
        )
        .reset_index()
    )
    anomalies = topic_summary.merge(company_baseline, on="company_name", how="left")
    anomalies = anomalies.merge(topic_baseline, on="topic", how="left")
    anomalies["click_index"] = anomalies["avg_clicks"] / anomalies["company_avg_clicks"]
    anomalies["invalid_click_index"] = (
        anomalies["avg_invalid_clicks"] / anomalies["company_avg_invalid_clicks"]
    )
    anomalies["topic_click_index"] = (
        anomalies["avg_clicks"] / anomalies["topic_avg_clicks"]
    )
    anomalies["company_adjusted_topic_click_index"] = anomalies["click_index"] / (
        anomalies["topic_avg_clicks"] / global_avg_clicks
    )
    anomalies["topic_invalid_click_index"] = (
        anomalies["avg_invalid_clicks"] / anomalies["topic_avg_invalid_clicks"]
    )

    return anomalies[
        [
            "company_name",
            "topic",
            "rows",
            "avg_clicks",
            "company_avg_clicks",
            "click_index",
            "topic_avg_clicks",
            "topic_click_index",
            "company_adjusted_topic_click_index",
            "avg_invalid_clicks",
            "company_avg_invalid_clicks",
            "invalid_click_index",
            "topic_avg_invalid_clicks",
            "topic_invalid_click_index",
            "invalid_click_rate",
        ]
    ].sort_values(
        ["company_adjusted_topic_click_index", "invalid_click_index", "rows"],
        ascending=False,
    )


def _topic_company_click_share(data: pd.DataFrame) -> pd.DataFrame:
    topic_totals = (
        data.groupby("topic")
        .agg(
            topic_clicks=("clicks", "sum"),
            topic_invalid_clicks=("invalid_clicks", "sum"),
        )
        .reset_index()
    )
    topic_company_clicks = (
        data.groupby(["topic", "company_name"])
        .agg(
            clicks=("clicks", "sum"),
        )
        .reset_index()
    )

    shares = topic_company_clicks.merge(topic_totals, on="topic", how="left")
    shares["click_share"] = shares["clicks"] / shares["topic_clicks"]

    pivot = shares.pivot(
        index="topic",
        columns="company_name",
        values="click_share",
    ).fillna(0)
    return (
        topic_totals[["topic", "topic_clicks"]]
        .merge(pivot.reset_index(), on="topic", how="left")
        .sort_values("topic_clicks", ascending=False)
    )


def _to_markdown_table(dataframe: pd.DataFrame) -> str:
    formatted = dataframe.copy()
    for column in formatted.select_dtypes(include="float").columns:
        if column.endswith("_share"):
            formatted[column] = formatted[column].map(lambda value: f"{value:.1%}")
        else:
            formatted[column] = formatted[column].map(lambda value: f"{value:.3f}")

    headers = [str(column) for column in formatted.columns]
    rows = [
        [str(value) for value in row]
        for row in formatted.itertuples(index=False, name=None)
    ]
    separator = ["---"] * len(headers)
    table_rows = [headers, separator, *rows]
    return "\n".join("| " + " | ".join(row) + " |" for row in table_rows)


if __name__ == "__main__":
    write_eda_summary()
