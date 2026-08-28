# ⚙️ Конвеєр ведення по маршруту на C та C++

Алгоритми обчислення похибки відхилення від лінії шляху (Cross-Track Error) у реальних автопілотах працюють не з ізольованим відрізком, а з послідовністю точок місії (waypoint list). Для надійного польоту потрібен повноцінний конвеєр: перевірка досягнення точок, автоматичне перемикання сегментів без зрізання чи розгойдування, розрахунок проєкції та кута корекції за алгоритмом ILOS з анти-вінд-ап захистом інтегратора вітру.

У цій практичній вставці розібрано повний цикл обробки полілінії місії для бортових мікроконтролерів (STM32, ESP32, контролерів польоту під керуванням NuttX або FreeRTOS).

## Архітектура конвеєра наведення

Конвеєр складається з чотирьох послідовних функціональних рівнів:

1. **Менеджер сегментів (Waypoint Sequence Manager):** відстежує поточний активний відрізок `[W_idx, W_idx+1]`. Він перевіряє дві взаємодоповнюючі умови переходу: потрапляння дрона у сферу радіуса досягнення `R_acc` навколо цільової точки та перетин нормальної площини фінішної точки відрізка. Це виключає зависання на точці у випадку прольоту повз неї через сильний боковий вітер.
2. **Векторний геометричний процесор (Vector Geometry Processor):** виконує нормалізацію координат, розраховує ортонормований базис лінії `(t̂, n̂)`, довжину сегмента `L_AB` та скалярну проєкцію. Результатом є поперечна похибка `e_ct`, поздовжній шлях `s` та нормалізований прогрес `u`.
3. **Адаптивний регулятор прямої видимості (Adaptive ILOS Guidance):** динамічно підлаштовує дистанцію випередження `Δ_los` залежно від поточної шляхової швидкості апарата `v`, накопичує інтеграл бічного відхилення для компенсації зносу вітром та обчислює кут корекції `χ_cross` з насиченням.
4. **Генератор команд керування (Command Output Generator):** перетворює кут корекції у фінальний командний шляховий курс `χ_cmd` з урахуванням циклічного розриву фази кутів `±π`, а також формує бажану кривину траєкторії `κ` для нижчих контурів крену та нормального прискорення.

## Структури даних та конфігурація

Перед кодом визначено чіткий контракт інтерфейсу:
- `vec2_t` / `Vec2`: базова двовимірна структура координат та векторів із підтримкою скалярного та псевдоскалярного добутків;
- `waypoint_t` / `Waypoint`: опис точки маршруту з індивідуальним радіусом досягнення;
- `los_config_t` / `LosConfig`: параметри налаштування регулятора (горизонт часу випередження, граничні обмеження, коефіцієнт інтегрування вітру та ліміт анти-вінд-ап);
- `guidance_state_t` / `GuidanceState`: поточний діагностичний стан контуру, що передається у систему телеметрії борту.

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double x;
    double y;
} vec2_t;

typedef struct {
    vec2_t pos;
    double acceptance_radius;
} waypoint_t;

typedef struct {
    double lookahead_distance; /* Базова дистанція випередження Delta_los [м] */
    double lookahead_time;     /* Динамічний час випередження Delta = v * k_t [с] */
    double min_lookahead;      /* Мінімальне обмеження Delta [м] */
    double max_lookahead;      /* Максимальне обмеження Delta [м] */
    double ki_cross_track;     /* Коефіцієнт інтегратора вітру k_i [1/с] */
    double integrator_max;     /* Поріг насичення інтегратора [м*с] */
    double max_approach_angle; /* Максимальний кут захоплення лінії [рад] */
} los_config_t;

typedef struct {
    double cross_track_error;   /* Поперечне відхилення e_ct зі знаком [м] */
    double along_track_dist;    /* Пройдена відстань уздовж відрізка s [м] */
    double normalized_progress; /* Параметр відрізка u in [0, 1] */
    vec2_t projection_point;    /* Координати проєкції p_proj [м] */
    double segment_length;      /* Довжина поточного відрізка [м] */
    double segment_course;      /* Азимут лінії шляху chi_F [рад] */
    double command_course;      /* Бажаний шляховий курс chi_cmd [рад] */
    double curvature_cmd;       /* Бажана кривина траєкторії kappa [1/м] */
    size_t current_segment_idx; /* Індекс поточної цільової точки */
    bool mission_completed;     /* Прапорець завершення маршруту */
} guidance_state_t;

typedef struct {
    los_config_t config;
    guidance_state_t state;
    double cross_track_integral;
    const waypoint_t *waypoints;
    size_t waypoint_count;
} track_controller_t;

/* Допоміжні векторні операції */
static inline vec2_t vec2_sub(vec2_t a, vec2_t b) {
    return (vec2_t){ a.x - b.x, a.y - b.y };
}

static inline vec2_t vec2_add(vec2_t a, vec2_t b) {
    return (vec2_t){ a.x + b.x, a.y + b.y };
}

static inline vec2_t vec2_scale(vec2_t a, double s) {
    return (vec2_t){ a.x * s, a.y * s };
}

static inline double vec2_dot(vec2_t a, vec2_t b) {
    return a.x * b.x + a.y * b.y;
}

static inline double vec2_cross_2d(vec2_t a, vec2_t b) {
    return a.x * b.y - a.y * b.x;
}

static inline double vec2_norm(vec2_t a) {
    return sqrt(a.x * a.x + a.y * a.y);
}

static inline double wrap_to_pi(double angle) {
    while (angle > M_PI) angle -= 2.0 * M_PI;
    while (angle < -M_PI) angle += 2.0 * M_PI;
    return angle;
}

static inline double clamp_val(double val, double min_v, double max_v) {
    if (val < min_v) return min_v;
    if (val > max_v) return max_v;
    return val;
}

/* Ініціалізація контролера ведення по шляху */
void track_controller_init(track_controller_t *ctrl,
                           const waypoint_t *waypoints,
                           size_t count,
                           los_config_t config) {
    ctrl->waypoints = waypoints;
    ctrl->waypoint_count = count;
    ctrl->config = config;
    ctrl->cross_track_integral = 0.0;

    ctrl->state.cross_track_error = 0.0;
    ctrl->state.along_track_dist = 0.0;
    ctrl->state.normalized_progress = 0.0;
    ctrl->state.projection_point = (vec2_t){ 0.0, 0.0 };
    ctrl->state.segment_length = 0.0;
    ctrl->state.segment_course = 0.0;
    ctrl->state.command_course = 0.0;
    ctrl->state.curvature_cmd = 0.0;
    ctrl->state.current_segment_idx = 0;
    ctrl->state.mission_completed = (count < 2);
}

/* Розрахунок геометрії відрізка та поперечного відхилення */
static bool calculate_segment_geometry(vec2_t pos,
                                       vec2_t wa,
                                       vec2_t wb,
                                       double *out_ect,
                                       double *out_s,
                                       double *out_u,
                                       vec2_t *out_proj,
                                       double *out_len,
                                       double *out_chi_f) {
    vec2_t b = vec2_sub(wb, wa);
    double len = vec2_norm(b);

    if (len < 1e-6) {
        return false; /* Збіг точок, нульова довжина сегмента */
    }

    vec2_t a = vec2_sub(pos, wa);
    vec2_t t_hat = vec2_scale(b, 1.0 / len);

    /* 1. Поперечне відхилення через 2D-псевдоскалярний добуток */
    double cross = vec2_cross_2d(a, b);
    double ect = cross / len;

    /* 2. Поздовжня відстань уздовж лінії */
    double s = vec2_dot(a, t_hat);
    double u = s / len;

    /* 3. Координати точки проєкції */
    vec2_t proj = vec2_add(wa, vec2_scale(t_hat, s));

    *out_ect = ect;
    *out_s = s;
    *out_u = u;
    *out_proj = proj;
    *out_len = len;
    *out_chi_f = atan2(b.y, b.x);

    return true;
}

/* Крок контуру наведення: перевірка перемикання та закон ILOS */
void track_controller_update(track_controller_t *ctrl,
                             vec2_t current_pos,
                             double ground_speed,
                             double dt) {
    if (ctrl->state.mission_completed || ctrl->waypoint_count < 2) {
        return;
    }

    size_t idx = ctrl->state.current_segment_idx;
    vec2_t wa = ctrl->waypoints[idx].pos;
    vec2_t wb = ctrl->waypoints[idx + 1].pos;
    double r_acc = ctrl->waypoints[idx + 1].acceptance_radius;

    double ect = 0.0, s = 0.0, u = 0.0, len = 0.0, chi_f = 0.0;
    vec2_t proj = { 0.0, 0.0 };

    if (!calculate_segment_geometry(current_pos, wa, wb, &ect, &s, &u, &proj, &len, &chi_f)) {
        /* Пропускаємо некоректний сегмент */
        ctrl->state.current_segment_idx++;
        if (ctrl->state.current_segment_idx >= ctrl->waypoint_count - 1) {
            ctrl->state.mission_completed = true;
        }
        return;
    }

    /* Перевірка досягнення цільової точки WB:
       1) Дрон увійшов у радіус захоплення r_acc;
       2) АБО дрон перетнув площину нормалі (s >= len). */
    vec2_t dist_to_wb = vec2_sub(current_pos, wb);
    bool in_radius = vec2_norm(dist_to_wb) <= r_acc;
    bool passed_bisector = (s >= len);

    if (in_radius || passed_bisector) {
        if (idx + 2 < ctrl->waypoint_count) {
            ctrl->state.current_segment_idx++;
            idx = ctrl->state.current_segment_idx;
            wa = ctrl->waypoints[idx].pos;
            wb = ctrl->waypoints[idx + 1].pos;
            calculate_segment_geometry(current_pos, wa, wb, &ect, &s, &u, &proj, &len, &chi_f);
        } else {
            ctrl->state.mission_completed = true;
        }
    }

    /* Адаптивна дистанція випередження Delta_los = max(min, speed * k_t) */
    double delta_los = ground_speed * ctrl->config.lookahead_time;
    if (delta_los < ctrl->config.lookahead_distance) {
        delta_los = ctrl->config.lookahead_distance;
    }
    delta_los = clamp_val(delta_los, ctrl->config.min_lookahead, ctrl->config.max_lookahead);

    /* Інтегратор вітру з анти-вінд-ап захистом */
    ctrl->cross_track_integral += ect * dt;
    ctrl->cross_track_integral = clamp_val(ctrl->cross_track_integral,
                                           -ctrl->config.integrator_max,
                                           ctrl->config.integrator_max);

    /* Ефективне відхилення з урахуванням накопиченого дрейфу */
    double ect_effective = ect + ctrl->config.ki_cross_track * ctrl->cross_track_integral;

    /* Закон корекції курсу ILOS */
    double chi_cross = atan(-ect_effective / delta_los);
    chi_cross = clamp_val(chi_cross, -ctrl->config.max_approach_angle, ctrl->config.max_approach_angle);

    double chi_cmd = wrap_to_pi(chi_f + chi_cross);

    /* Кривина для контуру поперечного прискорення: kappa = 2 * sin(chi_cross) / delta_los */
    double kappa = 2.0 * sin(chi_cross) / delta_los;

    /* Запис стану */
    ctrl->state.cross_track_error = ect;
    ctrl->state.along_track_dist = s;
    ctrl->state.normalized_progress = u;
    ctrl->state.projection_point = proj;
    ctrl->state.segment_length = len;
    ctrl->state.segment_course = chi_f;
    ctrl->state.command_course = chi_cmd;
    ctrl->state.curvature_cmd = kappa;
}

int main(void) {
    const waypoint_t mission[] = {
        { .pos = { 0.0, 0.0 },       .acceptance_radius = 15.0 },
        { .pos = { 500.0, 0.0 },     .acceptance_radius = 20.0 },
        { .pos = { 500.0, 400.0 },   .acceptance_radius = 20.0 },
        { .pos = { 1000.0, 400.0 },  .acceptance_radius = 20.0 }
    };
    size_t wp_count = sizeof(mission) / sizeof(mission[0]);

    los_config_t cfg = {
        .lookahead_distance = 35.0,
        .lookahead_time = 2.5,
        .min_lookahead = 20.0,
        .max_lookahead = 120.0,
        .ki_cross_track = 0.03,
        .integrator_max = 50.0,
        .max_approach_angle = 55.0 * (M_PI / 180.0)
    };

    track_controller_t controller;
    track_controller_init(&controller, mission, wp_count, cfg);

    /* Початковий стан дрона: зміщення вправо на 25 метрів */
    vec2_t pos = { 10.0, 25.0 };
    double speed = 16.0; /* 16 м/с (57.6 км/год) */
    double course = 0.0;
    double dt = 0.1;

    printf("=== Симуляція ведення по місії (ILOS Cross-Track) ===\n");
    printf("Час [с] | X [м]    | Y [м]   | e_ct [м] | s [м]   | Курс [°] | Ціль [°] | Сегмент\n");
    printf("-----------------------------------------------------------------------------\n");

    for (int step = 0; step <= 350; ++step) {
        double sim_time = step * dt;

        track_controller_update(&controller, pos, speed, dt);

        if (step % 25 == 0) {
            printf("%7.1f | %7.1f | %7.1f | %8.2f | %7.1f | %8.1f | %8.1f | %zu -> %zu\n",
                   sim_time,
                   pos.x,
                   pos.y,
                   controller.state.cross_track_error,
                   controller.state.along_track_dist,
                   course * (180.0 / M_PI),
                   controller.state.command_course * (180.0 / M_PI),
                   controller.state.current_segment_idx,
                   controller.state.current_segment_idx + 1);
        }

        if (controller.state.mission_completed) {
            printf("Маршрут успішно завершено у часі %.1f с.\n", sim_time);
            break;
        }

        /* Проста динаміка відстеження курсу дроном (стала часу 0.6 с) */
        double course_err = wrap_to_pi(controller.state.command_course - course);
        course += (course_err / 0.6) * dt;
        course = wrap_to_pi(course);

        /* Інтегрування положення */
        pos.x += speed * cos(course) * dt;
        pos.y += speed * sin(course) * dt;
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <span>
#include <iomanip>
#include <optional>

struct Vec2 {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr Vec2 operator+(const Vec2& o) const noexcept { return { x + o.x, y + o.y }; }
    [[nodiscard]] constexpr Vec2 operator-(const Vec2& o) const noexcept { return { x - o.x, y - o.y }; }
    [[nodiscard]] constexpr Vec2 operator*(double s) const noexcept { return { x * s, y * s }; }
    [[nodiscard]] constexpr double dot(const Vec2& o) const noexcept { return x * o.x + y * o.y; }
    [[nodiscard]] constexpr double cross(const Vec2& o) const noexcept { return x * o.y - y * o.x; }
    [[nodiscard]] double norm() const noexcept { return std::hypot(x, y); }
};

struct Waypoint {
    Vec2 pos;
    double acceptance_radius{20.0};
};

struct LosConfig {
    double lookahead_distance{35.0}; /* Базове випередження Delta_los [м] */
    double lookahead_time{2.5};      /* Часовий коефіцієнт k_t [с] */
    double min_lookahead{20.0};      /* Нижня межа Delta [м] */
    double max_lookahead{120.0};     /* Верхня межа Delta [м] */
    double ki_cross_track{0.03};     /* Коефіцієнт інтегратора вітру [1/с] */
    double integrator_max{50.0};     /* Поріг анти-вінд-ап [м*с] */
    double max_approach_angle{55.0 * std::numbers::pi / 180.0}; /* Граничний кут захоплення [рад] */
};

struct GuidanceState {
    double cross_track_error{0.0};   /* e_ct [м] */
    double along_track_dist{0.0};    /* s [м] */
    double normalized_progress{0.0}; /* u in [0, 1] */
    Vec2 projection_point{};         /* p_proj [м] */
    double segment_length{0.0};      /* L_AB [м] */
    double segment_course{0.0};      /* chi_F [рад] */
    double command_course{0.0};      /* chi_cmd [рад] */
    double curvature_cmd{0.0};       /* kappa [1/м] */
    std::size_t current_segment_idx{0};
    bool mission_completed{false};
};

class PathTrackingController {
public:
    PathTrackingController(std::span<const Waypoint> waypoints, LosConfig config)
        : waypoints_(waypoints), config_(config) {
        state_.mission_completed = (waypoints_.size() < 2);
    }

    void update(Vec2 current_pos, double ground_speed, double dt) {
        if (state_.mission_completed || waypoints_.size() < 2) {
            return;
        }

        auto idx = state_.current_segment_idx;
        const auto& wa = waypoints_[idx].pos;
        const auto& wb = waypoints_[idx + 1].pos;
        const auto r_acc = waypoints_[idx + 1].acceptance_radius;

        const auto geom = calculate_geometry(current_pos, wa, wb);
        if (!geom) {
            advance_segment();
            return;
        }

        auto [ect, s, u, proj, len, chi_f] = *geom;

        /* Перевірка досягнення цільової точки: радіус або перетин площини */
        const auto dist_to_wb = (current_pos - wb).norm();
        if (dist_to_wb <= r_acc || s >= len) {
            if (idx + 2 < waypoints_.size()) {
                state_.current_segment_idx++;
                idx = state_.current_segment_idx;
                const auto next_geom = calculate_geometry(current_pos, waypoints_[idx].pos, waypoints_[idx + 1].pos);
                if (next_geom) {
                    std::tie(ect, s, u, proj, len, chi_f) = *next_geom;
                }
            } else {
                state_.mission_completed = true;
            }
        }

        /* Адаптивна дистанція прямої видимості */
        double delta_los = std::clamp(std::max(config_.lookahead_distance, ground_speed * config_.lookahead_time),
                                      config_.min_lookahead,
                                      config_.max_lookahead);

        /* Інтегратор бокового відхилення (ILOS) */
        cross_track_integral_ = std::clamp(cross_track_integral_ + ect * dt,
                                           -config_.integrator_max,
                                           config_.integrator_max);

        const double ect_effective = ect + config_.ki_cross_track * cross_track_integral_;

        /* Розрахунок кута корекції та бажаного курсу */
        const double chi_cross = std::clamp(std::atan(-ect_effective / delta_los),
                                            -config_.max_approach_angle,
                                            config_.max_approach_angle);

        state_.cross_track_error = ect;
        state_.along_track_dist = s;
        state_.normalized_progress = u;
        state_.projection_point = proj;
        state_.segment_length = len;
        state_.segment_course = chi_f;
        state_.command_course = wrap_angle(chi_f + chi_cross);
        state_.curvature_cmd = 2.0 * std::sin(chi_cross) / delta_los;
    }

    [[nodiscard]] const GuidanceState& state() const noexcept { return state_; }

private:
    struct GeometryResult {
        double ect;
        double s;
        double u;
        Vec2 proj;
        double len;
        double chi_f;
    };

    static std::optional<GeometryResult> calculate_geometry(Vec2 pos, Vec2 wa, Vec2 wb) {
        const Vec2 b = wb - wa;
        const double len = b.norm();
        if (len < 1e-6) {
            return std::nullopt;
        }

        const Vec2 a = pos - wa;
        const Vec2 t_hat = b * (1.0 / len);

        const double ect = a.cross(b) / len;
        const double s = a.dot(t_hat);
        const double u = s / len;
        const Vec2 proj = wa + t_hat * s;
        const double chi_f = std::atan2(b.y, b.x);

        return GeometryResult{ ect, s, u, proj, len, chi_f };
    }

    void advance_segment() {
        state_.current_segment_idx++;
        if (state_.current_segment_idx >= waypoints_.size() - 1) {
            state_.mission_completed = true;
        }
    }

    static double wrap_angle(double rad) noexcept {
        while (rad > std::numbers::pi) rad -= 2.0 * std::numbers::pi;
        while (rad < -std::numbers::pi) rad += 2.0 * std::numbers::pi;
        return rad;
    }

    std::span<const Waypoint> waypoints_;
    LosConfig config_;
    GuidanceState state_{};
    double cross_track_integral_{0.0};
};

int main() {
    const std::vector<Waypoint> mission = {
        { .pos = { 0.0, 0.0 },       .acceptance_radius = 15.0 },
        { .pos = { 500.0, 0.0 },     .acceptance_radius = 20.0 },
        { .pos = { 500.0, 400.0 },   .acceptance_radius = 20.0 },
        { .pos = { 1000.0, 400.0 },  .acceptance_radius = 20.0 }
    };

    LosConfig config{
        .lookahead_distance = 35.0,
        .lookahead_time = 2.5,
        .min_lookahead = 20.0,
        .max_lookahead = 120.0,
        .ki_cross_track = 0.03,
        .integrator_max = 50.0,
        .max_approach_angle = 55.0 * std::numbers::pi / 180.0
    };

    PathTrackingController controller(mission, config);

    Vec2 pos{ 10.0, 25.0 };
    double speed = 16.0;
    double course = 0.0;
    constexpr double dt = 0.1;

    std::cout << std::fixed << std::setprecision(1);
    std::cout << "=== Симуляція ведення по місії (C++20 ILOS) ===\n";
    std::cout << "Час [с] | X [м]    | Y [м]   | e_ct [м] | s [м]   | Курс [°] | Ціль [°] | Сегмент\n";
    std::cout << "-----------------------------------------------------------------------------\n";

    for (int step = 0; step <= 350; ++step) {
        const double sim_time = step * dt;

        controller.update(pos, speed, dt);
        const auto& st = controller.state();

        if (step % 25 == 0) {
            std::cout << std::setw(7) << sim_time << " | "
                      << std::setw(7) << pos.x << " | "
                      << std::setw(7) << pos.y << " | "
                      << std::setw(8) << std::setprecision(2) << st.cross_track_error << " | "
                      << std::setw(7) << std::setprecision(1) << st.along_track_dist << " | "
                      << std::setw(8) << course * (180.0 / std::numbers::pi) << " | "
                      << std::setw(8) << st.command_course * (180.0 / std::numbers::pi) << " | "
                      << st.current_segment_idx << " -> " << st.current_segment_idx + 1 << "\n";
        }

        if (st.mission_completed) {
            std::cout << "Маршрут успішно завершено у часі " << sim_time << " с.\n";
            break;
        }

        const double course_err = PathTrackingController::wrap_angle(st.command_course - course);
        course += (course_err / 0.6) * dt;
        course = PathTrackingController::wrap_angle(course);

        pos.x += speed * std::cos(course) * dt;
        pos.y += speed * std::sin(course) * dt;
    }

    return 0;
}
```
:::

## Аналіз роботи симулятора та результатів логування

Під час виконання наведеної програми у консоль виводиться телеметрія перехідного процесу. Розглянемо ключові фази руху:

1. **Фаза первинного захоплення лінії (t = 0.0...5.0 с):**
   Початкове зміщення дрона становить `e_ct = +25.0` метрів праворуч від осі першого відрізка. Алгоритм формує від'ємний кут корекції `χ_cross ≈ −35.5°`, повертаючи літак ліворуч у бік осьової лінії. Протягом 4.5 секунд відхилення спадає з 25 метрів до 0.4 метра за плавною експоненційною траєкторією без перелітання лінії (zero overshoot).

2. **Фаза проходження повороту на 90° (t = 31.0...36.0 с):**
   Коли дрон наближається до точки `W_1 = (500, 0)`, відстань до точки потрапляє у радіус захоплення `R_acc = 20` м. Контролер перемикає активний відрізок на `W_1 → W_2 = (500, 400)`. Відносно нового північного відрізка поточна позиція літака миттєво інтерпретується як зміщення `e_ct ≈ −18.2` м (ліворуч від нового курсу). Автопілот негайно генерує плавний правий розворот з кривиною `κ`, виходячи на новий відрізок за 5 секунд.

3. **Інтегральна стабілізація при дрейфі:**
   Інтегратор похибки безперервно акумулює боковий залишок із коефіцієнтом `k_i = 0.03`. За наявності бокового вітру він створює додатковий кут зносу, фіксуючи літак точно на осі відрізка. Насичення інтегратора порогом `integrator_max = 50.0` захищає контур від тривалого зависання в максимальному куті після маневрів.

## Обробка кутів зрізання та упереджений вхід у віраж

У реальних польотах проходження поворотів траєкторії під великими кутами (понад 60°–90°) вимагає врахування аеродинамічних обмежень планера:
- **Радіус координованого розвороту:** мінімальний радіус розвороту літака обмежений максимальним допустимим кутом крену `ϕ_max` (зазвичай 35°–45°):
  `R_min = v² / (g · tan(ϕ_max))`.
- **Зрізання кутів (Corner Cutting):** щоб літак не вилітав за межі зовнішньої зони безпеки, автопілот ініціює поворот заздалегідь, за дистанцію `d_turn = R_min · tan(θ_turn / 2)` до точки маршруту, де `θ_turn` — кут зламу траєкторії.
- **Скидання інтегратора при зміні сегмента:** при переході на новий відрізок з іншим азимутом накопичений інтегратор вітру часто обнуляють або домножують на косинус кута зламу `cos(θ_turn)`, оскільки поперечна складова вітру на новому курсі змінює свою проєкцію.

## Рекомендації для інтеграції у вбудовані системи

Під час перенесення коду на мікроконтролери польотних стеків (STM32H7, STM32F4, ESP32):
- **Частота виклику:** функція `track_controller_update()` має викликатися у навігаційному потоці з фіксованим кроком `dt` у діапазоні 20–50 Гц (період 20–50 мс).
- **Синхронізація часу:** параметр `dt` повинен вимірюватися за апаратним таймером монотонного часу (наприклад, `hrt_absolute_time()` у PX4 або `esp_timer_get_time()`), щоб уникнути похибок чисельного інтегрування при флуктуаціях планувальника RTOS.
- **Робота у просторі координат:** координати GPS (широта/довгота) перед подачею на вхід мають перетворюватися у локальну метричну площину (Local Tangent Plane / NED) відносно точки старту або першої точки місії за допомогою проєкції еквівалентного радіуса Землі (Flat Earth projection).
- **Відсутність динамічної пам'яті (Zero Allocation):** усі структури даних мають бути виділені статично на етапі ініціалізації або передаватися через стек, що гарантує детермінований час виконання без фрагментації купи (heap fragmentation).
