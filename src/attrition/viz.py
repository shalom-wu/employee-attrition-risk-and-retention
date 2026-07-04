"""Shared chart style: one palette, clean labels, presentation-ready output."""

import matplotlib.pyplot as plt
import seaborn as sns

NAVY = "#1E2761"
CORAL = "#E14B4B"
ICE = "#A9C2EE"
MUTED = "#5A6178"
GRID = "#E2E8F0"
PALETTE = [NAVY, CORAL, ICE, "#7A8BC4", "#F0A05A"]


def apply_style() -> None:
    """Set the project-wide matplotlib/seaborn style."""
    sns.set_theme(
        style="whitegrid",
        palette=PALETTE,
        rc={
            "figure.dpi": 150,
            "savefig.dpi": 150,
            "savefig.bbox": "tight",
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.titlecolor": "#232946",
            "axes.labelsize": 11,
            "axes.labelcolor": MUTED,
            "axes.edgecolor": GRID,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "grid.color": GRID,
            "grid.linewidth": 0.6,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "legend.frameon": False,
        },
    )


def rate_barplot(table, xcol, title, path, company_avg, rotate=0):
    """Attrition-rate bar chart with a company-average reference line.

    Bars always start at 0 (no truncated axes) and carry value labels.
    """
    fig, ax = plt.subplots(figsize=(8, 4.2))
    bars = ax.bar(table[xcol].astype(str), table["attrition_rate"], color=NAVY)
    ax.axhline(company_avg * 100, color=CORAL, ls="--", lw=1.4,
               label=f"Company average {company_avg:.1%}")
    for b, v in zip(bars, table["attrition_rate"]):
        ax.annotate(f"{v:.0f}%", (b.get_x() + b.get_width() / 2, v),
                    ha="center", va="bottom", fontsize=10, color="#232946",
                    fontweight="bold")
    ax.set_ylabel("Attrition rate (%)")
    ax.set_ylim(0, max(table["attrition_rate"].max(), company_avg * 100) * 1.18)
    ax.set_title(title, loc="left", pad=12)
    ax.legend(loc="upper right")
    if rotate:
        plt.setp(ax.get_xticklabels(), rotation=rotate, ha="right")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
