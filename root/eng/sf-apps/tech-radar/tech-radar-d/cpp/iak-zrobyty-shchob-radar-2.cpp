// Фітнес-функція радара: новий код не сміє залежати від блипа в HOLD.
// Повертає кількість порушень (0 — складання проходить).
int check_no_hold_deps(const char* module, const char* deps[], int n) {
    int violations = 0;
    for (int i = 0; i < n; ++i) {
        int r = ring_of(deps[i]);
        if (r == HOLD) {
            fprintf(stderr,
                "[радар] %s тягне '%s' — це кільце HOLD, нового на цьому не заводимо\n",
                module, deps[i]);
            ++violations;
        } else if (r == -1) {
            // не заборона, а сигнал: технологія взагалі поза радаром —
            // її не оцінювали, тож варто винести на найближчий перегляд
            fprintf(stderr,
                "[радар] увага: %s тягне '%s', якого нема на радарі\n",
                module, deps[i]);
        }
    }
    return violations;
}
