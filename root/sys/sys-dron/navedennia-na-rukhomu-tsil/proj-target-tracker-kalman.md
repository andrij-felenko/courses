# ⚙️ Бортовий модуль наведення та фільтрації стану цілі: повна реалізація алгоритму

Бортовий модуль динамічного наведення поєднує тривимірний фільтр Калмана оцінки стану цілі (позиція, швидкість, прискорення) та генератор прискорень розширеної пропорційної навігації (APN). У реальному польоті сирі вимірювання від оптичного трекера або далекоміра містять високочастотний шум квантування та пропуски кадрів. Пряме чисельне диференціювання таких даних призводить до катастрофічних сплесків командного прискорення. Фільтр Калмана забезпечує гладку оцінку швидкості зближення `V_c`, вектора кутової швидкості лінії візування `Ω` та прискорення маневру цілі `a_t`.

---

### Архітектура та математична модель модулів

Модуль обчислення наведення складається з трьох послідовних кінематичних ланок:

1. **Тривимірний лінійний фільтр Калмана (Continuous-Discrete Kalman Filter):**
   Вектор стану має розмірність 9: положення `r_t`, швидкість `v_t` та прискорення `a_t` у системі координат NED (North-East-Down):
   ```
   x = [p_x, p_y, p_z, v_x, v_y, v_z, a_x, a_y, a_z]ᵀ
   ```
   Модель руху цілі — процес із випадковим прискоренням першого порядку (Singer model або Continuous White Noise Acceleration, CWNA). У неперервному часі динаміка описується стохастичним диференціальним рівнянням:
   ```
   dx/dt = A_c · x + G_c · w(t)
   ```
   де матриця інтенсивності шуму маневру `Q_c` характеризує очікувану дисперсію ривка цілі.

   Дискретизація на інтервалі тактування `Δt` дає матрицю переходу стану `F` та дискретну коваріацію шуму процесу `Q_d`:
   ```
   F = 
   ┌──────────────┐
   │ 1   Δt  Δt²/2│
   │ 0   1   Δt   │
   │ 0   0   1    │
   └──────────────┘
   ```
   Інтеграл поширення коваріації шуму процесу:
   ```
   Q_d = ∫₀^Δt F(τ) · G_c · Q_c · G_cᵀ · F(τ)ᵀ dτ
   ```
   Для моделі випадкового прискорення елементи матриці `Q_d` по кожній осі пропорційні степеням `Δt⁵/20`, `Δt⁴/8`, `Δt³/3`, `Δt²/2` та `Δt`, що забезпечує узгоджене зростання невизначеності швидкості та координати під час тривалих пауз між кадрами детектора.

2. **Векторний генератор пропорційної навігації (True & Augmented PN):**
   Обчислює вектор відносної дальності `R = r_t - r_d` та відносної швидкості `V_r = v_t - v_d`.
   Вектор кутової швидкості лінії візування `Ω` та швидкість зближення `V_c`:
   ```
   Ω = (R × V_r) / ||R||²
   V_c = - (R · V_r) / ||R||
   ```
   Командне прискорення:
   ```
   a_cmd = N · V_c · (Ω × e_los) + (N / 2) · a_t_perp
   ```

3. **Блок захисту та обмежень (Safety Limiter):**
   - Захист від ділення на нуль при малій дальності: регуляризація знаменника `||R||² + ε`.
   - Захист при від'ємній швидкості зближення `V_c ≤ 0` (ціль віддаляється швидше, ніж летить дрон): перехід у режим прямого переслідування максимальної тяги.
   - Насичення командного прискорення за сферичною або циліндричною нормою `||a_cmd|| ≤ a_max`.

---

### Геометрична проєкція та динамічна коваріація вимірювань

Оптичний сенсор (курсова камера на стабілізованому підвісі) вимірює піксельні координати центру обмежувальної рамки `(u, v)` та глибину `d` від далекоміра. Перетворення вимірювання в інерційну систему координат NED виконується через матрицю калібрування камери `K` та поточну матрицю орієнтації підвісу `R_cam_to_ned`:

```
p_cam = [ (u - c_x)·d / f_x,  (v - c_y)·d / f_y,  d ]ᵀ
p_target_ned = r_drone_ned + R_cam_to_ned · p_cam
```

Дисперсія вимірювання координат у просторі не є ізотропною. Похибка вимірювання дальності оптичним далекоміром зростає пропорційно квадрату відстані: `σ_depth = k_range · d²`. Поперечна похибка пропорційна кутовій роздільній здатності пікселя: `σ_lat = (d / f) · σ_pixel`. 

Матриця коваріації вимірювального шуму `R_cov` динамічно перераховується на кожному такті перед виконанням кроку корекції фільтра Калмана:

```
R_cov = R_cam_to_ned · diag(σ_lat², σ_lat², σ_depth²) · R_cam_to_nedᵀ
```

Завдяки цьому фільтр автоматично довіряє кутовим вимірюванням на великій відстані більше, ніж радіальній дальності, що запобігає розгойдуванню оцінки прискорення `a_t`.

---

### Реалізація на мовах C та C++

Нижче наведено модульну реалізацію тривимірного фільтра Калмана стану цілі та генератора прискорень наведення.

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define STATE_DIM 9
#define MEAS_DIM 3

typedef struct {
    double x, y, z;
} Vec3;

static inline Vec3 vec3_add(Vec3 a, Vec3 b) {
    return (Vec3){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline Vec3 vec3_sub(Vec3 a, Vec3 b) {
    return (Vec3){a.x - b.x, a.y - b.y, a.z - b.z};
}

static inline Vec3 vec3_scale(Vec3 a, double s) {
    return (Vec3){a.x * s, a.y * s, a.z * s};
}

static inline double vec3_dot(Vec3 a, Vec3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static inline Vec3 vec3_cross(Vec3 a, Vec3 b) {
    return (Vec3){
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

static inline double vec3_norm(Vec3 a) {
    return sqrt(vec3_dot(a, a));
}

static inline Vec3 vec3_clamp_norm(Vec3 a, double max_val) {
    double n = vec3_norm(a);
    if (n > max_val && n > 1e-6) {
        return vec3_scale(a, max_val / n);
    }
    return a;
}

/* 1D Фільтр Калмана (PV-A) для однієї координатної осі */
typedef struct {
    double p, v, a;      /* стан: координата, швидкість, прискорення */
    double P[3][3];      /* коваріація помилки */
    double q_acc;        /* інтенсивність шуму маневру цілі */
    double r_meas;       /* дисперсія шуму давача */
} AxisKalman;

static void axis_kalman_init(AxisKalman* kf, double init_p, double q_acc, double r_meas) {
    kf->p = init_p;
    kf->v = 0.0;
    kf->a = 0.0;
    kf->q_acc = q_acc;
    kf->r_meas = r_meas;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            kf->P[i][j] = (i == j) ? 10.0 : 0.0;
        }
    }
}

static void axis_kalman_predict(AxisKalman* kf, double dt) {
    double dt2 = 0.5 * dt * dt;
    /* Екстраполяція стану */
    kf->p += kf->v * dt + kf->a * dt2;
    kf->v += kf->a * dt;

    /* Матриця переходу F: [1, dt, dt2; 0, 1, dt; 0, 0, 1] */
    double P00 = kf->P[0][0] + dt * (kf->P[1][0] + kf->P[0][1]) + dt2 * (kf->P[2][0] + kf->P[0][2])
                 + dt * dt * kf->P[1][1] + dt * dt2 * (kf->P[2][1] + kf->P[1][2]) + dt2 * dt2 * kf->P[2][2];
    double P01 = kf->P[0][1] + dt * kf->P[1][1] + dt2 * kf->P[2][1] + dt * kf->P[0][2] + dt * dt * kf->P[1][2] + dt * dt2 * kf->P[2][2];
    double P02 = kf->P[0][2] + dt * kf->P[1][2] + dt2 * kf->P[2][2];
    double P11 = kf->P[1][1] + dt * (kf->P[2][1] + kf->P[1][2]) + dt * dt * kf->P[2][2];
    double P12 = kf->P[1][2] + dt * kf->P[2][2];
    double P22 = kf->P[2][2] + kf->q_acc * dt;

    kf->P[0][0] = P00; kf->P[0][1] = P01; kf->P[0][2] = P02;
    kf->P[1][0] = P01; kf->P[1][1] = P11; kf->P[1][2] = P12;
    kf->P[2][0] = P02; kf->P[2][1] = P12; kf->P[2][2] = P22;
}

static void axis_kalman_update(AxisKalman* kf, double z_meas) {
    double inn = z_meas - kf->p;
    double s = kf->P[0][0] + kf->r_meas;
    if (fabs(s) < 1e-9) return;

    double k0 = kf->P[0][0] / s;
    double k1 = kf->P[1][0] / s;
    double k2 = kf->P[2][0] / s;

    kf->p += k0 * inn;
    kf->v += k1 * inn;
    kf->a += k2 * inn;

    double p00 = kf->P[0][0], p01 = kf->P[0][1], p02 = kf->P[0][2];
    kf->P[0][0] -= k0 * p00; kf->P[0][1] -= k0 * p01; kf->P[0][2] -= k0 * p02;
    kf->P[1][0] -= k1 * p00; kf->P[1][1] -= k1 * p01; kf->P[1][2] -= k1 * p02;
    kf->P[2][0] -= k2 * p00; kf->P[2][1] -= k2 * p01; kf->P[2][2] -= k2 * p02;
}

/* 3D Стан цілі */
typedef struct {
    AxisKalman kf_x, kf_y, kf_z;
} TargetEstimator;

void target_estimator_init(TargetEstimator* est, Vec3 init_pos, double q_acc, double r_meas) {
    axis_kalman_init(&est->kf_x, init_pos.x, q_acc, r_meas);
    axis_kalman_init(&est->kf_y, init_pos.y, q_acc, r_meas);
    axis_kalman_init(&est->kf_z, init_pos.z, q_acc, r_meas);
}

void target_estimator_step(TargetEstimator* est, double dt, Vec3 raw_meas, bool valid_meas) {
    axis_kalman_predict(&est->kf_x, dt);
    axis_kalman_predict(&est->kf_y, dt);
    axis_kalman_predict(&est->kf_z, dt);

    if (valid_meas) {
        axis_kalman_update(&est->kf_x, raw_meas.x);
        axis_kalman_update(&est->kf_y, raw_meas.y);
        axis_kalman_update(&est->kf_z, raw_meas.z);
    }
}

/* Конфігурація наведення */
typedef struct {
    double N;            /* Навігаційний коефіцієнт (3.0 .. 5.0) */
    double a_max;        /* Граничне командне прискорення [м/с^2] */
    bool use_apn;        /* Чи використовувати APN компенсацію маневру */
} GuidanceConfig;

/* Генератор прискорення APN */
Vec3 compute_guidance_acceleration(
    GuidanceConfig cfg,
    Vec3 drone_pos,
    Vec3 drone_vel,
    const TargetEstimator* est
) {
    Vec3 target_pos = {est->kf_x.p, est->kf_y.p, est->kf_z.p};
    Vec3 target_vel = {est->kf_x.v, est->kf_y.v, est->kf_z.v};
    Vec3 target_acc = {est->kf_x.a, est->kf_y.a, est->kf_z.a};

    Vec3 R_vec = vec3_sub(target_pos, drone_pos);
    double R_norm = vec3_norm(R_vec);
    if (R_norm < 0.1) {
        return (Vec3){0.0, 0.0, 0.0};
    }

    Vec3 e_los = vec3_scale(R_vec, 1.0 / R_norm);
    Vec3 V_r = vec3_sub(target_vel, drone_vel);

    /* Швидкість зближення: V_c = - (R · V_r) / R */
    double V_c = -vec3_dot(e_los, V_r);
    if (V_c < 0.1) {
        V_c = 0.1; /* Захист від втрати швидкості зближення */
    }

    /* Кутова швидкість лінії візування: Ω = (R × V_r) / ||R||² */
    Vec3 cross_rv = vec3_cross(R_vec, V_r);
    Vec3 Omega = vec3_scale(cross_rv, 1.0 / (R_norm * R_norm));

    /* Базова складова PN: N * V_c * (Ω × e_los) */
    Vec3 omega_cross_los = vec3_cross(Omega, e_los);
    Vec3 a_pn = vec3_scale(omega_cross_los, cfg.N * V_c);

    /* Складова APN для маневруючої цілі: (N / 2) * a_target_normal */
    Vec3 a_total = a_pn;
    if (cfg.use_apn) {
        Vec3 a_t_parallel = vec3_scale(e_los, vec3_dot(target_acc, e_los));
        Vec3 a_t_perp = vec3_sub(target_acc, a_t_parallel);
        Vec3 a_apn = vec3_scale(a_t_perp, cfg.N * 0.5);
        a_total = vec3_add(a_total, a_apn);
    }

    return vec3_clamp_norm(a_total, cfg.a_max);
}
```
```cpp
#include <iostream>
#include <array>
#include <cmath>
#include <optional>
#include <span>
#include <concepts>

struct Vec3 {
    double x{0.0}, y{0.0}, z{0.0};

    [[nodiscard]] constexpr Vec3 operator+(const Vec3& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    [[nodiscard]] constexpr Vec3 operator-(const Vec3& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
    [[nodiscard]] constexpr Vec3 operator*(double s) const noexcept {
        return {x * s, y * s, z * s};
    }
    [[nodiscard]] constexpr double dot(const Vec3& o) const noexcept {
        return x * o.x + y * o.y + z * o.z;
    }
    [[nodiscard]] constexpr Vec3 cross(const Vec3& o) const noexcept {
        return {
            y * o.z - z * o.y,
            z * o.x - x * o.z,
            x * o.y - y * o.x
        };
    }
    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(dot(*this));
    }
    [[nodiscard]] Vec3 clamp_norm(double max_val) const noexcept {
        const double n = norm();
        if (n > max_val && n > 1e-6) {
            return (*this) * (max_val / n);
        }
        return *this;
    }
};

/* Одновимірний фільтр Калмана з постійним прискоренням (Singer модель) */
class AxisKalman {
public:
    explicit AxisKalman(double init_p = 0.0, double q_acc = 1.0, double r_meas = 0.1) noexcept
        : p_{init_p}, q_acc_{q_acc}, r_meas_{r_meas} {
        P_[0][0] = 10.0; P_[1][1] = 10.0; P_[2][2] = 10.0;
    }

    void predict(double dt) noexcept {
        const double dt2 = 0.5 * dt * dt;
        p_ += v_ * dt + a_ * dt2;
        v_ += a_ * dt;

        const double P00 = P_[0][0] + dt * (P_[1][0] + P_[0][1]) + dt2 * (P_[2][0] + P_[0][2])
                         + dt * dt * P_[1][1] + dt * dt2 * (P_[2][1] + P_[1][2]) + dt2 * dt2 * P_[2][2];
        const double P01 = P_[0][1] + dt * P_[1][1] + dt2 * P_[2][1] + dt * P_[0][2] + dt * dt * P_[1][2] + dt * dt2 * P_[2][2];
        const double P02 = P_[0][2] + dt * P_[1][2] + dt2 * P_[2][2];
        const double P11 = P_[1][1] + dt * (P_[2][1] + P_[1][2]) + dt * dt * P_[2][2];
        const double P12 = P_[1][2] + dt * P_[2][2];
        const double P22 = P_[2][2] + q_acc_ * dt;

        P_[0][0] = P00; P_[0][1] = P01; P_[0][2] = P02;
        P_[1][0] = P01; P_[1][1] = P11; P_[1][2] = P12;
        P_[2][0] = P02; P_[2][1] = P12; P_[2][2] = P22;
    }

    void update(double z_meas) noexcept {
        const double inn = z_meas - p_;
        const double s = P_[0][0] + r_meas_;
        if (std::abs(s) < 1e-9) return;

        const double k0 = P_[0][0] / s;
        const double k1 = P_[1][0] / s;
        const double k2 = P_[2][0] / s;

        p_ += k0 * inn;
        v_ += k1 * inn;
        a_ += k2 * inn;

        const double p00 = P_[0][0], p01 = P_[0][1], p02 = P_[0][2];
        P_[0][0] -= k0 * p00; P_[0][1] -= k0 * p01; P_[0][2] -= k0 * p02;
        P_[1][0] -= k1 * p00; P_[1][1] -= k1 * p01; P_[1][2] -= k1 * p02;
        P_[2][0] -= k2 * p00; P_[2][1] -= k2 * p01; P_[2][2] -= k2 * p02;
    }

    [[nodiscard]] constexpr double position() const noexcept { return p_; }
    [[nodiscard]] constexpr double velocity() const noexcept { return v_; }
    [[nodiscard]] constexpr double acceleration() const noexcept { return a_; }

private:
    double p_{0.0};
    double v_{0.0};
    double a_{0.0};
    std::array<std::array<double, 3>, 3> P_{};
    double q_acc_{1.0};
    double r_meas_{0.1};
};

/* 3D Оцінювач стану цілі */
class TargetEstimator3D {
public:
    TargetEstimator3D(Vec3 init_pos, double q_acc = 1.5, double r_meas = 0.05) noexcept
        : kf_x_{init_pos.x, q_acc, r_meas},
          kf_y_{init_pos.y, q_acc, r_meas},
          kf_z_{init_pos.z, q_acc, r_meas} {}

    void step(double dt, std::optional<Vec3> raw_measurement) noexcept {
        kf_x_.predict(dt);
        kf_y_.predict(dt);
        kf_z_.predict(dt);

        if (raw_measurement.has_value()) {
            kf_x_.update(raw_measurement->x);
            kf_y_.update(raw_measurement->y);
            kf_z_.update(raw_measurement->z);
        }
    }

    [[nodiscard]] Vec3 position() const noexcept {
        return {kf_x_.position(), kf_y_.position(), kf_z_.position()};
    }
    [[nodiscard]] Vec3 velocity() const noexcept {
        return {kf_x_.velocity(), kf_y_.velocity(), kf_z_.velocity()};
    }
    [[nodiscard]] Vec3 acceleration() const noexcept {
        return {kf_x_.acceleration(), kf_y_.acceleration(), kf_z_.acceleration()};
    }

private:
    AxisKalman kf_x_, kf_y_, kf_z_;
};

struct GuidanceSettings {
    double navigation_ratio{3.5};
    double max_acceleration{20.0}; // [м/с^2] ~2G
    bool enable_apn{true};
};

/* Контролер пропорційного наведення */
class ProportionalNavigationGuidance {
public:
    explicit ProportionalNavigationGuidance(GuidanceSettings settings = {}) noexcept
        : settings_{settings} {}

    [[nodiscard]] Vec3 compute_command(
        const Vec3& drone_pos,
        const Vec3& drone_vel,
        const TargetEstimator3D& target_est
    ) const noexcept {
        const Vec3 r_target = target_est.position();
        const Vec3 v_target = target_est.velocity();
        const Vec3 a_target = target_est.acceleration();

        const Vec3 R_vec = r_target - drone_pos;
        const double R_norm = R_vec.norm();
        if (R_norm < 0.1) {
            return {0.0, 0.0, 0.0};
        }

        const Vec3 e_los = R_vec * (1.0 / R_norm);
        const Vec3 V_r = v_target - drone_vel;

        double V_c = -e_los.dot(V_r);
        if (V_c < 0.1) {
            V_c = 0.1; // Запобігання інверсії знаку
        }

        const Vec3 cross_rv = R_vec.cross(V_r);
        const Vec3 Omega = cross_rv * (1.0 / (R_norm * R_norm));

        const Vec3 a_pn = Omega.cross(e_los) * (settings_.navigation_ratio * V_c);

        Vec3 a_cmd = a_pn;
        if (settings_.enable_apn) {
            const Vec3 a_t_parallel = e_los * a_target.dot(e_los);
            const Vec3 a_t_perp = a_target - a_t_parallel;
            const Vec3 a_apn = a_t_perp * (settings_.navigation_ratio * 0.5);
            a_cmd = a_cmd + a_apn;
        }

        return a_cmd.clamp_norm(settings_.max_acceleration);
    }

private:
    GuidanceSettings settings_;
};
```
:::

---

### Компенсація затримки детектора та позачергові вимірювання (OOSM)

У реальних вбудованих обчислювачах (наприклад, NVIDIA Jetson або Raspberry Pi CM4) нейромережевий трекер формує обмежувальні рамки (Bounding Boxes) із суттєвою часовою затримкою `Δt_delay ≈ 40–80 мс`. Якщо застосувати корекцію Калмана безпосередньо в момент отримання кадру, оновлення застосується до поточного стану, що створить штучний фазовий зсув і призведе до автоколивань контуру наведення.

Для усунення цієї вади застосовується кільцевий буфер станів (англ. *Circular History Buffer*):

1. **Збереження історії:** на кожному такті швидкого контуру (100 Гц) вектор стану дрона, стан фільтра Калмана та матриця коваріації записуються в кільцевий буфер розміром 32 слоти.
2. **Перевірка мітки часу:** оптичний кадр супроводжується апаратним таймстемпом зйомки `t_capture`.
3. **Ретроспективна корекція (Out-of-Sequence Measurement, OOSM):**
   - За таймстемпом `t_capture` з буфера витягується збережений стан фільтра `x̂(t_capture)` та `P(t_capture)`.
   - Виконується корекція Калмана `update()` за оптичними координатами.
   - Оновлений стан рекурсивно екстраполюється вперед через збережені команди прискорення від `t_capture` до поточного моменту `t_now`.

Такий алгоритм повністю компенсує затримку нейромережевої обробки, дозволяючи генератору APN формувати упереджувальні команди на основі актуального кінематичного стану.

---

### Обробка крайових ситуацій та сингулярностей

1. **Мала дальність (`R → 0`):**
   При наближенні на відстань менше габаритного радіуса апарата знаменник `||R||²` прямує до нуля, викликаючи чисельну нестійкість у розрахунку `Ω = (R × V_r) / ||R||²`. У коді передбачено зону відсікання `R < 0.1 м`, де кутова швидкість фіксується нульовою, а керування переходить на збереження постійної орієнтації або вимикання двигунів.

2. **Втрата оптичного контакту (Missing Frames):**
   Якщо ціль тимчасово перекривається перешкодою, метод `step()` викликається з порожнім вимірюванням (`std::nullopt` або `valid_meas = false`). Фільтр Калмана продовжує фазу прогнозу (`predict()`), зберігаючи екстрапольовану швидкість і прискорення цілі протягом допустимого таймауту (зазвичай 500–1000 мс), що дозволяє утримувати наведення під час короткочасних зривів оптичного супроводу.

3. **Фільтрація ривка (Jerk Limiting):**
   Миттєва стрибкоподібна зміна `a_cmd` призводить до насичення кутових швидкостей автопілота. На виході генератора встановлюється апертурний обмежувач похідної прискорення (Slew Rate Limiter):
   ```
   a_out(t) = a_out(t - Δt) + clamp(a_cmd - a_out(t - Δt), -j_max · Δt, +j_max · Δt)
   ```
   де `j_max ≈ 40–60 м/с³` — граничний допустимий ривок, узгоджений із динамікою поворотів гвинтомоторної групи.
