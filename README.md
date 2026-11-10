# Proposal simulations: adaptive multimodal pulsar searches

This repository contains the toy resource-allocation simulation used to support a
Henri Poincaré fellowship proposal on adaptive multimodal pulsar searches for
large-scale MeerKAT+/SKA-era surveys.

The current comparison is deliberately simple:

- **TD only** — a time-domain-only search hierarchy.
- **Multimodal** — a scalable interferometric evidence layer coupled to adaptive
  time-domain search allocation.

## Scientific question

Can interferometric evidence be supplied selectively enough that it improves
pulsar recovery at fixed survey-processing resources, especially for sources
whose detectability varies with time, frequency or orbital phase?

## Population model

Each of 400 realizations contains:

- 50 tied-array beams;
- 20 recoverable pulsars;
- a 2-hour observation divided into eight 15-minute intervals;
- a globular-cluster-like binary fraction anchored to the Freire GC pulsar census;
- independent scintillation, intermittency and eclipsing modifiers.

Source classes shown in the figures are dominant plotting categories rather than
mutually exclusive physical populations.

## Search hierarchy

The time-domain branch uses increasingly expensive searches:

1. acceleration;
2. segmented acceleration;
3. jerk;
4. segmented jerk;
5. 5-D Keplerian template-bank search;
6. segmented 5-D search.

The normalized full-track costs are 1, 25 and 100 for acceleration, jerk and
5-D template-bank searches respectively. These values encode only the qualitative
cost hierarchy; they are not survey runtime forecasts.

## Scalable interferometric evidence model

The multimodal branch uses an initial coarse interferometric reconstruction and
refines only where the imaging evidence is informative.

For the frozen proposal-scale experiment,

```text
C_img = 2 + 6 (N_info / 20)
```

where `N_info` is the number of image-informative scintillating, intermittent or
eclipsing sources in that realization. The maximum imaging-work ceiling is therefore
8 normalized units, but the mean realized cost is about 3.02 units.

This is an **illustrative resource model**, not a measured SMURFIT/OCA runtime.
The intended fellowship work would replace these parameters with measured
reconstruction and candidate-extraction benchmarks.

## Resource normalization

For every realization, `X` is the actual TD-only compute required to recover all
20 injected pulsars. Finite-budget tests are expressed as fractions of `X`.
The "Exhaustive" panel means effectively unlimited processing and is therefore
not identical to a strict budget of exactly `1.0 X`.

## Main results

| Available resource | TD only | Multimodal |
|---|---:|---:|
| 0.1 X | 80.59% | 80.32% |
| 0.4 X | 86.56% | 88.11% |
| 0.8 X | 92.28% | 95.90% |
| Exhaustive | 100% | 100% |

The multimodal strategy is therefore not beneficial when resources are extremely
scarce, but its advantage grows once enough compute exists to act on the
interferometric evidence. At exhaustive processing both strategies converge.

At 0.8 X, the largest gains occur for eclipsing, compact-binary and extreme-binary
regimes. Compact/extreme binaries receive no direct imaging shortcut; their gain
comes from computation saved on image-informative sources being redirected to
expensive orbital searches.

## Imaging-cost robustness

A separate sensitivity test treats the cost of a complete interferometric
evidence product as a fraction of `X`. Under the illustrative hierarchical
reconstruction model, the multimodal strategy remains competitive over a larger
range of imaging costs as the available survey-processing budget increases.

These break-even values are sensitivity-test outputs, not measured telescope-processing costs.

## Figures

- `figures/proposal_recovery_by_class.pdf` — proposal-style class recovery panels.
- `figures/proposal_overall_recovery_vs_compute.pdf` — overall recovery versus compute.
- `figures/proposal_gain_by_class.pdf` — direct multimodal gain by source class.
- `figures/proposal_break_even_imaging_cost.pdf` — imaging-cost robustness.

PNG versions are included for quick viewing.

## Reproduce

```bash
pip install -r requirements.txt
python simulation.py
```

## Scope and limitations

This is a qualitative resource-allocation toy model. It is designed to test the
logic of adaptive processing, not to predict MeerKAT+/SKA discovery yields.
Parameters governing imaging cost, time/frequency resolution and reconstruction
depth should be replaced with real benchmarks during the fellowship.
