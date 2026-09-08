/**
 * @file sea_controller.h
 * @brief Драйвер серійного пружного привода (R-SEA) для мікроконтролерів STM32.
 * Оголошення структур конфігурації, поточного стану та функцій опитування енкодерів.
 */

#ifndef SEA_CONTROLLER_H
#define SEA_CONTROLLER_H

#include "stm32g4xx_hal.h"
#include <stdint.h>
#include <stdbool.h>

#define AS5047P_CMD_READ_ANGLE  0xFFFF  /* Команда читання кута без виправлення помилок */
#define ENCODER_RESOLUTION      16384.0f/* Роздільна здатність 14-бітного енкодера */
#define MATH_TWO_PI             6.283185307179586f

/**
 * @brief Параметри конфігурації пружного привода
 */
typedef struct {
    float k_spring;         /* Жорсткість торсіонної пружини [Н*м/рад] */
    float gear_ratio;       /* Передатне число редуктора N:1 */
    float kp;               /* Пропорційний коефіцієнт регулятора моменту */
    float ki;               /* Інтегральний коефіцієнт */
    float kd;               /* Диференціальний коефіцієнт */
    float i_max;            /* Межа насичення інтегратора [А] */
    float torque_max;       /* Гранично допустимий крутний момент [Н*м] */
    float coulomb_friction; /* Сила сухого кулонівського тертя [Н*м] */
    float viscous_friction; /* В'язке тертя [Н*м/(рад/с)] */
    uint16_t enc_rotor_zero;/* Калібрувальний нуль енкодера ротора */
    uint16_t enc_joint_zero;/* Калібрувальний нуль енкодера суглоба */
} SeaConfig_t;

/**
 * @brief Поточний стан системи привода
 */
typedef struct {
    uint16_t raw_rotor;     /* Сирі відліки енкодера двигуна */
    uint16_t raw_joint;     /* Сирі відліки енкодера вихідного вала */
    float theta_rotor_rad;  /* Кут ротора в радіанах */
    float theta_joint_rad;  /* Кут вихідної ланки в радіанах */
    float theta_deflect_rad;/* Кут пружної деформації пружини */
    float torque_measured;  /* Виміряний крутний момент [Н*м] */
    float torque_desired;   /* Заданий цільовий момент [Н*м] */
    float torque_error;     /* Похибка регулювання */
    float integral_accum;   /* Акумулятор інтегральної складової */
    float prev_error;       /* Похибка на попередньому кроці для похідної */
    float current_q_cmd;    /* Розрахований керуючий струм q-осі [А] */
    bool is_overloaded;     /* Прапорець аварійного перевантаження */
} SeaState_t;

/* Прототипи інтерфейсних функцій */
HAL_StatusTypeDef Sea_Init(SPI_HandleTypeDef *hspi,
                           GPIO_TypeDef *cs1_port, uint16_t cs1_pin,
                           GPIO_TypeDef *cs2_port, uint16_t cs2_pin);

void Sea_SetConfig(const SeaConfig_t *cfg);
void Sea_CalibrateZeros(uint16_t num_samples);
uint16_t Sea_ReadEncoderSPI(uint8_t encoder_idx);
void Sea_SetDesiredTorque(float torque_nm);
void Sea_Timer1kHz_ISR(void);
const SeaState_t* Sea_GetState(void);

#endif /* SEA_CONTROLLER_H */
