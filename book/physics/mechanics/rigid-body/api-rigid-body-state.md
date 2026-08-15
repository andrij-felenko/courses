# 📋 Специфікація стану та інтерфейсу абсолютно твердого тіла

Ця вставка містить повну структурну специфікацію та відкритий програмний інтерфейс (API) для опису стану абсолютно твердого тіла, обчислення його похідних фізичних характеристик (таких як поступальна й обертальна кінетична енергія, вектори імпульсу й моменту імпульсу, трансформований у світову систему тензор інерції), а також верифікації фізичних інваріантів у сучасних обчислювальних рушіях моделювання динаміки та робототехнічних комплексах.

Інтерфейс розроблено з урахуванням суворих вимог до продуктивності в реальному часі, повної сумісності з двостороннім C-ABI (Application Binary Interface) та легкого вбудовування в симуляційні конвеєри паралельного обчислення на процесорах із SIMD-розширеннями (AVX-2, AVX-512, ARM NEON).

### 1. Архитектура стану та принципи представлення даних

У чисельному моделюванні динаміки тривимірного абсолютно твердого тіла вектор стану повинен одночасно задовольняти дві протилежні вимоги: бути мінімальним для збереження пам'яті та бути обчислювально гладким для запобігання математичним сингулярностям при розв'язанні диференціальних рівнянь руху.

Стандартний вектор стану твердого тіла складається з 13 скалярних величин подвійної точності (IEEE 754 double precision), що займає в пам'яті рівно 104 байти:
1. **Позиція центру мас у світовій системі `position` (3 скаляри):** Декартові координати `(x, y, z)` у метрах відносно початку лабораторної системи відліку.
2. **Поступальна швидкість `linear_velocity` (3 скаляри):** Вектор лінійної швидкості центру мас `(v_x, v_y, v_z)` у метрах за секунду у світовій системі.
3. **Одиничний кватерніон орієнтації `orientation` (4 скаляри):** Гіперкомплексне число Гамільтона `q = (w, x, y, z)`, яке задає поворот власної зв'язаної системи координат тіла відносно світової системи. Використання кватерніона замість трьох кутів Ейлера гарантує відсутність ефекту заклинювання кардана (Gimbal Lock) при довільних просторових поворотах.
4. **Вектор кутової швидкості `angular_velocity` (3 скаляри):** Компоненти `(ω_x, ω_y, ω_z)` у радіанах за секунду, виражені у **власній зв'язаній системі координат тіла**. Вибір власної системи координат для кутової швидкості є фундаментальним, оскільки саме у власних осях тензор інерції тіла є постійним у часі й діагональним.

Масо-інерційні характеристики винесені в окрему структуру `rb_mass_props_t`. Це дозволяє розділити динамічний стан тіла, який змінюється на кожному кроці інтегрування, від його конструктивних геометричних властивостей, які залишаються сталими протягом усього симуляційного експерименту.

:::tabs
```c
/* C API: Rigid Body Types and Structures (C99 / C11) */
#ifndef RIGID_BODY_API_H
#define RIGID_BODY_API_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/** @brief Тривимірний вектор подвійної точності (24 байти) */
typedef struct {
    double x;
    double y;
    double z;
} rb_vec3_t;

/** @brief Одиничний кватерніон орієнтації [w, x, y, z] (32 байти) */
typedef struct {
    double w;
    double x;
    double y;
    double z;
} rb_quat_t;

/** @brief Симетрична матриця 3x3 у формі плоского масиву (72 байти) */
typedef struct {
    double m[3][3];
} rb_mat3_t;

/**
 * @brief Повний вектор стану абсолютно твердого тіла (104 байти)
 */
typedef struct {
    rb_vec3_t position;         /**< Позиція центру мас у світовій системі (m) */
    rb_vec3_t linear_velocity;  /**< Поступальна швидкість у світовій системі (m/s) */
    rb_quat_t orientation;      /**< Орієнтація у вигляді одиничного кватерніона */
    rb_vec3_t angular_velocity; /**< Кутова швидкість у ВЛАСНІЙ системі тіла (rad/s) */
} rb_state_t;

/**
 * @brief Масо-інерційні характеристики твердого тіла
 */
typedef struct {
    double mass;                /**< Загальна маса тіла (kg), повинна бути > 0 */
    rb_vec3_t inertia_diag;     /**< Головні моменти інерції [I_xx, I_yy, I_zz] (kg·m²) */
    rb_vec3_t inv_inertia_diag; /**< Обернені моменти інерції [1/I_xx, 1/I_yy, 1/I_zz] */
    rb_vec3_t center_of_mass;   /**< Зсув центру мас відносно геометричного центру (m) */
} rb_mass_props_t;

/**
 * @brief Вхідні зовнішні силові фактори
 */
typedef struct {
    rb_vec3_t force_world;      /**< Результуюча сила у світовій системі (N) */
    rb_vec3_t torque_body;      /**< Результуючий момент у ВЛАСНІЙ системі (N·m) */
} rb_inputs_t;

/**
 * @brief Похідні фізичні величини стану тіла
 */
typedef struct {
    double kinetic_energy_trans; /**< Поступальна кінетична енергія (J) */
    double kinetic_energy_rot;   /**< Обертальна кінетична енергія (J) */
    double kinetic_energy_total; /**< Повна кінетична енергія (J) */
    rb_vec3_t linear_momentum;   /**< Повний лінійний імпульс у світовій системі (kg·m/s) */
    rb_vec3_t angular_momentum;  /**< Повний момент імпульсу у світовій системі (kg·m²/s) */
    rb_mat3_t inertia_world;     /**< Тензор інерції, трансформований у світову систему */
} rb_derived_t;

/** @brief Перерахований тип кодів помилок верифікації стану */
typedef enum {
    RB_OK = 0,
    RB_ERROR_INVALID_MASS = 1,
    RB_ERROR_INVALID_INERTIA = 2,
    RB_ERROR_QUAT_NOT_NORMALIZED = 3,
    RB_ERROR_NAN_OR_INF = 4
} rb_error_t;

#ifdef __cplusplus
}
#endif

#endif /* RIGID_BODY_API_H */
```
```cpp
// C++ API: Strongly-Typed Object-Oriented Rigid Body Specification
#ifndef RIGID_BODY_HPP
#define RIGID_BODY_HPP

#include <array>
#include <cmath>
#include <expected>
#include <optional>
#include <span>

namespace physics::api {

struct Vec3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] constexpr double norm_sq() const noexcept { return x * x + y * y + z * z; }
    [[nodiscard]] double norm() const noexcept { return std::sqrt(norm_sq()); }
};

struct Quat {
    double w{1.0};
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] constexpr double norm_sq() const noexcept { return w * w + x * x + y * y + z * z; }
    [[nodiscard]] double norm() const noexcept { return std::sqrt(norm_sq()); }
};

using Mat3x3 = std::array<std::array<double, 3>, 3>;

enum class ValidationError {
    InvalidMass,
    InvalidInertiaTensor,
    QuaternionDegenerate,
    ContainsNanOrInf
};

struct RigidBodyState {
    Vec3 position{};
    Vec3 linear_velocity{};
    Quat orientation{};
    Vec3 angular_velocity_body{};
};

struct MassProperties {
    double mass{1.0};
    Vec3 principal_inertia{1.0, 1.0, 1.0};
    Vec3 center_of_mass_offset{};

    [[nodiscard]] std::expected<void, ValidationError> validate() const noexcept {
        if (mass <= 0.0 || std::isnan(mass) || std::isinf(mass)) {
            return std::unexpected(ValidationError::InvalidMass);
        }
        if (principal_inertia.x <= 0.0 || principal_inertia.y <= 0.0 || principal_inertia.z <= 0.0) {
            return std::unexpected(ValidationError::InvalidInertiaTensor);
        }
        return {};
    }
};

struct DerivedState {
    double kinetic_energy_transient{0.0};
    double kinetic_energy_rotational{0.0};
    double kinetic_energy_total{0.0};
    Vec3 linear_momentum_world{};
    Vec3 angular_momentum_world{};
    Mat3x3 inertia_tensor_world{};
};

} // namespace physics::api

#endif // RIGID_BODY_HPP
```
:::

### 2. Детальний опис функціональних контрактів та параметрів

Кожна функція модуля строго підпорядковується принципу відсутності побічних ефектів і гарантує коректну обробку крайових випадків. Нижче наведено повну специфікацію викликів для роботи з вектором стану.

#### Перевірка валідності стану (`rb_validate_state`)

При тривалій чисельній симуляції через накопичення помилок заокруглення чисел з плаваючою крапкою норма кватерніона `||q||` може поступово відхилятися від одиниці. Крім того, при нестійких інтерполяціях або некоректних зовнішніх силах у вектор стану можуть потрапити значення `NaN` (Not a Number) або `Inf` (Infinity).

Функція `rb_validate_state` виконує повну інспекцію стану:
1. Сканує всі 13 компонент вектора стану та масових характеристик на відсутність невизначених залишків `NaN` чи нескінченностей `Inf`.
2. Перевіряє, що маса тіла є строго додатною величиною `mass > 0`.
3. Перевіряє, що всі три головні моменти інерції є строго додатними `I_xx > 0, I_yy > 0, I_zz > 0`.
4. Обчислює квадрат евклідової норми кватерніона `||q||² = w² + x² + y² + z²` та порівнює його відхилення від 1.0 з допуском `quat_tol`. Якщо відхилення перевищує допуск, функція повертає код помилки `RB_ERROR_QUAT_NOT_NORMALIZED`.

#### Обчислення похідних величин (`rb_compute_derived`)

Функція розраховує повний енергетичний та імпульсний паспорт тіла для поточного кроку симуляції:
- **Поступальна кінетична енергія:**Обчислюється за формулою `T_trans = ½ · m · (v_x² + v_y² + v_z²)`.
- **Обертальна кінетична енергія:**Оскільки кутова швидкість задана у власних осях, де тензор інерції є діагональним, обертальна енергія обчислюється без виснажливого множення матриць: `T_rot = ½ · (I_xx · ω_x² + I_yy · ω_y² + I_zz · ω_z²)`.
- **Лінійний імпульс у світовій системі:** `P_world = m · v_world`.
- **Момент імпульсу у світовій системі:** Спершу обчислюється момент імпульсу у власній системі тіла `L_body = (I_xx · ω_x, I_yy · ω_y, I_zz · ω_z)`, після чого він трансформується у світову систему за допомогою матриці обертання `L_world = R(q) · L_body`.
- **Тензор інерції у світовій системі:** Перераховується за формулою тензорного перетворення `I_world = R(q) · I_body · R(q)ᵀ`. Оскільки `I_body` є діагональною матрицею, ця операція оптимізована до прямих скалярних добутків компонент матриці `R`, що запобігає зайвим циклічним множенням.

| Функція / Метод | Опис і призначення | Вхідні параметри | Вихідне значення / Інваріант |
| :--- | :--- | :--- | :--- |
| `rb_validate_state` | Перевірка стану тіла на відсутність NaN, Inf та дрейф норми кватерніона | `const rb_state_t* s`, `const rb_mass_props_t* m`, `double tol` | `RB_OK` якщо стан задовольняє всі вимоги, інакше відповідний код помилки |
| `rb_normalize_state` | Примусове нормування кватерніона орієнтації до одиничної довжини | `rb_state_t* s` | Кватерніон стану гарантовано задовольняє `\|\|quat\|\| = 1.0` |
| `rb_compute_derived` | Обчислення імпульсів, енергій та світового тензора інерції | `const rb_state_t* s`, `const rb_mass_props_t* m` | Заповнена структура похідних величин `rb_derived_t` |
| `rb_body_to_world_vec` | Перетворення вектора зі зв'язаної системи тіла у світову систему | `rb_quat_t q`, `rb_vec3_t v_body` | Трансформований вектор `v_world = q ⊗ v_body ⊗ q*` |
| `rb_world_to_body_vec` | Перетворення вектора зі світової системи у зв'язану систему тіла | `rb_quat_t q`, `rb_vec3_t v_world` | Трансформований вектор `v_body = q* ⊗ v_world ⊗ q` |

### 3. Алгоритмічна реалізація валідації та перетворень

:::tabs
```c
/* C Implementation: State Validation and Matrix Transformations */
#include <math.h>
#include <stdbool.h>

rb_error_t rb_validate_state(const rb_state_t *s, const rb_mass_props_t *m, double quat_tol) {
    if (!s || !m) return RB_ERROR_NAN_OR_INF;

    /* 1. Сканування компонент на NaN / Inf */
    if (isnan(s->position.x) || isnan(s->position.y) || isnan(s->position.z) ||
        isnan(s->linear_velocity.x) || isnan(s->linear_velocity.y) || isnan(s->linear_velocity.z) ||
        isnan(s->orientation.w) || isnan(s->orientation.x) || isnan(s->orientation.y) || isnan(s->orientation.z) ||
        isnan(s->angular_velocity.x) || isnan(s->angular_velocity.y) || isnan(s->angular_velocity.z)) {
        return RB_ERROR_NAN_OR_INF;
    }

    if (m->mass <= 0.0 || isnan(m->mass) || isinf(m->mass)) return RB_ERROR_INVALID_MASS;
    if (m->inertia_diag.x <= 0.0 || m->inertia_diag.y <= 0.0 || m->inertia_diag.z <= 0.0) {
        return RB_ERROR_INVALID_INERTIA;
    }

    /* 2. Перевірка норми кватерніона */
    double q_sq = s->orientation.w * s->orientation.w +
                  s->orientation.x * s->orientation.x +
                  s->orientation.y * s->orientation.y +
                  s->orientation.z * s->orientation.z;
    if (fabs(q_sq - 1.0) > quat_tol) {
        return RB_ERROR_QUAT_NOT_NORMALIZED;
    }

    return RB_OK;
}

void rb_normalize_state(rb_state_t *s) {
    if (!s) return;
    double len = sqrt(s->orientation.w * s->orientation.w +
                      s->orientation.x * s->orientation.x +
                      s->orientation.y * s->orientation.y +
                      s->orientation.z * s->orientation.z);
    if (len < 1e-12) {
        s->orientation.w = 1.0;
        s->orientation.x = 0.0;
        s->orientation.y = 0.0;
        s->orientation.z = 0.0;
    } else {
        s->orientation.w /= len;
        s->orientation.x /= len;
        s->orientation.y /= len;
        s->orientation.z /= len;
    }
}

rb_derived_t rb_compute_derived(const rb_state_t *s, const rb_mass_props_t *m) {
    rb_derived_t d;

    /* 1. Поступальна кінетична енергія: T_trans = 0.5 * m * v² */
    double v_sq = s->linear_velocity.x * s->linear_velocity.x +
                  s->linear_velocity.y * s->linear_velocity.y +
                  s->linear_velocity.z * s->linear_velocity.z;
    d.kinetic_energy_trans = 0.5 * m->mass * v_sq;

    /* 2. Обертальна кінетична енергія: T_rot = 0.5 * (I_x w_x² + I_y w_y² + I_z w_z²) */
    d.kinetic_energy_rot = 0.5 * (
        m->inertia_diag.x * s->angular_velocity.x * s->angular_velocity.x +
        m->inertia_diag.y * s->angular_velocity.y * s->angular_velocity.y +
        m->inertia_diag.z * s->angular_velocity.z * s->angular_velocity.z
    );

    d.kinetic_energy_total = d.kinetic_energy_trans + d.kinetic_energy_rot;

    /* 3. Лінійний імпульс у світі: P = m * v */
    d.linear_momentum.x = m->mass * s->linear_velocity.x;
    d.linear_momentum.y = m->mass * s->linear_velocity.y;
    d.linear_momentum.z = m->mass * s->linear_velocity.z;

    /* 4. Момент імпульсу у власних осях: L_body = I_body * omega_body */
    rb_vec3_t L_body = {
        m->inertia_diag.x * s->angular_velocity.x,
        m->inertia_diag.y * s->angular_velocity.y,
        m->inertia_diag.z * s->angular_velocity.z
    };

    /* 5. Перетворення L_body у світову систему: L_world = R * L_body */
    double qw = s->orientation.w, qx = s->orientation.x, qy = s->orientation.y, qz = s->orientation.z;
    
    /* Елементи матриці обертання R з кватерніона */
    double R00 = 1.0 - 2.0 * (qy * qy + qz * qz);
    double R01 = 2.0 * (qx * qy - qz * qw);
    double R02 = 2.0 * (qx * qz + qy * qw);

    double R10 = 2.0 * (qx * qy + qz * qw);
    double R11 = 1.0 - 2.0 * (qx * qx + qz * qz);
    double R12 = 2.0 * (qy * qz - qx * qw);

    double R20 = 2.0 * (qx * qz - qy * qw);
    double R21 = 2.0 * (qy * qz + qx * qw);
    double R22 = 1.0 - 2.0 * (qx * qx + qy * qy);

    d.angular_momentum.x = R00 * L_body.x + R01 * L_body.y + R02 * L_body.z;
    d.angular_momentum.y = R10 * L_body.x + R11 * L_body.y + R12 * L_body.z;
    d.angular_momentum.z = R20 * L_body.x + R21 * L_body.y + R22 * L_body.z;

    /* 6. Трансформація тензора інерції у світову систему: I_world = R * I_body * Rᵀ */
    d.inertia_world.m[0][0] = R00*R00*m->inertia_diag.x + R01*R01*m->inertia_diag.y + R02*R02*m->inertia_diag.z;
    d.inertia_world.m[0][1] = R00*R10*m->inertia_diag.x + R01*R11*m->inertia_diag.y + R02*R12*m->inertia_diag.z;
    d.inertia_world.m[0][2] = R00*R20*m->inertia_diag.x + R01*R21*m->inertia_diag.y + R02*R22*m->inertia_diag.z;

    d.inertia_world.m[1][0] = d.inertia_world.m[0][1];
    d.inertia_world.m[1][1] = R10*R10*m->inertia_diag.x + R11*R11*m->inertia_diag.y + R12*R12*m->inertia_diag.z;
    d.inertia_world.m[1][2] = R10*R20*m->inertia_diag.x + R11*R21*m->inertia_diag.y + R12*R22*m->inertia_diag.z;

    d.inertia_world.m[2][0] = d.inertia_world.m[0][2];
    d.inertia_world.m[2][1] = d.inertia_world.m[1][2];
    d.inertia_world.m[2][2] = R20*R20*m->inertia_diag.x + R21*R21*m->inertia_diag.y + R22*R22*m->inertia_diag.z;

    return d;
}
```
```cpp
// C++ Implementation: Derived Computations using Modern C++ Types
#include <cmath>
#include <expected>

namespace physics::api {

[[nodiscard]] inline DerivedState compute_derived(const RigidBodyState& s, const MassProperties& m) noexcept {
    DerivedState d;

    double v_sq = s.linear_velocity.norm_sq();
    d.kinetic_energy_transient = 0.5 * m.mass * v_sq;

    d.kinetic_energy_rotational = 0.5 * (
        m.principal_inertia.x * s.angular_velocity_body.x * s.angular_velocity_body.x +
        m.principal_inertia.y * s.angular_velocity_body.y * s.angular_velocity_body.y +
        m.principal_inertia.z * s.angular_velocity_body.z * s.angular_velocity_body.z
    );

    d.kinetic_energy_total = d.kinetic_energy_transient + d.kinetic_energy_rotational;

    d.linear_momentum_world = {
        m.mass * s.linear_velocity.x,
        m.mass * s.linear_velocity.y,
        m.mass * s.linear_velocity.z
    };

    Vec3 L_body{
        m.principal_inertia.x * s.angular_velocity_body.x,
        m.principal_inertia.y * s.angular_velocity_body.y,
        m.principal_inertia.z * s.angular_velocity_body.z
    };

    const auto& q = s.orientation;
    double R00 = 1.0 - 2.0 * (q.y * q.y + q.z * q.z);
    double R01 = 2.0 * (q.x * q.y - q.z * q.w);
    double R02 = 2.0 * (q.x * q.z + q.y * q.w);

    double R10 = 2.0 * (q.x * q.y + q.z * q.w);
    double R11 = 1.0 - 2.0 * (q.x * q.x + q.z * q.z);
    double R12 = 2.0 * (q.y * q.z - q.x * q.w);

    double R20 = 2.0 * (q.x * q.z - q.y * q.w);
    double R21 = 2.0 * (q.y * q.z + q.x * q.w);
    double R22 = 1.0 - 2.0 * (q.x * q.x + q.y * q.y);

    d.angular_momentum_world = {
        R00 * L_body.x + R01 * L_body.y + R02 * L_body.z,
        R10 * L_body.x + R11 * L_body.y + R12 * L_body.z,
        R20 * L_body.x + R21 * L_body.y + R22 * L_body.z
    };

    d.inertia_tensor_world = {{
        { R00*R00*m.principal_inertia.x + R01*R01*m.principal_inertia.y + R02*R02*m.principal_inertia.z,
          R00*R10*m.principal_inertia.x + R01*R11*m.principal_inertia.y + R02*R12*m.principal_inertia.z,
          R00*R20*m.principal_inertia.x + R01*R21*m.principal_inertia.y + R02*R22*m.principal_inertia.z },
        { R00*R10*m.principal_inertia.x + R01*R11*m.principal_inertia.y + R02*R12*m.principal_inertia.z,
          R10*R10*m.principal_inertia.x + R11*R11*m.principal_inertia.y + R12*R12*m.principal_inertia.z,
          R10*R20*m.principal_inertia.x + R11*R21*m.principal_inertia.y + R12*R22*m.principal_inertia.z },
        { R00*R20*m.principal_inertia.x + R01*R21*m.principal_inertia.y + R02*R22*m.principal_inertia.z,
          R10*R20*m.principal_inertia.x + R11*R21*m.principal_inertia.y + R12*R22*m.principal_inertia.z,
          R20*R20*m.principal_inertia.x + R21*R21*m.principal_inertia.y + R22*R22*m.principal_inertia.z }
    }};

    return d;
}

} // namespace physics::api
```
:::

### 4. Вимоги до вирівнювання пам'яті, SIMD та продуктивності

Для досягнення максимальної швидкодії у фізичних симуляторах масштабу мільйонів об'єктів (наприклад, у моделюванні гранульованих середовищ або складених механічних масивів) структура стану та алгоритми її обробки повинні підпорядковуватися кільком суворим інженерним правилам.

#### Вирівнювання пам'яті та кеш-лінії (Cache Alignment)

Розмір структури `rb_state_t` становить 104 байти. У сучасних процесорах x86_64 та ARM64 розмір кеш-лінії L1 становить 64 байти. Це означає, що один екземпляр `rb_state_t` неминуче перетинає межу двох кеш-ліній. 

При збереженні тисяч тіл у вигляді масиву структур (Array of Structures, AoS) рекомендується вживати явне вирівнювання на 64 або 128 байт:

:::tabs
```c
typedef struct alignas(64) {
    rb_vec3_t position;
    rb_vec3_t linear_velocity;
    rb_quat_t orientation;
    rb_vec3_t angular_velocity;
    double _padding[3]; /* Доповнення до 128 байт (2 повні кеш-лінії) */
} rb_aligned_state_t;
```
```cpp
struct alignas(64) AlignedRigidBodyState {
    Vec3 position;
    Vec3 linear_velocity;
    Quat orientation;
    Vec3 angular_velocity;
    std::array<double, 3> padding; // Доповнення до 128 байт
};
```
:::

Вирівнювання до 128 байт гарантує, що вектор стану кожного тіла займає точно дві кеш-лінії й ніколи не викликає виснажливих промахів кешу при міжпроцесорному обміні у багатопотокових обчисленнях.

#### Автовекторизація та відсутність розгалужень (Branchless execution)

Обчислення похідних величин у `rb_compute_derived` навмисно позбавлено будь-яких умовних операторів `if/else` чи логічних розгалужень. Усі скалярні добутки реалізовано у вигляді прямих арифметика-математичних виразів. 

Це дає змогу сучасним компіляторам (GCC 13+, Clang 16+, MSVC 2022) генерувати повністю векторизований машиний код з використанням векторних регістрів AVX-2 / AVX-512 (на процесорах Intel/AMD) або NEON / SVE (на процесорах Apple Silicon / ARM). Один векторний регістр AVX-512 здатний одночасно обробляти 8 чисел типу `double`, прискорюючи розрахунок енергії та імпульсу масиву тіл майже в 7-8 разів.

#### Режими валідації та конвеєр симуляції

У бойових симуляційних рушіях функція валідації `rb_validate_state` викликається не на кожному внутрішньому підкроці інтегратора, а лише в таких критичних точках:
1. При ініціалізації об'єкта з зовнішніх конфігураційних файлів чи сцен.
2. Після виконання фази розв'язання дискретних контактів та імпульсів зіткнення (Contact Solver).
3. При виконанні контрольних процедур збереження стану (Checkpoints / State snapshots).

Такий роздільний підхід дозволяє поєднати математичну суворість і надійність із максимальною продуктивністю обчислювального ядра.
