#include <stdio.h>
#include <math.h>

// Залишкова напруга на опорі витоку З кільцем — сума двох джерел:
//   vos   — напруга зсуву ОП (В), стала, від сигналу не залежить
//   vsig  — розмах сигналу на вході (В)
//   aol   — власне підсилення ОП на робочій частоті (рази, без зворотного зв'язку)
// Похибка повторювача = vsig/aol (вихід не точно дорівнює входу через скінченне aol).
static float v_residual(float vos, float vsig, float aol) {
    return vos + vsig / aol;          // плаский зсув + пропорційна сигналу похибка
}

// Коефіцієнт пригнічення guard = повна різниця / залишкова напруга.
// ОПІР ВИТОКУ ТУТ НЕ ПОТРІБЕН — він скорочується у відношенні струмів.
static float guard_suppression(float dv_full, float vos, float vsig, float aol) {
    return dv_full / v_residual(vos, vsig, aol);
}

// Залишковий струм витоку З кільцем (А) — ось тут опір уже потрібен.
static float leak_residual(float vos, float vsig, float aol, float r_leak) {
    return v_residual(vos, vsig, aol) / r_leak;
}

int main(void) {
    // Типовий високоомний вхід:
    float dv_full = 4.9f;     // повна різниця без кільця (5 В сусід − 0.1 В вхід)
    float vos     = 2.0e-3f;  // зсув ОП: 2 мВ
    float vsig    = 0.1f;     // сигнал на вході: 0.1 В
    float r_leak  = 1.0e9f;   // опір витоку по вологій поверхні: 1 ГОм

    // Сценарій А: постійний струм, велике підсилення (aol = 100000)
    float aolA = 1.0e5f;
    float vresA = v_residual(vos, vsig, aolA);
    float gA    = guard_suppression(dv_full, vos, vsig, aolA);
    float iA    = leak_residual(vos, vsig, aolA, r_leak);

    // Сценарій Б: висока частота, підсилення просіло (aol = 1000), сигнал на повну шкалу
    float aolB = 1.0e3f;
    float vsigB = 5.0f;       // 5 В розмаху
    float vresB = v_residual(vos, vsigB, aolB);
    float gB    = guard_suppression(dv_full, vos, vsigB, aolB);

    printf("А (DC, Aol=1e5): Vзалишк = %.3f мВ, пригнічення = %.0f разів, витік = %.2f пА\n",
           vresA * 1e3f, gA, iA * 1e12f);
    printf("   (зсув домінує: похибка підсилення лише %.3f мкВ)\n",
           (vsig / aolA) * 1e6f);
    printf("Б (ВЧ, Aol=1e3, сигнал 5В): Vзалишк = %.2f мВ, пригнічення = %.0f разів\n",
           vresB * 1e3f, gB);
    printf("   (тепер домінує похибка підсилення: %.2f мВ проти зсуву %.1f мВ)\n",
           (vsigB / aolB) * 1e3f, vos * 1e3f);
    return 0;
}
