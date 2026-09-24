> **AI-use disclosure:** This file has been prepared or edited with assistance from OpenAI Codex. AI-generated content may contain errors. The author is responsible for verifying sources, calculations, and conclusions.
>
> **Educational purposes only. Not financial or investment advice, and not a recommendation to buy, sell, or hold any security.**

# META: model checks and market comparison

## Model checks

All five years pass the accounting checks. Cash stays at or above the $10 billion minimum.

| Year | Balance gap | Ending cash | Minimum cash | Result |
|---|---:|---:|---:|---|
| 2026 | $0.0 million | $10.00 billion | $10.00 billion | PASS |
| 2027 | $0.0 million | $10.00 billion | $10.00 billion | PASS |
| 2028 | $0.0 million | $17.97 billion | $10.00 billion | PASS |
| 2029 | $0.0 million | $57.28 billion | $10.00 billion | PASS |
| 2030 | $0.0 million | $117.69 billion | $10.00 billion | PASS |

No revolver is drawn: existing cash and sales of marketable securities cover the early funding needs. Securities sales are $16.178 billion in 2026 and $13.119 billion in 2027; the modeled revolver limit is zero.

Source: the completed `meta_proforma.py` run, saved in `META_proforma_output.txt` in this folder. The main valuation uses economic FCFF discounted at WACC and includes negative forecast cash flows.

## Comparison sentence

Using the same 2.574 billion-share proxy, my model based on January 29, 2026 assumptions says **$216.38 per share**, while the market quote was **[$770.25 on September 24, 2026, at 2:03 p.m. EDT](https://stockanalysis.com/stocks/meta/)**—what new information or stronger future cash-flow expectations would explain that difference?

The market price is an intraday snapshot, not the day's closing price. The 2.574 billion shares are the model's fixed FY2025 diluted weighted-average share proxy, not a verified September 24 outstanding share count. Applying that same proxy gives model equity value of approximately $556.97 billion and market-implied equity value of $1,982.62 billion. The model and quote have different information dates; this is not a valuation updated with September financial information.

## Revenue-growth assumption: META

**Question:** Meta’s revenue depends heavily on advertising demand and engagement. Why did you choose your revenue-growth assumption, and what evidence would make you lower it?

**Answer:** I based my growth assumption on Meta’s recent revenue trend and its continued growth in ad impressions, pricing, and AI-driven advertising tools. I would lower it if advertising demand weakened, engagement growth slowed, regulation limited ad targeting, or competition reduced Meta’s ability to maintain ad pricing.

## Separate company example: Visa

The following Q&A concerns Visa, not the META forecast above.

**Question:** Why use a 10% net-revenue growth judgment when FY2025 client incentives rose faster than net revenue and can reduce reported revenue conversion?

**Answer:** I used 10% because it is slightly below Visa’s recent 10.7% revenue-growth trend, so the forecast does not assume continued acceleration. I would lower it if payment volume, cross-border activity, or value-added-services growth weakened, or if client incentives continued increasing faster than gross revenue.
