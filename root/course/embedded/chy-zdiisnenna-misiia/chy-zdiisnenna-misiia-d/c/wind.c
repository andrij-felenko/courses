#include "wind.h"

#include <math.h>

#include "geo.h"

float wind_at_height(const WindProfile *profile, float height_agl_m)
{
    if (profile->ref_height_m <= 0.0f) {
        return profile->speed_mps;   /* висота виміру невідома — беремо як є */
    }

    /* Нижче анемометра степеневий закон не екстраполюємо: біля самої землі
       він дає нереально малий вітер, а це небезпечний оптимізм. */
    float z = height_agl_m;
    if (z < profile->ref_height_m) {
        z = profile->ref_height_m;
    }

    return profile->speed_mps * powf(z / profile->ref_height_m, profile->roughness_alpha);
}

bool wind_solve_leg(const WindProfile *profile,
                    float track_deg,
                    float height_agl_m,
                    float airspeed_mps,
                    LegWind *out)
{
    if (!isfinite(airspeed_mps) || airspeed_mps < 0.5f) {
        return false;
    }

    const float w = wind_at_height(profile, height_agl_m);
    const float rel_rad = (float)((double)(profile->from_deg - track_deg) * GEO_DEG_TO_RAD);

    out->speed_mps = w;
    /* from_deg — звідки дме, тому вектор руху повітря має протилежний знак:
       вітер строго в лоб (from_deg == track_deg) дає along < 0. */
    out->along_mps = -w * cosf(rel_rad);
    out->cross_mps = -w * sinf(rel_rad);

    /* v_air * sin(beta) + w_cross = 0 — ніс довертаємо проти зносу. */
    const float sin_beta = -out->cross_mps / airspeed_mps;
    if (fabsf(sin_beta) >= 1.0f) {
        out->crab_deg = 0.0f;
        out->ground_speed_mps = 0.0f;
        return false;
    }

    const float cos_beta = sqrtf(1.0f - sin_beta * sin_beta);
    out->crab_deg = (float)(asinf(sin_beta) * GEO_RAD_TO_DEG);
    out->ground_speed_mps = airspeed_mps * cos_beta + out->along_mps;
    return true;
}
