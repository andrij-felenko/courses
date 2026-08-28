// Повертає 1, якщо хвіст БІХ згас (фільтр стійкий), інакше 0.
int sos_is_stable(sos_chain_t *c) {
    sos_reset(c);
    int32_t out = sos_step(c, (int32_t)(1LL << 28));   // невеликий імпульс (із запасом)
    int64_t peak = out < 0 ? -(int64_t)out : out;
    for (int n = 1; n < 2000; ++n) {
        out = sos_step(c, 0);                           // далі — нулі
        int64_t m = out < 0 ? -(int64_t)out : out;
        if (m > peak) peak = m;
        if (m > (1LL << 30)) { sos_reset(c); return 0; }  // розганяється
    }
    sos_reset(c);
    return (out > -1024 && out < 1024);                 // хвіст справді осів
}
