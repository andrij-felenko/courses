from datetime import datetime
from zoneinfo import ZoneInfo   # стандартна бібліотека, читає живий tzdata IANA

# зберігаємо НАМІР: локальний час + назву зони
schedule = {"local": "2026-03-30T07:00", "zone": "Europe/Kyiv"}

# у мить спрацювання РОЗВ'ЯЗУЄМО намір за ЧИННИМИ правилами
local = datetime.fromisoformat(schedule["local"])
instant = local.replace(tzinfo=ZoneInfo(schedule["zone"]))
fire_at_utc = instant.astimezone(ZoneInfo("UTC"))   # 07:00 у Києві → точка на осі
