import re

# Виклики в старе й нове — заглушки під реальний HTTP-клієнт вашого шлюзу.
#   call_legacy(req) -> Response            — старий моноліт
#   call_service(base, req) -> Response     — новий сервіс

def user_key_of(path: str) -> str:
    """Стабільний ключ клієнта: id користувача зі шляху /api/users/:id.
    У житті це частіше id із токена автентифікації, а не з URL."""
    m = re.search(r"/api/users/([^/]+)", path)
    return m.group(1) if m else "anon"


async def intercept(rules: list[RouteRule], req) -> "Response":
    path = req.path
    rule = next((r for r in rules if r.pattern.search(path)), None)
    if rule is None:
        return await call_legacy(req)        # ніхто цей шлях не переносив

    key = user_key_of(path)

    if goes_to_service(rule, key):
        # основний потік цього клієнта — у новий сервіс
        return await call_service(rule.service_url, req)
    # основний потік — у старе (тут згодом стане тіньова звірка для читань)
    return await call_legacy(req)
