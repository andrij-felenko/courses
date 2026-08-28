#include <stdio.h>

// лінійна інтерполяція фази (у градусах) на частоті f_x
// за двома виміряними точками (f1,ph1) і (f2,ph2)
static float phase_at(float fx,
                      float f1, float ph1,
                      float f2, float ph2) {
    float k = (fx - f1) / (f2 - f1);   // частка шляху від точки 1 до 2
    return ph1 + k * (ph2 - ph1);      // фаза на fx
}

int main(void) {
    float f_cross = 80.0e3f;           // частота зрізу контуру (|Aβ| = 1)

    // фаза на частоті зрізу — інтерполяцією між 50 кГц і 100 кГц
    float ph = phase_at(f_cross,
                        50.0e3f, -120.0f,
                        100.0e3f, -150.0f);

    // запас фази = 180° − |фаза на частоті зрізу|
    float pm = 180.0f - (ph < 0 ? -ph : ph);

    printf("phase at crossover: %.1f deg\n", ph);  // -138.0
    printf("phase margin:       %.1f deg\n", pm);  //  42.0
    return 0;
}
