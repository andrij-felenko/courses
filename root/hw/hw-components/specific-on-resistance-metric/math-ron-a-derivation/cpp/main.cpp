#include <cmath>
#include <cstdio>

int main() {
    // Сталі кремнію (в системі см, В, Кл, Ф)
    const double eps0 = 8.854e-14;   // Ф/см — проникність вакууму
    const double epsSi = 11.7;       // відносна проникність кремнію
    const double eps  = eps0 * epsSi;// Ф/см
    const double q    = 1.602e-19;   // Кл — заряд електрона
    const double mu   = 1350.0;      // см²/(В·с) — рухливість електронів
    const double Ec   = 0.30e6;      // В/см — критичне поле кремнію

    double BV = 600.0;               // В — потрібна пробійна напруга

    double d  = 2.0 * BV / Ec;                 // товщина шару, см
    double Nd = eps * Ec * Ec / (2.0 * q * BV);// легування, см^-3
    double sigma = q * mu * Nd;                // провідність, (Ом·см)^-1
    double ronA  = d / sigma;                  // Ом·см²

    std::printf("d    = %.1f мкм\n", d * 1e4);
    std::printf("Nd   = %.3e см^-3\n", Nd);
    std::printf("rho  = %.1f Ом·см\n", 1.0 / sigma);
    std::printf("Ron*A(формула) = %.4f Ом·см²\n", 4.0*BV*BV/(mu*eps*Ec*Ec*Ec));
    std::printf("Ron*A(d/sigma) = %.4f Ом·см²\n", ronA);
    return 0;
}
