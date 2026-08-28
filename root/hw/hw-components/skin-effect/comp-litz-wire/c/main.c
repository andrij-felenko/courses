// Очікуваний опір ліцендрат-джгута на постійному струмі, Ом/м.
// N жилок увімкнено паралельно -> опір джгута = опір однієї жилки / N.
// Якщо вимір помітно вищий за розрахунок — пропаялися не всі жилки.
#include <stdio.h>

int main(void) {
    int   N           = 100;      // жил у джгуті («100/40»)
    float r_strand_pm = 3.5f;     // опір однієї жилки 40 AWG, Ом/м

    float r_bundle_pm = r_strand_pm / (float)N;   // паралель N жил
    printf("R_dc джгута = %.4f Om/m\n", r_bundle_pm);   // ~0.035 Ом/м

    // приклад перевірки: намотали 4 м, а зміряли 0.28 Ом замість ~0.14
    float len = 4.0f, measured = 0.28f;
    float expected = r_bundle_pm * len;
    printf("очікувано %.3f Om, зміряно %.3f Om -> коеф %.1f\n",
           expected, measured, measured / expected);   // коеф ~2 -> половина жил не в ділі
    return 0;
}
