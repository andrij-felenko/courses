def create_logout_url(
    end_session_endpoint: str,
    id_token_hint: str,
    post_logout_redirect_uri: str,
    state: str | None = None
) -> str:
    params = {
        "id_token_hint": id_token_hint,
        "post_logout_redirect_uri": post_logout_redirect_uri,
    }
    if state:
        params["state"] = state
    return f"{end_session_endpoint}?{urllib.parse.urlencode(params)}"
