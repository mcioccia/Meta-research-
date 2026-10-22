"""Test the saved QQQ-only prices with the existing Lab 15 engine.
AI-use disclosure: Prepared with OpenAI Codex assistance; verify results.
Educational purposes only. Not financial or investment advice.
"""
import csv
import hashlib
import json
import math
from pathlib import Path
import portfolio as p

ROOT = Path(__file__).resolve().parent
OBJECTIVE = .0749
RESERVE_MINIMUM = .03

def main():
    path = ROOT / 'QQQ_prices.csv'
    with path.open(encoding='utf-8-sig') as f:
        rows = list(csv.reader(line for line in f if not line.startswith('#')))
    assert rows[0] == ['Date','QQQ'] and len(rows) == 61
    prices = [float(row[1]) for row in rows[1:]]
    result = {'ai_disclosure':p.AI_NOTICE,'educational_notice':p.EDUCATIONAL_NOTICE,
              'objective':OBJECTIVE,'reserve_minimum':RESERVE_MINIMUM,
              'reserve_eligible':['BIL'],'csv_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
              'runs':{}}
    lines = [p.AI_NOTICE,p.EDUCATIONAL_NOTICE,
             'QQQ-only test. Target 7.49%; at least 3% in BIL. QQQ is not reserve-eligible.',
             'Annualized historical estimates, not forecasts.']
    for name,recent in [('All months',False),('Last 36 months',True)]:
        estimates = p.estimate_from_csv(path,recent)
        returns = [b/a-1 for a,b in zip(prices,prices[1:])]
        if recent:
            returns = returns[-36:]
        mean = sum(returns)/len(returns)
        sd = math.sqrt(sum((r-mean)**2 for r in returns)/(len(returns)-1))
        sleeve = estimates['sleeves'][0]
        assert math.isclose(sleeve['return'],mean*12,abs_tol=1e-12)
        assert math.isclose(sleeve['volatility'],sd*math.sqrt(12),abs_tol=1e-12)
        assert estimates['correlations'] == [[1.0]]
        assert not sleeve['reserve_eligible']
        mix = p.search_portfolios(estimates['sleeves'],estimates['correlations'],OBJECTIVE,RESERVE_MINIMUM)
        assert mix is None, 'QQQ alone must fail the BIL reserve requirement'
        # Direct 100% exposure is diagnostic only, not a relaxed-mandate allocation.
        covariance = p.build_covariance_matrix([sleeve['volatility']],[[1.0]])
        risk = p.portfolio_volatility([1.0],covariance)
        expected = p.portfolio_return([1.0],[sleeve['return']])
        reserve = p.reserve_eligible_weight([1.0],estimates['sleeves'])
        assert math.isclose(risk,sleeve['volatility'],abs_tol=1e-12) and reserve == 0
        result['runs'][name] = {'estimates':estimates,'mix':mix,
            'diagnostic_100_percent_QQQ':{'return':expected,'volatility':risk,'reserve':reserve},
            'checks':'PASS: independent mean/stdev; covariance identity; reserve infeasibility'}
        lines += [f'\n{name}: {len(returns)} monthly returns',
                  f'  Annual return estimate: {expected*100:.2f}%',
                  f'  Annual volatility estimate: {risk*100:.2f}%',
                  f'  Return threshold: {"pass" if expected >= OBJECTIVE else "FAIL"}',
                  f'  Reserve weight: {reserve*100:.2f}% -> FAIL (minimum {RESERVE_MINIMUM*100:.2f}%)',
                  '  no mix meets the objective: reserve rule makes QQQ-only infeasible.',
                  '  PASS: independent calculations and expected infeasibility.']
    lines += ['\nA one-fund test does not replace the required 3-6-fund universe.',
              'The six-fund prices and mandate have not been changed.']
    output = '\n'.join(lines)+'\n'
    print(output)
    (ROOT/'Lab_15_QQQ_test_output.txt').write_text(output,encoding='utf-8')
    (ROOT/'Lab_15_QQQ_test_results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')

if __name__ == '__main__':
    main()
