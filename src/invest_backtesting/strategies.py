import pandas as pd

def 매달_정액_매수(data, initial_capital, tax_rate, trade_commission, frequency='monthly'):
    """매달/매주 1주 매수."""
    capital = initial_capital
    shares = 0
    records = []
    last_trade_date = None
    for date, row in data.iterrows():
        price = row['Close']
        if frequency == 'monthly':
            if last_trade_date is None or date.month != last_trade_date.month:
                살까 = True
        elif frequency == 'weekly':
            if date.weekday() == 0:
                살까 = True
        else:
            살까 = False
        if 살까 and capital >= price * (1 + trade_commission):
            cost = price * (1 + trade_commission)
            capital -= cost
            shares += 1
            last_trade_date = date
        records.append({'date': date, 'remaining_capital': capital, 'shares_held': shares, 'total_value': capital + shares * price})
    return pd.DataFrame(records)

def 정액매수_수익_매도(data, initial_capital, tax_rate, trade_commission, frequency='monthly', profit_threshold=0.1):
    """매달/매주 정액 매수, 수익률 넘으면 매도."""
    capital = initial_capital
    shares = 0
    records = []
    투자금액 = 1_000_000
    매수기록 = []
    last_trade_date = None
    for date, row in data.iterrows():
        price = row['Close']
        if frequency == 'monthly':
            if last_trade_date is None or date.month != last_trade_date.month:
                매수조건 = True
        elif frequency == 'weekly':
            if date.weekday() == 0:
                매수조건 = True
        else:
            매수조건 = False
        if 매수조건 and capital >= 투자금액 * (1 + trade_commission):
            살수있는만큼 = int((투자금액 * (1 - trade_commission)) // price)
            if 살수있는만큼 > 0:
                매수금액 = price * 살수있는만큼 * (1 + trade_commission)
                capital -= 매수금액
                shares += 살수있는만큼
                매수기록.append((price, 살수있는만큼))
                last_trade_date = date
        새매수기록 = []
        for 매수가, 수량 in 매수기록:
            수익률 = (price - 매수가) / 매수가
            if 수익률 >= profit_threshold:
                매도금액 = price * 수량 * (1 - trade_commission - tax_rate)
                capital += 매도금액
                shares -= 수량
            else:
                새매수기록.append((매수가, 수량))
        매수기록 = 새매수기록
        records.append({'date': date, 'remaining_capital': capital, 'shares_held': shares, 'total_value': capital + shares * price, '보유종목수': len(매수기록)})
    return pd.DataFrame(records)

def 정액매수_보유(data, initial_capital, tax_rate, trade_commission, frequency='monthly'):
    """매달/매주 정액 매수 후 보유."""
    capital = initial_capital
    shares = 0
    records = []
    투자금액 = 1_000_000
    last_trade_date = None
    for date, row in data.iterrows():
        price = row['Close']
        if frequency == 'monthly':
            if last_trade_date is None or date.month != last_trade_date.month:
                매수조건 = True
        elif frequency == 'weekly':
            if date.weekday() == 0:
                매수조건 = True
        else:
            매수조건 = False
        if 매수조건 and capital >= 투자금액 * (1 + trade_commission):
            살수있는만큼 = int((투자금액 * (1 - trade_commission)) // price)
            if 살수있는만큼 > 0:
                매수금액 = price * 살수있는만큼 * (1 + trade_commission)
                capital -= 매수금액
                shares += 살수있는만큼
                last_trade_date = date
        records.append({'date': date, 'remaining_capital': capital, 'shares_held': shares, 'total_value': capital + shares * price})
    return pd.DataFrame(records)