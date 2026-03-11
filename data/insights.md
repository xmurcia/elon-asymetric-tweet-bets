# Data Insights Report - XTracker Elon Musk Tweets Analysis

## Dataset Overview
- **Total tweets**: 6,451
- **Date range**: 2025-10-31 to 2026-03-11 (133 days)
- **Average tweets per day**: 48.5 (σ=25.75)
- **Peak daily tweets**: 121 (2026-01-16)

## Tweet Frequency Patterns
- **Hourly distribution (UTC)**: Peaks at 5-8 UTC (early morning US) and 12-17 UTC (midday US).
- **Average tweets per hour**: 2.02
- **Most active hour**: 5 UTC (487 tweets)

## Burst Detection Analysis (15‑minute windows)
- **Bucket size**: 15 minutes (non‑overlapping)
- **Total buckets**: 12,650
- **Mean tweets per bucket**: 0.51 (σ=1.38)
- **Percentiles**:
  - 90th: 2 tweets
  - 95th: 3 tweets
  - 99th: 7 tweets
  - 99.5th: 8 tweets
- **Current threshold (≥8 tweets)** corresponds to the **99.3rd percentile**.
- **Empirical burst probability**: 0.711% of buckets (90 bursts out of 12,650)

### Burst Characteristics
- **Intensity distribution**:
  - 8 tweets: 41 bursts
  - 9 tweets: 20 bursts
  - 10 tweets: 16 bursts
  - 11‑17 tweets: 13 bursts
- **Duration**: Most bursts (64/90) are isolated 15‑minute windows; 12 bursts last 30‑45 minutes (2‑3 consecutive buckets).
- **Hourly pattern of burst starts**: Spread throughout the day, with slight concentrations at 5,12,14 UTC.

## Thematic Classification
**Keyword‑based classification (Tesla, SpaceX, IA, Politics, Grok, X)**:

| Theme       | Total tweets | Burst dominance | Avg per burst |
|-------------|--------------|-----------------|---------------|
| Tesla       | 1,271 (19.7%)| 45 (50.0%)      | 1.92          |
| IA          | 1,516 (23.5%)| 26 (28.9%)      | 1.96          |
| Grok        | 1,149 (17.8%)| 8 (8.9%)        | 1.46          |
| Politics    | 459 (7.1%)   | 7 (7.8%)        | 0.64          |
| SpaceX      | 485 (7.5%)   | 3 (3.3%)        | 0.57          |
| X           | 28 (0.4%)    | 0 (0.0%)        | 0.01          |

**Co‑occurrence within bursts**:
- Tesla & IA appear together in 64 bursts (71%).
- Grok & IA appear together in 57 bursts (63%).
- Many bursts contain multiple themes, indicating overlapping topics.

**Keyword expansion opportunities**:
- High‑frequency terms: `grok`, `elon`, `imagine`, `musk`, `doge`, `starlink`, `breaking`.
- Consider adding **Crypto** theme (keywords: doge, bitcoin, crypto, cryptocurrency).
- Add `imagine` to Grok theme.
- Improve `X` theme with `twitter`, `social media`, `subscription`, `x.com`.

## Gaussian Model Parameters
*Note: The placeholder Gauss model (μ=220, σ=50) does not match any observed tweet‑count distribution.*

**Possible interpretations**:
1. **Daily tweet counts**: μ = 48.5, σ = 25.75
2. **Burst intensity (tweets per 15‑min burst)**: μ = 9.30, σ = 1.86
3. **Hourly tweet counts**: μ = 2.02, σ = 1.98 (approx)

**Recommendation**: Use the distribution of **burst intensity** for modeling trading‑signal strength, as bursts are the primary trading triggers.

## Paper Trading Strategy Considerations
- **Signal**: Burst ≥8 tweets/15min with a dominant theme.
- **Position sizing**: 20% of bankroll per trade (as per spec), with 10% “relleno” (follow‑up).
- **Holding period**: To be determined – could be fixed (e.g., 1 hour) or until next burst.
- **Risk management**: Stop‑loss based on opposite‑theme bursts or time decay.
- **Backtesting requirement**: Historical Polymarket contract prices needed to validate profitability.

## Recommendations for Burst Detection Refinement
1. **Dynamic threshold**: Adjust threshold per hour based on baseline activity (e.g., mean + 3σ for that hour).
2. **Overlapping windows**: Use sliding 15‑min windows (step 1 min) to capture burst start more precisely.
3. **Multi‑theme weighting**: Instead of dominant theme only, compute theme‑specific intensities (tweets/minute per theme).
4. **Exclude retweets?** Retweets constitute a large portion; they are valid signals but may dilute originality. Consider weighting original tweets higher.

## Next Steps
1. Integrate refined burst detection into backend API.
2. Expand thematic classification with expanded keyword lists.
3. Connect to Polymarket API to fetch contract prices and simulate paper trading.
4. Build Gaussian visualization using actual burst‑intensity distribution (μ≈9.3, σ≈1.86) or daily tweet distribution.
5. Implement paper‑trading ledger and P&L tracking.

---
*Analysis performed on 2026‑03‑11 by Data Analyst subagent.*