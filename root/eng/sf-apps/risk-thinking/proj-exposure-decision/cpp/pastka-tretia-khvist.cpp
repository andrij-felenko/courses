struct Risk {
    const char* name;
    double      p;
    double      loss;
    int         group;
    bool        catastrophic;   // true = «хвіст»: рідкісна, але руйнівна подія
};

// Поріг, за яким втрата вважається такою, що її не можна усереднювати:
// подія цього масштабу не «дорога», вона ЕКЗИСТЕНЦІЙНА для проєкту.
static const double RUIN_THRESHOLD = 100.0;   // людино-днів

// Замість того, щоб мовчки додати хвіст до середнього, виносимо його окремо.
static void report_with_tail(const Variant& v) {
    double routine = 0.0;                 // сума експозицій буденних ризиків
    printf("=== %s ===\n", v.name);
    for (int i = 0; i < v.count; ++i) {
        const Risk& r = v.risks[i];
        bool tail = r.catastrophic || r.loss >= RUIN_THRESHOLD;
        if (tail) {
            // хвіст НЕ вливаємо в середнє — показуємо як окремий стоп-сигнал
            printf("  [ХВІСТ] %-38s p=%.3f, втрата=%.0f  <-- окреме рішення!\n",
                   r.name, r.p, r.loss);
        } else {
            routine += exposure(r);
        }
    }
    printf("  Буденна експозиція (усереднена): %.1f люд.-днів\n", routine);
    printf("  Хвостові ризики середнім НЕ вимірюються — їх або усувають "
           "(резервні копії, реплікація), або свідомо приймають ОКРЕМИМ рішенням.\n");
}
