// Підсумок перевірки — усе, що треба для вердикту й для діагностики.
struct Report {
    int   n             = 0;        // скільки кадрів перевірено
    float max_abs_diff  = 0.0f;     // найбільше |ref - lite| по ВСІХ виходах
    float mean_abs_diff = 0.0f;     // середнє |ref - lite|
    int   winner_match  = 0;        // на скількох кадрах клас-переможець збігся
    int   ref_correct   = 0;        // скільки правильних в оригіналу
    int   lite_correct  = 0;        // скільки правильних в експорту
    bool  have_labels   = false;    // чи були істинні відповіді
};

// Прогнати ВЕСЬ тестовий набір крізь кандидата й зібрати метрики.
Report evaluate(LiteModel& lite, const std::vector<TestCase>& set) {
    Report r;
    double sum_abs = 0.0;
    long   diff_count = 0;

    for (const TestCase& tc : set) {
        float out[kNumOutputs];
        if (!lite.run(tc.frame, out)) continue;     // збій прогону — пропускаємо
        r.n++;

        // ── вісь 1: амплітуда виходу ──
        for (int i = 0; i < kNumOutputs; ++i) {
            float d = std::fabs(tc.ref[i] - out[i]);
            if (d > r.max_abs_diff) r.max_abs_diff = d;
            sum_abs += d;
            diff_count++;
        }

        // ── вісь 2: клас-переможець ──
        int wr = winner(tc.ref, kNumOutputs);       // переможець ОРИГІНАЛУ
        int wl = winner(out,    kNumOutputs);       // переможець ЕКСПОРТУ
        if (wr == wl) r.winner_match++;

        // ── вісь 3: падіння точності (лише де є істина) ──
        if (tc.true_label >= 0) {
            r.have_labels = true;
            if (wr == tc.true_label) r.ref_correct++;
            if (wl == tc.true_label) r.lite_correct++;
        }
    }
    r.mean_abs_diff = diff_count ? (float)(sum_abs / diff_count) : 0.0f;
    return r;
}
