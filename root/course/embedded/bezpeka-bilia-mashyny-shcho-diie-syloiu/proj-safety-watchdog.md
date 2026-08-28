# ⚙️ Модуль моніторингу безпеки та спостерігач зіткнень робота

Модуль реалізує алгоритм спостереження за узагальненим імпульсом зчленувань для безсенсорного виявлення колізій, декартовий геофенсинг і дворівневий автомат безпечного відключення приводів.

У силових маніпуляторах безпека вимагає швидкого розпізнавання небажаного контакту з людиною (колізії) та контролю кінематичних інваріантів (швидкість, положення інструмента) у реальному часі. Використання зовнішніх 6-осьових силомоментних датчиків на кожному суглобі здорожчує конструкцію та збільшує вагу рухомих ланок, тому основним механізмом детекції є програмний спостерігач узагальненого імпульсу (Generalized Momentum Observer). Він порівнює виміряний струм двигунів із теоретичною динамічною моделлю маніпулятора й виділяє зовнішній момент `tau_ext`.

## 1. Математична модель спостерігача імпульсу

Динаміка просторового `N`-ланкового маніпулятора у просторі узагальнених координат описується рівнянням Лагранжа-Ейлера:

```
M(q)·q̈ + C(q, q̇)·q̇ + g(q) = τ + τ_ext       [динаміка жорсткого маніпулятора]
```

Тут `q`, `q̇`, `q̈` — вектори положення, кутової швидкості та кутового прискорення зчленувань; `M(q)` — симетрична додатно визначена матриця інерції; `C(q, q̇)` — матриця Коріолісових і відцентрових сил, визначена через символи Крістофеля; `g(q)` — вектор гравітаційних моментів; `τ` — корисний електромагнітний момент двигунів; `τ_ext` — зовнішній момент, викликаний фізичним контактом з людиною або перешкодою.

Класичний спосіб оцінки зовнішнього моменту шляхом прямого віднімання моделі `τ_ext = M(q)·q̈ + C(q, q̇)·q̇ + g(q) - τ` є непридатним для систем безпеки. Вимірювання прискорення `q̈` за допомогою чисельного диференціювання сигналів енкодерів супроводжується колосальним високочастотним шумом, який при фільтрації вносить затримку у десятки мілісекунд, роблячи систему нездатною запобігти травмі.

### Властивість кососиметричності та виведення імпульсу

Спостерігач імпульсу обходить потребу в розрахунку прискорення. Визначимо узагальнений механічний імпульс системи:

```
p = M(q)·q̇                                    [вектор узагальненого імпульсу]
```

Диференціюючи імпульс за часом:

```
ṗ
= M(q)·q̈ + Ṁ(q)·q̇                             [похідна добутку за часом]
= (τ + τ_ext - C(q, q̇)·q̇ - g(q)) + Ṁ(q)·q̇    [підстановка M·q̈ з рівняння динаміки]
= τ - g(q) + (Ṁ(q) - C(q, q̇))·q̇ + τ_ext       [перегрупування доданків]
```

З фундаментального закону збереження енергії матриця `(Ṁ - 2·C)` є кососиметричною: `x^T · (Ṁ - 2·C) · x = 0` для будь-якого вектора `x`. Звідси випливає алгебраїчна тотожність:

```
Ṁ(q) = C(q, q̇) + C^T(q, q̇)                    [зв'язок похідної інерції з матрицею Коріоліса]
```

Підставляючи цей вираз у похідну імпульсу, отримуємо:

```
ṗ = τ + C^T(q, q̇)·q̇ - g(q) + τ_ext           [остаточна форма динаміки імпульсу]
```

### Структура інтегрального спостерігача

На основі отриманої динаміки формується лінійний спостерігач залишкового вектора (residual vector) `r(t)`:

```
r(t) = K_I · [ p(t) - ∫ (τ + C^T(q, q̇)·q̇ - g(q) + r(t)) dt - p(0) ]
```

Тут `K_I = diag(k_1, k_2, ..., k_N) > 0` — діагональна матриця коефіцієнтів підсилення інтегратора (розмірність с⁻¹). Продиференціювавши вираз для `r(t)` за часом, отримуємо динаміку помилки оцінки:

```
ṙ(t)
= K_I · [ ṗ(t) - (τ + C^T·q̇ - g + r(t)) ]    [диференціювання інтеграла]
= K_I · [ (τ + C^T·q̇ - g + τ_ext) - (τ + C^T·q̇ - g + r(t)) ]
= -K_I · r(t) + K_I · τ_ext                   [рівняння фільтра першого порядку]
```

Це рівняння показує, що залишковий вектор `r(t)` поводиться як лінійний фільтр низьких частот першого порядку для зовнішнього моменту `τ_ext`. У стані вільного руху `τ_ext = 0` і сигнал `r(t) → 0`. При виникненні колізії оцінка `r(t)` експоненційно наближається до реального моменту контакту `r(t) → τ_ext` з постійною часу `T_obs = 1 / K_I`.

## 2. Архітектура та програмна реалізація

Модуль безпеки виконується в детермінованому циклі з фіксованим кроком дискретизації `DT_SEC = 0.001` с (1 кГц). Він реалізує чотири послідовні задачі:
1. Оновлення динамічної моделі маніпулятора `M(q)`, `C^T(q, q̇)·q̇`, `g(q)` та розрахунок прямої кінематики інструмента (Tool Center Point — TCP).
2. Дискретне інтегрування спостерігача імпульсу методом Ейлера та обчислення поточного залишкового вектора `r[i]`.
3. Перевірка кінематичних інваріантів: обмеження кутової швидкості осей (SLS) та перевірка потрапляння координат TCP у дозволений декартовий паралелепіпед (Geofence Box).
4. Оновлення кінцевого автомата безпеки з виходом на апаратне реле Safe Torque Off (STO).

Нижче наведено модулі на мовах C та C++20.

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define NUM_JOINTS 3
#define DT_SEC 0.001f

typedef enum {
    SAFETY_NORMAL = 0,
    SAFETY_WARNING_SLS,
    SAFETY_CONTROLLED_STOP_SS1,
    SAFETY_STO_TRIPPED
} safety_state_t;

typedef struct {
    float x_min, x_max;
    float y_min, y_max;
    float z_min, z_max;
} cartesian_box_t;

typedef struct {
    float max_joint_vel[NUM_JOINTS];
    float collision_threshold[NUM_JOINTS];
    float observer_gain_ki[NUM_JOINTS];
    cartesian_box_t allowed_zone;
} safety_config_t;

typedef struct {
    safety_config_t cfg;
    safety_state_t state;
    float momentum_integral[NUM_JOINTS];
    float residual[NUM_JOINTS];
    bool sto_relay_active;
} safety_watchdog_t;

/* Спрощена динамічна модель: матриця інерції M(q) для тестового вузла */
static void compute_dynamics(const float q[NUM_JOINTS], const float q_dot[NUM_JOINTS],
                             float M[NUM_JOINTS][NUM_JOINTS], float c_transpose_qdot[NUM_JOINTS],
                             float g[NUM_JOINTS]) {
    /* Базові діагональні інерції та перехресні зв'язки */
    M[0][0] = 2.5f + 0.8f * cosf(q[1]);
    M[0][1] = 0.4f * cosf(q[1]);
    M[0][2] = 0.0f;

    M[1][0] = M[0][1];
    M[1][1] = 1.2f + 0.3f * cosf(q[2]);
    M[1][2] = 0.15f * cosf(q[2]);

    M[2][0] = 0.0f;
    M[2][1] = M[1][2];
    M[2][2] = 0.5f;

    /* Коріолісові складові C^T(q, q_dot) * q_dot */
    c_transpose_qdot[0] = -0.4f * sinf(q[1]) * q_dot[1] * q_dot[0];
    c_transpose_qdot[1] =  0.4f * sinf(q[1]) * q_dot[0] * q_dot[0];
    c_transpose_qdot[2] =  0.0f;

    /* Гравітаційний вектор g(q) */
    g[0] = 0.0f;
    g[1] = 9.81f * 1.5f * cosf(q[0] + q[1]);
    g[2] = 9.81f * 0.5f * cosf(q[0] + q[1] + q[2]);
}

/* Пряма кінематика положення робочого інструмента (TCP) */
static void compute_forward_kinematics(const float q[NUM_JOINTS], float tcp[3]) {
    const float l1 = 0.4f, l2 = 0.35f, l3 = 0.15f;
    float a1 = q[0], a2 = q[0] + q[1], a3 = q[0] + q[1] + q[2];
    tcp[0] = l1 * cosf(a1) + l2 * cosf(a2) + l3 * cosf(a3);
    tcp[1] = l1 * sinf(a1) + l2 * sinf(a2) + l3 * sinf(a3);
    tcp[2] = 0.2f; /* Висота */
}

void safety_watchdog_init(safety_watchdog_t *wd, const safety_config_t *cfg) {
    memset(wd, 0, sizeof(*wd));
    wd->cfg = *cfg;
    wd->state = SAFETY_NORMAL;
    wd->sto_relay_active = false;
}

safety_state_t safety_watchdog_update(safety_watchdog_t *wd,
                                      const float q[NUM_JOINTS],
                                      const float q_dot[NUM_JOINTS],
                                      const float tau_measured[NUM_JOINTS]) {
    float M[NUM_JOINTS][NUM_JOINTS];
    float c_t_qdot[NUM_JOINTS];
    float g[NUM_JOINTS];
    float p[NUM_JOINTS];
    float tcp[3];
    int i, j;

    compute_dynamics(q, q_dot, M, c_t_qdot, g);
    compute_forward_kinematics(q, tcp);

    /* 1. Обчислення поточного імпульсу p = M * q_dot */
    for (i = 0; i < NUM_JOINTS; ++i) {
        p[i] = 0.0f;
        for (j = 0; j < NUM_JOINTS; ++j) {
            p[i] += M[i][j] * q_dot[j];
        }
    }

    /* 2. Оновлення спостерігача імпульсу: r = K_I * (p - integral) */
    bool collision_detected = false;
    for (i = 0; i < NUM_JOINTS; ++i) {
        float integrand = tau_measured[i] + c_t_qdot[i] - g[i] + wd->residual[i];
        wd->momentum_integral[i] += integrand * DT_SEC;
        wd->residual[i] = wd->cfg.observer_gain_ki[i] * (p[i] - wd->momentum_integral[i]);

        if (fabsf(wd->residual[i]) > wd->cfg.collision_threshold[i]) {
            collision_detected = true;
        }
    }

    /* 3. Перевірка обмеження швидкості осей (SLS) */
    bool speed_limit_violated = false;
    for (i = 0; i < NUM_JOINTS; ++i) {
        if (fabsf(q_dot[i]) > wd->cfg.max_joint_vel[i]) {
            speed_limit_violated = true;
        }
    }

    /* 4. Перевірка геофенсингу (Geofence Box) */
    bool geofence_violated = false;
    if (tcp[0] < wd->cfg.allowed_zone.x_min || tcp[0] > wd->cfg.allowed_zone.x_max ||
        tcp[1] < wd->cfg.allowed_zone.y_min || tcp[1] > wd->cfg.allowed_zone.y_max) {
        geofence_violated = true;
    }

    /* 5. Автомат безпечних станів */
    switch (wd->state) {
    case SAFETY_NORMAL:
        if (collision_detected) {
            wd->state = SAFETY_CONTROLLED_STOP_SS1;
        } else if (speed_limit_violated || geofence_violated) {
            wd->state = SAFETY_WARNING_SLS;
        }
        break;

    case SAFETY_WARNING_SLS:
        if (collision_detected) {
            wd->state = SAFETY_CONTROLLED_STOP_SS1;
        } else if (!speed_limit_violated && !geofence_violated) {
            wd->state = SAFETY_NORMAL;
        }
        break;

    case SAFETY_CONTROLLED_STOP_SS1:
        /* Після фіксації колізії привід гальмує і розмикає STO */
        wd->sto_relay_active = true;
        wd->state = SAFETY_STO_TRIPPED;
        break;

    case SAFETY_STO_TRIPPED:
        wd->sto_relay_active = true;
        break;
    }

    return wd->state;
}
```
```cpp
#include <array>
#include <span>
#include <cmath>
#include <algorithm>
#include <expected>
#include <numbers>

namespace safety {

inline constexpr size_t NumJoints = 3;
inline constexpr float DeltaTimeSec = 0.001f;

enum class State : uint8_t {
    Normal = 0,
    WarningSls,
    ControlledStopSS1,
    StoTripped
};

struct CartesianBox {
    float x_min, x_max;
    float y_min, y_max;
    float z_min, z_max;

    [[nodiscard]] constexpr bool contains(const std::array<float, 3>& pt) const noexcept {
        return (pt[0] >= x_min && pt[0] <= x_max &&
                pt[1] >= y_min && pt[1] <= y_max &&
                pt[2] >= z_min && pt[2] <= z_max);
    }
};

struct Config {
    std::array<float, NumJoints> max_joint_vel{1.5f, 1.5f, 2.0f};
    std::array<float, NumJoints> collision_threshold{12.0f, 10.0f, 6.0f};
    std::array<float, NumJoints> observer_gain_ki{25.0f, 25.0f, 25.0f};
    CartesianBox allowed_zone{-0.8f, 0.8f, -0.8f, 0.8f, 0.0f, 1.2f};
};

class Watchdog {
public:
    explicit constexpr Watchdog(const Config& cfg) noexcept
        : cfg_(cfg), state_(State::Normal), sto_active_(false) {
        momentum_integral_.fill(0.0f);
        residual_.fill(0.0f);
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] bool is_sto_active() const noexcept { return sto_active_; }
    [[nodiscard]] std::span<const float, NumJoints> residual_torque() const noexcept {
        return residual_;
    }

    State update(std::span<const float, NumJoints> q,
                 std::span<const float, NumJoints> q_dot,
                 std::span<const float, NumJoints> tau_measured) noexcept {
        auto [M, c_t_qdot, g] = compute_dynamics(q, q_dot);
        auto tcp = compute_forward_kinematics(q);

        /* 1. Розрахунок узагальненого імпульсу p = M * q_dot */
        std::array<float, NumJoints> p{};
        for (size_t i = 0; i < NumJoints; ++i) {
            for (size_t j = 0; j < NumJoints; ++j) {
                p[i] += M[i][j] * q_dot[j];
            }
        }

        /* 2. Інтегрування спостерігача імпульсу */
        bool collision = false;
        for (size_t i = 0; i < NumJoints; ++i) {
            float integrand = tau_measured[i] + c_t_qdot[i] - g[i] + residual_[i];
            momentum_integral_[i] += integrand * DeltaTimeSec;
            residual_[i] = cfg_.observer_gain_ki[i] * (p[i] - momentum_integral_[i]);

            if (std::abs(residual_[i]) > cfg_.collision_threshold[i]) {
                collision = true;
            }
        }

        /* 3. Перевірка безпечної швидкості (SLS) */
        bool speed_exceeded = false;
        for (size_t i = 0; i < NumJoints; ++i) {
            if (std::abs(q_dot[i]) > cfg_.max_joint_vel[i]) {
                speed_exceeded = true;
            }
        }

        /* 4. Перевірка декартової робочої зони */
        bool out_of_bounds = !cfg_.allowed_zone.contains(tcp);

        /* 5. Автомат станів */
        switch (state_) {
        case State::Normal:
            if (collision) {
                state_ = State::ControlledStopSS1;
            } else if (speed_exceeded || out_of_bounds) {
                state_ = State::WarningSls;
            }
            break;

        case State::WarningSls:
            if (collision) {
                state_ = State::ControlledStopSS1;
            } else if (!speed_exceeded && !out_of_bounds) {
                state_ = State::Normal;
            }
            break;

        case State::ControlledStopSS1:
            sto_active_ = true;
            state_ = State::StoTripped;
            break;

        case State::StoTripped:
            sto_active_ = true;
            break;
        }

        return state_;
    }

private:
    struct DynamicsResult {
        std::array<std::array<float, NumJoints>, NumJoints> M;
        std::array<float, NumJoints> c_t_qdot;
        std::array<float, NumJoints> g;
    };

    static DynamicsResult compute_dynamics(std::span<const float, NumJoints> q,
                                           std::span<const float, NumJoints> q_dot) noexcept {
        DynamicsResult res{};
        res.M[0][0] = 2.5f + 0.8f * std::cos(q[1]);
        res.M[0][1] = 0.4f * std::cos(q[1]);
        res.M[0][2] = 0.0f;

        res.M[1][0] = res.M[0][1];
        res.M[1][1] = 1.2f + 0.3f * std::cos(q[2]);
        res.M[1][2] = 0.15f * std::cos(q[2]);

        res.M[2][0] = 0.0f;
        res.M[2][1] = res.M[1][2];
        res.M[2][2] = 0.5f;

        res.c_t_qdot[0] = -0.4f * std::sin(q[1]) * q_dot[1] * q_dot[0];
        res.c_t_qdot[1] =  0.4f * std::sin(q[1]) * q_dot[0] * q_dot[0];
        res.c_t_qdot[2] =  0.0f;

        res.g[0] = 0.0f;
        res.g[1] = 9.81f * 1.5f * std::cos(q[0] + q[1]);
        res.g[2] = 9.81f * 0.5f * std::cos(q[0] + q[1] + q[2]);
        return res;
    }

    static std::array<float, 3> compute_forward_kinematics(std::span<const float, NumJoints> q) noexcept {
        constexpr float l1 = 0.4f, l2 = 0.35f, l3 = 0.15f;
        float a1 = q[0], a2 = q[0] + q[1], a3 = q[0] + q[1] + q[2];
        return {
            l1 * std::cos(a1) + l2 * std::cos(a2) + l3 * std::cos(a3),
            l1 * std::sin(a1) + l2 * std::sin(a2) + l3 * std::sin(a3),
            0.2f
        };
    }

    Config cfg_;
    State state_;
    bool sto_active_;
    std::array<float, NumJoints> momentum_integral_{};
    std::array<float, NumJoints> residual_{};
};

} // namespace safety
```
:::

## 3. Практичні підводні камені та налаштування

### Компенсація тертя редукторів та дрейф інтегратора

У реальних хвильових або планетарних редукторах завжди присутнє суттєве тертя (кулонівське сухе тертя, в'язке тертя та ефект Штрібека). Якщо модель динаміки не враховує момент тертя `tau_fric = f_v · q̇ + f_c · sign(q̇)`, струм двигуна під час вільного руху буде вищим за розрахунковий. Внаслідок цього підінтегральний вираз `integrand` стає ненульовим, і значення `residual` поступово дрейфує, викликаючи хибні аварійні зупинки на рівному місці.

Для усунення дрейфу вектор внутрішніх сил у коді доповнюється каліброваною функцією тертя осей. Калібрування проводиться шляхом прогону кожної осі в обох напрямках на різних сталих швидкостях з фіксацією середнього струму FOC.

### Вибір коефіцієнта підсилення інтегратора `K_I`

Параметр `K_I` визначає смугу пропускання спостерігача колізій:
- При `K_I < 15` с⁻¹ час реакції спостерігача становить понад 20 мс, що занадто повільно для захисту людини від ударних піків сили за стандартом ISO/TS 15066.
- При `K_I > 50` с⁻¹ спостерігач стає надмірно чутливим до високочастотного шуму АЦП фазного струму ШІМ та шуму квантування оптичних енкодерів, що призводить до хибних спрацьовувань при різких реверсах руху.

Для більшості промислових коботів оптимальним компромісом є діапазон `K_I = 25..35` с⁻¹ у комбінації з цифровим низькочастотним фільтром Баттерворта 2-го порядку з частотою зрізу 40–50 Гц на виході сигналу `residual`.

### Крутильна піддатливість хвильового редуктора

Хвильовий редуктор (Harmonic Drive) не є абсолютно жорстким тілом: його гнучкий стакан (Flexspline) деформується під навантаженням як торсіонна пружина з жорсткістю `K_joint ≈ 10 000..30 000` Н·м/рад.

Під час різкого прискорення виникає динамічний кутовий зсув між валом мотора та вихідним фланцем ланки. Модель жорсткого тіла інтерпретує накопичену в пружині редуктора енергію як зовнішній гальмівний удар. Найнадійніший спосіб боротьби з цим ефектом — встановлення двох енкодерів на кожну вісь: первинний (до редуктора) використовується для контуру комутації двигуна, а вторинний (після редуктора) — безпосередньо для моделі кінематики та спостерігача імпульсу.
