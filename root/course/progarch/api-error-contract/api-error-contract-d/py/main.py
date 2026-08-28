# доменні помилки — ті самі, що підіймалися крізь шари; тут вони впираються в межу HTTP
class DeviceNotFound(Exception):
    def __init__(self, id): self.id = id
class DeviceUnavailable(Exception):
    def __init__(self, id): self.id = id

def to_problem(err, req_id):                        # одне місце перекладу
    if isinstance(err, DeviceNotFound):
        return 404, {}, {
            "type": "https://api.dh.io/errors/device-not-found",
            "title": "Пристрій не знайдено", "status": 404,
            "code": "device_not_found", "detail": f"Пристрою {err.id} немає.",
            "requestId": req_id}

    if isinstance(err, DeviceUnavailable):
        return 503, {"Retry-After": "5"}, {
            "type": "https://api.dh.io/errors/device-unavailable",
            "title": "Пристрій тимчасово недоступний", "status": 503,
            "code": "device_unavailable", "retryable": True,
            "detail": "Давач не відповідає, спробуйте за кілька секунд.",
            "requestId": req_id}

    # усе інше — це БАГ, а не факт світу: назовні нічого, у журнал — усе
    log.error("unhandled", extra={"req_id": req_id}, exc_info=err)  # лог РАЗ, тут
    return 500, {}, {
        "type": "about:blank", "title": "Внутрішня помилка", "status": 500,
        "code": "internal", "detail": "Сталася непередбачена помилка.",
        "requestId": req_id}                        # жодного трейсбека назовні
