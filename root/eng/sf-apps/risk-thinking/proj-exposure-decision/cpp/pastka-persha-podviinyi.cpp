struct Risk {
    const char* name;
    double      p;
    double      loss;
    int         group;   // 0 = незалежний; однакове ненульове = зчеплені між собою
};

// Експозиція варіанта з урахуванням зчеплення.
// Незалежні ризики додаємо як є. Кожну групу зчеплених згортаємо в ОДИН
// доданок: ймовірність «спрацював хоч один» = 1 − Π(1 − p_i),
// а втрата — найбільша в групі (спільна скеля коштує стільки, скільки
// коштує найгірший її прояв, а не сума проявів того самого лиха).
static double total_exposure_grouped(const Variant& v) {
    double sum = 0.0;
    // спочатку незалежні
    for (int i = 0; i < v.count; ++i)
        if (v.risks[i].group == 0)
            sum += exposure(v.risks[i]);

    // тепер групи: припустимо, номери груп у діапазоні 1..MAXG
    const int MAXG = 16;
    for (int g = 1; g <= MAXG; ++g) {
        double p_none    = 1.0;   // ймовірність, що ЖОДЕН у групі не спрацював
        double max_loss  = 0.0;   // найбільша втрата в групі
        bool   has_group = false;
        for (int i = 0; i < v.count; ++i) {
            if (v.risks[i].group == g) {
                has_group = true;
                p_none   *= (1.0 - v.risks[i].p);
                if (v.risks[i].loss > max_loss) max_loss = v.risks[i].loss;
            }
        }
        if (has_group) {
            double p_any = 1.0 - p_none;   // об'єднання, не сума
            sum += p_any * max_loss;
        }
    }
    return sum;
}
