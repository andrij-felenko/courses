// Пороги — ІНЖЕНЕРНЕ рішення під конкретну задачу (див. розмову нижче).
struct Thresholds {
    float max_abs    = 0.10f;   // макс. допустиме |ref - lite| на виході
    float min_winner = 0.99f;   // частка кадрів, де переможець мусить збігтися
    float max_acc_drop = 0.01f; // макс. допустиме падіння точності (1%)
};

// true = ПРОШИВАТИ; false = РОЗБИРАТИСЯ. Друкує діагностику в обох випадках.
bool verdict(const Report& r, const Thresholds& th) {
    float winner_rate = r.n ? (float)r.winner_match / r.n : 0.0f;
    float acc_drop = 0.0f;
    if (r.have_labels && r.n)
        acc_drop = (float)(r.ref_correct - r.lite_correct) / r.n;

    printf("=== перевірка експорту: %d кадрів ===\n", r.n);
    printf("  макс |ref-lite|   = %.4f  (поріг %.4f)\n", r.max_abs_diff, th.max_abs);
    printf("  середнє |ref-lite|= %.4f\n", r.mean_abs_diff);
    printf("  збіг переможця    = %.3f  (поріг %.3f)\n", winner_rate, th.min_winner);
    if (r.have_labels) {
        printf("  точність ориг.    = %.3f\n", (float)r.ref_correct / r.n);
        printf("  точність експорт  = %.3f\n", (float)r.lite_correct / r.n);
        printf("  падіння точності  = %.4f  (поріг %.4f)\n", acc_drop, th.max_acc_drop);
    }

    bool ok = (r.max_abs_diff <= th.max_abs)
           && (winner_rate    >= th.min_winner)
           && (!r.have_labels || acc_drop <= th.max_acc_drop);

    printf(ok ? "ВЕРДИКТ: ПРОШИВАТИ ✓\n" : "ВЕРДИКТ: РОЗБИРАТИСЯ ✗\n");
    return ok;
}
