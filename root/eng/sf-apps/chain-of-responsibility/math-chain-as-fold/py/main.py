from functools import reduce
from typing import Callable

Handler = Callable[[Request], Response]
Link = Callable[[Handler], Handler]
Middleware = Callable[[Request, Handler], Response]

def flip(mw: Middleware) -> Link:
    return lambda nxt: lambda req: mw(req, nxt)

def build(links: list[Link], base: Handler) -> Handler:
    return reduce(lambda rest, link: link(rest), reversed(links), base)
