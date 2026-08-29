#include "flow.h"

#include "ekf_dr.h"

#include <math.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

void flow_init(flow_cfg_t *cfg)
{
    memset(cfg, 0, sizeof(*cfg));

    /* 42° поля зору на 35 пікселів матриці PMW3901. */
    cfg->rad_per_pixel = (float)(42.0 * M_PI / 180.0 / 35.0);
    cfg->squal_min = 30;
    cfg->squal_ref = 100;
    cfg->max_rate = 7.0f;          /* рад/с — понад це кадр гарантовано змазаний */
    cfg->min_range = 0.08f;
    cfg->max_range = 8.0f;
    cfg->min_tilt_cos = 0.70f;     /* нахил до ≈45° */
    cfg->r_base = 0.02f;
}

bool flow_measure(flow_cfg_t *cfg,
                  int16_t dpx, int16_t dpy, uint8_t squal, float dt,
                  const float gyro[3], const float R_wb[3][3], float range_m,
                  flow_meas_t *out)
{
    if (!(dt > 0.0f) || dt > 0.5f) return false;
    if (!ekf_vec3_finite(gyro) || !ekf_is_rotation(R_wb, 1.0e-2f)) return false;
    if (!isfinite(range_m)) return false;

    if (squal < cfg->squal_min) {          /* поверхня без текстури або темрява */
        cfg->n_quality++;
        return false;
    }

    /* Нахил: далекомір міряє вздовж осі тіла Z, а нам потрібна відстань по
       нормалі до поверхні. R_wb[2][2] — це косинус кута між віссю тіла Z і
       світовою «вниз», тобто якраз потрібний множник. */
    const float tilt_cos = R_wb[2][2];
    if (!(tilt_cos > cfg->min_tilt_cos)) {
        cfg->n_tilt++;
        return false;
    }

    const float range = range_m * tilt_cos;
    if (!(range > cfg->min_range) || range > cfg->max_range) {
        cfg->n_range++;
        return false;
    }

    /* Кутова швидкість потоку, рад/с. */
    const float w_flow_x = (float)dpx * cfg->rad_per_pixel / dt;
    const float w_flow_y = (float)dpy * cfg->rad_per_pixel / dt;

    /* ── Деротація ──
       Сенсор дивиться вниз, осі його матриці збігаються з осями тіла X/Y.
       Тангаж (обертання навколо осі тіла Y, швидкість gyro[1]) зсуває кадр
       уздовж X так само, як політ уперед; крен (навколо X, gyro[0]) зсуває
       кадр уздовж Y, але з протилежним знаком. Віднімання цих складових і
       лишає в потоці саме поступальний рух. */
    const float w_lin_x = w_flow_x - gyro[1];
    const float w_lin_y = w_flow_y + gyro[0];

    if (fabsf(w_lin_x) > cfg->max_rate || fabsf(w_lin_y) > cfg->max_rate) {
        cfg->n_rate++;
        return false;
    }

    /* Кутова швидкість × дальність = лінійна швидкість у системі тіла.
       Вертикальну складову беремо нульовою: потік про неї нічого не знає.
       Через це поворот у світ вносить похибку близько v_z·sin(нахилу) —
       на малих кутах вона тоне в шумі самого сенсора, і саме тому строб
       Махаланобіса тут потрібен навіть для «чистих» кадрів. */
    const float v_body[3] = {w_lin_x * range, w_lin_y * range, 0.0f};

    float v_world[3];
    ekf_rotate(v_world, R_wb, v_body);

    /* Дисперсія росте з дальністю (множник входить у швидкість) і з падінням
       якості поверхні (шум пікселів росте швидше за лінійний закон). */
    const float q = (float)(squal > 0 ? squal : 1);
    const float quality_factor = ((float)cfg->squal_ref / q) * ((float)cfg->squal_ref / q);

    out->vx_world = v_world[0];
    out->vy_world = v_world[1];
    out->range_used = range;
    out->r_cov = cfg->r_base * (1.0f + range * range) * quality_factor;

    return isfinite(out->vx_world) && isfinite(out->vy_world) && isfinite(out->r_cov);
}
