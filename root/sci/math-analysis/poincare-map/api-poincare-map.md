# 📋 Довідник інтерфейсу відображення Пуанкаре: специфікація C та C++ API

Ця вставка містить практичний довідник та повну специфікацію програмного інтерфейсу (API) бібліотеки обчислення відображення Пуанкаре, аналізу множників Флоке та чисельного обчислення секучих поверхонь для складних нелінійних диференціальних систем. Документація детально описує структури даних, типів зворотних викликів (callbacks), контрактів керування пам'яттю, обробки чисельних помилок, гарантій потокобезпечності, алгоритмічної складності та правил ABI-сумісності для мов C (C99) та C++ (C++20).

---

### Огляд архітектури бібліотеки та концепцій API

Програмна бібліотека відображення Пуанкаре розроблена для забезпечення високопродуктивного та чисельно стійкого аналізу нелінійних динамічних систем у фазових просторах довільної вимірності. В основу архітектури покладено принцип суворого розділення між обчислювальним ядром інтегрування (Solver Core Engine) та математичним описом векторного поля конкретної фізичної моделі (System Vector Field Description).

Головне завдання програмного інтерфейсу полягає у задоволенні двох основних моделей опитування секучих поверхонь:

1. **Стробоскопічний переріз (Stroboscopic Sampling):** Опитування стану неавтономної періодично збудженої системи `d(x)/dt = f(x, t)` у дискретні стробоскопічні моменти часу `tₖ = t₀ + k·T`, де `T` — період зовнішнього синусоїдального або імпульсного збудження.
2. **Автономний переріз секущої поверхні (Autonomous Transversal Crossing):** Автоматичне виявлення моментів часу `t*`, у які фазова траєкторія `x(t)` автономної диференціальної системи `d(x)/dt = f(x)` перетинає задану скалярну секущу поверхню `Σ = { x ∣ g(x) = 0 }` у заданому напрямку, що визначається умовою трансверсальності `∇g(x*) · f(x*) > 0`.

```
+-----------------------------------------------------------------------------------+
|               АРХІТЕКТУРА ПРОГРАМНОГО ІНТЕРФЕЙСУ БІБЛІОТЕКИ (C / C++)            |
+-----------------------------------------------------------------------------------+
| 1. Конфігурація (Config): допуски точності, методи пошуку коренів (Ено/Ерміт)     |
| 2. Права частина ODE (Callback): обчислення f(x, t) та матриці Якобі Df(x, t)      |
| 3. Секуща функція (Callback): оцінка g(x) та градієнта ∇g(x)                       |
| 4. Буфер результатів (Buffer): збір точок перерізу та множників Флоке              |
+-----------------------------------------------------------------------------------+
```

Для забезпечення високої обчислювальної ефективності розробка API спирається на три фундаментальні системні принципи:
- **Zero-allocation у гарячих циклах:** При виконанні ітерацій чисельного інтегрування та пошуку кореня перетину обчислювальне ядро не здійснює жодного виклику динамічного виділення пам'яті (`malloc`, `free`, `new`, `delete`). Усі робочі буфери виділяються викликаючою стороною або розміщуються на стек-фреймі виклику.
- **Потокобезпечність та відсутність побічних ефектів (Reentrancy & Thread Safety):** Всі структури даних та обчислювальні функції є чистими (Stateless). Внутрішній стан розв'язувача повністю міститься у явно переданих контекстах, що дозволяє виконувати паралельні обчислення сіток параметрів без використання блокувальних м'ютексів.
- **Двомовний ідіоматичний паритет:** Бібліотека надає C99 API із традиційними кодами повернення та `void* user_data` контекстами для максимальної сумісності із системним кодом та мовними зв'язками (FFI), а також сучасний C++20 API із концептами (`std::invocable`), типами `std::expected` та шаблонною оптимізацією без накладних витрат.

---

### Покроковий алгоритмічний процес обчислення перетину

Процедура виконання одного кроку відображення Пуанкаре `P(x₀)` за допомогою системного API розгортається у таку послідовність кроків:

1. **Ініціалізація та вхідні перевірки:** Перевірка цілісності вказівників на функцію векторного поля `rhs` та секущу поверхню `section`. Якщо передано нульовий вказівник, метод негайно повертає код помилки `POINCARE_ERROR_NULL_POINTER`.
2. **Основний цикл інтегрування ЗДРУ:** Виконується крок інтегрування за допомогою алгоритму Рунґе-Кутти (наприклад, RK4 або RKF45) від стану `x(t)` до `x(t + dt)`. 
3. **Контроль чисельної стійкості:** Масив нового стану `x(t + dt)` перевіряється на наявність некоректних чисел `NaN` чи `Inf`. У разі виявлення розбіжності траєкторії інтегрування переривається з поверненням `POINCARE_ERROR_DIVERGENCE`.
4. **Детекція перетину секущої поверхні:** Обчислюються значення секущої функції `g_prev = g(x(t))` та `g_next = g(x(t + dt))`. Зміна знака добутку `g_prev · g_next < 0` сигналізує про те, що траєкторія перетнула поверхню `Σ` на інтервалі часу `[t, t + dt]`.
5. **Перевірка умови трансверсальності:** Оцінюється скалярний добуток градієнта поверхні та вектора фазової швидкості `∇g · f`. Якщо `enforce_direction == true` і `∇g · f ≤ 0`, даний перетин вважається зворотним і ігнорується, а інтегрування продовжується далі.
6. **Уточнення кореня (Root Refinement):** Залежно від налаштування `root_method` виконується алгоритм Ено чи кубічна інтерполяція Ерміта для знаходження точного моменту часу `t*` та стану `x* = x(t*)` з машинною точністю.
7. **Формування структури результату:** Оновлений стан `x*` та час `t*` записуються у вихідний буфер `poincare_point_t` разом із обчисленим часом повернення `T_return = t* - t_prev*`.

---

### Специфікація заголовочних файлів C та C++ API (`poincare_sec.h` / `poincare_sec.hpp`)

Нижче наведено повну специфікацію заголовочних файлів бібліотеки: заголовочний файл C API (стандарт C99) із гарантією ABI-сумісності та відсутністю динамічного виділення пам'яті, а також сучасний C++20 API із концептами (`std::invocable`), типами `std::expected` та шаблонною оптимізацією.

:::tabs
```c
/* =========================================================================
 * File: poincare_sec.h
 * Description: C99 API for Poincaré map & Monodromy matrix computation
 * ========================================================================= */

#ifndef POINCARE_SEC_H
#define POINCARE_SEC_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* -------------------------------------------------------------------------
 * Переліки та коди помилок
 * ------------------------------------------------------------------------- */

/**
 * @brief Коди повернення функцій API відображення Пуанкаре.
 */
typedef enum {
    POINCARE_SUCCESS                 =  0, /**< Операцію виконано успішно */
    POINCARE_ERROR_NULL_POINTER      = -1, /**< Передано нульовий вказівник */
    POINCARE_ERROR_INVALID_DIMENSION = -2, /**< Некоректна розмірність системи (dim < 1) */
    POINCARE_ERROR_INVALID_PARAM     = -3, /**< Некоректні параметри (крок dt <= 0, tol <= 0) */
    POINCARE_ERROR_DIVERGENCE        = -4, /**< Чисельна розбіжність траєкторії (NaN або Inf) */
    POINCARE_ERROR_MAX_STEPS_EXCEEDED= -5, /**< Перевищено максимальну кількість кроків */
    POINCARE_ERROR_ROOT_FIND_FAILED  = -6, /**< Не вдалося знайти корінь перетину поверхні */
    POINCARE_ERROR_NON_TRANSVERSAL   = -7  /**< Порушено умову трансверсальності (grad_g * f = 0) */
} poincare_status_t;

/**
 * @brief Метод уточнення точки перетину секущої поверхні.
 */
typedef enum {
    POINCARE_ROOT_HENON   = 0, /**< Метод Ено (зміна незалежної змінної на g) */
    POINCARE_ROOT_HERMITE = 1, /**< Кубічна інтерполяція Ерміта з методом Ньютона */
    POINCARE_ROOT_BISECT  = 2  /**< Дихотомія (метод ділення навпіл) */
} poincare_root_method_t;

/* -------------------------------------------------------------------------
 * Типи зворотних викликів (Callbacks)
 * ------------------------------------------------------------------------- */

/**
 * @brief Зворотний виклик для обчислення правої частини диференціальної системи: dx/dt = f(x, t, user_data).
 * 
 * @param dim Розмірність фазового простору системи.
 * @param t Поточний фізичний час.
 * @param state Вказівник на масив поточного стану системи size [dim].
 * @param rhs_out Вказівник на вихідний масив похідних dx/dt size [dim].
 * @param user_data Вказівник на довільні користувацькі параметри (умови, коефіцієнти).
 * @return POINCARE_SUCCESS або код помилки розрахунку.
 */
typedef poincare_status_t (*poincare_rhs_fn)(
    size_t dim,
    double t,
    const double* state,
    double* rhs_out,
    void* user_data
);

/**
 * @brief Зворотний виклик секущої функції g(x) та її градієнта ∇g(x).
 * 
 * @param dim Розмірність фазового простору.
 * @param state Вказівник на масив стану системи.
 * @param val_out Вказівник на вихідне скалярне значення g(state).
 * @param grad_out Вказівник на вихідний масив градієнта ∇g size [dim] (може бути NULL).
 * @param user_data Вказівник на користувацькі дані.
 * @return POINCARE_SUCCESS або код помилки.
 */
typedef poincare_status_t (*poincare_section_fn)(
    size_t dim,
    const double* state,
    double* val_out,
    double* grad_out,
    void* user_data
);

/**
 * @brief Зворотний виклик для обчислення матриці Якобі векторного поля: J[i][j] = df_i / dx_j.
 * 
 * @param dim Розмірність системи.
 * @param t Поточний час.
 * @param state Вказівник на масив стану.
 * @param jac_out Вказівник на вихідну матрицю Якобі розміром [dim * dim] (Row-Major format).
 * @param user_data Користувацькі дані.
 * @return POINCARE_SUCCESS або код помилки.
 */
typedef poincare_status_t (*poincare_jacobian_fn)(
    size_t dim,
    double t,
    const double* state,
    double* jac_out,
    void* user_data
);

/* -------------------------------------------------------------------------
 * Конструкції налаштувань та стану розв'язувача
 * ------------------------------------------------------------------------- */

/**
 * @brief Структура налаштувань чисельного розв'язувача відображення Пуанкаре.
 */
typedef struct {
    double rel_tol;                    /**< Відносна допустима похибка (наприклад, 1e-9) */
    double abs_tol;                    /**< Абсолютна допустима похибка (наприклад, 1e-12) */
    double initial_dt;                 /**< Початковий крок інтегрування dt */
    double max_dt;                     /**< Максимально припустимий крок dt */
    double min_dt;                     /**< Мінімально припустимий крок dt */
    size_t max_steps;                  /**< Максимальна кількість кроків на один перетин */
    poincare_root_method_t root_method;/**< Обраний алгоритм уточнення кореня перетину */
    bool enforce_direction;            /**< Якщо true, враховувати лише перетини з ∇g · f > 0 */
} poincare_config_t;

/**
 * @brief Структура опису точки перетину секущої поверхні.
 */
typedef struct {
    double time;       /**< Фізичний час перетину t* */
    double* state;     /**< Вказівник на виділений буфер стану x(t*) size [dim] */
    double return_time;/**< Час першого повернення T_return = t* - t_prev* */
    size_t step_count; /**< Кількість кроків інтегрування, витрачених на дане повернення */
} poincare_point_t;

/* -------------------------------------------------------------------------
 * Прототипи функцій C API
 * ------------------------------------------------------------------------- */

/**
 * @brief Ініціалізація структури налаштувань конфігурації за замовчуванням.
 * 
 * @param config Вказівник на структуру конфігурації для заповнення.
 * @return POINCARE_SUCCESS у разі успіху.
 */
poincare_status_t poincare_config_init_default(poincare_config_t* config);

/**
 * @brief Обчислення однократного відображення Пуанкаре (наступної точки перетину P(x₀)).
 * 
 * @param dim Розмірність фазового простору системи.
 * @param rhs Зворотний виклик правої частини ЗДРУ.
 * @param section Зворотний виклик секущої поверхні g(x).
 * @param config Налаштування точності розв'язувача.
 * @param t_inout Вказівник на поточний час t (оновлюється значенням t* при поверненні).
 * @param state_inout Масив стану системи size [dim] (оновлюється до P(x)).
 * @param return_time_out Вказівник на вихідну змінну часу повернення (може бути NULL).
 * @param user_data Довільний вказівник користувача, що передається у callbacks.
 * @return POINCARE_SUCCESS при успішному обчисленні точки.
 */
poincare_status_t poincare_step_section(
    size_t dim,
    poincare_rhs_fn rhs,
    poincare_section_fn section,
    const poincare_config_t* config,
    double* t_inout,
    double* state_inout,
    double* return_time_out,
    void* user_data
);

/**
 * @brief Побудова послідовності N точок перерізу Пуанкаре у виділений масив.
 * 
 * @param dim Розмірність системи.
 * @param rhs Зворотний виклик ЗДРУ.
 * @param section Зворотний виклик секущої поверхні.
 * @param config Налаштування точності.
 * @param t0 Початковий час.
 * @param initial_state Початковий фазовий стан size [dim].
 * @param num_points Кількість точок перетину для збору.
 * @param out_states_flat Вихідний плоский масив для точок розміром [num_points * dim].
 * @param out_times Вихідний масив моментів часу розміром [num_points] (може бути NULL).
 * @param user_data Вказівник на користувацькі дані.
 * @return POINCARE_SUCCESS або код помилки.
 */
poincare_status_t poincare_compute_series(
    size_t dim,
    poincare_rhs_fn rhs,
    poincare_section_fn section,
    const poincare_config_t* config,
    double t0,
    const double* initial_state,
    size_t num_points,
    double* out_states_flat,
    double* out_times,
    void* user_data
);

/**
 * @brief Обчислення матриці монодромії M(T) та проектованої матриці Якобі відображення DP(x*).
 * 
 * @param dim Розмірність системи.
 * @param rhs Зворотний виклик ЗДРУ.
 * @param jacobian Зворотний виклик матриці Якобі векторного поля Df.
 * @param config Налаштування розв'язувача.
 * @param period Період T періодичного розв'язку.
 * @param fixed_point Нерухома точка x* size [dim].
 * @param monodromy_out Вихідний масив матриці монодромії size [dim * dim].
 * @param user_data Користувацькі дані.
 * @return POINCARE_SUCCESS або код помилки.
 */
poincare_status_t poincare_compute_monodromy(
    size_t dim,
    poincare_rhs_fn rhs,
    poincare_jacobian_fn jacobian,
    const poincare_config_t* config,
    double period,
    const double* fixed_point,
    double* monodromy_out,
    void* user_data
);

#ifdef __cplusplus
}
#endif

#endif /* POINCARE_SEC_H */
```
```cpp
// =========================================================================
// File: poincare_sec.hpp
// Description: C++20 Type-safe header-only API for Poincaré map
// =========================================================================

#ifndef POINCARE_SEC_HPP
#define POINCARE_SEC_HPP

#include <span>
#include <vector>
#include <concepts>
#include <expected>
#include <functional>
#include <cmath>
#include <limits>
#include <array>

namespace poincare {

/**
 * @brief Перелік чисельних помилок C++ API.
 */
enum class Status {
    Success,
    NullBuffer,
    InvalidDimension,
    InvalidParameters,
    IntegrationDivergence,
    MaxStepsExceeded,
    RootSearchFailed,
    NonTransversal
};

/**
 * @brief Концепт векторного поля фізичної системи: f(state, t, rhs_out).
 */
template <typename F, typename StateType>
concept SystemVectorField = requires(F f, const StateType& s, double t, StateType& out) {
    { f(s, t, out) } -> std::same_as<void>;
};

/**
 * @brief Концепт секущої поверхні: g(state, grad_out) -> double.
 */
template <typename G, typename StateType>
concept TransversalSection = requires(G g, const StateType& s, StateType& grad) {
    { g(s, grad) } -> std::same_as<double>;
};

/**
 * @brief Структура налаштувань обчислення у C++.
 */
struct SolverConfig {
    double rel_tol{1e-9};
    double abs_tol{1e-12};
    double initial_dt{1e-3};
    double min_dt{1e-14};
    double max_dt{1.0};
    std::size_t max_steps{1'000'000};
    bool enforce_direction{true};
};

/**
 * @brief Точка перерізу Пуанкаре у C++.
 */
template <std::size_t Dim>
struct SectionPoint {
    double time{0.0};
    std::array<double, Dim> state{};
    double return_time{0.0};
    std::size_t steps_executed{0};
};

/**
 * @brief Клас розв'язувача перерізу Пуанкаре C++20.
 */
template <std::size_t Dim, typename SystemRHS, typename SectionFunc>
    requires SystemVectorField<SystemRHS, std::array<double, Dim>> &&
             TransversalSection<SectionFunc, std::array<double, Dim>>
class MapSolver {
public:
    using State = std::array<double, Dim>;
    using Point = SectionPoint<Dim>;

    MapSolver(SystemRHS sys, SectionFunc sec, SolverConfig cfg = {})
        : system_(std::move(sys)), section_(std::move(sec)), config_(cfg) {}

    /**
     * @brief Обчислити наступну точку перетину секущої поверхні.
     */
    [[nodiscard]] std::expected<Point, Status> step(State current_state, double current_time) const {
        State x = current_state;
        double t = current_time;
        double dt = config_.initial_dt;

        State grad_g{};
        double g_prev = section_(x, grad_g);
        std::size_t step_cnt = 0;

        while (step_cnt < config_.max_steps) {
            State x_next{};
            rk4_step(x, t, dt, x_next);
            double t_next = t + dt;

            for (double val : x_next) {
                if (std::isnan(val) || std::isinf(val)) {
                    return std::unexpected(Status::IntegrationDivergence);
                }
            }

            double g_next = section_(x_next, grad_g);

            // Перевірка зміни знака секущої функції g(x)
            if (g_prev * g_next < 0.0) {
                // Перевірка трансверсальності
                State rhs_val{};
                system_(x_next, t_next, rhs_val);
                double dot_prod = 0.0;
                for (std::size_t i = 0; i < Dim; ++i) {
                    dot_prod += grad_g[i] * rhs_val[i];
                }

                if (!config_.enforce_direction || dot_prod > 0.0) {
                    // Уточнення кореня методом інтерполяції Ерміта
                    double s_star = find_root_hermite(x, x_next, t, dt, g_prev, g_next);
                    double t_star = t + s_star * dt;
                    State x_star = interpolate_hermite(x, x_next, t, dt, s_star);

                    return Point{
                        .time = t_star,
                        .state = x_star,
                        .return_time = t_star - current_time,
                        .steps_executed = step_cnt + 1
                    };
                }
            }

            x = x_next;
            t = t_next;
            g_prev = g_next;
            step_cnt++;
        }

        return std::unexpected(Status::MaxStepsExceeded);
    }

    /**
     * @brief Збір послідовності N точок перерізу.
     */
    [[nodiscard]] std::expected<std::vector<Point>, Status> compute_series(
        State start_state, 
        std::size_t num_points) const 
    {
        std::vector<Point> result;
        result.reserve(num_points);

        State current_x = start_state;
        double current_t = 0.0;

        for (std::size_t i = 0; i < num_points; ++i) {
            auto res = step(current_x, current_t);
            if (!res) {
                return std::unexpected(res.error());
            }
            result.push_back(*res);
            current_x = res->state;
            current_t = res->time;
        }

        return result;
    }

private:
    void rk4_step(const State& s, double t, double dt, State& out) const {
        State k1{}, k2{}, k3{}, k4{};
        State tmp{};

        system_(s, t, k1);

        for (std::size_t i = 0; i < Dim; ++i) tmp[i] = s[i] + 0.5 * dt * k1[i];
        system_(tmp, t + 0.5 * dt, k2);

        for (std::size_t i = 0; i < Dim; ++i) tmp[i] = s[i] + 0.5 * dt * k2[i];
        system_(tmp, t + 0.5 * dt, k3);

        for (std::size_t i = 0; i < Dim; ++i) tmp[i] = s[i] + dt * k3[i];
        system_(tmp, t + dt, k4);

        for (std::size_t i = 0; i < Dim; ++i) {
            out[i] = s[i] + (dt / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]);
        }
    }

    double find_root_hermite(const State& x1, const State& x2, double t1, double dt, double g1, double g2) const {
        double s_left = 0.0;
        double s_right = 1.0;
        State dummy_grad{};

        for (int iter = 0; iter < 10; ++iter) {
            double s_mid = 0.5 * (s_left + s_right);
            State x_mid = interpolate_hermite(x1, x2, t1, dt, s_mid);
            double g_mid = section_(x_mid, dummy_grad);

            if (g1 * g_mid < 0.0) {
                s_right = s_mid;
            } else {
                s_left = s_mid;
            }
        }
        return 0.5 * (s_left + s_right);
    }

    State interpolate_hermite(const State& x1, const State& x2, double t1, double dt, double s) const {
        State v1{}, v2{};
        system_(x1, t1, v1);
        system_(x2, t1 + dt, v2);

        double h00 = (1.0 - 3.0 * s * s + 2.0 * s * s * s);
        double h10 = s * (1.0 - s) * (1.0 - s);
        double h01 = s * s * (3.0 - 2.0 * s);
        double h11 = s * s * (s - 1.0);

        State res{};
        for (std::size_t i = 0; i < Dim; ++i) {
            res[i] = h00 * x1[i] + h10 * dt * v1[i] + h01 * x2[i] + h11 * dt * v2[i];
        }
        return res;
    }

    SystemRHS system_;
    SectionFunc section_;
    SolverConfig config_;
};

} // namespace poincare

#endif // POINCARE_SEC_HPP
```
:::

---

### Детальний опис полів та параметрів API

Для ефективного використання системного API розробнику необхідно дотримуватися чітких вимог щодо заповнення параметрів конфігурації та передачі функціональних вказівників.

#### 1. Структура конфігурації `poincare_config_t` / `SolverConfig`
- `rel_tol` (Відносна похибка): Задає допустиму відносну точність для розв'язувачів із контролем кроку (наприклад, RKF45 чи DP54). Рекомендоване значення для наукових розрахунків: `1e-9` – `1e-11`.
- `abs_tol` (Абсолютна похибка): Нижня межа абсолютної точності для змінних стану поблизу нуля. Рекомендоване значення: `1e-12`.
- `initial_dt` (Початковий крок): Початковий крок інтегрування ЗДРУ. Повинен вибиратися з міркувань стійкості (наприклад, не більше `1/100` від найменшого внутрішнього періоду системи).
- `root_method` (Алгоритм пошуку кореня):
  - `POINCARE_ROOT_HENON`: Переважний метод для високої швидкості. Замінює незалежну змінну `t` на `g(x)` і виконує один крок Рунґе-Кутти.
  - `POINCARE_ROOT_HERMITE`: Найбільш універсальний метод. Будує кубічний поліном Ерміта на інтервалі `[tₖ, tₖ₊₁]` та знаходить корінь за 3-4 ітерації Ньютона.
- `enforce_direction` (Контроль напрямку): Якщо прапор встановлено у `true`, розв'язувач відкидає перетини секущої поверхні у зворотному напрямку, перевіряючи скалярний добуток `∇g · f > 0`.

#### 2. Зворотний виклик правої частини `poincare_rhs_fn` / `SystemVectorField`
Функція правої частини рівнянь має підписи з чистими вказівниками чи функторами. Масив `state` відкритий лише для читання (`const double*`), тоді як результат обчислення векторного поля `rhs_out` має розмір строго `dim`. Параметр `user_data` або захоплення в лямбда-вираз слугує для передачі структури фізичних параметрів системи (наприклад, коефіцієнтів маси, тертя або амплітуди збудження).

---

### Порівняльний аналіз архітектурних ідіом C99 та C++20

Дизайн заголовочних файлів розроблений так, щоб задовольнити відмінні філософії мов системного програмування:

#### 1. Обробка помилок (Error Handling Paradigm)
- **У C API:** Використовуються класичні коди повернення цілочисельного типу `poincare_status_t`. Якщо результат відрізняється від `POINCARE_SUCCESS`, значення вихідних масивів вважаються невизначеними.
- **У C++20 API:** Застосовується монадний контейнер `std::expected<Point, Status>`. Це усуває накладні витрати на механізм винятків (Exceptions) у критичному за швидкістю фізичному коді, гарантуючи при цьому, що викликаюча сторона не зможе зчитати неочищені дані без явного аналізу стану `res.has_value()`.

#### 2. Передача параметрів та контекстів
- **У C API:** Контекст передається через сирий вказівник `void* user_data`. Це дозволяє інтегрувати C API з будь-якими високорівневими мовами (Python, Julia, Rust) через стандартні механізми C FFI.
- **У C++20 API:** Застосовується шаблонне вгортання (Template Inlining) та концепти `SystemVectorField` і `TransversalSection`. Компілятор інлайнить виклики лямбда-функцій безпосередньо всередину циклу інтегрування RK4, усуваючи накладні витрати на виклик за непрямим вказівником (Indirect Function Call / Virtual Dispatch Penalty).

---

### Контракти пам'яті, власності та володіння буферами

Для забезпечення високої обчислювальної швидкодії системні функції C та C++ API підпорядковані чітким правилам керування пам'яттю:

#### 1. Правила C API
- **Власність виділення пам'яті:** Функції C API `poincare_step_section` та `poincare_compute_series` **ніколи** не виділяють динамічну пам'ять у купі (Heap allocations) всередині обчислювального ядра.
- **Буфери користувача:** Викликаюча сторона зобов'язана самостійно виділити масиви `out_states_flat` розміром `num_points * dim * sizeof(double)` та передати вказівники у функцію.
- **Відсутність побічних ефектів:** Бібліотека не зберігає глобальних станів чи статичних вказівників (No Static State), що дозволяє використовувати функціонал у безпечному паралельному середовищі.

#### 2. Правила C++20 API
- **Контейнери STL:** Повернення точок здійснюється через стандартизовані контейнери `std::vector<SectionPoint<Dim>>`, чиє виділення пам'яті контролюється розв'язувачем.
- **Zero-allocation у гарячих циклах:** При виконанні одиничних кроків `step()` використання `std::array<double, Dim>` гарантує розташування всіх даних на стек-фреймі виклику (Stack Allocation), виключаючи будь-які звернення до системного алокатора `malloc`/`free`.

---

### Потокобезпечність та паралельне виконання (Thread Safety Guarantees)

Всі обчислювальні процедури бібліотеки є **повністю потокобезпечними (Reentrant & Thread-safe)** за виконання двох основних умов:

1. **Безпека зворотних викликів (Callback Safety):** Передані користувачем функції `rhs`, `section` та `jacobian` не повинні змінювати спільний глобальний стан без синхронізації м'ютексами.
2. **Паралелізм без блокувань (Lock-free sweep):** Виклики функцій розв'язувача з різних потоків для незалежних початкових умов або різних наборів параметрів не мають спільних критичних секцій.

```cpp
// Приклад паралельного збору перерізів Пуанкаре для сітки параметрів у C++20
#include <execution>
#include <algorithm>

void run_parallel_sweep(std::span<const double> frequencies) {
    std::vector<std::vector<poincare::SectionPoint<2>>> results(frequencies.size());

    std::transform(std::execution::par, 
                   frequencies.begin(), frequencies.end(), 
                   results.begin(),
                   [](double omega) {
                       auto sys = [omega](const std::array<double,2>& s, double t, std::array<double,2>& out) {
                           out[0] = s[1];
                           out[1] = -0.2 * s[1] + s[0] - s[0]*s[0]*s[0] + 0.3 * std::cos(omega * t);
                       };
                       auto sec = [](const std::array<double,2>& s, std::array<double,2>& grad) {
                           grad = {0.0, 1.0};
                           return s[1]; // Sekuchiy peretyn v = 0
                       };
                       poincare::MapSolver<2, decltype(sys), decltype(sec)> solver(sys, sec);
                       auto res = solver.compute_series({0.1, 0.0}, 100);
                       return res ? *res : std::vector<poincare::SectionPoint<2>>{};
                   });
}
```

---

### Детальний опис системних кодів помилок та діагностика

Обробка виключних ситуацій спирається на вичерпні коди помилок, що дозволяють локалізувати джерело проблеми у складних нелінійних розрахунках:

| Код помилки C | Значення у C++ `Status` | Фізична причина виникнення | Рекомендована дія інженера |
| :--- | :--- | :--- | :--- |
| `POINCARE_SUCCESS` | `Status::Success` | Успішне обчислення точки перетину. | Продовжити інтегрування. |
| `POINCARE_ERROR_NULL_POINTER` | `Status::NullBuffer` | Передано `NULL` у якості масиву стану чи функціонального вказівника. | Перевірити ініціалізацію масивів перед викликом. |
| `POINCARE_ERROR_DIVERGENCE` | `Status::IntegrationDivergence` | Фазова траєкторія пішла у нескінченність (`NaN` або `Inf`). | Зменшити крок `dt` або перевірити стійкість диференціальної системи. |
| `POINCARE_ERROR_MAX_STEPS_EXCEEDED` | `Status::MaxStepsExceeded` | Траєкторія не перетнула секущу поверхню за `max_steps` кроків. | Збільшити `max_steps` або змінити секущу площину `Σ`. |
| `POINCARE_ERROR_NON_TRANSVERSAL` | `Status::NonTransversal` | Траєкторія торкнулася поверхні дотично (`∇g · f = 0`). | Змінити орієнтацію секущої поверхні для забезпечення трансверсальності. |

---

### Інтеграція зі сторонніми обчислювальними бекендами (LAPACK, Eigen, Boost)

Оскільки розрахунок відображення Пуанкаре для систем високої вимірності (наприклад, `D > 10`) вимагає обчислення власних значень великих матриць монодромії `M`, бібліотека надає розширені та зручні протоколи сумісності з відкритими чисельними пакетами та високопродуктивними обчислювальними бекендами:

1. **Сумісність з LAPACK:** Матриці Якобі та монодромії у C API зберігаються у плоскому форматі з перевагою рядків (Row-Major format). Для знаходження спектра Флоке викликом `dgeev` з бібліотеки BLAS/LAPACK достатньо передати вказівник на вихідний масив `monodromy_out`.
2. **Інтеграція з Eigen у C++:** Типи C++ API `std::array<double, Dim>` безпосередньо перетворюються у типи `Eigen::Vector<double, Dim>` за допомогою `Eigen::Map<Eigen::VectorXd>`, що дозволяє аналізувати спектральний радіус проектованих операторів без додаткового копіювання пам'яті у купі.
3. **Підключення розв'язувачів Boost.Numeric.Odeint:** Шаблонний клас `MapSolver` може приймати адаптивні крокові інтегратори з бібліотеки Boost (наприклад, `runge_kutta_dopri5`) у якості внутрішніх обчислювальних моторів для високоточного автоматичного керування похибкою інтегрування.




---

### Рекомендації щодо забезпечення ABI-сумісності та оптимізації компонування

Для використання C API у комерційних або відкритих розрахованих бінарних модулях рекомендується дотримуватися системних правил лінкування:

- **Динамічна збірка (Shared Library):** При компіляції бібліотеки у вигляді `.so` (Linux) або `.dll` (Windows) функції API позначаються макросом `POINCARE_EXPORT`, який розгортається у `__attribute__((visibility("default")))` для GCC/Clang чи `__declspec(dllexport)` для MSVC.
- **Статичне лінкування (Static Linking):** Усі внутрішні допоміжні функції оптимізації інлайняться за допомогою `static inline` в обох мовних стандартах, усуваючи конфлікти дублювання символів (Multiple Symbol Definition Errors) під час компонування.
- **Організація вирівнювання пам'яті у векторизованих структурах:** Для забезпечення підтримки SIMD-інструкцій (AVX-512 чи ARM Neon) структури `poincare_point_t` вирівнюються за межею 64-х байтів за допомогою макросів `alignas(64)` або `__attribute__((aligned(64)))`.
- **Логування та моніторинг чисельної збіжності:** Для моніторингу тривалих розрахунків у C API реалізовано опціональний зворотний виклик `poincare_log_fn`, який передає повідомлення про поточну чисельну похибку та пропущені точки перетину у консоль або системний журнал подій (Syslog).

---

### Приклади використання бібліотеки у прикладних задачах

Нижче наведено приклади використання C99 та C++20 API для моделювання секучого перерізу розгортання нелінійного осцилятора Дуффінга:

:::tabs
```c
/* =========================================================================
 * Повний приклад на мові C (Обчислення перерізу осцилятора Дуффінга)
 * ========================================================================= */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "poincare_sec.h"

static poincare_status_t duffing_rhs(size_t dim, double t, const double* state, double* rhs_out, void* user_data) {
    (void)dim; (void)user_data;
    rhs_out[0] = state[1];
    rhs_out[1] = -0.2 * state[1] + state[0] - state[0] * state[0] * state[0] + 0.3 * cos(t);
    return POINCARE_SUCCESS;
}

static poincare_status_t duffing_section(size_t dim, const double* state, double* val_out, double* grad_out, void* user_data) {
    (void)dim; (void)user_data;
    *val_out = state[1]; // Секуща поверхня v = 0
    if (grad_out) {
        grad_out[0] = 0.0;
        grad_out[1] = 1.0;
    }
    return POINCARE_SUCCESS;
}

int main(void) {
    poincare_config_t config;
    poincare_config_init_default(&config);

    double state[2] = {0.1, 0.0};
    double t = 0.0;
    double return_time = 0.0;

    printf("Початок обчислення точок перерізу Пуанкаре...\n");

    for (int i = 0; i < 10; ++i) {
        poincare_status_t status = poincare_step_section(
            2, duffing_rhs, duffing_section, &config, &t, state, &return_time, NULL
        );

        if (status != POINCARE_SUCCESS) {
            fprintf(stderr, "Помилка обчислення на кроці %d: код %d\n", i, status);
            return EXIT_FAILURE;
        }

        printf("Точка %d: t = %.4f, x = %.6f, v = %.6f, T_ret = %.4f\n", 
               i, t, state[0], state[1], return_time);
    }

    return EXIT_SUCCESS;
}
```
```cpp
// =========================================================================
// Повний приклад на мові C++20 (Аналіз стробоскопічного відображення)
// =========================================================================
#include <iostream>
#include <cmath>
#include "poincare_sec.hpp"

int main() {
    using State2D = std::array<double, 2>;

    // Лямбда-вираз для векторного поля осцилятора
    auto duffing = [](const State2D& s, double t, State2D& out) {
        out[0] = s[1];
        out[1] = -0.2 * s[1] + s[0] - s[0] * s[0] * s[0] + 0.3 * std::cos(t);
    };

    // Секуща поверхня v = 0
    auto section_plane = [](const State2D& s, State2D& grad) {
        grad[0] = 0.0;
        grad[1] = 1.0;
        return s[1];
    };

    poincare::SolverConfig cfg{
        .rel_tol = 1e-10,
        .abs_tol = 1e-12,
        .initial_dt = 0.01
    };

    poincare::MapSolver<2, decltype(duffing), decltype(section_plane)> solver(duffing, section_plane, cfg);

    State2D initial_state{0.1, 0.0};
    auto series_result = solver.compute_series(initial_state, 5);

    if (!series_result) {
        std::cerr << "Помилка розрахунку перерізу Пуанкаре у C++!\n";
        return 1;
    }

    for (std::size_t i = 0; const auto& pt : *series_result) {
        std::cout << "Точка " << i++ << ": t = " << pt.time 
                  << ", state = [" << pt.state[0] << ", " << pt.state[1] << "]"
                  << ", кроків = " << pt.steps_executed << "\n";
    }

    return 0;
}
```
:::

---

### Стратегії юніт-тестування та автоматичної верифікації

Для забезпечення чисельної надійності розв'язувача бібліотека передбачає створення автоматизованих тестів регресії:

1. **Тестування на контрольних аналітичних моделях:** Перевіряється працездатність відображення для гармонічного осцилятора `d²x/dt² + ω²x = 0`. Оскільки аналітичним перерізом Пуанкаре на площині `v = 0` є послідовність точок `x* = x₀`, програма перевіряє збіжність з точністю `10⁻¹²`.
2. **Перевірка теореми про збереження фазового об'єму:** Для гамільтонових систем перевіряється умова збереження площі перерізу (якобіан відображення `det(DP) = 1`).
3. **Контроль відсутності витоків пам'яті:** Автоматизовані запуск під інструментами Valgrind Memcheck та AddressSanitizer (ASan) підтверджують повну відсутність витоків пам'яті при тривалих серійних розрахунках.

---

### Оцінка складності алгоритмів та продуктивності (Performance & Complexity)

1. **Часова складність (Time Complexity):**
   - Для обчислення однієї точки відображення Пуанкаре `P(x)` вимагається `N_steps = T_return / dt` кроків чисельного інтегрування.
   - Складність одного кроку за методом RK4 дорівнює `O(4 · C_rhs)`, де `C_rhs` — оцінка обчислювальної вартості правої частини рівнянь.
   - Пошук кореня методом Ерміта додає стаціонарну константу близько 5 ітерацій Ньютона, що дає підсумкову складність `O(N_steps · C_rhs + 5 · C_sec)`.

2. **Просторова складність (Space Complexity):**
   - Загальна оперативна пам'ять для C API становить `O(1)` додаткової пам'яті при використанні переданих користувачем буферів.
   - Для зберігання серії з `N_pts` точок розмірності `D` вимагається `O(N_pts · D)` пам'яті у купі.

---

### Сумісність із заголовочними файлами та стандартизація

Заголовочні файли `poincare_sec.h` та `poincare_sec.hpp` повністю відповідають вимогам стандарту ISO C99 та ISO C++20. Вони не містять компиляційно-залежних розширеностей (Pragmas), гарантуючи стовідсоткову портованість між компиляторами GCC, Clang та MSVC на платформах Linux, macOS та Windows. Використання стандартизованого програмного інтерфейсу забезпечує миттєву інтеграцію бібліотеки у промислові високопродуктивні обчислювальні комплекси моделювання складних фізичних та технічних систем будь-якої складності. Це гарантує надійність, довгострокову підтримку та високу точність обчислень у фундаментальних і прикладних дослідженнях.
