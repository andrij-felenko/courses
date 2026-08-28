#include <math.h>
#include <stdint.h>

typedef struct {
    double e_rms;        // середньоквадратична помилка стеження, °
    int    zero_cross;   // скільки разів помилка змінила знак (дзвін)
} TrackHealth;

// des[], act[] — паралельні масиви за один відрізок польоту, n точок.
static TrackHealth track_health(const double *des, const double *act, int n) {
    TrackHealth h = {0.0, 0};
    if (n < 2) return h;

    double sum_sq = 0.0;
    double prev_e = des[0] - act[0];
    for (int i = 0; i < n; i++) {
        double e = des[i] - act[i];       // помилка стеження в точці i
        sum_sq += e * e;                  // накопичуємо квадрат
        if (i > 0 && (e > 0) != (prev_e > 0) && e != 0.0)
            h.zero_cross++;               // знак помінявся — перетин нуля
        prev_e = e;
    }
    h.e_rms = sqrt(sum_sq / n);           // корінь із середнього квадратів
    return h;
}
