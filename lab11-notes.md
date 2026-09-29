# Lab 11 — ADM Pro-Forma Sensitivity Analysis

**Company:** Archer-Daniels-Midland Company (ADM)  
**Ticker:** ADM  
**Date:** September 29, 2026  
**Units:** USD millions, unless otherwise noted.

---

## 1. Driver Question

**Which assumptions drive ADM's forecast and value, and what explains their effects?**

For this lab, I tested **gross margin** and **annual capital expenditures (CapEx)** using my existing Lab 10 pro-forma model. I selected these drivers because ADM operates with relatively thin gross margins and requires significant capital investment. I wanted to understand how changes in profitability and reinvestment affect operating profit, free cash flow to equity (FCFE), liquidity requirements, and estimated value per share.

## 2. Original Lab 10 Base Results

| Assumption | Base Value |
|:--|--:|
| Revenue growth | 2.00% |
| Gross margin | 6.75% |
| SG&A / gross profit | 65.00% |
| Inventory days | 51 |
| D&A / PP&E | 10.50% |
| Annual CapEx | $1,400 million |
| Tax rate | 18.00% |
| Minimum cash balance | $500 million |
| Liquidity facility limit | $6,000 million |
| **Estimated value per share** | **$33.70** |

My model forecasts ADM's financial statements from 2026E through 2030E. The original Lab 10 value of **$33.70 per share** serves as the sensitivity baseline.

---

## 3. Selected Operating Drivers and Ranges

### Driver 1 — Gross Margin

| Scenario | Gross Margin |
|:--|--:|
| Lower | 6.25% |
| **Base** | **6.75%** |
| Higher | 7.25% |

ADM's historical gross margins were approximately **8.00% in 2023, 6.76% in 2024, and 6.27% in 2025**.

I selected a judgment-based range of 6.25%–7.25%, or 0.50 percentage points below and above the base, informed by that history. Each assumption is applied consistently to **2026E–2030E**.

### Driver 2 — Annual Capital Expenditures (CapEx)

| Scenario | Annual CapEx |
|:--|--:|
| Lower | $1,200 million |
| **Base** | **$1,400 million** |
| Higher | $1,600 million |

I selected a judgment-based range of $200 million below and above my $1,400 million base to test how reinvestment affects cash flow, depreciation, liquidity, and valuation.

Each amount is applied annually from **2026E–2030E**.

**One-at-a-time rule:** Each scenario changes only one existing independent operating assumption. All other inputs remain at their original base values.

---

## 4. Locked Prediction — Before Running Sensitivity

**Prediction Date:** September 29, 2026

### Gross Margin Prediction

I predict that increasing gross margin from 6.75% to 7.25% will increase operating profit, FCFE before facility borrowing, and potentially value per share. I expect the opposite effect at 6.25%.

Since ADM operates on relatively thin margins, even a 0.50 percentage-point change could have a meaningful impact.

### CapEx Prediction

I predict that reducing annual CapEx from $1,400 million to $1,200 million will improve cash flow by reducing reinvestment spending. Increasing it to $1,600 million should have the opposite effect.

CapEx should also affect future depreciation through PP&E, changing operating profit.

### Overall Prediction

I expect gross margin to have the larger impact on operating profit. I am less certain which driver will have the larger effect on FCFE and valuation.

---

## 5. Sensitivity Analysis Results

The linked income statement, balance sheet, cash flow statement, and valuation were recalculated for each one-at-a-time scenario.

### 5.1 Gross Margin Sensitivity — 2030E

| Scenario | Operating Profit ($m) | FCFE ($m) | Value/Share |
|:--|--:|--:|--:|
| Lower: 6.25% | 683.78* | 1,006.72* | **UNAVAILABLE** |
| **Base: 6.75%** | **838.87** | **1,006.72** | **$33.70** |
| Higher: 7.25% | 993.96 | 1,006.72 | $33.70 |

*The 6.25% scenario has calculated statement outputs but fails liquidity validation in 2030E. Its valuation is not valid.*

### 5.2 Annual CapEx Sensitivity — 2030E

| Scenario | Operating Profit ($m) | FCFE ($m) | Value/Share |
|:--|--:|--:|--:|
| Lower: $1,200m | 910.54 | 1,006.72 | $33.70 |
| **Base: $1,400m** | **838.87** | **1,006.72** | **$33.70** |
| Higher: $1,600m | 767.20* | 1,006.72* | **UNAVAILABLE** |

*The $1,600 million scenario has calculated statement outputs but fails liquidity validation in 2030E. Its valuation is not valid.*

### 5.3 Signed Changes from Base

**Formula:**

Changed Scenario Output − Base Output = Signed Difference

| Scenario | Change in Operating Profit ($m) | Change in FCFE ($m) | Change in Value/Share |
|:--|--:|--:|--:|
| Gross margin: 6.25% | -155.09* | +0.00* | UNAVAILABLE |
| Gross margin: 7.25% | +155.09 | +0.00 | +$0.00 |
| CapEx: $1,200m | +71.67 | +0.00 | +$0.00 |
| CapEx: $1,600m | -71.67* | +0.00* | UNAVAILABLE |

*Calculated differences from an invalid scenario are shown for transparency, not treated as validated valuation results.*

### 5.4 Output Spans

**Formula:**

Maximum Valid Output − Minimum Valid Output = Span

| Output | Gross Margin Span | CapEx Span |
|:--|:--:|:--:|
| Operating profit | UNAVAILABLE | UNAVAILABLE |
| FCFE | UNAVAILABLE | UNAVAILABLE |
| Value per share | UNAVAILABLE | UNAVAILABLE |

A complete lower/base/higher span cannot be reported because **only two of three scenarios pass validation for each driver**.

For context, the calculated operating-profit difference between the two endpoints is:

- **Gross margin:** $310.18 million
- **CapEx:** $143.34 million

These are descriptive endpoint differences that include invalid scenarios, **not validated three-case spans**.

---

## 6. Validation and Restored-Base Check

I checked that only one independent input changed per scenario, while all other assumptions stayed at their base values. I recalculated the full linked statements for every run.

### 6.1 Manual Difference Check

I manually checked the higher gross-margin scenario:

| Item | 2030E Operating Profit |
|:--|--:|
| Higher gross margin (7.25%) | $993.96m |
| Base gross margin (6.75%) | $838.87m |
| **Difference** | **+$155.09m** |

**Calculation:**

$993.96m − $838.87m = +$155.09m

This matches the Python sensitivity output.

### 6.2 Liquidity Validation

Both failed scenarios balanced their accounting statements and maintained the modeled cash floor, but exceeded the **$6,000 million facility limit in 2030E**.

| Failed Scenario | 2030E Facility Balance | Facility Limit | Over Limit |
|:--|--:|--:|--:|
| Gross margin: 6.25% | $6,229.30m | $6,000.00m | **$229.30m** |
| CapEx: $1,600m | $6,539.80m | $6,000.00m | **$539.80m** |

The other sensitivity scenarios passed the existing accounting and liquidity checks.

I kept the original $6 billion borrowing limit rather than raising it simply to make the scenarios pass. I marked both failed valuations **UNAVAILABLE**.

This demonstrates how weaker profitability or increased capital spending puts pressure on ADM's liquidity under my assumptions.

### 6.3 Restored-Base Check

After the sensitivity runs, I restored every original independent assumption and reran the base model.

| Validation Item | Result |
|:--|--:|
| Maximum difference from original base | 0.000000 |
| Tolerance | $0.01 million / $0.01 per share |
| **Restored-base status** | **PASS** |

The restored baseline matches the original model within the stated tolerance.

---

## 7. Understanding the FCFE Results

One surprising result was that **reported 2030E FCFE stayed at $1,006.72 million** across all the calculated scenarios, even though operating profit changed.

My model draws on the liquidity facility to support the minimum cash balance and shareholder distributions. When cash generated before borrowing decreases, additional borrowing offsets the shortfall in reported FCFE.

To see the underlying operating effect, I compared **FCFE before facility borrowing**:

| Scenario | 2030E FCFE Before Facility Borrowing ($m) |
|:--|--:|
| Gross margin: 6.25%* | -337.8 |
| **Base** | **-190.5** |
| Gross margin: 7.25% | -43.3 |
| CapEx: $1,200m | +23.4 |
| CapEx: $1,600m* | -404.5 |

*Scenario fails the 2030E facility-limit check.*

For example, reducing CapEx to $1,200 million improves FCFE before borrowing from approximately **-$190.5 million to +$23.4 million**.

The unchanged reported FCFE and valid-case value per share do not mean the drivers have no economic impact; the financing mechanism is offsetting the cash-flow changes in the model.

---

## 8. Main Driver and Explanation

Over my chosen ranges, gross margin caused a larger **calculated change in operating profit** than CapEx.

- A **±0.50 percentage-point gross-margin change** moved 2030E operating profit by approximately **±$155.09 million**.
- A **±$200 million annual CapEx change** moved 2030E operating profit by approximately **∓$71.67 million**.

Gross margin directly changes gross profit, which flows through operating income, taxes, and cash flow. CapEx affects immediate reinvestment spending and future depreciation through PP&E.

For FCFE **before facility borrowing**, the calculated lower-to-higher endpoint difference was approximately:

| Driver | Calculated Endpoint Difference |
|:--|--:|
| Gross margin | $294.5 million |
| Annual CapEx | $427.9 million |

Both endpoint comparisons include one failed scenario, so they are descriptive, not complete validated spans.

These results apply only to my selected ranges. I cannot establish a complete validated three-scenario comparison for either driver because of the liquidity failures.

---

## 9. Prediction vs. Actual Results

I originally predicted gross margin would have the larger effect on operating profit. The calculated operating-profit differences supported that expectation over my chosen ranges.

What surprised me was that **reported FCFE and value per share did not change across valid scenarios**, even though operating performance did.

Reviewing the linked statements showed that liquidity-facility draws offset the underlying cash-flow changes.

I also learned that the lower gross-margin and higher-CapEx scenarios exceeded the borrowing limit in 2030E. This reinforced why I need to review the full statements and validation checks, not just the final valuation number.

---

## 10. Valuation Conclusion and Research Priority

My Lab 10 baseline estimated ADM at **$33.70 per share**, compared with the observed market price of **$82.42 on September 24, 2026**.

The valid sensitivity scenarios also returned **$33.70 per share**. However, this reflects how my model treats borrowing and reported FCFE; it is not evidence that gross margin and CapEx have no economic effect.

The sensitivity exercise did not change my reported base valuation, but it revealed an important modeling limitation.

My next research priorities are **ADM's capital spending requirements, available liquidity, and the reasonableness of the borrowing and shareholder-distribution assumptions**.

In particular, the higher-CapEx scenario required **$6,539.8 million** of facility borrowing by 2030E, or **$539.8 million over the modeled limit**.

Sensitivity analysis shows how the model responds to an assumption change; it does not tell me how likely a scenario is to occur.

---

## 11. Partner Exchange Notes

### Exchange 1 — Prediction and Ranges

**Partner's Question:**

Why did you choose gross margin and CapEx as your two drivers instead of revenue growth?

**My Response:**

I chose gross margin because ADM operates on relatively thin margins, so even a small percentage-point change could significantly affect profitability. I chose CapEx because ADM requires substantial reinvestment, and I wanted to see how changing that spending would affect cash flow and valuation.

### Exchange 2 — Validation

**My Partner Checked:**

My partner manually verified the change in my ADM operating income when gross margin increased from 6.75% to 7.25%.

**Calculation:**

$993.96m − $838.87m = +$155.09m

This matched my Python sensitivity output.

**I Checked My Partner's Model:**

I manually recalculated the difference between their changed operating income and base operating income.

**Calculation:**

$2,051.49m − $1,956.53m = +$94.96m

This confirmed a **$94.96 million increase** in operating income.

**Validation Discussion:**

We discussed why only one independent input should change at a time, with all other assumptions kept at their original base values.

### Exchange 3 — Driver Explanation

**Partner's Question:**

Do you think gross margin would still have the largest impact on operating income if you tested a smaller range?

**My Response:**

Not necessarily. Gross margin had the larger calculated impact over my selected ranges, but narrowing the range could change that comparison. Two of my scenarios also failed liquidity validation, so I cannot report a complete validated three-scenario comparison.

**What I Learned From My Partner's Model:**

My partner's Ulta results showed that revenue growth had a larger effect on operating income, while changes in SG&A had a larger effect on cash flow and estimated value per share over the ranges tested.

This showed how controlling expenses can be just as important as increasing sales.

---

## 12. Reflection

This lab helped me understand how individual assumptions influence ADM's financial forecast. Instead of relying only on the original base valuation, I tested different scenarios and traced their effects through operating profit, cash flow, borrowing requirements, and value per share.

Gross margin had the larger calculated effect on operating profit over my chosen ranges, while CapEx had a significant effect on underlying cash flow and liquidity.

I was surprised that reported FCFE stayed unchanged because the model kept drawing on the liquidity facility. I learned to look beyond the final valuation and understand how the financial statements connect.

---

## 13. Sources

Archer-Daniels-Midland Company. (2025). *Form 10-K, Annual Report*.

[ADM 2025 Form 10-K — SEC](https://www.sec.gov/ix?doc=/Archives/edgar/data/0000007084/000000708426000011/adm-20251231.htm)

---

## 14. AI Disclosure

I used AI to assist in adding one-at-a-time sensitivity analysis to my existing ADM pro-forma Python model and investigating the liquidity validation failures. I selected the operating drivers and input ranges, reviewed the generated results, and checked the output differences and restored-base validation. AI also assisted with organizing this Markdown write-up and explaining the model's results.