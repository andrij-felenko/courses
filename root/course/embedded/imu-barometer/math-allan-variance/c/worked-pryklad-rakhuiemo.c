// Девіація Аллана для кластера з m відліків: τ = m*dt.
// Overlapping: сусідні кластери [s, s+m) і [s+m, s+2m), s біжить по всіх зсувах.
double allan_dev(const double *cs, int N, int m, double dt)
{
    double acc = 0.0;                 // накопичена сума квадратів різниць
    long   cnt = 0;                   // скільки пар усереднили
    for (int s = 0; s + 2 * m <= N; s++) {
        double mean1 = (cs[s + m]     - cs[s])     / m;   // середнє 1-го кластера
        double mean2 = (cs[s + 2 * m] - cs[s + m]) / m;   // середнє 2-го (сусіда)
        double d = mean2 - mean1;                         // різниця сусідів
        acc += d * d;                                     // накопичуємо квадрат
        cnt++;
    }
    double avar = acc / (2.0 * cnt);  // σ_A²(τ): множник ½ з означення
    return sqrt(avar);                // σ_A(τ) — девіація (корінь із дисперсії)
}
