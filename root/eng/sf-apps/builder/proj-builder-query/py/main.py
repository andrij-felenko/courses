from __future__ import annotations
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Optional

# ── ПРОДУКТ: незмінний. frozen=True забороняє переприсвоєння полів. ──
@dataclass(frozen=True)
class HttpRequest:
    method: str
    url: str
    headers: Mapping[str, str]
    body: Optional[str]
    timeout_ms: int
    retries: int

    @staticmethod
    def builder(method: str, url: str) -> "HttpRequestBuilder":
        return HttpRequestBuilder(method, url)


# ── БУДІВЕЛЬНИК: звичайний змінний об'єкт, копить рішення ──
class HttpRequestBuilder:
    def __init__(self, method: str, url: str):   # обов'язкове — одразу
        self._method = method
        self._url = url
        self._headers: dict[str, str] = {}
        self._body: Optional[str] = None
        self._timeout_ms = 30_000
        self._retries = 0

    def header(self, name: str, value: str) -> "HttpRequestBuilder":
        self._headers[name] = value
        return self                              # крок повертає САМ будівельник

    def body(self, text: str) -> "HttpRequestBuilder":
        self._body = text
        return self

    def timeout(self, ms: int) -> "HttpRequestBuilder":
        self._timeout_ms = ms
        return self

    def retries(self, n: int) -> "HttpRequestBuilder":
        self._retries = n
        return self

    def build(self) -> HttpRequest:
        # ── ЄДИНА точка перевірки ──
        if self._url.strip() == "":
            raise ValueError("HttpRequest: url порожній")
        if self._body is not None and self._method in ("GET", "DELETE"):
            raise ValueError(
                f"HttpRequest: метод {self._method} не несе тіла, але body задано — "
                f"прибери body або зміни метод на POST/PUT"
            )
        if self._timeout_ms <= 0:
            raise ValueError(f"HttpRequest: timeout має бути > 0, а не {self._timeout_ms}")
        if self._retries < 0:
            raise ValueError(f"HttpRequest: retries не може бути від'ємним ({self._retries})")
        return HttpRequest(
            method=self._method,
            url=self._url,
            headers=MappingProxyType(dict(self._headers)),  # незмінне read-only view копії
            body=self._body,
            timeout_ms=self._timeout_ms,
            retries=self._retries,
        )


# ── Виклик читається сам ──
req = (HttpRequest.builder("POST", "https://api.example.com/orders")
       .header("Content-Type", "application/json")
       .body('{"item":"кава","qty":2}')
       .timeout(5_000)
       .retries(3)
       .build())

print(req.method, req.url, req.retries)          # POST  https://…/orders  3
