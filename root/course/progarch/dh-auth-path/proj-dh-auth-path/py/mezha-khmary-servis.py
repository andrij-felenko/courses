# ── Межа хмари, бік сервісу: приймаємо ЗАСВІДЧЕННЯ, не клієнтський токен ──
def attested_subject(req) -> Subject:
    token = req.headers.get("x-dh-attestation")
    if not token:
        raise Http(401)                                  # напряму, без шлюзу → стоп (fail-closed)
    try:
        c = jwt.decode(token, GATEWAY_INTERNAL_PUBLIC_KEY,
                       algorithms=["RS256"],
                       issuer="edge-gateway",            # підписав саме шлюз
                       audience="devices")               # і саме НАМ
        return Subject(id=c["sub"], scopes=c.get("scopes", []))
    except Exception:
        raise Http(401)                                  # підроблене / протухле / чуже aud → ні
