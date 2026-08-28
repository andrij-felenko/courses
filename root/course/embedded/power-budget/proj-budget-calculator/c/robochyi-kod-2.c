typedef struct {
    uint64_t worst_uw;    // найгірший одночасний попит на вході, мкВт
    uint64_t avg_uw;      // середнє за цикл на вході, мкВт
    uint64_t source_uw;   // стеля джерела, мкВт
    uint64_t headroom_uw; // робоча межа = стеля × 0.8, мкВт
    bool     fits;        // worst ≤ headroom ?
    uint16_t load_pct;    // worst як % стелі (для звіту)
} budget_t;

// rails[], loads[] — таблиці системи; nr, nl — їхні розміри.
// src_mv, src_ma   — стеля джерела на вході (напр. 5000 мВ × 500 мА для USB).
// headroom_pct     — частка стелі, у яку дозволяємо лізти (звичайно 80).
budget_t power_budget(const rail_t *rails, size_t nr,
                      const load_t *loads, size_t nl,
                      uint32_t src_mv, uint32_t src_ma,
                      uint16_t headroom_pct) {
    budget_t b = {0, 0, 0, 0, false, 0};

    for (size_t i = 0; i < nl; i++) {
        const load_t *L = &loads[i];
        if (L->rail >= nr) continue;             // захист від кривого індексу
        const rail_t *R = &rails[L->rail];
        if (R->eff_pct == 0) continue;           // ділення на нуль: пропускаємо

        // 1) потужність на ВИХОДІ шини: U[мВ] × I[мА] = P[мкВт]
        uint64_t p_out = (uint64_t)R->mv * L->peak_ma;

        // 2) відбиваємо на ВХІД через ККД: P_вх = P_вих / ККД
        //    ділимо в кінці кроку, але множник 100 беремо в 64 бітах
        uint64_t p_in = (p_out * 100u) / R->eff_pct;

        // 3) пік іде у worst-case як є; у середнє — помножений на цикл
        b.worst_uw += p_in;
        b.avg_uw   += (p_in * L->duty_pm) / 1000u;
    }

    // стеля джерела й робоча межа
    b.source_uw   = (uint64_t)src_mv * src_ma;            // мВ × мА = мкВт
    b.headroom_uw = (b.source_uw * headroom_pct) / 100u;
    b.fits        = (b.worst_uw <= b.headroom_uw);
    if (b.source_uw)
        b.load_pct = (uint16_t)((b.worst_uw * 100u) / b.source_uw);
    return b;
}
