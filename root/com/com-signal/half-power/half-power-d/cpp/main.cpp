#include <cmath>

/* Частота зрізу (−3 дБ) RC-фільтра нижніх частот, Гц.
   R — опір в омах, C — ємність у фарадах. */
float rc_cutoff_hz(float r_ohm, float c_farad)
{
    if (r_ohm <= 0.0f || c_farad <= 0.0f) {
        return 0.0f;            /* некоректні дані — межі немає */
    }
    return 1.0f / (2.0f * static_cast<float>(M_PI) * r_ohm * c_farad);
}
