# Шлях 2: read-your-writes. Після запису «пришпилюємо» читання цього
# користувача до основної на вікно W — доки репліка гарантовано наздожене.
import random

class ProfileStore:
    WINDOW_MS = 1000   # W = 1 с: стеля лага з запасом

    def __init__(self, primary, replicas, recent):
        self.primary = primary
        self.replicas = replicas
        self.recent = recent          # спільний на ВСІ вузли (напр. Redis із TTL)

    async def save(self, user_id, patch):
        await self.primary.execute(
            "UPDATE profiles SET data = $2, updated_at = now() WHERE id = $1",
            user_id, patch,
        )
        await self.recent.mark(user_id, self.WINDOW_MS)   # «гарячий» на W мс

    async def get(self, user_id):
        if await self.recent.is_hot(user_id):
            src = self.primary                            # свіжо писав → з основної
        else:
            src = random.choice(self.replicas)
        row = await src.fetchrow(
            "SELECT data FROM profiles WHERE id = $1", user_id,
        )
        return row["data"]   # гаряче читання ЗАВЖДИ бачить власний запис
