import click
import FinanceDataReader as fdr
import pandas as pd
import os
from .strategies import 매달_정액_매수, 정액매수_수익_매도, 정액매수_보유
from .plotting import plot_results

def get_stock_data(stock_code, start_date, end_date):
    stock_data = fdr.DataReader(stock_code, start_date, end_date)
    return stock_data

STRATEGIES = {
    '매달_정액_매수': 매달_정액_매수,
    '정액매수_수익_매도': 정액매수_수익_매도,
    '정액매수_보유': 정액매수_보유,
}
STRATEGY_NAMES = list(STRATEGIES.keys())

@click.command()
@click.option('--stock_code', '-s', default='133690', help='Stock code to analyze.')
@click.option('--start_date', '-start', default='2019-01-01', help='Start date for analysis (YYYY-MM-DD).')
@click.option('--end_date', '-end', default='2024-11-01', help='End date for analysis (YYYY-MM-DD).')
@click.option('--output', '-o', default='trading_strategy_results.csv', help='The output CSV file name.')
@click.option('--strategies', '-st', multiple=True, type=click.Choice(STRATEGY_NAMES),
              default=STRATEGY_NAMES, help='The trading strategies to use (can be specified multiple times).')
def main(stock_code, start_date, end_date, output, strategies):
    """
    주식 데이터를 가져와 선택한 거래 전략들을 시뮬레이션하고 결과를 CSV 파일로 저장합니다.
    """
    # 주가 데이터 가져오기
    data = get_stock_data(stock_code, start_date, end_date)
    INITIAL_CAPITAL = 10_000_000
    TAX_RATE = 0.15
    TRADE_COMMISSION = 0.015

    results = {}
    for strategy_name in strategies:
        strategy_func = STRATEGIES[strategy_name]
        if strategy_name == '매달_정액_매수':
            results[strategy_name] = strategy_func(data.copy(), INITIAL_CAPITAL, TAX_RATE, TRADE_COMMISSION, frequency='monthly')
        elif strategy_name == '정액매수_수익_매도':
            results[strategy_name] = strategy_func(data.copy(), INITIAL_CAPITAL, TAX_RATE, TRADE_COMMISSION, frequency='monthly',
                                                  profit_threshold=0.1)
        elif strategy_name == '정액매수_보유':
            results[strategy_name] = strategy_func(data.copy(), INITIAL_CAPITAL, TAX_RATE, TRADE_COMMISSION, frequency='monthly')

    if not results:
        print("선택된 전략이 없습니다.")
        return

    # 결과를 하나의 DataFrame으로 합치기
    combined_results = pd.concat([results[name] for name in results], axis=1, keys=list(results.keys()))

    # 각 전략별 최종 성과 비교
    comparison = pd.DataFrame({
        name: {
            '최종 자산': results[name]['total_value'].iloc[-1],
            '수익률': (results[name]['total_value'].iloc[-1] - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
        }
        for name in results
    })

    print("\n=== 전략별 성과 비교 ===")
    print(comparison.round(2))
    print("\n")
    # 결과를 CSV 파일로 저장
    combined_results.to_csv(output, encoding='utf-8', index=False)
    print(f"선택된 전략 결과가 '{output}' 파일로 저장되었습니다.")

    # 시각화
    plot_results(data, results, output, stock_code, start_date, end_date)

if __name__ == "__main__":
    main()