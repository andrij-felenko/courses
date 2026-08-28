# ⚙️ Розрахунок уставки посадки за PnP-вектором маркера

Цей алгоритмічний модуль перетворює сирий вектор просторового положення візуального маркера, отриманий від PnP-розв'язувача камери, на безпечну уставку тривимірної швидкості та швидкості гарчання для польотного контролера безпілотника. Без цього проміжного контуру пряме подавання зміщення в контур керування спричиняє розгойдування апарата через затримку обробки зображення, втрату маркера з поля зору під час нахилу проти вітру або небезпечне падіння повз зону безпечного конуса посадки.

## Архітектура контуру наведення та обробки даних

Навігаційна камера глобального затвора (*global shutter*), спрямована вертикально в надир, захоплює кадри з фіксованою частотою 30–60 Гц. Процесор комп'ютерного зору (бортовий комп'ютер класу Raspberry Pi CM4, Jetson Orin Nano або STM32H7) виконує конвеєр розпізнавання: детектування 4 субпіксельних кутів мітки, зчитування бінарного коду та розв'язання задачі Perspective-n-Point. На виході PnP формується вектор трансляції `t_cam = [x_c, y_c, z_c]^T` та матриця орієнтації `R_mc` маркера відносно камери.

Сирі оптичні дані не можна транслювати безпосередньо в регулятори тяги двигунів. Контролер посадки виконує багаторівневу обробку:

```
       [Камера] → PnP (t_cam, R_mc)
           │
           ▼
[Extrinsics: t_b = R_cb · t_c + t_cb]
           │
           ▼
[Компенсація затримки: t_est = t_b - v_b · Δt_lat]
           │
           ▼
[Вибір активного маркера та зсув ΔX, ΔY]
           │
           ▼
[Перевірка конуса Landing Cone: r_xy ≤ k_cone·h + r_0]
           │
           ├── [Поза конусом] ───► v_z = 0 (зависання й центрування)
           │
           └── [Всередині] ──────► v_z = k_z · h (контрольований спуск)
           │
           ▼
[PI-регулятор швидкості v_xy з Anti-Windup]
           │
           ▼
[MAVLink SET_POSITION_TARGET_LOCAL_NED] → Польотний контролер
```

1. **Перетворення координат (Extrinsics):** узгодження оптичної системи координат камери (`X_c` — праворуч, `Y_c` — вниз, `Z_c` — уперед уздовж оптичної осі) з навігаційною системою корпусу дрона (`Body NED: X_b` — уперед, `Y_b` — праворуч, `Z_b` — вниз).
2. **Компенсація затримки конвеєра (Pipeline Latency):** експозиція кадру, передача по шині CSI/USB, робота нейромережі чи PnP-алгоритму створюють затримку `Δt_lat ≈ 30–80` мс. За цей час дрон зміщується у просторі. Алгоритм екстраполює координати вперед за поточною швидкістю з бортового фільтра EKF.
3. **Узгодження ієрархії міток (Handover Offset):** якщо на док-станції встановлено вкладену систему маркерів, внутрішній мікромаркер може бути геометрично зміщений відносно центру посадкового гнізда на вектор `[ΔX, ΔY]`. Алгоритм вводить відповідну поправку при перемиканні джерела.
4. **Обмеження конусом безпеки (Landing Cone):** вертикальне зниження блокується, якщо горизонтальне відхилення перевищує допустимий радіус на поточній висоті. Це виключає спуск під гострим кутом, що веде до вильоту маркера з поля зору.
5. **PI-регулювання з анти-віндапом:** інтегральний канал компенсує постійний вітровий дрейф, а обмеження інтегратора усуває перерегулювання.

## Повний код модуля розрахунку уставки

Нижче наведено самодостатню реалізацію модуля на мовах C та C++.

:::tabs
```c
#include <math.h>
#include <stdbool.h>
#include <stdint.h>

#define MARKER_TIMEOUT_SEC     0.4f
#define MAX_HORIZONTAL_VEL     1.5f   /* м/с */
#define MAX_VERTICAL_VEL       0.8f   /* м/с */
#define MIN_VERTICAL_VEL       0.15f  /* м/с */
#define CONE_SLOPE             0.45f  /* тангенс кута напівконуса посадки (≈24°) */
#define MIN_CONE_RADIUS        0.06f  /* мінімальний радіус біля землі, м */

typedef struct {
    float x;
    float y;
    float z;
} Vector3f;

typedef struct {
    float kp_xy;
    float ki_xy;
    float kd_xy;
    float kp_z;
    float i_limit_xy;
    float cam_to_body_r[3][3]; /* матриця повороту камери відносно корпусу */
    Vector3f cam_to_body_t;    /* зміщення камери відносно центру мас, м */
} PrecisionLandingConfig;

typedef struct {
    Vector3f integral_err;
    Vector3f prev_body_err;
    float last_detection_time;
    uint32_t active_marker_id;
    bool is_tracking;
} PrecisionLandingState;

typedef struct {
    Vector3f vel_setpoint_body; /* уставка швидкості в Body NED (м/с) */
    float yaw_rate_setpoint;    /* уставка швидкості гарчання (рад/с) */
    bool descent_allowed;       /* дозвіл на вертикальне зниження */
    bool touchdown_ready;       /* готовність до відсікання двигунів */
} LandingSetpointOutput;

/* Ініціалізація стану контролера */
void landing_control_init(PrecisionLandingState *state)
{
    state->integral_err.x = 0.0f;
    state->integral_err.y = 0.0f;
    state->integral_err.z = 0.0f;
    state->prev_body_err.x = 0.0f;
    state->prev_body_err.y = 0.0f;
    state->prev_body_err.z = 0.0f;
    state->last_detection_time = 0.0f;
    state->active_marker_id = 0;
    state->is_tracking = false;
}

/* Обмеження скалярного значення в діапазоні [min_v, max_v] */
static inline float clampf(float val, float min_v, float max_v)
{
    if (val < min_v) return min_v;
    if (val > max_v) return max_v;
    return val;
}

/* Перетворення вектора з системи камери в систему корпусу: v_b = R_cb * v_c + t_cb */
static Vector3f transform_camera_to_body(const Vector3f *v_cam,
                                         const PrecisionLandingConfig *cfg)
{
    Vector3f v_body;
    v_body.x = cfg->cam_to_body_r[0][0] * v_cam->x +
               cfg->cam_to_body_r[0][1] * v_cam->y +
               cfg->cam_to_body_r[0][2] * v_cam->z + cfg->cam_to_body_t.x;

    v_body.y = cfg->cam_to_body_r[1][0] * v_cam->x +
               cfg->cam_to_body_r[1][1] * v_cam->y +
               cfg->cam_to_body_r[1][2] * v_cam->z + cfg->cam_to_body_t.y;

    v_body.z = cfg->cam_to_body_r[2][0] * v_cam->x +
               cfg->cam_to_body_r[2][1] * v_cam->y +
               cfg->cam_to_body_r[2][2] * v_cam->z + cfg->cam_to_body_t.z;
    return v_body;
}

/* Головна функція такту керування посадкою */
bool landing_control_update(const PrecisionLandingConfig *cfg,
                            PrecisionLandingState *state,
                            const Vector3f *pos_cam,
                            float marker_yaw_cam,
                            uint32_t marker_id,
                            const Vector3f *marker_offset_body,
                            const Vector3f *cur_body_vel,
                            float latency_sec,
                            float current_time,
                            float dt,
                            LandingSetpointOutput *out)
{
    if (dt <= 0.0f || dt > 0.2f) {
        return false;
    }

    bool fresh_detection = (pos_cam != NULL);

    if (fresh_detection) {
        state->last_detection_time = current_time;
        state->active_marker_id = marker_id;
        state->is_tracking = true;
    } else if (current_time - state->last_detection_time > MARKER_TIMEOUT_SEC) {
        state->is_tracking = false;
        out->vel_setpoint_body.x = 0.0f;
        out->vel_setpoint_body.y = 0.0f;
        out->vel_setpoint_body.z = 0.0f;
        out->yaw_rate_setpoint = 0.0f;
        out->descent_allowed = false;
        out->touchdown_ready = false;
        return false;
    }

    Vector3f target_body;
    if (fresh_detection) {
        /* 1. Переведення в систему корпусу */
        Vector3f raw_body = transform_camera_to_body(pos_cam, cfg);

        /* 2. Врахування зміщення вкладеного маркера відносно головного центру дока */
        if (marker_offset_body != NULL) {
            raw_body.x -= marker_offset_body->x;
            raw_body.y -= marker_offset_body->y;
        }

        /* 3. Компенсація затримки передачі кадру через одометрію тіла */
        target_body.x = raw_body.x - cur_body_vel->x * latency_sec;
        target_body.y = raw_body.y - cur_body_vel->y * latency_sec;
        target_body.z = raw_body.z - cur_body_vel->z * latency_sec;
        state->prev_body_err = target_body;
    } else {
        /* Екстраполяція позиції за відсутності свіжого кадру */
        target_body.x = state->prev_body_err.x - cur_body_vel->x * dt;
        target_body.y = state->prev_body_err.y - cur_body_vel->y * dt;
        target_body.z = state->prev_body_err.z - cur_body_vel->z * dt;
        state->prev_body_err = target_body;
    }

    /* Помилка позиціонування: вектор від дрона до маркера (уперед/праворуч/униз) */
    float err_x = target_body.x;
    float err_y = target_body.y;
    float altitude = target_body.z; /* відстань по вертикалі до маркера (м) */

    float horiz_dist = sqrtf(err_x * err_x + err_y * err_y);
    float cone_radius = altitude * CONE_SLOPE + MIN_CONE_RADIUS;

    /* Перевірка перебування всередині конуса безпеки */
    bool inside_cone = (horiz_dist <= cone_radius);
    out->descent_allowed = inside_cone;

    /* Інтегрування горизонтальної помилки для парирування вітру */
    state->integral_err.x += err_x * dt;
    state->integral_err.y += err_y * dt;
    state->integral_err.x = clampf(state->integral_err.x, -cfg->i_limit_xy, cfg->i_limit_xy);
    state->integral_err.y = clampf(state->integral_err.y, -cfg->i_limit_xy, cfg->i_limit_xy);

    /* Розрахунок горизонтальних уставок швидкості */
    float cmd_vx = cfg->kp_xy * err_x + cfg->ki_xy * state->integral_err.x;
    float cmd_vy = cfg->kp_xy * err_y + cfg->ki_xy * state->integral_err.y;

    out->vel_setpoint_body.x = clampf(cmd_vx, -MAX_HORIZONTAL_VEL, MAX_HORIZONTAL_VEL);
    out->vel_setpoint_body.y = clampf(cmd_vy, -MAX_HORIZONTAL_VEL, MAX_HORIZONTAL_VEL);

    /* Розрахунок вертикальної швидкості */
    if (inside_cone && altitude > 0.05f) {
        float vz_cmd = cfg->kp_z * altitude;
        out->vel_setpoint_body.z = clampf(vz_cmd, MIN_VERTICAL_VEL, MAX_VERTICAL_VEL);
    } else {
        /* Зупинка зниження для центрування */
        out->vel_setpoint_body.z = 0.0f;
    }

    /* Розрахунок кута розвороту за маркером */
    if (fresh_detection) {
        out->yaw_rate_setpoint = clampf(0.8f * marker_yaw_cam, -0.5f, 0.5f);
    } else {
        out->yaw_rate_setpoint = 0.0f;
    }

    /* Критерій фінального торкання (Touchdown) */
    out->touchdown_ready = (altitude < 0.12f) && (horiz_dist < 0.04f);

    return true;
}
```
```cpp
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <optional>

namespace precision_landing {

struct Vector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] constexpr Vector3f operator+(const Vector3f& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    [[nodiscard]] constexpr Vector3f operator-(const Vector3f& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
    [[nodiscard]] constexpr Vector3f operator*(float s) const noexcept {
        return {x * s, y * s, z * s};
    }
    [[nodiscard]] float norm_xy() const noexcept {
        return std::sqrt(x * x + y * y);
    }
};

struct Config {
    float kp_xy{1.1f};
    float ki_xy{0.25f};
    float kd_xy{0.05f};
    float kp_z{0.45f};
    float i_limit_xy{0.6f};
    float cone_slope{0.45f};
    float min_cone_radius{0.06f};
    float max_horizontal_vel{1.5f};
    float max_vertical_vel{0.8f};
    float min_vertical_vel{0.15f};
    float marker_timeout_sec{0.4f};
    std::array<std::array<float, 3>, 3> cam_to_body_r{
        std::array<float, 3>{0.0f, 1.0f, 0.0f},
        std::array<float, 3>{1.0f, 0.0f, 0.0f},
        std::array<float, 3>{0.0f, 0.0f, 1.0f}
    };
    Vector3f cam_to_body_t{0.05f, 0.0f, 0.08f};
};

struct MarkerMeasurement {
    Vector3f pos_camera;
    float yaw_camera_rad{0.0f};
    uint32_t marker_id{0};
    Vector3f offset_in_dock_body{0.0f, 0.0f, 0.0f};
};

struct ControllerOutput {
    Vector3f vel_setpoint_body;
    float yaw_rate_setpoint{0.0f};
    bool descent_allowed{false};
    bool touchdown_ready{false};
};

class LandingGuidanceController {
public:
    explicit LandingGuidanceController(Config config) noexcept
        : cfg_(config) {}

    void reset() noexcept {
        integral_err_ = {0.0f, 0.0f, 0.0f};
        prev_body_err_ = {0.0f, 0.0f, 0.0f};
        last_detection_time_ = 0.0f;
        active_marker_id_ = 0;
        is_tracking_ = false;
    }

    [[nodiscard]] std::optional<ControllerOutput> update(
        const std::optional<MarkerMeasurement>& marker_meas,
        const Vector3f& current_body_vel,
        float latency_sec,
        float current_time_sec,
        float dt_sec) noexcept
    {
        if (dt_sec <= 0.0f || dt_sec > 0.2f) {
            return std::nullopt;
        }

        if (marker_meas.has_value()) {
            last_detection_time_ = current_time_sec;
            active_marker_id_ = marker_meas->marker_id;
            is_tracking_ = true;
        } else if (current_time_sec - last_detection_time_ > cfg_.marker_timeout_sec) {
            is_tracking_ = false;
            return std::nullopt;
        }

        Vector3f target_body{};
        float yaw_cam = 0.0f;

        if (marker_meas.has_value()) {
            Vector3f raw_body = transform_cam_to_body(marker_meas->pos_camera);
            raw_body.x -= marker_meas->offset_in_dock_body.x;
            raw_body.y -= marker_meas->offset_in_dock_body.y;

            target_body = raw_body - (current_body_vel * latency_sec);
            prev_body_err_ = target_body;
            yaw_cam = marker_meas->yaw_camera_rad;
        } else {
            target_body = prev_body_err_ - (current_body_vel * dt_sec);
            prev_body_err_ = target_body;
        }

        const float err_x = target_body.x;
        const float err_y = target_body.y;
        const float altitude = target_body.z;
        const float horiz_dist = std::sqrt(err_x * err_x + err_y * err_y);
        const float cone_radius = altitude * cfg_.cone_slope + cfg_.min_cone_radius;

        const bool inside_cone = (horiz_dist <= cone_radius);

        integral_err_.x = std::clamp(integral_err_.x + err_x * dt_sec,
                                     -cfg_.i_limit_xy, cfg_.i_limit_xy);
        integral_err_.y = std::clamp(integral_err_.y + err_y * dt_sec,
                                     -cfg_.i_limit_xy, cfg_.i_limit_xy);

        ControllerOutput out{};
        out.descent_allowed = inside_cone;

        const float cmd_vx = cfg_.kp_xy * err_x + cfg_.ki_xy * integral_err_.x;
        const float cmd_vy = cfg_.kp_xy * err_y + cfg_.ki_xy * integral_err_.y;

        out.vel_setpoint_body.x = std::clamp(cmd_vx, -cfg_.max_horizontal_vel, cfg_.max_horizontal_vel);
        out.vel_setpoint_body.y = std::clamp(cmd_vy, -cfg_.max_horizontal_vel, cfg_.max_horizontal_vel);

        if (inside_cone && altitude > 0.05f) {
            const float vz_cmd = cfg_.kp_z * altitude;
            out.vel_setpoint_body.z = std::clamp(vz_cmd, cfg_.min_vertical_vel, cfg_.max_vertical_vel);
        } else {
            out.vel_setpoint_body.z = 0.0f;
        }

        if (marker_meas.has_value()) {
            out.yaw_rate_setpoint = std::clamp(0.8f * yaw_cam, -0.5f, 0.5f);
        } else {
            out.yaw_rate_setpoint = 0.0f;
        }

        out.touchdown_ready = (altitude < 0.12f) && (horiz_dist < 0.04f);

        return out;
    }

    [[nodiscard]] bool is_tracking() const noexcept { return is_tracking_; }
    [[nodiscard]] uint32_t active_marker_id() const noexcept { return active_marker_id_; }

private:
    [[nodiscard]] Vector3f transform_cam_to_body(const Vector3f& v_cam) const noexcept {
        return {
            cfg_.cam_to_body_r[0][0] * v_cam.x + cfg_.cam_to_body_r[0][1] * v_cam.y +
            cfg_.cam_to_body_r[0][2] * v_cam.z + cfg_.cam_to_body_t.x,

            cfg_.cam_to_body_r[1][0] * v_cam.x + cfg_.cam_to_body_r[1][1] * v_cam.y +
            cfg_.cam_to_body_r[1][2] * v_cam.z + cfg_.cam_to_body_t.y,

            cfg_.cam_to_body_r[2][0] * v_cam.x + cfg_.cam_to_body_r[2][1] * v_cam.y +
            cfg_.cam_to_body_r[2][2] * v_cam.z + cfg_.cam_to_body_t.z
        };
    }

    Config cfg_;
    Vector3f integral_err_{0.0f, 0.0f, 0.0f};
    Vector3f prev_body_err_{0.0f, 0.0f, 0.0f};
    float last_detection_time_{0.0f};
    uint32_t active_marker_id_{0};
    bool is_tracking_{false};
};

} // namespace precision_landing
```
:::

## Покроковий числовий розрахунок одного такту

Розглянемо числовий приклад розрахунку на реальних фізичних величинах.

Нехай апарат перебуває на висоті близько 4 метрів і спускається до док-станції. Вхідні параметри такту:
- Виміряний PnP-вектор у системі камери: `pos_cam = [ -0.25,  0.40,  4.20 ]^T` (метри);
- Поточна швидкість дрона в системі тіла: `cur_body_vel = [ 0.30, -0.15, 0.40 ]^T` (м/с);
- Затримка конвеєра комп'ютерного зору: `latency_sec = 0.06` с (60 мс);
- Крок квантування часу: `dt = 0.02` с (50 Гц);
- Накопичена інтегральна похибка на попередньому кроці: `integral_err = [ 0.12, -0.05 ]^T`;
- Коефіцієнти регулятора: `kp_xy = 1.1`, `ki_xy = 0.25`, `kp_z = 0.45`, `cone_slope = 0.45`, `min_cone_radius = 0.06`.

**Крок 1. Перетворення в систему корпусу (Extrinsics).**
Матриця `R_cb` перетворює оптичні осі: `X_b = Y_c`, `Y_b = X_c`, `Z_b = Z_c`. Додаємо конструктивне зміщення об'єктива `t_cb = [0.05, 0.00, 0.08]`:
```
raw_body.x = 0.40 + 0.05 = 0.45 м
raw_body.y = -0.25 + 0.00 = -0.25 м
raw_body.z = 4.20 + 0.08 = 4.28 м
```

**Крок 2. Компенсація затримки (Dead-Reckoning).**
Віднімаємо зміщення, яке дрон пройшов за час формування кадру:
```
target_body.x = 0.45 - (0.30 · 0.06) = 0.45 - 0.018 = 0.432 м
target_body.y = -0.25 - (-0.15 · 0.06) = -0.25 + 0.009 = -0.241 м
target_body.z = 4.28 - (0.40 · 0.06) = 4.28 - 0.024 = 4.256 м
```

**Крок 3. Перевірка конуса безпеки Landing Cone.**
```
horiz_dist = √( 0.432² + (-0.241)² )
           = √( 0.1866 + 0.0581 )
           = √0.2447
           ≈ 0.495 м

cone_radius = 4.256 · 0.45 + 0.06
            = 1.915 + 0.06
            = 1.975 м
```
Оскільки `horiz_dist = 0.495 м ≤ 1.975 м`, апарат перебуває глибоко всередині безпечного конуса (`descent_allowed = true`).

**Крок 4. Розрахунок інтегральної складової та уставок швидкості.**
Оновлюємо інтегратор похибки:
```
integral_err.x = 0.12 + 0.432 · 0.02 = 0.12 + 0.0086 = 0.1286
integral_err.y = -0.05 + (-0.241) · 0.02 = -0.05 - 0.0048 = -0.0548
```
Формуємо команди швидкості для польотного контролера:
```
cmd_vx = 1.1 · 0.432 + 0.25 · 0.1286 = 0.475 + 0.032 = 0.507 м/с (вперед)
cmd_vy = 1.1 · (-0.241) + 0.25 · (-0.0548) = -0.265 - 0.014 = -0.279 м/с (вліво)
cmd_vz = 0.45 · 4.256 = 1.915 м/с  →  обмежується стелею MAX_VERTICAL_VEL = 0.80 м/с
```

Сформований вектор швидкості `v_cmd = [0.507, -0.279, 0.800]^T` надсилається в шину польотного контролера.

## Інженерні пастки та крайові випадки

1. **Неузгодженість знаків систем координат.** Оптична вісь камери спрямована вперед (`Z_cam` додатний у бік об'єкта), тоді як у системі навігації NED вісь вниз позначається як `Z_ned`. Помилка в орієнтації матриці `R_cb` перетворює зниження на зліт у стелю або реверсує команди крену й тангажу.
2. **Накопичення інтеграла під час підходу здалеку (Integrator Windup).** Якщо інтегратор вітрової помилки ввімкнений на етапі горизонтального підльоту (коли дрон ще на висоті 15 м бореться з початковим зміщенням 3 м), значення інтегральної суми досягає максимуму. При вході в конус посадки дрон за інерцією пролітає повз маркер у протилежний бік. Обмежувач `i_limit_xy` та занулення інтегратора до входу в конус усувають перерегулювання.
3. **Ігнорування затримки сенсора (Pipeline Latency).** При швидкості зміщення 1 м/с затримка обробки кадру 60 мс зміщує оцінку на 6 см. Без екстраполяції положення зворотний зв'язок втрачає фазовий запас стійкості, викликаючи стійкий автоколивальний автопілотаж над маркером на частоті 1.5–3 Гц.
4. **Короткочасне затінення пропелерами чи стійками.** Під час різких поривів вітру маркер може випасти з кадру на 1–2 кадри (20–40 мс). Тайм-аут `MARKER_TIMEOUT_SEC = 0.4` с дозволяє контролеру продовжувати плавне гальмування за інерцією на основі одометрії IMU, не перериваючи посадку аварійним зависанням при одиночних пропусках детекції.
5. **Інтеграція з MAVLink.** На польотний контролер (ArduPilot або PX4) вихідний вектор транслюється через повідомлення `SET_POSITION_TARGET_LOCAL_NED` (ID 84) з бітовою маскою швидкостей `type_mask = 0b0000111111000111` (ігнорувати положення та прискорення, керувати лише 3D-швидкістю та швидкістю гарчання Yaw Rate).
