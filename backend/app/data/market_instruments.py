MARKET_INSTRUMENTS = [
    # Commodities
    {"code": "GOLD", "name": "Gold", "category": "commodity", "unit": "USD"},
    {"code": "SILVER", "name": "Silver", "category": "commodity", "unit": "USD"},
    {"code": "PLATINUM", "name": "Platinum", "category": "commodity", "unit": "USD"},
    {"code": "COPPER", "name": "Copper", "category": "commodity", "unit": "USD"},
    {"code": "BRENT", "name": "Brent Crude Oil", "category": "commodity", "unit": "USD"},
    {"code": "WTI", "name": "WTI Crude Oil", "category": "commodity", "unit": "USD"},
    {"code": "NATGAS", "name": "Natural Gas", "category": "commodity", "unit": "USD"},

    # Currencies
    {"code": "DXY", "name": "US Dollar Index", "category": "currency", "unit": "index"},
    {"code": "EURUSD", "name": "EUR/USD", "category": "currency", "unit": "USD"},
    {"code": "USDJPY", "name": "USD/JPY", "category": "currency", "unit": "JPY"},
    {"code": "USDTRY", "name": "USD/TRY", "category": "currency", "unit": "TRY"},

    # Interest rates
    {"code": "US2Y", "name": "US 2-Year Treasury Yield", "category": "rate", "unit": "percent"},
    {"code": "US10Y", "name": "US 10-Year Treasury Yield", "category": "rate", "unit": "percent"},
    {"code": "US10Y_REAL", "name": "US 10-Year Real Yield", "category": "rate", "unit": "percent"},
    {"code": "FED_FUNDS", "name": "Federal Funds Rate", "category": "rate", "unit": "percent"},

    # Equity / volatility
    {"code": "SP500", "name": "S&P 500", "category": "equity", "unit": "index"},
    {"code": "NASDAQ100", "name": "Nasdaq 100", "category": "equity", "unit": "index"},
    {"code": "RUSSELL2000", "name": "Russell 2000", "category": "equity", "unit": "index"},
    {"code": "VIX", "name": "CBOE Volatility Index", "category": "risk", "unit": "index"},
    {"code": "BIST100", "name": "BIST 100", "category": "equity", "unit": "index"},

    # Crypto / sovereign risk / macro
    {"code": "BTCUSD", "name": "Bitcoin / USD", "category": "crypto", "unit": "USD"},
    {"code": "TURKEY_CDS_5Y", "name": "Türkiye 5-Year CDS", "category": "risk", "unit": "bps"},
    {
        "code": "US_10Y_BREAKEVEN",
        "name": "US 10-Year Breakeven Inflation Rate",
        "category": "macro",
        "unit": "percent",
    },
]