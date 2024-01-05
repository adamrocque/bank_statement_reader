import json
trans_types = {
  "Adam Car Payment": [],
  "Aevi": [],
  "Arya": [],
  "BTC": [],
  "Booze": [],
  "Car Fuel": [],
  "Car Maint": [],
  "Dine Out": [],
  "Electricity & Water": [],
  "Entertainment": ["THE MULE", "SQ *CROWSNEST B   _F"],
  "Gas": [],
  "Gifts": [],
  "Groceries": ["CAPTL ONE MC X5Y8X9 "],
  "Health Savings": [],
  "Honeymoon": [],
  "Hot Water Heater": [],
  "House": ["AMZN Mktp CA*TQ94B7941"],
  "Ignore": [
    "PAYMENT - THANK YOU",
    "MONTHLY ACCOUNT FEE ",
    "ACCT BAL REBATE     ",
    "WL511 TFR-TO C/C    "
  ],
  "Insurance (Car/House)": ["BELAIR INS/ASS.  INS"],
  "Internet": [],
  "Monthly Subscriptions": [],
  "Mortgage": [],
  "Personal Purchases": [],
  "Phone": [],
  "Property Tax": [],
  "RRSP Adam": ["EDWARD JONES AY#001 "],
  "RRSP Sarah": [],
  "Raj Savings": [],
  "Sarah Car Payment": [],
  "Savings": ["SSV TO:  05366534547", "PTS TO:  05366534547"],
  "Stocks": [],
  "Trips": [],
  "Wedding": ["KYM'S ALTERATIONS INC"]
}


for element in trans_types:
  trans_types[element] = {}

print(json.dumps(trans_types, indent = 4, sort_keys=True))