import urllib.parse

def encode_query_params(params: dict[str, str], form_mode: bool = False) -> str:
    """
    Кодує словник параметрів у query string.
    form_mode=True: пробіл стає '+', як у application/x-www-form-urlencoded.
    form_mode=False: пробіл стає '%20' за стандартом RFC 3986.
    """
    if form_mode:
        return urllib.parse.urlencode(params)
    return urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

def decode_query_param(val: str, form_mode: bool = False) -> str:
    """Розкодовує значення параметра запиту."""
    if form_mode:
        return urllib.parse.unquote_plus(val)
    return urllib.parse.unquote(val)
