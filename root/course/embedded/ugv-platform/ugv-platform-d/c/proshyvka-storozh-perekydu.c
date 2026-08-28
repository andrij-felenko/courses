#include <math.h>

// Геометрія машини (виміряти для конкретного шасі)
#define HALF_TRACK_M   0.15f   // пів-колії b, м
#define CM_HEIGHT_M    0.12f   // висота центра мас h, м
#define TIP_MARGIN     0.70f   // працюємо лише до 70% критичного кута

// Критичний кут перекиду (радіани), рахуємо раз при старті
static float tip_angle_lat;    // бічний
static float tip_angle_lon;    // поздовжній (тут для прикладу — той самий b)

void tipguard_init(void) {
    tip_angle_lat = atanf(HALF_TRACK_M / CM_HEIGHT_M);   // arctan(b/h)
    tip_angle_lon = tip_angle_lat;                        // спрощено
}

// roll, pitch — крен і тангаж від IMU (радіани).
// Повертає множник 0..1, на який треба помножити КЕРУВАННЯ.
// Що ближче нахил до межі, то менший множник; за межею — 0.
static float tipguard_scale(float roll, float pitch) {
    // наскільки «вибрали» бічний і поздовжній запас (0 — рівне, 1 — на межі)
    float use_lat = fabsf(roll)  / (tip_angle_lat * TIP_MARGIN);
    float use_lon = fabsf(pitch) / (tip_angle_lon * TIP_MARGIN);
    float use = use_lat > use_lon ? use_lat : use_lon;   // гірший із двох

    if (use <= 0.5f) return 1.0f;          // спокійна зона — не чіпаємо
    if (use >= 1.0f) return 0.0f;          // на межі — глушимо повністю
    // між 0.5 і 1.0 — лінійно від 1 до 0
    return 1.0f - (use - 0.5f) / 0.5f;
}

// Обгортка над драйвером шасі: спершу сторож, тоді змішування.
void chassis_drive_guarded(int throttle, int steer,
                           float i_total, float roll, float pitch) {
    float k = tipguard_scale(roll, pitch);
    // поворот душимо СИЛЬНІШЕ за газ: на схилі саме він перекидає боком
    int thr_safe = (int)(throttle * k);
    int str_safe = (int)(steer    * k * k);   // квадрат — крутіший спад
    chassis_drive(thr_safe, str_safe, i_total);   // драйвер із базового кроку
}
