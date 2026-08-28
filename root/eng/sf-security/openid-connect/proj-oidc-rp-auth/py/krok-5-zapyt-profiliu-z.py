def fetch_userinfo(userinfo_endpoint: str, access_token: str) -> dict:
    req = urllib.request.Request(
        userinfo_endpoint,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "User-Agent": "OIDC-RelyingParty-Engine/1.0"
        }
    )
    with urllib.request.urlopen(req, timeout=5) as response:
        if response.status != 200:
            raise RuntimeError(f"Помилка UserInfo: HTTP {response.status}")
        return json.loads(response.read().decode('utf-8'))
