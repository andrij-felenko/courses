# acl/crm_facade.py — ховає незручний доступ. Усе ще в ЧУЖИХ типах.
from collections import deque
from crm.dto import CrmOrderDto
from crm.http_client import CrmHttpClient  # сира HTTP-обгортка CRM

class CrmOrderFacade:
    def __init__(self, http: CrmHttpClient):
        self._http = http
        self._buffer: deque[CrmOrderDto] = deque()
        self._page = 0
        self._exhausted = False

    # Один чесний виклик замість пагінації, ретраїв і формату відповіді.
    def fetch_next(self) -> CrmOrderDto | None:
        if not self._buffer and not self._exhausted:
            self._load_page()
        return self._buffer.popleft() if self._buffer else None

    def _load_page(self) -> None:
        resp = self._retry(
            lambda: self._http.get(f"/orders?page={self._page}&size=100"))
        self._buffer = deque(resp.items)      # сирі CrmOrderDto
        self._exhausted = not resp.items
        self._page += 1

    def _retry(self, fn, tries=3):
        for i in range(tries):
            try:
                return fn()
            except Exception:
                if i >= tries - 1:
                    raise
