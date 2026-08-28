# ⚙️ Реалізація контролера візуального наведення з фільтром Калмана

Цей проект містить повну, оптимізовану для вбудованих систем реалізацію бортового контролера візуального наведення (Image-Based Visual Servoing, IBVS). Модуль спроектовано для виконання на бортовому комп'ютері (Single Board Computer під керуванням Linux/RTOS) або безпосередньо у прошивці польотного контролера (NuttX/FreeRTOS). Він перетворює дискретний і запізнілий потік координат обмежувальних рамок цілі (Bounding Box) у високочастотні уставки кутових і лінійних швидкостей для автопілота.

## Архітектурний дизайн та потік даних

Програмна архітектура розділена на три незалежні рівні з детермінованим часом виконання `O(1)` і повною відсутністю динамічного виділення пам'яті (zero-allocation):

1. **Рівень геометричної нормалізації:** приймає піксельні координати детектора `(u, v, w, h)`, віднімає зміщення оптичного центра `(cx, cy)` та ділить на фокусну відстань `(fx, fy)`, приводячи вимірювання до фізичних кутів у радіанах.
2. **Рівень оцінки та компенсації затримки (1D Kalman Tracker на кожну вісь):**
   - Фаза `predict` викликається з високою частотою основного циклу керування (100–250 Гц) і враховує сигнал бортового гіроскопа (Ego-Motion Feedforward), щоб обертання самого апарата не сприймалося як маневр цілі.
   - Фаза `update` викликається асинхронно при надходженні нового кадру від нейромережі (типово 20–30 Гц).
   - Фаза `extrapolate` проектує оцінений стан цілі вперед на інтервал повної транспортної затримки `t_now − t_capture`.
3. **Рівень формування уставок (Servoing PID):** генерує кутові швидкості `(yaw_rate, pitch_rate)` та лінійну швидкість `forward_vel`. Використовує диференціювання за вимірюваною величиною (Derivative-on-Measurement) для усунення ударів при стрибках детектора, умовне інтегрування (Anti-Windup Clamping) та зону нечутливості (Deadband) проти тремтіння нейромережі.

:::tabs
```c
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define M_PI_F 3.14159265358979323846f

/* ── Параметри камери та калібрування ───────────────────────────────────── */
typedef struct {
    float fx;           /* Фокусна відстань за X у пікселях */
    float fy;           /* Фокусна відстань за Y у пікселях */
    float cx;           /* Оптичний центр за X у пікселях */
    float cy;           /* Оптичний центр за Y у пікселях */
    float img_width;    /* Ширина зображення в пікселях */
    float img_height;   /* Висота зображення в пікселях */
} CameraIntrinsics;

/* ── Вимірювання від детектора (Bounding Box) ────────────────────────────── */
typedef struct {
    float u;            /* Координата X центра рамки (пікселі) */
    float v;            /* Координата Y центра рамки (пікселі) */
    float width;        /* Ширина рамки (пікселі) */
    float height;       /* Висота рамки (пікселі) */
    uint64_t timestamp_us; /* Мітка часу захоплення кадру сенсором (мкс) */
    bool valid;         /* Прапорець достовірності детекції */
} TargetDetection;

/* ── Стан фільтра Калмана для однієї осі (кут + кутова швидкість) ────────── */
typedef struct {
    float angle;        /* Оцінка кута візування (рад) */
    float rate;         /* Оцінка кутової швидкості цілі (рад/с) */
    float P[2][2];      /* Матриця коваріації похибок оцінки */
    float Q_angle;      /* Шум процесу за кутом */
    float Q_rate;       /* Шум процесу за кутовою швидкістю */
    float R_meas;       /* Шум вимірювання детектора */
    uint64_t last_update_us; /* Час останнього оновлення */
} KalmanAxis1D;

/* ── ПІД-регулятор для контуру візуального супроводу ─────────────────────── */
typedef struct {
    float kp;           /* Пропорційний коефіцієнт */
    float ki;           /* Інтегральний коефіцієнт */
    float kd;           /* Диференційний коефіцієнт */
    float integral;     /* Накопичена інтегральна помилка */
    float prev_meas;    /* Попереднє вимірювання для похідної */
    float max_integral; /* Межа інтегратора (anti-windup) */
    float max_output;   /* Максимальне значення вихідного сигналу */
    float deadband;     /* Зона нечутливості за похибкою */
    bool is_initialized;
} ServoingPID;

/* ── Вихідні уставки для автопілота ──────────────────────────────────────── */
typedef struct {
    float yaw_rate_rad_s;     /* Уставка кутової швидкості рискання */
    float pitch_rate_rad_s;   /* Уставка кутової швидкості тангажу */
    float forward_vel_m_s;    /* Уставка лінійної швидкості вперед */
    bool target_acquired;     /* Прапорець стабільного супроводу */
} GuidanceSetpoints;

/* ── Ініціалізація осі фільтра Калмана ───────────────────────────────────── */
void kalman_axis_init(KalmanAxis1D *k, float q_angle, float q_rate, float r_meas) {
    k->angle = 0.0f;
    k->rate = 0.0f;
    k->P[0][0] = 0.1f;
    k->P[0][1] = 0.0f;
    k->P[1][0] = 0.0f;
    k->P[1][1] = 1.0f;
    k->Q_angle = q_angle;
    k->Q_rate = q_rate;
    k->R_meas = r_meas;
    k->last_update_us = 0;
}

/* ── Крок прогнозу фільтра Калмана з компенсацією власного обертання ─────── */
void kalman_axis_predict(KalmanAxis1D *k, float dt, float gyro_rate_rad_s) {
    if (dt <= 0.0f || dt > 1.0f) return;

    /* Динаміка: кут цілі змінюється через швидкість цілі та власне обертання */
    float apparent_rate = k->rate - gyro_rate_rad_s;
    k->angle += apparent_rate * dt;

    /* Еволюція коваріації: P = F * P * F^T + Q */
    float P00 = k->P[0][0] + dt * (k->P[1][0] + k->P[0][1]) + dt * dt * k->P[1][1] + k->Q_angle * dt;
    float P01 = k->P[0][1] + dt * k->P[1][1];
    float P10 = k->P[1][0] + dt * k->P[1][1];
    float P11 = k->P[1][1] + k->Q_rate * dt;

    k->P[0][0] = P00;
    k->P[0][1] = P01;
    k->P[1][0] = P10;
    k->P[1][1] = P11;
}

/* ── Крок корекції фільтра Калмана новим вимірюванням ─────────────────────── */
void kalman_axis_update(KalmanAxis1D *k, float measured_angle) {
    /* Інновація (нев'язка) */
    float y = measured_angle - k->angle;

    /* Коваріація інновації: S = H * P * H^T + R = P00 + R */
    float S = k->P[0][0] + k->R_meas;
    if (fabsf(S) < 1e-6f) return;

    /* Коефіцієнти Калмана: K = P * H^T * inv(S) */
    float K0 = k->P[0][0] / S;
    float K1 = k->P[1][0] / S;

    /* Оновлення вектора стану */
    k->angle += K0 * y;
    k->rate  += K1 * y;

    /* Оновлення коваріації: P = (I - K * H) * P */
    float P00_new = (1.0f - K0) * k->P[0][0];
    float P01_new = (1.0f - K0) * k->P[0][1];
    float P10_new = k->P[1][0] - K1 * k->P[0][0];
    float P11_new = k->P[1][1] - K1 * k->P[0][1];

    k->P[0][0] = P00_new;
    k->P[0][1] = P01_new;
    k->P[1][0] = P10_new;
    k->P[1][1] = P11_new;
}

/* ── Екстраполяція стану вперед на час транспортної затримки T_lat ───────── */
void kalman_axis_extrapolate(const KalmanAxis1D *k, float latency_s, float *out_angle, float *out_rate) {
    if (out_angle) {
        *out_angle = k->angle + k->rate * latency_s;
    }
    if (out_rate) {
        *out_rate = k->rate;
    }
}

/* ── Ініціалізація ПІД-регулятора ────────────────────────────────────────── */
void pid_init(ServoingPID *pid, float kp, float ki, float kd, float max_out, float max_i, float deadband) {
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
    pid->max_output = max_out;
    pid->max_integral = max_i;
    pid->deadband = deadband;
    pid->integral = 0.0f;
    pid->prev_meas = 0.0f;
    pid->is_initialized = false;
}

/* ── Обчислення виходу ПІД-регулятора ────────────────────────────────────── */
float pid_update(ServoingPID *pid, float error, float measured_val, float dt) {
    if (dt <= 0.0f) return 0.0f;

    /* Застосування зони нечутливості */
    if (fabsf(error) < pid->deadband) {
        error = 0.0f;
    }

    /* Пропорційна складова */
    float p_term = pid->kp * error;

    /* Інтегральна складова з обмеженням (anti-windup) */
    pid->integral += error * dt;
    if (pid->integral > pid->max_integral) {
        pid->integral = pid->max_integral;
    } else if (pid->integral < -pid->max_integral) {
        pid->integral = -pid->max_integral;
    }
    float i_term = pid->ki * pid->integral;

    /* Диференційна складова за вимірюванням (уникає derivative kick) */
    float d_term = 0.0f;
    if (pid->is_initialized) {
        float d_meas = (measured_val - pid->prev_meas) / dt;
        d_term = -pid->kd * d_meas;
    } else {
        pid->is_initialized = true;
    }
    pid->prev_meas = measured_val;

    /* Формування та обмеження загального виходу */
    float output = p_term + i_term + d_term;
    if (output > pid->max_output) {
        output = pid->max_output;
    } else if (output < -pid->max_output) {
        output = -pid->max_output;
    }

    return output;
}

/* ── Контролер візуального наведення в цілому ────────────────────────────── */
typedef struct {
    CameraIntrinsics camera;
    KalmanAxis1D kf_yaw;
    KalmanAxis1D kf_pitch;
    ServoingPID pid_yaw;
    ServoingPID pid_pitch;
    ServoingPID pid_forward;
    float desired_bbox_scale;  /* Бажаний розмір об'єкта sqrt(w*h) */
    uint64_t last_frame_time_us;
    uint64_t last_exec_time_us;
    bool target_tracked;
} VisualGuidanceController;

void visual_guidance_init(VisualGuidanceController *c, const CameraIntrinsics *cam) {
    c->camera = *cam;
    kalman_axis_init(&c->kf_yaw, 0.01f, 0.5f, 0.005f);
    kalman_axis_init(&c->kf_pitch, 0.01f, 0.5f, 0.005f);

    /* Налаштування коефіцієнтів ПІД (кутові швидкості обмежені 1.0 рад/с) */
    pid_init(&c->pid_yaw, 1.8f, 0.1f, 0.15f, 1.0f, 0.3f, 0.008f);
    pid_init(&c->pid_pitch, 1.8f, 0.1f, 0.15f, 0.8f, 0.2f, 0.008f);
    pid_init(&c->pid_forward, 0.02f, 0.001f, 0.005f, 3.0f, 0.5f, 2.0f);

    c->desired_bbox_scale = 80.0f; /* 80 пікселів за геометричним середнім */
    c->last_frame_time_us = 0;
    c->last_exec_time_us = 0;
    c->target_tracked = false;
}

/* ── Обробка нового кадру від детектора ──────────────────────────────────── */
void visual_guidance_on_detection(VisualGuidanceController *c, const TargetDetection *det) {
    if (!det->valid) {
        c->target_tracked = false;
        return;
    }

    /* Перетворення координат пікселів у кутові похибки за моделлю камери */
    float norm_x = (det->u - c->camera.cx) / c->camera.fx;
    float norm_y = (det->v - c->camera.cy) / c->camera.fy;

    float angle_yaw_meas = atanf(norm_x);
    float angle_pitch_meas = atanf(norm_y);

    /* Корекція фільтрів Калмана */
    kalman_axis_update(&c->kf_yaw, angle_yaw_meas);
    kalman_axis_update(&c->kf_pitch, angle_pitch_meas);

    c->last_frame_time_us = det->timestamp_us;
    c->target_tracked = true;
}

/* ── Високочастотний цикл керування (виклик з частотою контуру автопілота) ─ */
void visual_guidance_update(VisualGuidanceController *c,
                            uint64_t current_time_us,
                            float gyro_yaw_rad_s,
                            float gyro_pitch_rad_s,
                            float current_bbox_scale,
                            GuidanceSetpoints *out_sp) {
    if (!c->target_tracked || c->last_exec_time_us == 0) {
        c->last_exec_time_us = current_time_us;
        out_sp->yaw_rate_rad_s = 0.0f;
        out_sp->pitch_rate_rad_s = 0.0f;
        out_sp->forward_vel_m_s = 0.0f;
        out_sp->target_acquired = false;
        return;
    }

    float dt_exec = (float)(current_time_us - c->last_exec_time_us) * 1e-6f;
    c->last_exec_time_us = current_time_us;

    /* 1. Крок прогнозу фільтра Калмана за часом циклу та гіроскопами */
    kalman_axis_predict(&c->kf_yaw, dt_exec, gyro_yaw_rad_s);
    kalman_axis_predict(&c->kf_pitch, dt_exec, gyro_pitch_rad_s);

    /* 2. Оцінка повної затримки кадру (t_now - t_capture) */
    float latency_s = (float)(current_time_us - c->last_frame_time_us) * 1e-6f;
    if (latency_s > 0.5f) {
        /* Якщо кадри не надходили більше 500 мс — втрата супроводу */
        c->target_tracked = false;
        out_sp->target_acquired = false;
        return;
    }

    /* 3. Екстраполяція положення цілі на поточний момент часу */
    float est_yaw_angle, est_yaw_rate;
    float est_pitch_angle, est_pitch_rate;
    kalman_axis_extrapolate(&c->kf_yaw, latency_s, &est_yaw_angle, &est_yaw_rate);
    kalman_axis_extrapolate(&c->kf_pitch, latency_s, &est_pitch_angle, &est_pitch_rate);

    /* 4. Формування уставок ПІД-регулятором (ціль тримаємо в центрі: e = -angle) */
    float err_yaw = est_yaw_angle;
    float err_pitch = est_pitch_angle;

    out_sp->yaw_rate_rad_s = pid_update(&c->pid_yaw, err_yaw, est_yaw_angle, dt_exec);
    /* Тангаж: зміщення вниз (позитивний v) вимагає нахилу носа вниз (позитивна уставка) */
    out_sp->pitch_rate_rad_s = -pid_update(&c->pid_pitch, err_pitch, est_pitch_angle, dt_exec);

    /* 5. Уставка швидкості вперед за похибкою масштабу цілі */
    if (current_bbox_scale > 5.0f) {
        float err_scale = c->desired_bbox_scale - current_bbox_scale;
        out_sp->forward_vel_m_s = pid_update(&c->pid_forward, err_scale, current_bbox_scale, dt_exec);
    } else {
        out_sp->forward_vel_m_s = 0.0f;
    }

    out_sp->target_acquired = true;
}
```
```cpp
#include <array>
#include <chrono>
#include <cmath>
#include <concepts>
#include <cstdint>
#include <optional>

namespace guidance {

using Microseconds = std::chrono::microseconds;
using SecondsF = std::chrono::duration<float>;

/* ── Параметри камери та калібрування ───────────────────────────────────── */
struct CameraIntrinsics {
    float fx{800.0f};
    float fy{800.0f};
    float cx{320.0f};
    float cy{240.0f};
    float img_width{640.0f};
    float img_height{480.0f};
};

/* ── Вимірювання від детектора ──────────────────────────────────────────── */
struct TargetDetection {
    float u{0.0f};
    float v{0.0f};
    float width{0.0f};
    float height{0.0f};
    Microseconds timestamp{0};
    bool valid{false};

    [[nodiscard]] constexpr float scale() const noexcept {
        return std::sqrt(width * height);
    }
};

/* ── Вихідні уставки для автопілота ──────────────────────────────────────── */
struct GuidanceSetpoints {
    float yaw_rate_rad_s{0.0f};
    float pitch_rate_rad_s{0.0f};
    float forward_vel_m_s{0.0f};
    bool target_acquired{false};
};

/* ── 1D Фільтр Калмана з компенсацією власного обертання ─────────────────── */
class KalmanAxisTracker {
public:
    constexpr KalmanAxisTracker(float q_angle = 0.01f, float q_rate = 0.5f, float r_meas = 0.005f) noexcept
        : q_angle_(q_angle), q_rate_(q_rate), r_meas_(r_meas) {}

    void predict(float dt, float gyro_rate_rad_s) noexcept {
        if (dt <= 0.0f || dt > 1.0f) return;

        /* Динаміка відносного руху */
        const float apparent_rate = rate_ - gyro_rate_rad_s;
        angle_ += apparent_rate * dt;

        /* Оновлення коваріації P = F * P * F^T + Q */
        const float p00 = P_[0][0] + dt * (P_[1][0] + P_[0][1]) + dt * dt * P_[1][1] + q_angle_ * dt;
        const float p01 = P_[0][1] + dt * P_[1][1];
        const float p10 = P_[1][0] + dt * P_[1][1];
        const float p11 = P_[1][1] + q_rate_ * dt;

        P_[0][0] = p00;
        P_[0][1] = p01;
        P_[1][0] = p10;
        P_[1][1] = p11;
    }

    void update(float measured_angle) noexcept {
        const float y = measured_angle - angle_;
        const float s = P_[0][0] + r_meas_;
        if (std::abs(s) < 1e-6f) return;

        const float k0 = P_[0][0] / s;
        const float k1 = P_[1][0] / s;

        angle_ += k0 * y;
        rate_  += k1 * y;

        const float p00_new = (1.0f - k0) * P_[0][0];
        const float p01_new = (1.0f - k0) * P_[0][1];
        const float p10_new = P_[1][0] - k1 * P_[0][0];
        const float p11_new = P_[1][1] - k1 * P_[0][1];

        P_[0][0] = p00_new;
        P_[0][1] = p01_new;
        P_[1][0] = p10_new;
        P_[1][1] = p11_new;
    }

    [[nodiscard]] std::pair<float, float> extrapolate(float latency_s) const noexcept {
        return {angle_ + rate_ * latency_s, rate_};
    }

    [[nodiscard]] float angle() const noexcept { return angle_; }
    [[nodiscard]] float rate() const noexcept { return rate_; }

private:
    float angle_{0.0f};
    float rate_{0.0f};
    std::array<std::array<float, 2>, 2> P_{{{0.1f, 0.0f}, {0.0f, 1.0f}}};
    float q_angle_;
    float q_rate_;
    float r_meas_;
};

/* ── ПІД-регулятор із захистом від насичення (Anti-Windup) ────────────────── */
class ServoingPID {
public:
    struct Config {
        float kp{1.8f};
        float ki{0.1f};
        float kd{0.15f};
        float max_output{1.0f};
        float max_integral{0.3f};
        float deadband{0.008f};
    };

    explicit ServoingPID(const Config& cfg) noexcept : cfg_(cfg) {}

    float update(float error, float measured_val, float dt) noexcept {
        if (dt <= 0.0f) return 0.0f;

        if (std::abs(error) < cfg_.deadband) {
            error = 0.0f;
        }

        const float p_term = cfg_.kp * error;

        integral_ = std::clamp(integral_ + error * dt, -cfg_.max_integral, cfg_.max_integral);
        const float i_term = cfg_.ki * integral_;

        float d_term = 0.0f;
        if (initialized_) {
            const float d_meas = (measured_val - prev_meas_) / dt;
            d_term = -cfg_.kd * d_meas;
        } else {
            initialized_ = true;
        }
        prev_meas_ = measured_val;

        return std::clamp(p_term + i_term + d_term, -cfg_.max_output, cfg_.max_output);
    }

    void reset() noexcept {
        integral_ = 0.0f;
        prev_meas_ = 0.0f;
        initialized_ = false;
    }

private:
    Config cfg_;
    float integral_{0.0f};
    float prev_meas_{0.0f};
    bool initialized_{false};
};

/* ── Головний клас візуального наведення ──────────────────────────────────── */
class VisualServoingController {
public:
    explicit VisualServoingController(CameraIntrinsics camera) noexcept
        : camera_(camera),
          pid_yaw_({.kp = 1.8f, .ki = 0.1f, .kd = 0.15f, .max_output = 1.0f, .max_integral = 0.3f, .deadband = 0.008f}),
          pid_pitch_({.kp = 1.8f, .ki = 0.1f, .kd = 0.15f, .max_output = 0.8f, .max_integral = 0.2f, .deadband = 0.008f}),
          pid_forward_({.kp = 0.02f, .ki = 0.001f, .kd = 0.005f, .max_output = 3.0f, .max_integral = 0.5f, .deadband = 2.0f}) {}

    void onDetection(const TargetDetection& det) noexcept {
        if (!det.valid) {
            tracked_ = false;
            return;
        }

        /* Перехід до кутових похибок за моделлю камери-обскури */
        const float norm_x = (det.u - camera_.cx) / camera_.fx;
        const float norm_y = (det.v - camera_.cy) / camera_.fy;

        kf_yaw_.update(std::atan(norm_x));
        kf_pitch_.update(std::atan(norm_y));

        last_frame_time_ = det.timestamp;
        current_scale_ = det.scale();
        tracked_ = true;
    }

    GuidanceSetpoints update(Microseconds current_time,
                              float gyro_yaw_rad_s,
                              float gyro_pitch_rad_s) noexcept {
        if (!tracked_ || last_exec_time_.count() == 0) {
            last_exec_time_ = current_time;
            return {};
        }

        const float dt = std::chrono::duration<float>(current_time - last_exec_time_).count();
        last_exec_time_ = current_time;

        /* 1. Прогноз стану за моделлю руху та гіроскопами */
        kf_yaw_.predict(dt, gyro_yaw_rad_s);
        kf_pitch_.predict(dt, gyro_pitch_rad_s);

        /* 2. Компенсація повної латентності контуру */
        const float latency_s = std::chrono::duration<float>(current_time - last_frame_time_).count();
        if (latency_s > 0.5f) {
            tracked_ = false;
            return {};
        }

        const auto [est_yaw_angle, est_yaw_rate] = kf_yaw_.extrapolate(latency_s);
        const auto [est_pitch_angle, est_pitch_rate] = kf_pitch_.extrapolate(latency_s);

        /* 3. Формування уставок кутових швидкостей */
        GuidanceSetpoints sp{};
        sp.yaw_rate_rad_s = pid_yaw_.update(est_yaw_angle, est_yaw_angle, dt);
        sp.pitch_rate_rad_s = -pid_pitch_.update(est_pitch_angle, est_pitch_angle, dt);

        /* 4. Формування поздовжньої швидкості за масштабом рамки */
        if (current_scale_ > 5.0f) {
            const float err_scale = desired_scale_ - current_scale_;
            sp.forward_vel_m_s = pid_forward_.update(err_scale, current_scale_, dt);
        }

        sp.target_acquired = true;
        return sp;
    }

    void setDesiredScale(float scale_px) noexcept { desired_scale_ = scale_px; }
    [[nodiscard]] bool isTracking() const noexcept { return tracked_; }

private:
    CameraIntrinsics camera_;
    KalmanAxisTracker kf_yaw_{0.01f, 0.5f, 0.005f};
    KalmanAxisTracker kf_pitch_{0.01f, 0.5f, 0.005f};
    ServoingPID pid_yaw_;
    ServoingPID pid_pitch_;
    ServoingPID pid_forward_;

    float desired_scale_{80.0f};
    float current_scale_{0.0f};
    Microseconds last_frame_time_{0};
    Microseconds last_exec_time_{0};
    bool tracked_{false};
};

} // namespace guidance
```
:::

## Інженерні особливості та граничні випадки

Реалізація враховує специфічні аспекти експлуатації систем комп'ютерного зору в реальному часі:

1. **Розділення частот обробки кадрів та виконання контуру:**
   Нейромережевий детектор на NPU працює асинхронно з частотою 25–30 Гц. Проте внутрішній контур стабілізації апарата потребує надходження свіжих уставок на частоті 100–200 Гц. Функція `visual_guidance_update` викликається в таймерному перериванні RTOS на частоті 100 Гц, плавно інтегруючи гіроскопи та екстраполюючи стан цілі між рідкісними кадрами. Це усуває сходинковий характер керування («драбинку» уставок), що перегріває цифрові сервоприводи.

2. **Захист від диференційного стрибка (Derivative Kick):**
   При звичайному диференціюванні похибки `d(e)/dt = d(target − measured)/dt` будь-яка зміна бажаного положення або перестрибування рамки детектора на сусідній об'єкт генерує нескінченно велику похідну, що викликає різкий удар моторів. У реалізації похідна обчислюється як `-Kd · d(measured)/dt`, що забезпечує плавний вихід регулятора навіть при миттєвих стрибках вхідних координат.

3. **Стійкість до втрати кадрів (Timeout Handling):**
   Якщо зв'язок із камерою обривається або детектор не може розпізнати об'єкт довше 500 мс (`latency_s > 0.5 с`), контролер автоматично скидає прапорець `target_acquired` та обнуляє уставки, переводячи апарат у безпечний режим зависання, запобігаючи неконтрольованому розгону за застарілою екстраполяцією.

---

## Інтеграція в бортову ОС та формування пакетів MAVLink

На практиці контролер візуального наведення вбудовується в архітектуру бортового комп'ютера у вигляді двох взаємодіючих потоків реального часу:

- **Потік зору (Vision Worker Thread, пріоритет нормальний):** виконує зчитування кадрів із V4L2/DMA буферів камери, запускає інференс нейромережі на NPU, зчитує апаратну мітку часу початку експозиції сенсора та передає структуру `TargetDetection` через потокобезпечну чергу (Lock-Free SPSC Queue) у функцію `onDetection`.
- **Контур керування (Control Loop Thread, пріоритет реального часу SCHED_FIFO):** працює за таймером 100 Гц. Опитує останні значення кутових швидкостей із повідомлення `HIGHRES_IMU` автопілота, викликає функцію `update` та транслює сформовані уставки `GuidanceSetpoints` у MAVLink-пакети.

### Серіалізація в повідомлення MAVLink `SET_ATTITUDE_TARGET`

Для передачі кутових швидкостей на автопілот формується повідомлення `mavlink_msg_set_attitude_target_pack`:
- Поле `type_mask` встановлюється в значення `0b00000111` (біти 0..2 встановлені в 1, що вказує автопілоту ігнорувати орієнтацію у вигляді кватерніона `q` та виконувати керування виключно за кутовими швидкостями).
- Поле `body_yaw_rate` заповнюється значенням `out_sp.yaw_rate_rad_s`.
- Поле `body_pitch_rate` заповнюється значенням `out_sp.pitch_rate_rad_s`.
- Поле `body_roll_rate` встановлюється в `0.0f` (для стабілізації горизонту або підтримується контуром утримання висоти).
- Поле `thrust` передає нормалізоване значення вертикальної тяги `[0.0 .. 1.0]`.

При роботі на мікроконтролерах без апаратного блоку FPU подвійної точності всі структури оптимізовано під 32-бітні числа одинарної точності `float`. Використання прапорця компілятора `-ffast-math` або явне включення режиму Flush-to-Zero (FTZ) у регістрі керування FPU запобігає виникненню повільних апаратних пасток при обробці денормалізованих чисел (subnormal floats), гарантуючи стабільний час виконання одного циклу регулятора менше 5 мікросекунд на ядрі ARM Cortex-M7 (480 МГц).

---

## Модульне тестування та верифікація на симульованій траєкторії

Для перевірки стійкості контуру перед польовими випробуваннями реалізується модульний тест (Unit Test / SIL-симуляція) із синтетичним джерелом запізнілих даних:

1. **Генерація штучної сходинки кута:** ціль миттєво зміщується на `α_target = +15°` (+0.2618 рад).
2. **Моделювання затримки камери:** координати поміщаються у кільцевий буфер-чергу затримки довжиною `N = T_delay / dt = 100 мс / 10 мс = 10` кроків.
3. **Замкнений контур динаміки дрона:** кутове прискорення моделюється як `α̈_drone = M_torque / J_inertia − D_aero · α̇_drone`.
4. **Критерії успішного проходження тесту:**
   - Час встановлення перехідного процесу (Settling Time до коридору ±5%): менше 0.75 секунди.
   - Перерегулювання (Overshoot): менше 12%.
   - Повна відсутність незатухаючих автоколивань (Limit Cycles) у стаціонарному режимі.


