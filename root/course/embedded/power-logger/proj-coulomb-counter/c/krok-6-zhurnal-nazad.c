// Підсумок проходу журналу.
typedef struct {
    uint32_t avg_current_uA;     // середній струм за весь журнал, мкА
    uint64_t total_charge_mC;    // повний заряд, мілікулони
    uint32_t span_s;             // повний охоплений час, секунди
    uint32_t hourly_mC[24];      // заряд за кожну годину доби, мілікулони
} journal_stats_t;

void journal_analyze(const log_rec_t *recs, size_t n, journal_stats_t *out) {
    memset(out, 0, sizeof(*out));
    if (n < 2) return;

    uint64_t charge_mC = 0;
    for (size_t i = 0; i < n; i++) {
        charge_mC += recs[i].charge_mC;
        uint32_t hour = (recs[i].epoch_s / 3600u) % 24u;   // година доби 0..23
        out->hourly_mC[hour] += recs[i].charge_mC;
    }
    out->total_charge_mC = charge_mC;
    out->span_s = recs[n - 1].epoch_s - recs[0].epoch_s;

    if (out->span_s == 0) return;                          // захист від ділення на нуль
    // Середній струм: I = Q / t.  мКл / с = мА, переводимо в мкА (×1000).
    // Q*1000 у 64 бітах, бо мКл за тиждень легко дають мільярди.
    uint64_t avg_uA = (charge_mC * 1000u + out->span_s / 2) / out->span_s;
    out->avg_current_uA = (uint32_t)avg_uA;
}
