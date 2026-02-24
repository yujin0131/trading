from datetime import datetime, timedelta
from pykrx import stock
import pandas as pd

# https://github.com/sharebook-kr/pykrx/blob/master/pykrx/stock/stock_api.py
def get_stock_data(ticker, days=365):
    end = datetime.now().strftime("%Y%m%d")
    start = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")

    try:
        df = stock.get_market_ohlcv(start, end, ticker)
        return df
    except:
        return None

def get_top_stocks(top_n=30):
    # 네이버 시가총액 상위 (2025.02.24 기준)
    stocks = {
        "005930": "삼성전자",
        "000660": "SK하이닉스",
        "005380": "현대차",
        "373220": "LG에너지솔루션",
        "207940": "삼성바이오로직스",
        "000270": "기아",
        "105560": "KB금융",
        "068270": "셀트리온",
        "028260": "삼성물산",
        "055550": "신한지주",
        "032830": "삼성생명",
        "012330": "현대모비스",
        "035420": "NAVER",
        "086790": "하나금융지주",
        "006400": "삼성SDI",
        "005490": "POSCO홀딩스",
        "009150": "삼성전기",
        "034730": "SK",
        "035720": "카카오",
        "000810": "삼성화재",
        "051910": "LG화학",
        "096770": "SK이노베이션",
        "066570": "LG전자",
        "003670": "포스코퓨처엠",
        "017670": "SK텔레콤",
        "036570": "엔씨소프트",
        "003550": "LG",
        "015760": "한국전력",
        "323410": "카카오뱅크",
        "352820": "하이브",
    }

    data = []
    for ticker, name in stocks.items():
        df = get_stock_data(ticker, days=7)
        if df is None or df.empty:
            continue

        latest = df.iloc[-1]
        data.append({
            '종목코드': ticker,
            '종목명': name,
            '종가': int(latest['종가']),
            '거래량': int(latest['거래량']),
            '거래대금': int(latest['종가'] * latest['거래량'])
        })

    result = pd.DataFrame(data)
    result = result.sort_values('거래대금', ascending=False)
    return result.head(top_n)

# 변동성 - 최근 30일 평균
def calc_volatility(ticker, days=30):
    df = get_stock_data(ticker, days=days*2)
    if df is None or len(df) < days:
        return 999

    # 일별 -> (고가-저가) / 종가 * 100
    df['변동폭'] = ((df['고가'] - df['저가']) / df['종가'] * 100).abs()
    return round(df['변동폭'].tail(days).mean(), 2)

# 종목 필터링
def filter_stocks(max_volatility=10):
    df = get_top_stocks()
    print(f'총 {len(df)}개')

    vols = []
    for ticker in df['종목코드']:
        vol = calc_volatility(ticker)
        vols.append(vol)

    df['변동성'] = vols
    df = df[df['변동성'] <= max_volatility]

    print(f'{max_volatility}% 이하: {len(df)}개')
    return df


if __name__ == "__main__":
    result = filter_stocks(max_volatility=10)

    if result is not None and not result.empty:
        print(f'최종: {len(result)}개')
        print(result.head(20))

        filename = "./data/stocks.xlsx"
        sheet_name = datetime.now().strftime('%Y.%m.%d')

        try:
            with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                result.to_excel(writer, sheet_name=sheet_name, index=False)
        except FileNotFoundError:
            result.to_excel(filename, sheet_name=sheet_name, index=False)
    else:
        print('종목 없음')
