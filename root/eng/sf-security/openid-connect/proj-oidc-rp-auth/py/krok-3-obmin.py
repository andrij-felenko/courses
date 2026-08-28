def exchange_code_for_tokens(
    token_endpoint: str,
    client_id: str,
    client_secret: str | None,
    code: str,
    code_verifier: str,
    redirect_uri: str
) -> dict:
    payload_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "code_verifier": code_verifier,
    }
    if client_secret:
        payload_data["client_secret"] = client_secret
        
    encoded_data = urllib.parse.urlencode(payload_data).encode('ascii')
    req = urllib.request.Request(
        token_endpoint,
        data=encoded_data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": "OIDC-RelyingParty-Engine/1.0"
        },
        method="POST"
    )
    
    with urllib.request.urlopen(req, timeout=10) as response:
        if response.status != 200:
            raise RuntimeError(f"Помилка обміну токенів: HTTP {response.status}")
        return json.loads(response.read().decode('utf-8'))
