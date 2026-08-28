import time
import threading
from dataclasses import dataclass
from typing import Optional


@dataclass
class TokenState:
    access_token: str
    refresh_token: str
    expires_at: float


class ThreadSafeAuthInterceptor:
    def __init__(self, skew_seconds: float = 30.0):
        self._skew_seconds = skew_seconds
        self._state: Optional[TokenState] = None
        self._lock = threading.Lock()
        self._cv = threading.Condition(self._lock)
        self._is_refreshing = False

    def update_tokens(self, access: str, refresh: str, expires_in: float) -> None:
        with self._lock:
            self._state = TokenState(access, refresh, time.time() + expires_in)

    def get_authorized_token(self) -> str:
        """Повертає дійсний токен, синхронізуючи оновлення між потоками."""
        with self._lock:
            while True:
                if self._state is None:
                    raise RuntimeError("Сесія відсутня")

                now = time.time()
                is_expired = now >= (self._state.expires_at - self._skew_seconds)

                if not is_expired:
                    return self._state.access_token

                if not self._is_refreshing:
                    self._is_refreshing = True
                    current_refresh = self._state.refresh_token
                    break
                else:
                    self._cv.wait()

        # Виконуємо виклик сервера авторизації поза блокуванням основного стану
        try:
            new_tokens = self._call_token_endpoint(current_refresh)
            with self._lock:
                self._state = new_tokens
                self._is_refreshing = False
                self._cv.notify_all()
                return self._state.access_token
        except Exception:
            with self._lock:
                self._is_refreshing = False
                self._cv.notify_all()
            raise

    def _call_token_endpoint(self, refresh_token: str) -> TokenState:
        # Імітація мережевого запиту POST /oauth/v2/token
        time.sleep(0.05)
        now = time.time()
        return TokenState(
            access_token=f"acc_{int(now * 1000)}",
            refresh_token=f"ref_{int(now * 1000)}",
            expires_at=now + 900.0
        )
