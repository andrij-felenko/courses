#include <math.h>
#include <stdio.h>

// Кремнієва межа: Ron·A [Ом·см²] = 8.3e-9 · BV^2.5
double si_ron_a(double bv_volts) {
    return 8.3e-9 * pow(bv_volts, 2.5);   // Ом·см²
}

int main(void) {
    double BV      = 600.0;      // робоча напруга, В
    double Rds_max = 0.050;      // бажаний опір, Ом (50 мОм)

    double ronA_si = si_ron_a(BV);          // Ом·см² на межі кремнію
    double area_si = ronA_si / Rds_max;     // потрібна площа: A = Ron·A / R
    printf("Si: Ron*A = %.4f Ом*см^2,  площа = %.3f см^2\n", ronA_si, area_si);

    // SiC: приблизно у 340 разів менший питомий опір -> у 340 разів менша площа
    double ronA_sic = ronA_si / 340.0;
    double area_sic = ronA_sic / Rds_max;
    printf("SiC: Ron*A = %.5f Ом*см^2, площа = %.4f см^2\n", ronA_sic, area_sic);

    printf("Виграш за площею: %.0fx\n", area_si / area_sic);
    return 0;
}
