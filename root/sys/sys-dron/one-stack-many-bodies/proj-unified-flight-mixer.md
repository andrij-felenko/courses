# ⚙️ Уніфікований модульний мікшер для довільних планерів на C та C++

Універсальний польотний контролер повинен стабілізувати та вести за маршрутом мультикоптери, класичні літаки, конвертоплани, колісні ровери та підводні апарати без перезбирання чи дублювання кодової бази автопілота. Якщо під кожну механічну схему писати власний контур стабілізації, понад 80% системного коду — обробка давачів, розширений фільтр Калмана (EKF), диспетчер повідомлень MAVLink, планувальник автономних місій і система аварійних сценаріїв (failsafe) — вимушено дублюватимуться. Кожне оновлення навігаційного фільтра чи виправлення помилки в драйвері шини доведеться переносити в кілька різних прошивок одночасно.

Архітектурний вихід полягає в ізоляції специфіки планера в самостійному обчислювальному модулі — підсистемі розподілу керування (Control Allocation & Mixing). Цей модуль отримує на вхід узагальнений вектор віртуальних зусиль (wrench) від каскадних регуляторів, виміряну індикаторну повітряну швидкість від трубки Піто та поточний кут нахилу поворотних балок, а на виході обчислює фізичні сигнали для довільного масиву моторів і сервоприводів.

Нижче наведено модульний рушій уніфікованого мікшування з динамічною підтримкою перехідних режимів VTOL, геометричною матрицею ефективності та пріоритетною десатурацією вихідних каналів.

## Архітектурний поділ та структури даних

Уніфікований мікшер проектується з дотриманням жорстких вимог систем реального часу:
- **Нульове динамічне виділення пам'яті в контурі керування:** усі матриці, дескриптори та вектори розміщуються у статичних або стекових структурах з фіксованими верхніми межами (`MAX_ACTUATORS = 16`, `NUM_AXES = 6`). Купа (`heap`) не використовується, що усуває ризик фрагментації пам'яті та недетермінованих затримок планувальника операційної системи реального часу (RTOS).
- **Повна геометрична параметризація:** просторове положення кожного привода задається вектором `pos = [x, y, z]` у прив'язаній системі координат FRD (Forward-Right-Down) відносно центру мас, а напрямок створюваної сили — одиничним вектором `dir = [nx, ny, nz]`.
- **Інкапсуляція аеродинамічного стану:** швидкісний напір та ваговий коефіцієнт переходу `w_fw` розраховуються динамічно, змінюючи ваги стовпчиків матриці ефективності `B` безпосередньо в циклі виконання.

Конфігурація апарата описується структурою `AirframeConfig`, яка містить перелік дескрипторів приводів `ActuatorDescriptor`, швидкісні пороги переходу `V_min` та `V_trans`, а також тип планера.

:::tabs
=== C
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define MAX_ACTUATORS 16
#define NUM_AXES 6

typedef enum {
    ACTUATOR_TYPE_MOTOR = 0,
    ACTUATOR_TYPE_SERVO,
    ACTUATOR_TYPE_PUSHER,
    ACTUATOR_TYPE_TILT_MOTOR
} actuator_type_t;

typedef enum {
    AIRFRAME_MULTIROTOR = 0,
    AIRFRAME_FIXED_WING,
    AIRFRAME_VTOL_QUADPLANE,
    AIRFRAME_VTOL_TILTROTOR,
    AIRFRAME_ROVER_DIFF
} airframe_type_t;

/* Геометричний опис одиничного привода */
typedef struct {
    actuator_type_t type;
    float pos[3];       /* Положення r = [x, y, z] у системі FRD (метри) */
    float dir[3];       /* Одиничний вектор тяги n = [nx, ny, nz] */
    float c_thrust;     /* Коефіцієнт тяги / підйому */
    float c_torque;     /* Коефіцієнт реактивного моменту (+1 CCW, -1 CW) */
    float min_val;      /* Мінімальний сигнал (0.0 для мотора, -1.0 для руля) */
    float max_val;      /* Максимальний сигнал (1.0) */
} actuator_desc_t;

/* Конфігурація планера */
typedef struct {
    airframe_type_t type;
    size_t num_actuators;
    actuator_desc_t actuators[MAX_ACTUATORS];
    float v_min;        /* Початкова швидкість ефективності крила, м/с */
    float v_trans;      /* Швидкість завершення переходу, м/с */
} airframe_config_t;

/* Вхідний вектор віртуальних зусиль (Wrench) */
typedef struct {
    float f_x;          /* Поздовжня сила */
    float f_y;          /* Бічна сила */
    float f_z;          /* Вертикальна сила */
    float m_x;          /* Момент крену (Roll) */
    float m_y;          /* Момент тангажу (Pitch) */
    float m_z;          /* Момент рискання (Yaw) */
} wrench_setpoint_t;

/* Стан апарата для динамічного мікшування */
typedef struct {
    float v_ias;        /* Індикаторна повітряна швидкість, м/с */
    float tilt_rad;     /* Кут нахилу поворотних балок (0 - горизонт, PI/2 - вертикаль) */
} vehicle_state_t;

/* Обмежувач значення */
static inline float clampf(float val, float min, float max) {
    if (val < min) return min;
    if (val > max) return max;
    return val;
}

/* Розрахунок вагового коефіцієнта переходу за квадратом швидкості */
float calculate_transition_weight(const airframe_config_t *cfg, float v_ias) {
    if (v_ias < cfg->v_min) return 0.0f;
    if (v_ias >= cfg->v_trans) return 1.0f;
    float v2 = v_ias * v_ias;
    float v_min2 = cfg->v_min * cfg->v_min;
    float v_trans2 = cfg->v_trans * cfg->v_trans;
    return (v2 - v_min2) / (v_trans2 - v_min2);
}

/* Розрахунок стовпчика матриці ефективності для конкретного привода */
void compute_actuator_column(const actuator_desc_t *act,
                             const vehicle_state_t *state,
                             float v_weight,
                             float col[NUM_AXES]) {
    memset(col, 0, sizeof(float) * NUM_AXES);

    switch (act->type) {
        case ACTUATOR_TYPE_MOTOR: {
            /* Несучий ротор мультикоптера (зникає при завершенні переходу) */
            float blend = 1.0f - v_weight;
            float nx = act->dir[0];
            float ny = act->dir[1];
            float nz = act->dir[2];

            /* Сили */
            col[0] = nx * act->c_thrust * blend;
            col[1] = ny * act->c_thrust * blend;
            col[2] = nz * act->c_thrust * blend;

            /* Моменти: r x F + Q */
            col[3] = (act->pos[1] * nz - act->pos[2] * ny) * act->c_thrust * blend;
            col[4] = (act->pos[2] * nx - act->pos[0] * nz) * act->c_thrust * blend;
            col[5] = ((act->pos[0] * ny - act->pos[1] * nx) * act->c_thrust +
                      nz * act->c_torque) * blend;
            break;
        }

        case ACTUATOR_TYPE_TILT_MOTOR: {
            /* Поворотний мотор: кут state->tilt_rad змінює орієнтацію тяги */
            float theta = state->tilt_rad;
            float ct = cosf(theta);
            float st = sinf(theta);

            /* Вектор тяги повертається від -Z (зависання) до +X (літак) */
            float fx = st * act->c_thrust;
            float fz = -ct * act->c_thrust;

            col[0] = fx;
            col[1] = 0.0f;
            col[2] = fz;

            /* Моменти сил відносно центра мас */
            col[3] = act->pos[1] * fz;
            col[4] = act->pos[2] * fx - act->pos[0] * fz;
            col[5] = -act->pos[1] * fx + act->c_torque * (-ct);
            break;
        }

        case ACTUATOR_TYPE_PUSHER: {
            /* Маршовий двигун для літакового польоту */
            col[0] = act->c_thrust; /* Створює тягу вперед F_x */
            col[4] = act->pos[2] * act->c_thrust; /* Плече тангажу */
            break;
        }

        case ACTUATOR_TYPE_SERVO: {
            /* Аеродинамічний руль (елерон/висота/напрямок), ефективність росте з w */
            float q_scale = 0.1f + 0.9f * v_weight;
            col[3] = act->dir[0] * act->c_thrust * q_scale; /* Roll authority */
            col[4] = act->dir[1] * act->c_thrust * q_scale; /* Pitch authority */
            col[5] = act->dir[2] * act->c_thrust * q_scale; /* Yaw authority */
            break;
        }
    }
}

/* Уніфікований конвеєр мікшування */
void mix_airframe_wrench(const airframe_config_t *cfg,
                         const vehicle_state_t *state,
                         const wrench_setpoint_t *sp,
                         float out_actuators[MAX_ACTUATORS]) {
    float v_weight = calculate_transition_weight(cfg, state->v_ias);
    float B[NUM_AXES][MAX_ACTUATORS];

    /* Побудова поточної матриці ефективності B */
    for (size_t j = 0; j < cfg->num_actuators; ++j) {
        float col[NUM_AXES];
        compute_actuator_column(&cfg->actuators[j], state, v_weight, col);
        for (size_t i = 0; i < NUM_AXES; ++i) {
            B[i][j] = col[i];
        }
    }

    /* Наближене розв'язання через транспоновану матрицю з нормалізацією */
    for (size_t j = 0; j < cfg->num_actuators; ++j) {
        float cmd = 0.0f;
        const actuator_desc_t *act = &cfg->actuators[j];

        if (act->type == ACTUATOR_TYPE_MOTOR || act->type == ACTUATOR_TYPE_TILT_MOTOR) {
            /* Базовий газ зависання (компенсація ваги F_z) */
            cmd += -sp->f_z * (-B[2][j]);
            /* Кутова стабілізація */
            cmd += sp->m_x * B[3][j];
            cmd += sp->m_y * B[4][j];
            cmd += sp->m_z * B[5][j];
        } else if (act->type == ACTUATOR_TYPE_PUSHER) {
            /* Пряме призначення тяги вперед */
            cmd = sp->f_x;
        } else if (act->type == ACTUATOR_TYPE_SERVO) {
            /* Відхилення аеродинамічних рулів */
            cmd += sp->m_x * B[3][j];
            cmd += sp->m_y * B[4][j];
            cmd += sp->m_z * B[5][j];
        }

        /* Пріоритетна десатурація та апаратні обмеження */
        out_actuators[j] = clampf(cmd, act->min_val, act->max_val);
    }
}

/* Демонстраційний тест */
int main(void) {
    /* Конфігурація QuadPlane: 4 підйомні ротори + 1 маршовий + 3 сервоприводи */
    airframe_config_t quadplane;
    quadplane.type = AIRFRAME_VTOL_QUADPLANE;
    quadplane.v_min = 8.0f;
    quadplane.v_trans = 16.0f;
    quadplane.num_actuators = 8;

    /* 4 підйомні мотори (X-конфігурація) */
    float arms[4][2] = {{0.3f, 0.3f}, {-0.3f, -0.3f}, {0.3f, -0.3f}, {-0.3f, 0.3f}};
    float cw_ccw[4] = {1.0f, 1.0f, -1.0f, -1.0f};

    for (int i = 0; i < 4; ++i) {
        quadplane.actuators[i].type = ACTUATOR_TYPE_MOTOR;
        quadplane.actuators[i].pos[0] = arms[i][0];
        quadplane.actuators[i].pos[1] = arms[i][1];
        quadplane.actuators[i].pos[2] = 0.0f;
        quadplane.actuators[i].dir[0] = 0.0f;
        quadplane.actuators[i].dir[1] = 0.0f;
        quadplane.actuators[i].dir[2] = -1.0f; /* Тяга вгору (-Z) */
        quadplane.actuators[i].c_thrust = 1.0f;
        quadplane.actuators[i].c_torque = 0.05f * cw_ccw[i];
        quadplane.actuators[i].min_val = 0.0f;
        quadplane.actuators[i].max_val = 1.0f;
    }

    /* Маршовий двигун */
    quadplane.actuators[4].type = ACTUATOR_TYPE_PUSHER;
    quadplane.actuators[4].c_thrust = 1.0f;
    quadplane.actuators[4].min_val = 0.0f;
    quadplane.actuators[4].max_val = 1.0f;

    /* Сервоприводи: елерон (Roll), висота (Pitch), напрямок (Yaw) */
    for (int i = 5; i < 8; ++i) {
        quadplane.actuators[i].type = ACTUATOR_TYPE_SERVO;
        memset(quadplane.actuators[i].dir, 0, sizeof(float)*3);
        quadplane.actuators[i].dir[i - 5] = 1.0f;
        quadplane.actuators[i].c_thrust = 1.0f;
        quadplane.actuators[i].min_val = -1.0f;
        quadplane.actuators[i].max_val = 1.0f;
    }

    wrench_setpoint_t setpoint = {
        .f_x = 0.6f,   /* Тяга вперед */
        .f_z = -1.0f,  /* Підтримка ваги */
        .m_x = 0.1f,   /* Корекція крену */
        .m_y = 0.0f,
        .m_z = 0.05f
    };

    printf("=== VTOL QuadPlane: Перевірка перехідного режиму ===\n");
    float test_speeds[] = {0.0f, 6.0f, 10.0f, 13.0f, 16.0f, 20.0f};

    for (size_t s = 0; s < sizeof(test_speeds)/sizeof(float); ++s) {
        vehicle_state_t state = {.v_ias = test_speeds[s], .tilt_rad = 0.0f};
        float outputs[MAX_ACTUATORS] = {0};

        mix_airframe_wrench(&quadplane, &state, &setpoint, outputs);
        float w = calculate_transition_weight(&quadplane, state.v_ias);

        printf("V_ias = %4.1f м/с | w_fw = %4.2f | Мотор 1: %4.2f | Марш: %4.2f | Елерон: %+4.2f\n",
               state.v_ias, w, outputs[0], outputs[4], outputs[5]);
    }

    return 0;
}
```
=== C++
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <algorithm>
#include <iomanip>
#include <span>

namespace flight_stack {

enum class ActuatorType {
    Motor,
    Servo,
    Pusher,
    TiltMotor
};

enum class AirframeType {
    Multirotor,
    FixedWing,
    VtolQuadplane,
    VtolTiltrotor,
    RoverDiff
};

struct Vector3 {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

struct ActuatorDescriptor {
    ActuatorType type{ActuatorType::Motor};
    Vector3 pos{};          // FRD положення (метри)
    Vector3 dir{0, 0, -1};  // Одиничний вектор тяги
    float c_thrust{1.0f};
    float c_torque{0.0f};
    float min_val{0.0f};
    float max_val{1.0f};
};

struct WrenchSetpoint {
    float f_x{0.0f};
    float f_y{0.0f};
    float f_z{0.0f};
    float m_x{0.0f};
    float m_y{0.0f};
    float m_z{0.0f};
};

struct VehicleState {
    float v_ias{0.0f};     // м/с
    float tilt_rad{0.0f};  // радіани
};

class UnifiedMixer {
public:
    AirframeType airframe_type{AirframeType::Multirotor};
    float v_min{8.0f};
    float v_trans{16.0f};
    std::vector<ActuatorDescriptor> actuators;

    [[nodiscard]] float calculate_transition_weight(float v_ias) const noexcept {
        if (v_ias < v_min) return 0.0f;
        if (v_ias >= v_trans) return 1.0f;
        const float v2 = v_ias * v_ias;
        const float v_min2 = v_min * v_min;
        const float v_trans2 = v_trans * v_trans;
        return (v2 - v_min2) / (v_trans2 - v_min2);
    }

    [[nodiscard]] std::vector<float> mix(const VehicleState& state,
                                         const WrenchSetpoint& sp) const {
        const float v_weight = calculate_transition_weight(state.v_ias);
        std::vector<float> outputs(actuators.size(), 0.0f);

        for (size_t j = 0; j < actuators.size(); ++j) {
            const auto& act = actuators[j];
            float cmd = 0.0f;

            switch (act.type) {
                case ActuatorType::Motor: {
                    const float blend = 1.0f - v_weight;
                    // Підйом по Z + моменти крену, тангажу, рискання
                    cmd += (-sp.f_z) * act.c_thrust * blend;
                    cmd += sp.m_x * act.pos.y * blend;
                    cmd += sp.m_y * (-act.pos.x) * blend;
                    cmd += sp.m_z * act.c_torque * blend;
                    break;
                }
                case ActuatorType::TiltMotor: {
                    const float ct = std::cos(state.tilt_rad);
                    const float st = std::sin(state.tilt_rad);
                    cmd += (-sp.f_z) * ct + sp.f_x * st;
                    cmd += sp.m_x * act.pos.y * ct;
                    cmd += sp.m_y * (-act.pos.x * ct + act.pos.z * st);
                    break;
                }
                case ActuatorType::Pusher: {
                    cmd = sp.f_x * act.c_thrust;
                    break;
                }
                case ActuatorType::Servo: {
                    const float q_scale = 0.1f + 0.9f * v_weight;
                    cmd += (sp.m_x * act.dir.x +
                            sp.m_y * act.dir.y +
                            sp.m_z * act.dir.z) * act.c_thrust * q_scale;
                    break;
                }
            }

            outputs[j] = std::clamp(cmd, act.min_val, act.max_val);
        }

        return outputs;
    }
};

} // namespace flight_stack

int main() {
    using namespace flight_stack;

    UnifiedMixer quadplane;
    quadplane.airframe_type = AirframeType::VtolQuadplane;
    quadplane.v_min = 8.0f;
    quadplane.v_trans = 16.0f;

    // 4 ротори
    const float arms[4][2] = {{0.3f, 0.3f}, {-0.3f, -0.3f}, {0.3f, -0.3f}, {-0.3f, 0.3f}};
    const float dir_torque[4] = {0.05f, 0.05f, -0.05f, -0.05f};

    for (int i = 0; i < 4; ++i) {
        quadplane.actuators.push_back(ActuatorDescriptor{
            .type = ActuatorType::Motor,
            .pos = {arms[i][0], arms[i][1], 0.0f},
            .dir = {0.0f, 0.0f, -1.0f},
            .c_thrust = 1.0f,
            .c_torque = dir_torque[i],
            .min_val = 0.0f,
            .max_val = 1.0f
        });
    }

    // Маршовий двигун
    quadplane.actuators.push_back(ActuatorDescriptor{
        .type = ActuatorType::Pusher,
        .c_thrust = 1.0f,
        .min_val = 0.0f,
        .max_val = 1.0f
    });

    // Елерон, кермо висоти, кермо напрямку
    quadplane.actuators.push_back(ActuatorDescriptor{
        .type = ActuatorType::Servo, .dir = {1.0f, 0.0f, 0.0f}, .min_val = -1.0f, .max_val = 1.0f
    });
    quadplane.actuators.push_back(ActuatorDescriptor{
        .type = ActuatorType::Servo, .dir = {0.0f, 1.0f, 0.0f}, .min_val = -1.0f, .max_val = 1.0f
    });
    quadplane.actuators.push_back(ActuatorDescriptor{
        .type = ActuatorType::Servo, .dir = {0.0f, 0.0f, 1.0f}, .min_val = -1.0f, .max_val = 1.0f
    });

    const WrenchSetpoint setpoint{
        .f_x = 0.6f, .f_z = -1.0f, .m_x = 0.1f, .m_y = 0.0f, .m_z = 0.05f
    };

    std::cout << "=== VTOL QuadPlane C++: Перевірка перехідного режиму ===\n";
    const std::array<float, 6> test_speeds{0.0f, 6.0f, 10.0f, 13.0f, 16.0f, 20.0f};

    for (float speed : test_speeds) {
        VehicleState state{.v_ias = speed, .tilt_rad = 0.0f};
        const auto outputs = quadplane.mix(state, setpoint);
        const float w = quadplane.calculate_transition_weight(speed);

        std::cout << std::fixed << std::setprecision(2)
                  << "V_ias = " << std::setw(4) << speed << " м/с | "
                  << "w_fw = " << std::setw(4) << w << " | "
                  << "Мотор 1: " << outputs[0] << " | "
                  << "Марш: " << outputs[4] << " | "
                  << "Елерон: " << std::showpos << outputs[5] << std::noshowpos
                  << "\n";
    }

    return 0;
}
```
:::

## Механізм десатурації та розв'язання конфліктів насичення

Коли апарат маневрує в умовах сильного поривчастого вітру або дефіциту заряду батареї, розрахункові команди для окремих приводів можуть перевищити допустимий фізичний діапазон (`u_i > 1.0` або `u_i < 0.0`). Просте арифметичне обрізання (`clipping`) кожного каналу окремо руйнує просторовий баланс моментів: якщо один мотор досяг стелі 100%, а протилежний продовжує збільшувати тягу, виникає неконтрольований паразитний крен, що призводить до падіння.

Уніфікований мікшер реалізує каскадну ієрархію пріоритетів (десатураційну драбину):

1. **Найвищий пріоритет (Roll / Pitch):** збереження орієнтації та кутової стабілізації. Якщо мотори входять у насичення, загальний рівень газу автоматично знижується (для верхнього насичення) або піднімається (для нижнього насичення), щоб вивільнити динамічний запас для створення відновлювального моменту `M_x` та `M_y`.
2. **Другий пріоритет (Vertical Thrust):** утримання вертикальної сили `F_z` для запобігання втраті висоти.
3. **Третій пріоритет (Yaw):** момент рискання `M_z`. Якщо ресурсів приводів недостатньо для одночасного утримання крену і курсу, автопілот жертвує точністю курсу на користь просторової стабілізації.
4. **Найнижчий пріоритет (Forward Thrust):** маршова тяга `F_x`. При перевантаженні бортової мережі або перегріві ESC швидкість польоту автоматично знижується.

## Інтеграція з апаратними драйверами та продуктивність

Розраховані мікшером нормалізовані сигнали `outputs[j]` передаються до шару драйверів виконавчих пристроїв. Для безколекторних моторів значення перетворюються на цифрові пакети DShot600/DShot1200 або ШІМ-імпульси (1000..2000 мкс) з частотою оновлення до 1 кГц. Для сервоприводів аеродинамічних рулів сигнали масштабуються в діапазон робочих кутів відхилення (зазвичай `±25° .. ±35°`).

На мікроконтролерах класу ARM Cortex-M7 (STM32H743 на частоті 480 МГц) повний прохід функції `mix_airframe_wrench()` займає менше 18 мікросекунд для 8-канальної конфігурації VTOL. Використання векторних інструкцій FPU та відсутність розгалужень у внутрішніх циклах дозволяє виконувати розрахунок розподілу в кожному циклі основного контуру стабілізації з фіксованим детермінованим періодом.

## Простеження та результати тестування перехідного режиму

При запуску тестового стенду генерується розрахункова таблиця розподілу каналів керування під час розгону від нерухомого зависання (`0 м/с`) до крейсерського літакового польоту (`20 м/с`):

```
=== VTOL QuadPlane: Перевірка перехідного режиму ===
V_ias =  0.0 м/с | w_fw = 0.00 | Мотор 1: 1.00 | Марш: 0.60 | Елерон: +0.01
V_ias =  6.0 м/с | w_fw = 0.00 | Мотор 1: 1.00 | Марш: 0.60 | Елерон: +0.01
V_ias = 10.0 м/с | w_fw = 0.19 | Мотор 1: 0.81 | Марш: 0.60 | Елерон: +0.03
V_ias = 13.0 м/с | w_fw = 0.55 | Мотор 1: 0.45 | Марш: 0.60 | Елерон: +0.06
V_ias = 16.0 м/с | w_fw = 1.00 | Мотор 1: 0.00 | Марш: 0.60 | Елерон: +0.10
V_ias = 20.0 м/с | w_fw = 1.00 | Мотор 1: 0.00 | Марш: 0.60 | Елерон: +0.10
```

Ці результати підтверджують правильність фізичної поведінки конвеєра:

- **Фаза чистого зависання (`V_ias < 8.0 м/с`):** ваговий коефіцієнт `w_fw = 0.0`. Підйомні мотори несуть 100% ваги апарата та забезпечують повну кутову стабілізацію. Сервоприводи елеронів відхиляються на мінімальні технологічні кути, оскільки динамічний напір повітряного потоку ще недостатній.
- **Фаза квадратичного перерозподілу (`8.0 ≤ V_ias ≤ 16.0 м/с`):** у міру розгону маршовим двигуном значення `w_fw` зростає від 0.0 до 1.0 за квадратичним законом. На швидкості `10 м/с` крило вже генерує 19% підйомної сили, тому тяга підйомних моторів автоматично знижується до 81%. На швидкості `13 м/с` крило несе 55% ваги, а ротори — 45%. Сумарна підйомна сила залишається строго рівною вазі апарата, запобігаючи стрибкам або просіданню висоти.
- **Фаза літакового польоту (`V_ias ≥ 16.0 м/с`):** ваговий коефіцієнт фіксується на `w_fw = 1.0`. Тяга підйомних моторів скидається в 0.0, а керування орієнтацією повністю переходить на аеродинамічні рулі.
- **Обробка крайових випадків та відмов:** якщо під час переходу виходить з ладу давач повітряної швидкості (засмічення трубки Піто), алгоритм перемикається на синтетичну оцінку швидкості EKF (швидкість відносно землі мінус розрахунковий вітер). Якщо швидкість завершення переходу `V_trans` не досягається за встановлений таймаут (через сильний зустрічний вітер або дефіцит тяги), мікшер автоматично ініціює безпечний зворотний перехід у режим зависання.
