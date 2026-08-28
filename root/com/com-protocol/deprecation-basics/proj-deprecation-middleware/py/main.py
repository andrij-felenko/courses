from datetime import datetime, timezone
from email.utils import format_datetime
from fastapi import Request, Response, Depends
from prometheus_client import Counter

# Один лічильник; різні маршрути — різні значення мітки route.
depr_calls = Counter(
    "deprecated_route_calls_total",
    "Виклики застарілих маршрутів за клієнтом",
    ["route", "client"],
)

KNOWN_CLIENTS: dict[str, str] = {      # ключ API -> людська назва клієнта
    "ak_live_9f3…": "acme-mobile",
    "ak_live_2b7…": "partner-erp",
}

def deprecated(route: str, announced: str, sunset: str, docs: str):
    announced_at = datetime.fromisoformat(announced).replace(tzinfo=timezone.utc)
    sunset_at = datetime.fromisoformat(f"{sunset}T23:59:59").replace(tzinfo=timezone.utc)

    # Контракт — до старту: зняття не раніше за оголошення.
    if sunset_at <= announced_at:
        raise ValueError(
            f"deprecated({route}): sunset {sunset} не пізніше за announced {announced}")

    # Форматуємо один раз. Deprecation — секунди Unix із '@' (RFC 9745);
    # Sunset — HTTP-date. format_datetime(usegmt=True) завжди дає англійський
    # "…GMT" незалежно від локалі сервера — на відміну від strftime.
    depr_value = f"@{int(announced_at.timestamp())}"
    sunset_value = format_datetime(sunset_at, usegmt=True)  # "Wed, 31 Dec 2025 23:59:59 GMT"
    link_value = f'<{docs}>; rel="deprecation"; type="text/html"'

    def stamp(request: Request, response: Response):
        response.headers["Deprecation"] = depr_value
        response.headers["Sunset"] = sunset_value
        response.headers["Link"] = link_value
        client = KNOWN_CLIENTS.get(request.headers.get("x-api-key", ""), "unknown")
        depr_calls.labels(route=route, client=client).inc()

    return stamp

# залежність вішається на ОДИН маршрут:
@app.get(
    "/v1/orders",
    dependencies=[Depends(deprecated("orders.v1", "2024-06-30", "2025-12-31", DOCS))],
)
def list_orders_v1():
    ...
