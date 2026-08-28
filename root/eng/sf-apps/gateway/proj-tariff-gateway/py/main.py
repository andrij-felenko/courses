# main.py — точка збірки. Поза доменом. Тут абстракція стає конкретикою.
import os, asyncio
from http.http_tariff_gateway import HttpТарифШлюз
from domain.доставка_сервіс import ДоставкаСервіс
from domain.tariff import Напрямок

async def main():
    # ↓ ЄДИНЕ місце, що знає і про HTTP-шлюз, і про домен — і зшиває їх
    шлюз  = HttpТарифШлюз(os.environ["TARIFF_URL"], os.environ["TARIFF_TOKEN"])
    домен = ДоставкаСервіс(шлюз)   # домен дістав шлюз через інтерфейс
    print(await домен.порадити_спосіб(Напрямок("SEG_A")))

asyncio.run(main())
