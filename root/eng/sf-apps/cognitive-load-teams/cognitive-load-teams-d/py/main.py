# Стороннє глушить внутрішнє: логіку знижки видно ледве
def final_price(o):
    # ручне складання конфігу з трьох джерел просто щоб дізнатися ставку
    tier = os.environ.get("DISCOUNT_TIER") or read_file("/etc/app/tier.conf")
    if not tier:
        tier = query_db("SELECT tier FROM cfg LIMIT 1")
    rate = float(tier)                   # а раптом не число — впаде тут
    # ще й ручний перерахунок валюти вкраплено в ту саму функцію
    usd = o.amount * fetch_rate(o.ccy)   # мережевий виклик усередині ціни
    return usd - usd * rate              # ← а ось це і є вся суть
