import matplotlib.pyplot as plt

# 데이터 설정
years = [2019, 2020, 2021, 2022, 2023, 2024]
gdp_growth_rates = [2.2, -0.7, 4.1, 2.6, 1.4, 2.5]  # 예측 포함

# 색상 설정
colors = ['blue', 'orange', 'green', 'red', 'purple', 'cyan']

# 그래프 그리기
plt.figure(figsize=(10, 6))
plt.plot(years, gdp_growth_rates, marker='o', color='black')

# 각 년도별 성장률 수치 표시
for i in range(len(years)):
    plt.text(years[i], gdp_growth_rates[i], f"{gdp_growth_rates[i]}%", 
             ha='center', va='bottom', color=colors[i])

# 그래프 제목 및 축 레이블 설정
plt.title('Recent GDP Growth Rates and 2024 Forecast')
plt.xlabel('Year')
plt.ylabel('GDP Growth Rate (%)')
plt.xticks(years)  # x축에 년도 표시
plt.grid(True)

# 색상으로 각 년도 구분
for i in range(len(years)):
    plt.plot(years[i:i+2], gdp_growth_rates[i:i+2], color=colors[i])

# 그래프 출력
plt.axhline(0, color='black',linewidth=0.5, ls='--')  # x축 추가
plt.show()