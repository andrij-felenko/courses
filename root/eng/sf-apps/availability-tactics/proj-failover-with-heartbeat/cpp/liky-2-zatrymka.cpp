#define RETURN_DELAY_MS   30000u   // 30 с стабільної роботи в резерві до права вернутись
#define STICKY_FAILBACK   true     // true = автоматично роль НЕ повертаємо взагалі

// Викликається на вузлі в стані REJOINING (колишній головний, що ожив).
// Повертає true, лише коли вузлові МОЖНА знову претендувати на роль.
bool may_reclaim_role(Hysteretic *self, uint32_t now_ms) {
    if (!self->eligible)                       // ще не визнаний придатним
        return false;
    if (STICKY_FAILBACK)                       // sticky: не забираємо роль назад самі
        return false;
    // відсидів у резерві стабільний карантин від миті, як став придатним?
    return (now_ms - self->eligible_since_ms) >= RETURN_DELAY_MS;
}
