#include <cstdio>

struct After { double v1, v2; };            // швидкості після удару

// Резолвер контакту: рівно це фізичний рушій крутить у гарячому циклі —
// по парі тіл на кожен дотик, тисячі разів за кадр. Ані виділень, ані гілок.
constexpr After collide(double m1, double m2,
                        double u1, double u2, double e) {
    const double vcm = (m1*u1 + m2*u2) / (m1 + m2);   // швидкість центра мас
    return { (1 + e)*vcm - e*u1,                       // v₁
             (1 + e)*vcm - e*u2 };                     // v₂
}

constexpr double kinetic(double m1, double m2, double w1, double w2) {
    return 0.5*m1*w1*w1 + 0.5*m2*w2*w2;
}
