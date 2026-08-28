#include <cstdio>
#include <cmath>

// Одна нелінійна ланка: діод послідовно з резистором від Vdd.
// Шукаємо напругу на діоді методом Ньютона — як це робить SPICE у вузлі.
int main() {
    const double Vt = 0.02585;   // теплова напруга при ~27 °C
    const double Is = 1e-14;     // зворотний струм насичення
    const double Vdd = 5.0, R = 1000.0;

    double U = 0.6;              // початкова здогадка
    for (int k = 0; k < 8; k++) {
        double Id  = Is * (std::exp(U / Vt) - 1.0);   // струм діода
        double Ir  = (Vdd - U) / R;                   // струм резистора
        double f   = Id - Ir;                         // нев'язка балансу струмів
        double dfd = Is / Vt * std::exp(U / Vt);      // похідна струму діода (провідність)
        double df  = dfd + 1.0 / R;                   // повна похідна f по U
        U = U - f / df;                               // крок Ньютона: зсунути здогадку
        std::printf("крок %d: U = %.4f В, нев'язка = %+.2e А\n", k, U, f);
        if (std::fabs(f) < 1e-12) break;              // збіглося — виходимо
    }
    std::printf("робоча точка: U = %.4f В, I = %.3f мА\n",
                U, (Vdd - U) / R * 1000.0);
    return 0;
}
