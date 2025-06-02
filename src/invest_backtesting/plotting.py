import matplotlib.pyplot as plt
import os
import pandas as pd
import platform

def plot_results(data: pd.DataFrame, results: dict, output_filename: str, stock_code: str, start_date: str, end_date: str):
    """
    주가 데이터와 전략 결과를 이용하여 시각화하고 저장합니다.

    Args:
        data (pd.DataFrame): 주가 데이터.
        results (dict): 전략 실행 결과 (각 전략 이름이 키).
        output_filename (str): CSV 출력 파일 이름.
        stock_code (str): 주식 종목 코드.
        start_date (str): 분석 시작 날짜.
        end_date (str): 분석 종료 날짜.
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

    fig, axs = plt.subplots(2, 1, figsize=(14, 10))

    # 위쪽 서브플롯: 전체 주가 그래프
    axs[0].plot(data.index, data['Close'], color='gray', label='Stock Price', alpha=0.5)
    axs[0].set_ylabel('Stock Price')
    axs[0].set_title(f'{stock_code} 주가 ({start_date} ~ {end_date})')
    axs[0].legend()
    axs[0].grid()

    # 아래쪽 서브플롯: 전략별 최종 자산 그래프
    for name, result in results.items():
        axs[1].plot(result['date'], result['total_value'], label=f'{name}')
    axs[1].set_ylabel('Total Value')
    axs[1].set_xlabel('Date')
    axs[1].set_title('전략별 최종 자산 비교')
    axs[1].legend()
    axs[1].grid()

    plt.tight_layout()

    # 플롯을 CSV 파일과 같은 폴더에 저장
    plot_filename = os.path.splitext(output_filename)[0] + '_strategies.png'
    plt.savefig(plot_filename)
    print(f"플롯이 '{plot_filename}' 파일로 저장되었습니다.")
    # plt.show()