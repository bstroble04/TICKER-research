## ADM DCF Inputs and Sources

| Input | Value | Unit | As-of Date | Source / Exact Locator |
|---|---:|---|---|---|
| Starting FCFF | $4,741.8 | $ millions | December 31, 2025 | ADM 2025 Form 10-K, Consolidated Statements of Cash Flows, p. 51. Net cash provided by operating activities = $5,452 million; capital expenditures = $1,248 million; cash interest paid = $629 million. Using ADM's 14.5% effective tax rate, FCFF = $5,452 + [$629 × (1 − 0.145)] − $1,248 = $4,741.8 million. |
| Growth — Year 1 | 5.0% | Annual FCFF growth | 2026 forecast | **Estimate.** Based on ADM's Item 7, Management's Discussion and Analysis (MD&A), recent operating performance, and expected 2026 capital expenditures. |
| Growth — Year 2 | 4.5% | Annual FCFF growth | 2027 forecast | **Estimate.** Assumes FCFF growth begins gradually normalizing toward ADM's long-run sustainable growth rate. |
| Growth — Year 3 | 4.0% | Annual FCFF growth | 2028 forecast | **Estimate.** Assumes continued normalization toward long-run growth. |
| Growth — Year 4 | 3.5% | Annual FCFF growth | 2029 forecast | **Estimate.** Assumes FCFF growth continues converging toward the terminal growth assumption. |
| Growth — Year 5 | 3.0% | Annual FCFF growth | 2030 forecast | **Estimate.** Assumes FCFF growth reaches the long-run terminal growth assumption by Year 5. |
| WACC | 7.4% | Discount rate | September 10, 2026 estimate | **Estimate.** WACC is not directly reported by ADM. Estimated using cost of equity and after-tax cost of debt weighted by their market values. ADM's 2025 Form 10-K provides the underlying debt and interest information used to support the estimate. |
| Terminal Growth | 3.0% | Perpetual annual growth | Long-run assumption | **Estimate.** Represents a sustainable long-run economic growth assumption rather than ADM's short-term company-specific growth. |
| Cash | $1,015 | $ millions | December 31, 2025 | ADM 2025 Form 10-K, Consolidated Balance Sheets, p. 47, "Cash and cash equivalents." |
| Debt | $8,410 | $ millions | December 31, 2025 | ADM 2025 Form 10-K, Consolidated Balance Sheets and Note 8 — Debt. Short-term debt of $798 million plus total long-term debt, including current maturities, of $7,612 million = $8,410 million. |
| Diluted Shares | 484 | million shares | Year ended December 31, 2025 | ADM 2025 Form 10-K, Consolidated Statements of Earnings, p. 45, "Weighted average number of shares outstanding — diluted." |

### Starting FCFF Calculation

Starting FCFF is calculated using operating cash flow plus after-tax interest paid minus capital expenditures:

**After-tax interest paid:**

$629 × (1 − 0.145) = $537.8 million

**Starting FCFF:**

$5,452 + $537.8 − $1,248 = **$4,741.8 million**

Therefore, the starting FCFF used in the DCF model is **$4,741.8 million**.

### Current ADM Share Price

| Item | Value | Unit | Date / Time | Source |
|---|---:|---|---|---|
| ADM Share Price | $[86.91] | $ per share | September 10, 2026 at [4:40pm] ET | Current ADM market quote |

**Reverse DCF target price:** $[86.91] per share.

The current market price is used as the target for the reverse DCF. The share price is not sourced from ADM's 2025 Form 10-K because it must reflect the current market price on September 10, 2026.

### Inputs Used in `dcf.py`

- Starting FCFF: **$4,741.8 million**
- Year 1 Growth: **5.0%**
- Year 2 Growth: **4.5%**
- Year 3 Growth: **4.0%**
- Year 4 Growth: **3.5%**
- Year 5 Growth: **3.0%**
- WACC: **7.4%**
- Terminal Growth: **3.0%**
- Cash: **$1,015 million**
- Debt: **$8,410 million**
- Diluted Shares: **484 million**

Growth rates, WACC, and terminal growth are explicitly labeled as estimates rather than values directly reported by ADM. All financial statement amounts are sourced from ADM's 2025 Form 10-K.


## Conditional Call

**Initiate.** Initiate at ADM's current market price of $86.91 because it is below my base-case DCF value of $224.92 per diluted share. Otherwise, reconsider the position if future operating performance causes my FCFF assumptions and estimated valuation to decline materially toward or below the market price.

**Monitor:** Operating cash flow next quarter.


## Reasonableness Check

My base-case DCF value is $224.92 per diluted share compared with ADM's current market price of $86.91 per share. The DCF value is approximately 2.59× the current market price, which is outside the 0.5× to 2.0× reasonableness range.

The input I distrust most is starting FCFF because the $4,741.8 million starting value is based on a single year's operating cash flow, which can be affected by working-capital movements and may not represent ADM's normalized long-term FCFF. I did not adjust this input simply to make the model fit the current market price.


## Reverse DCF

The reverse DCF used ADM's current market price of **$86.91 per share** as the target.

The model found **no solution within the specified bracket of -5.00 to +10.00 percentage points** for a uniform shift to all five explicit FCFF growth rates.

The reverse DCF held starting FCFF, WACC, terminal growth, cash, debt, and diluted shares fixed. Therefore, ADM's $86.91 market price cannot be reproduced by changing only the five explicit growth rates within the specified bracket while holding these other assumptions constant.

This does not prove that ADM is mispriced. Instead, it indicates that at least one of the assumptions held fixed, particularly starting FCFF, may differ materially from the assumptions embedded in the market price.