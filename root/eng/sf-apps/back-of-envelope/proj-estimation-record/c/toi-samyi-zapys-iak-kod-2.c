// ── Вирок: порівняти з порогом, надрукувати бік і запас ───────────────
static void verdict(const char *what, uint64_t value, uint64_t threshold) {
    if (value == 0) { printf("%s: оцінка 0 — щось не так у припущеннях\n", what); return; }
    if (value <= threshold) {
        // запас = у скільки разів поріг більший за оцінку (ціла частина)
        uint64_t margin = threshold / value;
        printf("%s: %llu <= поріг %llu  ->  ВЛАЗИТЬ (запас x%llu)\n",
               what, (unsigned long long)value, (unsigned long long)threshold,
               (unsigned long long)margin);
    } else {
        uint64_t over = value / threshold;
        printf("%s: %llu >  поріг %llu  ->  НЕ ВЛАЗИТЬ (перевищення x%llu)\n",
               what, (unsigned long long)value, (unsigned long long)threshold,
               (unsigned long long)over);
    }
}
