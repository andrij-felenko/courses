// У скільки разів скін-ефект підіймає опір круглого проводу на частоті f.
// Порівнюємо повний переріз πr² з робочим кільцем завтовшки δ (площа ≈ 2πrδ).
#include <stdio.h>
#include <math.h>

// Глибина проникнення для міді, м; f — частота, Гц.
float skin_depth_cu(float f) {
    const float rho = 1.68e-8f;   // питомий опір міді, Ом·м
    const float mu0 = 1.256637e-6f; // магнітна стала (мідь немагнітна), Гн/м
    float w = 2.0f * (float)M_PI * f;
    return sqrtf(2.0f * rho / (w * mu0));
}

int main(void) {
    float r = 5.0e-3f;            // радіус шини 5 мм
    float f = 1.0e6f;            // 1 МГц
    float d = skin_depth_cu(f);  // глибина проникнення

    float area_dc = (float)M_PI * r * r;   // повний переріз
    float area_ac = 2.0f * (float)M_PI * r * d; // робоче кільце ≈ окружність × δ
    printf("delta = %.1f um\n", d * 1e6f);
    printf("R_ac / R_dc ≈ %.0f\n", area_dc / area_ac); // у стільки разів опір вищий
    return 0;
}
