#include "guidance.h"

#include <math.h>
#include <string.h>

/* Довше за це без кадру — супровід утрачено, уставки в нуль. */
#define TRACK_TIMEOUT_S 0.5f

/* Випередження на запізнення внутрішнього контуру стабілізації: поки уставка
 * пройде мікшер і приводи, ціль устигає трохи зміститися. */
#define ACTUATOR_LEAD_S 0.03f

/* Максимальна довіра до мітки часу кадру. Більше — годинник детектора поїхав. */
#define MAX_FRAME_AGE_S 0.5f

static float clampf(float v, float lo, float hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

static void ego_push(VisualGuidance *g, uint64_t t_us, float yaw, float pitch)
{
    g->ego[g->ego_head].t_us = t_us;
    g->ego[g->ego_head].yaw = yaw;
    g->ego[g->ego_head].pitch = pitch;
    g->ego_head = (g->ego_head + 1u) % EGO_HISTORY_LEN;
    if (g->ego_count < EGO_HISTORY_LEN) {
        g->ego_count++;
    }
}

/* Ракурс апарата на момент t_us — лінійною інтерполяцією між сусідніми
 * записами. false означає, що кадр старіший за всю історію: беремо найдавніший
 * запис, але викликач знає, що компенсація неповна. */
static bool ego_lookup(const VisualGuidance *g, uint64_t t_us, float *yaw, float *pitch)
{
    if (g->ego_count == 0u) {
        *yaw = 0.0f;
        *pitch = 0.0f;
        return false;
    }

    const EgoSample *newer = NULL;
    for (unsigned i = 1u; i <= g->ego_count; ++i) {
        const unsigned idx = (g->ego_head + EGO_HISTORY_LEN - i) % EGO_HISTORY_LEN;
        const EgoSample *s = &g->ego[idx];
        if (s->t_us <= t_us) {
            if (newer != NULL && newer->t_us > s->t_us) {
                const float a = (float)(t_us - s->t_us) / (float)(newer->t_us - s->t_us);
                *yaw = s->yaw + a * (newer->yaw - s->yaw);
                *pitch = s->pitch + a * (newer->pitch - s->pitch);
            } else {
                *yaw = s->yaw;
                *pitch = s->pitch;
            }
            return true;
        }
        newer = s;
    }

    *yaw = newer->yaw;      /* найдавніший запис в історії */
    *pitch = newer->pitch;
    return false;
}

void visual_guidance_init(VisualGuidance *g, const CameraIntrinsics *cam)
{
    memset(g, 0, sizeof(*g));
    g->cam = *cam;

    /* q_rate задає, наскільки жваво фільтр вірить у маневр цілі; r_meas —
     * дисперсія детектора: ≈1.2 пікселя при fx = 800 це (1.5e-3 рад)². */
    kalman_axis_init(&g->kf_yaw, 1e-3f, 2.0f, 2.3e-6f);
    kalman_axis_init(&g->kf_pitch, 1e-3f, 2.0f, 2.3e-6f);

    /* Кутові швидкості обмежені: рискання 1.0 рад/с, тангаж 0.8 рад/с. */
    pid_init(&g->pid_yaw,     1.8f,  0.10f,  0.15f,  1.0f, 0.30f, 0.008f);
    pid_init(&g->pid_pitch,   1.8f,  0.10f,  0.15f,  0.8f, 0.20f, 0.008f);
    /* Поздовжній канал працює в пікселях розміру рамки, звідси дрібні коефіцієнти. */
    pid_init(&g->pid_forward, 0.02f, 0.001f, 0.005f, 3.0f, 0.50f, 2.0f);

    g->desired_scale_px = 80.0f;
}

void visual_guidance_on_detection(VisualGuidance *g, const TargetDetection *det)
{
    /* Кадр без часу порівнювати немає з чим, а поза межами матриці — це збій
     * детектора, не ціль. */
    if (det->t_capture_us == 0u ||
        !isfinite(det->u) || !isfinite(det->v) ||
        !(det->width > 1.0f) || !(det->height > 1.0f) ||
        det->u < 0.0f || det->u > g->cam.img_width ||
        det->v < 0.0f || det->v > g->cam.img_height) {
        g->frames_rejected++;
        return;
    }

    /* Кадр із майбутнього або старший за півсекунди — годинники розійшлися. */
    if (g->last_tick_us != 0u) {
        if (det->t_capture_us > g->last_tick_us) {
            g->frames_rejected++;
            return;
        }
        const float age_s = (float)(g->last_tick_us - det->t_capture_us) * 1e-6f;
        if (age_s > MAX_FRAME_AGE_S) {
            g->frames_rejected++;
            return;
        }
    }

    /* Дубль тієї самої мітки часу (черга віддала кадр двічі) не несе інформації. */
    if (g->tracking && det->t_capture_us <= g->last_frame_us) {
        g->frames_rejected++;
        return;
    }

    /* Рівень геометричної нормалізації: піксель → кут. Ділення на фокусну
     * відстань дає тангенс кута, arctan повертає сам кут — на краю кадру
     * різниця між ними вже помітна. */
    const float norm_x = (det->u - g->cam.cx) / g->cam.fx;
    const float norm_y = (det->v - g->cam.cy) / g->cam.fy;
    const float los_yaw = atanf(norm_x);
    const float los_pitch = atanf(norm_y);

    float ego_yaw = 0.0f;
    float ego_pitch = 0.0f;
    ego_lookup(g, det->t_capture_us, &ego_yaw, &ego_pitch);

    if (!g->tracking) {
        /* Захоплення: фільтри засіваються цим кадром, регулятори стартують
         * із нуля — інакше в них лишається інтеграл із минулого супроводу. */
        kalman_axis_acquire(&g->kf_yaw);
        kalman_axis_acquire(&g->kf_pitch);
        pid_reset(&g->pid_yaw);
        pid_reset(&g->pid_pitch);
        pid_reset(&g->pid_forward);
        g->scale_px = sqrtf(det->width * det->height);
        g->tracking = true;
    }

    float latency_s = 0.0f;
    if (g->last_tick_us > det->t_capture_us) {
        latency_s = (float)(g->last_tick_us - det->t_capture_us) * 1e-6f;
    }

    const bool ok_yaw = kalman_axis_update(&g->kf_yaw, los_yaw, ego_yaw, latency_s);
    const bool ok_pitch = kalman_axis_update(&g->kf_pitch, los_pitch, ego_pitch, latency_s);

    if (!ok_yaw && !ok_pitch) {
        /* Обидві осі відкинув гейт — це чужий об'єкт, а не наша ціль:
         * ні розміру, ні мітки часу з нього не беремо. */
        g->frames_rejected++;
        return;
    }

    /* Розмір рамки шумить сильніше за центр (краї об'єкта «дихають»),
     * тому в поздовжній канал він іде згладженим. */
    const float scale = sqrtf(det->width * det->height);
    g->scale_px += 0.3f * (scale - g->scale_px);

    g->last_frame_us = det->t_capture_us;
    g->frames_used++;
}

void visual_guidance_update(VisualGuidance *g, uint64_t now_us,
                            float gyro_yaw_rad_s, float gyro_pitch_rad_s,
                            GuidanceSetpoints *out)
{
    out->yaw_rate_rad_s = 0.0f;
    out->pitch_rate_rad_s = 0.0f;
    out->forward_vel_m_s = 0.0f;
    out->target_acquired = false;

    if (g->last_tick_us == 0u || now_us <= g->last_tick_us) {
        /* Перший крок або годинник не зрушив: dt немає, керувати немає з чого. */
        g->last_tick_us = now_us;
        ego_push(g, now_us, kalman_axis_body_angle(&g->kf_yaw),
                 kalman_axis_body_angle(&g->kf_pitch));
        return;
    }

    const float dt = clampf((float)(now_us - g->last_tick_us) * 1e-6f, 0.0f, 0.5f);
    g->last_tick_us = now_us;

    /* 1. Прогноз і інтегрування гіроскопів — незалежно від того, чи є ціль:
     * історія ракурсу має бути суцільною ще до першого кадру. */
    kalman_axis_predict(&g->kf_yaw, dt, gyro_yaw_rad_s);
    kalman_axis_predict(&g->kf_pitch, dt, gyro_pitch_rad_s);
    ego_push(g, now_us, kalman_axis_body_angle(&g->kf_yaw),
             kalman_axis_body_angle(&g->kf_pitch));

    if (!g->tracking) {
        return;
    }

    /* 2. Повна транспортна затримка: від експозиції матриці до цієї миті. */
    const float latency_s = (float)(now_us - g->last_frame_us) * 1e-6f;
    if (latency_s > TRACK_TIMEOUT_S) {
        /* Кадри скінчилися. Далі екстраполяція розганяла б апарат за
         * вигаданою ціллю, тож супровід закриваємо й зависаємо. */
        g->tracking = false;
        pid_reset(&g->pid_yaw);
        pid_reset(&g->pid_pitch);
        pid_reset(&g->pid_forward);
        return;
    }

    /* 3. Екстраполяція: стан фільтра вже приведено до «тепер» фазою predict,
     * тут додається лише випередження на запізнення приводів. */
    const float los_yaw = kalman_axis_extrapolate(&g->kf_yaw, ACTUATOR_LEAD_S);
    const float los_pitch = kalman_axis_extrapolate(&g->kf_pitch, ACTUATOR_LEAD_S);

    /* 4. Регулятори тримають кут візування на нулі — ціль у центрі кадру.
     * Знак рискання інвертовано: додатна кутова швидкість повертає апарат
     * праворуч, а це ЗМЕНШУЄ кут візування на ціль, що праворуч. */
    out->yaw_rate_rad_s = -pid_update(&g->pid_yaw, 0.0f, los_yaw, dt);
    /* Тангаж: ціль нижче центра (додатний los_pitch) вимагає опустити ніс,
     * а це від'ємна кутова швидкість тангажу — вихід регулятора вже такий. */
    out->pitch_rate_rad_s = pid_update(&g->pid_pitch, 0.0f, los_pitch, dt);

    /* 5. Дальність — за видимим розміром цілі. Рамка менша за 5 пікселів
     * означає, що детектор чіпляється за шум; поздовжній канал мовчить. */
    if (g->scale_px > 5.0f) {
        out->forward_vel_m_s = pid_update(&g->pid_forward, g->desired_scale_px,
                                          g->scale_px, dt);
    }

    out->target_acquired = true;
}
