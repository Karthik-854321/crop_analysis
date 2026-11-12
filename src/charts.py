import matplotlib.pyplot as plt
import pandas as pd

_INK = "#263b2f"
_MUTED = "#718075"
_GREEN = "#3f704f"
_GOLD = "#c39a4a"
_GRID = "#dce3d6"
_PAPER = "#f5f4ed"


def _style_axes(ax):
    ax.set_facecolor(_PAPER)
    ax.title.set_color(_INK)
    ax.title.set_fontweight("semibold")
    ax.xaxis.label.set_color(_MUTED)
    ax.yaxis.label.set_color(_MUTED)
    ax.tick_params(colors=_MUTED, labelsize=9)
    ax.grid(True, color=_GRID, linewidth=0.8, alpha=0.8)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)


def _empty_chart(message):
    fig, ax = plt.subplots(figsize=(9, 4), facecolor=_PAPER)
    ax.text(0.5, 0.5, message, ha="center", va="center", transform=ax.transAxes, color=_MUTED)
    ax.set_axis_off()
    fig.tight_layout()
    return fig


def production_trend(df):
    if df.empty or df["production"].dropna().empty:
        return _empty_chart("No production values available")
    grouped = df.groupby("year", as_index=False)["production"].sum(min_count=1).sort_values("year")
    fig, ax = plt.subplots(figsize=(10, 4), facecolor=_PAPER)
    ax.plot(
        grouped["year"],
        grouped["production"],
        color=_GREEN,
        linewidth=2.8,
        marker="o",
        markersize=6,
        markerfacecolor=_GOLD,
        markeredgecolor=_PAPER,
        markeredgewidth=1.5,
    )
    ax.set_title("Total recorded production by year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Production (source units)")
    _style_axes(ax)
    fig.tight_layout()
    return fig


def yield_trend(df):
    if df.empty or "yield" not in df or df["yield"].dropna().empty:
        return _empty_chart("Yield unavailable: check positive area and compatible units")
    grouped = df.groupby("year", as_index=False)["yield"].mean().sort_values("year")
    fig, ax = plt.subplots(figsize=(8, 4), facecolor=_PAPER)
    ax.plot(
        grouped["year"],
        grouped["yield"],
        color=_GREEN,
        linewidth=2.8,
        marker="o",
        markersize=6,
        markerfacecolor=_GOLD,
        markeredgecolor=_PAPER,
        markeredgewidth=1.5,
    )
    ax.set_title("Mean record-level yield by year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Production / area (source units)")
    _style_axes(ax)
    fig.tight_layout()
    return fig


def region_comparison(df):
    if df.empty or df["production"].dropna().empty:
        return _empty_chart("No production values available")
    grouped = df.groupby("region")["production"].sum().sort_values(ascending=False).head(12)
    fig, ax = plt.subplots(figsize=(8, 4), facecolor=_PAPER)
    grouped.sort_values().plot(kind="barh", ax=ax, color=_GREEN, edgecolor="none", width=0.68)
    ax.set_title("Production by region (selected records)")
    ax.set_xlabel("Production (source units)")
    ax.set_ylabel("Region")
    ax.grid(True, axis="x", color=_GRID, linewidth=0.8, alpha=0.8)
    ax.grid(False, axis="y")
    _style_axes(ax)
    fig.tight_layout()
    return fig
