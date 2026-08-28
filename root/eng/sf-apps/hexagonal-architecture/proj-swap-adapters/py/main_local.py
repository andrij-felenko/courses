# main_local.py ── ТОЧКА ЗБІРКИ (локально). Слова "Postgres" тут НЕМА зовсім.
from uuid import uuid4
from order.service import ЗамовленняСервіс
from adapters.memory import ПамятьСховище        # ← єдиний інший імпорт
from adapters.http import ЗамовленняHttp

сервіс = ЗамовленняСервіс(ПамятьСховище(), lambda: str(uuid4()))   # ← пам'ять сюди
http = ЗамовленняHttp(сервіс)

app.add_route("/orders", http.post, methods=["POST"])
