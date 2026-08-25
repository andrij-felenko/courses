# 📋 Інтерфейс бібліотеки фазового аналізу: контракти, структури та конфігурація

У цій довідковій вставці детально специфіковано публічний програмний інтерфейс (API) універсальної обчислювальної бібліотеки аналізу та чисельної картографії фазового простору двовимірних автономних систем `libphase`.

Інтерфейс розроблено для задоволення потреб високоефективного чисельного моделювання фізичних систем, робототехнічних контролерів, симуляцій електронних генераторів та систем автоматичного керування. Бібліотека надає повний спектр функцій: від швидкого чисельного інтегрування одиночних фазових траєкторій методом Рунґе-Кутти до автоматичного пошуку точок рівноваги, обчислення Якобіана, класифікації їхнього топологічного типу та генерації двовимірних векторних сіток для візуалізації фазового поля.

---

### 1. Архитектурний контракт та фундаментальні типи даних

Архітектура бібліотеки `libphase` побудована на чіткому розділенні відповідальності між описом фізичної моделі (права частина диференціальних рівнянь), чисельним рушієм інтегрування та аналітичним модулем класифікації особливих точок. 

Програмний контракт оперує чотирма основними сутностями:

1. **Точка фазового стану (`PhasePoint`)** — базова геометрична сутність у двовимірному фазовому просторі, яка задається двома плаваючими числами подвійної точності `q` (узагальнена координата) та `p` (узагальнений імпульс або швидкість).
2. **Опис векторного поля (`PhaseSystem`)** — структура-контейнер, яка зв'язує вказівник на користувацьку функцію обчислення правих частин диференціальних рівнянь `(dq/dt, dp/dt)` із довільним контекстним вказівником `user_data`, що містить фізичні параметри системи (масу, жорсткість пружини, коефіцієнт тертя, індуктивність тощо).
3. **Опишувач особливої точки (`SingularPointInfo`)** — об'ємна структура даних, що містить вичерпний результат аналізу стійкості точки рівноваги: її точні координати, елементи матриці Якобі, слід, детермінант, дискримінант, комплексна пара власних значень `λ₁,₂` та підсумковий топологічний прапор.
4. **Конфігурація векторної сітки (`PhaseGridConfig`)** — специфікація прямокутного вікна фазового простору (межі по координаті та імпульсу, а також роздільна здатність сітки) для масового обчислення векторів фазової швидкості.

#### Перелік типів особливих точок (`PhaseSingularType`)

Топологічна класифікація особливих точок здійснюється аналітичним модулем бібліотеки на основі аналізу знаків інваріантів Якобіана — детермінанта `Det(J)`, сліду `Tr(J)` та дискримінанта характеристичного рівняння `Δ = (Tr J)² - 4·Det(J)`.

Всі можливі топологічні стани представлено у спеціалізованому переліку `PhaseSingularType`:

```
Значення Enum              Математична умова                        Фізичний та топологічний опис
-----------------------------------------------------------------------------------------------------------------------------------
SINGULAR_SADDLE            Det(J) < 0                               Сідло: нестійка точка розгалуження траєкторій;
                                                                    власні значення дійсні й мають протилежні знаки.

SINGULAR_CENTER            Det(J) > 0, Tr(J) == 0, Δ < 0            Центр: консервативні ізольовані коливання;
                                                                    траєкторії є концентричними замкненими еліпсами.

SINGULAR_FOCUS_STABLE      Det(J) > 0, Tr(J) < 0, Δ < 0             Стійкий фокус: згасаючі спіральні коливання;
                                                                    траєкторії закручуються всередину до точки рівноваги.

SINGULAR_FOCUS_UNSTABLE    Det(J) > 0, Tr(J) > 0, Δ < 0             Нестійкий фокус: зростаючі спіральні коливання;
                                                                    траєкторії розкручуються назовні від точки рівноваги.

SINGULAR_NODE_STABLE       Det(J) > 0, Tr(J) < 0, Δ >= 0            Стійкий вузол: аперіодичне згасання без осциляцій;
                                                                    траєкторії експоненційно входять у точку рівноваги.

SINGULAR_NODE_UNSTABLE     Det(J) > 0, Tr(J) > 0, Δ >= 0            Нестійкий вузол: аперіодичне зростання без осциляцій;
                                                                    траєкторії випромінюються з точки в усіх напрямках.

SINGULAR_DEGENERATE        Det(J) == 0                              Вироджена точка: детермінант Якобіана дорівнює нулю;
                                                                    система має лінію або область неізольованих рівноваг.
```

---

### 2. Специфікація інтерфейсу мовами C та C++

Для забезпечення максимальної гнучкості бібліотека `libphase` надає два рівня програмного інтерфейсу:

1. **Низькорівневий C-інтерфейс (`phase_portrait_api.h`)** — розроблений за стандартами C99 з суворим дотриманням правила ABI-сумісності. Він не використовує винятків, підтримує прямий виклик з мов C, Rust, Python (через `ctypes` або `cffi`), Fortran та Assembly, і повертає коди помилок через значення типу `PhaseStatus`.
2. **Високорівневий C++20-інтерфейс (`PhaseEngine.hpp`)** — виразна об'єктно-орієнтована обгортка, побудована на сучасних стандартах C++20. Він утилізує концепт `std::expected` для безпечної обробки помилок без викидання винятків, підтримує лямбда-вирази у якості векторних полів, оперує метапрограмуванням і забезпечує повну відсутність накладних витрат (zero-cost abstractions).

:::tabs
```c
/* phase_portrait_api.h — Публічний C-інтерфейс бібліотеки libphase */
#ifndef PHASE_PORTRAIT_API_H
#define PHASE_PORTRAIT_API_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди повернення та статусів помилок */
typedef enum {
    PHASE_SUCCESS               =  0,  /* Успішне виконання операції */
    PHASE_ERROR_NULL_POINTER    = -1,  /* Передано нульовий вказівник */
    PHASE_ERROR_INVALID_PARAM   = -2,  /* Некоректні параметри (наприклад, step <= 0) */
    PHASE_ERROR_DIVERGENCE      = -3,  /* Траєкторія пішла в нескінченність (переповнення) */
    PHASE_ERROR_CONVERGENCE     = -4,  /* Не вдалося знайти особливу точку за макс. кроків */
    PHASE_ERROR_ALLOCATION      = -5   /* Помилка виділення пам'яті */
} PhaseStatus;

/* Точка у двовимірному фазовому просторі (q, p) */
typedef struct {
    double q; /* Узагальнена координата */
    double p; /* Узагальнений імпульс або швидкість */
} PhasePoint;

/* Похідні стану (dq/dt, dp/dt) */
typedef struct {
    double dq_dt;
    double dp_dt;
} PhaseDerivs;

/* Прототип функції правих частин системи: F(t, state, user_data, derivs) */
typedef void (*PhaseVectorFieldFn)(double t, const PhasePoint* state, void* user_data, PhaseDerivs* derivs);

/* Структура опису динамічної системи */
typedef struct {
    PhaseVectorFieldFn field_fn; /* Вказівник на функцію поля */
    void* user_data;             /* Довільні параметри фізичної моделі */
} PhaseSystem;

/* Класифікаційний тип особливої точки */
typedef enum {
    SINGULAR_SADDLE = 0,
    SINGULAR_CENTER,
    SINGULAR_FOCUS_STABLE,
    SINGULAR_FOCUS_UNSTABLE,
    SINGULAR_NODE_STABLE,
    SINGULAR_NODE_UNSTABLE,
    SINGULAR_DEGENERATE
} PhaseSingularType;

/* Детальний опишувач особливої точки */
typedef struct {
    PhasePoint point;           /* Координати особливої точки (q0, p0) */
    double jacobian[2][2];      /* Матриця Якобі J у цій точці */
    double trace;               /* Слід Tr(J) */
    double det;                 /* Детермінант Det(J) */
    double discr;               /* Дискримінант (Tr J)^2 - 4*Det */
    double lambda1_re;          /* Дійсна частина першого власного значення */
    double lambda1_im;          /* Уявна частина першого власного значення */
    double lambda2_re;          /* Дійсна частина другого власного значення */
    double lambda2_im;          /* Уявна частина другого власного значення */
    PhaseSingularType type;     /* Топологічний тип точки */
} SingularPointInfo;

/* Конфігурація сітки фазового поля */
typedef struct {
    double q_min;
    double q_max;
    size_t q_steps;
    double p_min;
    double p_max;
    size_t p_steps;
} PhaseGridConfig;

/* Запис одного вектора сітки */
typedef struct {
    PhasePoint point;
    PhaseDerivs derivs;
    double magnitude;
} PhaseGridVector;

/* === ОСНОВНІ ФУНКЦІЇ АНАЛІТИЧНОГО ТА ЧИСЕЛЬНОГО АПІ === */

/**
 * @brief Обчислити один крок інтегрування методом RK4.
 * @param sys Посилання на систему.
 * @param current Поточний фазовий стан.
 * @param t Поточний час.
 * @param h Крок інтегрування.
 * @param next [out] Результат наступного стану.
 * @return PHASE_SUCCESS або код помилки.
 */
PhaseStatus phase_rk4_step(const PhaseSystem* sys, const PhasePoint* current, double t, double h, PhasePoint* next);

/**
 * @brief Проінтегрувати повну траєкторію та зберегти в масив.
 * @param sys Посилання на систему.
 * @param initial Початковий стан.
 * @param h Крок за часом.
 * @param steps Кількість кроків.
 * @param out_buffer [out] Виділений масив розміром (steps + 1) PhasePoint.
 * @return PHASE_SUCCESS або код помилки.
 */
PhaseStatus phase_integrate_trajectory(const PhaseSystem* sys, const PhasePoint* initial, double h, size_t steps, PhasePoint* out_buffer);

/**
 * @brief Обчислити матрицю Якобі чисельним диференціюванням у заданій точці.
 * @param sys Посилання на систему.
 * @param pt Точка, у якій обчислюється Якобіан.
 * @param eps Приріст для чисельної похідної (наприклад, 1e-6).
 * @param jacobian [out] Матриця 2x2.
 */
PhaseStatus phase_compute_jacobian(const PhaseSystem* sys, const PhasePoint* pt, double eps, double jacobian[2][2]);

/**
 * @brief Проаналізувати та класифікувати особливу точку.
 * @param sys Посилання на систему.
 * @param pt Точка рівноваги (де f=0, g=0).
 * @param info [out] Детальна структура аналізу.
 */
PhaseStatus phase_analyze_singular_point(const PhaseSystem* sys, const PhasePoint* pt, SingularPointInfo* info);

/**
 * @brief Сформувати масив векторів поля на прямокутній сітці.
 * @param sys Посилання на систему.
 * @param config Параметри сітки.
 * @param out_grid [out] Виділений буфер розміром (q_steps * p_steps) PhaseGridVector.
 */
PhaseStatus phase_generate_grid(const PhaseSystem* sys, const PhaseGridConfig* config, PhaseGridVector* out_grid);

#ifdef __cplusplus
}
#endif

#endif /* PHASE_PORTRAIT_API_H */
```
```cpp
// PhaseEngine.hpp — Високорівневий C++20 інтерфейс бібліотеки phase
#ifndef PHASE_ENGINE_HPP
#define PHASE_ENGINE_HPP

#include <array>
#include <vector>
#include <functional>
#include <expected>
#include <string_view>
#include <complex>

namespace phase {

enum class ErrorCode {
    NullPointer,
    InvalidParameter,
    Divergence,
    ConvergenceFailed,
    AllocationFailed
};

struct Point {
    double q{0.0};
    double p{0.0};

    [[nodiscard]] constexpr Point operator+(const Point& rhs) const noexcept {
        return {q + rhs.q, p + rhs.p};
    }
    [[nodiscard]] constexpr Point operator*(double s) const noexcept {
        return {q * s, p * s};
    }
};

struct Derivs {
    double dq_dt{0.0};
    double dp_dt{0.0};
};

using VectorField = std::function<Derivs(double t, const Point& state)>;

enum class SingularType {
    Saddle,
    Center,
    FocusStable,
    FocusUnstable,
    NodeStable,
    NodeUnstable,
    Degenerate
};

struct SingularAnalysis {
    Point location;
    std::array<std::array<double, 2>, 2> jacobian;
    double trace;
    double det;
    double discriminant;
    std::complex<double> lambda1;
    std::complex<double> lambda2;
    SingularType type;
};

struct GridConfig {
    double q_min{-5.0};
    double q_max{5.0};
    std::size_t q_steps{30};
    double p_min{-5.0};
    double p_max{5.0};
    std::size_t p_steps{30};
};

struct GridVector {
    Point point;
    Derivs derivs;
    double magnitude;
};

class SystemEngine {
public:
    explicit SystemEngine(VectorField field) : field_(std::move(field)) {}

    // Обчислення наступного стану за допомогою RK4
    [[nodiscard]] Point rk4_step(const Point& current, double t, double h) const noexcept {
        const auto k1 = field_(t, current);
        const Point p1{current.q + 0.5 * h * k1.dq_dt, current.p + 0.5 * h * k1.dp_dt};

        const auto k2 = field_(t + 0.5 * h, p1);
        const Point p2{current.q + 0.5 * h * k2.dq_dt, current.p + 0.5 * h * k2.dp_dt};

        const auto k3 = field_(t + 0.5 * h, p2);
        const Point p3{current.q + h * k3.dq_dt, current.p + h * k3.dp_dt};

        const auto k4 = field_(t + h, p3);

        return {
            current.q + (h / 6.0) * (k1.dq_dt + 2.0 * k2.dq_dt + 2.0 * k3.dq_dt + k4.dq_dt),
            current.p + (h / 6.0) * (k1.dp_dt + 2.0 * k2.dp_dt + 2.0 * k3.dp_dt + k4.dp_dt)
        };
    }

    // Інтегрування траєкторії із поверненням std::expected
    [[nodiscard]] std::expected<std::vector<Point>, ErrorCode>
    integrate(const Point& initial, double h, std::size_t steps) const {
        if (h <= 0.0 || steps == 0) {
            return std::unexpected(ErrorCode::InvalidParameter);
        }

        std::vector<Point> traj;
        traj.reserve(steps + 1);
        Point curr = initial;
        double t = 0.0;
        traj.push_back(curr);

        for (std::size_t i = 0; i < steps; ++i) {
            curr = rk4_step(curr, t, h);
            if (std::isnan(curr.q) || std::isnan(curr.p) || std::isinf(curr.q) || std::isinf(curr.p)) {
                return std::unexpected(ErrorCode::Divergence);
            }
            traj.push_back(curr);
            t += h;
        }

        return traj;
    }

    // Обчислення Якобіана та аналіз стійкості
    [[nodiscard]] std::expected<SingularAnalysis, ErrorCode>
    analyze_singular_point(const Point& eq_pt, double eps = 1e-6) const {
        const auto d0 = field_(0.0, eq_pt);
        if (std::hypot(d0.dq_dt, d0.dp_dt) > 1e-3) {
            return std::unexpected(ErrorCode::InvalidParameter); // Точка не є рівноважною
        }

        // Чисельне диференціювання для Якобіана
        const auto dq_plus  = field_(0.0, Point{eq_pt.q + eps, eq_pt.p});
        const auto dq_minus = field_(0.0, Point{eq_pt.q - eps, eq_pt.p});
        const auto dp_plus  = field_(0.0, Point{eq_pt.q, eq_pt.p + eps});
        const auto dp_minus = field_(0.0, Point{eq_pt.q, eq_pt.p - eps});

        double J00 = (dq_plus.dq_dt - dq_minus.dq_dt) / (2.0 * eps);
        double J01 = (dp_plus.dq_dt - dp_minus.dq_dt) / (2.0 * eps);
        double J10 = (dq_plus.dp_dt - dq_minus.dp_dt) / (2.0 * eps);
        double J11 = (dp_plus.dp_dt - dp_minus.dp_dt) / (2.0 * eps);

        double tr = J00 + J11;
        double det = J00 * J11 - J01 * J10;
        double discr = tr * tr - 4.0 * det;

        SingularAnalysis res{};
        res.location = eq_pt;
        res.jacobian = {{{J00, J01}, {J10, J11}}};
        res.trace = tr;
        res.det = det;
        res.discriminant = discr;

        if (discr >= 0.0) {
            res.lambda1 = std::complex<double>((tr + std::sqrt(discr)) / 2.0, 0.0);
            res.lambda2 = std::complex<double>((tr - std::sqrt(discr)) / 2.0, 0.0);
        } else {
            res.lambda1 = std::complex<double>(tr / 2.0,  std::sqrt(-discr) / 2.0);
            res.lambda2 = std::complex<double>(tr / 2.0, -std::sqrt(-discr) / 2.0);
        }

        // Класифікація
        if (det < 0.0) {
            res.type = SingularType::Saddle;
        } else if (std::abs(tr) < 1e-7 && discr < 0.0) {
            res.type = SingularType::Center;
        } else if (discr < 0.0) {
            res.type = (tr < 0.0) ? SingularType::FocusStable : SingularType::FocusUnstable;
        } else if (det > 0.0) {
            res.type = (tr < 0.0) ? SingularType::NodeStable : SingularType::NodeUnstable;
        } else {
            res.type = SingularType::Degenerate;
        }

        return res;
    }

private:
    VectorField field_;
};

} // namespace phase

#endif // PHASE_ENGINE_HPP
```
:::

---

### 3. Детальний розбір функцій та гарантії викликів

Розглянемо семантику, вхідні вимоги та гарантії виконання кожної публічної функції бібліотеки `libphase`.

#### 3.1. Функція `phase_rk4_step`

```
PhaseStatus phase_rk4_step(const PhaseSystem* sys, const PhasePoint* current, double t, double h, PhasePoint* next);
```

- **Призначення:** Виконує обчислення точно одного кроку чисельного інтегрування стану `current` на проміжок часу `h` із використанням класичного 4-етапного алгоритму Рунґе-Кутти.
- **Вхідні вимоги:** 
  - Вказівники `sys`, `current` та `next` не повинні бути `NULL`.
  - Вказівник `sys->field_fn` має посилатися на коректну функцію правих частин.
  - Крок `h` повинен бути строго більшим за нуль (`h > 0.0`).
- **Семантика роботи:** Залежно від переданого стану `current`, функція чотири рази викликає користувацьку функцію `sys->field_fn` для обчислення векторів похідних у проміжних точках `(t, X)`, `(t + h/2, X + h/2·k₁)`, `(t + h/2, X + h/2·k₂)` та `(t + h, X + h·k₃)`. Результат зваженої суми записується в заздалегідь виділену пам'ять за вказівником `next`.
- **Повернене значення:** При успіху повертає `PHASE_SUCCESS`. Якщо один з вказівників нульовий — повертає `PHASE_ERROR_NULL_POINTER`. Якщо `h <= 0` — повертає `PHASE_ERROR_INVALID_PARAM`.

#### 3.2. Функція `phase_integrate_trajectory`

```
PhaseStatus phase_integrate_trajectory(const PhaseSystem* sys, const PhasePoint* initial, double h, size_t steps, PhasePoint* out_buffer);
```

- **Призначення:** Здійснює серійне інтегрування фазової траєкторії, починаючи від стану `initial`, протягом `steps` кроків з часовим інтервалом `h`.
- **Вимоги до пам'яті:** Користувач зобов'язаний заздалегідь виділити неперервний масив пам'яті розміром щонайменше `(steps + 1) * sizeof(PhasePoint)`. Першим елементом `out_buffer[0]` буде записано точно стан `initial`.
- **Контроль дивергенції:** На кожному кроці функція перевіряє значення координат на вихід за межі чисел з плаваючою крапкою (`isnan` або `isinf`). Якщо система розганяється до нескінченності (наприклад, при русі по нестійкій сепаратрисі чи при вибуховій нелінійності), обчислення переривається, а функція повертає код `PHASE_ERROR_DIVERGENCE`.

#### 3.3. Функція `phase_analyze_singular_point`

```
PhaseStatus phase_analyze_singular_point(const PhaseSystem* sys, const PhasePoint* pt, SingularPointInfo* info);
```

- **Призначення:** Проводить повний аналітичний та чисельний аналіз точки рівноваги `pt`.
- **Алгоритм роботи:**
  1. Перевіряє, чи дійсно у точці `pt` фазова швидкість близька до нуля `||V(pt)|| < 1e-3`. Якщо значення перевищує поріг, функція повертає `PHASE_ERROR_INVALID_PARAM`.
  2. Виконує чисельне диференціювання методом центральних різниць із кроком `eps = 1e-6` для формування елементів `2 × 2` матриці Якобі `J`.
  3. Обчислити інваріанти: слід `Tr(J) = J₀₀ + J₁₁`, детермінант `Det(J) = J₀₀·J₁₁ - J₀₁·J₁₀` та дискримінант `Δ = (Tr J)² - 4·Det(J)`.
  4. Знаходить комплексну пару власних значень `λ₁,₂ = (Tr J ± √Δ) / 2`.
  5. Заповнює прапор `info->type` відповідно до класифікаційної таблиці (Сідло, Центр, Фокус, Вузол).

---

### 4. Вимоги до потокобезпечності та пам'яті

При використанні бібліотеки `libphase` у багатонаправлених (multi-threaded) додатках реального часу або в інтерактивних візуалізаторах графічного інтерфейсу (Qt, OpenGL, ImGui) розробник повинен дотримуватися наступних гарантій потокобезпечності:

1. **Відсутність внутрішнього глобального стану:** Жодна з функцій C-інтерфейсу `libphase` не зберігає внутрішніх статичних або глобальних змінних. Функції є повністю чисто реентрабельними (reentrant).
2. **Паралельне обчислення сітки:** Виклики `phase_rk4_step` та `phase_generate_grid` для різних незалежних екземплярів буферів пам'яті можуть безпечно здійснюватися паралельно з кількох потоків без використання блокувальних примітивів (мутексів).
3. **Контекстний вказівник `user_data`:** Розробник зобов'язаний гарантувати, що об'єкт, на який вказує `user_data`, не модифікується іншими потоками під час виконання чисельного інтегрування.

#### Багатоточкова інтеграція з візуалізаційними графічними рушіями

При побудові реальних графічних інтерфейсів фазових портретів (наприклад, у наукових пакетах візуалізації або навчальних лабораторних стендах) бібліотека надає оптимальний масив векторів `PhaseGridVector`.

Кожен елемент `PhaseGridVector` містить координати точки `(q, p)`, компоненти векторів похідних `(dq_dt, dp_dt)` та норму вектора `magnitude`. Норма вектора використовується візуалізаційним рушієм для кодування кольору стрілок (наприклад, колірна гама від синього для повільного руху до червоного для високих фазових швидкостей).

---

### 5. Модуль реконструкції часових рядів (`phase_embed.h`)

Для практичних завдань експериментальної фізики бібліотека надає допоміжний модуль фазової реконструкції одночасових скалярних сигналів за теоремою Такена.

:::tabs
```c
/* phase_embed.h — C-інтерфейс фазової реконструкції за теоремою Такена */
typedef struct {
    double delay_tau;   /* Часова затримка tau */
    size_t dim;         /* Розмірність вкладення d */
} PhaseEmbedConfig;

/**
 * @brief Оцінити оптимальну часову затримку tau за першим нулем автокореляції.
 * @param signal Вхідний часовий ряд.
 * @param length Довжина ряду.
 * @return Оптимальне значення tau у відліках.
 */
size_t phase_estimate_delay_tau(const double* signal, size_t length);

/**
 * @brief Реконструювати фазову траєкторію за допомогою вектора затримок.
 * @param signal Скалярний сигнал x(t).
 * @param length Кількість відліків.
 * @param config Параметри вкладення.
 * @param out_points [out] Реконструйований масив векторів Y(t).
 */
PhaseStatus phase_reconstruct_portrait(const double* signal, size_t length, const PhaseEmbedConfig* config, double* out_points);
```
```cpp
// PhaseEmbed.hpp — Високорівневий C++20 модуль фазової реконструкції
#ifndef PHASE_EMBED_HPP
#define PHASE_EMBED_HPP

#include <span>
#include <vector>
#include <expected>
#include <cstddef>

namespace phase {

struct EmbedConfig {
    double delay_tau{1.0};
    std::size_t dim{2};
};

/**
 * @brief Оцінити оптимальну часову затримку tau за першим нулем автокореляції.
 * @param signal Вхідний часовий ряд у вигляді span.
 * @return Оптимальне значення tau у відліках або код помилки.
 */
[[nodiscard]] std::expected<std::size_t, ErrorCode>
estimate_delay_tau(std::span<const double> signal) noexcept;

/**
 * @brief Реконструювати фазову траєкторію за допомогою вектора затримок.
 * @param signal Скалярний сигнал x(t).
 * @param config Параметри вкладення.
 * @return Масив реконструйованих векторів Y(t) або код помилки.
 */
[[nodiscard]] std::expected<std::vector<double>, ErrorCode>
reconstruct_portrait(std::span<const double> signal, const EmbedConfig& config);

} // namespace phase

#endif // PHASE_EMBED_HPP
```
:::

---

### 6. Специфікація параметрів конфігурації та коди помилок

При генерації сітки векторного поля за допомогою функції `phase_generate_grid` структура `PhaseGridConfig` задає розміри прямокутного вікна фазового простору та щільність вузлів.

#### Поля структури конфігурації сітки (`PhaseGridConfig`)

```
Поле структури      Тип         Замовчування     Опис, межі та фізичні вимоги
-----------------------------------------------------------------------------------------------------------------------------------
q_min               double      -5.0             Нижня межа узагальненої координати q у фазовому просторі.

q_max               double       5.0             Верхня межа узагальненої координати q (вимога: q_max > q_min).

q_steps             size_t       30              Кількість вузлів дискретизації по координаті q (вимога: q_steps >= 2).

p_min               double      -5.0             Нижня межа імпульсу чи швидкості p у фазовому просторі.

p_max               double       5.0             Верхня межа імпульсу чи швидкості p (вимога: p_max > p_min).

p_steps             size_t       30              Кількість вузлів дискретизації по імпульсу p (вимога: p_steps >= 2).
```

#### Повна таблиця статусів помилок та рекомендацій розробнику

```
Код помилки                    Семантика та причина виникнення               Рекомендована дія у коді розробника
-----------------------------------------------------------------------------------------------------------------------------------
PHASE_SUCCESS                  Операцію виконано успішно без зауважень.      Продовжити обробку отриманих даних.

PHASE_ERROR_NULL_POINTER       Вказано NULL замість обов'язкового буфера     Перевірити ініціалізацію вказівників перед
                               чи структури динамічної системи.              викликом функції.

PHASE_ERROR_INVALID_PARAM      Крок інтегрування h <= 0, steps == 0 або      Перевірити некоректні межі q_min/q_max та
                               межі сітки переплутані місцями.              значення кроку часової сітки h.

PHASE_ERROR_DIVERGENCE         Координати q або p стали NaN чи Inf через     Зменшити крок h, перевірити стійкість або
                               чисельну нестійкість розрахунку.              встановити обмежувальні пороги.

PHASE_ERROR_CONVERGENCE        Чисельний метод локалізації не зміг знайти    Збільшити максимальну кількість ітерацій
                               точний нуль векторного поля.                 або зменшити точність eps.

PHASE_ERROR_ALLOCATION         Помилка виділення динамічної пам'яті          Перевірити наявність вільної оперативної
                               під буфер векторної сітки.                    пам'яті в системі.
```

Застосування вищенаведених контрактів гарантує повну обчислювальну стабільність, відсутність витоків пам'яті та коректну класифікацію особливих точок при побудові будь-яких фазових портретів.
