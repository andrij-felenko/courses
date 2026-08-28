# Шлях 1: читання завжди з пулу реплік. Швидко й дешево —
# але репліка може ще НЕ мати щойно записаного (застаріле читання).
import random

class ProfileStore:
    def __init__(self, primary, replicas):
        self.primary = primary      # єдина основна — приймає записи
        self.replicas = replicas    # пул реплік — розносять читання

    async def save(self, user_id, patch):
        await self.primary.execute(
            "UPDATE profiles SET data = $2, updated_at = now() WHERE id = $1",
            user_id, patch,
        )

    async def get(self, user_id):
        r = random.choice(self.replicas)   # розносимо читання по репліках
        row = await r.fetchrow(
            "SELECT data FROM profiles WHERE id = $1", user_id,
        )
        return row["data"]   # може бути версія ДО save(), якщо репліка відстала
