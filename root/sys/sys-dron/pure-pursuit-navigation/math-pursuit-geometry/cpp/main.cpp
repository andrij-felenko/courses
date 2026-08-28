#include <cmath>
#include <cstdio>

int main() {
    // осі виведення: x>0 — ціль праворуч, центр у (+R, 0)
    double L = 2.0, x = 0.5;                 // випередження й бічний зсув [м]
    double y = std::sqrt(L*L - x*x);         // поздовжній зсув [м]

    double R = (L*L) / (2.0*x);              // радіус дуги
    double kappa = 2.0*x / (L*L);            // кривина

    double cx = R, cy = 0.0;                 // центр — на осі «вбік», на R
    double d = std::hypot(x - cx, y - cy);   // відстань центр → ціль (має бути R)

    std::printf("y=%.3f  R=%.3f  kappa=%.3f  |center->goal|=%.3f\n", y, R, kappa, d);
    // друкує: y=1.936  R=4.000  kappa=0.250  |center->goal|=4.000
    return 0;
}
