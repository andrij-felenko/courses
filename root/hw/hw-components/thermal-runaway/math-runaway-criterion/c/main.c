// Критичний тепловий опір для теплового розгону.
// Беремо ефективну чутливість каскаду 0.6 %/°C (як у наскрізному прикладі теми).
#include <stdio.h>

int main(void) {
    const float Vce = 10.0f;      // напруга колектор–емітер, В
    const float Ic  = 0.100f;     // струм спокою, А
    const float tc  = 0.006f;     // ефективна чутливість, частка струму на °C

    float dIc_dTj  = tc * Ic;             // чутливість струму, А/°C → 0.6 мА/°C
    float Rth_crit = 1.0f / (Vce * dIc_dTj);

    printf("dIc/dTj  = %.4f A/C\n", dIc_dTj);   // 0.0006 A/C
    printf("Rth_crit = %.0f C/W\n", Rth_crit);  // ~167 C/W
    return 0;
}
