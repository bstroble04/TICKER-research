Lab 13 — Portfolio Mandate Defense
D — Define
Decision question: Which of these portfolios does the Meridian Foundation's mandate permit, and what must the CIO answer before anyone optimizes?
The goal is to translate the CIO's statements into measurable portfolio checks without inventing requirements that have not been defined. Passing the checks establishes compliance with the rules implemented in the program, not overall suitability.
R — Represent
Meridian Foundation Case
The Meridian Foundation manages a $100 million reserve, has a seven-year investment horizon, and rebalances annually. Its return objective is CPI + 4% per year, net of costs, over rolling five-year periods. It distributes $0.75 million quarterly.
CIO Statement Classifications — AI-Generated Study Examples
Academic integrity note: The lab requires you to classify S1–S10 without AI. The following are examples for reviewing your own independently written classifications; do not submit them as an AI-closed exercise without completing that exercise yourself.
Statement	Classification	Reason
S1	Hard constraint / implementation policy	The seven-year horizon and annual rebalancing schedule establish how the portfolio is managed, though the horizon is also important context for objectives.
S2	Objective	CPI + 4%, net of costs, over rolling five-year periods specifies the desired investment return.
S3	Hard constraint	The fund must hold twelve months of quarterly distributions in cash or eligible government securities.
S4	Preference / benchmark	The 60% global equity and 40% U.S. investment-grade bond benchmark provides a comparison point, not a mandatory portfolio weight.
S5	Hard constraint	Borrowing, short sales, and derivatives are prohibited.
S6	Hard constraint	Exposure to a single company issuer cannot exceed 8%.
S7	Hard constraint	Annual turnover cannot exceed 25% without committee approval.
S8	Hard constraint	At least 90% must be redeemable within five business days.
S9	Unverifiable promise	The statement about avoiding calendar-year losses above 10% lacks a measurement method and breach rule; a loss cannot be guaranteed away.
S10	Missing	The CIO has not specified what the pilot should optimize; the absence of sector, ESG, tax, and home-bias preferences is also recorded.


Holdings and Candidate Weights
Holding	Issuer	Redeemable (business days)	Reserve-eligible	A	B	C	D
Cash	None	0	Yes	2	1	1	3
Treasury bills	U.S. Treasury	1	Yes	2	0	1	97
Treasury 10-year note	U.S. Treasury	1	Yes	10	0	0	0
Global equity index fund	Diversified fund	2	No	60	55	70	0
Investment-grade bond fund	Diversified fund	3	No	26	20	20	0
Private real estate fund	Diversified fund	90	No	0	15	0	0
Acme Corp bonds	Acme Corp	4	No	0	5	0	0
Acme Corp stock	Acme Corp	1	No	0	4	8	0
Total				100	100	100	100


Candidate D is an AI-generated adversarial example, not one of the three original candidates.
I — Implement
Python Checker
I used ChatGPT to help develop mandate.py, a standard-library Python program that reads the holdings and candidate weights and computes each check from its inputs. The five implemented tests are (1) weights sum to 100%, (2) minimum weight is nonnegative, (3) reserve-eligible allocation meets the calculated minimum, (4) five-business-day liquidity is at least 90%, and (5) the largest nonexempt company issuer is no more than 8%. Cash, U.S. Treasury securities, and diversified funds are exempt from the single-company issuer limit; securities issued by the same company are aggregated.
The checker reports requires CIO clarification for the calendar-year loss statement rather than inventing a numerical test. The return objective, benchmark, turnover policy, and broader suitability are not all proven by these five checks.
Reserve Calculation
Four quarterly payouts of $0.75 million equal $3.00 million for twelve months. Dividing by the $100 million reserve gives:
Minimum reserve = (4 × 0.75 / 100) × 100 = 3.0%
Command
python mandate.py
AI Code-Comprehension Quiz
AI question: Why does the issuer check combine Acme Corp bonds and Acme Corp stock rather than checking each holding separately?
Example explanation (AI-generated; write your own answer first): The restriction applies to a company issuer, not to each security. Candidate B holds 5% Acme bonds plus 4% Acme stock, so its Acme issuer exposure is 9%, exceeding the 8% limit even though each security individually is below 8%.
My answer before reading AI's explanation: The issuer check combines Acme Corp bonds and Acme Corp stock because even though bonds and stocks are different, they are both issued by Acme Corp. They have a combined percentage of 9%, and the mandate says no single issuer can exceed 8%, not that each individual investment must stay below 8%. Since both investments are issued by the same company, their combined percentage exceeds the limit.
V — Validate
Known-Answer Validation
I ran python mandate.py for Candidates A, B, C, and D. The following results were copied from my actual Python output for the normal (non-probe) run. The reserve minimum was 3.0%.
Rule	Candidate A	Candidate B	Candidate C	Candidate D
Weights sum to 100%	100.0% pass	100.0% pass	100.0% pass	100.0% pass
Long-only (lowest weight ≥ 0%)	0.0% pass	0.0% pass	0.0% pass	0.0% pass
Reserve ≥ 3.0%	14.0% pass	1.0% FAIL	2.0% FAIL	100.0% pass
Redeemable within 5 days ≥ 90%	100.0% pass	85.0% FAIL	100.0% pass	100.0% pass
Largest single company ≤ 8%	0.0% pass	9.0% FAIL	8.0% pass	0.0% pass
Calendar-year loss	Requires CIO clarification	Requires CIO clarification	Requires CIO clarification	Requires CIO clarification
Verdict	Passes every checkable rule	Fails 3 rules	Fails 1 rule	Passes every checkable rule


The results for A, B, and C match the lab's published known-answer table. Candidate B fails reserve, liquidity, and issuer concentration because its Acme bonds and stock together equal 9%. Candidate C fails the reserve minimum. Candidate D passes all five programmed checks.
Negative-Weight Probe
Required test procedure: Temporarily change Candidate A's cash weight from 2 to -2 and its global equity index fund weight from 60 to 64, preserving a total weight of 100%. Run python mandate.py again, record the results, and restore the original values.
Check	Expected probe result
Weights sum to 100%	100.0% pass
Long-only (lowest weight)	-2.0% FAIL
Reserve-eligible weight	10.0% pass
Redeemable within five days	100.0% pass
Largest single company	0.0% pass
Calendar-year loss	Requires CIO clarification
Verdict	Fails 1 rule


Negative-Weight Probe

To validate that the Python checker correctly identifies violations, I temporarily changed Candidate A's cash allocation from 2% to -2% and increased its global equity index fund allocation from 60% to 64%. This kept the total portfolio weight at 100% while introducing a negative allocation.

I reran python mandate.py and observed the following results:

Rule

Observed Value

Result

Weights sum to 100%

100.0%

Pass

Long-only (lowest weight ≥ 0%)

-2.0%

FAIL

Reserve ≥ 3.0%

10.0%

Pass

Redeemable within 5 days ≥ 90%

100.0%

Pass

Largest single company ≤ 8%

0.0%

Pass

Calendar-year loss

Requires CIO clarification

Not tested

Final Verdict

Fails 1 rule

FAIL

The negative-weight probe successfully demonstrated that the checker evaluates actual portfolio allocations rather than printing predetermined results. When Candidate A contained a negative cash allocation, the program correctly identified a violation of the long-only requirement while all other checkable rules continued to pass.

The results matched the expected validation outcome provided in Lab 13.


E — Evolve
Candidate D: AI Challenge
I asked ChatGPT to propose a portfolio that would pass the checker but could still reasonably be rejected by the CIO. It proposed 3% cash and 97% Treasury bills, with 0% in every other holding. I added it to the Python candidate dictionary and ran the checker. Its actual output showed 100.0% total weight, 0.0% lowest weight, 100.0% reserve eligibility, 100.0% five-day liquidity, and 0.0% largest single-company exposure. The verdict was passes every checkable rule.
AI's Objection
Candidate D has little long-term growth exposure. It may struggle to meet S2's CPI + 4% net-of-costs return objective over rolling five-year periods, even though it meets the five coded restrictions. It also differs greatly from the S4 benchmark, although benchmark deviation by itself is not a violation.
My Independent Judgment — Example Only
The following is an AI-generated example; the lab requires your own two-sentence AI-closed judgment. The objection is reasonable because compliance with allocation and liquidity limits does not establish a sufficient expected return to meet the foundation's objective. S2 is the decisive statement, while S4 offers a benchmark for comparison rather than a binding allocation.
Skeptical Colleague / Partner Check
The lab instructs students working alone to play both roles: proposer and skeptical colleague. A skeptical colleague should challenge whether D can plausibly achieve the inflation-plus-4% target and should avoid treating the benchmark as a hard 60/40 requirement. Personal partner-role response: Write your own response after carrying out the requested role swap/check; no separate completed exchange was supplied.
Completed this lab online so partners were removed from the lab.

One Question for the CIO — 
Question: When selecting among portfolios that meet the hard constraints, should the pilot minimize risk while targeting CPI + 4%, maximize expected return, or optimize another clearly defined measure?
If the CIO prioritizes minimizing risk while seeking the return target, I would evaluate portfolios with more investment-grade bonds and Treasuries, subject to return feasibility. If the CIO prioritizes expected return, I would evaluate a higher global equity allocation while retaining the required reserves, liquidity, and issuer limits. A balanced objective could begin with the 60/40 benchmark, adjusted to satisfy the mandate. The CIO must choose the objective before optimization; the checker cannot choose it on the client's behalf.
Investment Policy Statement
What Is an IPS?
An Investment Policy Statement (IPS) documents an investor's objectives, constraints, governance, and investment guidelines. It helps managers construct portfolios consistent with the client's needs and evaluate proposed decisions against agreed standards.
How an IPS Works
An IPS separates desired outcomes, such as a long-run return target, from restrictions, such as minimum liquidity and issuer limits. It also records benchmark and implementation policies and identifies undefined terms that require client clarification.
Meridian IPS Summary
The Meridian Foundation manages $100 million over a seven-year horizon, with annual rebalancing. It seeks CPI + 4% net of costs over rolling five-year periods and uses a 60% global equities/40% U.S. investment-grade bonds benchmark. It pays $0.75 million quarterly and requires at least 3% in cash or eligible daily-liquid government securities. Its investment policies prohibit borrowing, short selling, and derivatives; cap a single company issuer at 8%; limit annual turnover to 25% without approval; and require at least 90% of assets to be redeemable within five business days. The calendar-year loss statement needs definition before it can be tested, and the optimization priority is missing.
Mapping S1–S10 to the IPS
Statement	IPS element	Interpretation
S1	Horizon / implementation	Seven years and annual rebalancing
S2	Return objective	CPI + 4%, net of costs, rolling five-year periods
S3	Spending / liquidity constraint	Twelve months of quarterly payouts in reserve-eligible assets
S4	Benchmark	60% global equities / 40% U.S. investment-grade bonds
S5	Investment restrictions	No borrowing, short sales, or derivatives
S6	Concentration restriction	Maximum 8% per single company issuer
S7	Trading restriction	Turnover ≤ 25% without approval
S8	Liquidity restriction	≥ 90% redeemable in five business days
S9	Unverifiable statement	Calendar-year loss threshold lacks measure and breach rule
S10	Preferences and missing decision	No sector/ESG/tax/home-bias preference; optimization goal unspecified


Reflect 
Why Passing Is Not the Same as Suitable
A checker can verify the measurable rules supplied to it but cannot establish that a portfolio will meet its investment return objective or satisfy all of the client's needs. Candidate D is a useful example: it passes the five programmed checks but may not generate sufficient real returns to support S2.
Statement Type That Was Least Clear
S9 is difficult because it sounds like a hard maximum-loss restriction, yet the CIO has not defined the measurement or consequences of a breach. It should therefore remain flagged for clarification instead of being converted into a guessed pass/fail test.
What This Lab Demonstrates
The lab separates coding correctness from investment suitability. The known-answer cases check calculation accuracy, the negative-weight probe tests whether the logic responds to invalid inputs, and Candidate D shows why a compliant portfolio still needs investment judgment.

Project 2 — Initial Client Mandate
Client Overview
Proposed fictional client: A university scholarship endowment with $50 million in assets that provides annual student scholarships. This is a new illustrative case, not a fact from the Meridian assignment.
Investment Objective
Seek an average annual return of 6%, net of investment costs, over rolling five-year periods, while maintaining resources for future scholarships. The 6% target is an assumed client goal for this exercise, not a guaranteed outcome.
Hard Constraints
Constraint	Proposed requirement
Assets	$50 million
Horizon	10 years
Annual scholarship distributions	$2 million
Reserve	12 months of distributions in cash or eligible government securities
Minimum reserve weight	4%
Five-business-day liquidity	At least 85%
Single-company issuer exposure	No more than 10%
Borrowing, short selling, derivatives	Not permitted
Rebalancing	Annually
Annual turnover	No more than 25% without approval


The reserve minimum is $2 million / $50 million × 100 = 4%.
Preferences
The fund prefers diversification across equities and high-quality fixed income and would like to avoid excessive volatility. These preferences are not additional numeric constraints unless the client defines them as such.
One Question for This Client
Should portfolio selection primarily seek long-term growth or prioritize reducing the risk that market losses disrupt scholarship payments?
If the client emphasizes growth, I would examine larger diversified equity allocations. If the client emphasizes payout stability, I would examine more high-quality fixed income and liquid reserves while assessing whether the 6% objective remains feasible. The answer would determine the optimization objective for Project 2.
AI Disclosure
I used ChatGPT to assist with the Python checker, explanations of its rules, Candidate D generation, Markdown organization, and an illustrative Project 2 mandate. AI also supplied study examples for statement classifications, the independent CIO question and judgment, and reflections; these examples must not be represented as independently authored AI-closed work. I personally supplied the normal-run Python output for Candidates A–D. 