# Намір розкладу — правило+зона, а не застиглий момент.
from zoneinfo import ZoneInfo          # база переведень IANA у stdlib
from datetime import datetime, timedelta, time, timezone

def yesterday_window(zone: str, now: datetime) -> tuple[datetime, datetime]:
    """Вікно «вчора» = від локальної півночі до локальної півночі, у UTC-інстантах.
    Дві сусідні локальні півночі самі дають 23/24/25 год — DST враховано за побудовою."""
    local = now.astimezone(ZoneInfo(zone))
    start_local = datetime.combine(local.date() - timedelta(days=1),
                                   time(0, 0), ZoneInfo(zone))
    end_local = datetime.combine(local.date(), time(0, 0), ZoneInfo(zone))
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)

async def aggregate_day(home_id: str, day: str, w: tuple) -> None:
    # Задача ідемпотентна за (дім, доба): другий запуск ПЕРЕПИШЕ, а не додасть.
    rows = await telemetry.read_between(home_id, w[0], w[1])   # виміри-інстанти
    summary = roll_up(rows)                                    # сума/макс/мін за добу
    await daily_summary.upsert({"home": home_id, "day": day}, summary)  # не append
