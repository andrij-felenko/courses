# main.py ── КОРІНЬ ЗБІРКИ. ЄДИНЕ місце, де сходяться "Postgres" і "SMTP".
import os
from uuid import uuid4
from domain.place_order import PlaceOrder
from infra.pg_orders import PgOrders
from infra.smtp_notifier import SmtpNotifier


async def build_place_order() -> PlaceOrder:
    db = await create_pool(os.environ["DATABASE_URL"])
    smtp = await connect_smtp(os.environ["SMTP_URL"])
    # обидва адаптери сходяться ТУТ і подаються сценарію ззовні
    return PlaceOrder(
        PgOrders(db),                          # порт Orders   ← Postgres
        SmtpNotifier(smtp, "shop@acme.io"),    # порт Notifier ← SMTP
        lambda: str(uuid4()),
    )
    # далі place_order.run(...) не знає ні слова "Postgres", ні слова "SMTP"
