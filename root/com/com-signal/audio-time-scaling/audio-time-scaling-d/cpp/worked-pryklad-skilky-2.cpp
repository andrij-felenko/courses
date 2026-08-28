// Знайти зсув у [-seek, +seek], за якого кандидат зі входу
// найкраще продовжує хвіст уже викладеного виходу (шаблон).
// tail[]   — останні L відліків виходу (шаблон)
// in[]     — вхідний сигнал; base — ідеальна позиція кадру в ньому
int find_best_shift(const float* tail, int L,
                    const float* in, int base, int seek) {
    long  best_corr  = -2147483647L;   // якнайменше, щоб перший збіг переміг
    int   best_shift = 0;

    for (int d = -seek; d <= seek; ++d) {   // пробуємо кожен зсув
        long corr = 0;
        for (int i = 0; i < L; ++i)         // сума добутків = схожість форми
            corr += (long)(tail[i] * in[base + d + i]);
        if (corr > best_corr) {             // запам'ятати найсхожіший
            best_corr  = corr;
            best_shift = d;
        }
    }
    return best_shift;   // δ: звідси беремо наступний кадр
}
