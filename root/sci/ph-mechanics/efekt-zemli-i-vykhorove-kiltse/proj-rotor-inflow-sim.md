# ⚙️ Моделювання перехідних аеродинамічних режимів ротора (IGE, OGE, VRS)

Цей проект реалізує комплексний числовий розв'язувач аеродинаміки несучого гвинта для вбудованих автопілотів (прошивок типу ArduPilot, PX4) та високоточних польотних симуляторів реального часу. Програма розраховує поле індукованих швидкостей у трьох принципово різних фізичних режимах: у вільному просторі (OGE), в екрані землі (IGE) за емпіричною моделлю Гейдена, а також у зоні гідродинамічної нестабільності вихорового кільця (VRS) за кусочно-гладкою моделлю Волковича — Лейшмана.

---

### Фізична постановка та алгоритмічна структура розв'язувача

Головна проблема чисельного моделювання динаміки ротокрафта в реальному часі полягає в тому, що класична одновимірна теорія імпульсу Ренкіна — Фруда містить математичні сингулярності. Під час вертикального зниження (`-2 < V̂_z < 0`) підкореневий вираз формули Главерта стає від'ємним, що викликає появу недійсних чисел (NaN) та збій польотного комп'ютера. Крім того, при нульовій тязі формули вимагають ділення на нуль, а поблизу землі класична модель не враховує тверду межу розтікання потоку.

Для усунення цих дефектів алгоритм розбивається на кілька послідовних розрахункових блоків:

1. **Розрахунок масштабу швидкості висіння:** за поточною командною тягою `T`, густиною атмосфери `ρ` та площею диска `A = π·R²` визначається базова індукована швидкість:
   ```
   v_i0 = √( T / (2 · ρ · A) )
   ```
   Якщо тяга менша за порогову величину (`T ≤ 0.05` Н), алгоритм повертає нульову індуковану швидкість без обчислення коренів, запобігаючи діленню на нуль у точках вимкнення моторів або вільного падіння.

2. **Нормалізація вектора швидкостей:** обчислюються безрозмірні компоненти відносно швидкості висіння `v_i0`:
   - Безрозмірна вертикальна швидкість: `V̂_z = V_z / v_i0` (де `V_z > 0` — набір висоти, `V_z < 0` — спуск).
   - Безрозмірна горизонтальна швидкість: `V̂_x = √(V_x² + V_y²) / v_i0`.

3. **Визначення аеродинамічного режиму за віссю тяги:**
   - **Режим набору висоти та висіння (`V̂_z ≥ 0`):** застосовується точний аналітичний розв'язок Главерта `v̂_i = −V̂_z/2 + √((V̂_z/2)² + 1)`.
   - **Режим швидкого спуску та вітряка (`V̂_z ≤ −2.0`):** застосовується розв'язок вітряного гальма `v̂_i = −V̂_z/2 − √((V̂_z/2)² − 1)`.
   - **Зона тороїдальної рециркуляції та VRS (`−2.0 < V̂_z < 0`):** при малій поступальній швидкості (`V̂_x < 1.0`) активується кубічний поліном Волковича `v̂_i,VRS = 1.0 − 0.125·V̂_z − 1.125·V̂_z² − 0.5·V̂_z³`. При наявності горизонтального руху потік косо обдуває диск за моделлю Лейшмана:
     ```
     v̂_i = v̂_i,VRS · (1 − V̂_x) + (1 / √(V̂_x² + V̂_z²)) · V̂_x
     ```

4. **Корекція на екран землі (IGE):** якщо висота апарата над поверхнею `h < 2.5·R`, а горизонтальна швидкість невелика (`V_horiz < 1.5` м/с), індукована швидкість масштабується коефіцієнтом Гейдена:
   ```
   k_IGE = 1 / ( 0.9926 + 0.0379 · (h / R)⁻² )
   v_i,IGE = v_i · k_IGE
   ```

5. **Числове інтегрування динаміки:** стан апарата `(x, y, z, v_x, v_y, v_z)` оновлюється на кожному часовому кроці `dt`. Враховується падіння аеродинамічного ККД лопатей у режимі VRS (втрата 35% корисної тяги через компресорний зрив і вихорову рециркуляцію) та динамічний опір набігаючого потоку.

---

:::tabs
```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define R_ROTOR      0.15     /* радіус гвинта квадрокоптера, м */
#define MASS         1.20     /* маса апарата, кг */
#define GRAVITY      9.80665  /* прискорення вільного падіння, м/с² */
#define RHO_AIR      1.225    /* густина повітря на рівні моря, кг/м³ */
#define PI_CONST     3.14159265358979323846

typedef enum {
    REGIME_NORMAL_HOVER,
    REGIME_GROUND_EFFECT,
    REGIME_VORTEX_RING_STATE,
    REGIME_TURBULENT_WAKE,
    REGIME_WINDMILL_BRAKE
} RotorRegime;

typedef struct {
    double z;           /* висота над землею, м */
    double vx;          /* горизонтальна швидкість уперед, м/с */
    double vy;          /* бічна швидкість управо, м/с */
    double vz;          /* вертикальна швидкість (додатна вгору), м/с */
    double thrust_cmd;  /* командна тяга моторів, Н */
    RotorRegime regime; /* поточний аеродинамічний режим */
} VehicleState;

/* Розрахунок індукованої швидкості з урахуванням екрана землі та VRS */
double compute_induced_velocity(double thrust, double z, double vx, double vy, double vz, RotorRegime *out_regime) {
    double disk_area = PI_CONST * R_ROTOR * R_ROTOR;
    if (thrust <= 0.05) {
        if (out_regime) *out_regime = REGIME_NORMAL_HOVER;
        return 0.0;
    }

    double vi0 = sqrt(thrust / (2.0 * RHO_AIR * disk_area));
    double v_horiz = sqrt(vx * vx + vy * vy);
    double v_hat_z = vz / vi0;
    double v_hat_x = v_horiz / vi0;
    double vi_dimless = 1.0;
    RotorRegime reg = REGIME_NORMAL_HOVER;

    /* 1. Перевірка осьового режиму */
    if (v_hat_z >= 0.0) {
        /* Набір або зависання */
        double half_vz = v_hat_z / 2.0;
        vi_dimless = -half_vz + sqrt(half_vz * half_vz + 1.0);
        reg = REGIME_NORMAL_HOVER;
    } else if (v_hat_z <= -2.0) {
        /* Режим вітряка / авторотації */
        double half_vz = v_hat_z / 2.0;
        double disc = half_vz * half_vz - 1.0;
        vi_dimless = -half_vz - sqrt(disc > 0.0 ? disc : 0.0);
        reg = REGIME_WINDMILL_BRAKE;
    } else {
        /* Зона -2.0 < V_hat_z < 0.0: рециркуляція та VRS */
        if (v_hat_x < 1.0) {
            /* Модель Волковича для чистого спуску */
            double vi_vrs = 1.0 - 0.125 * v_hat_z - 1.125 * v_hat_z * v_hat_z - 0.5 * v_hat_z * v_hat_z * v_hat_z;
            /* Корекція на косий потік Лейшмана */
            double vi_skew = 1.0 / sqrt(v_hat_x * v_hat_x + (v_hat_z + vi_vrs) * (v_hat_z + vi_vrs) + 0.01);
            vi_dimless = vi_vrs * (1.0 - v_hat_x) + vi_skew * v_hat_x;

            if (v_hat_z >= -1.25 && v_hat_z <= -0.4) {
                reg = REGIME_VORTEX_RING_STATE;
            } else {
                reg = REGIME_TURBULENT_WAKE;
            }
        } else {
            /* Достатня горизонтальна швидкість — потік косо обдуває диск */
            vi_dimless = 1.0 / sqrt(v_hat_x * v_hat_x + v_hat_z * v_hat_z);
            reg = REGIME_NORMAL_HOVER;
        }
    }

    double vi = vi_dimless * vi0;

    /* 2. Корекція на ефект землі (IGE) при висінні поблизу поверхні */
    if (z > 0.05 && z < 2.5 * R_ROTOR && vz > -0.5 && vz < 0.5 && v_horiz < 1.5) {
        double hr = z / R_ROTOR;
        /* Модель Гейдена для зменшення індукованої швидкості */
        double ige_ratio = 1.0 / (0.9926 + 0.0379 / (hr * hr));
        vi *= ige_ratio;
        reg = REGIME_GROUND_EFFECT;
    }

    if (out_regime) *out_regime = reg;
    return vi;
}

/* Симуляція кроку польоту (інтегрування за Ейлером) */
void step_simulation(VehicleState *s, double dt) {
    double vi = compute_induced_velocity(s->thrust_cmd, s->z, s->vx, s->vy, s->vz, &s->regime);

    /* Фактична тяга: в режимі VRS через падіння кутів атаки та зрив тяга падає */
    double actual_thrust = s->thrust_cmd;
    if (s->regime == REGIME_VORTEX_RING_STATE) {
        /* Втрата ефективної тяги на 35% через тороїдальний зрив */
        actual_thrust *= 0.65;
    } else if (s->regime == REGIME_GROUND_EFFECT) {
        /* Приріст тяги в екрані землі */
        actual_thrust *= 1.18;
    }

    double weight = MASS * GRAVITY;
    double az = (actual_thrust - weight) / MASS;
    double ax = -0.5 * RHO_AIR * 0.05 * s->vx * fabs(s->vx) / MASS;
    double ay = -0.5 * RHO_AIR * 0.05 * s->vy * fabs(s->vy) / MASS;

    s->vz += az * dt;
    s->vx += ax * dt;
    s->vy += ay * dt;
    s->z += s->vz * dt;

    if (s->z < 0.0) {
        s->z = 0.0;
        s->vz = 0.0;
    }
}

int main(void) {
    printf("=== Симуляція потрапляння у VRS та виходу маневром Вюішара ===\n\n");

    /* Сценарій 1: Помилкова спроба дати повний газ у VRS (Settling with Power) */
    VehicleState s_panic = { .z = 30.0, .vx = 0.0, .vy = 0.0, .vz = -3.2, .thrust_cmd = MASS * GRAVITY, .regime = REGIME_NORMAL_HOVER };
    printf("--- Сценарій 1: Додавання газу без розгону (залипання у VRS) ---\n");
    for (int t_step = 0; t_step <= 30; ++t_step) {
        double time = t_step * 0.1;
        if (t_step == 5) {
            /* Пілот бачить падіння і дає 140% тяги */
            s_panic.thrust_cmd = MASS * GRAVITY * 1.40;
        }
        step_simulation(&s_panic, 0.1);
        if (t_step % 5 == 0) {
            printf("t=%.1fs | z=%5.2fm | vz=%+5.2fm/s | Тяга=%5.1fН | Режим=%d\n",
                   time, s_panic.z, s_panic.vz, s_panic.thrust_cmd, s_panic.regime);
        }
    }

    /* Сценарій 2: Маневр Вюішара (бічний зсув цикліком + крок) */
    VehicleState s_vuichard = { .z = 30.0, .vx = 0.0, .vy = 0.0, .vz = -3.2, .thrust_cmd = MASS * GRAVITY, .regime = REGIME_NORMAL_HOVER };
    printf("\n--- Сценарій 2: Маневр Вюішара (бічний імпульс vy = 3.5 м/с) ---\n");
    for (int t_step = 0; t_step <= 30; ++t_step) {
        double time = t_step * 0.1;
        if (t_step == 3) {
            /* Застосування цикліка вбік та збільшення тяги */
            s_vuichard.vy = 3.5;
            s_vuichard.thrust_cmd = MASS * GRAVITY * 1.25;
        }
        step_simulation(&s_vuichard, 0.1);
        if (t_step % 5 == 0) {
            printf("t=%.1fs | z=%5.2fm | vz=%+5.2fm/s | vy=%4.1fm/s | Режим=%d\n",
                   time, s_vuichard.z, s_vuichard.vz, s_vuichard.vy, s_vuichard.regime);
        }
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <numbers>
#include <string_view>
#include <vector>
#include <iomanip>

namespace aero {

constexpr double R_ROTOR     = 0.15;     // радіус гвинта квадрокоптера, м
constexpr double MASS        = 1.20;     // маса апарата, кг
constexpr double GRAVITY     = 9.80665;  // прискорення вільного падіння, м/с²
constexpr double RHO_AIR     = 1.225;    // густина повітря, кг/м³

enum class RotorRegime {
    NormalHover,
    GroundEffect,
    VortexRingState,
    TurbulentWake,
    WindmillBrake
};

[[nodiscard]] constexpr std::string_view regime_name(RotorRegime r) noexcept {
    switch (r) {
        case RotorRegime::NormalHover:     return "Звичайне висіння (OGE)";
        case RotorRegime::GroundEffect:    return "Екран землі (IGE)";
        case RotorRegime::VortexRingState: return "Вихорове кільце (VRS)";
        case RotorRegime::TurbulentWake:   return "Турбулентний слід";
        case RotorRegime::WindmillBrake:   return "Режим вітряка";
    }
    return "Невідомий";
}

struct VehicleState {
    double z{0.0};           // висота над землею, м
    double vx{0.0};          // горизонтальна швидкість уперед, м/с
    double vy{0.0};          // бічна швидкість управо, м/с
    double vz{0.0};          // вертикальна швидкість (додатна вгору), м/с
    double thrust_cmd{0.0};  // командна тяга моторів, Н
    RotorRegime regime{RotorRegime::NormalHover};
};

class AerodynamicSolver {
public:
    [[nodiscard]] static std::pair<double, RotorRegime> compute_inflow(
        double thrust, double z, double vx, double vy, double vz) noexcept
    {
        constexpr double disk_area = std::numbers::pi * R_ROTOR * R_ROTOR;
        if (thrust <= 0.05) {
            return {0.0, RotorRegime::NormalHover};
        }

        const double vi0 = std::sqrt(thrust / (2.0 * RHO_AIR * disk_area));
        const double v_horiz = std::hypot(vx, vy);
        const double v_hat_z = vz / vi0;
        const double v_hat_x = v_horiz / vi0;

        double vi_dimless = 1.0;
        RotorRegime reg = RotorRegime::NormalHover;

        if (v_hat_z >= 0.0) {
            // Режим висіння або набору
            const double half_vz = v_hat_z / 2.0;
            vi_dimless = -half_vz + std::sqrt(half_vz * half_vz + 1.0);
            reg = RotorRegime::NormalHover;
        } else if (v_hat_z <= -2.0) {
            // Режим вітряка / авторотації
            const double half_vz = v_hat_z / 2.0;
            const double disc = half_vz * half_vz - 1.0;
            vi_dimless = -half_vz - std::sqrt(std::max(0.0, disc));
            reg = RotorRegime::WindmillBrake;
        } else {
            // Зона VRS / рециркуляції
            if (v_hat_x < 1.0) {
                const double vi_vrs = 1.0 - 0.125 * v_hat_z - 1.125 * v_hat_z * v_hat_z - 0.5 * std::pow(v_hat_z, 3);
                const double vi_skew = 1.0 / std::sqrt(v_hat_x * v_hat_x + std::pow(v_hat_z + vi_vrs, 2) + 0.01);
                vi_dimless = vi_vrs * (1.0 - v_hat_x) + vi_skew * v_hat_x;

                if (v_hat_z >= -1.25 && v_hat_z <= -0.4) {
                    reg = RotorRegime::VortexRingState;
                } else {
                    reg = RotorRegime::TurbulentWake;
                }
            } else {
                vi_dimless = 1.0 / std::hypot(v_hat_x, v_hat_z);
                reg = RotorRegime::NormalHover;
            }
        }

        double vi = vi_dimless * vi0;

        // Корекція на ефект землі (IGE)
        if (z > 0.05 && z < 2.5 * R_ROTOR && std::abs(vz) < 0.5 && v_horiz < 1.5) {
            const double hr = z / R_ROTOR;
            const double ige_ratio = 1.0 / (0.9926 + 0.0379 / (hr * hr));
            vi *= ige_ratio;
            reg = RotorRegime::GroundEffect;
        }

        return {vi, reg};
    }

    static void step(VehicleState& s, double dt) noexcept {
        const auto [vi, regime] = compute_inflow(s.thrust_cmd, s.z, s.vx, s.vy, s.vz);
        s.regime = regime;

        double actual_thrust = s.thrust_cmd;
        if (s.regime == RotorRegime::VortexRingState) {
            actual_thrust *= 0.65; // втрата 35% тяги через тороїдальний зрив
        } else if (s.regime == RotorRegime::GroundEffect) {
            actual_thrust *= 1.18; // приріст тяги на повітряній подушці
        }

        const double weight = MASS * GRAVITY;
        const double az = (actual_thrust - weight) / MASS;
        const double ax = -0.5 * RHO_AIR * 0.05 * s.vx * std::abs(s.vx) / MASS;
        const double ay = -0.5 * RHO_AIR * 0.05 * s.vy * std::abs(s.vy) / MASS;

        s.vz += az * dt;
        s.vx += ax * dt;
        s.vy += ay * dt;
        s.z += s.vz * dt;

        if (s.z < 0.0) {
            s.z = 0.0;
            s.vz = 0.0;
        }
    }
};

} // namespace aero

int main() {
    std::cout << "=== Симуляція динаміки VRS та маневру Вюішара (C++) ===\n\n";

    // Сценарій 1: Помилкова спроба дати газ на місці
    aero::VehicleState s_panic{
        .z = 30.0, .vx = 0.0, .vy = 0.0, .vz = -3.2,
        .thrust_cmd = aero::MASS * aero::GRAVITY
    };

    std::cout << "--- Сценарій 1: Додавання газу на місці (залипання у VRS) ---\n";
    for (int step = 0; step <= 30; ++step) {
        const double time = step * 0.1;
        if (step == 5) {
            s_panic.thrust_cmd = aero::MASS * aero::GRAVITY * 1.40;
        }
        aero::AerodynamicSolver::step(s_panic, 0.1);
        if (step % 5 == 0) {
            std::cout << std::fixed << std::setprecision(1)
                      << "t=" << time << "s | z=" << std::setprecision(2) << s_panic.z
                      << "m | vz=" << std::showpos << s_panic.vz << "m/s | Режим: "
                      << std::noshowpos << aero::regime_name(s_panic.regime) << "\n";
        }
    }

    // Сценарій 2: Маневр Вюішара
    aero::VehicleState s_vuichard{
        .z = 30.0, .vx = 0.0, .vy = 0.0, .vz = -3.2,
        .thrust_cmd = aero::MASS * aero::GRAVITY
    };

    std::cout << "\n--- Сценарій 2: Маневр Вюішара (бічний зсув vy = 3.5 м/с) ---\n";
    for (int step = 0; step <= 30; ++step) {
        const double time = step * 0.1;
        if (step == 3) {
            s_vuichard.vy = 3.5;
            s_vuichard.thrust_cmd = aero::MASS * aero::GRAVITY * 1.25;
        }
        aero::AerodynamicSolver::step(s_vuichard, 0.1);
        if (step % 5 == 0) {
            std::cout << std::fixed << std::setprecision(1)
                      << "t=" << time << "s | z=" << std::setprecision(2) << s_vuichard.z
                      << "m | vz=" << std::showpos << s_vuichard.vz << "m/s | vy="
                      << s_vuichard.vy << "m/s | Режим: "
                      << std::noshowpos << aero::regime_name(s_vuichard.regime) << "\n";
        }
    }

    return 0;
}
```
:::

---

### Динаміка стійкості, демпфування та аналіз результатів

1. **Інверсія аеродинамічного демпфування за вертикаллю (`Z_w`):**
   У нормальному режимі польоту вертикальне аеродинамічне демпфування `Z_w = ∂Z / ∂w` є строго від'ємним: будь-яке випадкове збільшення швидкості спуску збільшує кут атаки лопатей, збільшуючи тягу й автоматично гальмуючи падіння.
   У зоні вихорового кільця похідна `Z_w` змінює знак на додатний (`Z_w > 0`). Збільшення швидкості спуску посилює тороїдальну рециркуляцію, викликаючи додатковий зрив потоку й подальше падіння тяги. Апарат втрачає природну статичну стійкість за швидкістю спуску і самовільно розганяється вниз без жодного додаткового збурення.

2. **Фізична природа «залипання під тягою» (Settling with Power):**
   У першому сценарії апарат знаходиться у фазі спуску зі швидкістю `V_z = -3.2` м/с. На часовій мітці `t = 0.5` с пілот різко підвищує командну тягу на 40% (`1.40 · m·g`). В інтуїтивному уявленні це мало б дати вертикальне прискорення `a_z = +3.9` м/с² і зупинити спуск.
   Однак числовий розрахунок показує протилежне: збільшення командної тяги збільшує індуковану швидкість `v_i0`, через що безрозмірне відношення `V̂_z = V_z / v_i0` залишається строго в інтервалі максимальної рециркуляції (`V̂_z ≈ -1.0`). Падіння фактичної підіймальної сили на 35% нівелює додану потужність двигуна: апарат продовжує провалюватися вниз і за 3 секунди втрачає всю висоту.

3. **Динаміка порятунку маневром Вюішара:**
   У другому сценарії надання бічного імпульсу швидкості `V_y = 3.5` м/с миттєво переводить безрозмірну горизонтальну швидкість `V̂_x` вище одиниці (`V̂_x > 1.0`). Набігаючий потік здуває завихрення з площини диска, переводячи ротор у режим звичайного косого обдування. Ефективна тяга відновлюється до 100%, і апарат успішно гасить спуск на безпечній висоті `z ≈ 20.8` м, втративши лише 9.2 метра висоти від точки входу в маневр.

4. **Інженерні пастки при інтеграції в польотні контролери:**
   - **Стрибок барометра в зоні екрана землі:** при наближенні до поверхні (`h < 1.0·D`) надлишковий динамічний тиск створює хвилю стиснення в корпусі дрона. Якщо фільтр розширеного фільтра Калмана (EKF) не має підтримки оптичного потоку чи ультразвукового/лазерного далекоміра (LiDAR), барометр передає хибне повідомлення про «зниження нижче рівня землі», що змушує регулятор висоти глушити мотори на висоті пів метра над землею.
   - **Шум акселерометра в зоні VRS:** потужні періодичні зриви вихорів породжують вібрації на частотах обертання лопатей (`10...40` Гц для гелікоптерів, `100...300` Гц для мультикоптерів). Без адекватних цифрових режекторних фільтрів (Notch filters) цей шум насичує інтегральну складову PID-регулятора, викликаючи розгойдування та повну втрату орієнтації.
