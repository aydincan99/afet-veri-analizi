import pandas as pd


def compute_region_risk_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Compute a simple risk score per region based on frequency and severity.

    The score combines:
    - Normalized event frequency
    - Normalized average magnitude / severity
    - Normalized average affected people
    - Normalized average economic damage

    This is intentionally simple and is meant as an educational example,
    not a scientifically validated risk model.
    """
    # Aggregate metrics by location
    grouped = df.groupby("location").agg(
        event_count=("location", "size"),
        avg_magnitude=("magnitude", "mean"),
        avg_affected_people=("affected_people", "mean"),
        avg_economic_damage=("economic_damage", "mean"),
        latitude=("latitude", "mean"),
        longitude=("longitude", "mean"),
    )

    # Avoid division by zero by adding a small epsilon
    eps = 1e-9

    # Normalize each component to 0–1
    def normalize(series: pd.Series) -> pd.Series:
        return (series - series.min()) / (series.max() - series.min() + eps)

    grouped["freq_score"] = normalize(grouped["event_count"])
    grouped["magnitude_score"] = normalize(grouped["avg_magnitude"])
    grouped["impact_people_score"] = normalize(grouped["avg_affected_people"])
    grouped["impact_econ_score"] = normalize(grouped["avg_economic_damage"])

    # Weighted sum to get final risk score
    grouped["risk_score"] = (
        0.3 * grouped["freq_score"]
        + 0.3 * grouped["magnitude_score"]
        + 0.2 * grouped["impact_people_score"]
        + 0.2 * grouped["impact_econ_score"]
    )

    return grouped.sort_values("risk_score", ascending=False).reset_index()

