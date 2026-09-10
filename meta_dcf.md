# Meta Platforms, Inc. (NASDAQ: META) — Five-Row DCF Model

Valuation date anchored to Form 10-K filing date: **January 29, 2026** (Fiscal Year ended December 31, 2025).  
Primary SEC filing: [Meta Platforms, Inc. Form 10-K (2025)](https://www.sec.gov/Archives/edgar/data/1326801/0001628280-26-003942-index.htm).  
*Dollar figures are in USD billions unless noted.*

---

## 1. Five-Row Input Table

| Input | Meta value | Source and calculation |
| :--- | :--- | :--- |
| **Starting FCFF** | **$46.66B**, simplified estimate | Operating cash flow 115.800 + cash interest 0.696 × (1 − 21%) − equipment/property purchases 69.691. The 21% tax shield is an assumption. [Cash-flow statements, pp. 92–93](https://www.sec.gov/Archives/edgar/data/1326801/000162828026003942/meta-20251231.htm). |
| **Growth, Years 1–5** | **−60%, +60%, +40%, +20%, +10%** for 2026–2030 | Illustrative assumptions. The initial decline reflects planned 2026 capex of $115–135B; subsequent recovery assumes cash generation improves relative to spending. The exact percentages are my scenario. [Item 7, MD&A, pp. 77–78](https://www.sec.gov/Archives/edgar/data/1326801/000162828026003942/meta-20251231.htm). |
| **WACC** | **9.4%** estimated | Calculated below using the January 29 Treasury yield and an equity risk premium, with explicit assumptions for beta, borrowing spread and capital weights. [Treasury rates](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value=2026&type=daily_treasury_yield_curve), [NYU premium data](https://pages.stern.nyu.edu/adamodar/New_Home_Page/datafile/histimpl.html). |
| **Terminal growth** | **2.5%** nominal, assumed | Below the approximately 3.8% long-run nominal economic benchmark implied by the Fed’s 1.8% real growth + 2% inflation projections. [Fed projections, Table 1](https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20251210.htm). |
| **Cash · debt · shares** | **$81.592B · $58.744B · 2.574B shares** | Cash includes 35.873 cash/equivalents + 45.719 marketable securities. Debt is bond carrying value. Shares are diluted weighted-average shares. [Balance sheet p. 88; debt Note 10; EPS Note 3](https://www.sec.gov/Archives/edgar/data/1326801/000162828026003942/meta-20251231.htm). |

---

## 2. Supporting Calculations & Accounting Notes

### WACC Derivation
- Risk-free rate (10-Yr Treasury as of Jan 29, 2026): 4.24%
- Equity Risk Premium (ERP): 4.23%
- Beta: 1.25
- Cost of Equity: $4.24\% + 1.25 \times 4.23\% = 9.53\%$
- Borrowing spread: 0.80% → Pre-tax cost of debt = $4.24\% + 0.80\% = 5.04\%$
- Marginal tax rate: 21% → After-tax cost of debt = $5.04\% \times (1 - 21\%) = 3.98\%$
- Capital weights: 97% Equity / 3% Debt
- **WACC** = $97\% \times 9.53\% + 3\% \times 5.04\% \times (1 - 21\%) = 9.36\% \approx \mathbf{9.4\%}$

### Annual FCFF Projection (Years 1–5)
- **Year 1 (2026)**: $\$46.66\text{B} \times (1 - 0.60) = \mathbf{\$18.66\text{B}}$
- **Year 2 (2027)**: $\$18.664\text{B} \times (1 + 0.60) = \mathbf{\$29.86\text{B}}$
- **Year 3 (2028)**: $\$29.8624\text{B} \times (1 + 0.40) = \mathbf{\$41.81\text{B}}$
- **Year 4 (2029)**: $\$41.8074\text{B} \times (1 + 0.20) = \mathbf{\$50.17\text{B}}$
- **Year 5 (2030)**: $\$50.1688\text{B} \times (1 + 0.10) = \mathbf{\$55.19\text{B}}$

### Accounting Details
- **Meta reported FCF**: $\$43.585\text{B}$ (operating cash flow of $\$115.800\text{B}$ less capital expenditures of $\$69.691\text{B}$ and principal payments on finance leases of $\$2.524\text{B}$).
- **Lease liabilities**: Finance lease liabilities add $\$1.184\text{B}$ if included in total debt, bringing debt input to $\$59.928\text{B}$.

---

## 3. Valuation Summary & Share Price

- **Model Implied Value per Diluted Share**: **$268.13** (`$268.1297`)
- **Market Closing Price (January 29, 2026)**: **$738.31**

### Twelve-Line DCF Model Output (`python dcf.py`)
```text
FCFF Year 1: 18.6640
FCFF Year 2: 29.8624
FCFF Year 3: 41.8074
FCFF Year 4: 50.1688
FCFF Year 5: 55.1857
Present value of the five explicit FCFF: 144.1815
Terminal value at Year 5: 819.7878
Present value of the terminal value: 523.1363
Enterprise value: 667.3178
Equity value: 690.1658
Value per diluted share: 268.1297
Present value of the terminal value as a share of enterprise value: 0.7839
```

*Educational disclaimer: This DCF analysis was prepared for coursework learning purposes and does not constitute personalized investment advice.*

