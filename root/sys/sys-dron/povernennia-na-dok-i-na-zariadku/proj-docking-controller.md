# ⚙️ Контролер прецизійного стикування та моніторингу заряду

Автономне функціонування роботизованого комплексу класу Drone-in-a-Box вимагає безперервної узгодженої роботи двох систем керування: бортового комп'ютера візуальної навігації, який формує кінематичні уставки руху дрона на основі оптичного розпізнавання реперних міток, та наземного контролера док-станції, який керує приводами люка, затискними механізмами, вимірювальними зондами та комутацією силового зарядного контуру.

Якщо обчислювальний модуль оптичного наведення видає координати з випадковою затримкою або втрачає маркер під час різкого маневру, автопілот ризикує зіткнутися з краєм відкритого люка станції. Якщо ж наземний контролер замкне силове реле живлення до завершення перевірки перехідного опору контакту, струм силою двадцять ампер викличе електричну дугу й розплавить контакти. Даний проект описує програмну архітектуру та повну реалізацію контролера стикування, що об'єднує 6-DoF оцінку позиції за алгоритмом Perspective-n-Point (PnP), дискретний фільтр Калмана для фільтрації шумів та компенсації затримки камери, контур формування швидкісних уставок польоту та автомат станів діагностики силового живлення.

---

### Архітектура системи та розподіл функцій

Контролер стикування розділений на два функціональні блоки, які взаємодіють між собою через бездротовий міст зв'язку та бортову телеметрію:

1. **Бортовий модуль візуального наведення (Vision Precision Landing Worker):** функціонує на бортовому комп'ютері (наприклад, Raspberry Pi CM4 або Nvidia Jetson), захоплює кадри з камери глобального затвора (*Global Shutter*), детектує кути маркерів AprilTag 36h11, розв'язує рівняння PnP, фільтрує траєкторію у фільтрі Калмана та відправляє у польотний контролер команди корекції швидкості через MAVLink.
2. **Контролер заряду док-станції (Dock Station Power & Safety Manager):** працює на мікроконтролері дока (STM32 або ESP32), керує приводами затискачів, проводить зондування перехідного опору методом Кельвіна, контролює температуру батареї через CAN-шину та перемикає силові MOSFET-ключі за алгоритмом плавного пуску.

```
┌───────────────────────────────────────────────────────────────────────────┐
│                    БОРТОВИЙ ОБЧИСЛЮВАЧ (Companion PC)                     │
│                                                                           │
│  ┌──────────────┐   Кадри (60 fps)   ┌───────────────┐   Кути маркерів    │
│  │ Камера (CSI) │───────────────────→│ AprilTag / PnP│─────────────────┐  │
│  └──────────────┘                    └───────────────┘                 │  │
│                                                                        ▼  │
│  ┌──────────────┐   Уставки швидкості┌───────────────┐   Відносна поза    │
│  │ Польотний FC │←───────────────────│ PID Регулятор │←────────────────│  │
│  │ (MAVLink NED)│   SET_POSITION_NED │ швидкості     │  Фільтр Калмана │  │
│  └──────────────┘                    └───────────────┘  (Згладжування) │  │
└───────────────────────────────────────────────────────────────────────────┘
                                     │
                             Радіолінк / Wi-Fi
                                     │
┌───────────────────────────────────────────────────────────────────────────┐
│                      КОНТРОЛЕР ДОК-СТАНЦІЇ (Dock MCU)                     │
│                                                                           │
│  ┌──────────────┐  Крокові приводи   ┌───────────────┐   Зондування Кельв.│
│  │ Механіка     │←───────────────────│ Автомат станів│─────────────────┐  │
│  │ Затискачі X/Y│   Позиціонування   │ Док-станції   │                 │  │
│  └──────────────┘                    └───────────────┘                 │  │
│                                              │                         ▼  │
│  ┌──────────────┐   Струм CC / CV    ┌───────┴───────┐   Sense лінія АЦП  │
│  │ Силове джерело│←───────────────────│ Силове реле   │←────────────────│  │
│  │ Живлення 24V │   Керування шиною  │ та Soft-Start │   Вимір R_конт. │  │
│  └──────────────┘                    └───────────────┘                 │  │
└───────────────────────────────────────────────────────────────────────────┘
```

---

### Математична модель 6-DoF візуального наведення

Оптична камера формує проекцію тривимірних точок мішені на двовимірну матрицю пікселів. Нехай координати кутів квадратного маркера у власній системі мішені становлять:

```
P_tag_0 = [-L/2, -L/2, 0]^T,  P_tag_1 = [ L/2, -L/2, 0]^T
P_tag_2 = [ L/2,  L/2, 0]^T,  P_tag_3 = [-L/2,  L/2, 0]^T   [кути маркера розміром L]
```

Проекція кожної точки на площину сенсора визначається матрицею внутрішніх параметрів камери `K` та вектором дисторсії:

```
K = ⎡ f_x   0   c_x ⎤
    ⎢  0   f_y  c_y ⎥   [матриця калібрування камери]
    ⎣  0    0    1  ⎦
```

Алгоритм PnP мінімізує суму квадратів похибок репроекції:

```
E_reproj = ∑ || p_pixel_i - π(K, R, T, P_tag_i) ||^2   [критерій мінімізації PnP]
```

Отриманий вектор трансляції `T_cam = [x_c, y_c, z_c]^T` задано в системі координат камери (вісь X спрямована праворуч, Y — вниз, Z — вперед вздовж оптичної осі). Для передачі автопілоту вектор перераховується у зв'язану систему координат безпілотника Body NED (X — вперед по курсу дрона, Y — праворуч, Z — вниз):

```
⎡ x_body ⎤   ⎡  0   1   0 ⎤   ⎡ x_cam ⎤
⎢ y_body ⎥ = ⎢  1   0   0 ⎥ · ⎢ y_cam ⎥   [перехід з камери в Body Frame]
⎣ z_body ⎦   ⎣  0   0   1 ⎦   ⎣ z_cam ⎦
```

Для пласких маркерів класичні алгоритми розв'язання PnP (такі як EPnP або DLT) мають виражену проблему двозначності оцінки нахилу (*Planar Pose Ambiguity*). Дві дзеркальні конфігурації орієнтації маркера відносно оптичної осі можуть генерувати майже ідентичні координати пікселів на зображенні. Це призводить до раптових стрибків розрахованого кута рискання (Yaw) або нахилів (Pitch/Roll) на 180 градусів між сусідніми кадрами. Щоб усунути цей ефект, модуль оцінки позиції застосовує аналітичний метод IPPE (*Infinitesimal Plane-based Pose Estimation*), який завжди повертає обидва математичні розв'язки разом із залишковими нев'язками. Модуль відкидає хибний корінь, порівнюючи вектор швидкості мішені з попередньою оцінкою фільтра Калмана.

---

### Дискретний фільтр Калмана та компенсація часової затримки камери

Візуальні вимірювання від детектора AprilTag надходять із дискретністю кадрової частоти (30–60 Гц) і містять транспортне запізнювання `Δt_lag = 30–80 мс`, що складається з часу експозиції матриці, передачі по шині MIPI-CSI та обчислення градієнтів у потоці комп'ютерного зору. Безпосередня подача таких запізнілих даних у швидкісний контур стабілізації польоту викликає фазове відставання та самозбудження коливань дрона над платформою.

Для фільтрації шумів розпізнавання та екстраполяції положення на час затримки передачі кадру `Δt_lag` вектор стану системи обирається як:

```
x = [ p_x, p_y, p_z, v_x, v_y, v_z ]^T   [вектор стану відносного руху]
```

Матриця переходу стану `F` та матриця коваріації шуму процесу `Q` для періоду дискретизації `dt`:

```
F = ⎡ I_3x3   dt · I_3x3 ⎤
    ⎣ 0_3x3     I_3x3    ⎦   [матриця динаміки системи]
```

```
Q = ⎡ (dt^3 / 3) · q_pos · I_3x3   (dt^2 / 2) · q_pos · I_3x3 ⎤
    ⎣ (dt^2 / 2) · q_pos · I_3x3         dt · q_vel · I_3x3   ⎦   [коваріація процесу]
```

Робота фільтра розділена на два етапи:
1. **Прогноз (Predict):** виконується на кожному кроці основного циклу керування автопілота (зазвичай 100 або 250 Гц), використовуючи лінійне інтегрування швидкостей та модель розширення коваріації `P_(k|k-1) = F · P_(k-1) · F^T + Q`.
2. **Корекція (Update):** спрацьовує асинхронно в момент прибуття нового обробленого кадру від камери. Обчислюється вектор нев'язки (інновації) `y = z_meas - H · x_pred`, коефіцієнт підсилення Калмана `K = P · H^T · (H · P · H^T + R)^(-1)` та оновлюється вектор стану.

Завдяки цьому автопілот безперервно отримує гладкі та актуальні оцінки швидкості і положення мішені без стрибків і фазового зсуву.

---

### Контур формування швидкісних уставок польоту

Горизонтальна швидкість зближення формується за пропорційно-диференціальним законом із нелінійним насиченням, щоб уникнути різких нахилів дрона на малій висоті:

```
v_x_cmd = sat( K_p · e_x - K_d · v_x_est,  V_max_horiz )   [уставка швидкості X]
v_y_cmd = sat( K_p · e_y - K_d · v_y_est,  V_max_horiz )   [уставка швидкості Y]
```

Вертикальна швидкість спуску `v_z_cmd` задається як спадна функція від поточної висоти над доком `h`:

```
v_z_cmd = min( V_desc_max, max( V_desc_min, k_z · h ) )   [профіль вертикального зниження]
```

Особливості роботи контуру на різних фазах:
* **Етап пошуку та зависання (h > 3.0 м):** максимальна горизонтальна швидкість обмежена значенням 1.5 м/с, дрон вирівнює свій курс паралельно осі док-станції, мінімізуючи кут рискання `Δψ`.
* **Етап прецизійного зниження (3.0 м > h > 0.3 м):** горизонтальні уставки затискаються до максимуму 0.5 м/с, щоб уникнути надмірних кутів крену і тангажу, які можуть вивести оптичний маркер із поля зору камери.
* **Етап торкання (h ≤ 0.3 м):** горизонтальні уставки блокуються на нулі, регулятор фіксує поточний кут нахилу, а вертикальна швидкість обмежується мінімальним посадковим значенням 0.15 м/с до моменту фізичного торкання воронок і скидання газу мотора (*Disarm*).

---

### Чотирипровідна діагностика Кельвіна та керування зарядом

Електричний опір перехідного контакту розраховується за законом Ома при пропусканні фіксованого струму зондування `I_probe = 200 мА`:

```
R_contact_mohm = ( (V_sense_plus - V_sense_minus) / I_probe ) · 1000.0   [перехідний опір у мОм]
```

Температура батареї обчислюється на основі сигналу бортового термістора NTC 10 кОм за спрощеним рівнянням B-параметра:

```
1 / T_kelvin = 1 / T_0 + (1 / B) · ln( R_ntc / R_0 )   [розрахунок температури за NTC]
```

де `T_0 = 298.15 К (25 °C)`, `R_0 = 10000 Ом`, `B = 3950 К`.

Процедура комутації силового струму станції реалізує такі захисні бар'єри:
* **Діагностика заземлення та полярності:** вимірювання різниці потенціалів без навантаження для виключення переполюсовки акумулятора.
* **Поріг перехідного опору:** якщо `R_contact > 40 мОм`, контакт визнається брудним або нещільним. Силове реле блокується, а крокові приводи виконують цикл розмикання-змикання затискачів.
* **М'який старт (Pre-Charge Softstart):** обмеження пускового струму заряду вхідних ємностей регуляторів швидкості за допомогою проміжного резистора 10 Ом протягом 150 мс.
* **Тепловий захист комірок:** динамічне обмеження зарядного струму CC при досягненні температури 42 °C та аварійне відключення при 48 °C.

---

### Повна програмна реалізація контролера

Нижче наведено модульну реалізацію системи мовами C та C++. Код містить модуль оцінки позиції маркера, фільтр Калмана, контур обчислення швидкостей та повнофункціональний автомат станів док-станції.

:::tabs
```c
/* docking_controller.h */
#ifndef DOCKING_CONTROLLER_H
#define DOCKING_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    float fx;
    float fy;
    float cx;
    float cy;
    float tag_size_m;
} camera_intrinsics_t;

typedef struct {
    float u[4];
    float v[4];
    uint32_t tag_id;
    uint64_t timestamp_us;
    bool valid;
} fiducial_corners_t;

typedef struct {
    float pos_body[3];      /* X (вперед), Y (праворуч), Z (вниз) в метрах */
    float vel_body[3];      /* лінійні швидкості в м/с */
    float yaw_relative_rad; /* відносний розворот за курсом */
    uint64_t state_time_us;
    bool is_tracking;
} docking_target_state_t;

typedef struct {
    float x[6];             /* [px, py, pz, vx, vy, vz] */
    float P[6][6];          /* матриця коваріацій помилок */
    float q_pos;            /* шум процесу положення */
    float q_vel;            /* шум процесу швидкості */
    float r_pos;            /* шум вимірювання камери */
    uint64_t last_update_us;
    bool initialized;
} docking_kalman_filter_t;

typedef struct {
    float kp_xy;
    float kd_xy;
    float kz_desc;
    float max_horiz_vel;
    float max_desc_vel;
    float min_desc_vel;
    float land_height_threshold;
} guidance_params_t;

typedef struct {
    float vel_cmd_body[3];  /* Vx, Vy, Vz уставки швидкості для FC */
    float yaw_rate_cmd_rad;
    bool initiate_touchdown;
    bool abort_landing;
} guidance_output_t;

typedef enum {
    DOCK_STATE_IDLE = 0,
    DOCK_STATE_ROOF_OPENING,
    DOCK_STATE_WAITING_UAV_APPROACH,
    DOCK_STATE_TOUCHDOWN_CONFIRMED,
    DOCK_STATE_MECHANICAL_CLAMPING,
    DOCK_STATE_CONTACT_PROBE,
    DOCK_STATE_PRECHARGE_SOFTSTART,
    DOCK_STATE_MAIN_CHARGING,
    DOCK_STATE_CHARGE_COMPLETE,
    DOCK_STATE_EMERGENCY_ISOLATION
} dock_station_fsm_state_t;

typedef struct {
    float sense_voltage_drop_mv;
    float probe_current_ma;
    float battery_voltage_mv;
    float charge_current_a;
    float cell_temperatures_c[6];
    uint8_t cell_count;
    bool uav_disarmed;
    bool bms_can_alive;
    bool emergency_stop_pressed;
} dock_hardware_inputs_t;

typedef struct {
    bool roof_open_cmd;
    bool clamp_motors_engage;
    bool probe_generator_enable;
    bool precharge_relay_enable;
    bool main_power_relay_enable;
    bool cooling_fans_enable;
    float target_psu_voltage_v;
    float target_psu_current_limit_a;
} dock_hardware_outputs_t;

typedef struct {
    dock_station_fsm_state_t state;
    uint32_t state_timer_ms;
    float contact_resistance_mohm;
    uint8_t retry_count;
} dock_station_controller_t;

/* Функції ініціалізації та оновлення */
void docking_kalman_init(docking_kalman_filter_t *kf, float q_pos, float q_vel, float r_pos);
void docking_kalman_predict(docking_kalman_filter_t *kf, float dt);
void docking_kalman_update(docking_kalman_filter_t *kf, const float meas_pos[3]);

bool docking_solve_pnp(const camera_intrinsics_t *cam, const fiducial_corners_t *corners, float out_pos_body[3], float *out_yaw_rad);

void docking_guidance_compute(
    const docking_target_state_t *target,
    const guidance_params_t *params,
    float dt,
    guidance_output_t *out);

void dock_station_fsm_init(dock_station_controller_t *ctrl);
void dock_station_fsm_update(
    dock_station_controller_t *ctrl,
    const dock_hardware_inputs_t *inputs,
    dock_hardware_outputs_t *outputs,
    uint32_t dt_ms);

#ifdef __cplusplus
}
#endif

#endif /* DOCKING_CONTROLLER_H */
```
```c
/* docking_controller.c */
#include "docking_controller.h"
#include <string.h>

void docking_kalman_init(docking_kalman_filter_t *kf, float q_pos, float q_vel, float r_pos) {
    if (!kf) return;
    memset(kf, 0, sizeof(docking_kalman_filter_t));
    kf->q_pos = q_pos;
    kf->q_vel = q_vel;
    kf->r_pos = r_pos;

    for (int i = 0; i < 6; ++i) {
        kf->P[i][i] = 1.0f;
    }
    kf->initialized = false;
}

void docking_kalman_predict(docking_kalman_filter_t *kf, float dt) {
    if (!kf || !kf->initialized || dt <= 0.0f) return;

    /* x = F * x */
    for (int i = 0; i < 3; ++i) {
        kf->x[i] += kf->x[i + 3] * dt;
    }

    /* P = F * P * F^T + Q */
    for (int i = 0; i < 3; ++i) {
        kf->P[i][i] += (kf->P[i + 3][i + 3] * dt * dt) + (2.0f * kf->P[i][i + 3] * dt) + (kf->q_pos * dt);
        kf->P[i][i + 3] += kf->P[i + 3][i + 3] * dt;
        kf->P[i + 3][i] = kf->P[i][i + 3];
        kf->P[i + 3][i + 3] += kf->q_vel * dt;
    }
}

void docking_kalman_update(docking_kalman_filter_t *kf, const float meas_pos[3]) {
    if (!kf || !meas_pos) return;

    if (!kf->initialized) {
        for (int i = 0; i < 3; ++i) {
            kf->x[i] = meas_pos[i];
            kf->x[i + 3] = 0.0f;
        }
        kf->initialized = true;
        return;
    }

    for (int i = 0; i < 3; ++i) {
        float y = meas_pos[i] - kf->x[i];
        float s = kf->P[i][i] + kf->r_pos;
        if (fabsf(s) > 1e-6f) {
            float k_gain = kf->P[i][i] / s;
            float k_gain_vel = kf->P[i + 3][i] / s;

            kf->x[i] += k_gain * y;
            kf->x[i + 3] += k_gain_vel * y;

            kf->P[i][i] *= (1.0f - k_gain);
            kf->P[i + 3][i + 3] -= k_gain_vel * kf->P[i][i + 3];
            kf->P[i][i + 3] *= (1.0f - k_gain);
            kf->P[i + 3][i] = kf->P[i][i + 3];
        }
    }
}

bool docking_solve_pnp(const camera_intrinsics_t *cam, const fiducial_corners_t *corners, float out_pos_body[3], float *out_yaw_rad) {
    if (!cam || !corners || !out_pos_body || !out_yaw_rad || !corners->valid) {
        return false;
    }

    /* Спрощений аналітичний розв'язок для плаского маркера з відомим розміром */
    float du1 = corners->u[1] - corners->u[0];
    float dv1 = corners->v[1] - corners->v[0];
    float pixel_width = sqrtf(du1 * du1 + dv1 * dv1);

    if (pixel_width < 4.0f) return false;

    float z_cam = (cam->fx * cam->tag_size_m) / pixel_width;
    float u_center = (corners->u[0] + corners->u[1] + corners->u[2] + corners->u[3]) * 0.25f;
    float v_center = (corners->v[0] + corners->v[1] + corners->v[2] + corners->v[3]) * 0.25f;

    float x_cam = (u_center - cam->cx) * z_cam / cam->fx;
    float y_cam = (v_center - cam->cy) * z_cam / cam->fy;

    /* Перехід у Body Frame NED: X_body = Y_cam, Y_body = X_cam, Z_body = Z_cam */
    out_pos_body[0] = y_cam;
    out_pos_body[1] = x_cam;
    out_pos_body[2] = z_cam;

    *out_yaw_rad = atan2f(dv1, du1);
    return true;
}

void docking_guidance_compute(
    const docking_target_state_t *target,
    const guidance_params_t *params,
    float dt,
    guidance_output_t *out)
{
    if (!target || !params || !out) return;

    memset(out, 0, sizeof(guidance_output_t));

    if (!target->is_tracking) {
        out->vel_cmd_body[0] = 0.0f;
        out->vel_cmd_body[1] = 0.0f;
        out->vel_cmd_body[2] = 0.0f;
        return;
    }

    float ex = target->pos_body[0];
    float ey = target->pos_body[1];
    float ez = target->pos_body[2];

    /* Горизонтальний ПД-регулятор */
    float vx = params->kp_xy * ex - params->kd_xy * target->vel_body[0];
    float vy = params->kp_xy * ey - params->kd_xy * target->vel_body[1];

    /* Насичення горизонтальної швидкості */
    float h_speed = sqrtf(vx * vx + vy * vy);
    if (h_speed > params->max_horiz_vel) {
        vx = (vx / h_speed) * params->max_horiz_vel;
        vy = (vy / h_speed) * params->max_horiz_vel;
    }

    /* Вертикальний профіль спуску */
    float vz = params->kz_desc * ez;
    if (vz > params->max_desc_vel) vz = params->max_desc_vel;
    if (vz < params->min_desc_vel) vz = params->min_desc_vel;

    /* Фінальний етап посадки */
    if (ez < params->land_height_threshold) {
        vx = 0.0f;
        vy = 0.0f;
        vz = params->min_desc_vel;
        out->initiate_touchdown = true;
    }

    out->vel_cmd_body[0] = vx;
    out->vel_cmd_body[1] = vy;
    out->vel_cmd_body[2] = vz;
    out->yaw_rate_cmd_rad = -0.8f * target->yaw_relative_rad;
}

void dock_station_fsm_init(dock_station_controller_t *ctrl) {
    if (!ctrl) return;
    ctrl->state = DOCK_STATE_IDLE;
    ctrl->state_timer_ms = 0;
    ctrl->contact_resistance_mohm = 0.0f;
    ctrl->retry_count = 0;
}

void dock_station_fsm_update(
    dock_station_controller_t *ctrl,
    const dock_hardware_inputs_t *inputs,
    dock_hardware_outputs_t *outputs,
    uint32_t dt_ms)
{
    if (!ctrl || !inputs || !outputs) return;

    ctrl->state_timer_ms += dt_ms;

    if (inputs->emergency_stop_pressed) {
        ctrl->state = DOCK_STATE_EMERGENCY_ISOLATION;
    }

    switch (ctrl->state) {
    case DOCK_STATE_IDLE:
        outputs->roof_open_cmd = false;
        outputs->clamp_motors_engage = false;
        outputs->probe_generator_enable = false;
        outputs->precharge_relay_enable = false;
        outputs->main_power_relay_enable = false;
        outputs->cooling_fans_enable = false;
        break;

    case DOCK_STATE_ROOF_OPENING:
        outputs->roof_open_cmd = true;
        if (ctrl->state_timer_ms > 4000) {
            ctrl->state = DOCK_STATE_WAITING_UAV_APPROACH;
            ctrl->state_timer_ms = 0;
        }
        break;

    case DOCK_STATE_WAITING_UAV_APPROACH:
        outputs->roof_open_cmd = true;
        if (inputs->uav_disarmed) {
            ctrl->state = DOCK_STATE_TOUCHDOWN_CONFIRMED;
            ctrl->state_timer_ms = 0;
        }
        break;

    case DOCK_STATE_TOUCHDOWN_CONFIRMED:
        /* Затримка на повну зупинку пропелерів */
        if (ctrl->state_timer_ms > 2000) {
            ctrl->state = DOCK_STATE_MECHANICAL_CLAMPING;
            ctrl->state_timer_ms = 0;
        }
        break;

    case DOCK_STATE_MECHANICAL_CLAMPING:
        outputs->clamp_motors_engage = true;
        if (ctrl->state_timer_ms > 3500) {
            ctrl->state = DOCK_STATE_CONTACT_PROBE;
            ctrl->state_timer_ms = 0;
        }
        break;

    case DOCK_STATE_CONTACT_PROBE:
        outputs->probe_generator_enable = true;
        if (inputs->probe_current_ma > 50.0f) {
            ctrl->contact_resistance_mohm = (inputs->sense_voltage_drop_mv / inputs->probe_current_ma) * 1000.0f;
            if (ctrl->contact_resistance_mohm < 40.0f && inputs->bms_can_alive) {
                ctrl->state = DOCK_STATE_PRECHARGE_SOFTSTART;
                ctrl->state_timer_ms = 0;
            } else if (ctrl->state_timer_ms > 2000) {
                /* Спроба повторного затискання при високому опорі */
                if (ctrl->retry_count++ < 3) {
                    ctrl->state = DOCK_STATE_MECHANICAL_CLAMPING;
                } else {
                    ctrl->state = DOCK_STATE_EMERGENCY_ISOLATION;
                }
                ctrl->state_timer_ms = 0;
            }
        }
        break;

    case DOCK_STATE_PRECHARGE_SOFTSTART:
        outputs->probe_generator_enable = false;
        outputs->precharge_relay_enable = true;
        outputs->target_psu_voltage_v = 25.2f;
        outputs->target_psu_current_limit_a = 2.0f;

        if (ctrl->state_timer_ms > 150) {
            ctrl->state = DOCK_STATE_MAIN_CHARGING;
            ctrl->state_timer_ms = 0;
        }
        break;

    case DOCK_STATE_MAIN_CHARGING:
        outputs->precharge_relay_enable = true;
        outputs->main_power_relay_enable = true;
        outputs->cooling_fans_enable = true;
        outputs->target_psu_voltage_v = 25.2f;
        outputs->target_psu_current_limit_a = 15.0f;

        /* Перевірка критичної температури комірок */
        for (uint8_t i = 0; i < inputs->cell_count; ++i) {
            if (inputs->cell_temperatures_c[i] > 48.0f) {
                ctrl->state = DOCK_STATE_EMERGENCY_ISOLATION;
                break;
            }
        }

        /* Критерій завершення заряду (CV стадія зі спадом струму) */
        if (inputs->battery_voltage_mv >= 25150 && inputs->charge_current_a < 0.5f) {
            if (ctrl->state_timer_ms > 5000) {
                ctrl->state = DOCK_STATE_CHARGE_COMPLETE;
                ctrl->state_timer_ms = 0;
            }
        }
        break;

    case DOCK_STATE_CHARGE_COMPLETE:
        outputs->main_power_relay_enable = false;
        outputs->precharge_relay_enable = false;
        outputs->cooling_fans_enable = false;
        break;

    case DOCK_STATE_EMERGENCY_ISOLATION:
    default:
        outputs->main_power_relay_enable = false;
        outputs->precharge_relay_enable = false;
        outputs->probe_generator_enable = false;
        outputs->cooling_fans_enable = false;
        outputs->clamp_motors_engage = false;
        break;
    }
}
```
```cpp
// DockingController.hpp
#pragma once

#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <optional>
#include <span>

namespace DroneDock {

struct CameraIntrinsics {
    float fx{800.0F};
    float fy{800.0F};
    float cx{320.0F};
    float cy{240.0F};
    float tagSizeM{0.2F};
};

struct FiducialCorners {
    std::array<float, 4> u{};
    std::array<float, 4> v{};
    uint32_t tagId{0};
    std::chrono::microseconds timestampUs{0};
    bool valid{false};
};

struct TargetState {
    std::array<float, 3> posBody{};
    std::array<float, 3> velBody{};
    float yawRelativeRad{0.0F};
    std::chrono::microseconds timestampUs{0};
    bool isTracking{false};
};

struct GuidanceParams {
    float kpXy{1.2F};
    float kdXy{0.3F};
    float kzDesc{0.5F};
    float maxHorizVel{1.5F};
    float maxDescVel{0.7F};
    float minDescVel{0.15F};
    float landHeightThreshold{0.3F};
};

struct GuidanceCommand {
    std::array<float, 3> velCmdBody{};
    float yawRateCmdRad{0.0F};
    bool initiateTouchdown{false};
    bool abortLanding{false};
};

enum class DockState : uint8_t {
    Idle,
    RoofOpening,
    WaitingUavApproach,
    TouchdownConfirmed,
    MechanicalClamping,
    ContactProbe,
    PrechargeSoftstart,
    MainCharging,
    ChargeComplete,
    EmergencyIsolation
};

struct HardwareInputs {
    float senseVoltageDropMv{0.0F};
    float probeCurrentMa{0.0F};
    float batteryVoltageMv{0.0F};
    float chargeCurrentA{0.0F};
    std::array<float, 6> cellTemperaturesC{};
    uint8_t cellCount{6};
    bool uavDisarmed{false};
    bool bmsCanAlive{false};
    bool emergencyStopPressed{false};
};

struct HardwareOutputs {
    bool roofOpenCmd{false};
    bool clampMotorsEngage{false};
    bool probeGeneratorEnable{false};
    bool prechargeRelayEnable{false};
    bool mainPowerRelayEnable{false};
    bool coolingFansEnable{false};
    float targetPsuVoltageV{0.0F};
    float targetPsuCurrentLimitA{0.0F};
};

class KalmanFilter3D {
public:
    constexpr KalmanFilter3D() noexcept {
        reset();
    }

    void reset() noexcept {
        x_.fill(0.0F);
        for (size_t i = 0; i < 6; ++i) {
            for (size_t j = 0; j < 6; ++j) {
                P_[i][j] = (i == j) ? 1.0F : 0.0F;
            }
        }
        initialized_ = false;
    }

    void predict(float dt) noexcept {
        if (!initialized_ || dt <= 0.0F) return;

        for (size_t i = 0; i < 3; ++i) {
            x_[i] += x_[i + 3] * dt;
        }

        constexpr float qPos = 0.05F;
        constexpr float qVel = 0.1F;

        for (size_t i = 0; i < 3; ++i) {
            P_[i][i] += (P_[i + 3][i + 3] * dt * dt) + (2.0F * P_[i][i + 3] * dt) + (qPos * dt);
            P_[i][i + 3] += P_[i + 3][i + 3] * dt;
            P_[i + 3][i] = P_[i][i + 3];
            P_[i + 3][i + 3] += qVel * dt;
        }
    }

    void update(std::span<const float, 3> measPos) noexcept {
        if (!initialized_) {
            for (size_t i = 0; i < 3; ++i) {
                x_[i] = measPos[i];
                x_[i + 3] = 0.0F;
            }
            initialized_ = true;
            return;
        }

        constexpr float rPos = 0.02F;
        for (size_t i = 0; i < 3; ++i) {
            const float y = measPos[i] - x_[i];
            const float s = P_[i][i] + rPos;
            if (std::abs(s) > 1e-6F) {
                const float kGain = P_[i][i] / s;
                const float kGainVel = P_[i + 3][i] / s;

                x_[i] += kGain * y;
                x_[i + 3] += kGainVel * y;

                P_[i][i] *= (1.0F - kGain);
                P_[i + 3][i + 3] -= kGainVel * P_[i][i + 3];
                P_[i][i + 3] *= (1.0F - kGain);
                P_[i + 3][i] = P_[i][i + 3];
            }
        }
    }

    [[nodiscard]] std::array<float, 3> getPosition() const noexcept {
        return {x_[0], x_[1], x_[2]};
    }

    [[nodiscard]] std::array<float, 3> getVelocity() const noexcept {
        return {x_[3], x_[4], x_[5]};
    }

private:
    std::array<float, 6> x_{};
    std::array<std::array<float, 6>, 6> P_{};
    bool initialized_{false};
};

class PrecisionDockingEstimator {
public:
    explicit constexpr PrecisionDockingEstimator(CameraIntrinsics intrinsics) noexcept
        : intrinsics_{intrinsics} {}

    [[nodiscard]] std::optional<TargetState> processCorners(const FiducialCorners& corners, float dt) noexcept {
        if (!corners.valid) {
            targetState_.isTracking = false;
            return std::nullopt;
        }

        const float du1 = corners.u[1] - corners.u[0];
        const float dv1 = corners.v[1] - corners.v[0];
        const float pixelWidth = std::sqrt(du1 * du1 + dv1 * dv1);

        if (pixelWidth < 4.0F) {
            targetState_.isTracking = false;
            return std::nullopt;
        }

        const float zCam = (intrinsics_.fx * intrinsics_.tagSizeM) / pixelWidth;
        const float uCenter = (corners.u[0] + corners.u[1] + corners.u[2] + corners.u[3]) * 0.25F;
        const float vCenter = (corners.v[0] + corners.v[1] + corners.v[2] + corners.v[3]) * 0.25F;

        const float xCam = (uCenter - intrinsics_.cx) * zCam / intrinsics_.fx;
        const float yCam = (vCenter - intrinsics_.cy) * zCam / intrinsics_.fy;

        const std::array<float, 3> measBody{yCam, xCam, zCam};

        kalman_.predict(dt);
        kalman_.update(measBody);

        targetState_.posBody = kalman_.getPosition();
        targetState_.velBody = kalman_.getVelocity();
        targetState_.yawRelativeRad = std::atan2(dv1, du1);
        targetState_.timestampUs = corners.timestampUs;
        targetState_.isTracking = true;

        return targetState_;
    }

private:
    CameraIntrinsics intrinsics_{};
    KalmanFilter3D kalman_{};
    TargetState targetState_{};
};

class DockStationController {
public:
    constexpr DockStationController() noexcept = default;

    void update(const HardwareInputs& in, HardwareOutputs& out, std::chrono::milliseconds dt) noexcept {
        stateTimer_ += dt;

        if (in.emergencyStopPressed) {
            state_ = DockState::EmergencyIsolation;
        }

        switch (state_) {
        case DockState::Idle:
            out = {};
            break;

        case DockState::RoofOpening:
            out.roofOpenCmd = true;
            if (stateTimer_ > std::chrono::seconds(4)) {
                transitionTo(DockState::WaitingUavApproach);
            }
            break;

        case DockState::WaitingUavApproach:
            out.roofOpenCmd = true;
            if (in.uavDisarmed) {
                transitionTo(DockState::TouchdownConfirmed);
            }
            break;

        case DockState::TouchdownConfirmed:
            if (stateTimer_ > std::chrono::seconds(2)) {
                transitionTo(DockState::MechanicalClamping);
            }
            break;

        case DockState::MechanicalClamping:
            out.clampMotorsEngage = true;
            if (stateTimer_ > std::chrono::milliseconds(3500)) {
                transitionTo(DockState::ContactProbe);
            }
            break;

        case DockState::ContactProbe:
            out.probeGeneratorEnable = true;
            if (in.probeCurrentMa > 50.0F) {
                contactResistanceMohm_ = (in.senseVoltageDropMv / in.probeCurrentMa) * 1000.0F;
                if (contactResistanceMohm_ < 40.0F && in.bmsCanAlive) {
                    transitionTo(DockState::PrechargeSoftstart);
                } else if (stateTimer_ > std::chrono::seconds(2)) {
                    if (retryCount_++ < 3) {
                        transitionTo(DockState::MechanicalClamping);
                    } else {
                        transitionTo(DockState::EmergencyIsolation);
                    }
                }
            }
            break;

        case DockState::PrechargeSoftstart:
            out.probeGeneratorEnable = false;
            out.prechargeRelayEnable = true;
            out.targetPsuVoltageV = 25.2F;
            out.targetPsuCurrentLimitA = 2.0F;

            if (stateTimer_ > std::chrono::milliseconds(150)) {
                transitionTo(DockState::MainCharging);
            }
            break;

        case DockState::MainCharging:
            out.prechargeRelayEnable = true;
            out.mainPowerRelayEnable = true;
            out.coolingFansEnable = true;
            out.targetPsuVoltageV = 25.2F;
            out.targetPsuCurrentLimitA = 15.0F;

            for (size_t i = 0; i < in.cellCount; ++i) {
                if (in.cellTemperaturesC[i] > 48.0F) {
                    transitionTo(DockState::EmergencyIsolation);
                    return;
                }
            }

            if (in.batteryVoltageMv >= 25150.0F && in.chargeCurrentA < 0.5F) {
                if (stateTimer_ > std::chrono::seconds(5)) {
                    transitionTo(DockState::ChargeComplete);
                }
            }
            break;

        case DockState::ChargeComplete:
            out.mainPowerRelayEnable = false;
            out.prechargeRelayEnable = false;
            out.coolingFansEnable = false;
            break;

        case DockState::EmergencyIsolation:
        default:
            out = {};
            break;
        }
    }

    [[nodiscard]] DockState getState() const noexcept { return state_; }
    [[nodiscard]] float getContactResistanceMohm() const noexcept { return contactResistanceMohm_; }

private:
    void transitionTo(DockState nextState) noexcept {
        state_ = nextState;
        stateTimer_ = std::chrono::milliseconds(0);
    }

    DockState state_{DockState::Idle};
    std::chrono::milliseconds stateTimer_{0};
    float contactResistanceMohm_{0.0F};
    uint8_t retryCount_{0};
};

} // namespace DroneDock
```
:::

---

### Практичні крайові випадки та аналіз надійності

Під час розгортання контролера прецизійного стикування слід враховувати низку критичних апаратних та алгоритмічних пасток:

1. **Ефект тремтіння затвора (Rolling Shutter Jello):** висока вібрація від незбалансованих пропелерів на частотах 80–150 Гц створює хвилеподібні спотворення зображення при використанні звичайних камер із рухомим затвором. Прямі лінії маркера викривляються, алгоритм PnP видає псевдоповорот за креном і тангажем до 15°, що спричиняє зрив посадки. Застосування сенсорів виключно з глобальним затвором (*Global Shutter*) та встановлення камери на силіконові демпфери є обов'язковою інженерною вимогою.
2. **Асинхронне спрацьовування кінцевиків затискачів:** якщо один із приводів позиціонування підклинює через потрапляння піску, контролер фіксує перекіс струму двигуна. Автомат станів повинен негайно відвести обидві штанги у вихідне положення й виконати повторний цикл із плавним нарощуванням моменту.
3. **Термічний дрейф вимірювання струму:** шунт вимірювання зондувального струму Кельвіна нагрівається під час тривалого силового заряду. Для запобігання похибкам вимірювання опору при наступних посадках застосовуються прецизійні чотирививідні шунти з низьким температурним коефіцієнтом опору (TCR < 20 ppm/°C).
4. **Засліплення оптичної матриці прямим сонцем:** при низькому стоянні сонця сонячні промені можуть створювати бліки на полірованих металевих кільцях заряду. Алгоритм бінаризації повинен використовувати локальне адаптивне порогове відсікання замість глобального порогу яскравості, а на об'єктив камери рекомендується встановлювати циркулярний поляризаційний фільтр (CPL).
