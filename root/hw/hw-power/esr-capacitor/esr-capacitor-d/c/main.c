// Скільки тепла народжує пульсівний струм на ESR конденсатора.
// I_rms — діюче значення пульсації, А; esr — еквівалентний послідовний опір, Ом.
#include <stdio.h>

float ripple_heat(float i_rms, float esr) {
    return i_rms * i_rms * esr;     // P = I² · ESR, Вт
}

int main(void) {
    float i = 2.0f;                          // пульсівний струм 2 А (rms)
    printf("ESR=0.50: P = %.2f W\n", ripple_heat(i, 0.50f));  // звичайний електроліт
    printf("ESR=0.02: P = %.2f W\n", ripple_heat(i, 0.02f));  // low-ESR
    return 0;
}
