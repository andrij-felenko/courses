RETURN_DELAY_MS = 30000   # 30 с стабільної роботи в резерві до права вернутись
STICKY_FAILBACK = True    # True = автоматично роль НЕ повертаємо взагалі


# Викликається на вузлі в стані REJOINING (колишній головний, що ожив).
# Повертає True, лише коли вузлові МОЖНА знову претендувати на роль.
def may_reclaim_role(self: Hysteretic, now_ms: int) -> bool:
    if not self.eligible:              # ще не визнаний придатним
        return False
    if STICKY_FAILBACK:                # sticky: не забираємо роль назад самі
        return False
    # відсидів у резерві стабільний карантин від миті, як став придатним?
    return (now_ms - self.eligible_since_ms) >= RETURN_DELAY_MS
