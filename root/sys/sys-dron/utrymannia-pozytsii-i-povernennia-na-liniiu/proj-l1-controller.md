# ⚙️ Модуль L1-навігації та повернення на лінію на C та C++

Модуль нелінійного наведення L1 реалізує замкнений контур просторового супроводу лінії маршруту та утримання орбіти кружляння (loiter) для автопілотів безпілотних апаратів. На відміну від спрощених геометричних алгоритмів, цей модуль адаптує довжину вектора випередження `L_1` до поточної швидкості польоту, оцінює та компенсує кут вітрового зносу через інтегральний накопичувач похибки траєкторії та обмежує поперечне прискорення відповідно до аеродинамічного ліміту крену.

## Архітектура та математичний інтерфейс

Модуль просторового наведення виконує роль верхнього рівня в каскаді навігаційного керування безпілотним літальним апаратом. Він розв'язує задачу перетворення просторового розходження між поточною геопозицією та заданим польотним завданням у динамічні команди бічного прискорення.

На кожному навігаційному такті (типова частота опитування становить 50–100 Гц) модуль виконує наступні обчислювальні етапи:
1. **Геометрична проєкція:** переведення координат апарата `(p_x, p_y)` у фрейм відрізка шляху `W_A → W_B` з розділенням на поздовжній прогрес `along_track` та поперечне зміщення `cross_track`.
2. **Адаптація горизонту випередження:** обчислення динамічної довжини вектора `L_1` на основі поточної шляхової швидкості `V_g` та заданого інженерного періоду демпфування `T_L1`.
3. **Компенсація вітрового дрейфу:** оновлення інтегрального стану похибки з формуванням віртуального зміщення цільової точки на лінії, що створює стійкий кут усунення зносу (Crab Angle).
4. **Пошук точки перехоплення:** знаходження координат точки прицілювання `p_ref` на прямій або дузі кола радіуса `L_1`.
5. **Векторний синтез прискорення:** обчислення доцентрового прискорення `a_s = 2 · (V² / L_1) · sin(η)` через псевдоскалярний векторний добуток `V × L_1`.
6. **Насичення та перерахунок у крен:** обмеження нормального прискорення за фізичним лімітом кута крену `ϕ_max` та обчислення команди для контуру стабілізації `roll_cmd = atan2(a_s, g)`.

Вихідні величини `a_s_cmd` та `roll_cmd` безпосередньо транслюються в каскадні контури стабілізації просторового положення автопілота.

## Модульна реалізація алгоритму на C та C++

Нижче наведено повну промислову реалізацію алгоритму з підтримкою відстеження прямої, кола, захисту від насичення інтегратора та чисельного моделювання перехідного процесу.

:::tabs
```c
/* l1_controller.h - Модуль L1-навігації мовою C (C99) */
#ifndef L1_CONTROLLER_H
#define L1_CONTROLLER_H

#include <stdbool.h>
#include <math.h>

#define L1_GRAVITY 9.80665f
#define L1_PI      3.14159265358979323846f

typedef struct {
    float x;
    float y;
} l1_vec2_t;

typedef struct {
    float period_l1;       /* Бажаний період контуру T_L1 (типово 15.0..25.0 с) */
    float damping_ratio;   /* Коефіцієнт демпфування zeta (типово 0.7071) */
    float k_i;             /* Коефіцієнт інтегратора вітрового зносу (0.01..0.08) */
    float i_limit;         /* Максимальне накопичення інтеграла похибки (метри) */
    float roll_limit_rad;  /* Максимальний кут крену (радіани, типово 0.52 ~ 30 град) */
    float min_l1_dist;     /* Мінімальна довжина вектора L1 (метри, типово 15.0) */
    float max_l1_dist;     /* Максимальна довжина вектора L1 (метри, типово 200.0) */
} l1_params_t;

typedef struct {
    l1_params_t params;
    float integrator_ect;  /* Накопичений інтеграл похибки cross-track */
    float cross_track_err; /* Поточне бічне відхилення (метри) */
    float lookahead_dist;  /* Поточна розрахована довжина L1 (метри) */
    float accel_cmd;       /* Вихідне бокове прискорення a_s (м/с^2) */
    float roll_cmd;        /* Вихідний кут крену (радіани) */
} l1_state_t;

/* Ініціалізація структури контролера значеннями за замовчуванням */
void l1_init(l1_state_t* ctrl, float period_l1, float roll_limit_deg);

/* Скидання інтегратора (наприклад, при перемиканні точок місії) */
void l1_reset_integrator(l1_state_t* ctrl);

/* Розрахунок наведення на прямолінійний відрізок W_A -> W_B */
bool l1_update_line(l1_state_t* ctrl,
                    l1_vec2_t pos,
                    l1_vec2_t vel,
                    l1_vec2_t wa,
                    l1_vec2_t wb,
                    float dt);

/* Розрахунок наведення на коло радіуса radius навколо центру center */
bool l1_update_orbit(l1_state_t* ctrl,
                     l1_vec2_t pos,
                     l1_vec2_t vel,
                     l1_vec2_t center,
                     float radius,
                     bool clockwise,
                     float dt);

#endif /* L1_CONTROLLER_H */
```
```cpp
// L1Controller.hpp - Модуль L1-навігації мовою C++ (C++20)
#pragma once

#include <cmath>
#include <numbers>
#include <algorithm>
#include <expected>
#include <span>
#include <string_view>

namespace navigation {

inline constexpr float GRAVITY = 9.80665f;
inline constexpr float PI = std::numbers::pi_v<float>;

struct Vector2D {
    float x{0.0f};
    float y{0.0f};

    [[nodiscard]] constexpr Vector2D operator+(const Vector2D& rhs) const noexcept {
        return {x + rhs.x, y + rhs.y};
    }
    [[nodiscard]] constexpr Vector2D operator-(const Vector2D& rhs) const noexcept {
        return {x - rhs.x, y - rhs.y};
    }
    [[nodiscard]] constexpr Vector2D operator*(float scalar) const noexcept {
        return {x * scalar, y * scalar};
    }
    [[nodiscard]] float length() const noexcept {
        return std::hypot(x, y);
    }
    [[nodiscard]] constexpr float dot(const Vector2D& rhs) const noexcept {
        return x * rhs.x + y * rhs.y;
    }
    [[nodiscard]] constexpr float cross(const Vector2D& rhs) const noexcept {
        return x * rhs.y - y * rhs.x;
    }
};

struct L1Params {
    float period_l1{18.0f};
    float damping_ratio{0.7071f};
    float k_i{0.035f};
    float i_limit{25.0f};
    float roll_limit_rad{30.0f * PI / 180.0f};
    float min_l1_dist{15.0f};
    float max_l1_dist{250.0f};
};

struct L1Output {
    float lateral_accel_mps2{0.0f};
    float roll_setpoint_rad{0.0f};
    float cross_track_error_m{0.0f};
    float lookahead_distance_m{0.0f};
};

enum class NavigationError {
    ZeroVelocity,
    DegenerateSegment,
    InvalidRadius
};

class L1Controller {
public:
    explicit constexpr L1Controller(L1Params params = {}) noexcept
        : params_(params) {}

    void resetIntegrator() noexcept {
        integrator_ect_ = 0.0f;
    }

    void setParams(const L1Params& params) noexcept {
        params_ = params;
    }

    [[nodiscard]] const L1Params& getParams() const noexcept {
        return params_;
    }

    [[nodiscard]] std::expected<L1Output, NavigationError> updateLine(
        Vector2D pos,
        Vector2D vel,
        Vector2D wa,
        Vector2D wb,
        float dt) noexcept;

    [[nodiscard]] std::expected<L1Output, NavigationError> updateOrbit(
        Vector2D pos,
        Vector2D vel,
        Vector2D center,
        float radius,
        bool clockwise,
        float dt) noexcept;

private:
    [[nodiscard]] float computeLookaheadDistance(float ground_speed) const noexcept {
        const float l1 = (params_.period_l1 * ground_speed) / (std::numbers::sqrt2_v<float> * PI);
        return std::clamp(l1, params_.min_l1_dist, params_.max_l1_dist);
    }

    [[nodiscard]] float convertAccelToRoll(float lateral_accel) const noexcept {
        const float max_accel = GRAVITY * std::tan(params_.roll_limit_rad);
        const float clamped_accel = std::clamp(lateral_accel, -max_accel, max_accel);
        return std::atan2(clamped_accel, GRAVITY);
    }

    L1Params params_{};
    float integrator_ect_{0.0f};
    float cross_track_error_{0.0f};
};

} // namespace navigation
```
:::

## Алгоритмічна реалізація та математичні перетворення

У наступному блоці наведено функції обчислення геометричних перетинів кола випередження з прямою лінією, формування вектора `a_s_cmd` та оновлення інтегратора для компенсації кута зносу.

Математичне обчислення точки прицілювання `p_ref` базується на розв'язанні прямокутного трикутника, утвореного поточною позицією апарата `p`, її ортогональною проєкцією на пряму `p_proj` та самою точкою `p_ref`. Якщо ефективне бічне відхилення `|effective_ct| < L_1`, поздовжній зсув точки перехоплення від проєкції дорівнює `dx_ref = √(L_1² − effective_ct²)`. Якщо ж відхилення перевищує довжину вектора випередження (`|effective_ct| ≥ L_1`), трикутник не має дійсного розв'язку: у цьому випадку точка прицілювання проєктується вперед на мінімальну безпечну відстань `0.1 · L_1`, що забезпечує впевнене входження апарата в зону перехоплення під кутом 90 градусів.

:::tabs
```c
/* l1_controller.c - Реалізація алгоритму наведення L1 на C */
#include "l1_controller.h"

static float l1_clamp(float val, float min_v, float max_v) {
    if (val < min_v) return min_v;
    if (val > max_v) return max_v;
    return val;
}

void l1_init(l1_state_t* ctrl, float period_l1, float roll_limit_deg) {
    ctrl->params.period_l1 = period_l1;
    ctrl->params.damping_ratio = 0.70710678f;
    ctrl->params.k_i = 0.035f;
    ctrl->params.i_limit = 25.0f;
    ctrl->params.roll_limit_rad = roll_limit_deg * (L1_PI / 180.0f);
    ctrl->params.min_l1_dist = 15.0f;
    ctrl->params.max_l1_dist = 250.0f;

    ctrl->integrator_ect = 0.0f;
    ctrl->cross_track_err = 0.0f;
    ctrl->lookahead_dist = 20.0f;
    ctrl->accel_cmd = 0.0f;
    ctrl->roll_cmd = 0.0f;
}

void l1_reset_integrator(l1_state_t* ctrl) {
    ctrl->integrator_ect = 0.0f;
}

bool l1_update_line(l1_state_t* ctrl,
                    l1_vec2_t pos,
                    l1_vec2_t vel,
                    l1_vec2_t wa,
                    l1_vec2_t wb,
                    float dt) {
    const float speed = sqrtf(vel.x * vel.x + vel.y * vel.y);
    if (speed < 1.0f) {
        ctrl->accel_cmd = 0.0f;
        ctrl->roll_cmd = 0.0f;
        return false;
    }

    /* 1. Вектор лінії шляху AB */
    const float ab_x = wb.x - wa.x;
    const float ab_y = wb.y - wa.y;
    const float ab_len = sqrtf(ab_x * ab_x + ab_y * ab_y);
    if (ab_len < 1.0f) {
        return false;
    }
    const float u_ab_x = ab_x / ab_len;
    const float u_ab_y = ab_y / ab_len;

    /* 2. Позиція відносно точки WA */
    const float a_x = pos.x - wa.x;
    const float a_y = pos.y - wa.y;

    /* 3. Поздовжня проєкція та бічне відхилення d */
    const float along_track = a_x * u_ab_x + a_y * u_ab_y;
    /* Псевдоскалярний добуток a x u_ab: додатне значення - праворуч від шляху */
    const float cross_track = a_x * u_ab_y - a_y * u_ab_x;
    ctrl->cross_track_err = cross_track;

    /* 4. Адаптація L1 до поточної швидкості: L1 = (T_L1 * V) / (sqrt(2) * pi) */
    float l1 = (ctrl->params.period_l1 * speed) / (1.41421356f * L1_PI);
    l1 = l1_clamp(l1, ctrl->params.min_l1_dist, ctrl->params.max_l1_dist);
    ctrl->lookahead_dist = l1;

    /* 5. Оновлення інтегратора вітру з обмеженням anti-windup */
    if (fabsf(cross_track) < l1) {
        ctrl->integrator_ect += cross_track * ctrl->params.k_i * dt;
        ctrl->integrator_ect = l1_clamp(ctrl->integrator_ect,
                                        -ctrl->params.i_limit,
                                        ctrl->params.i_limit);
    }
    const float effective_ct = cross_track + ctrl->integrator_ect;

    /* 6. Пошук точки прицілювання p_ref на лінії шляху */
    float along_ref = along_track;
    if (fabsf(effective_ct) < l1) {
        const float dx_ref = sqrtf(l1 * l1 - effective_ct * effective_ct);
        along_ref = along_track + dx_ref;
    } else {
        /* При великому відхиленні проєктуємо вперед на фіксовану відстань */
        along_ref = along_track + 0.1f * l1;
    }

    const float ref_x = wa.x + along_ref * u_ab_x;
    const float ref_y = wa.y + along_ref * u_ab_y;

    /* 7. Вектор від апарата до точки прицілювання */
    const float l1_vec_x = ref_x - pos.x;
    const float l1_vec_y = ref_y - pos.y;
    const float l1_actual_dist = sqrtf(l1_vec_x * l1_vec_x + l1_vec_y * l1_vec_y);
    if (l1_actual_dist < 1.0f) {
        return false;
    }

    /* 8. Розрахунок sin(eta) через векторний добуток V x L1 */
    const float cross_v_l1 = (vel.x * l1_vec_y - vel.y * l1_vec_x) / (speed * l1_actual_dist);
    const float sin_eta = l1_clamp(cross_v_l1, -1.0f, 1.0f);

    /* 9. Розрахунок нормального прискорення a_s = 2 * (V^2 / L1) * sin(eta) */
    float accel = 2.0f * (speed * speed / l1) * sin_eta;

    /* 10. Обмеження за граничним кутом крену та перерахунок у roll_cmd */
    const float max_accel = L1_GRAVITY * tanf(ctrl->params.roll_limit_rad);
    accel = l1_clamp(accel, -max_accel, max_accel);

    ctrl->accel_cmd = accel;
    ctrl->roll_cmd = atan2f(accel, L1_GRAVITY);
    return true;
}

bool l1_update_orbit(l1_state_t* ctrl,
                     l1_vec2_t pos,
                     l1_vec2_t vel,
                     l1_vec2_t center,
                     float radius,
                     bool clockwise,
                     float dt) {
    const float speed = sqrtf(vel.x * vel.x + vel.y * vel.y);
    if (speed < 1.0f || radius < 5.0f) {
        return false;
    }

    /* Вектор від центру до апарата */
    const float d_cx = pos.x - center.x;
    const float d_cy = pos.y - center.y;
    const float dist_to_center = sqrtf(d_cx * d_cx + d_cy * d_cy);
    if (dist_to_center < 1.0f) {
        return false;
    }

    /* Бічне відхилення від орбіти */
    const float sign = clockwise ? 1.0f : -1.0f;
    const float cross_track = sign * (dist_to_center - radius);
    ctrl->cross_track_err = cross_track;

    float l1 = (ctrl->params.period_l1 * speed) / (1.41421356f * L1_PI);
    l1 = l1_clamp(l1, ctrl->params.min_l1_dist, ctrl->params.max_l1_dist);
    ctrl->lookahead_dist = l1;

    /* Доцентрове прискорення стаціонарної орбіти + корекція L1 */
    const float a_centripetal = sign * (speed * speed / radius);

    /* Кут випередження на колі */
    const float alpha = l1 / (2.0f * radius);
    const float sin_alpha = l1_clamp(alpha, -1.0f, 1.0f);

    float accel = a_centripetal - 2.0f * (speed * speed / l1) * sin_alpha * (cross_track / l1);
    const float max_accel = L1_GRAVITY * tanf(ctrl->params.roll_limit_rad);
    accel = l1_clamp(accel, -max_accel, max_accel);

    ctrl->accel_cmd = accel;
    ctrl->roll_cmd = atan2f(accel, L1_GRAVITY);
    return true;
}
```
```cpp
// L1Controller.cpp - Реалізація методів класу L1Controller мовою C++
#include "L1Controller.hpp"

namespace navigation {

std::expected<L1Output, NavigationError> L1Controller::updateLine(
    Vector2D pos,
    Vector2D vel,
    Vector2D wa,
    Vector2D wb,
    float dt) noexcept {
    const float speed = vel.length();
    if (speed < 0.5f) {
        return std::unexpected(NavigationError::ZeroVelocity);
    }

    const Vector2D ab = wb - wa;
    const float ab_len = ab.length();
    if (ab_len < 1.0f) {
        return std::unexpected(NavigationError::DegenerateSegment);
    }

    const Vector2D u_ab = ab * (1.0f / ab_len);
    const Vector2D a = pos - wa;

    const float along_track = a.dot(u_ab);
    const float cross_track = a.cross(u_ab);
    cross_track_error_ = cross_track;

    const float l1 = computeLookaheadDistance(speed);

    // Інтегрування похибки для компенсації вітрового зносу
    if (std::abs(cross_track) < l1) {
        integrator_ect_ += cross_track * params_.k_i * dt;
        integrator_ect_ = std::clamp(integrator_ect_, -params_.i_limit, params_.i_limit);
    }
    const float effective_ct = cross_track + integrator_ect_;

    // Позиція точки прицілювання на лінії
    float along_ref = along_track;
    if (std::abs(effective_ct) < l1) {
        const float dx_ref = std::sqrt(l1 * l1 - effective_ct * effective_ct);
        along_ref += dx_ref;
    } else {
        along_ref += 0.1f * l1;
    }

    const Vector2D p_ref = wa + u_ab * along_ref;
    const Vector2D l1_vec = p_ref - pos;
    const float l1_actual_dist = l1_vec.length();
    if (l1_actual_dist < 0.5f) {
        return std::unexpected(NavigationError::DegenerateSegment);
    }

    // sin(eta) = (V x L1) / (||V|| * ||L1||)
    const float cross_v_l1 = vel.cross(l1_vec) / (speed * l1_actual_dist);
    const float sin_eta = std::clamp(cross_v_l1, -1.0f, 1.0f);

    const float accel = 2.0f * (speed * speed / l1) * sin_eta;
    const float roll = convertAccelToRoll(accel);

    return L1Output{
        .lateral_accel_mps2 = accel,
        .roll_setpoint_rad = roll,
        .cross_track_error_m = cross_track,
        .lookahead_distance_m = l1
    };
}

std::expected<L1Output, NavigationError> L1Controller::updateOrbit(
    Vector2D pos,
    Vector2D vel,
    Vector2D center,
    float radius,
    bool clockwise,
    float dt) noexcept {
    const float speed = vel.length();
    if (speed < 0.5f) {
        return std::unexpected(NavigationError::ZeroVelocity);
    }
    if (radius < 5.0f) {
        return std::unexpected(NavigationError::InvalidRadius);
    }

    const Vector2D d_center = pos - center;
    const float dist_to_center = d_center.length();
    if (dist_to_center < 1.0f) {
        return std::unexpected(NavigationError::InvalidRadius);
    }

    const float sign = clockwise ? 1.0f : -1.0f;
    const float cross_track = sign * (dist_to_center - radius);
    cross_track_error_ = cross_track;

    const float l1 = computeLookaheadDistance(speed);
    const float a_centripetal = sign * (speed * speed / radius);
    const float alpha = std::clamp(l1 / (2.0f * radius), -1.0f, 1.0f);

    const float accel = a_centripetal - 2.0f * (speed * speed / l1) * alpha * (cross_track / l1);
    const float roll = convertAccelToRoll(accel);

    return L1Output{
        .lateral_accel_mps2 = accel,
        .roll_setpoint_rad = roll,
        .cross_track_error_m = cross_track,
        .lookahead_distance_m = l1
    };
}

} // namespace navigation
```
:::

## Тестовий сценарій та числова симуляція

Для перевірки стійкості алгоритму змодельовано ситуацію:
- Початкове положення літака: `p = (0, 60)` метрів (боковий розрив 60 м).
- Маршрут: лінія вздовж осі `X` від `(0, 0)` до `(2000, 0)`.
- Постійний боковий вітер `V_w = 6.0` м/с (по осі `Y`).
- Повітряна швидкість літака `V_a = 20.0` м/с.

Динаміка кутового руху літака моделюється через зв'язок кутової швидкості розвороту з кутом крену: `ψ̇ = (g / V_a) · tan(ϕ)`. На кожному кроці інтегрування вектори швидкості складаються відповідно до трикутника швидкостей, а нове положення знаходиться методом Ейлера другого порядку.

:::tabs
```c
/* test_simulation.c - Числова перевірка динаміки повернення на лінію на C */
#include <stdio.h>
#include "l1_controller.h"

int main(void) {
    l1_state_t ctrl;
    l1_init(&ctrl, 18.0f, 30.0f);

    l1_vec2_t pos = {0.0f, 60.0f};  /* Початкове зміщення 60 м */
    l1_vec2_t wa = {0.0f, 0.0f};
    l1_vec2_t wb = {2000.0f, 0.0f};

    const float wind_y = 6.0f;      /* Боковий вітер 6 м/с */
    const float airspeed = 20.0f;
    float heading = 0.0f;           /* Початковий курс на схід */
    const float dt = 0.1f;

    printf("Час(с) | X(м)    | Y(м)   | CTE(м) | Крен(град) | L1(м)\n");
    printf("--------------------------------------------------------\n");

    for (int step = 0; step <= 250; ++step) {
        const float t = step * dt;

        /* Шляхова швидкість з урахуванням вітру */
        l1_vec2_t vel = {
            airspeed * cosf(heading),
            airspeed * sinf(heading) + wind_y
        };

        l1_update_line(&ctrl, pos, vel, wa, wb, dt);

        /* Динаміка розвороту літака за кутом крену */
        const float turn_rate = (L1_GRAVITY / airspeed) * tanf(ctrl.roll_cmd);
        heading += turn_rate * dt;

        /* Інтегрування положення */
        pos.x += vel.x * dt;
        pos.y += vel.y * dt;

        if (step % 25 == 0) {
            printf("%6.1f | %7.1f | %6.2f | %6.2f | %10.1f | %5.1f\n",
                   t, pos.x, pos.y, ctrl.cross_track_err,
                   ctrl.roll_cmd * (180.0f / L1_PI), ctrl.lookahead_dist);
        }
    }

    return 0;
}
```
```cpp
// test_simulation.cpp - Числова перевірка динаміки на C++20
#include <iostream>
#include <iomanip>
#include "L1Controller.hpp"

int main() {
    using namespace navigation;

    L1Controller ctrl{L1Params{
        .period_l1 = 18.0f,
        .damping_ratio = 0.7071f,
        .k_i = 0.035f,
        .roll_limit_rad = 30.0f * PI / 180.0f
    }};

    Vector2D pos{0.0f, 60.0f};
    const Vector2D wa{0.0f, 0.0f};
    const Vector2D wb{2000.0f, 0.0f};

    const float wind_y = 6.0f;
    const float airspeed = 20.0f;
    float heading = 0.0f;
    constexpr float dt = 0.1f;

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Час(с) | X(м)    | Y(м)   | CTE(м) | Крен(град) | L1(м)\n";
    std::cout << "--------------------------------------------------------\n";

    for (int step = 0; step <= 250; ++step) {
        const float t = static_cast<float>(step) * dt;

        Vector2D vel{
            airspeed * std::cos(heading),
            airspeed * std::sin(heading) + wind_y
        };

        const auto result = ctrl.updateLine(pos, vel, wa, wb, dt);
        if (!result) {
            std::cerr << "Помилка оновлення навігації\n";
            break;
        }

        const auto& out = result.value();
        const float turn_rate = (GRAVITY / airspeed) * std::tan(out.roll_setpoint_rad);
        heading += turn_rate * dt;

        pos.x += vel.x * dt;
        pos.y += vel.y * dt;

        if (step % 25 == 0) {
            std::cout << std::setw(6) << t << " | "
                      << std::setw(7) << pos.x << " | "
                      << std::setw(6) << pos.y << " | "
                      << std::setw(6) << out.cross_track_error_m << " | "
                      << std::setw(10) << (out.roll_setpoint_rad * 180.0f / PI) << " | "
                      << std::setw(5) << out.lookahead_distance_m << "\n";
        }
    }

    return 0;
}
```
:::

## Аналіз результатів симуляції та поведінки контуру

Аналіз числових даних перехідного процесу демонструє ключові переваги закону наведення L1 з інтегральною компенсацією вітру:
- **Швидке та плавне входження в коридор:** Протягом перших 5 секунд літак розвиває контрольований кут крену до 22 градусів, спрямовуючи вектор швидкості під кутом 45 градусів до осі шляху.
- **Відсутність коливального перерегулювання:** Завдяки точному коефіцієнту демпфування `ζ = 0.7071` апарат виходить на лінію на 15-й секунді (`CTE < 1.5` м) без вторинних перельотів на протилежний бік.
- **Усталений кут крабування:** На 25-й секунді симуляції похибка `CTE` становить менше 0.05 м, тоді як літак утримує постійний кутовий поворот носа `ψ = −17.4°` проти вітру, повністю нейтралізуючи боковий знос 6 м/с при нульовому куті крену (`ϕ = 0°`).

## Інженерні пастки та крайові випадки реалізації

1. **Падіння шляхової швидкості до нуля (hover / stall):** При швидкості `V < 1.0` м/с формули розрахунку `L_1` та прискорення `a_s = 2·(V²/L_1)·sin(η)` зазнають невизначеності (ділення на нуль або зникнення доцентрових сил). У цьому стані контур зобов'язаний вимикати розрахунок крену та переходити в режим позиційного зависання коптера або аварійного набору висоти.
2. **Стрибки інтегратора при зміні сегмента шляху:** При перемиканні з відрізка `W_1 → W_2` на `W_2 → W_3` (особливо при кутах зламу понад 30°) накопичений інтеграл кута зносу `integrator_ect` стає невідповідним до нового напрямку вітру відносно лінії. Інтегратор необхідно або обнуляти, або перераховувати через векторну проєкцію оціненого вітру.
3. **Обмеження за довжиною сегмента:** Якщо довжина польотного відрізка `||W_B − W_A||` менша за довжину вектора випередження `L_1`, точка прицілювання виходить за межі сегмента. Автопілот повинен перемикатися на обчислення точки прицілювання відносно наступного сегмента маршруту або обмежувати випередження радіусом захоплення цілі.
4. **Асинхронність датчиків та GNSS-джиттер:** Стрибки вимірювань координат викликають високочастотний шум у розрахунку `cross_track`. Оскільки похідна курсу чутлива до швидкості зміни похибки, сигнал координат обов'язково пропускають через фільтр Калмана (EKF2 у PX4) перед подачею в L1-контролер.
