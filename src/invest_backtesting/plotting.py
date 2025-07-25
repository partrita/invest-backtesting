import matplotlib.pyplot as plt
import os
import pandas as pd
import platform

def plot_results(all_stock_data: dict[str, pd.DataFrame], all_results: dict[str, dict[str, pd.DataFrame]], output_filename: str, start_date: str, end_date: str):
    """
    여러 종목의 주가 데이터와 전략 결과를 받아 시각화하고 저장합니다.

    Args:
        all_stock_data: 키는 주식 종목 코드, 값은 주가 데이터 (pd.DataFrame).
        all_results: 키는 주식 종목 코드, 값은 해당 종목의 전략 실행 결과 dict.
        output_filename: CSV 출력 파일 이름.
        start_date: 분석 시작 날짜.
        end_date: 분석 종료 날짜.
    """
    system_name = platform.system()
    if system_name == 'Darwin':  # macOS
        plt.rcParams['font.family'] = 'AppleGothic'
    elif system_name == 'Windows':
        plt.rcParams['font.family'] = 'Malgun Gothic'
    elif system_name == 'Linux':
        try:
            import matplotlib.font_manager as fm
            nanum_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'  # Nanum Gothic 기본 경로
            if os.path.exists(nanum_path):
                plt.rcParams['font.family'] = 'NanumGothic'
            else:
                print("Warning: NanumGothic font not found. Using default font.")
        except ImportError:
            print("Warning: matplotlib.font_manager could not be imported.")
    else:
        print(f"Warning: Unknown operating system '{system_name}'. Using default font.")

    plt.rcParams['axes.unicode_minus'] = False

    num_stocks = len(all_stock_data)
    fig, axs = plt.subplots(num_stocks, 2, figsize=(16, 6 * num_stocks), squeeze=False)

    fig.suptitle(f'Backtesting Results ({start_date} ~ {end_date})', fontsize=16, y=1.02)

    for i, (stock_code, data) in enumerate(all_stock_data.items()):
        results = all_results[stock_code]

        # 왼쪽 서브플롯: 주가 그래프
        ax_price = axs[i, 0]
        ax_price.plot(data.index, data['Close'], color='gray', label='Stock Price', alpha=0.7)
        ax_price.set_ylabel('Stock Price')
        ax_price.set_title(f'{stock_code} Price')
        ax_price.legend()
        ax_price.grid(True)

        # 오른쪽 서브플롯: 전략별 최종 자산 그래프
        ax_value = axs[i, 1]
        for name, result in results.items():
            ax_value.plot(result['date'], result['total_value'], label=f'{name}')
        ax_value.set_ylabel('Total Value')
        ax_value.set_xlabel('Date')
        ax_value.set_title(f'{stock_code} Strategy Performance')
        ax_value.legend()
        ax_value.grid(True)

    plt.tight_layout(rect=[0, 0, 1, 0.98])

    # 플롯을 CSV 파일과 같은 폴더에 저장
    plot_filename = os.path.splitext(output_filename)[0] + '_strategies.png'
    plt.savefig(plot_filename)
    print(f"플롯이 '{plot_filename}' 파일로 저장되었습니다.")