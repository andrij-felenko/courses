async def intercept(rules: list[RouteRule], req) -> "Response":
    path = req.path
    rule = next((r for r in rules if r.pattern.search(path)), None)
    if rule is None:
        return await call_legacy(req)

    is_write = req.method in ("PUT", "POST", "PATCH", "DELETE")

    if is_write:
        # запис іде туди, де ЗАРАЗ власник даних; друга база наздоганяє outbox'ом
        # (напрям власності задає той самий rule.target — теж оборотний конфігом)
        if rule.target == "service":
            return await call_service(rule.service_url, req)   # власник — сервіс
        return await call_legacy(req)                          # власник — моноліт

    # читання: стабільний canary + тіньова звірка
    if goes_to_service(rule, user_key_of(path)):
        return await call_service(rule.service_url, req)   # цей клієнт на новому
    return await read_with_shadow(rule, req)               # старе клієнту, нове тінню
