import time
import threading
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class TokenState:
    access_token: str
    refresh_token: str
    expires_at: float  # UNIX timestamp в секундах


class AuthInterceptor:
    def __init__(self, auth_endpoint: str, client_id: str, clock_skew_sec: float = 30.0):
        self.auth_endpoint = auth_endpoint
        self.client_id = client_id
        self.clock_skew_sec = clock_skew_sec
        self.token_state: Optional[TokenState] = None

        self._lock = threading.Lock()
        self._cv = threading.Condition(self._lock)
        self._is_refreshing = False

    def set_tokens(self, access_token: str, refresh_token: str, expires_in_sec: float) -> None:
        with self._lock:
            self.token_state = TokenState(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=time.time() + expires_in_sec
            )

    def get_valid_access_token(self) -> str:
        """Повертає дійсний токен, оновлюючи його при потребі (Single-Flight)."""
        with self._lock:
            while True:
                if self.token_state is None:
                    raise RuntimeError("Користувач не автентифікований")

                now = time.time()
                is_expired = now >= (self.token_state.expires_at - self.clock_skew_sec)

                if not is_expired:
                    return self.token_state.access_token

                if not self._is_refreshing:
                    # Цей потік стає лідером оновлення
                    self._is_refreshing = True
                    break
                else:
                    # Інші потоки очікують завершення лідера
                    self._cv.wait()

        # Виконуємо мережевий запит оновлення поза блокуванням основного стану
        try:
            new_tokens = self._perform_network_refresh(self.token_state.refresh_token)
            with self._lock:
                self.token_state = new_tokens
                self._is_refreshing = False
                self._cv.notify_all()
                return self.token_state.access_token
        except Exception as err:
            with self._lock:
                self._is_refreshing = False
                self._cv.notify_all()
            raise RuntimeError(f"Помилка оновлення токена: {err}") from err

    def handle_401_unauthorized(self, failed_token: str) -> str:
        """Реактивне оновлення: якщо запит отримав 401 зі старим токеном."""
        with self._lock:
            # Якщо токен уже був оновлений іншим потоком, просто беремо новий
            if self.token_state and self.token_state.access_token != failed_token:
                return self.token_state.access_token

        # Примусово запускаємо оновлення
        return self.get_valid_access_token()

    def _perform_network_refresh(self, refresh_token: str) -> TokenState:
        # Імітація HTTP POST /oauth/v2/token
        time.sleep(0.05)  # Імітація затримки мережі
        now = time.time()
        return TokenState(
            access_token=f"new_access_{int(now * 1000)}",
            refresh_token=f"new_refresh_{int(now * 1000)}",
            expires_at=now + 900.0  # +15 хвилин
        )
