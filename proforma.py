# AI-use disclosure: This file has been prepared or edited with assistance from OpenAI Codex. AI-generated content may contain errors. The author is responsible for verifying sources, calculations, and conclusions.
# Educational purposes only. Not financial or investment advice, and not a recommendation to buy, sell, or hold any security.

"""Lab 09: ABG five-year three-statement engine. Python standard library only.

Run: python proforma.py
     python proforma.py --break-cash
Source: CinderZhang/FIN43900-Fall2026, lessons/week-05/lab-09-proforma-build.md
All amounts USD millions; shares millions. Educational model.
"""

if __name__ == "__main__":
    print('AI-use disclosure: This file has been prepared or edited with assistance from OpenAI Codex. AI-generated content may contain errors. The author is responsible for verifying sources, calculations, and conclusions.')
    print('Educational purposes only. Not financial or investment advice, and not a recommendation to buy, sell, or hold any security.')
    print()

from copy import deepcopy
import argparse
import math

ABG_SOURCE = 'https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-05/lab-09-proforma-build.md'
ABG_OPENING = dict(revenue=17999.0, cash=40.4, inventory=2135.8, ppe=3070.4,
                   other_assets=6371.6, floor_plan=2027.0, debt=3572.0,
                   other_liabilities=2127.5, equity=3891.7, revolver=0.0)
ABG_ASSUMPTIONS = dict(
    growth=[.018]*5, gross_margin=.1705, sga_ratio=[.665,.655,.645,.645,.645],
    depreciation_ratio=82.4/3070.4, impairment=120.0, capex=[250.0]*5,
    tax=.255, inventory_days=2135.8/(17999.0-3071.7)*365,
    floor_plan_ratio=2027.0/2135.8, other_wc_ratio=.008,
    minimum_cash=25.0, revolver_limit=850.0, revolver_rate=.06,
    repayment=[150.0]*5, buyback=[150.0]*5,
    floor_plan_rate=.0467, debt_rate=.0544, discount_rate=.10,
    terminal_growth=.025, shares=17.951349)

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

def project_abg(assumptions=None, opening=None):
    a=deepcopy(ABG_ASSUMPTIONS if assumptions is None else assumptions)
    b=deepcopy(ABG_OPENING if opening is None else opening)
    validate_numbers(a); validate_numbers(b)
    for key in ('growth','sga_ratio','capex','repayment','buyback'):
        require(len(a[key])==5, f'{key} must have five annual inputs')
    require(0<=a['tax']<=1 and 0<=a['gross_margin']<=1,'Invalid tax or gross margin')
    rows=[]
    for i,year in enumerate(range(2026,2031)):
        o=deepcopy(b)
        require(a['growth'][i]>-1, 'Revenue growth must exceed -100%')
        require(0<=a['sga_ratio'][i]<=1, 'Invalid SG&A ratio')
        require(a['capex'][i]>=0 and a['repayment'][i]>=0 and a['buyback'][i]>=0,
                'Capital spending, repayment and buyback must be nonnegative')
        revenue=o['revenue']*(1+a['growth'][i])
        gp=revenue*a['gross_margin']; sga=gp*a['sga_ratio'][i]
        dep=o['ppe']*a['depreciation_ratio']; imp=a['impairment']
        ebit=gp-sga-dep-imp
        interest=o['floor_plan']*a['floor_plan_rate']+o['debt']*a['debt_rate']+o['revolver']*a['revolver_rate']
        pretax=ebit-interest; tax=max(0,pretax)*a['tax']; ni=pretax-tax
        income=dict(revenue=revenue,cost_of_sales=revenue-gp,gross_profit=gp,sga=sga,
                    depreciation=dep,impairment=imp,operating_income=ebit,
                    interest=interest,pretax_income=pretax,tax=tax,net_income=ni)
        repayment=min(a['repayment'][i],o['debt'])
        dwc=a['other_wc_ratio']*(revenue-o['revenue'])
        # All non-cash balance sheet lines first. Cash is never an accounting plug.
        b=dict(revenue=revenue,inventory=(revenue-gp)*a['inventory_days']/365,
               ppe=o['ppe']+a['capex'][i]-dep,
               other_assets=o['other_assets']+dwc-imp,
               debt=o['debt']-repayment,other_liabilities=o['other_liabilities'],
               equity=o['equity']+ni-a['buyback'][i])
        b['floor_plan']=b['inventory']*a['floor_plan_ratio']
        dinv=b['inventory']-o['inventory']; dfp=b['floor_plan']-o['floor_plan']
        # Course convention: floor-plan inventory funding is operating throughout.
        cfo=ni+dep+imp-dinv-dwc+dfp
        fcfe=cfo-a['capex'][i]-repayment
        before=o['cash']+fcfe-a['buyback'][i]
        b['cash'],b['revolver'],draw=funding(before,o['revolver'],a['minimum_cash'],a['revolver_limit'])
        cff=-repayment-a['buyback'][i]+draw
        cf=dict(net_income=ni,depreciation=dep,impairment=imp,
                change_inventory=dinv,change_other_wc=dwc,change_floor_plan=dfp,
                cfo=cfo,capex=a['capex'][i],cfi=-a['capex'][i],
                debt_repayment=repayment,buyback=a['buyback'][i],net_revolver_draw=draw,
                cff=cff,net_change=cfo-a['capex'][i]+cff,fcfe=fcfe,
                opening_cash=o['cash'],closing_cash=b['cash'])
        rows.append(dict(year=year,opening=o,income=income,balance=b,cashflow=cf,
                         minimum_cash=a['minimum_cash'],revolver_limit=a['revolver_limit'],kind='abg'))
    return rows

def check_row(row):
    """Recompute every check from the statements, never trust a saved PASS flag."""
    o=row['opening']; b=row['balance']; c=row['cashflow']; inc=row['income']
    if row['kind']=='abg':
        assets=b['cash']+b['inventory']+b['ppe']+b['other_assets']
        liabilities=b['floor_plan']+b['debt']+b['other_liabilities']+b['revolver']
        gap=assets-liabilities-b['equity']
        equity_expected=o['equity']+inc['net_income']-c['buyback']
        ppe_expected=o['ppe']+c['capex']-inc['depreciation']
        checks={'balance_gap':gap,
                'gross_profit_gap':inc['gross_profit']-inc['revenue']+inc['cost_of_sales'],
                'operating_income_gap':inc['operating_income']-inc['gross_profit']+inc['sga']+inc['depreciation']+inc['impairment'],
                'inventory_gap':b['inventory']-o['inventory']-c['change_inventory'],
                'cfo_detail_gap':c['cfo']-inc['net_income']-inc['depreciation']-inc['impairment']+c['change_inventory']+c['change_other_wc']-c['change_floor_plan'],
                'cfi_detail_gap':c['cfi']+c['capex'],
                'cff_detail_gap':c['cff']+c['debt_repayment']+c['buyback']-c['net_revolver_draw'],
                'fcfe_gap':c['fcfe']-c['cfo']+c['capex']+c['debt_repayment'],
                'inventory_funding_gap':b['floor_plan']-o['floor_plan']-c['change_floor_plan'],
                'other_assets_gap':b['other_assets']-o['other_assets']-c['change_other_wc']+inc['impairment']}
    else:
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
    return checks

def assert_balanced(rows):
    require(len(rows)==5,'Valuation requires five projected years')
    prior=None
    for row in rows:
        validate_numbers(row,f"FY{row['year']}E")
        if prior:
            require(row['year']==prior['year']+1,'Forecast years must be consecutive')
            require(row['opening']==prior['balance'],f"FY{row['year']}E opening balances do not match prior closing balances")
        o=row['opening']
        ak=('cash','inventory','ppe','other_assets') if row['kind']=='abg' else row['asset_keys']
        lk=('floor_plan','debt','other_liabilities','revolver') if row['kind']=='abg' else row['liability_keys']
        require(abs(sum(o[k] for k in ak)-sum(o[k] for k in lk)-o['equity'])<1e-6,'Opening balance sheet does not balance')
        checks=check_row(row)
        for name,value in checks.items():
            good=value>=-1e-7 if name.endswith('headroom') else abs(value)<1e-6
            require(good,f"FY{row['year']}E {name}: gap {value:+.1f} million (exact {value:+.8f}); valuation refused")
        for key in ('cash','ppe','debt','revolver'):
            require(row['balance'][key]>=-1e-7,f"FY{row['year']}E negative {key}; valuation refused")
        prior=row
    return True

def value_abg(rows, assumptions=None):
    a=ABG_ASSUMPTIONS if assumptions is None else assumptions
    validate_numbers(a)
    assert_balanced(rows)
    r=a['discount_rate']; g=a['terminal_growth']
    require(r>g and r>0 and g>-1, 'Terminal growth must be below the positive discount rate')
    require(a['shares']>0,'Shares must be positive')
    require(rows[-1]['balance']['revolver']<1e-7,'Outstanding terminal revolver: supply a terminal financing policy before valuing')
    # Exact Lab 09 valuation convention: use the specified five FCFE amounts.
    flows=[x['cashflow']['fcfe'] for x in rows]
    terminal_cf=(flows[-1]+rows[-1]['cashflow']['debt_repayment'])*(1+g)
    require(terminal_cf>0,'Nonpositive terminal cash flow: extend the forecast before valuing')
    pv=sum(cf/(1+r)**(i+1) for i,cf in enumerate(flows))
    pv_terminal=terminal_cf/(r-g)/(1+r)**5
    equity=pv+pv_terminal
    return dict(pv_explicit=pv,pv_terminal=pv_terminal,equity_value=equity,
                terminal_share=pv_terminal/equity,value_per_share=equity/a['shares'])

def table(title, rows, section, fields):
    print('\n'+title+' (USD millions)')
    print(f"{'Line':36}"+''.join(f"{str(r['year'])+'E':>14}" for r in rows))
    for key,label in fields:
        print(f'{label:36}'+''.join(f"{(0.0 if abs(r[section][key])<1e-7 else r[section][key]):14,.1f}" for r in rows))

def print_checks(rows):
    print('\nINDEPENDENT CHECKS (USD millions; gaps must be zero)')
    print(f"{'Year':8}{'Balance gap':>14}{'Cash link':>14}{'PP&E gap':>14}{'Cash >= floor':>18}")
    for row in rows:
        c=check_row(row)
        clean=lambda v: 0.0 if abs(v)<1e-7 else v
        print(f"{row['year']:<8}{clean(c['balance_gap']):14,.1f}{clean(c['cash_link_gap']):14,.1f}{clean(c['ppe_gap']):14,.1f}{str(c['cash_floor_headroom']>=-1e-7):>18}")

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--break-cash',action='store_true',help='Deliberately break FY2026 cash; must exit with an error')
    args=parser.parse_args(); rows=project_abg()
    if args.break_cash: rows[0]['balance']['cash']=ABG_OPENING['cash']
    print('ABG | Lab 09 exact instructor assumptions | 2026-2030 | Educational model')
    table('INCOME STATEMENT',rows,'income',[(k,k.replace('_',' ').title()) for k in rows[0]['income']])
    table('BALANCE SHEET',rows,'balance',[(k,k.replace('_',' ').title()) for k in rows[0]['balance'] if k!='revenue'])
    table('CASH FLOW STATEMENT',rows,'cashflow',[(k,k.replace('_',' ').title()) for k in rows[0]['cashflow']])
    print_checks(rows)
    v=value_abg(rows)
    print(f"\nEquity value: ${v['equity_value']:,.2f} million\nValue after 2030: {v['terminal_share']:.2%}\nValue per share: ${v['value_per_share']:.2f}")

if __name__=='__main__':
    try: main()
    except ModelError as exc: raise SystemExit(str(exc))
