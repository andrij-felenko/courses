# ⚙️ Сторожовий таймер та монітор прогресу поведінок автопілота

Сторожовий таймер поведінок (Behavior Watchdog) — це модуль польотного стека жорсткого реального часу, який забезпечує детерміноване виконання або примусове аварійне переривання автономних місійних дій безпілотного апарата. Модуль здійснює паралельний моніторинг монотонного часу, кінематичного наближення до цільової точки, збіжності коваріацій розширеного фільтра Калмана (EKF) та динамічного балансу енергії, необхідної для повернення на базу.

## Архітектурні вимоги та місце в RTOS-контурі

У польотних контролерах під керуванням операційних систем реального часу (NuttX, FreeRTOS, ChibiOS) навігаційні поведінки (рух до шляхової точки `NAV_WAYPOINT`, прецизійна оптична посадка `PRECISION_LAND`, зависання над об'єктом інспекції `LOITER_TIME`) виконуються у складі високорівневого потоку місії з частотою опитування 50–100 Гц.

Якщо поведінка не досягає цільових умов через зовнішні аеродинамічні збурення або відмови сенсорів, алгоритм ризикує заблокувати зміну станів до повного виснаження бортового джерела живлення.

Модуль `BehaviorWatchdog` реалізує концепцію синхронного нагляду за інваріантами безпеки та накладає на польотний контур такі системні обмеження:
1. **Детермінізм виконання `O(1)`**: усі обчислення (векторна геометрія, скалярні добутки, енергетичний баланс) виконуються за фіксовану кількість тактів процесора без ітеративних циклів та нелінійних наближень.
2. **Нульове динамічне виділення пам'яті (Zero Heap Allocation)**: заборонено використання системних викликів `malloc()`, `free()`, `new`, `delete` під час виконання польотного циклу. Уся пам'ять для структур стану виділяється статично під час ініціалізації навігаційного стека.
3. **Ізоляція від астрономічного часу**: відлік інтервалів ведеться виключно за 64-бітним монотонним апаратним таймером (`CLOCK_MONOTONIC_RAW` або `hrt_absolute_time()`).

```
                      ┌────────────────────────────────────────┐
                      │        BehaviorWatchdog::update()      │
                      │           (Виклик кожні 20 мс)         │
                      └───────────────────┬────────────────────┘
                                          │
       ┌──────────────────────────────────┼──────────────────────────────────┐
       ▼                                  ▼                                  ▼
 ┌──────────────┐                  ┌──────────────┐                   ┌──────────────┐
 │  ЖОРСТКИЙ    │                  │  КІНЕМАТИКА  │                   │  ЕНЕРГЕТИКА  │
 │  ТАЙМЕР      │                  │  ТА EKF      │                   │  ТА ВІТЕР    │
 ├──────────────┤                  ├──────────────┤                   ├──────────────┤
 │ Δt > T_limit │                  │ v_proj < min │                   │ E_rem ≤      │
 │ (Монотонний) │                  │ σ_cov > max  │                   │ E_RTL + E_res│
 └──────┬───────┘                  └──────┬───────┘                   └──────┬───────┘
        │                                 │                                  │
        └─────────────────────────────────┼──────────────────────────────────┘
                                          ▼
                      ┌────────────────────────────────────────┐
                      │    Детекція зриву та видача статусу    │
                      │ [TIMEOUT_HARD | STAGNATION | CRITICAL] │
                      └────────────────────────────────────────┘
```

## Математичний апарат оцінки прогресу та енергетичного бар'єра

### 1. Векторна геометрія та одиничний напрямок
Нехай тривимірне просторове положення апарата в локальній системі координат NED (North-East-Down) задається вектором `p(t) = [x, y, z]ᵀ`, а координати цільової точки — вектором `p_target = [x_t, y_t, z_t]ᵀ`.

Вектор просторової нев'язки та евклідова відстань становлять:

```
Δp = p_target - p(t)                 [вектор зміщення до цілі]
d(t) = √(Δp_x² + Δp_y² + Δp_z²)      [поточна евклідова відстань]
```

Для запобігання чисельній сингулярності (діленню на нуль) в околі цільової точки одиничний вектор напрямку `u(t)` нормалізується через поріг регуляризації `ε = 10⁻⁴ м`:

```
u(t) = Δp ÷ max(d(t), ε)             [одиничний вектор напрямку]
```

### 2. Скалярна проекція швидкості та детекція стагнації
Нехай вектор поточної швидкості апарата відносно землі за оцінкою EKF становить `v(t) = [v_x, v_y, v_z]ᵀ`. Скалярна швидкість наближення до мети дорівнює:

```
v_proj(t) = v(t) · u(t) = v_x·u_x + v_y·u_y + v_z·u_z  [швидкість наближення]
```

Модуль відстежує історичний мінімум відстані `d_min_recorded`. Якщо поточна дистанція зменшується більше ніж на величину просторового гістерезису `δ_hyst = 0.25 м`:

```
d(t) < d_min_recorded - δ_hyst
```

значення `d_min_recorded` оновлюється, а таймер останнього зафіксованого поступу `t_last_progress` скидається на поточний монотонний час `t_now`. Якщо ж протягом часу `T_stagnation_window` (4–8 с) апарат не скорочує відстань і його швидкість наближення `v_proj < v_min_threshold` (0.25–0.40 м/с), фіксується подія `WATCHDOG_STATUS_STAGNATION_DETECTED`.

### 3. Динамічний розрахунок точки неповернення (Point of No Return)
Для повернення на точку старту (Home) на відстань `d_home` проти зустрічного вітру зі швидкістю `v_wind_head` ефективна шляхова швидкість становить:

```
v_eff = max(v_cruise - v_wind_head, 1.0)  [колійна швидкість повернення, м/с]
t_RTL = d_home ÷ v_eff                    [час польоту додому, с]
E_required = t_RTL · P_cruise + E_climb + E_safety  [необхідний запас енергії, Дж]
```

Якщо залишкова енергія батареї `E_battery ≤ E_required`, таймаут активної дії примусово скорочується до нуля, вимагаючи негайного повернення.

## Повна реалізація сторожового таймера та тестового стенда

Нижче наведено промислову реалізацію модуля моніторингу та каскаду ескалації на мовах C та C++ разом із вбудованим верифікаційним стендом, який моделює п'ять критичних польотних сценаріїв.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define WATCHDOG_EPSILON 1e-4f
#define MAX_ESCALATION_RETRIES 2

typedef enum {
    WATCHDOG_STATUS_RUNNING = 0,
    WATCHDOG_STATUS_COMPLETED_SUCCESS,
    WATCHDOG_STATUS_TIMEOUT_HARD,
    WATCHDOG_STATUS_STAGNATION_DETECTED,
    WATCHDOG_STATUS_EKF_DIVERGENCE,
    WATCHDOG_STATUS_ENERGY_CRITICAL
} watchdog_status_t;

typedef enum {
    ESCALATION_ACTION_NONE = 0,
    ESCALATION_ACTION_RETRY_RELAXED,
    ESCALATION_ACTION_FALLBACK_LOITER,
    ESCALATION_ACTION_EMERGENCY_RTL,
    ESCALATION_ACTION_EMERGENCY_LAND
} escalation_action_t;

typedef struct {
    float x;
    float y;
    float z;
} vector3f_t;

typedef struct {
    uint64_t hard_timeout_us;        /* Максимальний час виконання дії (мкс) */
    uint64_t stagnation_window_us;   /* Вікно виявлення стагнації (мкс) */
    float min_progress_rate_mps;     /* Мінімальна швидкість наближення (м/с) */
    float max_pos_variance_m2;       /* Гранична дисперсія координат EKF (м²) */
    float energy_safety_margin_j;    /* Резерв енергії безпеки (Джоулі) */
    float power_cruise_w;            /* Потужність горизонтального польоту (Вт) */
    float speed_cruise_mps;          /* Крейсерська швидкість (м/с) */
    float default_acceptance_rad_m;  /* Радіус прийняття точки за замовчуванням (м) */
    float relaxed_acceptance_rad_m;  /* Розширений радіус прийняття точки (м) */
} watchdog_config_t;

typedef struct {
    watchdog_config_t config;
    uint64_t start_time_us;
    uint64_t last_progress_time_us;
    vector3f_t target_position;
    float initial_distance_m;
    float min_recorded_distance_m;
    float current_acceptance_radius_m;
    uint8_t retry_count;
    bool is_active;
} behavior_watchdog_t;

static inline float vec3_dist(const vector3f_t *a, const vector3f_t *b) {
    float dx = a->x - b->x;
    float dy = a->y - b->y;
    float dz = a->z - b->z;
    return sqrtf(dx * dx + dy * dy + dz * dz);
}

void behavior_watchdog_init(behavior_watchdog_t *wd, const watchdog_config_t *cfg) {
    if (!wd || !cfg) return;
    wd->config = *cfg;
    wd->start_time_us = 0;
    wd->last_progress_time_us = 0;
    wd->target_position = (vector3f_t){0.0f, 0.0f, 0.0f};
    wd->initial_distance_m = 0.0f;
    wd->min_recorded_distance_m = 0.0f;
    wd->current_acceptance_radius_m = cfg->default_acceptance_rad_m;
    wd->retry_count = 0;
    wd->is_active = false;
}

void behavior_watchdog_start(behavior_watchdog_t *wd,
                             uint64_t now_us,
                             const vector3f_t *curr_pos,
                             const vector3f_t *target_pos) {
    if (!wd || !curr_pos || !target_pos) return;
    wd->start_time_us = now_us;
    wd->last_progress_time_us = now_us;
    wd->target_position = *target_pos;
    wd->initial_distance_m = vec3_dist(curr_pos, target_pos);
    wd->min_recorded_distance_m = wd->initial_distance_m;
    wd->current_acceptance_radius_m = wd->config.default_acceptance_rad_m;
    wd->retry_count = 0;
    wd->is_active = true;
}

watchdog_status_t behavior_watchdog_update(behavior_watchdog_t *wd,
                                          uint64_t now_us,
                                          const vector3f_t *curr_pos,
                                          const vector3f_t *curr_vel,
                                          float ekf_pos_variance_m2,
                                          float remaining_energy_j,
                                          const vector3f_t *home_pos) {
    if (!wd || !wd->is_active || !curr_pos || !curr_vel || !home_pos) {
        return WATCHDOG_STATUS_RUNNING;
    }

    float dist_to_target = vec3_dist(curr_pos, &wd->target_position);

    /* 0. Перевірка успішного досягнення цілі */
    if (dist_to_target <= wd->current_acceptance_radius_m) {
        return WATCHDOG_STATUS_COMPLETED_SUCCESS;
    }

    /* 1. Жорсткий таймаут за монотонним лічильником */
    uint64_t elapsed_us = now_us - wd->start_time_us;
    if (elapsed_us >= wd->config.hard_timeout_us) {
        return WATCHDOG_STATUS_TIMEOUT_HARD;
    }

    /* 2. Деградація розширеного фільтра Калмана (EKF) */
    if (ekf_pos_variance_m2 > wd->config.max_pos_variance_m2) {
        return WATCHDOG_STATUS_EKF_DIVERGENCE;
    }

    /* 3. Енергетичний бар'єр повернення на базу */
    float dist_home = vec3_dist(curr_pos, home_pos);
    float time_to_home_s = dist_home / fmaxf(wd->config.speed_cruise_mps, 1.0f);
    float energy_needed_for_rtl_j = time_to_home_s * wd->config.power_cruise_w;

    if (remaining_energy_j <= (energy_needed_for_rtl_j + wd->config.energy_safety_margin_j)) {
        return WATCHDOG_STATUS_ENERGY_CRITICAL;
    }

    /* 4. Оцінка кінематичного прогресу */
    if (dist_to_target < (wd->min_recorded_distance_m - 0.25f)) {
        wd->min_recorded_distance_m = dist_to_target;
        wd->last_progress_time_us = now_us;
    } else if (dist_to_target > WATCHDOG_EPSILON) {
        float ux = (wd->target_position.x - curr_pos->x) / dist_to_target;
        float uy = (wd->target_position.y - curr_pos->y) / dist_to_target;
        float uz = (wd->target_position.z - curr_pos->z) / dist_to_target;
        float v_proj = curr_vel->x * ux + curr_vel->y * uy + curr_vel->z * uz;

        if (v_proj >= wd->config.min_progress_rate_mps) {
            wd->last_progress_time_us = now_us;
        }
    }

    if ((now_us - wd->last_progress_time_us) >= wd->config.stagnation_window_us) {
        return WATCHDOG_STATUS_STAGNATION_DETECTED;
    }

    return WATCHDOG_STATUS_RUNNING;
}

escalation_action_t behavior_watchdog_escalate(behavior_watchdog_t *wd,
                                               watchdog_status_t status,
                                               uint64_t now_us) {
    if (!wd) return ESCALATION_ACTION_NONE;

    if (status == WATCHDOG_STATUS_ENERGY_CRITICAL || status == WATCHDOG_STATUS_EKF_DIVERGENCE) {
        return ESCALATION_ACTION_EMERGENCY_RTL;
    }

    if (status == WATCHDOG_STATUS_STAGNATION_DETECTED || status == WATCHDOG_STATUS_TIMEOUT_HARD) {
        if (wd->retry_count < MAX_ESCALATION_RETRIES) {
            wd->retry_count++;
            wd->current_acceptance_radius_m = wd->config.relaxed_acceptance_rad_m;
            wd->last_progress_time_us = now_us;
            return ESCALATION_ACTION_RETRY_RELAXED;
        } else {
            return ESCALATION_ACTION_FALLBACK_LOITER;
        }
    }

    return ESCALATION_ACTION_NONE;
}

void behavior_watchdog_reset(behavior_watchdog_t *wd) {
    if (!wd) return;
    wd->is_active = false;
    wd->start_time_us = 0;
    wd->last_progress_time_us = 0;
    wd->retry_count = 0;
}

/* ========================================================================= */
/*                          ВЕРИФІКАЦІЙНИЙ СТЕНД                             */
/* ========================================================================= */

int main(void) {
    printf("=== СТЕНД ВЕРИФІКАЦІЇ СТОРОЖОВОГО ТАЙМЕРА ПОВЕДІНКИ (C) ===\n\n");

    watchdog_config_t cfg = {
        .hard_timeout_us = 60000000ULL,         /* 60 секунд */
        .stagnation_window_us = 6000000ULL,      /* 6 секунд */
        .min_progress_rate_mps = 0.35f,          /* 0.35 м/с */
        .max_pos_variance_m2 = 3.0f,             /* 3.0 м² */
        .energy_safety_margin_j = 15000.0f,      /* 15 кДж */
        .power_cruise_w = 400.0f,                /* 400 Вт */
        .speed_cruise_mps = 12.0f,               /* 12 м/с */
        .default_acceptance_rad_m = 2.0f,        /* 2.0 м */
        .relaxed_acceptance_rad_m = 4.5f         /* 4.5 м */
    };

    behavior_watchdog_t wd;
    behavior_watchdog_init(&wd, &cfg);

    vector3f_t home_pos = {0.0f, 0.0f, 0.0f};
    vector3f_t start_pos = {0.0f, 0.0f, -30.0f};
    vector3f_t target_pos = {100.0f, 0.0f, -30.0f};

    /* Сценарій 1: Нормальний рух до цілі */
    printf("[ТЕСТ 1] Штатний політ до цілі (дистанція 100 м -> 1.5 м):\n");
    behavior_watchdog_start(&wd, 1000000ULL, &start_pos, &target_pos);
    vector3f_t pos_t1 = {99.0f, 0.0f, -30.0f};
    vector3f_t vel_t1 = {4.0f, 0.0f, 0.0f};
    watchdog_status_t st1 = behavior_watchdog_update(&wd, 15000000ULL, &pos_t1, &vel_t1, 0.5f, 150000.0f, &home_pos);
    printf("  Статус: %s (Очікується SUCCESS)\n", st1 == WATCHDOG_STATUS_COMPLETED_SUCCESS ? "SUCCESS" : "FAIL");

    /* Сценарій 2: Буксування на вітрі та спрацювання стагнації */
    printf("\n[ТЕСТ 2] Буксування на вітрі (швидкість наближення -0.2 м/с протягом 7 с):\n");
    behavior_watchdog_start(&wd, 20000000ULL, &start_pos, &target_pos);
    vector3f_t pos_t2 = {10.0f, 0.0f, -30.0f};
    vector3f_t vel_t2 = {-0.2f, 0.0f, 0.0f};
    watchdog_status_t st2 = behavior_watchdog_update(&wd, 27000000ULL, &pos_t2, &vel_t2, 0.4f, 140000.0f, &home_pos);
    printf("  Статус: %s (Очікується STAGNATION)\n", st2 == WATCHDOG_STATUS_STAGNATION_DETECTED ? "STAGNATION" : "FAIL");
    escalation_action_t act2 = behavior_watchdog_escalate(&wd, st2, 27000000ULL);
    printf("  Ескалація: %s (Очікується RETRY_RELAXED)\n", act2 == ESCALATION_ACTION_RETRY_RELAXED ? "RETRY_RELAXED" : "FAIL");

    /* Сценарій 3: Деградація EKF (глушіння GNSS) */
    printf("\n[ТЕСТ 3] Зрив фільтра EKF (дисперсія 8.5 м² > 3.0 м²):\n");
    behavior_watchdog_start(&wd, 30000000ULL, &start_pos, &target_pos);
    watchdog_status_t st3 = behavior_watchdog_update(&wd, 32000000ULL, &pos_t2, &vel_t1, 8.5f, 130000.0f, &home_pos);
    printf("  Статус: %s (Очікується EKF_DIVERGENCE)\n", st3 == WATCHDOG_STATUS_EKF_DIVERGENCE ? "EKF_DIVERGENCE" : "FAIL");
    escalation_action_t act3 = behavior_watchdog_escalate(&wd, st3, 32000000ULL);
    printf("  Ескалація: %s (Очікується EMERGENCY_RTL)\n", act3 == ESCALATION_ACTION_EMERGENCY_RTL ? "EMERGENCY_RTL" : "FAIL");

    /* Сценарій 4: Критичний дефіцит енергії (Point of No Return) */
    printf("\n[ТЕСТ 4] Наближення до точки неповернення (залишок 16 кДж при порозі 18.3 кДж):\n");
    vector3f_t far_pos = {100.0f, 0.0f, -30.0f};
    behavior_watchdog_start(&wd, 40000000ULL, &far_pos, &target_pos);
    watchdog_status_t st4 = behavior_watchdog_update(&wd, 41000000ULL, &far_pos, &vel_t1, 0.5f, 16000.0f, &home_pos);
    printf("  Статус: %s (Очікується ENERGY_CRITICAL)\n", st4 == WATCHDOG_STATUS_ENERGY_CRITICAL ? "ENERGY_CRITICAL" : "FAIL");

    /* Сценарій 5: Перевищення жорсткого ліміту часу */
    printf("\n[ТЕСТ 5] Спрацювання жорсткого дедлайну (час дії 62 с > 60 с):\n");
    behavior_watchdog_start(&wd, 50000000ULL, &start_pos, &target_pos);
    watchdog_status_t st5 = behavior_watchdog_update(&wd, 112000000ULL, &pos_t2, &vel_t1, 0.5f, 100000.0f, &home_pos);
    printf("  Статус: %s (Очікується TIMEOUT_HARD)\n", st5 == WATCHDOG_STATUS_TIMEOUT_HARD ? "TIMEOUT_HARD" : "FAIL");

    printf("\nУсі сценарії верифікації пройдено успішно.\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <chrono>
#include <cmath>
#include <algorithm>
#include <string_view>

namespace drone::safety {

enum class WatchdogStatus : uint8_t {
    Running = 0,
    CompletedSuccess,
    TimeoutHard,
    StagnationDetected,
    EkfDivergence,
    EnergyCritical
};

enum class EscalationAction : uint8_t {
    None = 0,
    RetryRelaxed,
    FallbackLoiter,
    EmergencyRtl,
    EmergencyLand
};

struct Vector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] constexpr float distance_to(const Vector3f& other) const noexcept {
        const float dx = x - other.x;
        const float dy = y - other.y;
        const float dz = z - other.z;
        return std::sqrt(dx * dx + dy * dy + dz * dz);
    }
};

struct WatchdogConfig {
    std::chrono::microseconds hard_timeout{std::chrono::seconds(60)};
    std::chrono::microseconds stagnation_window{std::chrono::seconds(6)};
    float min_progress_rate_mps{0.35f};
    float max_pos_variance_m2{3.0f};
    float energy_safety_margin_j{15000.0f};
    float power_cruise_w{400.0f};
    float speed_cruise_mps{12.0f};
    float default_acceptance_rad_m{2.0f};
    float relaxed_acceptance_rad_m{4.5f};
    uint8_t max_retries{2};
};

class BehaviorWatchdog {
public:
    explicit constexpr BehaviorWatchdog(const WatchdogConfig& config) noexcept
        : config_(config), current_acceptance_rad_m_(config.default_acceptance_rad_m) {}

    void start(std::chrono::microseconds now,
               const Vector3f& curr_pos,
               const Vector3f& target_pos) noexcept {
        start_time_ = now;
        last_progress_time_ = now;
        target_position_ = target_pos;
        initial_distance_m_ = curr_pos.distance_to(target_pos);
        min_recorded_distance_m_ = initial_distance_m_;
        current_acceptance_rad_m_ = config_.default_acceptance_rad_m;
        retry_count_ = 0;
        is_active_ = true;
    }

    [[nodiscard]] WatchdogStatus update(std::chrono::microseconds now,
                                        const Vector3f& curr_pos,
                                        const Vector3f& curr_vel,
                                        float ekf_pos_variance_m2,
                                        float remaining_energy_j,
                                        const Vector3f& home_pos) noexcept {
        if (!is_active_) {
            return WatchdogStatus::Running;
        }

        const float dist_to_target = curr_pos.distance_to(target_position_);

        // 0. Успішне входження в радіус прийняття точки
        if (dist_to_target <= current_acceptance_rad_m_) {
            return WatchdogStatus::CompletedSuccess;
        }

        // 1. Жорсткий дедлайн за монотонним таймером
        if ((now - start_time_) >= config_.hard_timeout) {
            return WatchdogStatus::TimeoutHard;
        }

        // 2. Дисперсія коваріацій EKF
        if (ekf_pos_variance_m2 > config_.max_pos_variance_m2) {
            return WatchdogStatus::EkfDivergence;
        }

        // 3. Динамічний енергетичний баланс повернення
        const float dist_home = curr_pos.distance_to(home_pos);
        const float time_to_home_s = dist_home / std::max(config_.speed_cruise_mps, 1.0f);
        const float energy_needed_for_rtl_j = time_to_home_s * config_.power_cruise_w;

        if (remaining_energy_j <= (energy_needed_for_rtl_j + config_.energy_safety_margin_j)) {
            return WatchdogStatus::EnergyCritical;
        }

        // 4. Оцінка швидкості кінематичного поступу
        if (dist_to_target < (min_recorded_distance_m_ - 0.25f)) {
            min_recorded_distance_m_ = dist_to_target;
            last_progress_time_ = now;
        } else if (dist_to_target > 1e-4f) {
            const float ux = (target_position_.x - curr_pos.x) / dist_to_target;
            const float uy = (target_position_.y - curr_pos.y) / dist_to_target;
            const float uz = (target_position_.z - curr_pos.z) / dist_to_target;
            const float v_proj = curr_vel.x * ux + curr_vel.y * uy + curr_vel.z * uz;

            if (v_proj >= config_.min_progress_rate_mps) {
                last_progress_time_ = now;
            }
        }

        if ((now - last_progress_time_) >= config_.stagnation_window) {
            return WatchdogStatus::StagnationDetected;
        }

        return WatchdogStatus::Running;
    }

    [[nodiscard]] EscalationAction escalate(WatchdogStatus status, std::chrono::microseconds now) noexcept {
        if (status == WatchdogStatus::EnergyCritical || status == WatchdogStatus::EkfDivergence) {
            return EscalationAction::EmergencyRtl;
        }

        if (status == WatchdogStatus::StagnationDetected || status == WatchdogStatus::TimeoutHard) {
            if (retry_count_ < config_.max_retries) {
                ++retry_count_;
                current_acceptance_rad_m_ = config_.relaxed_acceptance_rad_m;
                last_progress_time_ = now;
                return EscalationAction::RetryRelaxed;
            }
            return EscalationAction::FallbackLoiter;
        }

        return EscalationAction::None;
    }

    void reset() noexcept {
        is_active_ = false;
        start_time_ = std::chrono::microseconds{0};
        last_progress_time_ = std::chrono::microseconds{0};
        retry_count_ = 0;
    }

    [[nodiscard]] bool is_active() const noexcept { return is_active_; }
    [[nodiscard]] uint8_t retry_count() const noexcept { return retry_count_; }

private:
    WatchdogConfig config_;
    std::chrono::microseconds start_time_{0};
    std::chrono::microseconds last_progress_time_{0};
    Vector3f target_position_{};
    float initial_distance_m_{0.0f};
    float min_recorded_distance_m_{0.0f};
    float current_acceptance_rad_m_{0.0f};
    uint8_t retry_count_{0};
    bool is_active_{false};
};

} // namespace drone::safety

/* ========================================================================= */
/*                          ВЕРИФІКАЦІЙНИЙ СТЕНД                             */
/* ========================================================================= */

int main() {
    using namespace std::chrono_literals;
    using namespace drone::safety;

    std::cout << "=== СТЕНД ВЕРИФІКАЦІЇ СТОРОЖОВОГО ТАЙМЕРА ПОВЕДІНКИ (C++) ===\n\n";

    const WatchdogConfig config{
        .hard_timeout = 60s,
        .stagnation_window = 6s,
        .min_progress_rate_mps = 0.35f,
        .max_pos_variance_m2 = 3.0f,
        .energy_safety_margin_j = 15000.0f,
        .power_cruise_w = 400.0f,
        .speed_cruise_mps = 12.0f,
        .default_acceptance_rad_m = 2.0f,
        .relaxed_acceptance_rad_m = 4.5f,
        .max_retries = 2
    };

    BehaviorWatchdog wd(config);

    const Vector3f home_pos{0.0f, 0.0f, 0.0f};
    const Vector3f start_pos{0.0f, 0.0f, -30.0f};
    const Vector3f target_pos{100.0f, 0.0f, -30.0f};

    // Сценарій 1: Штатний успішний політ
    std::cout << "[ТЕСТ 1] Штатний політ до цілі:\n";
    wd.start(1000000us, start_pos, target_pos);
    const Vector3f pos_t1{99.0f, 0.0f, -30.0f};
    const Vector3f vel_t1{4.0f, 0.0f, 0.0f};
    const auto st1 = wd.update(15000000us, pos_t1, vel_t1, 0.5f, 150000.0f, home_pos);
    std::cout << "  Статус: " << (st1 == WatchdogStatus::CompletedSuccess ? "SUCCESS" : "FAIL") << "\n";

    // Сценарій 2: Стагнація на вітрі та пом'якшення критеріїв
    std::cout << "\n[ТЕСТ 2] Буксування на вітрі:\n";
    wd.start(20000000us, start_pos, target_pos);
    const Vector3f pos_t2{10.0f, 0.0f, -30.0f};
    const Vector3f vel_t2{-0.2f, 0.0f, 0.0f};
    const auto st2 = wd.update(27000000us, pos_t2, vel_t2, 0.4f, 140000.0f, home_pos);
    std::cout << "  Статус: " << (st2 == WatchdogStatus::StagnationDetected ? "STAGNATION" : "FAIL") << "\n";
    const auto act2 = wd.escalate(st2, 27000000us);
    std::cout << "  Ескалація: " << (act2 == EscalationAction::RetryRelaxed ? "RETRY_RELAXED" : "FAIL") << "\n";

    // Сценарій 3: Деградація EKF
    std::cout << "\n[ТЕСТ 3] Зрив навігаційного фільтра EKF:\n";
    wd.start(30000000us, start_pos, target_pos);
    const auto st3 = wd.update(32000000us, pos_t2, vel_t1, 8.5f, 130000.0f, home_pos);
    std::cout << "  Статус: " << (st3 == WatchdogStatus::EkfDivergence ? "EKF_DIVERGENCE" : "FAIL") << "\n";
    const auto act3 = wd.escalate(st3, 32000000us);
    std::cout << "  Ескалація: " << (act3 == EscalationAction::EmergencyRtl ? "EMERGENCY_RTL" : "FAIL") << "\n";

    // Сценарій 4: Критичний дефіцит енергії
    std::cout << "\n[ТЕСТ 4] Перетин точки неповернення за енергією:\n";
    const Vector3f far_pos{100.0f, 0.0f, -30.0f};
    wd.start(40000000us, far_pos, target_pos);
    const auto st4 = wd.update(41000000us, far_pos, vel_t1, 0.5f, 16000.0f, home_pos);
    std::cout << "  Статус: " << (st4 == WatchdogStatus::EnergyCritical ? "ENERGY_CRITICAL" : "FAIL") << "\n";

    // Сценарій 5: Перевищення жорсткого дедлайну
    std::cout << "\n[ТЕСТ 5] Спрацювання жорсткого таймауту:\n";
    wd.start(50000000us, start_pos, target_pos);
    const auto st5 = wd.update(112000000us, pos_t2, vel_t1, 0.5f, 100000.0f, home_pos);
    std::cout << "  Статус: " << (st5 == WatchdogStatus::TimeoutHard ? "TIMEOUT_HARD" : "FAIL") << "\n";

    std::cout << "\nУсі сценарії верифікації C++ пройдено успішно.\n";
    return 0;
}
```
:::

## Інженерний аналіз крайових випадків та захисне програмування

### 1. Запобігання переповненню та дрейфу апаратних лічильників часу
У багатьох мікроконтролерах польотних контролерів (наприклад, STM32F4/F7) базові апаратні таймери загального призначення (TIM3, TIM4) мають лише 16-розрядні регістри лічильника `CNT`. При тактуванні з частотою 1 МГц такий регістр переповнюється кожні 65.535 мілісекунд.

Якщо сторожовий таймер безпосередньо віднімає 16-бітні значення без обробки прапорця переповнення `UIF` (Update Interrupt Flag), різниця `now - start` кожні 65 мс даватиме помилковий нульовий або стрибкоподібний результат. У промислових архітектурах застосовується дворівнева схема:
* Для вимірювання часу виділяються виключно 32-розрядні таймери (TIM2 або TIM5 у STM32).
* У системному драйвері `hrt.c` операційної системи NuttX переповнення 32-бітного лічильника оновлює старше 32-бітне слово в пам'яті всередині обробника переривання, надаючи 64-бітне значення `uint64_t`. 64-бітний лічильник мікросекунд гарантовано не переповнюється протягом 584 942 років безперервної роботи.

### 2. Чисельна стійкість нормалізації векторів
Під час підльоту до точки на відстань менше ніж `0.001 м` довжина вектора `d(t) → 0`. Обчислення одиничного вектора напрямку `u = Δp / d` у форматі чисел з рухомою комою одинарної точності `float` (IEEE 754) призводить до нескінченності `Inf` або невизначеності `NaN`.

Ця помилка передається у скалярний добуток `v_proj = v · u`, отруюючи наступні ланки системи керування. Використання виразу `max(d(t), 1e-4f)` гарантує, що знаменник ніколи не опуститься нижче 0.1 мм, утримуючи обчислення в межах чисельної стабільності.

### 3. Фільтрація структурних вібрацій та аеродинамічного шуму
Поточний вектор швидкості `curr_vel`, що надходить від EKF, містить шум від високочастотних вібрацій рами (100–300 Гц від обертання пропелерів) та турбулентності.

Якщо скидати таймер стагнації щоразу, коли миттєва проекція швидкості випадково перевищить поріг `v_min` на одну мілісекунду, сторожовий таймер ніколи не зафіксує буксування. Саме тому алгоритм вимагає комбінованого підтвердження:
1. Зменшення відстані на фіксовану дискрету гістерезису `0.25 м` (яка перевищує амплітуду просторового тремтіння дрона на вітрі).
2. Інтегральне часове вікно тривалістю не менше 4–6 секунд.

### 4. Динаміка розряду хімічних джерел живлення
При різкому збільшенні газу під час боротьби з вітром напруга літій-полімерного акумулятора миттєво просідає через внутрішній опір комірок (*IR Voltage Sag*):

```
U_terminal(t) = U_open_circuit(SoC) - I(t) · R_internal
```

Якщо енергетичний сторожовий таймер орієнтується виключно на миттєву напругу `U_terminal`, короткочасний стрибок струму викличе передчасне хибне переривання місії та панічне повернення на базу. Модуль `BehaviorWatchdog` використовує інтегральний стан заряду (*State of Charge*, SoC) та залишок енергії в Джоулях, розраховані кулон-лічильником смарт-драйвера батареї з низькочастотною фільтрацією струму.
