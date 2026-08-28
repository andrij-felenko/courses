import urllib.parse
from dataclasses import dataclass
from typing import Optional

@dataclass
class ParsedUrlPy:
    scheme: str
    userinfo: Optional[str]
    host: str
    port: Optional[int]
    path: str
    query: str
    fragment: str

def parse_url_rfc3986(url_str: str) -> ParsedUrlPy:
    """Розбір URL за допомогою urllib.parse.urlsplit з виділенням компонентів."""
    res = urllib.parse.urlsplit(url_str)
    
    userinfo = None
    if res.username:
        userinfo = res.username
        if res.password:
            userinfo += f":{res.password}"
            
    return ParsedUrlPy(
        scheme=res.scheme,
        userinfo=userinfo,
        host=res.hostname or "",
        port=res.port,
        path=res.path,
        query=res.query,
        fragment=res.fragment
    )
