#include <stdio.h>
#include <math.h>

int main(void) {
    const double Vin   = 3.3;      // напруга живлення, В
    const double Vphi  = 3.3;      // розмах такту (гойдається на всю шину), В
    const double Vd    = 0.3;      // падіння на одному клапані, В
    const double Vgoal = 18.0;     // цільова напруга, В
    const double Iout  = 50e-6;    // струм навантаження, А
    const double f     = 500e3;    // частота такту, Гц
    const double Cs    = 100e-12;  // конденсатор сходинки, Ф

    // Скільки сходинок треба (без урахування провисання):
    // Vgoal = Vin + N*(Vphi - Vd)  →  N = (Vgoal - Vin)/(Vphi - Vd)
    double N_real = (Vgoal - Vin) / (Vphi - Vd);
    int N = (int)ceil(N_real);     // округлюємо вгору — сходинок ціле число
    printf("Треба сходинок: %.2f -> беремо %d\n", N_real, N);

    // Провисання під навантаженням: Rвих ~ N/(f*Cs)
    double Rout = N / (f * Cs);
    double droop = Iout * Rout;
    printf("Вихідний опір: %.0f Ом, провисання: %.2f В\n", Rout, droop);

    // Напруга без навантаження і під навантаженням:
    double Voc = Vin + N * (Vphi - Vd);
    double Vload = Voc - droop;
    printf("Холостий хід: %.2f В, під навантаженням: %.2f В\n", Voc, Vload);
    return 0;
}
