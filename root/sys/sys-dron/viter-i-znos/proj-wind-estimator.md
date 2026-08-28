# Реалізація оцінювача вітру та компенсації зносу

Для утримання заданої лінії шляху автопілот літака повинен у реальному часі знати поточний вектор швидкості вітру та транслювати бажаний шляховий кут у курс орієнтації носа. Нижче наведено повнофункціональну бібліотеку розрахунку навігаційного трикутника швидкостей та рекурсивного розширеного фільтра Калмана (EKF) для оцінювання 2D-вектора вітру за даними трубки Піто, GNSS та IMU мовами C та C++.

## Математична структура оцінювача та рівняння стану

Оцінювач вітру побудований за принципом рекурсивної фільтрації Калмана з нелінійним вектором вимірювання (Extended Kalman Filter). Задача фільтра полягає у розділенні вектору швидкості польоту над землею на вектор руху літака в повітрі та вектор знесення самої повітряної маси.

### 1. Модель стану та динаміка процесу

Вектор стану системи об'єднує три оцінювані величини:

```
x = [ W_N,  W_E,  k_scale ]ᵀ
```

- `W_N` — північна складова швидкості вітру (м/с) у навігаційній системі NED;
- `W_E` — східна складова швидкості вітру (м/с);
- `k_scale` — масштабний коефіцієнт калібрування датчика повітряної швидкості (трубки Піто). Номінальне значення дорівнює `1.0`, проте через похибки встановлення приймача динамічного тиску або локальні спотворення потоку на фюзеляжі реальне значення може дрейфувати в межах від `0.7` до `1.3`.

Швидкість вітру в атмосфері моделюється як неперервне випадкове блукання (Random Walk). Це означає, що похідна стану за часом є білим гаусовим шумом `w_w` з нульовим математичним сподіванням:

```
Ẇ_N = 0 + w_w
Ẇ_E = 0 + w_w
k̇_scale = 0 + w_scale
```

На кроці часової екстраполяції (прогнозу) стан залишається незмінним `x(t + dt) = x(t)`, а елементи діагоналі коваріаційної матриці помилок `P` збільшуються пропорційно часу дискретизації `dt` та спектральній густині процесного шуму `Q_wind`:

```
P_00(t + dt) = P_00(t) + Q_wind · dt
P_11(t + dt) = P_11(t) + Q_wind · dt
P_22(t + dt) = P_22(t) + Q_scale · dt
```

### 2. Нелінійне вимірювання та лінеаризація (Якобіан H)

Датчик перепаду тиску вимірює скалярну величину дійсної повітряної швидкості `V_a_meas`. Водночас супутниковий приймач GNSS видає вектор швидкості по землі `V_g = [V_g_N, V_g_E]ᵀ`.

Зв'язок між вектором швидкості по землі та вітром визначається різницею:

```
v_a_vec = V_g − W = [ V_g_N − W_N,  V_g_E − W_E ]ᵀ
```

Очікуваний модуль повітряної швидкості `pred_tas` виражається через евклідову норму цього вектора:

```
pred_tas = ||V_g − W|| = √( (V_g_N − W_N)² + (V_g_E − W_E)² )
```

З іншого боку, з урахуванням оціненого коефіцієнта масштабу датчика виміряна швидкість дорівнює `tas_scaled = k_scale · V_a_meas`.

Інновація (нев'язка вимірювання) `y` дорівнює різниці між масштабованим вимірюванням та очікуваною швидкістю:

```
y = tas_scaled − pred_tas
```

Для оновлення стану фільтра Калмана обчислюється вектор градієнта функції спостереження — матриця Якобі `H = ∂y / ∂x`:

```
H_0 = ∂y / ∂W_N = −(V_g_N − W_N) / pred_tas     [похідна за північною складовою вітру]
H_1 = ∂y / ∂W_E = −(V_g_E − W_E) / pred_tas     [похідна за східною складовою вітру]
H_2 = ∂y / ∂k_scale = V_a_meas                  [похідна за коефіцієнтом масштабу]
```

### 3. Рекурсивне оновлення Калмана

За матрицею `H` обчислюються проміжні вектори:

1. **Вектор інноваційної коваріації:** `PHᵀ = P · Hᵀ` (вектор розмірності `3×1`).
2. **Скалярна коваріація інновації:** `S = H · P · Hᵀ + R_tas` (де `R_tas` — дисперсія шуму датчика тиску).
3. **Коефіцієнт підсилення Калмана:** `K = PHᵀ / S` (вектор вагових коефіцієнтів розмірності `3×1`).
4. **Корекція вектора стану:** `x_new = x_old + K · y`.
5. **Оновлення коваріаційної матриці помилок:** `P_new = (I − K · H) · P_old`.

## Геометрія розрахунку кута крабування

Контур навігації формує заданий шляховий кут руху по землі `χ_cmd`. Оцінений вектор вітру `W = [W_N, W_E]ᵀ` розкладається на дві взаємно перпендикулярні осі:

- **Бокова складова вітру (Crosswind component):** перпендикулярна до лінії шляху, зі знаком плюс при вітрі з правого борту:
```
W_cross = W_N · sin(χ_cmd) − W_E · cos(χ_cmd)
```
- **Поздовжня складова вітру (Along-track component):** паралельна до лінії шляху, зі знаком плюс для попутного вітру:
```
W_along = W_N · cos(χ_cmd) + W_E · sin(χ_cmd)
```

Кут крабування обчислюється через арксинус відношення бокового вітру до дійсної повітряної швидкості `V_a`:

```
sin(α_c) = W_cross / V_a
α_c = arcsin( W_cross / V_a )
ψ_cmd = χ_cmd − α_c
```

Якщо `|W_cross| ≥ V_a`, виникає аеродинамічне насичення: боковий вітер перевищує максимальну швидкість літака. У цьому випадку алгоритм обмежує кут крабування значенням `±90°` та встановлює прапорець `is_solvable = false`, сигналізуючи контуру автопілота про неможливість утримання коридору.

## Повний вихідний код оцінювача

:::tabs
```c
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define PI_F 3.14159265358979323846f
#define TWO_PI_F (2.0f * PI_F)

/* Нормалізація кута в діапазон [-pi, +pi] */
static float wrap_pi(float angle) {
    while (angle > PI_F) {
        angle -= TWO_PI_F;
    }
    while (angle < -PI_F) {
        angle += TWO_PI_F;
    }
    return angle;
}

/* Обмеження величини в діапазон [min, max] */
static float constrain_f(float val, float min_val, float max_val) {
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

/* Структура стану фільтра вітру EKF */
typedef struct {
    float state[3];      /* [0]: W_N (м/с), [1]: W_E (м/с), [2]: k_scale (коеф. піто) */
    float P[3][3];       /* Коваріаційна матриця оцінки */
    float Q_wind;        /* Дисперсія процесу для вітру (м/с)^2 / с */
    float Q_scale;       /* Дисперсія процесу для коефіцієнта трубки Піто */
    float R_tas;         /* Дисперсія вимірювання повітряної швидкості (м/с)^2 */
    bool  initialized;
} WindEkf;

/* Структура розв'язку навігаційного трикутника */
typedef struct {
    float heading_cmd_rad;    /* Заданий курс орієнтації носа psi (рад) */
    float crab_angle_rad;     /* Кут крабування alpha_c (рад) */
    float ground_speed_exp;   /* Очікувана шляхова швидкість V_g (м/с) */
    bool  is_solvable;        /* Чи вистачає швидкості подолати вітер */
} CrabAngleSolution;

/* Ініціалізація EKF оцінювача вітру */
void wind_ekf_init(WindEkf *ekf) {
    ekf->state[0] = 0.0f; /* Початковий вітер Північ = 0 */
    ekf->state[1] = 0.0f; /* Початковий вітер Схід = 0 */
    ekf->state[2] = 1.0f; /* Номінальний масштаб трубки Піто = 1.0 */

    memset(ekf->P, 0, sizeof(ekf->P));
    ekf->P[0][0] = 25.0f;   /* Початкова дисперсія W_N: (5 м/с)^2 */
    ekf->P[1][1] = 25.0f;   /* Початкова дисперсія W_E: (5 м/с)^2 */
    ekf->P[2][2] = 0.04f;   /* Початкова дисперсія k_scale: (0.2)^2 */

    ekf->Q_wind  = 0.1f;    /* Шум випадкового блукання вітру */
    ekf->Q_scale = 0.00001f;/* Повільний дрейф масштабу датчика */
    ekf->R_tas   = 1.5f;    /* Шум вимірювання датчика тиску */
    ekf->initialized = true;
}

/* Крок прогнозу фільтра Калмана (часова екстраполяція) */
void wind_ekf_predict(WindEkf *ekf, float dt) {
    if (!ekf->initialized || dt <= 0.0f) return;

    /* Стан не змінюється (W_dot = 0, k_scale_dot = 0) */
    /* Зростання коваріації за рахунок процесного шуму */
    ekf->P[0][0] += ekf->Q_wind * dt;
    ekf->P[1][1] += ekf->Q_wind * dt;
    ekf->P[2][2] += ekf->Q_scale * dt;
}

/* Крок корекції за даними трубки Піто, GNSS швидкості та орієнтації */
bool wind_ekf_fuse_airspeed(WindEkf *ekf,
                            float tas_measured,
                            float vg_n,
                            float vg_e,
                            float heading_rad,
                            float pitch_rad) {
    if (!ekf->initialized || tas_measured <= 1.0f) return false;

    float cos_hdg = cosf(heading_rad);
    float sin_hdg = sinf(heading_rad);
    float cos_pit = cosf(pitch_rad);

    /* Проєкція повітряної швидкості в горизонтальну площину NED */
    float dir_n = cos_hdg * cos_pit;
    float dir_e = sin_hdg * cos_pit;

    float k_scale = ekf->state[2];
    float tas_scaled = k_scale * tas_measured;

    /* Очікувана швидкість по землі: v_g_pred = v_a + W */
    float pred_vg_n = dir_n * tas_scaled + ekf->state[0];
    float pred_vg_e = dir_e * tas_scaled + ekf->state[1];

    /* Очікуваний модуль повітряної швидкості за різницею швидкостей: */
    /* v_a_vec = V_g - W */
    float diff_n = vg_n - ekf->state[0];
    float diff_e = vg_e - ekf->state[1];
    float pred_tas = sqrtf(diff_n * diff_n + diff_e * diff_e);

    if (pred_tas < 0.1f) return false;

    /* Інновація (нев'язка вимірювання): y = tas_scaled - pred_tas */
    float innov = tas_scaled - pred_tas;

    /* Матриця спостереження H (Якобіан відносно [W_N, W_E, k_scale]): */
    float H[3];
    H[0] = -diff_n / pred_tas;
    H[1] = -diff_e / pred_tas;
    H[2] = tas_measured;

    /* P * H^T */
    float PHt[3];
    PHt[0] = ekf->P[0][0] * H[0] + ekf->P[0][1] * H[1] + ekf->P[0][2] * H[2];
    PHt[1] = ekf->P[1][0] * H[0] + ekf->P[1][1] * H[1] + ekf->P[1][2] * H[2];
    PHt[2] = ekf->P[2][0] * H[0] + ekf->P[2][1] * H[1] + ekf->P[2][2] * H[2];

    /* Інноваційна коваріація: S = H * P * H^T + R */
    float S = H[0] * PHt[0] + H[1] * PHt[1] + H[2] * PHt[2] + ekf->R_tas;
    if (S <= 0.0001f) return false;

    /* Коефіцієнт підсилення Калмана: K = PHt / S */
    float K[3];
    K[0] = PHt[0] / S;
    K[1] = PHt[1] / S;
    K[2] = PHt[2] / S;

    /* Оновлення стану: x = x + K * innov */
    ekf->state[0] += K[0] * innov;
    ekf->state[1] += K[1] * innov;
    ekf->state[2] += K[2] * innov;

    /* Обмеження масштабу трубки Піто у розумних межах [0.7, 1.3] */
    ekf->state[2] = constrain_f(ekf->state[2], 0.7f, 1.3f);

    /* Оновлення коваріаційної матриці: P = (I - K*H) * P */
    float I_KH[3][3];
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            float kh = K[i] * H[j];
            I_KH[i][j] = (i == j ? 1.0f : 0.0f) - kh;
        }
    }

    float P_new[3][3];
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            P_new[i][j] = 0.0f;
            for (int k = 0; k < 3; k++) {
                P_new[i][j] += I_KH[i][k] * ekf->P[k][j];
            }
        }
    }
    memcpy(ekf->P, P_new, sizeof(ekf->P));
    return true;
}

/* Отримання поточної оцінки вітру */
void wind_ekf_get_wind(const WindEkf *ekf, float *wind_n, float *wind_e, float *wind_speed, float *wind_dir_rad) {
    *wind_n = ekf->state[0];
    *wind_e = ekf->state[1];
    *wind_speed = sqrtf((*wind_n) * (*wind_n) + (*wind_e) * (*wind_e));
    *wind_dir_rad = wrap_pi(atan2f(*wind_e, *wind_n));
}

/* Розрахунок навігаційного кута крабування та уставки курсу */
CrabAngleSolution solve_crab_angle(float track_cmd_rad,
                                  float tas,
                                  float wind_n,
                                  float wind_e) {
    CrabAngleSolution sol;
    memset(&sol, 0, sizeof(sol));

    if (tas < 1.0f) {
        sol.heading_cmd_rad = track_cmd_rad;
        sol.is_solvable = false;
        return sol;
    }

    /* Проєкція вітру на нормаль до лінії шляху: W_cross (з правого борту > 0) */
    float w_cross = wind_n * sinf(track_cmd_rad) - wind_e * cosf(track_cmd_rad);
    /* Проєкція вітру вздовж лінії шляху: W_along (попутний > 0, зустрічний < 0) */
    float w_along = wind_n * cosf(track_cmd_rad) + wind_e * sinf(track_cmd_rad);

    float sin_crab_arg = w_cross / tas;

    if (fabsf(sin_crab_arg) >= 1.0f) {
        /* Критичний вітер: боковий вітер перевищує повітряну швидкість */
        sol.is_solvable = false;
        sol.crab_angle_rad = (sin_crab_arg > 0.0f) ? (PI_F * 0.5f) : (-PI_F * 0.5f);
        sol.heading_cmd_rad = wrap_pi(track_cmd_rad - sol.crab_angle_rad);
        sol.ground_speed_exp = 0.0f;
        return sol;
    }

    /* Стандартний розрахунок кута крабування */
    sol.crab_angle_rad = asinf(sin_crab_arg);
    sol.heading_cmd_rad = wrap_pi(track_cmd_rad - sol.crab_angle_rad);
    sol.ground_speed_exp = tas * cosf(sol.crab_angle_rad) + w_along;
    sol.is_solvable = (sol.ground_speed_exp > 0.0f);

    return sol;
}
```
```cpp
#include <array>
#include <cmath>
#include <numbers>
#include <optional>

namespace autopilot::navigation {

constexpr float PI = std::numbers::pi_v<float>;
constexpr float TWO_PI = 2.0f * PI;

/* Нормалізація кута в діапазон [-pi, +pi] */
[[nodiscard]] constexpr float wrap_pi(float angle) noexcept {
    while (angle > PI) angle -= TWO_PI;
    while (angle < -PI) angle += TWO_PI;
    return angle;
}

struct WindVector2D {
    float north{0.0f};  // м/с
    float east{0.0f};   // м/с

    [[nodiscard]] float speed() const noexcept {
        return std::hypot(north, east);
    }

    [[nodiscard]] float direction_rad() const noexcept {
        return wrap_pi(std::atan2(east, north));
    }
};

struct CrabSolution {
    float heading_cmd_rad{0.0f};   // Уставка курсу psi
    float crab_angle_rad{0.0f};    // Кут крабування alpha_c
    float ground_speed_exp{0.0f};  // Очікувана шляхова швидкість V_g
    bool  is_solvable{true};       // Чи подолано бічний знос
};

class WindEstimatorEKF {
public:
    WindEstimatorEKF() noexcept {
        reset();
    }

    void reset() noexcept {
        state_ = {0.0f, 0.0f, 1.0f}; // W_N=0, W_E=0, k_scale=1.0
        P_ = {};
        P_[0][0] = 25.0f;   // Дисперсія W_N (5 м/с)^2
        P_[1][1] = 25.0f;   // Дисперсія W_E (5 м/с)^2
        P_[2][2] = 0.04f;   // Дисперсія k_scale (0.2)^2
    }

    // Прогноз стану (часова екстраполяція)
    void predict(float dt) noexcept {
        if (dt <= 0.0f) return;
        P_[0][0] += Q_wind_ * dt;
        P_[1][1] += Q_wind_ * dt;
        P_[2][2] += Q_scale_ * dt;
    }

    // Комплексування вимірювання повітряної швидкості
    bool fuse_airspeed(float tas_measured,
                       float vg_north,
                       float vg_east,
                       float heading_rad,
                       float pitch_rad) noexcept {
        if (tas_measured <= 1.0f) return false;

        const float k_scale = state_[2];
        const float tas_scaled = k_scale * tas_measured;

        // Вектор повітряної швидкості за різницею: v_a = V_g - W
        const float diff_n = vg_north - state_[0];
        const float diff_e = vg_east - state_[1];
        const float pred_tas = std::hypot(diff_n, diff_e);

        if (pred_tas < 0.1f) return false;

        // Інновація (нев'язка вимірювання)
        const float innov = tas_scaled - pred_tas;

        // Градієнт функції спостереження (Якобіан H)
        const std::array<float, 3> H = {
            -diff_n / pred_tas,
            -diff_e / pred_tas,
            tas_measured
        };

        // Обчислення P * H^T
        std::array<float, 3> PHt{};
        for (std::size_t i = 0; i < 3; ++i) {
            PHt[i] = P_[i][0] * H[0] + P_[i][1] * H[1] + P_[i][2] * H[2];
        }

        // Інноваційна коваріація S = H * P * H^T + R
        const float S = H[0] * PHt[0] + H[1] * PHt[1] + H[2] * PHt[2] + R_tas_;
        if (S <= 0.0001f) return false;

        // Коефіцієнт Калмана K = PHt / S
        std::array<float, 3> K{};
        for (std::size_t i = 0; i < 3; ++i) {
            K[i] = PHt[i] / S;
            state_[i] += K[i] * innov;
        }

        // Обмеження калібрувального коефіцієнта трубки Піто
        state_[2] = std::clamp(state_[2], 0.7f, 1.3f);

        // Оновлення коваріації Joseph-подібним виразом: P = (I - K*H) * P
        std::array<std::array<float, 3>, 3> I_KH{};
        for (std::size_t i = 0; i < 3; ++i) {
            for (std::size_t j = 0; j < 3; ++j) {
                const float delta = (i == j) ? 1.0f : 0.0f;
                I_KH[i][j] = delta - K[i] * H[j];
            }
        }

        std::array<std::array<float, 3>, 3> P_next{};
        for (std::size_t i = 0; i < 3; ++i) {
            for (std::size_t j = 0; j < 3; ++j) {
                float sum = 0.0f;
                for (std::size_t k = 0; k < 3; ++k) {
                    sum += I_KH[i][k] * P_[k][j];
                }
                P_next[i][j] = sum;
            }
        }
        P_ = P_next;
        return true;
    }

    [[nodiscard]] WindVector2D wind() const noexcept {
        return WindVector2D{state_[0], state_[1]};
    }

    [[nodiscard]] float airspeed_scale() const noexcept {
        return state_[2];
    }

private:
    std::array<float, 3> state_{0.0f, 0.0f, 1.0f}; // [W_N, W_E, k_scale]
    std::array<std::array<float, 3>, 3> P_{};      // Коваріація
    float Q_wind_{0.1f};                            // Процесний шум вітру
    float Q_scale_{1e-5f};                          // Дрейф масштабу
    float R_tas_{1.5f};                             // Шум датчика швидкості
};

// Аналітичний розрахунок уставки курсу та кута крабування
[[nodiscard]] CrabSolution calculate_crab_solution(float track_cmd_rad,
                                                   float tas,
                                                   const WindVector2D& wind) noexcept {
    CrabSolution solution{};

    if (tas < 1.0f) {
        solution.heading_cmd_rad = track_cmd_rad;
        solution.is_solvable = false;
        return solution;
    }

    // Бокова та поздовжня складові вітру відносно лінії шляху
    const float w_cross = wind.north * std::sin(track_cmd_rad) - wind.east * std::cos(track_cmd_rad);
    const float w_along = wind.north * std::cos(track_cmd_rad) + wind.east * std::sin(track_cmd_rad);

    const float sin_crab = w_cross / tas;

    if (std::abs(sin_crab) >= 1.0f) {
        // Зрив наведення: боковий вітер перевищує повітряну швидкість
        solution.is_solvable = false;
        solution.crab_angle_rad = (sin_crab > 0.0f) ? (PI * 0.5f) : (-PI * 0.5f);
        solution.heading_cmd_rad = wrap_pi(track_cmd_rad - solution.crab_angle_rad);
        solution.ground_speed_exp = 0.0f;
        return solution;
    }

    solution.crab_angle_rad = std::asin(sin_crab);
    solution.heading_cmd_rad = wrap_pi(track_cmd_rad - solution.crab_angle_rad);
    solution.ground_speed_exp = tas * std::cos(solution.crab_angle_rad) + w_along;
    solution.is_solvable = (solution.ground_speed_exp > 0.0f);

    return solution;
}

} // namespace autopilot::navigation
```
:::

## Інтеграція в цикл керування польотом та телеметрична валідація

У головному циклі навігаційного контролера (типова частота 50 Гц) виклики розподіляються наступним чином:

1. **Етап прогнозу (50 Гц):** функція `predict(dt)` викликається щоітерації для моделювання поступового зростання невизначеності вітру через атмосферну турбулентність.
2. **Етап оновлення за сенсорами (10–20 Гц):** при надходженні нового вимірювання від супутникового приймача GNSS та датчика перепаду тиску трубки Піто викликається `fuse_airspeed()`. Фільтр адаптивно підлаштовує як вектор швидкості вітру, так і калібрувальний масштаб датчика швидкості.
3. **Етап наведення (50 Гц):** алгоритм ведення за маршрутом обчислює бажаний напрямок переміщення по землі `track_cmd_rad`, після чого функція `calculate_crab_solution()` генерує скориговану на вітер уставку орієнтації носа `heading_cmd_rad` для контуру кутової стабілізації.

### Аналіз логів польоту та діагностика розбіжності

У польотних логах (формат ULog у PX4 або DataFlash `.bin` в ArduPilot) оцінка вітру записується в топіки `estimator_wind` або `EKF3.WN/WE`. При аналізі логів звертають увагу на три критичні діагностичні ознаки:

- **Стрибки інновації `innov`:** якщо нев'язка вимірювання повітряної швидкості перевищує `3–5 м/с` під час прямолінійного польоту, це свідчить про неправильне встановлення шуму `R_tas` або механічне засмічення трубки Піто.
- **Дрейф коефіцієнта `k_scale` до меж діапазону (0.7 або 1.3):** якщо масштабний коефіцієнт вперся в обмежувач, на літаку присутня суттєва аеродинамічна похибка статичного тиску (наприклад, статичні отвори потрапляють у зону підвищеного тиску від гвинта або носового обтічника).
- **Фазова затримка відновлення вітру при зміні курсу на 180°:** якщо після розвороту літака оцінений вітер різко змінює свій напрямок, на борту присутня похибка орієнтації компаса. У правильно відкаліброваній системі вектор вітру в системі NED залишається незмінним під час будь-яких маневрів літака.
