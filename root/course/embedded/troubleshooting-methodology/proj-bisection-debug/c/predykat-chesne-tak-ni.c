// ── Ознака збою. Її виставляє те місце коду, що ловить симптом (ISR аварії,
//    перевірка порогу, лічильник скидань). reset_symptom() чистить перед дослідом.
static volatile int g_symptom_seen = 0;

void reset_symptom(void)  { g_symptom_seen = 0; }
void mark_symptom(void)   { g_symptom_seen = 1; }   // клич із місця, що ловить збій

// Автоматичний предикат: після навантаження дивимось, чи виставилась ознака.
static int predicate_symptom_flag(void) {
    return g_symptom_seen;
}

// Приклад місця, що ловить симптом: перевірка виміру на абсурд.
void on_new_sample(int32_t value) {
    if (value < SANE_MIN || value > SANE_MAX)
        mark_symptom();          // збій проявився — зафіксувати
}
