import click
import FinanceDataReader as fdr
import pandas as pd
import inspect
from . import strategies
from .plotting import plot_results

def get_stock_data(stock_codes: list[str], start_date: str, end_date: str) -> dict[str, pd.DataFrame]:
    """
    FinanceDataReader를 사용하여 여러 주식 데이터를 가져옵니다.

    Args:
        stock_codes: 분석할 주식 코드 리스트.
        start_date: 분석 시작 날짜 (YYYY-MM-DD).
        end_date: 분석 종료 날짜 (YYYY-MM-DD).

    Returns:
        각 주식 코드에 해당하는 주가 데이터 (DataFrame)를 담은 딕셔너리.
    """
    all_data = {}
    for code in stock_codes:
        all_data[code] = fdr.DataReader(code, start_date, end_date)
    return all_data

def get_strategies() -> dict[str, type[strategies.Strategy]]:
    """
    strategies 모듈에서 Strategy 클래스를 상속받는 모든 전략 클래스를 동적으로 찾아서 반환합니다.

    Returns:
        전략 이름(str)을 키로, 전략 클래스(type[strategies.Strategy])를 값으로 하는 딕셔너리.
    """
    strategy_classes = {}
    for name, cls in inspect.getmembers(strategies, inspect.isclass):
        if issubclass(cls, strategies.Strategy) and cls is not strategies.Strategy:
            strategy_classes[name] = cls
    return strategy_classes

def _run_optimization(
    stock_data: dict[str, pd.DataFrame],
    initial_capital: float,
    tax_rate: float,
    trade_commission: float
):
    """
    단일 종목에 대해 최적의 매매 전략을 계산하고 결과를 출력합니다.

    Args:
        stock_data: 최적화할 주식 데이터 (단일 종목).
        initial_capital: 초기 자본.
        tax_rate: 거래세율.
        trade_commission: 거래 수수료율.
    """
    target_code = list(stock_data.keys())[0]
    data = stock_data[target_code]

    print(f"\n=== {target_code} 최적 거래 내역 계산 ===")
    transactions, final_capital = strategies.calculate_optimal_strategy(data, initial_capital, tax_rate, trade_commission)
    
    if not transactions.empty:
        print(transactions.to_string())
        print(f"\n초기 자본: {initial_capital:,.0f}원")
        print(f"최종 자산: {final_capital:,.0f}원")
        profit = final_capital - initial_capital
        profit_rate = (profit / initial_capital) * 100
        print(f"총 수익: {profit:,.0f}원 ({profit_rate:.2f}%)")
        print(f"총 거래 횟수: {len(transactions)}회")
    else:
        print("거래 내역이 없습니다.")

def _run_backtesting(
    all_stock_data: dict[str, pd.DataFrame],
    selected_strategies: list[str],
    initial_capital: float,
    tax_rate: float,
    trade_commission: float,
    output_filename: str,
    start_date: str,
    end_date: str
):
    """
    여러 종목에 대해 선택된 거래 전략들을 시뮬레이션하고 결과를 저장 및 시각화합니다.

    Args:
        all_stock_data: 모든 주식 데이터.
        selected_strategies: 실행할 전략 이름 리스트.
        initial_capital: 초기 자본.
        tax_rate: 거래세율.
        trade_commission: 거래 수수료율.
        output_filename: 결과 CSV 파일 이름.
        start_date: 분석 시작 날짜.
        end_date: 분석 종료 날짜.
    """
    all_results = {}
    strategy_classes = get_strategies()

    for code, data in all_stock_data.items():
        results = {}
        for strategy_name in selected_strategies:
            strategy_class = strategy_classes[strategy_name]
            strategy_instance = strategy_class(
                data.copy(), initial_capital, tax_rate, trade_commission,
                frequency='monthly', profit_threshold=0.1, investment_amount=1_000_000
            )
            results[strategy_name] = strategy_instance.execute()
        all_results[code] = results

    _print_summary(all_results, initial_capital)

    # CSV 저장 (모든 결과를 하나의 파일에 저장)
    all_combined_results = {}
    for code, results in all_results.items():
        for strategy_name, result_df in results.items():
            all_combined_results[f'{code}_{strategy_name}'] = result_df
    
    final_df = pd.concat(all_combined_results.values(), axis=1, keys=all_combined_results.keys())
    final_df.to_csv(output_filename, encoding='utf-8', index=False)
    print(f"전체 결과가 '{output_filename}' 파일로 저장되었습니다.")

    # 시각화
    plot_results(all_stock_data, all_results, output_filename, start_date, end_date)

def _print_summary(all_results: dict, initial_capital: float):
    """
    백테스팅 결과를 요약하여 출력합니다.

    Args:
        all_results: 모든 종목의 전략 실행 결과.
        initial_capital: 초기 자본.
    """
    summary = pd.DataFrame()
    for code, results in all_results.items():
        for name, result in results.items():
            final_value = result['total_value'].iloc[-1]
            returns = (final_value - initial_capital) / initial_capital * 100
            summary = pd.concat([
                summary, 
                pd.DataFrame([{'Stock': code, 'Strategy': name, 'Final Asset': final_value, 'Return (%)': returns}])
            ], ignore_index=True)

    print("\n=== 백테스팅 결과 요약 ===")
    print(summary.round(2))
    print("\n")

@click.command()
@click.option('--stock_codes', '-s', multiple=True, default=['133690'], help='분석할 주식 코드 (여러 번 지정 가능)')
@click.option('--start_date', '-start', default='2019-01-01', help='분석 시작 날짜 (YYYY-MM-DD)')
@click.option('--end_date', '-end', default='2024-11-01', help='분석 종료 날짜 (YYYY-MM-DD)')
@click.option('--output', '-o', default='trading_strategy_results.csv', help='출력 CSV 파일 이름')
@click.option('--strategy', '-st', 'selected_strategies', multiple=True,
              type=click.Choice(list(get_strategies().keys())),
              default=list(get_strategies().keys()),
              help='사용할 거래 전략 (여러 번 지정 가능)')
@click.option('--optimize', is_flag=True, help='첫 번째 지정된 주식에 대해 최적의 거래 내역을 계산합니다.')
def main(stock_codes, start_date, end_date, output, selected_strategies, optimize):
    """
    주식 데이터를 가져와 선택한 거래 전략들을 시뮬레이션하고 결과를 CSV 파일과 플롯으로 저장합니다.
    --optimize 옵션을 사용하면, 첫 번째 주식에 대한 최적 거래 내역을 계산합니다.
    """
    all_stock_data = get_stock_data(stock_codes, start_date, end_date)
    INITIAL_CAPITAL = 10_000_000
    TAX_RATE = 0.15
    TRADE_COMMISSION = 0.015

    if optimize:
        if not stock_codes:
            print("최적화를 위해서는 주식 코드를 하나 이상 지정해야 합니다.")
            return
        # 최적화 모드에서는 현실적인 거래 비용을 적용
        _run_optimization(all_stock_data, INITIAL_CAPITAL, 0, 0.0015) # TAX_RATE 0, TRADE_COMMISSION 0.15%
    else:
        _run_backtesting(
            all_stock_data, selected_strategies, INITIAL_CAPITAL, TAX_RATE, TRADE_COMMISSION,
            output, start_date, end_date
        )

if __name__ == "__main__":
    main()
