# main.py ── ОДНА збірка на всі середовища. Вибір адаптера — тут, і тільки тут.
import os
from uuid import uuid4
from order.service import ЗамовленняСервіс
from order.core import ЗамовленняСховище
from adapters.pg import PgСховище
from adapters.memory import ПамятьСховище
from adapters.http import ЗамовленняHttp


# ↓ ЄДИНА розвилка на весь застосунок
async def зібрати_сховище() -> ЗамовленняСховище:
    if os.environ.get("STORE") == "memory":
        return ПамятьСховище()
    return PgСховище(await create_pool(os.environ["DATABASE_URL"]))


сервіс = ЗамовленняСервіс(await зібрати_сховище(), lambda: str(uuid4()))
http = ЗамовленняHttp(сервіс)
app.add_route("/orders", http.post, methods=["POST"])
# STORE=memory python main.py  → пам'ять
# (без STORE)                  → Postgres
