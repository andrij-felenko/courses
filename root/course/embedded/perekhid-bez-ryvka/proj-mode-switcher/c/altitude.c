#include "altitude.h"

#include <math.h>

void alt_filter_init(alt_filter_t *f, float k_alt, float k_climb)
{
    f->alt = 0.0f;
    f->climb = 0.0f;
    f->k_alt = k_alt;
    f->k_climb = k_climb;
    f->spike_limit = 15.0f;
    f->primed = false;
    f->rejected = 0;
}

void alt_filter_update(alt_filter_t *f, float baro_alt, float acc_up, float dt)
{
    if (!(dt > 0.0f)) return;

    if (!f->primed) {
        /* Перший придатний відлік барометра задає початок відліку. */
        if (isfinite(baro_alt)) {
            f->alt = baro_alt;
            f->climb = 0.0f;
            f->primed = true;
        }
        return;
    }

    const float a = isfinite(acc_up) ? acc_up : 0.0f;

    /* Прогноз за акселерометром */
    f->alt += f->climb * dt + 0.5f * a * dt * dt;
    f->climb += a * dt;

    /* Корекція за барометром */
    if (!isfinite(baro_alt)) return;
    if (fabsf(baro_alt - f->alt) > f->spike_limit) {
        /* Стрибок на десятки метрів за такт — це не політ, а поштовх
           тиску (відкрили ліхтар, порив у трубку). Такий відлік геть. */
        f->rejected++;
        return;
    }
    const float err = baro_alt - f->alt;
    f->alt   += f->k_alt   * err * dt;
    f->climb += f->k_climb * err * dt;
}

float alt_filter_altitude(const alt_filter_t *f) { return f->alt; }
float alt_filter_climb(const alt_filter_t *f)    { return f->climb; }
