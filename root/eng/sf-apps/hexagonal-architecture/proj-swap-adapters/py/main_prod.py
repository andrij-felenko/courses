# main_prod.py ── ТОЧКА ЗБІРКИ (прод). ЄДИНЕ місце, де звучить слово "Postgres".
import os
from uuid import uuid4
from order.service import ЗамовленняСервіс
from adapters.pg import PgСховище
from adapters.http import ЗамовленняHttp

db = await create_pool(os.environ["DATABASE_URL"])

сервіс = ЗамовленняСервіс(PgСховище(db), lambda: str(uuid4()))   # ← база сюди
http = ЗамовленняHttp(сервіс)                                    # ← ядро сюди

app.add_route("/orders", http.post, methods=["POST"])
