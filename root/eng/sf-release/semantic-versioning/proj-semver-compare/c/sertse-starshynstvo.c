static bool all_digits(const char *s) {
    for (; *s; ++s) if (!isdigit((unsigned char)*s)) return false;
    return true;                         // порожніх ідентифікаторів тут не буває — відсіяв розбір
}

// Одна пара ідентифікаторів передвипуску: правила 11.4.1–11.4.3 специфікації.
static int cmp_id(const char *a, const char *b) {
    bool na = all_digits(a), nb = all_digits(b);
    if (na && nb) {                      // обидва числові — ЧИСЛАМИ, а не рядками
        size_t la = strlen(a), lb = strlen(b);
        if (la != lb) return (la > lb) - (la < lb);  // без провідних нулів довший = більший
        return strcmp(a, b);             // рівні завдовжки — лексичне дасть саме числовий порядок
    }
    if (na != nb) return na ? -1 : +1;   // числовий ЗАВЖДИ нижчий за буквений
    return strcmp(a, b);                 // обидва буквені — лексично, в ASCII-порядку
}

// Передвипуски двох версій з РІВНИМ ядром: правила 11.2 і 11.4.
int cmp_prerelease(const semver_t *a, const semver_t *b) {
    if (a->pre_count == 0 && b->pre_count == 0) return 0;   // обидва готові — рівні
    if (a->pre_count == 0) return +1;    // готовий випуск старший за передвипуск
    if (b->pre_count == 0) return -1;

    int n = a->pre_count < b->pre_count ? a->pre_count : b->pre_count;
    for (int i = 0; i < n; ++i) {
        int c = cmp_id(a->pre[i], b->pre[i]);
        if (c) return c;                 // перша ж відмінність вирішує все
    }
    // спільний префікс рівний — довший набір ідентифікаторів старший
    return (a->pre_count > b->pre_count) - (a->pre_count < b->pre_count);
}
