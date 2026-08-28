static void resize(HashTable *t, size_t new_cap);   // прототип; тіло — на кроці 6

static void put(HashTable *t, const char *key, long value) {
    // поріг: α = used/cap ≥ 0.7 ?  (used лічить і надгробки — вони теж займають пробу)
    if ((t->used + 1) * 10 >= t->cap * 7)
        resize(t, t->cap * 2);

    size_t mask       = t->cap - 1;
    size_t idx        = fnv1a(key) & mask;
    size_t first_tomb = 0;
    bool   have_tomb  = false;                // ще не бачили надгробка

    for (size_t i = 0; i < t->cap; ++i) {
        size_t j = (idx + i) & mask;
        Slot  *s = &t->slots[j];

        if (s->state == EMPTY) {              // дійшли до порожньої → ключа немає
            Slot *dst = have_tomb ? &t->slots[first_tomb] : s;
            if (!have_tomb) t->used++;        // зайняли РАНІШЕ порожню комірку
            dst->key   = dup_key(key);        // …а надгробок вже рахувався в used
            dst->value = value;
            dst->state = OCCUPIED;
            t->len++;
            return;
        }
        if (s->state == DELETED) {
            if (!have_tomb) { have_tomb = true; first_tomb = j; }  // лише ПЕРШИЙ
            continue;                         // але йдемо далі — ключ може бути попереду!
        }
        if (strcmp(s->key, key) == 0) {       // OCCUPIED і той самий ключ → оновлюємо
            s->value = value;
            return;
        }
        // чужий ключ — колізія, наступна проба
    }
}
