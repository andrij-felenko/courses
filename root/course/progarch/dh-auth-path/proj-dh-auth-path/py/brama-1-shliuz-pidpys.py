from dataclasses import dataclass

@dataclass
class Subject:                       # доведена особа + грубі скоупи з токена
    id: str
    scopes: list[str]

# ── Брама 1: шлюз на краю хмари ─────────────────────────────────────────────
def edge_gate(req) -> str:
    subject = verify_access_token(req.headers.get("authorization"))  # підпис ключем ЕМІТЕНТА, локально
    if subject is None:
        raise Http(401)                                              # печатка/термін не зійшлись

    if "device:command" not in subject.scopes:                      # об'єкто-НЕЗАЛЕЖне: роль узагалі командує?
        raise Http(403)                                             # гість (лише device:view) — стоп ТУТ

    return mint_attestation(subject)   # суб'єкт доведено → свіже засвідчення саме для сервісу пристроїв

def mint_attestation(subject: Subject) -> str:
    now = int(time.time())
    return jwt.encode(
        {"sub": subject.id, "scopes": subject.scopes,
         "iss": "edge-gateway", "aud": "devices",   # від кого й КОМУ
         "iat": now, "exp": now + 10},              # живе 10 с — на один стрибок
        GATEWAY_INTERNAL_PRIVATE_KEY,               # НЕ ключ клієнтських токенів!
        algorithm="RS256",
    )

async def forward_to_devices(req, attestation: str):
    headers = {"x-dh-attestation": attestation}     # свіже, підписане шлюзом
    # Authorization (клієнтський токен) НЕ переслали.
    return await http.request(req.method, f"http://devices.internal{req.path}",
                              headers=headers, content=req.raw_body)
