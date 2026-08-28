# ⚙️ Вбудований балістичний калькулятор скиду вантажу для автопілота

Точний скид вантажу в задану наземну ціль вимагає від польотного контролера безперервного прогнозування точки падіння з урахуванням швидкості носія, барометричної та рельєфної висоти, швидкості й напрямку вітру, а також апаратної затримки спрацьовування замка. Якщо виконувати повне чисельне моделювання на кожній ітерації основного циклу стабілізації (400–1000 Гц), процесор буде перевантажений. Тому балістичний калькулятор виділяють в окрему задачу з частотою оновлення 10–25 Гц, яка працює виключно зі статично виділеною пам'яттю і детермінованим часом виконання.

Нижче наведено робочу реалізацію балістичного модуля для вбудованих систем на C та C++, яка розраховує траєкторію методом Рунге-Кутти 4-го порядку (RK4), знаходить точку відкриття замка за алгоритмом CCRP (Constantly Computed Release Point) та формує сигнал прямої компенсації тяги двигунів (Throttle Feed-Forward).

## Архітектура балістичного модуля та потік даних

Модуль спроектований як детермінований обчислювальний блок реального часу, інтегрований у проміжне програмне забезпечення польотного контролера (middleware). Потік обробки даних організований за наступною схемою:

```
 ┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
 │ GNSS + EKF Навігація │   │ Барометр + Далекомір │   │ Оцінка вітру EKF     │
 │ Позиція (x, y, z)    │   │ Висота цілі z_target │   │ Вектор (w_x, w_y, 0) │
 └──────────┬───────────┘   └──────────┬───────────┘   └──────────┬───────────┘
            │                          │                          │
            └──────────────────────────┼──────────────────────────┘
                                       ▼
                       ┌───────────────────────────────┐
                       │ Задача балістики (10–25 Гц)   │
                       │ 1. Інтегрування RK4           │
                       │ 2. Обчислення вектора CCRP    │
                       │ 3. Перевірка воріт скиду      │
                       └───────────────┬───────────────┘
                                       │
                                       ▼
                       ┌───────────────────────────────┐
                       │ Видача команд:                │
                       │ - Сигнал на замок (GPIO/ШІМ)  │
                       │ - Throttle Feed-Forward       │
                       │ - MAVLink телеметрія          │
                       └───────────────────────────────┘
```

Модуль складається з трьох ключових блоків:

1. **Балістичний інтегратор (RK4):** приймає початковий стан БПЛА (тривимірні координати, вектор швидкості в системі NED — North-East-Down), параметри вантажу (масу, коефіцієнт лобового опору `C_d`, площу міделя `A`) та оцінку вітру. Інтегрує рівняння руху до перетину площини цілі `z = z_target` з фіксованим кроком `dt = 0.05` с.
2. **Калькулятор точки скиду (CCRP):** віднімає вектор балістичного виносу `Δ_drop` та відстань, пройдену за час спрацьовування замка `V · Δt_actuator`, від координат цілі. Обчислює горизонтальну дистанцію до лінії скиду та час до скиду (Time-to-Release, TTR).
3. **Компенсатор динамічного розвантаження:** генерує команду миттєвого зниження базового газу автопілота на частку `m_drop / M_total` одночасно з імпульсом активації замка.

## Часовий бюджет і навантаження на процесор (ARM Cortex-M4 / M7)

Для вбудованих мікроконтролерів без апаратної підтримки подвійної точності (FP64) або з обмеженою тактовою частотою (наприклад, STM32F405 на 168 МГц) критично важливо, щоб усі операції виконувалися в одинарній точності (`float32`).

Один повний прогін інтегратора RK4 на 150 кроків (що відповідає 7.5 секундам вільного падіння вантажу з висоти 250 м) потребує:
- 150 кроків × 4 обчислення похідних = 600 викликів векторної фізичної моделі;
- Кожен виклик містить одне обчислення квадратного кореня `sqrtf` (апаратна інструкція `VSQRT.F32` на Cortex-M4 виконується за 14 тактів) та 12 операцій множення-додавання (`VFMA.F32` виконується за 1 такт);
- Сумарний час виконання повного балістичного розрахунку на ядрі STM32F4 становить близько `180–240 мікросекунд`.

При частоті виклику задачі 20 Гц балістичний калькулятор споживає менше `0.5%` сумарного процесорного часу мікроконтролера, що дозволяє виконувати його паралельно з основними контурами кутової стабілізації та навігації.

## Реалізація балістичного калькулятора (C / C++)

:::tabs
```c
#include <stdbool.h>
#include <math.h>

#define MAX_BALLISTIC_STEPS 300
#define GRAVITY_MSS 9.80665f
#define AIR_DENSITY_KG_M3 1.225f

typedef struct {
    float x; // North (м)
    float y; // East (м)
    float z; // Down (м, додатне значення — вниз)
} Vec3f;

typedef struct {
    float mass_kg;
    float cd;
    float area_m2;
} PayloadSpec;

typedef struct {
    Vec3f pos;
    Vec3f vel;
} KinematicState;

typedef struct {
    Vec3f wind_vel; // Швидкість вітру (North, East, Down = 0)
    float target_z; // Висота площини скиду / цілі (Down)
    float actuator_delay_s; // Затримка серво/соленоїда (с)
} EnvironmentParams;

typedef struct {
    Vec3f impact_pos;     // Точка торкання поверхні цілі
    Vec3f release_offset; // Вектор виносу скиду від точки скиду до цілі
    float time_of_fall_s; // Час падіння вантажу
    float ttr_s;          // Час до перетину лінії скиду (Time-to-Release)
    float dist_to_rel_m;  // Горизонтальна відстань до точки скиду
    bool  in_release_gate;// Чи перебуває апарат у вікні скиду
} CcrpResult;

static inline Vec3f vec3_add(Vec3f a, Vec3f b) {
    return (Vec3f){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline Vec3f vec3_sub(Vec3f a, Vec3f b) {
    return (Vec3f){a.x - b.x, a.y - b.y, a.z - b.z};
}

static inline Vec3f vec3_scale(Vec3f v, float k) {
    return (Vec3f){v.x * k, v.y * k, v.z * k};
}

static inline float vec3_norm(Vec3f v) {
    return sqrtf(v.x * v.x + v.y * v.y + v.z * v.z);
}

// Похідні стану для інтегратора: d(pos)/dt = vel, d(vel)/dt = g - drag_accel
static void state_derivative(const KinematicState *state, const PayloadSpec *spec,
                             const Vec3f *wind, KinematicState *deriv) {
    deriv->pos = state->vel;

    Vec3f v_rel = vec3_sub(state->vel, *wind);
    float speed_rel = vec3_norm(v_rel);

    // k_drag = (1/2) * rho * C_d * A / m
    float k_drag = 0.5f * AIR_DENSITY_KG_M3 * spec->cd * spec->area_m2 / spec->mass_kg;
    float drag_factor = k_drag * speed_rel;

    deriv->vel.x = -drag_factor * v_rel.x;
    deriv->vel.y = -drag_factor * v_rel.y;
    deriv->vel.z = GRAVITY_MSS - drag_factor * v_rel.z;
}

// Чисельне інтегрування траєкторії падіння вантажу методом RK4
bool ballistic_calculate_impact(const KinematicState *uav_state,
                                const PayloadSpec *spec,
                                const EnvironmentParams *env,
                                Vec3f *out_impact,
                                float *out_tof) {
    KinematicState cur = *uav_state;
    float dt = 0.05f;
    float t = 0.0f;

    if (cur.pos.z >= env->target_z) {
        return false; // БПЛА нижче або на рівні цілі
    }

    for (int step = 0; step < MAX_BALLISTIC_STEPS; ++step) {
        KinematicState prev = cur;
        float prev_t = t;

        // Рунге-Кутта 4-го порядку (RK4)
        KinematicState k1, k2, k3, k4, temp;

        state_derivative(&cur, spec, &env->wind_vel, &k1);

        temp.pos = vec3_add(cur.pos, vec3_scale(k1.pos, dt * 0.5f));
        temp.vel = vec3_add(cur.vel, vec3_scale(k1.vel, dt * 0.5f));
        state_derivative(&temp, spec, &env->wind_vel, &k2);

        temp.pos = vec3_add(cur.pos, vec3_scale(k2.pos, dt * 0.5f));
        temp.vel = vec3_add(cur.vel, vec3_scale(k2.vel, dt * 0.5f));
        state_derivative(&temp, spec, &env->wind_vel, &k3);

        temp.pos = vec3_add(cur.pos, vec3_scale(k3.pos, dt));
        temp.vel = vec3_add(cur.vel, vec3_scale(k3.vel, dt));
        state_derivative(&temp, spec, &env->wind_vel, &k4);

        cur.pos.x += (dt / 6.0f) * (k1.pos.x + 2.0f * k2.pos.x + 2.0f * k3.pos.x + k4.pos.x);
        cur.pos.y += (dt / 6.0f) * (k1.pos.y + 2.0f * k2.pos.y + 2.0f * k3.pos.y + k4.pos.y);
        cur.pos.z += (dt / 6.0f) * (k1.pos.z + 2.0f * k2.pos.z + 2.0f * k3.pos.z + k4.pos.z);

        cur.vel.x += (dt / 6.0f) * (k1.vel.x + 2.0f * k2.vel.x + 2.0f * k3.vel.x + k4.vel.x);
        cur.vel.y += (dt / 6.0f) * (k1.vel.y + 2.0f * k2.vel.y + 2.0f * k3.vel.y + k4.vel.y);
        cur.vel.z += (dt / 6.0f) * (k1.vel.z + 2.0f * k2.vel.z + 2.0f * k3.vel.z + k4.vel.z);

        t += dt;

        // Перевірка досягнення площини поверхні цілі
        if (cur.pos.z >= env->target_z) {
            float dz = cur.pos.z - prev.pos.z;
            float ratio = (fabsf(dz) > 1e-4f) ? (env->target_z - prev.pos.z) / dz : 1.0f;

            out_impact->x = prev.pos.x + ratio * (cur.pos.x - prev.pos.x);
            out_impact->y = prev.pos.y + ratio * (cur.pos.y - prev.pos.y);
            out_impact->z = env->target_z;
            *out_tof = prev_t + ratio * dt;
            return true;
        }
    }

    return false; // Вичерпано ліміт кроків інтегратора
}

// Розрахунок параметрів точки скиду CCRP
bool ccrp_evaluate(const KinematicState *uav,
                   const Vec3f *target_pos,
                   const PayloadSpec *spec,
                   const EnvironmentParams *env,
                   float gate_radius_m,
                   CcrpResult *res) {
    Vec3f impact;
    float tof = 0.0f;

    if (!ballistic_calculate_impact(uav, spec, env, &impact, &tof)) {
        return false;
    }

    res->impact_pos = impact;
    res->time_of_fall_s = tof;

    // Вектор балістичного зміщення від поточної точки БПЛА до розрахункового падіння
    res->release_offset = vec3_sub(impact, uav->pos);

    // Урахування апаратної затримки відкриття замка
    Vec3f actuator_lead = vec3_scale(uav->vel, env->actuator_delay_s);
    Vec3f total_lead = vec3_add(res->release_offset, actuator_lead);

    // Розрахункова точка, в якій має перебувати БПЛА для скиду
    Vec3f ideal_release_pos = (Vec3f){
        target_pos->x - total_lead.x,
        target_pos->y - total_lead.y,
        uav->pos.z
    };

    // Вектор відстані від БПЛА до точки скиду
    Vec3f to_release = vec3_sub(ideal_release_pos, uav->pos);
    float dist_h = sqrtf(to_release.x * to_release.x + to_release.y * to_release.y);
    res->dist_to_rel_m = dist_h;

    // Проекція швидкості на лінію до точки скиду
    float ground_speed = sqrtf(uav->vel.x * uav->vel.x + uav->vel.y * uav->vel.y);
    if (ground_speed > 0.5f) {
        float dot = (to_release.x * uav->vel.x + to_release.y * uav->vel.y) / ground_speed;
        res->ttr_s = dot / ground_speed;
    } else {
        res->ttr_s = 999.0f;
    }

    // Перевірка перебування у вікні скиду
    res->in_release_gate = (dist_h <= gate_radius_m) && (res->ttr_s >= -0.1f && res->ttr_s <= 0.15f);

    return true;
}

// Розрахунок зрізу тяги під час скидання 30–50% MTOW
float calculate_throttle_feedforward(float hover_throttle, float uav_mass_kg, float payload_mass_kg) {
    if (uav_mass_kg <= payload_mass_kg || uav_mass_kg <= 0.1f) {
        return hover_throttle;
    }
    float mass_ratio = (uav_mass_kg - payload_mass_kg) / uav_mass_kg;
    return hover_throttle * mass_ratio;
}
```
```cpp
#include <array>
#include <cmath>
#include <expected>
#include <numbers>

namespace avionics::ballistics {

inline constexpr float Gravity = 9.80665f;
inline constexpr float AirDensity = 1.225f;
inline constexpr std::size_t MaxBallisticSteps = 300;

enum class CalculationError {
    BelowTargetElevation,
    StepLimitExceeded,
    InvalidMass
};

struct Vector3D {
    float x{0.0f}; // North (м)
    float y{0.0f}; // East (м)
    float z{0.0f}; // Down (м, додатне вниз)

    constexpr Vector3D operator+(const Vector3D& rhs) const noexcept {
        return {x + rhs.x, y + rhs.y, z + rhs.z};
    }
    constexpr Vector3D operator-(const Vector3D& rhs) const noexcept {
        return {x - rhs.x, y - rhs.y, z - rhs.z};
    }
    constexpr Vector3D operator*(float scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }
    [[nodiscard]] float norm() const noexcept {
        return std::sqrt(x * x + y * y + z * z);
    }
    [[nodiscard]] float horizontal_norm() const noexcept {
        return std::sqrt(x * x + y * y);
    }
};

struct PayloadProfile {
    float mass_kg{1.5f};
    float drag_coefficient{0.45f};
    float cross_section_area_m2{0.007f};
};

struct KinematicState {
    Vector3D position;
    Vector3D velocity;
};

struct Environment {
    Vector3D wind_velocity; // Вітер (North, East, Down)
    float target_elevation_down{0.0f};
    float actuator_latency_s{0.10f};
};

struct CcrpSolution {
    Vector3D impact_point;
    Vector3D release_offset;
    float time_of_fall_s{0.0f};
    float time_to_release_s{0.0f};
    float distance_to_release_m{0.0f};
    bool is_in_release_gate{false};
};

class BallisticCalculator {
public:
    [[nodiscard]] static std::expected<std::pair<Vector3D, float>, CalculationError>
    integrate_trajectory(const KinematicState& initial,
                         const PayloadProfile& payload,
                         const Environment& env,
                         float dt = 0.05f) noexcept {
        if (initial.position.z >= env.target_elevation_down) {
            return std::unexpected(CalculationError::BelowTargetElevation);
        }

        KinematicState state = initial;
        float time_elapsed = 0.0f;

        const float k_drag = 0.5f * AirDensity * payload.drag_coefficient *
                             payload.cross_section_area_m2 / payload.mass_kg;

        auto compute_deriv = [&](const KinematicState& s) noexcept -> KinematicState {
            const Vector3D v_rel = s.velocity - env.wind_velocity;
            const float speed_rel = v_rel.norm();
            const float factor = k_drag * speed_rel;
            return {
                s.velocity,
                {
                    -factor * v_rel.x,
                    -factor * v_rel.y,
                    Gravity - factor * v_rel.z
                }
            };
        };

        for (std::size_t step = 0; step < MaxBallisticSteps; ++step) {
            const KinematicState prev_state = state;
            const float prev_t = time_elapsed;

            // RK4 інтегрування
            const auto k1 = compute_deriv(state);
            const auto k2 = compute_deriv({state.position + k1.position * (dt * 0.5f),
                                           state.velocity + k1.velocity * (dt * 0.5f)});
            const auto k3 = compute_deriv({state.position + k2.position * (dt * 0.5f),
                                           state.velocity + k2.velocity * (dt * 0.5f)});
            const auto k4 = compute_deriv({state.position + k3.position * dt,
                                           state.velocity + k3.velocity * dt});

            state.position = state.position +
                (k1.position + k2.position * 2.0f + k3.position * 2.0f + k4.position) * (dt / 6.0f);
            state.velocity = state.velocity +
                (k1.velocity + k2.velocity * 2.0f + k3.velocity * 2.0f + k4.velocity) * (dt / 6.0f);

            time_elapsed += dt;

            // Перетин площини рельєфу цілі
            if (state.position.z >= env.target_elevation_down) {
                const float dz = state.position.z - prev_state.position.z;
                const float ratio = (std::abs(dz) > 1e-4f)
                    ? (env.target_elevation_down - prev_state.position.z) / dz
                    : 1.0f;

                const Vector3D impact{
                    prev_state.position.x + ratio * (state.position.x - prev_state.position.x),
                    prev_state.position.y + ratio * (state.position.y - prev_state.position.y),
                    env.target_elevation_down
                };
                return std::make_pair(impact, prev_t + ratio * dt);
            }
        }

        return std::unexpected(CalculationError::StepLimitExceeded);
    }

    [[nodiscard]] static std::expected<CcrpSolution, CalculationError>
    compute_ccrp(const KinematicState& uav,
                 const Vector3D& target_ground,
                 const PayloadProfile& payload,
                 const Environment& env,
                 float gate_radius_m = 4.0f) noexcept {
        auto trajectory_res = integrate_trajectory(uav, payload, env);
        if (!trajectory_res) {
            return std::unexpected(trajectory_res.error());
        }

        const auto& [impact, tof] = *trajectory_res;
        CcrpSolution solution;
        solution.impact_point = impact;
        solution.time_of_fall_s = tof;
        solution.release_offset = impact - uav.position;

        // Врахування апаратного запізнення
        const Vector3D actuator_lead = uav.velocity * env.actuator_latency_s;
        const Vector3D total_lead = solution.release_offset + actuator_lead;

        const Vector3D ideal_release{
            target_ground.x - total_lead.x,
            target_ground.y - total_lead.y,
            uav.position.z
        };

        const Vector3D to_release = ideal_release - uav.position;
        solution.distance_to_release_m = to_release.horizontal_norm();

        const float ground_speed = uav.velocity.horizontal_norm();
        if (ground_speed > 0.5f) {
            const float dot = (to_release.x * uav.velocity.x + to_release.y * uav.velocity.y) / ground_speed;
            solution.time_to_release_s = dot / ground_speed;
        } else {
            solution.time_to_release_s = 999.0f;
        }

        solution.is_in_release_gate = (solution.distance_to_release_m <= gate_radius_m) &&
                                      (solution.time_to_release_s >= -0.1f && solution.time_to_release_s <= 0.15f);

        return solution;
    }

    // Компенсація стрибка тяги при скиданні 30–50% маси
    [[nodiscard]] static constexpr float
    compensate_throttle(float current_hover_throttle,
                        float total_mass_kg,
                        float dropped_mass_kg) noexcept {
        if (total_mass_kg <= dropped_mass_kg || total_mass_kg <= 0.1f) {
            return current_hover_throttle;
        }
        return current_hover_throttle * ((total_mass_kg - dropped_mass_kg) / total_mass_kg);
    }
};

} // namespace avionics::ballistics
```
:::

## Інтеграція з протоколом MAVLink та апаратними таймерами

У реальних польотних контролерах (на базі стеку ArduPilot або PX4) балістичний модуль взаємодіє з навігаційним сервером через внутрішні шини обміну повідомленнями (наприклад, uORB у PX4).

Спрацьовування замка ініціюється командою `MAV_CMD_DO_SET_SERVO` (для сервоприводів) або `MAV_CMD_DO_SET_RELAY` (для соленоїдів та MOSFET-ключів). У момент скиду модуль формує розширене телеметричне повідомлення, що транслюється на наземну станцію керування:
- Поточні розраховані координати точки падіння `P_impact`;
- Оцінена радіальна похибка `dist_to_rel_m`;
- Прапорець активації скидання та стан зворотного зв'язку кінцевого вимикача замка (Limit switch feedback).

Якщо механізм скиду обладнаний мікроперемикачем підтвердження виходу штифта, таймер автопілота вимірює реальний інтервал між подачею логічного сигналу і механічним розмиканням. Якщо виміряний час перевищує допустимий поріг (наприклад, > 250 мс), контролер генерує подію `PAYLOAD_RELEASE_STALL`, сигналізуючи про заклинювання штифта або знос редуктора.

## Інженерні пастки та крайові випадки

1. **Нелінійність барометричного вимірювання біля землі:**
   При наближенні до рельєфу повітряні хвилі від роторів створюють локальну зону підвищеного статичного тиску («екранний ефект»). Якщо висота цілі `z_target` обчислюється виключно за бортовим барометром без лазерного далекоміра (LiDAR) або GNSS RTK, помилка оцінки висоти скиду може сягати 2–4 метрів, що дає поздовжній промах у 3–6 метрів.
2. **Апаратна затримка замка при низьких температурах:**
   Змазка в редукторі сервоприводу гусне за температури нижче `-10 °C`. Час відкриття штифта зростає зі штатних 100 мс до 250–350 мс. На швидкості польоту 20 м/с це створює непоправний переліт цілі на 3–5 метрів, якщо затримка `actuator_delay_s` жорстко зашита сталою константою.
3. **Зсув вітру в ярах та біля лісосмуг:**
   Оцінка вітру, отримана польотним контролером на висоті 100 м (наприклад, 8 м/с), не діє в приземному 10-метровому шарі, де вітер гаситься перешкодами до 1–2 м/с. Застосування постійного вектора вітру по всій висоті призводить до перекомпенсації та зносу вантажу в навітряний бік.
4. **Скид у маневрі пікірування або кабрування:**
   Якщо носій має ненульову вертикальну швидкість `V_z` (наприклад, апарат знижується зі швидкістю 3 м/с), час падіння скорочується, а початковий вектор імпульсу спрямований під кутом до горизонту. Спрощені двовимірні калькулятори, які розраховують час падіння лише за висотою `h`, у такій ситуації дають помилку дальності до 10–18 метрів.
