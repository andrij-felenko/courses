import time
import asyncio
from dataclasses import dataclass

@dataclass
class TokenBundle:
    access_token: str
    refresh_token: str
    expires_at: int

class AsyncTokenRefreshCoordinator:
    """Координатор ротації токенів із захистом від паралельних запитів (Single-Flight)."""

    def __init__(self, initial_tokens: TokenBundle):
        self.tokens = initial_tokens
        self._lock = asyncio.Lock()

    async def get_valid_access_token(self) -> str:
        now = int(time.time())
        # Якщо токен діє щонайменше 30 секунд, віддаємо без блокувань
        if self.tokens.expires_at > (now + 30):
            return self.tokens.access_token

        async with self._lock:
            # Повторна перевірка після захоплення замка (Double-Checked Locking)
            now = int(time.time())
            if self.tokens.expires_at > (now + 30):
                return self.tokens.access_token

            # Тільки один асинхронний таск виконує виклик /token
            self.tokens = await self._execute_network_refresh(self.tokens.refresh_token)
            return self.tokens.access_token

    async def _execute_network_refresh(self, current_refresh_token: str) -> TokenBundle:
        await asyncio.sleep(0.1)
        now = int(time.time())
        return TokenBundle(
            access_token="eyJhbGciOiJSUzI1NiIs...",
            refresh_token="r_rotated_secret_999",
            expires_at=now + 3600
        )
