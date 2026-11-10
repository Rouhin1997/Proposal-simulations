#!/usr/bin/env python3
"""Adaptive multimodal pulsar-search resource simulation.

This is the current proposal model. It compares only:
    - TD only
    - Multimodal

The multimodal branch includes a scalable/adaptive interferometric evidence layer:
a coarse reconstruction is always performed, while additional reconstruction/
candidate extraction is spent only in proportion to image-informative sources.

The source populations and search-response kernels are frozen from the 400
GC-like realizations used to develop the proposal. This isolates the effect of
the scalable imaging-resource model from changes in the underlying pulsar
population.

This is a qualitative resource-allocation toy model, not a MeerKAT/SKA yield or
runtime forecast.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
RESULTS.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)

N_PULSARS = 20
MAX_IMAGING_COST = 8.0
COARSE_IMAGING_COST = 2.0
BASE_RECONSTRUCTION_SHARE = 0.25

CATEGORIES = [
    "Standard / ordinary",
    "Image-visible scintillator",
    "Image-visible intermittent",
    "Image-visible eclipsing",
    "Compact binary",
    "Extreme binary",
]
INFO_COLUMNS = [
    "Image-visible scintillator",
    "Image-visible intermittent",
    "Image-visible eclipsing",
]

population = pd.read_csv(DATA / "population_realizations.csv").set_index("repeat")
kernel = np.load(DATA / "search_response_kernel.npz")

repeats = kernel["repeats"].astype(int)
fractions = kernel["fractions"].astype(float)
td_overall = kernel["td_overall"]
evidence_overall = kernel["evidence_response_overall"]

X = population.loc[repeats, "X_td_all"].to_numpy(float)
n_info = population.loc[repeats, INFO_COLUMNS].sum(axis=1).to_numpy(float)

imaging_cost = (
    COARSE_IMAGING_COST
    + (MAX_IMAGING_COST - COARSE_IMAGING_COST) * (n_info / N_PULSARS)
)

def interp_rows(values, xeff):
    """Interpolate one recovery curve per Monte-Carlo realization."""
    xeff = np.asarray(xeff, dtype=float)
    if xeff.ndim == 0:
        xeff = np.full(values.shape[0], xeff)
    out = np.empty(values.shape[0])
    xp = np.r_[0.0, fractions]
    for i in range(values.shape[0]):
        out[i] = np.interp(
            np.clip(xeff[i], 0.0, 1.0),
            xp,
            np.r_[0.0, values[i]],
        )
    return out

def interp_rows_nan(values, xeff):
    """As above, preserving realizations that contain no source of a class."""
    xeff = np.asarray(xeff, dtype=float)
    if xeff.ndim == 0:
        xeff = np.full(values.shape[0], xeff)
    out = np.full(values.shape[0], np.nan)
    for i in range(values.shape[0]):
        valid = ~np.isnan(values[i])
        if not np.any(valid):
            continue
        xp = np.r_[0.0, fractions[valid]]
        yp = np.r_[0.0, values[i, valid]]
        out[i] = np.interp(np.clip(xeff[i], 0.0, 1.0), xp, yp)
    return out

curve_rows = []
repeat_rows = []

for f in fractions[fractions <= 0.9]:
    j = np.where(np.isclose(fractions, f))[0][0]
    f_eff = f + (MAX_IMAGING_COST - imaging_cost) / X

    td_vals = td_overall[:, j]
    mm_vals = interp_rows(evidence_overall, f_eff)

    curve_rows.append({
        "resource_fraction": f,
        "TD_only_mean": td_vals.mean(),
        "Multimodal_mean": mm_vals.mean(),
        "gain_percentage_points": 100.0 * (mm_vals.mean() - td_vals.mean()),
    })

    for r, tdv, mmv in zip(repeats, td_vals, mm_vals):
        repeat_rows.append({
            "repeat": r,
            "resource_fraction": f,
            "TD_only": tdv,
            "Multimodal": mmv,
        })

curve = pd.DataFrame(curve_rows)
curve.to_csv(RESULTS / "overall_recovery_curve.csv", index=False)
pd.DataFrame(repeat_rows).to_csv(RESULTS / "per_realisation_recovery.csv", index=False)

class_rows = []
proposal_regimes = [("Low", 0.1), ("Moderate", 0.4), ("High", 0.8)]

for regime, f in proposal_regimes:
    j = np.where(np.isclose(fractions, f))[0][0]
    f_eff = f + (MAX_IMAGING_COST - imaging_cost) / X

    for i, category in enumerate(CATEGORIES):
        td_class = kernel[f"td_class_{i}"]
        evidence_class = kernel[f"evidence_class_{i}"]

        td_vals = td_class[:, j]
        mm_vals = interp_rows_nan(evidence_class, f_eff)

        class_rows.append({
            "regime": regime,
            "resource_fraction": f,
            "class": category,
            "TD_only": np.nanmean(td_vals),
            "Multimodal": np.nanmean(mm_vals),
            "gain_percentage_points":
                100.0 * (np.nanmean(mm_vals) - np.nanmean(td_vals)),
        })

for category in CATEGORIES:
    class_rows.append({
        "regime": "Exhaustive",
        "resource_fraction": np.nan,
        "class": category,
        "TD_only": 1.0,
        "Multimodal": 1.0,
        "gain_percentage_points": 0.0,
    })

class_df = pd.DataFrame(class_rows)
class_df.to_csv(RESULTS / "class_recovery_proposal_regimes.csv", index=False)

sensitivity_rows = []
break_even_rows = []
cost_grid = np.linspace(0.0, 0.60, 601)

for f in fractions[(fractions >= 0.1) & (fractions <= 0.9)]:
    j = np.where(np.isclose(fractions, f))[0][0]
    td_mean = td_overall[:, j].mean()
    acceptable = []

    for full_imaging_cost in cost_grid:
        adaptive_fraction = full_imaging_cost * (
            BASE_RECONSTRUCTION_SHARE
            + (1.0 - BASE_RECONSTRUCTION_SHARE) * (n_info / N_PULSARS)
        )

        f_eff = f - adaptive_fraction + (MAX_IMAGING_COST / X)
        mm_mean = interp_rows(evidence_overall, f_eff).mean()

        sensitivity_rows.append({
            "resource_fraction": f,
            "full_imaging_cost_fraction_of_X": full_imaging_cost,
            "TD_only": td_mean,
            "Multimodal": mm_mean,
            "gain_percentage_points": 100.0 * (mm_mean - td_mean),
        })

        if mm_mean >= td_mean:
            acceptable.append(full_imaging_cost)

    break_even_rows.append({
        "resource_fraction": f,
        "break_even_full_imaging_cost_fraction_of_X":
            max(acceptable) if acceptable else np.nan,
    })

pd.DataFrame(sensitivity_rows).to_csv(
    RESULTS / "imaging_cost_sensitivity.csv", index=False
)
break_even = pd.DataFrame(break_even_rows)
break_even.to_csv(RESULTS / "break_even_imaging_cost.csv", index=False)

plt.rcParams.update({
    "font.size": 10.5,
    "axes.titlesize": 11.5,
    "axes.labelsize": 11,
    "legend.fontsize": 10,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 9,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

short_labels = ["Standard", "Scint.", "Interm.", "Eclipse", "Compact\nbinary", "Extreme\nbinary"]
panels = [("Low", "0.1X"), ("Moderate", "0.4X"), ("High", "0.8X"), ("Exhaustive", "Exhaustive")]
x = np.arange(len(CATEGORIES))
width = 0.36

fig, axes = plt.subplots(2, 2, figsize=(9.6, 5.8), sharey=True)
for ax, (regime, title) in zip(axes.ravel(), panels):
    sub = class_df[class_df["regime"] == regime].set_index("class").loc[CATEGORIES].reset_index()
    ax.bar(x - width/2, sub["TD_only"], width=width, label="TD only")
    ax.bar(x + width/2, sub["Multimodal"], width=width, label="Multimodal")
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(short_labels)
    ax.set_ylim(0, 1.04)
    ax.grid(axis="y", alpha=0.16, linewidth=0.6)
axes[0,0].set_ylabel("Recovered fraction")
axes[1,0].set_ylabel("Recovered fraction")
handles, labels = axes[0,0].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.01))
fig.tight_layout(rect=(0, 0, 1, 0.965))
fig.savefig(FIGURES / "proposal_recovery_by_class.pdf", bbox_inches="tight")
fig.savefig(FIGURES / "proposal_recovery_by_class.png", bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(6.8, 4.2))
ax.plot(curve["resource_fraction"], curve["TD_only_mean"], marker="o", label="TD only")
ax.plot(curve["resource_fraction"], curve["Multimodal_mean"], marker="o", label="Multimodal")
ax.set_xlabel(r"Available compute ($X$)")
ax.set_ylabel("Recovered fraction")
ax.set_xlim(0.1, 0.9)
ax.set_ylim(0.79, 1.0)
ax.grid(alpha=0.16, linewidth=0.6)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(FIGURES / "proposal_overall_recovery_vs_compute.pdf", bbox_inches="tight")
fig.savefig(FIGURES / "proposal_overall_recovery_vs_compute.png", bbox_inches="tight")
plt.close(fig)

fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.2), sharex=True)
labels = ["Standard / ordinary", "Scintillating", "Intermittent", "Eclipsing", "Compact binary", "Extreme binary"]
for ax, (regime, title) in zip(axes, [("Moderate", "0.4X"), ("High", "0.8X")]):
    sub = class_df[class_df["regime"] == regime]
    y = np.arange(len(sub))
    ax.barh(y, sub["gain_percentage_points"])
    ax.axvline(0, linewidth=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_title(title)
    ax.set_xlabel("Recovery gain (percentage points)")
    ax.grid(axis="x", alpha=0.16, linewidth=0.6)
fig.tight_layout()
fig.savefig(FIGURES / "proposal_gain_by_class.pdf", bbox_inches="tight")
fig.savefig(FIGURES / "proposal_gain_by_class.png", bbox_inches="tight")
plt.close(fig)

mask = break_even["break_even_full_imaging_cost_fraction_of_X"].notna()
fig, ax = plt.subplots(figsize=(7.0, 4.5))
ax.plot(
    break_even.loc[mask, "resource_fraction"],
    100.0 * break_even.loc[mask, "break_even_full_imaging_cost_fraction_of_X"],
    marker="o",
)
ax.set_xlabel(r"Available compute ($X$)")
ax.set_ylabel(r"Break-even imaging cost (% of $X$)")
ax.set_xlim(0.18, 0.92)
ax.set_ylim(bottom=0)
ax.grid(alpha=0.16, linewidth=0.6)
fig.tight_layout()
fig.savefig(FIGURES / "proposal_break_even_imaging_cost.pdf", bbox_inches="tight")
fig.savefig(FIGURES / "proposal_break_even_imaging_cost.png", bbox_inches="tight")
plt.close(fig)

print(curve.to_string(index=False))
