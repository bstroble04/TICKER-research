# Lab 08 — Deal Evidence and Valuation Triangulation

## Target and Valuation Date

**Target Company:** Archer-Daniels-Midland Company (ADM)  
**Ticker:** ADM  
**Valuation Date:** September 10, 2026

The question I am trying to answer is: What would ADM's shares be worth at defensible peer P/E multiples, and how does that compare with my Week 3 DCF valuation?

## Company Overview

ADM earns money through agricultural commodity origination, processing, merchandising, transportation, and nutrition and ingredient businesses. Because of this, I looked for peers with similar agricultural processing, commodity, or ingredient economics.

## Peer Selection Policy

ADM peers should be publicly traded operating companies with significant exposure to agricultural commodities, processing, merchandising, food ingredients, or related businesses. Companies with similar economics but meaningful differences in product mix or geographic exposure may be qualified. Companies whose primary business model is substantially different from ADM or whose annual diluted EPS is not usable should be excluded.

I would reject a peer if its primary business economics are substantially different from ADM, if comparable annual reported diluted EPS cannot be verified, or if the necessary information was not public by my valuation date.

## Candidate Peer Evidence

| Company | Role / Decision | Business Similarity to ADM | Important Difference | Annual Reported Diluted EPS | Fiscal Year | Price on Comparison Date |
|---|---|---|---|---:|---:|---:|
| Archer-Daniels-Midland Company (ADM) | Target | Agricultural origination, processing, merchandising, and nutrition | N/A | $2.23 | 2025 | $86.91 |
| Bunge Global SA (BG) | Qualify | Agricultural commodity processing and merchandising are similar to major parts of ADM | Different business mix and geographic exposure; Bunge was also affected by its Viterra transaction | $4.91 | 2025 | $124.59 |
| Ingredion Incorporated (INGR) | Qualify | Processes agricultural raw materials into food and ingredient products, similar to parts of ADM's processing and nutrition businesses | More concentrated in specialty ingredients and has less agricultural commodity origination and merchandising exposure | $11.18 | 2025 | $101.13 |

## Candidate Decisions

### Bunge Global SA — Qualify

I qualified Bunge because its agricultural processing and merchandising operations share important business economics with ADM. However, differences in business mix and geographic exposure mean it is not a perfect comparison.

### Ingredion Incorporated — Qualify

I qualified Ingredion because it processes agricultural raw materials into food and ingredient products, which overlaps with ADM's processing and nutrition operations. However, Ingredion is more focused on specialty ingredients and has less exposure to commodity origination and merchandising than ADM.

## Peer P/E Valuation

The peer P/E multiple is calculated as:

**Peer P/E = Peer Share Price / Annual Reported Diluted EPS**

The peer P/E is then applied to ADM's annual reported diluted EPS:

**ADM Implied Share Price = Peer P/E × ADM Annual Reported Diluted EPS**

### Bunge Calculation

Bunge P/E:

**$124.59 / $4.91 = 25.37x**

ADM implied share price using Bunge:

**25.37 × $2.23 = $56.57**

### Ingredion Calculation

Ingredion P/E:

**$101.13 / $11.18 = 9.05x**

ADM implied share price using Ingredion:

**9.05 × $2.23 = $20.17**

### Peer-Implied ADM Valuation Range

Based on the two qualified peers, ADM's peer-implied valuation range is:

**$20.17 – $56.57 per share**

ADM's actual share price on the comparison date was **$86.91**, which was above the values implied by both qualified peer P/E multiples.

## Manual Validation

I manually checked Bunge's P/E by dividing its $124.59 share price by its $4.91 annual reported diluted EPS:

**$124.59 / $4.91 = 25.37x**

I then applied the 25.37x multiple to ADM's $2.23 annual reported diluted EPS:

**25.37 × $2.23 = approximately $56.57**

This agrees with the result from my Lab 07 calculator.

## Changed-Peer Test

Before removing Ingredion, I predicted that removing it would eliminate the lower end of ADM's implied valuation range because Ingredion has the lower P/E multiple.

After removing Ingredion, Bunge was the only remaining qualified peer, resulting in a single-peer reference value of approximately $56.57 per ADM share. This confirms that Ingredion's lower P/E multiple was responsible for the lower end of the original $20.17–$56.57 range.

## DCF vs. Peer P/E Comparison

| Method | ADM Result and Date | Main Assumption or Limitation |
|---|---|---|
| Week 3 DCF | $224.92 per share — September 10, 2026 | Depends heavily on forecast FCFF, WACC, and terminal growth assumptions |
| Peer P/E | $20.17–$56.57 per share — September 10, 2026 | Depends on the comparability of Bunge and Ingredion and the use of annual reported diluted earnings |

The peer P/E valuation provides a market-based comparison to my DCF. The difference between the two methods shows how sensitive the valuation is to the assumptions used. The DCF depends on ADM's expected future cash flows, WACC, and terminal growth, while the peer P/E approach depends on how comparable Bunge and Ingredion are to ADM and how the market values their current reported earnings.

## AI Skeptical Review

**AI Criticism:** The weakest assumption is the comparability of the two peers. Bunge and Ingredion both share some business economics with ADM, but neither is a perfect comparison. Ingredion is more focused on value-added ingredients, while Bunge's 2025 results and share base were affected by the Viterra acquisition. These differences could make their P/E multiples less directly comparable to ADM.


**My Judgment:** Accept 

**Reason:** I accept this criticism because the companies' filings confirm meaningful differences in their businesses. Bunge's 2025 results were affected by the Viterra acquisition, while Ingredion is primarily an ingredient solutions company. Therefore, I kept both as qualified peers rather than treating them as perfect comparisons.

### Skeptical Question

**Question:** Why should I rely on a $224.92 DCF value when both qualified peer P/E estimates are substantially below ADM's $86.91 market price?

**Answer:** The large difference makes me less confident in relying on the DCF alone. The DCF is highly dependent on my future cash-flow, WACC, and terminal growth assumptions, while the peer P/E analysis depends on peer comparability and current reported earnings. This disagreement is why I chose to watch and defer rather than rely completely on either method.

## Final Conditional Call

**Decision:** WATCH-DEFER

The peer P/E analysis produced an implied ADM valuation range of $20.17 to $56.57 per share, while my Week 3 DCF produced a base-case value of $224.92 per share. These results differ significantly and depend on different assumptions. The DCF is sensitive to my future cash flow, WACC, and terminal growth assumptions, while the peer valuation depends heavily on the comparability of Bunge and Ingredion and ADM's reported earnings. I would watch and defer until additional evidence provides more confidence in which valuation better reflects ADM's value.

## What Would Change My Decision

The evidence most likely to change my decision would be stronger support for ADM's long-term cash-flow assumptions. This would help determine whether my DCF valuation of $224.92 is reasonable compared with the much lower peer P/E valuation.

## Sources

### ADM
- ADM 2025 Form 10-K — Business section and annual reported diluted EPS
https://www.sec.gov/ix?doc=/Archives/edgar/data/0000007084/000000708426000011/adm-20251231.htm
- ADM historical stock price source for the comparison date
https://finance.yahoo.com/quote/ADM/history/

### Bunge Global SA
- Bunge 2025 Form 10-K — Business section and annual reported diluted EPS
https://www.sec.gov/ix?doc=/Archives/edgar/data/0001996862/000162828026009842/bg-20251231.htm
- Bunge historical stock price source for the comparison date
https://finance.yahoo.com/quote/BG/history/

### Ingredion Incorporated
- Ingredion 2025 Form 10-K — Business section and annual reported diluted EPS
https://www.sec.gov/ix?doc=/Archives/edgar/data/0001046257/000162828026008603/ingr-20251231.htm
- Ingredion historical stock price source for the comparison date
https://finance.yahoo.com/quote/INGR/history/


