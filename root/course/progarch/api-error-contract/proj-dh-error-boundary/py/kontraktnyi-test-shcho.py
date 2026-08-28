import json, pytest

FIXED = "req-TEST"

SAMPLES = {
    "device_not_found":   lambda: DeviceNotFound("42"),
    "device_unavailable": lambda: DeviceUnavailable("42"),
    "invalid_command":    lambda: InvalidCommand("mode", "невідоме значення"),
    "rate_limited":       lambda: RateLimited(30),
}

# (а) інваріанти — над УСІМА класами каталогу
@pytest.mark.parametrize("row", list(CATALOG.values()), ids=lambda r: r.code)
def test_envelope_invariants(row):
    make = SAMPLES.get(row.code)
    assert make, f"нема зразка для {row.code} — додай його"
    status, headers, body = to_problem(make(), FIXED)
    assert status == row.status
    assert body["status"] == row.status            # статус у тілі === HTTP-статус
    assert body["code"] == row.code                # стабільний ярлик присутній
    assert body["requestId"] == FIXED              # кореляційний id відлунено
    assert isinstance(body["detail"], str)         # текст Є; його ЗМІСТ не пришпилюємо
    assert headers["Content-Type"] == "application/problem+json"
    if row.retryable:
        assert "Retry-After" in headers

# (б) golden-знімок точної форми (syrupy: assert == snapshot)
@pytest.mark.parametrize("code", list(SAMPLES), ids=list(SAMPLES))
def test_shape_pinned(code, snapshot):
    status, headers, body = to_problem(SAMPLES[code](), FIXED)
    assert {"status": status, "headers": headers, "body": body} == snapshot

# (в) редакція
def test_opaque_500_redacts():
    boom = RuntimeError("SQL: SELECT password FROM users WHERE id=1")
    status, headers, body = to_problem(boom, FIXED, expose_internals=False)
    assert status == 500
    assert body["code"] == "internal"
    assert body["requestId"] == FIXED
    assert "debug" not in body                     # у проді жодного стека
    wire = json.dumps({"h": headers, "b": body})
    for leak in ("SQL", "password", "SELECT"):
        assert leak not in wire
