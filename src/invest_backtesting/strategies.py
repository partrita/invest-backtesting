import pandas as pd
from abc import ABC, abstractmethod

class Strategy(ABC):
    """
    모든 투자 전략의 기본이 되는 추상 클래스입니다.
    모든 구체적인 전략은 이 클래스를 상속받아 `execute` 메서드를 구현해야 합니다.
    """
    def __init__(self, data: pd.DataFrame, initial_capital: float, tax_rate: float, trade_commission: float, **kwargs):
        self.data = data
        self.initial_capital = initial_capital
        self.tax_rate = tax_rate
        self.trade_commission = trade_commission
        self.kwargs = kwargs

    @abstractmethod
    def execute(self) -> pd.DataFrame:
        """
        전략을 실행하고 시간 경과에 따른 자산 변화를 담은 DataFrame을 반환합니다.
        반환되는 DataFrame은 'date', 'remaining_capital', 'shares_held', 'total_value' 컬럼을 포함해야 합니다.
        """
        pass

class BuyAndHold(Strategy):
    """
    백테스팅 시작일에 가능한 많은 주식을 매수하여 종료일까지 보유하는 전략입니다.
    """
    def execute(self) -> pd.DataFrame:
        capital = self.initial_capital
        shares = 0
        records = []
        
        # 첫 거래일에 매수
        first_day = self.data.iloc[0]
        price = first_day['Close']
        buyable_shares = int(capital // (price * (1 + self.trade_commission)))
        
        if buyable_shares > 0:
            cost = price * buyable_shares * (1 + self.trade_commission)
            capital -= cost
            shares += buyable_shares

        for date, row in self.data.iterrows():
            price = row['Close']
            records.append({'date': date, 'remaining_capital': capital, 'shares_held': shares, 'total_value': capital + shares * price})
        return pd.DataFrame(records)

class MonthlyDCA(Strategy):
    """
    매달 1주씩 매수하는 전략입니다.
    """
    def execute(self) -> pd.DataFrame:
        capital = self.initial_capital
        shares = 0
        records = []
        last_trade_date = None
        frequency = self.kwargs.get('frequency', 'monthly')

        for date, row in self.data.iterrows():
            price = row['Close']
            should_buy = False
            if frequency == 'monthly':
                if last_trade_date is None or date.month != last_trade_date.month:
                    should_buy = True
            elif frequency == 'weekly':
                if date.weekday() == 0:
                    should_buy = True

            if should_buy and capital >= price * (1 + self.trade_commission):
                cost = price * (1 + self.trade_commission)
                capital -= cost
                shares += 1
                last_trade_date = date
            records.append({'date': date, 'remaining_capital': capital, 'shares_held': shares, 'total_value': capital + shares * price})
        return pd.DataFrame(records)

class DCASellOnProfit(Strategy):
    """
    매달 정액 매수 후, 특정 수익률에 도달하면 매도하는 전략입니다.
    """
    def execute(self) -> pd.DataFrame:
        capital = self.initial_capital
        shares = 0
        records = []
        investment_amount = self.kwargs.get('investment_amount', 1_000_000)
        profit_threshold = self.kwargs.get('profit_threshold', 0.1)
        frequency = self.kwargs.get('frequency', 'monthly')
        purchase_history = []
        last_trade_date = None

        for date, row in self.data.iterrows():
            price = row['Close']
            should_buy = False
            if frequency == 'monthly':
                if last_trade_date is None or date.month != last_trade_date.month:
                    should_buy = True
            elif frequency == 'weekly':
                if date.weekday() == 0:
                    should_buy = True

            if should_buy and capital >= investment_amount * (1 + self.trade_commission):
                buyable_shares = int((investment_amount * (1 - self.trade_commission)) // price)
                if buyable_shares > 0:
                    purchase_cost = price * buyable_shares * (1 + self.trade_commission)
                    capital -= purchase_cost
                    shares += buyable_shares
                    purchase_history.append((price, buyable_shares))
                    last_trade_date = date

            new_purchase_history = []
            for purchase_price, num_shares in purchase_history:
                profit_margin = (price - purchase_price) / purchase_price
                if profit_margin >= profit_threshold:
                    sell_proceeds = price * num_shares * (1 - self.trade_commission - self.tax_rate)
                    capital += sell_proceeds
                    shares -= num_shares
                else:
                    new_purchase_history.append((purchase_price, num_shares))
            purchase_history = new_purchase_history
            records.append({'date': date, 'remaining_capital': capital, 'shares_held': shares, 'total_value': capital + shares * price, 'holding_count': len(purchase_history)})
        return pd.DataFrame(records)

class DCAAndHold(Strategy):
    """
    매달 정액 매수 후 보유하는 전략입니다.
    """
    def execute(self) -> pd.DataFrame:
        capital = self.initial_capital
        shares = 0
        records = []
        investment_amount = self.kwargs.get('investment_amount', 1_000_000)
        frequency = self.kwargs.get('frequency', 'monthly')
        last_trade_date = None

        for date, row in self.data.iterrows():
            price = row['Close']
            should_buy = False
            if frequency == 'monthly':
                if last_trade_date is None or date.month != last_trade_date.month:
                    should_buy = True
            elif frequency == 'weekly':
                if date.weekday() == 0:
                    should_buy = True

            if should_buy and capital >= investment_amount * (1 + self.trade_commission):
                buyable_shares = int((investment_amount * (1 - self.trade_commission)) // price)
                if buyable_shares > 0:
                    purchase_cost = price * buyable_shares * (1 + self.trade_commission)
                    capital -= purchase_cost
                    shares += buyable_shares
                    last_trade_date = date
            records.append({'date': date, 'remaining_capital': capital, 'shares_held': shares, 'total_value': capital + shares * price})
        return pd.DataFrame(records)

def calculate_optimal_strategy(data: pd.DataFrame, initial_capital: float, tax_rate: float, trade_commission: float) -> tuple[pd.DataFrame, float]:
    """
    주어진 주식 데이터에 대해 최적의 매매 전략을 찾아냅니다. (완벽한 사후 분석)
    이 함수는 주가의 저점(valley)에서 매수하고 고점(peak)에서 매도하여 수익을 극대화하는 시나리오를 시뮬레이션합니다.

    Args:
        data: 주식 데이터 (DataFrame).
        initial_capital: 초기 자본.
        tax_rate: 거래세율 (매도 시 적용).
        trade_commission: 거래 수수료율 (매수/매도 시 적용).

    Returns:
        거래 내역을 담은 DataFrame과 최종 자산.
    """
    prices = data['Close'].tolist()
    dates = data.index.tolist()
    n = len(prices)
    if n < 2:
        return pd.DataFrame(), initial_capital

    capital = float(initial_capital)
    transactions = []
    i = 0 # 현재 날짜 인덱스

    while i < n: # 모든 날짜를 순회
        # 다음 저점(잠재적 매수 시점) 찾기
        # 주가가 다음 날보다 크거나 같은 첫 번째 날을 찾습니다. 이는 상승 추세의 시작 또는 지역 최저점을 찾습니다.
        buy_start_index = i
        while buy_start_index < n - 1 and prices[buy_start_index] >= prices[buy_start_index + 1]:
            buy_start_index += 1

        # 끝에 도달했거나 상승 추세가 없으면 더 이상 매수할 수 없습니다.
        if buy_start_index == n - 1:
            break

        buy_index = buy_start_index
        buy_price = prices[buy_index]

        # 다음 고점(잠재적 매도 시점) 찾기
        # buy_index 다음 날부터 주가가 다음 날보다 작거나 같은 마지막 날을 찾습니다. 이는 상승 추세의 끝 또는 지역 최고점을 찾습니다.
        sell_start_index = buy_index + 1 # 매수 시점 다음 날부터 고점 찾기 시작
        while sell_start_index < n - 1 and prices[sell_start_index] <= prices[sell_start_index + 1]:
            sell_start_index += 1

        sell_index = sell_start_index
        sell_price = prices[sell_index]

        # 매수와 매도가 같은 날이거나, 매도 가격이 매수 가격보다 높지 않으면 이 사이클을 건너뜁니다.
        # (거래 수수료 및 세금 고려)
        if sell_index <= buy_index or (sell_price * (1 - trade_commission - tax_rate)) <= (buy_price * (1 + trade_commission)):
            i = sell_index + 1 # 현재 잠재적 매도 시점 다음 날로 이동
            continue

        # 수익성 있는 거래 발견
        buyable_shares = int(capital / (buy_price * (1 + trade_commission)))

        if buyable_shares > 0:
            # --- 매수 거래 ---
            cost = buy_price * buyable_shares * (1 + trade_commission)
            capital -= cost
            
            transactions.append({
                'Date': dates[buy_index],
                'Action': 'BUY',
                'Price': buy_price,
                'Shares': buyable_shares,
                'Capital': capital, # 매수 후 남은 현금
                'Total Value': capital + buyable_shares * buy_price # 매수 후 총 자산 가치
            })

            # --- 매도 거래 ---
            sell_proceeds = buyable_shares * sell_price * (1 - trade_commission - tax_rate)
            capital += sell_proceeds
            
            transactions.append({
                'Date': dates[sell_index],
                'Action': 'SELL',
                'Price': sell_price,
                'Shares': buyable_shares,
                'Capital': capital, # 매도 후 현금 (모두 현금화)
                'Total Value': capital # 매도 후 총 자산 가치 (모두 현금화)
            })
        
        i = sell_index + 1 # 다음 사이클을 위해 매도 거래 다음 날로 이동

    final_capital = capital
    if not transactions:
        return pd.DataFrame(), initial_capital

    return pd.DataFrame(transactions), final_capital
