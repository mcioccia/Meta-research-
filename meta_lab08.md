# Lab 08 — Meta Platforms: peer evidence and valuation triangulation

**AI-use disclosure:** Prepared with OpenAI Codex assistance for research, drafting, coding, and calculation checks, including two independent AI reviews. AI-generated content may contain errors. The student is responsible for reviewing the sources, calculations, and final judgments before submission; this disclosure does not claim that personal review has already occurred. This work is for educational purposes and is not personalized investment advice.

**Target:** Meta Platforms, Inc., Class A (NASDAQ: META).  
**Comparison date:** January 29, 2026, U.S. regular-session close, matching the saved Week 3 DCF date.  
**Prepared:** September 17, 2026; the analysis uses only financial information public by the comparison date.  
**Proposed coursework call:** **watch-defer**.  
**Status:** AI-assisted research draft for individual review. Two independent AI evidence reviews were completed; this document does not claim a human partner discussion occurred or that the student personally opened the sources. Company documents and the price pages identified below were opened during preparation.

## 1. Reopen and explain the method

The saved `asbury_comps.py` was rerun successfully: peer median 10.743987x, midpoint $231.00, and removal of GPI lowered the estimate by $15.18. Those training inputs are absent from `meta_comps.py`.

A peer's P/E measures how many dollars investors pay for one dollar of its annual earnings. Multiplying that multiple by Meta's annual EPS asks what one Meta share would be worth **if investors assigned Meta that peer's earnings multiple**. This requires an economic comparability judgment; a common industry label alone is insufficient.

P/E produces an **equity price per share**. Cash and debt are not added or subtracted. The DCF's separate enterprise-to-equity conversion is appropriate within that model.

## 2. Understand Meta and preserve the initial policy

Meta monetizes audience attention and advertiser results across its apps. FY2025 advertising revenue was $196.175 billion of $200.966 billion total revenue, approximately 97.6%. Reality Labs introduces a different business and investment profile. [Meta 2025 10-K, Item 1 Business and Note 2 Revenue][M10K]. Annual reported diluted EPS was positive, **$23.49**, announced January 28, 2026. [Annual release, full-year financial highlights and income statement][MREL].

**Focused research question:** At January 29, 2026 prices, do other advertising platforms provide a useful reference for Meta's earnings, given different business mixes, fiscal periods, tax effects and investment requirements?

### Initial policy — established before calculating peer multiples

- Require listed operating companies that monetize digital audiences through advertising, with comparable advertiser demand, targeting and platform economics.
- Qualify differences in business mix, scale, geography, spending and unusual tax effects. A qualification permits calculation but does not establish that the result is a reliable fair-value estimate.
- Exclude a business without a meaningful economic match, nonpositive annual reported diluted EPS, or missing/unverifiable required inputs. Do not infer a price or invent earnings.
- Use the latest **full-year GAAP diluted EPS public by the comparison date**, compatible USD/share-class and stock-split bases, and same-day closing share prices. Disclose differing fiscal periods. Do not annualize a quarter, replace GAAP with adjusted EPS, or use later earnings.
- Investigate exactly **Alphabet Class A (GOOGL)** and **Pinterest Class A (PINS)**. Do not rank them by the answer their multiples produce.

**Policy revisions:** none. Both candidates remain qualified. Neither is removed because of an inconvenient result. The removal calculations below are sensitivity exercises.

**Rejection evidence sought:** no material audience-advertising economics; a required denominator that is zero/negative; an unresolved share-class/currency mismatch; or an untraceable price or annual earnings figure. A large unusual tax effect triggers the policy's qualification and may justify withholding an investment-value conclusion even when arithmetic is possible.

## 3. Two sourced candidate decisions

| Candidate | Decision before valuation | Why it belongs | Material qualification and locator |
|---|---|---|---|
| Alphabet, GOOGL | **Qualify; include** | Search, YouTube and partner advertising monetize audience attention and measurable advertiser results. | Search intent, Cloud, subscriptions/devices and other businesses differ from Meta. Traffic-acquisition payments also affect economics. [2024 10-K, Item 1, Google Services—How We Make Money; Google Cloud, pp. 7–8][G10K]. |
| Pinterest, PINS | **Qualify; include** | Visual discovery connects users and commercial intent with advertisers through targeted ads and auctions. | Smaller, shopping-oriented platform; retail/consumer-goods advertiser concentration and user engagement differ. [2024 10-K, Item 1 Overview/Our Advertising System; Item 1A advertising and engagement risks, pp. 13–15][P10K]. A major tax benefit also distorts its annual earnings; see section 5. |

**Excluded candidates:** none among the two investigated. The target is excluded from its own peer set.

Two independent AI reviews received the same company, date, policy and two-candidate limit. Both located the same annual EPS and identified the Alphabet share-class distinction and Pinterest tax issue. Their agreement was a research lead; the primary documents were then checked directly.

## 4. Input audit: prices, periods and publication dates

All prices are USD per listed Class A share on **January 29, 2026**. Use the historical **Close**, not dividend-adjusted close, intraday prices or current quotes. The historical prices and reported EPS are on their post-split share bases; no additional split factor is applied. No ADR conversion is involved.

| Company | Closing price | Annual reported diluted EPS | Fiscal year ended | EPS publication evidence available by cutoff | Price evidence and locator |
|---|---:|---:|---|---|---|
| META — target | $738.31 | $23.49 | Dec. 31, 2025 | Jan. 28, 2026 [release][MREL], full-year 2025 income statement, diluted row. Jan. 29 10-K Note 3 corroborates. | [StockInvest earnings history][MP], Dec. 31, 2025 report / Jan. 28 release block, price table row Jan. 29, 2026. |
| GOOGL — qualify | $338.25 | **$8.05** | Dec. 31, 2024 | [2024 10-K][G10K], Note 12, p. 83, 2024 **Class A** diluted row. SEC accepted Feb. 4, 2025 at 20:41:40; formal filing date **Feb. 5, 2025**, used conservatively as availability date. [Filing index][GIDX]. | [Odin500 GOOGL historical OHLC][GP], Jan. 29, 2026 row, Close column. |
| PINS — qualify | $22.35 | $2.67 | Dec. 31, 2024 | Feb. 6, 2025 [release][PREL], Condensed Consolidated Statements of Operations, **year ended 2024**, diluted row. | [Trading 212 PINS share history][PP], Historical data, Jan. 29, 2026 row, Close column. This is the shares page, not a CFD quote. |

**Price-source limitation:** the requested starting point, [Nasdaq META][MN], [GOOGL][GN] and [PINS][PN] historical pages, returned unavailable data. The table therefore uses opened secondary sources. Search-indexed Yahoo historical rows independently corroborated GOOGL $338.25 and PINS $22.35, but direct Yahoo opens failed; those snippets are corroboration, not the main source. **Direct exchange confirmation remains unresolved.** A Nasdaq/NYSE historical export or comparable official closing-price record would resolve that narrower verification gap. No missing exchange price has been fabricated.

**Share-class check:** Alphabet's consolidated headline EPS is $8.04; Note 12 gives GOOGL Class A $8.05. The calculator uses the class-specific figure. Pinterest's Q4 EPS is $2.68, while its full-year figure is $2.67; the latter is used. [G10K][G10K], [Pinterest annual release][PREL].

**Knowledge-date check:** Meta had released FY2025; the peers had not. Alphabet's January 8 announcement scheduled FY2025 results for **February 4, 2026**; Pinterest's January 16 announcement scheduled its results for **February 12, 2026**. Both dates are after cutoff. [Alphabet schedule][GSCHED], [Pinterest schedule][PSCHED]. Thus Meta FY2025 versus peer FY2024 is an explicit limitation of the latest-public-annual convention, not a reason to import later earnings.

## 5. Earnings quality: positive does not mean comparable

- **Pinterest:** FY2024 net income of about $1.862 billion includes a **$1.597 billion deferred-tax valuation-allowance release benefit**, approximately 86% of reported net income. It enlarges EPS and lowers P/E without equivalent recurring advertising profit. Retain $2.67 reported EPS for this lab. [Annual release, highlights and tax footnote (2)][PREL].
- **Meta:** the 2025 10-K reports a **$15.93 billion Q3 tax charge**, including a $14.03 billion valuation allowance. This depresses its reported EPS. [Note 14 Income Taxes, p. 121][M10K]. The annual release also explains the tax effect in financial-highlight footnote (1). [MREL][MREL].
- **Alphabet:** consolidated earnings include nonoperating investment results as well as the operating businesses. [2024 10-K, Other Income (Expense), Net][G10K].

**Interpretation:** these denominators do not cleanly represent the same recurring earnings concept. Pinterest's benefit lowers the multiple applied to Meta; Meta's charge lowers the EPS to which that multiple is applied. Both mechanically pull that endpoint downward. This is an analytical limitation, not proof that either share is cheap. No tax-adjusted or management-adjusted EPS is substituted.

## 6. Calculator results and arithmetic check

The standalone, standard-library `meta_comps.py` keeps editable inputs at the top. It retains exact fractions through calculation, deduplicates tickers, excludes META, labels unusable inputs, and handles zero or one valid peer. All multiples are displayed to six decimals and prices to cents. The saved run is `meta_comps_output.txt`.

| Calculation | Result |
|---|---:|
| GOOGL P/E: 338.25 / 8.05 | 42.018634x |
| PINS P/E: 22.35 / 2.67 | 8.370787x |
| Peer median P/E | 25.194710x |
| Minimum peer P/E × Meta EPS | $196.63 |
| Median peer P/E × Meta EPS | **$591.82** |
| Maximum peer P/E × Meta EPS | $987.02 |
| Mechanical peer-implied band | **$196.63–$987.02** |
| Meta observed P/E, comparison only | 31.430822x |

**Independent arithmetic check:** 338.25 / 8.05 = 33825 / 805 = 42.01863354037267…; multiplying by 23.49 gives $987.017701863354… → **$987.02**. The ratio has units of price dollars per annual earnings dollar; the final result is dollars per Meta share.

### Predict, then remove one peer

Prediction recorded before the run: removing lower-multiple Pinterest should raise the midpoint; removing higher-multiple Alphabet should lower it.

| Removal | Remaining reference | Change from full-peer midpoint, using unrounded values |
|---|---:|---:|
| Remove PINS; keep GOOGL | $987.02 | **+$395.19** |
| Remove GOOGL; keep PINS | $196.63 | **−$395.19** |

For example, $987.017701863354… − $591.823738572126… = $395.193963291228… → **+$395.19**. Subtracting rounded displays gives a different last cent. With one remaining peer there is one reference estimate, not an empirical range. Removing that sole peer leaves no usable estimate.

This very large sensitivity measures dependence on peer choice. It does not justify dropping Pinterest after seeing the result. The two-peer policy remains unchanged.

## 7. Compare with the saved Week 3 DCF

| Method | Meta result and date | Main assumption or limitation |
|---|---|---|
| Week 3 DCF | Jan. 29, 2026; saved range **$212.32–$369.19**; base **$268.13** | Starting FCFF $46.66B; annual growth −60%, +60%, +40%, +20%, +10%; base WACC 9.4%, terminal growth 2.5%. Range varies WACC 8.4%–10.4% and terminal growth 1.5%–3.5%, holding the cash-flow path fixed. It is a sensitivity range, not a confidence interval. |
| Peer P/E | Jan. 29, 2026 prices; mechanical band **$196.63–$987.02**, median **$591.82** | Two qualified peers; older peer fiscal periods, materially different taxes and business mixes; secondary price-source limitation. The band is not adopted as a reliable fair-value range. |

**Saved-work check:** `dcf.py meta` reproduces the range and $268.1297 base. The base uses cash/securities $81.592B, debt $58.744B and 2.574B diluted shares. Terminal value represents about **78.39%** of enterprise value. These are the existing model assumptions, not new estimates for Lab 08. Sources were retained in `meta_dcf.md` and `meta reverse DCF.md` in the work folder.

**Date correction in interpretation:** the reverse-DCF file also discusses a later $653.69 price. That price is excluded from this January 29 comparison. Use $738.31 for this date. Also, `dcf.py` defaults to the training case; the explicit `meta` argument is necessary.

**Why methods differ:** the DCF prices a particular future cash-flow path, including a sharp initial contraction and subsequent recovery. Peer P/E transfers market prices of other companies' historical earnings onto Meta. Capital expenditure affects cash flow immediately while accounting earnings reflect different timing, including depreciation and tax items. The methods therefore test different assumptions. Their disagreement directs research toward cash conversion, investment returns and earnings comparability; it does not justify averaging their values.

The saved DCF is rerun, not rebuilt. Its WACC inputs, simplified FCFF construction, cash/debt treatment and diluted-share assumption retain their original limitations. In particular, the exact −60% decline and recovery rates remain scenarios. Meta's $115–135B 2026 capex guidance alone does not establish that cash-flow path. [Jan. 28 release, CFO Outlook Commentary][MREL].

## 8. Skeptical AI review and source-checked judgment

Before the skeptical review, the provisional call was watch-defer. The evidence most likely to change it is a source-backed operating-cash-flow and capital-spending forecast that materially changes the DCF, together with evidence that the peer earnings comparison is economically representative.

The independent reviewer received the table above, inputs, limitations and provisional call. Its main criticism was that reported EPS is not necessarily comparable recurring earnings. It also challenged the unsupported exact initial FCFF contraction.

| Criticism | Judgment | Check and response |
|---|---|---|
| The peer midpoint assumes comparable earnings despite tax distortions. | **Accept** | Pinterest's tax footnote and Meta's Note 14 support the concern (section 5). Keep GAAP inputs; withhold a fair-value interpretation. |
| Latest-public annual EPS mixes fiscal periods. | **Accept** | The peer release schedules fall after cutoff (section 4). Retain the required annual convention and disclose the mismatch; do not use hindsight. |
| The DCF's exact 60% FCFF contraction needs an operating bridge. | **Accept** | The saved model specifies it as an assumption. Management's capex guidance does not supply a complete operating-cash-flow forecast. |
| The models may have a company or valuation-object mismatch. | **Reject that concern for this run** | Both value Meta equity per share. P/E has no cash/debt bridge; DCF performs its own bridge once. Alphabet Class A price and EPS match. |
| Exchange closing-price verification is incomplete. | **Unresolved** | Opened secondary tables trace the inputs; official historical exchange records remain to be confirmed. |

**Reviewer question:** What source-backed operating cash flow and capital-expenditure forecast produces the DCF's initial 60% FCFF decline, and does watch-defer survive correcting that assumption?

**Answer:** The saved materials do not establish that exact decline; it is an illustrative scenario. A defensible revision would project operating cash generation, capital spending, leases and the FCFF reconciliation consistently, rather than infer cash flow from capex alone. Watch-defer remains appropriate while that work is unresolved. If evidence supports much stronger durable cash generation and an independently justified valuation above the comparison price with a sufficient margin of safety, reconsider initiation. The current work does not establish that result.

## 9. Conditional conclusion

**Watch-defer at the January 29, 2026 comparison date.** Alphabet and Pinterest belong because their advertising-platform economics are relevant, but both require explicit qualifications. Their multiples add a market-based cross-check and expose how strongly the conclusion depends on earnings quality and peer selection.

The defensible numeric statements are the **saved DCF scenario range of $212.32–$369.19** and the **mechanical peer band of $196.63–$987.02**. The latter is too sensitive and economically uneven to adopt as fair value. **Withhold a combined investment-value range; do not average the methods or use their overlap as a new estimate.** The $738.31 historical share price lies above the saved DCF range and inside the broad peer band; neither observation by itself establishes value.

Evidence that could change the call: an operating forecast linking AI spending to durable incremental advertising cash generation; support for recurring earnings comparability; and official confirmation of the historical prices. Any future-date update must advance all relevant prices and information dates together rather than insert later EPS into this frozen comparison.

## 10. Run commands and checkout

Verified PowerShell commands for the existing work folder:

```powershell
& 'C:\Users\mac10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'C:\Users\mac10\finance-ai-work\asbury_comps.py'
& 'C:\Users\mac10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'C:\Users\mac10\finance-ai-work\meta_comps.py'
& 'C:\Users\mac10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'C:\Users\mac10\finance-ai-work\dcf.py' meta
```

No packages need to be installed; the peer calculator does not fetch data.

**Files to submit:** `meta_lab08.md`, `meta_comps.py`, and optionally `meta_comps_output.txt`. GitHub publication is pending the student's repository destination. The supplied CinderZhang link is the course handout, not a verified personal submission repository. No GitHub file link has been invented.

Before individual submission, open the cited sources and decide whether the proposed peer judgments and conditional call reflect your own reasoning. Any human-partner discussion remains yours to complete.

## Source links

All sources below were accessed during this preparation. Section and row locators appear with the claims above. Historical-data access dates are later than the valuation date; no later earnings or later-date market quotes are used in the calculation.

[M10K]: https://www.sec.gov/Archives/edgar/data/1326801/000162828026003942/meta-20251231.htm
[MREL]: https://www.sec.gov/Archives/edgar/data/1326801/000162828026003832/meta-12312025xexhibit991.htm
[G10K]: https://www.sec.gov/Archives/edgar/data/1652044/000165204425000014/goog-20241231.htm
[GIDX]: https://www.sec.gov/Archives/edgar/data/1652044/000165204425000014/0001652044-25-000014-index.htm
[P10K]: https://www.sec.gov/Archives/edgar/data/1506293/000150629325000022/pins-20241231.htm
[PREL]: https://investor.pinterestinc.com/news-and-events/press-releases/press-releases-details/2025/Pinterest-Announces-Fourth-Quarter-and-Full-Year-2024-Results-Delivers-First-Billion-Dollar-Revenue-Quarter/
[GSCHED]: https://abc.xyz/investor/news/news-details/2026/Alphabet-Announces-Date-of-Fourth-Quarter-and-Fiscal-Year-2025-Financial-Results-Conference-Call-2026-_PQVrgzUKX/default.aspx
[PSCHED]: https://investor.pinterestinc.com/news-and-events/press-releases/press-releases-details/2026/Pinterest-to-Announce-Fourth-Quarter-and-Full-Year-2025-Results/default.aspx
[MP]: https://stockinvest.us/earnings-report/META
[GP]: https://www.odin500.com/ticker/googl
[PP]: https://www.trading212.com/trading-instruments/isa/PINS.US
[MN]: https://www.nasdaq.com/market-activity/stocks/meta/historical
[GN]: https://www.nasdaq.com/market-activity/stocks/googl/historical
[PN]: https://www.nasdaq.com/market-activity/stocks/pins/historical
