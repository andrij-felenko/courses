#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_CHANNELS 16

/* Типи планерів, підтримувані єдиним стеком */
typedef enum {
    AIRFRAME_MULTIROTOR_X4 = 0,
    AIRFRAME_FIXED_WING_CONVENTIONAL,
    AIRFRAME_VTOL_QUADPLANE,
    AIRFRAME_VTOL_TILTROTOR,
    AIRFRAME_ROVER_SKID_STEER
} airframe_class_t;

/* Вектор сил і моментів від каскадних регуляторів */
typedef struct {
    float fx, fy, fz; /* Сили у зв'язаній системі координат FRD (Н) */
    float mx, my, mz; /* Моменти сил крену, тангажу, рискання (Н·м) */
} wrench_command_t;

/* Динамічний стан планера */
typedef struct {
    float v_ias;        /* Індикаторна швидкість (м/с) */
    float tilt_angle;   /* Кут нахилу гондол (рад, 0 = літак, PI/2 = коптер) */
    float dynamic_press;/* Швидкісний напір q = 0.5 * rho * V^2 (Па) */
} airframe_state_t;

/* Структура конфігурації конкретного привода */
typedef struct {
    uint8_t output_channel; /* Фізичний канал (PWM/DShot 0..15) */
    float pos[3];           /* Координати [x, y, z] від центру мас (м) */
    float dir[3];           /* Одиничний вектор тяги [nx, ny, nz] */
    float c_thrust;         /* Коефіцієнт тяги */
    float c_torque;         /* Коефіцієнт реактивного моменту */
    float min_limit;        /* Нижнє насичення (0.0 або -1.0) */
    float max_limit;        /* Верхнє насичення (+1.0) */
} actuator_channel_t;

/* Головний інтерфейс виклику уніфікованого мікшера */
void allocate_actuators(airframe_class_t airframe,
                        const airframe_state_t *state,
                        const wrench_command_t *wrench,
                        const actuator_channel_t *actuators,
                        size_t num_actuators,
                        float *out_commands);
