from datetime import datetime, timezone
from zoneinfo import ZoneInfo

def classify(local: str, zone: str) -> str:
    z = ZoneInfo(zone)
    naive = datetime.fromisoformat(local)
    dt0 = naive.replace(tzinfo=z, fold=0)
    dt1 = naive.replace(tzinfo=z, fold=1)
    # чи існує мить? прогнана крізь UTC і назад, у ЩІЛИНІ вона зсувається
    exists = naive == dt0.astimezone(timezone.utc).astimezone(z).replace(tzinfo=None)
    if not exists:
        return "щілина: миті немає (весняний перехід)"
    if dt0.utcoffset() != dt1.utcoffset():
        return "повтор: миті дві — fold=0 (+03) та fold=1 (+02)"
    return "звичайна: рівно одна мить"

print(classify("2026-03-29T03:30", "Europe/Kyiv"))  # щілина: миті немає
print(classify("2026-10-25T03:30", "Europe/Kyiv"))  # повтор: миті дві
print(classify("2026-07-01T07:00", "Europe/Kyiv"))  # звичайна: рівно одна мить
