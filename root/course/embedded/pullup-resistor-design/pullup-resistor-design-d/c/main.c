#include <stdio.h>

// Повертає межі опору підтяжки [Ом] для заданих умов шини.
// vdd, vol — у вольтах; iol — у амперах; tr — у секундах; cb — у фарадах.
void pullup_window(double vdd, double vol, double iol,
                   double tr, double cb,
                   double *rp_min, double *rp_max) {
    *rp_min = (vdd - vol) / iol;            // нижня межа: надійний нуль
    *rp_max = tr / (0.8473 * cb);           // верхня межа: фронт устигає
}

int main(void) {
    double rmin, rmax;
    // Швидкий I2C: 3.3 В, VOL=0.4 В, IOL=3 мА, t_r=300 нс, Cb=150 пФ
    pullup_window(3.3, 0.4, 3e-3, 300e-9, 150e-12, &rmin, &rmax);

    printf("Rp(min) = %.0f Om\n", rmin);    // ~967
    printf("Rp(max) = %.0f Om\n", rmax);    // ~2360
    if (rmax < rmin)
        printf("Vikno porozhnie -> rozvantazhuy shynu!\n");
    else
        printf("Bery Rp mizh %.0f i %.0f Om\n", rmin, rmax);  // напр. 2.2 кОм
    return 0;
}
