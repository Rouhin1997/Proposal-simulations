# Results

## Overall recovery

| Resource | TD only | Multimodal | Difference |
|---|---:|---:|---:|
| 0.1 X | 80.59% | 80.32% | -0.27 pp |
| 0.4 X | 86.56% | 88.11% | +1.55 pp |
| 0.8 X | 92.28% | 95.90% | +3.62 pp |
| Exhaustive | 100.00% | 100.00% | 0.00 pp |

## Recovery by source class

### 0.4 X

| Class | TD only | Multimodal | Difference |
|---|---:|---:|---:|
| Standard / ordinary | 99.38% | 98.10% | -1.28 pp |
| Image-visible scintillator | 93.67% | 97.40% | +3.73 pp |
| Image-visible intermittent | 88.18% | 95.65% | +7.47 pp |
| Image-visible eclipsing | 57.44% | 74.85% | +17.42 pp |
| Compact binary | 53.46% | 56.73% | +3.27 pp |
| Extreme binary | 3.26% | 15.38% | +12.12 pp |

### 0.8 X

| Class | TD only | Multimodal | Difference |
|---|---:|---:|---:|
| Standard / ordinary | 99.76% | 98.53% | -1.23 pp |
| Image-visible scintillator | 96.38% | 99.09% | +2.71 pp |
| Image-visible intermittent | 93.58% | 98.26% | +4.68 pp |
| Image-visible eclipsing | 76.16% | 91.85% | +15.69 pp |
| Compact binary | 72.75% | 86.28% | +13.53 pp |
| Extreme binary | 37.33% | 76.04% | +38.71 pp |

## Interpretation

The model produces three qualitative regimes:

1. **Very low compute:** the interferometric evidence layer has an opportunity cost,
   so TD-only processing can remain marginally better.
2. **Constrained but usable compute:** multimodal triage improves total recovery and
   redirects saved processing toward more expensive binary searches.
3. **Exhaustive processing:** both approaches converge to complete recovery.

The absolute percentages are toy-model outputs; the robust result is the change in
resource-allocation behaviour.
