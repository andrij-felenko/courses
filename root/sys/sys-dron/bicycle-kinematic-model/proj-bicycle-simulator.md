# Реалізація кінематичного симулятора та інтегратора позиції на C та C++

У системах автономного керування наземними роботами (роверами, безпілотними платформами, польовими машинами та складськими AGV) кінематична модель велосипеда використовується у двох взаємодоповнюючих задачах реального часу:

1. **Інтегратор одометрії (Dead Reckoning):** обчислення приросту глобальних координат `(x, y, θ)` робота за виміряною швидкістю коліс `v` (від енкодерів) та поточним кутом вивороту керма `δ` (від абсолютного давача положення сервоприводу). Цей блок працює з високою частотою (100–500 Гц) безпосередньо в контурі польотного контролера або мікроконтролера керування рухом.
2. **Кінематичний предиктор траєкторії (Forward Simulation):** багатокрокове прогнозування стану апарата вперед у часі на горизонт від одного до п'яти секунд. Предиктор необхідний для алгоритмів оптимізації траєкторій (Model Predictive Control, lattice planners), де потрібно оцінити сотні кандидатних траєкторій на кожен такт планування.

Нижче наведено модульну та детерміновану реалізацію кінематичного симулятора та інтегратора на мовах C та C++ трьома методами: прямим методом Ейлера, методом точної кругової дуги (Exact Arc) та класичним методом Рунге-Кутти 4-го порядку (RK4), з урахуванням фізичних обмежень кермового приводу.

## 1. Архітектура стану та фізичні обмеження

Вектор стану робота описується структурою з п'яти величин:
- `x, y` — просторові координати на площині (метри);
- `theta` — кут курсу (радіани, орієнтація поздовжньої осі кузова відносно світової осі `X`);
- `v` — поздовжня лінійна швидкість (метри на секунду);
- `delta` — поточний кут вивороту переднього керованого колеса (радіани).

Керуючими впливами на кожному кроці дискретизації `dt` є цільова швидкість `target_v` та цільовий кут керма `target_delta`.

Реальний виконавчий механізм не здатний змінити кут керма чи швидкість миттєво. Тому симулятор моделює обмеження першої похідної:
- `max_steer_rate` — максимальна швидкість повороту коліс сервоприводом (рад/с);
- `max_accel` — граничне лінійне прискорення та гальмування приводу (м/с²);
- `max_steer` — механічний упор кермової рейки (граничний кут `δ`).

## 2. Реалізація симулятора на C та C++

:::tabs
```c
#include <math.h>
#include <stdbool.h>

/* Геометричні параметри та фізичні обмеження шасі */
typedef struct {
    double l_f;           /* Відстань від центру мас до передньої осі, м */
    double l_r;           /* Відстань від центру мас до задньої осі, м   */
    double max_steer;     /* Максимальний кут вивороту керма, рад       */
    double max_steer_rate;/* Максимальна швидкість перекладки, рад/с    */
    double max_accel;     /* Максимальне лінійне прискорення, м/с^2     */
} BicycleParams;

/* Вектор стану кінематичної моделі */
typedef struct {
    double x;             /* Координата X у світовій системі, м */
    double y;             /* Координата Y у світовій системі, м */
    double theta;         /* Курс (yaw), рад                    */
    double v;             /* Поздовжня лінійна швидкість, м/с   */
    double delta;         /* Поточний кут повороту коліс, рад   */
} BicycleState;

/* Похідні стану за часом */
typedef struct {
    double dx;
    double dy;
    double dtheta;
    double dv;
    double ddelta;
} BicycleDerivatives;

/* Метод чисельного інтегрування */
typedef enum {
    INTEGRATION_EULER,
    INTEGRATION_EXACT_ARC,
    INTEGRATION_RK4
} IntegrationMethod;

/* Обчислення похідних стану відносно центру мас */
static BicycleDerivatives bicycle_eval_derivatives(
    const BicycleState *state,
    double accel,
    double steer_rate,
    const BicycleParams *params)
{
    BicycleDerivatives deriv;
    double L = params->l_f + params->l_r;

    /* Кут зсуву швидкості (side-slip angle beta) */
    double beta = atan((params->l_r / L) * tan(state->delta));

    deriv.dx = state->v * cos(state->theta + beta);
    deriv.dy = state->v * sin(state->theta + beta);
    deriv.dtheta = (state->v / L) * tan(state->delta) * cos(beta);
    deriv.dv = accel;
    deriv.ddelta = steer_rate;

    return deriv;
}

/* Нормалізація кута в діапазон [-pi, pi] */
static double normalize_angle(double angle)
{
    while (angle > M_PI) angle -= 2.0 * M_PI;
    while (angle < -M_PI) angle += 2.0 * M_PI;
    return angle;
}

/* Обмеження величини за модулем */
static double clamp_value(double val, double min_val, double max_val)
{
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

/* Один крок симуляції (інтеграція стану на dt) */
bool bicycle_step(
    BicycleState *state,
    double target_v,
    double target_delta,
    double dt,
    const BicycleParams *params,
    IntegrationMethod method)
{
    if (!state || !params || dt <= 0.0) {
        return false;
    }

    /* 1. Розрахунок керуючих похідних з урахуванням обмежень приводу */
    double v_error = target_v - state->v;
    double accel = clamp_value(v_error / dt, -params->max_accel, params->max_accel);

    double delta_clamped = clamp_value(target_delta, -params->max_steer, params->max_steer);
    double delta_error = delta_clamped - state->delta;
    double steer_rate = clamp_value(delta_error / dt, -params->max_steer_rate, params->max_steer_rate);

    if (method == INTEGRATION_EULER) {
        /* Метод Ейлера 1-го порядку */
        BicycleDerivatives d = bicycle_eval_derivatives(state, accel, steer_rate, params);
        state->x += d.dx * dt;
        state->y += d.dy * dt;
        state->theta += d.dtheta * dt;
        state->v += d.dv * dt;
        state->delta += d.ddelta * dt;
    }
    else if (method == INTEGRATION_EXACT_ARC) {
        /* Метод точної кругової дуги для постійної кривини на відрізку dt */
        double L = params->l_f + params->l_r;
        double beta = atan((params->l_r / L) * tan(state->delta));
        double omega = (state->v / L) * tan(state->delta) * cos(beta);
        double delta_theta = omega * dt;

        if (fabs(omega) > 1e-6) {
            double R_cg = state->v / omega;
            state->x += R_cg * (sin(state->theta + beta + delta_theta) - sin(state->theta + beta));
            state->y += R_cg * (-cos(state->theta + beta + delta_theta) + cos(state->theta + beta));
        } else {
            /* Прямолінійний рух при нульовій кутовій швидкості */
            state->x += state->v * cos(state->theta + beta) * dt;
            state->y += state->v * sin(state->theta + beta) * dt;
        }
        state->theta += delta_theta;
        state->v += accel * dt;
        state->delta += steer_rate * dt;
    }
    else if (method == INTEGRATION_RK4) {
        /* Класичний метод Рунге-Кутти 4-го порядку */
        BicycleDerivatives k1 = bicycle_eval_derivatives(state, accel, steer_rate, params);

        BicycleState s2 = {
            .x = state->x + 0.5 * dt * k1.dx,
            .y = state->y + 0.5 * dt * k1.dy,
            .theta = state->theta + 0.5 * dt * k1.dtheta,
            .v = state->v + 0.5 * dt * k1.dv,
            .delta = state->delta + 0.5 * dt * k1.ddelta
        };
        BicycleDerivatives k2 = bicycle_eval_derivatives(&s2, accel, steer_rate, params);

        BicycleState s3 = {
            .x = state->x + 0.5 * dt * k2.dx,
            .y = state->y + 0.5 * dt * k2.dy,
            .theta = state->theta + 0.5 * dt * k2.dtheta,
            .v = state->v + 0.5 * dt * k2.dv,
            .delta = state->delta + 0.5 * dt * k2.ddelta
        };
        BicycleDerivatives k3 = bicycle_eval_derivatives(&s3, accel, steer_rate, params);

        BicycleState s4 = {
            .x = state->x + dt * k3.dx,
            .y = state->y + dt * k3.dy,
            .theta = state->theta + dt * k3.dtheta,
            .v = state->v + dt * k3.dv,
            .delta = state->delta + dt * k3.ddelta
        };
        BicycleDerivatives k4 = bicycle_eval_derivatives(&s4, accel, steer_rate, params);

        state->x += (dt / 6.0) * (k1.dx + 2.0 * k2.dx + 2.0 * k3.dx + k4.dx);
        state->y += (dt / 6.0) * (k1.dy + 2.0 * k2.dy + 2.0 * k3.dy + k4.dy);
        state->theta += (dt / 6.0) * (k1.dtheta + 2.0 * k2.dtheta + 2.0 * k3.dtheta + k4.dtheta);
        state->v += (dt / 6.0) * (k1.dv + 2.0 * k2.dv + 2.0 * k3.dv + k4.dv);
        state->delta += (dt / 6.0) * (k1.ddelta + 2.0 * k2.ddelta + 2.0 * k3.ddelta + k4.ddelta);
    }

    /* Фінальна нормалізація стану */
    state->theta = normalize_angle(state->theta);
    state->delta = clamp_value(state->delta, -params->max_steer, params->max_steer);

    return true;
}
```
```cpp
#include <cmath>
#include <numbers>
#include <algorithm>
#include <span>
#include <array>

/* Ідіоматична реалізація кінематичного симулятора на C++20 */
namespace robotics {

enum class IntegrationMethod {
    Euler,
    ExactArc,
    RungeKutta4
};

struct BicycleParams {
    double l_f{1.2};             // Відстань CoM -> передня вісь, м
    double l_r{1.4};             // Відстань CoM -> задня вісь, м
    double max_steer{0.65};      // Максимальний кут вивороту керма, рад (~37.2 град)
    double max_steer_rate{1.2};  // Гранична швидкість сервоприводу, рад/с
    double max_accel{3.0};       // Граничне прискорення, м/с^2

    [[nodiscard]] constexpr double wheelbase() const noexcept {
        return l_f + l_r;
    }
};

struct BicycleState {
    double x{0.0};
    double y{0.0};
    double theta{0.0};
    double v{0.0};
    double delta{0.0};
};

struct BicycleDerivatives {
    double dx{0.0};
    double dy{0.0};
    double dtheta{0.0};
    double dv{0.0};
    double ddelta{0.0};
};

class KinematicBicycleModel {
public:
    explicit constexpr KinematicBicycleModel(BicycleParams params) noexcept
        : params_{params} {}

    [[nodiscard]] BicycleDerivatives evaluate_derivatives(
        const BicycleState& state,
        double accel,
        double steer_rate) const noexcept
    {
        const double L = params_.wheelbase();
        const double beta = std::atan((params_.l_r / L) * std::tan(state.delta));
        const double heading_eff = state.theta + beta;

        return BicycleDerivatives{
            .dx = state.v * std::cos(heading_eff),
            .dy = state.v * std::sin(heading_eff),
            .dtheta = (state.v / L) * std::tan(state.delta) * std::cos(beta),
            .dv = accel,
            .ddelta = steer_rate
        };
    }

    void step(
        BicycleState& state,
        double target_v,
        double target_delta,
        double dt,
        IntegrationMethod method = IntegrationMethod::RungeKutta4) const noexcept
    {
        if (dt <= 0.0) return;

        // Обмеження прискорень та кутів
        const double v_err = target_v - state.v;
        const double accel = std::clamp(v_err / dt, -params_.max_accel, params_.max_accel);

        const double delta_clamped = std::clamp(target_delta, -params_.max_steer, params_.max_steer);
        const double delta_err = delta_clamped - state.delta;
        const double steer_rate = std::clamp(delta_err / dt, -params_.max_steer_rate, params_.max_steer_rate);

        switch (method) {
            case IntegrationMethod::Euler:
                integrate_euler(state, accel, steer_rate, dt);
                break;
            case IntegrationMethod::ExactArc:
                integrate_exact_arc(state, accel, steer_rate, dt);
                break;
            case IntegrationMethod::RungeKutta4:
                integrate_rk4(state, accel, steer_rate, dt);
                break;
        }

        state.theta = normalize_angle(state.theta);
        state.delta = std::clamp(state.delta, -params_.max_steer, params_.max_steer);
    }

    // Симуляція пачки кроків уперед (траєкторний горизонт прогнозування)
    void predict_trajectory(
        BicycleState initial_state,
        double target_v,
        double target_delta,
        double dt,
        std::span<BicycleState> out_trajectory) const noexcept
    {
        BicycleState current = initial_state;
        for (auto& point : out_trajectory) {
            step(current, target_v, target_delta, dt, IntegrationMethod::RungeKutta4);
            point = current;
        }
    }

private:
    BicycleParams params_;

    static double normalize_angle(double angle) noexcept {
        while (angle > std::numbers::pi) angle -= 2.0 * std::numbers::pi;
        while (angle < -std::numbers::pi) angle += 2.0 * std::numbers::pi;
        return angle;
    }

    void integrate_euler(BicycleState& s, double a, double sr, double dt) const noexcept {
        const auto d = evaluate_derivatives(s, a, sr);
        s.x += d.dx * dt;
        s.y += d.dy * dt;
        s.theta += d.dtheta * dt;
        s.v += d.dv * dt;
        s.delta += d.ddelta * dt;
    }

    void integrate_exact_arc(BicycleState& s, double a, double sr, double dt) const noexcept {
        const double L = params_.wheelbase();
        const double beta = std::atan((params_.l_r / L) * std::tan(s.delta));
        const double omega = (s.v / L) * std::tan(s.delta) * std::cos(beta);
        const double delta_theta = omega * dt;

        if (std::abs(omega) > 1e-6) {
            const double R = s.v / omega;
            s.x += R * (std::sin(s.theta + beta + delta_theta) - std::sin(s.theta + beta));
            s.y += R * (-std::cos(s.theta + beta + delta_theta) + std::cos(s.theta + beta));
        } else {
            s.x += s.v * std::cos(s.theta + beta) * dt;
            s.y += s.v * std::sin(s.theta + beta) * dt;
        }

        s.theta += delta_theta;
        s.v += a * dt;
        s.delta += sr * dt;
    }

    void integrate_rk4(BicycleState& s, double a, double sr, double dt) const noexcept {
        const auto k1 = evaluate_derivatives(s, a, sr);

        const BicycleState s2{
            .x = s.x + 0.5 * dt * k1.dx,
            .y = s.y + 0.5 * dt * k1.dy,
            .theta = s.theta + 0.5 * dt * k1.dtheta,
            .v = s.v + 0.5 * dt * k1.dv,
            .delta = s.delta + 0.5 * dt * k1.ddelta
        };
        const auto k2 = evaluate_derivatives(s2, a, sr);

        const BicycleState s3{
            .x = s.x + 0.5 * dt * k2.dx,
            .y = s.y + 0.5 * dt * k2.dy,
            .theta = s.theta + 0.5 * dt * k2.dtheta,
            .v = s.v + 0.5 * dt * k2.dv,
            .delta = s.delta + 0.5 * dt * k2.ddelta
        };
        const auto k3 = evaluate_derivatives(s3, a, sr);

        const BicycleState s4{
            .x = s.x + dt * k3.dx,
            .y = s.y + dt * k3.dy,
            .theta = s.theta + dt * k3.dtheta,
            .v = s.v + dt * k3.dv,
            .delta = s.delta + dt * k3.ddelta
        };
        const auto k4 = evaluate_derivatives(s4, a, sr);

        s.x += (dt / 6.0) * (k1.dx + 2.0 * k2.dx + 2.0 * k3.dx + k4.dx);
        s.y += (dt / 6.0) * (k1.dy + 2.0 * k2.dy + 2.0 * k3.dy + k4.dy);
        s.theta += (dt / 6.0) * (k1.dtheta + 2.0 * k2.dtheta + 2.0 * k3.dtheta + k4.dtheta);
        s.v += (dt / 6.0) * (k1.dv + 2.0 * k2.dv + 2.0 * k3.dv + k4.dv);
        s.delta += (dt / 6.0) * (k1.ddelta + 2.0 * k2.ddelta + 2.0 * k3.ddelta + k4.ddelta);
    }
};

} // namespace robotics
```
:::

## 3. Аналіз обчислювальної складності та чисельної стійкості

Під час вибору алгоритму для інтегратора в реальних системах слід враховувати такі особливості:

1. **Метод Ейлера (Euler):**
   - *Операції:* 2 обчислення тригонометричних функцій (`sin`, `cos`) на крок.
   - *Стійкість:* похибка має порядок `O(dt)`. Якщо такт оновлення становить `dt = 50 мс`, на радіусі повороту 5 метрів накопичена похибка положення зростає на 10–15 сантиметрів за кожен секунду маневру. Метод допустимий лише при дуже високих частотах опитування (`dt ≤ 5 мс`).

2. **Метод точної кругової дуги (Exact Arc):**
   - *Операції:* 4 тригонометричні функції на крок.
   - *Стійкість:* забезпечує математично точне інтегрування траєкторії для умов, коли швидкість та кут керма не змінюються стрибком під час кроку `dt`. Це ідеальний вибір для бортової одометрії за сигналами енкодерів, де значення кута фіксується лічильником на початку такту таймера.
   - *Особливість реалізації:* вимагає обов'язкової перевірки на малу кутову швидкість `|omega| < 1e-6` з переходом на формулу прямолінійного руху для уникнення ділення на нуль при русі прямо.

3. **Метод Рунге-Кутти 4-го порядку (RK4):**
   - *Операції:* 16 обчислень тригонометричних функцій на крок.
   - *Стійкість:* похибка порядку `O(dt⁴)`. Метод розраховує проміжні стани всередині інтервалу `dt`, що критично важливо під час динамічної перекладки керма з високою кутовою швидкістю `steer_rate`.

## 4. Пастки реалізації на мікроконтролерах

- **Переповнення та фазовий розрив курсу `θ`:** безперервне інтегрування кута `θ += dtheta` призводить до зростання величини за межі `±2π` та `±1000π`. При великих значеннях аргументу стандартні функції `sin(θ)` та `cos(θ)` втрачають точність у молодших розрядах мантиси. Нормалізація в діапазон `[-π, π]` після кожного кроку є обов'язковою.
- **Одинарна чи подвійна точність:** на процесорах ARM Cortex-M4 (STM32F4) апаратний блок FPU підтримує лише 32-бітний тип `float`. Використання `double` призводить до програмної емуляції операцій і сповільнення розрахунків у 10–20 разів. Якщо симулятор компілюється для Cortex-M4, усі типи слід замінити на `float`, а поріг прямолінійного руху підвищити до `1e-4f`. На Cortex-M7 (STM32H7) та процесорах x86/ARM64 слід застосовувати `double`.
- **Рух заднім ходом (`v < 0`):** модель повністю симетрична відносно знаку швидкості. При зміні знаку `v` напрямок обертання `ω` змінюється на протилежний, що коректно відтворює кінематику заднього ходу без потреби введення окремих умовних розгалужень у коді.

## 5. Методика тестування та валідації симулятора

Для перевірки коректності інтегратора рекомендується виконати три аналітичні тести:

1. **Тест кругового руху (Constant Radius Circle):** при фіксованих параметрах `v = 2.0 м/с` та `δ = 0.5 рад` на колісній базі `L = 2.0 м` теоретичний радіус повороту становить `R = L / tan(δ) ≈ 3.661 м`, а період повного оберту — `T = 2π·R / v ≈ 11.50 с`. Інтегратор повинен повернути робота точно у вихідну точку `(x_0, y_0)` через час `T`. Метод точної дуги та RK4 демонструють замикання траєкторії з точністю до мікронів, тоді як метод Ейлера накопичує радіальний дрейф у кілька десятків сантиметрів.
2. **Тест прямолінійного руху (Zero Steering):** при `δ = 0` та `v = 10 м/с` робот повинен рухатися строго вздовж прямої лінії без виникнення бічного зміщення `ẏ = 0` через залишковий шум обчислень із плаваючою комою.
3. **Тест реверсу (Forward-Backward Invariance):** проїзд уперед на 5 секунд із вивернутим кермом з наступним рухом назад із тією самою швидкістю протягом 5 секунд мусить повернути робота точно у початковий стан `(x_0, y_0, θ_0)`. Цей тест підтверджує відсутність фазового зсуву знаків у неголономних рівняннях швидкості.
