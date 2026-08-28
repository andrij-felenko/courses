BASE = "https://api.dh.io/errors"
CT = "application/problem+json"

def _detail(err: DomainError) -> str:
    # АВТОРСЬКИЙ текст, ніколи не str(err): сире повідомлення винесло б нутрощі назовні
    if isinstance(err, DeviceNotFound):    return f"Пристрою {err.id} немає або він не ваш."
    if isinstance(err, DeviceUnavailable): return "Давач не відповідає, спробуйте за кілька секунд."
    if isinstance(err, InvalidCommand):    return f"Поле «{err.field}»: {err.reason}."
    if isinstance(err, RateLimited):       return "Забагато запитів, зачекайте перед повтором."
    return "Помилка."

def to_problem(err, req_id, expose_internals=False):
    row = CATALOG.get(type(err))                          # точний тип; чужий підклас впаде в default

    if row is not None and isinstance(err, DomainError):
        headers = {"Content-Type": CT}
        body = {
            "type": f"{BASE}/{row.code.replace('_', '-')}",
            "title": row.title,
            "status": row.status,
            "code": row.code,
            "detail": _detail(err),
            "requestId": req_id,                          # той самий id, що в журналі
        }
        if row.retryable:
            body["retryable"] = True
            ra = err.retry_after_s if isinstance(err, RateLimited) else row.retry_after_s
            if ra is not None:
                headers["Retry-After"] = str(ra)
        if isinstance(err, InvalidCommand):
            body["field"] = err.field
        return row.status, headers, body

    # ── гілка «усе інше»: БАГ, не факт світу ──
    log.error("unhandled", extra={"req_id": req_id}, exc_info=err)   # лог РАЗ, тут, зі стеком
    body = {
        "type": "about:blank",                            # «нічого понад статус» (RFC 9457 §4.2.1)
        "title": "Внутрішня помилка",
        "status": 500,
        "code": "internal",
        "detail": "Сталася непередбачена помилка.",
        "requestId": req_id,
    }
    if expose_internals:
        import traceback
        body["debug"] = "".join(traceback.format_exception(err))     # ЛИШЕ dev
    return 500, {"Content-Type": CT}, body
