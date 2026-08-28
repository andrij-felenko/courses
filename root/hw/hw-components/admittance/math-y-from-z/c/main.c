// Полярний бік обернення: |Y| = 1/|Z|, φ_Y = −φ_Z
#include <stdio.h>
#include <math.h>

int main(void) {
    double R = 30.0, X = 40.0;              // Ом
    double Zmag = sqrt(R*R + X*X);          // |Z| = sqrt(2500) = 50 Ом
    double phiZ = atan2(X, R);              // кут імпедансу (рад), +53.13°

    double Ymag = 1.0 / Zmag;               // |Y| = 1/50 = 0.0200 См
    double phiY = -phiZ;                    // кут адмітансу = −φ_Z, −53.13°

    printf("|Z| = %.1f Ом,  phiZ = %+.2f deg\n", Zmag, phiZ*180.0/M_PI);
    printf("|Y| = %.4f См,  phiY = %+.2f deg\n", Ymag, phiY*180.0/M_PI);
    return 0;
}
