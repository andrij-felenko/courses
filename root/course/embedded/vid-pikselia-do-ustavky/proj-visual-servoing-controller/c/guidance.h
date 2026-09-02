#ifndef GUIDANCE_H
#define GUIDANCE_H

#include <stdbool.h>
#include <stdint.h>

#include "kalman.h"
#include "pid.h"

/* Внутрішні параметри камери (модель камери-обскури, дисторсія знята
 * заздалегідь у драйвері зображення). */
typedef struct {
    float fx;
    float fy;
    float cx;
    float cy;
    float img_width;
    float img_height;
} CameraIntrinsics;

/* Одна детекція: центр і розміри обмежувальної рамки в пікселях плюс
 * АПАРАТНА мітка часу початку експозиції кадру (CLOCK_MONOTONIC, мкс).
 * Мітка обов'язкова: без неї затримку в 110 мс нічим компенсувати. */
typedef struct {
    float    u;
    float    v;
    float    width;
    float    height;
    uint64_t t_capture_us;
} TargetDetection;

/* Уставки для автопілота. */
typedef struct {
    float yaw_rate_rad_s;
    float pitch_rate_rad_s;
    float forward_vel_m_s;
    bool  target_acquired;
} GuidanceSetpoints;

/* Історія ракурсу апарата. Кадр приходить із запізненням, а гіроскоп
 * інтегрується безперервно, тож на момент експозиції ракурс треба ДІСТАТИ
 * з минулого. 128 записів на 100 Гц — 1.28 с, із запасом на затримку. */
#define EGO_HISTORY_LEN 128u

typedef struct {
    uint64_t t_us;
    float    yaw;
    float    pitch;
} EgoSample;

typedef struct {
    CameraIntrinsics cam;
    KalmanAxis  kf_yaw;
    KalmanAxis  kf_pitch;
    ServoingPid pid_yaw;
    ServoingPid pid_pitch;
    ServoingPid pid_forward;

    EgoSample ego[EGO_HISTORY_LEN];
    unsigned  ego_head;
    unsigned  ego_count;

    float    desired_scale_px;   /* бажаний розмір рамки √(w·h) */
    float    scale_px;           /* згладжений поточний розмір рамки */
    uint64_t last_frame_us;      /* мітка експозиції останнього кадру */
    uint64_t last_tick_us;       /* час останнього кроку контуру */
    bool     tracking;
    unsigned frames_used;
    unsigned frames_rejected;
} VisualGuidance;

void visual_guidance_init(VisualGuidance *g, const CameraIntrinsics *cam);

/* Асинхронний вхід: новий кадр від детектора (20–30 Гц). */
void visual_guidance_on_detection(VisualGuidance *g, const TargetDetection *det);

/* Синхронний вхід: крок контуру керування (100–250 Гц). */
void visual_guidance_update(VisualGuidance *g, uint64_t now_us,
                            float gyro_yaw_rad_s, float gyro_pitch_rad_s,
                            GuidanceSetpoints *out);

#endif /* GUIDANCE_H */
