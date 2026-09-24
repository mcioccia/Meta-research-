"""META standalone five-year three-statement pro forma, 2026-2030.

AI-use disclosure: Prepared or edited with assistance from OpenAI Codex.
AI-generated content may contain errors. The author is responsible for verifying
sources, calculations, and conclusions.
Educational purposes only. Not financial or investment advice, and not a
recommendation to buy, sell, or hold any security.

Run: python meta_proforma.py
Failure demonstration: python meta_proforma.py --break-cash
Funding stress: python meta_proforma.py --scenario high-capex
Assumptions and opening balances are embedded below; no other files or packages
are required. All dollars and shares are in millions. This is the January 29,
2026 coursework scenario, not a current-market valuation.

The META adaptation includes R&D in operating costs and links infrastructure
capex, construction, depreciation, stock compensation, leases and liquidity.
The main valuation retains the existing FCFF/WACC method, with negative flows
included. Separate positive-only FCFE subtotals satisfy the classroom display
request; they are not complete equity valuations.
"""
import argparse
from copy import deepcopy
import math

DISCLOSURE = (
    "AI-use disclosure: Prepared or edited with OpenAI Codex assistance. "
    "Verify sources, calculations and conclusions.\n"
    "Educational purposes only. Not financial or investment advice; "
    "not a recommendation to buy, sell or hold any security."
)

# Edit these sourced inputs to explore a different scenario.


META_CONFIG = {'company': 'Meta Platforms (META)',
 'valuation_date': '2026-01-29',
 'units': 'USD millions; shares in millions',
 'sources': {'M25': 'https://www.sec.gov/Archives/edgar/data/1326801/000162828026003942/meta-20251231.htm',
             'M24': 'https://www.sec.gov/Archives/edgar/data/1326801/000132680125000017/meta-20241231.htm',
             'M23': 'https://www.sec.gov/Archives/edgar/data/1326801/000132680124000012/meta-20231231.htm',
             'E25': 'https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Fourth-Quarter-and-Full-Year-2025-Results/'},
 'opening': {'revenue': 200966,
             'advertising': 196175,
             'other_foa': 2584,
             'rl_revenue': 2207,
             'cash': 35873,
             'securities': 45719,
             'receivables': 19769,
             'other_current': 6524,
             'restricted_current': 837,
             'ppe': 176400,
             'land': 3687,
             'cip': 50521,
             'active_ppe': 122192,
             'nonmarket_investments': 27524,
             'operating_rou': 20404,
             'goodwill': 24534,
             'intangibles': 3692,
             'other_noncurrent': 4745,
             'payables_accruals': 34913,
             'operating_lease': 25153,
             'finance_lease': 1184,
             'debt': 58744,
             'tax_liability': 21005,
             'other_liabilities': 3377,
             'revolver': 0,
             'equity': 217243,
             'capex_payable': 4402},
 'opening_source': 'M25 consolidated balance sheet p.88; Notes 6-9 pp.107-110. Other current = 7361-837 '
                   'restricted cash. Operating payables/accruals = 8894+30729-308 current finance '
                   'lease-4402 accrued PP&E = 34913. Accrued PP&E 4402 is held flat, so forecast asset '
                   'additions equal cash property purchases. Other liabilities = 4253-876 noncurrent '
                   'finance lease. Other noncurrent = 8437-3692 intangibles. Intangibles comprise 3295 '
                   'finite-lived and 397 indefinite-lived assets. PP&E detail sums land 3687 + CIP 50521 '
                   '+ active assets 122192 = 176400. No opening plug.',
 'assumptions': {'impression_growth': {'value': [0.1, 0.08, 0.07, 0.06, 0.05],
                                       'label': 'judgment',
                                       'reason': "Fade below FY2025's 12% impression growth as the "
                                                 'advertising base matures; no unproven standalone AI '
                                                 'revenue is added.',
                                       'source': 'M25 Item 7, advertising discussion p.73'},
                 'ad_price_growth': {'value': [0.06, 0.05, 0.04, 0.035, 0.03],
                                     'label': 'judgment',
                                     'reason': "Fade from FY2025's 9% price growth to allow for weaker "
                                               'incremental targeting gains and mix effects. Advertising '
                                               'growth compounds price and volume, rather than adding '
                                               'them.',
                                     'source': 'M25 Item 7 p.73'},
                 'other_foa_growth': {'value': [0.25, 0.2, 0.18, 0.15, 0.12],
                                      'label': 'judgment',
                                      'reason': 'Below the reported 50% FY2025 increase in other FoA '
                                                'revenue; smaller messaging/subscription businesses '
                                                'mature.',
                                      'source': 'M25 Note 2 revenue; Item 7 p.73'},
                 'rl_growth': {'value': [0.1, 0.1, 0.08, 0.08, 0.05],
                               'label': 'judgment',
                               'reason': "Modest hardware recovery scenario above FY2025's 3%; no "
                                         'assumption that Reality Labs becomes a large profit source.',
                               'source': 'M25 Note 2 and segment Note 16'},
                 'opex_ex_da_ratio': {'value': [0.5912977220829279, 0.58, 0.56, 0.54, 0.52],
                                      'label': 'judgment',
                                      'reason': '2026 non-D&A costs are calibrated once so base total '
                                                'operating expense equals 165500, midpoint of the '
                                                'January 28 range 162000-169000. Later ratios fade from '
                                                'about 59.13% to 52%, still above FY2025 49.30%. '
                                                'Includes R&D, Reality Labs, SBC and operating rent. '
                                                'Ratios stay fixed in depreciation shocks so higher D&A '
                                                'reduces income. Our slower revenue scenario puts 2026 '
                                                "operating income below management's expectation of "
                                                'growth; this is a conservative analyst case, not a '
                                                'replication of the full outlook.',
                                      'source': 'E25 CFO Outlook; M25 income/cash-flow statements; '
                                                'analyst cost-revenue path'},
                 'cash_capex': {'value': [124692, 115000, 105000, 95000, 95000],
                                'label': 'judgment',
                                'reason': '2026 property purchases plus 308 of finance-lease principal '
                                          'total 125000, the midpoint of the filed 115000-135000 capital '
                                          'expenditure range. The split and later spending decline are '
                                          'judgments, not guidance. A sustained-high-spend case is '
                                          'tested separately.',
                                'source': 'M25 Item 7 p.77; Note 7 p.108'},
                 'capex_guidance_2026': {'value': [115000, 135000],
                                         'label': 'guidance',
                                         'reason': 'Filed management range available at the January 29 '
                                                   'cutoff; later 2026 updates are excluded from this '
                                                   'historical scenario.',
                                         'source': 'M25 Item 7 p.77'},
                 'opening_active_depreciation': {'value': 18000,
                                                 'label': 'judgment',
                                                 'reason': 'Use the historical FY2025 PP&E depreciation '
                                                           'of 18000 as a constant annual charge on the '
                                                           'opening active pool, capped at remaining '
                                                           'carrying value. The input is observed '
                                                           'history but carrying it forward is judgment '
                                                           'because asset ages are not disclosed.',
                                                 'source': 'M25 Note 6 p.107'},
                 'cip_commission_fraction': {'value': 0.5,
                                             'label': 'judgment',
                                             'reason': 'Commission half of opening '
                                                       'construction-in-progress each year; the filing '
                                                       'does not give a project commissioning schedule. '
                                                       'CIP is not depreciated until commissioned.',
                                             'source': 'M25 Note 1 PP&E accounting and Note 6; opening '
                                                       'CIP 50521'},
                 'capex_in_service_fraction': {'value': 0.6,
                                               'label': 'judgment',
                                               'reason': '60% of current-year cash purchases enter '
                                                         'service at midyear; the remainder stays in '
                                                         'CIP. The same transfer changes CIP, active '
                                                         'PP&E and depreciation.',
                                               'source': 'M25 Note 1: land and CIP are not depreciated'},
                 'new_server_share': {'value': 0.8,
                                      'label': 'judgment',
                                      'reason': '80% of commissioned additions are treated as '
                                                'servers/network assets; 20% as buildings. This '
                                                'simplified mix is not a disclosed spending allocation.',
                                      'source': 'M25 Notes 1 and 6, infrastructure asset categories'},
                 'server_life': {'value': 5.5,
                                 'label': 'judgment',
                                 'reason': 'Most servers/network assets use 5.5 years after the January '
                                           '2025 estimate change. Applying 5.5 years to all new server '
                                           'cohorts is the model convention; test a shorter life.',
                                 'source': 'M25 Notes 1 and 6'},
                 'building_life': {'value': 27.5,
                                   'label': 'judgment',
                                   'reason': 'Midpoint of the filed 25-30 year building lives, applied '
                                             'to the non-server share of commissioned assets.',
                                   'source': 'M25 Note 1 PP&E useful-life table'},
                 'amortization': {'value': [1259, 1162, 771, 39, 27],
                                  'label': 'guidance',
                                  'reason': 'Use the filed expected amortization schedule for existing '
                                            'finite-lived intangibles. No new acquisitions or purchased '
                                            'intangibles are assumed; the 397 indefinite-lived balance '
                                            'is not amortized. This is an accounting estimate schedule, '
                                            'not earnings guidance. In the permitted three-label '
                                            'taxonomy, a forward disclosed accounting estimate is '
                                            'classified as guidance.',
                                  'source': 'M25 Note 8, expected amortization table p.110'},
                 'receivables_ratio': {'value': 0.09836987351094215,
                                       'label': 'judgment',
                                       'reason': 'The opening number is history; using it unchanged in '
                                                 'the forecast is judgment. 19769 / 200966; maintain '
                                                 'FY2025 receivables intensity.',
                                       'source': 'M25 balance sheet p.88 and income statement p.89'},
                 'other_current_ratio': {'value': 0.03246320273081019,
                                         'label': 'judgment',
                                         'reason': 'The opening number is history; using it unchanged in '
                                                   'the forecast is judgment. (7361-837 restricted cash) '
                                                   '/ 200966; restricted cash stays fixed and is not '
                                                   'available for funding.',
                                         'source': 'M25 balance sheet and restricted-cash '
                                                   'reconciliation'},
                 'payables_accruals_ratio': {'value': 0.1737259038842391,
                                             'label': 'judgment',
                                             'reason': 'The opening number is history; using it '
                                                       'unchanged in the forecast is judgment. '
                                                       '(8894+30729-308 finance lease-4402 accrued PP&E) '
                                                       '/ 200966. Exclude both finance debt and capital '
                                                       'accruals from the operating funding ratio. Other '
                                                       'accruals remain aggregated; this is a '
                                                       'simplifying historical-intensity assumption.',
                                             'source': 'M25 balance sheet and Notes 7, 9'},
                 'tax_rate': {'value': 0.18,
                              'label': 'judgment',
                              'reason': 'Normalize below the 29.6% FY2025 rate distorted by the large '
                                        "tax charge; near FY2023's 17.6%, above FY2024's 11.8%. Cash tax "
                                        'equals tax expense; existing long-term tax liabilities are held '
                                        'separately and deducted in the value bridge.',
                              'source': 'M25 Note 14 income taxes'},
                 'debt_rate': {'value': 0.045,
                               'label': 'judgment',
                               'reason': 'Simplified 4.5% expense rate on opening bond carrying value, '
                                         'not a measured market borrowing yield. Keeps financing '
                                         'explicit; no forecast investment income or capitalized '
                                         'interest.',
                               'source': 'M25 Note 10 debt; simplification requiring student defense'},
                 'finance_lease_rate': {'value': 0.041,
                                        'label': 'judgment',
                                        'reason': 'FY2025 weighted-average finance lease discount rate '
                                                  'used as an interest proxy.',
                                        'source': 'M25 Note 7 p.108'},
                 'lease_principal': {'value': [308, 60, 60, 55, 55],
                                     'label': 'judgment',
                                     'reason': '2026 uses the filed current finance-lease liability. '
                                               'Later principal amounts approximate the disclosed '
                                               'declining maturity schedule; not a contractual '
                                               'amortization schedule. No new finance leases: future '
                                               'modeled investment is cash-funded.',
                                     'source': 'M25 Note 7 p.108'},
                 'debt_repayment': {'value': [0, 0, 0, 0, 0],
                                    'label': 'judgment',
                                    'reason': 'Refinance bonds at carrying value on maturity, leaving '
                                              'net bond debt flat. Financing access and rates are '
                                              'assumptions, not guaranteed outcomes.',
                                    'source': 'M25 Note 10'},
                 'sbc_ratio': {'value': 0.10164405919409253,
                               'label': 'judgment',
                               'reason': 'The opening number is history; using it unchanged in the '
                                         'forecast is judgment. 20427 / 200966. SBC remains an '
                                         'income-statement cost, is added back in cash from operations '
                                         'and credited to equity. Valuation deducts the grant expense '
                                         'from cash flow to recognize its economic cost with a fixed '
                                         'diluted share count.',
                               'source': 'M25 cash flow pp.92-93; Note 13'},
                 'share_withholding': {'value': [18000, 18000, 18000, 18000, 18000],
                                       'label': 'judgment',
                                       'reason': 'Near FY2025 net-share-settlement tax cash payments of '
                                                 '18400; financing distribution reduces cash and equity. '
                                                 'Not deducted again in economic FCFF because the full '
                                                 'SBC cost is already recognized there.',
                                       'source': 'M25 cash flow pp.92-93'},
                 'buyback': {'value': [0, 0, 10000, 10000, 10000],
                             'label': 'judgment',
                             'reason': 'Suspend discretionary repurchases in 2026-27 during the '
                                       'infrastructure build, then restart at 10000 annually. This is an '
                                       'analyst financing policy, not announced management policy. Cash '
                                       'and equity both reflect it; no mechanical reduction to the fixed '
                                       'valuation share denominator.',
                             'source': 'M25 cash flow pp.92-93'},
                 'dividends': {'value': [5500, 5500, 5500, 5500, 5500],
                               'label': 'judgment',
                               'reason': 'Near FY2025 dividends of 5324, kept flat for a transparent '
                                         'funding scenario.',
                               'source': 'M25 cash flow pp.92-93'},
                 'minimum_cash': {'value': 10000,
                                  'label': 'judgment',
                                  'reason': 'Operating liquidity reserve; sell marketable securities '
                                            'before any modeled facility draw. Restricted cash cannot '
                                            'fund the reserve. Reserve is excluded from surplus cash in '
                                            'valuation.',
                                  'source': 'M25 balance sheet and cash reconciliation; analyst policy'},
                 'revolver_limit': {'value': 0,
                                    'label': 'judgment',
                                    'reason': 'No unverified financing facility is invented. If '
                                              'liquidity falls below the floor after securities are '
                                              'sold, the engine refuses valuation; change the '
                                              'distributions or explicitly document a funding plan.',
                                    'source': 'Analyst policy'},
                 'revolver_rate': {'value': 0.06,
                                   'label': 'judgment',
                                   'reason': 'Inactive at the zero facility limit. Scenario borrowing '
                                             'must carry an explicit interest assumption.',
                                   'source': 'Analyst policy'},
                 'discount_rate': {'value': 0.094,
                                   'label': 'judgment',
                                   'reason': 'Retain the Lab 05 9.4% WACC to isolate the cash-flow model '
                                             'change. Its assumed beta and capital weights have not been '
                                             'independently re-estimated here.',
                                   'source': 'Existing meta_dcf.md, WACC derivation'},
                 'terminal_growth': {'value': 0.025,
                                     'label': 'judgment',
                                     'reason': 'Retain the prior nominal perpetual growth assumption, '
                                               'strictly below WACC; terminal reinvestment is required '
                                               'to support it.',
                                     'source': 'Existing meta_dcf.md'},
                 'terminal_roic': {'value': 0.15,
                                   'label': 'judgment',
                                   'reason': '15% return on incremental terminal invested capital. '
                                             'Stable reinvestment = terminal NOPAT × growth / ROIC; do '
                                             'not assume zero investment while growing forever. This is '
                                             'not a measured Meta return.',
                                   'source': 'Analyst terminal-state assumption; subject to sensitivity'},
                 'shares': {'value': 2574,
                            'label': 'judgment',
                            'reason': 'The opening number is history; using it unchanged in the forecast '
                                      'is judgment. FY2025 weighted-average diluted shares retained for '
                                      'comparability with Lab 05. It is a proxy, not the point-in-time '
                                      'diluted count; economic SBC cost is retained to avoid treating '
                                      'future grants as free.',
                            'source': 'M25 EPS Note 3'},
                 'nonmarket_value_fraction': {'value': 0.5,
                                              'label': 'judgment',
                                              'reason': 'Value non-marketable investments at half their '
                                                        '27524 carrying amount to reflect uncertain '
                                                        'realization; no investment income enters the '
                                                        'operating forecast. A valuation policy, not a '
                                                        'market quote.',
                                              'source': 'M25 Note 5 and balance sheet'},
                 'fixed_balances_policy': {'value': 'Hold land, restricted cash, goodwill, operating '
                                                    'lease assets/liabilities, nonmarket investments, '
                                                    'existing tax liability and remaining other '
                                                    'noncurrent balances flat; no M&A, FX, remeasurement '
                                                    'gains, asset disposals or new financing leases. '
                                                    'Hold accrued PP&E 4402 flat, so cash property '
                                                    'purchases equal asset additions.',
                                           'label': 'judgment',
                                           'reason': 'Condensed coursework scope. Operating rent remains '
                                                     'within expenses and cash costs; equal replacement '
                                                     'lease activity is implicit in flat lease balances. '
                                                     'The undisclosed timing/mix of 103770 in '
                                                     'uncommenced lease commitments is not individually '
                                                     'modeled, making this a material limitation.',
                                           'source': 'M25 Notes 1, 7 and 8'},
                 'expenses_guidance_2026': {'value': [162000, 169000],
                                            'label': 'guidance',
                                            'reason': 'Total expense guidance available at January 29; '
                                                      'choosing the midpoint and later expense ratios '
                                                      'are judgments.',
                                            'source': 'E25 CFO Outlook Commentary'},
                 'tax_guidance_2026': {'value': [0.13, 0.16],
                                       'label': 'guidance',
                                       'reason': 'Management expected a 13-16% effective tax rate absent '
                                                 'tax-landscape changes. The model deliberately uses the '
                                                 'more conservative 18% normalized rate rather than '
                                                 'labeling it guidance.',
                                       'source': 'E25 CFO Outlook Commentary'},
                 'classroom_cost_of_equity': {'value': 0.0953,
                                              'label': 'judgment',
                                              'reason': 'Retain the Lab 05 cost of equity for the '
                                                        'separate FCFE classroom subtotal; not newly '
                                                        'estimated. The main FCFF valuation uses WACC.',
                                              'source': 'Existing meta_dcf.md: 4.24% + assumed beta 1.25 '
                                                        'x ERP 4.23%, rounded.'}},
 'company_specific_policy': 'No modeled floor-plan loan. AI infrastructure capex is the company-specific '
                            'line: cash purchases increase PP&E; construction in progress enters service '
                            'explicitly; depreciation then reduces earnings. No separate forecast '
                            'impairment is assumed. Inventory is not separately disclosed, not proven to '
                            'be zero.'}


ASSETS = ('cash', 'securities', 'receivables', 'other_current', 'restricted_current',
          'ppe', 'nonmarket_investments', 'operating_rou', 'goodwill', 'intangibles',
          'other_noncurrent')
LIABILITIES = ('payables_accruals', 'capex_payable', 'operating_lease', 'finance_lease',
               'debt', 'tax_liability', 'other_liabilities', 'revolver')

def load_inputs():
    """Return independent editable inputs without reading another file."""
    return deepcopy(META_CONFIG)


class ModelError(ValueError):
    """An accounting identity, financing constraint or valuation rule failed."""

def require(condition, message):
    if not condition:
        raise ModelError(message)

def validate_numbers(obj, path='inputs'):
    if isinstance(obj, dict):
        for key, value in obj.items(): validate_numbers(value, f'{path}.{key}')
    elif isinstance(obj, (list,tuple)):
        for n,value in enumerate(obj): validate_numbers(value, f'{path}[{n}]')
    elif isinstance(obj, (int,float)):
        require(math.isfinite(obj), f'{path}: non-finite number')

def funding(cash_before, opening_revolver, minimum, limit):
    """End-year draw/repayment; interest is on opening debt to avoid circularity."""
    require(limit >= opening_revolver >= 0, 'Invalid opening revolver or limit')
    if cash_before < minimum:
        net_draw = min(minimum-cash_before, limit-opening_revolver)
    else:
        net_draw = -min(opening_revolver, cash_before-minimum)
    return cash_before+net_draw, opening_revolver+net_draw, net_draw

def values(config):
    return {k:v['value'] for k,v in config['assumptions'].items()}

def assert_opening_balanced(opening, year=2026):
    gap = sum(opening[k] for k in ASSETS) - sum(opening[k] for k in LIABILITIES) - opening['equity']
    require(abs(gap) < 1e-6,
            f"FY{year}E opening_balance_gap: gap {gap:+.1f} million "
            f"(exact {gap:+.8f}); valuation refused")


def project_meta(config=None):
    config=deepcopy(load_inputs() if config is None else config)
    a=values(config); b=deepcopy(config['opening']); validate_numbers(config)
    assert_opening_balanced(b)
    for name,entry in config['assumptions'].items():
        require(entry['label'] in ('history','guidance','judgment'),f'{name}: missing valid label')
        require(bool(entry['reason']) and bool(entry['source']),f'{name}: missing reason/source')
    for key in ('impression_growth','ad_price_growth','other_foa_growth','rl_growth','opex_ex_da_ratio',
                'cash_capex','lease_principal','debt_repayment','share_withholding','buyback','dividends','amortization'):
        require(len(a[key])==5,f'{key} requires five annual inputs')
    for key in ('tax_rate','cip_commission_fraction','capex_in_service_fraction','new_server_share','sbc_ratio'):
        require(0<=a[key]<=1,f'{key} must be between 0 and 1')
    require(a['server_life']>0 and a['building_life']>0,'Useful lives must be positive')
    require(a['minimum_cash']>=0 and a['revolver_limit']>=0,'Invalid funding policy')
    require(all(x>=0 for x in a['amortization']) and a['opening_active_depreciation']>=0,'Invalid D&A')
    for key in ('receivables_ratio','other_current_ratio','payables_accruals_ratio','debt_rate','finance_lease_rate','revolver_rate'):
        require(a[key]>=0,f'{key} must be nonnegative')
    # Old assets are a separate pool. New assets use tracked cost/life cohorts.
    old_active=b['active_ppe']; cohorts=[]; rows=[]
    for i,year in enumerate(range(2026,2031)):
        o=deepcopy(b); b=deepcopy(o)
        for key in ('impression_growth','ad_price_growth','other_foa_growth','rl_growth'):
            require(a[key][i]>-1,f'{key}: growth must exceed -100%')
        for key in ('cash_capex','lease_principal','debt_repayment','share_withholding','buyback','dividends'):
            require(a[key][i]>=0,f'{key} must be nonnegative')
        require(0<=a['opex_ex_da_ratio'][i]<=1,'Invalid expense ratio')
        b['advertising']=o['advertising']*(1+a['impression_growth'][i])*(1+a['ad_price_growth'][i])
        b['other_foa']=o['other_foa']*(1+a['other_foa_growth'][i])
        b['rl_revenue']=o['rl_revenue']*(1+a['rl_growth'][i])
        b['revenue']=b['advertising']+b['other_foa']+b['rl_revenue']; revenue=b['revenue']
        capex=a['cash_capex'][i]
        commissioned=o['cip']*a['cip_commission_fraction']+capex*a['capex_in_service_fraction']
        dep=min(a['opening_active_depreciation'],old_active); old_active-=dep
        for cohort in cohorts:
            charge=min(cohort['remaining'],cohort['annual']); cohort['remaining']-=charge; dep+=charge
        for share,life in ((a['new_server_share'],a['server_life']),(1-a['new_server_share'],a['building_life'])):
            cost=commissioned*share; annual=cost/life; first=min(cost,annual*.5)
            cohorts.append(dict(remaining=cost-first,annual=annual)); dep+=first
        # $397m indefinite-lived intangibles are not amortized.
        amort=min(a['amortization'][i],max(0,o['intangibles']-397))
        costs=revenue*a['opex_ex_da_ratio'][i]; sbc=revenue*a['sbc_ratio']
        require(costs>=sbc,'Operating costs must include SBC')
        ebit=revenue-costs-dep-amort
        interest=o['debt']*a['debt_rate']+o['finance_lease']*a['finance_lease_rate']+o['revolver']*a['revolver_rate']
        pretax=ebit-interest; tax=max(pretax,0)*a['tax_rate']; ni=pretax-tax
        inc=dict(advertising=b['advertising'],other_foa=b['other_foa'],rl_revenue=b['rl_revenue'],
                 revenue=revenue,operating_costs_ex_da=costs,sbc=sbc,depreciation=dep,amortization=amort,
                 operating_income=ebit,interest=interest,pretax_income=pretax,tax=tax,net_income=ni)
        b['receivables']=revenue*a['receivables_ratio']; b['other_current']=revenue*a['other_current_ratio']
        b['payables_accruals']=revenue*a['payables_accruals_ratio']
        dnwc=(b['receivables']-o['receivables'])+(b['other_current']-o['other_current'])-(b['payables_accruals']-o['payables_accruals'])
        b['cip']=o['cip']+capex-commissioned
        b['active_ppe']=old_active+sum(c['remaining'] for c in cohorts)
        b['ppe']=o['ppe']+capex-dep; b['intangibles']=o['intangibles']-amort
        repay=min(a['debt_repayment'][i],o['debt']); lease=min(a['lease_principal'][i],o['finance_lease'])
        b['debt']=o['debt']-repay; b['finance_lease']=o['finance_lease']-lease
        buyback=a['buyback'][i]; dividend=a['dividends'][i]; withholding=a['share_withholding'][i]
        b['equity']=o['equity']+ni+sbc-buyback-dividend-withholding
        cfo=ni+dep+amort+sbc-dnwc
        cff_before=-repay-lease-buyback-dividend-withholding
        cash_before=o['cash']+cfo-capex+cff_before
        sales=min(o['securities'],max(0,a['minimum_cash']-cash_before))
        b['securities']=o['securities']-sales
        b['cash'],b['revolver'],draw=funding(cash_before+sales,o['revolver'],a['minimum_cash'],a['revolver_limit'])
        cfi=-capex+sales; cff=cff_before+draw
        economic_fcff=ebit*(1-a['tax_rate'])+dep+amort-capex-dnwc
        cf=dict(net_income=ni,depreciation=dep,amortization=amort,sbc=sbc,change_nwc=dnwc,cfo=cfo,
                capex=capex,commissioned_assets=commissioned,securities_sales=sales,cfi=cfi,
                debt_repayment=repay,lease_principal=lease,buyback=buyback,dividends=dividend,
                share_withholding=withholding,net_revolver_draw=draw,cff=cff,net_change=cfo+cfi+cff,
                opening_cash=o['cash'],closing_cash=b['cash'],economic_fcff=economic_fcff)
        cf['cash_fcfe'] = cfo-capex-repay-lease+draw
        cf['economic_fcfe'] = cf['cash_fcfe']-sbc
        rows.append(dict(year=year,kind='meta',opening=o,income=inc,balance=b,cashflow=cf,
                         minimum_cash=a['minimum_cash'],revolver_limit=a['revolver_limit'],
                         tax_rate=a['tax_rate'],asset_keys=ASSETS,liability_keys=LIABILITIES))
    return rows

def check_row(row):
    """Recompute every check from the statements, never trust a saved PASS flag."""
    o=row['opening']; b=row['balance']; c=row['cashflow']; inc=row['income']
    assets=sum(b[k] for k in row['asset_keys'])
    liabilities=sum(b[k] for k in row['liability_keys'])
    checks={'balance_gap':assets-liabilities-b['equity'],
            'operating_income_gap':inc['operating_income']-inc['revenue']+inc['operating_costs_ex_da']+inc['depreciation']+inc['amortization'],
            'working_capital_gap':c['change_nwc']-((b['receivables']-o['receivables'])+(b['other_current']-o['other_current'])-(b['payables_accruals']-o['payables_accruals'])),
            'cfo_detail_gap':c['cfo']-inc['net_income']-inc['depreciation']-inc['amortization']-inc['sbc']+c['change_nwc'],
            'cfi_detail_gap':c['cfi']+c['capex']-c['securities_sales'],
            'cff_detail_gap':c['cff']+c['debt_repayment']+c['lease_principal']+c['buyback']+c['dividends']+c['share_withholding']-c['net_revolver_draw'],
            'fcff_gap':c['economic_fcff']-(inc['operating_income']*(1-row['tax_rate'])+inc['depreciation']+inc['amortization']-c['capex']-c['change_nwc']),
            'securities_gap':b['securities']-o['securities']+c['securities_sales'],
            'finance_lease_gap':b['finance_lease']-o['finance_lease']+c['lease_principal'],
            'intangible_gap':b['intangibles']-o['intangibles']+inc['amortization'],
            'cip_gap':b['cip']-o['cip']-c['capex']+c['commissioned_assets'],
            'ppe_detail_gap':b['ppe']-b['land']-b['cip']-b['active_ppe']}
    equity_expected=o['equity']+inc['net_income']+inc['sbc']-c['buyback']-c['dividends']-c['share_withholding']
    ppe_expected=o['ppe']+c['capex']-inc['depreciation']
    checks.update(cash_link_gap=b['cash']-o['cash']-c['net_change'],
                  opening_cash_gap=c['opening_cash']-o['cash'],
                  net_income_link_gap=c['net_income']-inc['net_income'],
                  pretax_gap=inc['pretax_income']-inc['operating_income']+inc['interest'],
                  earnings_gap=inc['net_income']-inc['pretax_income']+inc['tax'],
                  cash_statement_gap=b['cash']-c['closing_cash'],
                  cf_sum_gap=c['net_change']-c['cfo']-c['cfi']-c['cff'],
                  ppe_gap=b['ppe']-ppe_expected,
                  equity_gap=b['equity']-equity_expected,
                  debt_gap=b['debt']-o['debt']+c['debt_repayment'],
                  revolver_gap=b['revolver']-o['revolver']-c['net_revolver_draw'],
                  cash_floor_headroom=b['cash']-row['minimum_cash'],
                  revolver_headroom=row['revolver_limit']-b['revolver'])
    checks.update(
        revenue_sum_gap=inc['revenue']-inc['advertising']-inc['other_foa']-inc['rl_revenue'],
        tax_gap=inc['tax']-max(0,inc['pretax_income'])*row['tax_rate'],
        cash_fcfe_gap=c['cash_fcfe']-c['cfo']+c['capex']+c['debt_repayment']+c['lease_principal']-c['net_revolver_draw'],
        economic_fcfe_gap=c['economic_fcfe']-c['cash_fcfe']+c['sbc'])
    return checks

def assert_balanced(rows):
    """Refuse valuation on any accounting or funding failure; never plug cash."""
    require(len(rows) == 5, 'Valuation requires five projected years')
    prior = None
    for year, row in zip(range(2026, 2031), rows):
        require(row['year'] == year, f'Expected FY{year}E; forecast year sequence is wrong')
        validate_numbers(row, f'FY{year}E')
        assert_opening_balanced(row['opening'], year)
        if prior:
            require(row['opening'].keys() == prior['balance'].keys(),
                    f'FY{year}E opening balance keys differ from the prior closing statement')
            for key, value in row['opening'].items():
                gap = value-prior['balance'][key]
                require(abs(gap) < 1e-6,
                        f'FY{year}E opening_{key}_gap: gap {gap:+.8f} million; valuation refused')
        for name, gap in check_row(row).items():
            valid = gap >= -1e-7 if name.endswith('headroom') else abs(gap) < 1e-6
            require(valid, f'FY{year}E {name}: gap {gap:+.1f} million '
                    f'(exact {gap:+.8f}); valuation refused')
        for key in ('cash', 'securities', 'ppe', 'cip', 'active_ppe', 'intangibles',
                    'debt', 'finance_lease', 'revolver'):
            amount = row['balance'][key]
            require(amount >= -1e-7,
                    f'FY{year}E negative_{key}: gap {amount:+.8f} million; valuation refused')
        prior = row
    return True


def value_meta(rows, config=None):
    config=load_inputs() if config is None else config; a=values(config)
    validate_numbers(a); assert_balanced(rows)
    require(rows[0]['opening']==config['opening'],'Valuation opening balances differ from forecast')
    r=a['discount_rate']; g=a['terminal_growth']; roic=a['terminal_roic']
    require(r>g>=0 and r>0,'Require 0 <= terminal growth < WACC')
    require(roic>g and a['shares']>0,'Require terminal ROIC > growth and positive shares')
    require(0<=a['nonmarket_value_fraction']<=1,'Invalid investment haircut')
    # Negative explicit cash flows are economic costs; never discard them.
    pv=sum(row['cashflow']['economic_fcff']/(1+r)**(i+1) for i,row in enumerate(rows))
    terminal_nopat=rows[-1]['income']['operating_income']*(1-a['tax_rate'])*(1+g)
    terminal_reinvestment=terminal_nopat*g/roic
    terminal_fcff=terminal_nopat-terminal_reinvestment
    require(terminal_fcff>0,'Nonpositive terminal FCFF: extend the forecast')
    pvt=terminal_fcff/(r-g)/(1+r)**5; ev=pv+pvt; o=config['opening']
    cash_surplus=max(0,o['cash']-a['minimum_cash'])
    bridge=cash_surplus+o['securities']+o['nonmarket_investments']*a['nonmarket_value_fraction']-o['debt']-o['finance_lease']-o['tax_liability']-o['revolver']
    equity=ev+bridge
    return dict(pv_explicit=pv,pv_terminal=pvt,enterprise_value=ev,equity_bridge=bridge,
                equity_value=equity,value_per_share=equity/a['shares'],terminal_share=pvt/ev,
                terminal_nopat=terminal_nopat,terminal_reinvestment=terminal_reinvestment,terminal_fcff=terminal_fcff)

def scenario(config,name):
    c=deepcopy(config)
    if name=='high-capex': c['assumptions']['cash_capex']['value']=[134692,130000,125000,120000,115000]
    elif name=='shorter-life': c['assumptions']['server_life']['value']=4.0
    elif name!='base': raise ModelError('Unknown scenario')
    return c

def table(title, rows, section, fields):
    print('\n'+title+' (USD millions)')
    print(f"{'Line':36}"+''.join(f"{str(r['year'])+'E':>14}" for r in rows))
    for key,label in fields:
        print(f'{label:36}'+''.join(f"{(0.0 if abs(r[section][key])<1e-7 else r[section][key]):14,.1f}" for r in rows))

def print_checks(rows):
    print('\nCHECK BLOCK (USD millions; accounting gaps must be zero)')
    print(f"{'Year':8}{'Balance gap':>15}{'Max link gap':>16}{'Cash':>16}{'Cash floor':>16}{'Result':>9}")
    for row in rows:
        checks = check_row(row)
        largest = max(abs(v) for k, v in checks.items() if not k.endswith('headroom'))
        passed = largest < 1e-6 and all(v >= -1e-7 for k,v in checks.items() if k.endswith('headroom'))
        gap = 0 if abs(checks['balance_gap']) < 1e-7 else checks['balance_gap']
        print(f"{row['year']:<8}{gap:15,.1f}{largest:16,.8f}"
              f"{row['balance']['cash']:16,.1f}{row['minimum_cash']:16,.1f}{'PASS' if passed else 'FAIL':>9}")

def print_balance_totals(rows):
    for label, fn in (
        ('Total assets', lambda b: sum(b[k] for k in ASSETS)),
        ('Total liabilities', lambda b: sum(b[k] for k in LIABILITIES)),
        ('Liabilities plus equity', lambda b: sum(b[k] for k in LIABILITIES)+b['equity'])):
        print(f'{label:36}'+''.join(f"{fn(r['balance']):14,.1f}" for r in rows))

def print_fcfe_subtotals(rows, config):
    assert_balanced(rows)
    print('\nFCFE STATUS (before shareholder distributions; USD millions)')
    for row in rows:
        cf = row['cashflow']
        cash_status = 'negative FCFE' if cf['cash_fcfe'] < 0 else 'positive FCFE'
        economic_status = 'negative FCFE' if cf['economic_fcfe'] < 0 else 'positive FCFE'
        print(f"{row['year']}: cash FCFE {cf['cash_fcfe']:,.1f} ({cash_status}); "
              f"SBC-adjusted FCFE {cf['economic_fcfe']:,.1f} ({economic_status})")
    ke = values(config)['classroom_cost_of_equity']
    require(ke > 0, 'Classroom cost of equity must be positive')
    for key, label in (('cash_fcfe', 'Cash FCFE'), ('economic_fcfe', 'SBC-adjusted FCFE')):
        positive = sum(max(0,r['cashflow'][key])/(1+ke)**(i+1) for i,r in enumerate(rows))
        signed = sum(r['cashflow'][key]/(1+ke)**(i+1) for i,r in enumerate(rows))
        print(f'{label}: positive-only five-year PV at {ke:.2%} = {positive:,.2f}; signed PV = {signed:,.2f}')
    print('Positive-only subtotals are classroom displays, not complete equity values.')
    print('Negative cash flows remain in the statements, funding needs and complete DCF.')

def main():
    print(DISCLOSURE)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenario', choices=('base','high-capex','shorter-life'), default='base')
    parser.add_argument('--break-cash', action='store_true',
                        help='Deliberately add 1,000 to FY2026 cash; valuation must refuse')
    args = parser.parse_args()
    config = scenario(load_inputs(), args.scenario)
    rows = project_meta(config)
    if args.break_cash:
        rows[0]['balance']['cash'] += 1000
    print(f"\nMETA | {args.scenario} | 2026-2030 | information cutoff {config['valuation_date']}")
    print('Company-specific line: AI infrastructure capex. No floor-plan loan is modeled.')
    print('Operating costs include R&D, SBC and rent; separate D&A is deducted only once.')
    print('Revenue segment and PP&E detail rows are sublines, not additional assets or revenue.')
    opening = config['opening']
    print(f"Opening assets {sum(opening[k] for k in ASSETS):,.1f} = "
          f"liabilities {sum(opening[k] for k in LIABILITIES):,.1f} + equity {opening['equity']:,.1f}")
    table('INCOME STATEMENT', rows, 'income', [(k,k.replace('_',' ').title()) for k in rows[0]['income']])
    table('BALANCE SHEET', rows, 'balance', [(k,k.replace('_',' ').title()) for k in ASSETS+LIABILITIES+('equity',)])
    print_balance_totals(rows)
    table('PP&E DETAIL (included above)', rows, 'balance', [(k,k.replace('_',' ').title()) for k in ('land','cip','active_ppe')])
    table('CASH FLOW STATEMENT', rows, 'cashflow', [(k,k.replace('_',' ').title()) for k in rows[0]['cashflow']])
    print_checks(rows)
    assert_balanced(rows)
    print_fcfe_subtotals(rows, config)
    value = value_meta(rows, config)
    print('\nCOMPLETE VALUATION: economic FCFF at 9.4% WACC in the base case')
    print('Negative explicit FCFF is retained. SBC economic cost is retained with fixed share count.')
    print(f"Five-year FCFF present value: ${value['pv_explicit']:,.2f} million")
    print(f"Terminal present value: ${value['pv_terminal']:,.2f} million")
    print(f"Enterprise value: ${value['enterprise_value']:,.2f} million")
    print(f"Net opening asset/debt adjustments: ${value['equity_bridge']:,.2f} million")
    print(f"Equity value: ${value['equity_value']:,.2f} million")
    print(f"Share of enterprise value after 2030: {value['terminal_share']:.2%}")
    print(f"Value per share: ${value['value_per_share']:.2f}")
    print(f"Terminal FCFF: {value['terminal_fcff']:,.1f}; terminal reinvestment: {value['terminal_reinvestment']:,.1f}")
    print('A negative terminal cash flow requires a path to sustainable positive cash flow; do not force a positive terminal value.')
    print('Base assumptions include a capex slowdown and simplified lease/asset schedules; balancing does not establish realism.')

if __name__ == '__main__':
    try:
        main()
    except ModelError as exc:
        raise SystemExit(str(exc))

