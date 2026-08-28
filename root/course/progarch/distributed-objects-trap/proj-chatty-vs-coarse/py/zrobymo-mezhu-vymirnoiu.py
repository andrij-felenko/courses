# Перехід через межу невидимий у коді — тому й пастка.
# Зробимо його ВИМІРНИМ: кожен перехід іде крізь Link, і той його лічить.
class Link:
    def __init__(self):
        self.crossings = 0

    async def cross(self, work):            # один похід туди-й-назад
        self.crossings += 1
        return work()                       # «летіли б байти»; ми лише рахуємо перехід

    def cost_ms(self, per_crossing: float) -> float:
        return self.crossings * per_crossing   # 0.5 — той самий ДЦ; 150 — океан
