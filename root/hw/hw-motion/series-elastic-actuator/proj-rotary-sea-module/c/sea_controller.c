/**
 * @file sea_controller.c
 * @brief Реалізація SPI-обміну з енкодерами AS5047P та швидкого ПІД-контуру моменту 1 кГц.
 */

#include "sea_controller.h"
#include <math.h>

static SPI_HandleTypeDef *p_hspi = NULL;
static GPIO_TypeDef *p_cs1_port = NULL;
static uint16_t g_cs1_pin = 0;
static GPIO_TypeDef *p_cs2_port = NULL;
static uint16_t g_cs2_pin = 0;

static SeaConfig_t g_cfg = {
    .k_spring = 240.0f,
    .gear_ratio = 50.0f,
    .kp = 0.85f,
    .ki = 12.0f,
    .kd = 0.015f,
    .i_max = 15.0f,
    .torque_max = 50.0f,
    .coulomb_friction = 0.45f,
    .viscous_friction = 0.08f,
    .enc_rotor_zero = 0,
    .enc_joint_zero = 0
};

static SeaState_t g_state = {0};

/**
 * @brief Ініціалізація апаратних ліній керування енкодерами
 */
HAL_StatusTypeDef Sea_Init(SPI_HandleTypeDef *hspi,
                           GPIO_TypeDef *cs1_port, uint16_t cs1_pin,
                           GPIO_TypeDef *cs2_port, uint16_t cs2_pin) {
    if (!hspi || !cs1_port || !cs2_port) return HAL_ERROR;

    p_hspi = hspi;
    p_cs1_port = cs1_port;
    g_cs1_pin = cs1_pin;
    p_cs2_port = cs2_port;
    g_cs2_pin = cs2_pin;

    /* Деактивація ліній Chip Select (активний низький) */
    HAL_GPIO_WritePin(p_cs1_port, g_cs1_pin, GPIO_PIN_SET);
    HAL_GPIO_WritePin(p_cs2_port, g_cs2_pin, GPIO_PIN_SET);

    return HAL_OK;
}

void Sea_SetConfig(const SeaConfig_t *cfg) {
    if (cfg) {
        g_cfg = *cfg;
    }
}

/**
 * @brief Опитування одного з магнітних енкодерів через шину SPI
 * @param encoder_idx 1 — енкодер вала ротора, 2 — енкодер вихідного суглоба
 */
uint16_t Sea_ReadEncoderSPI(uint8_t encoder_idx) {
    GPIO_TypeDef *port = (encoder_idx == 1) ? p_cs1_port : p_cs2_port;
    uint16_t pin = (encoder_idx == 1) ? g_cs1_pin : g_cs2_pin;

    uint16_t tx_buf = AS5047P_CMD_READ_ANGLE;
    uint16_t rx_buf = 0;

    /* Опускаємо CS */
    HAL_GPIO_WritePin(port, pin, GPIO_PIN_RESET);
    /* Передача команди запиту кута */
    HAL_SPI_TransmitReceive(p_hspi, (uint8_t*)&tx_buf, (uint8_t*)&rx_buf, 1, 5);
    /* Піднімаємо CS */
    HAL_GPIO_WritePin(port, pin, GPIO_PIN_SET);

    /* Маска 14 біт кутових даних (ігноруємо біт парності та прапорець помилки) */
    return (rx_buf & 0x3FFF);
}

/**
 * @brief Автоматичне калібрування нульових точок обох енкодерів при знеструмленому приводі
 */
void Sea_CalibrateZeros(uint16_t num_samples) {
    if (num_samples == 0) num_samples = 100;
    uint32_t sum_rotor = 0;
    uint32_t sum_joint = 0;

    for (uint16_t i = 0; i < num_samples; i++) {
        sum_rotor += Sea_ReadEncoderSPI(1);
        sum_joint += Sea_ReadEncoderSPI(2);
        HAL_Delay(1);
    }

    g_cfg.enc_rotor_zero = (uint16_t)(sum_rotor / num_samples);
    g_cfg.enc_joint_zero = (uint16_t)(sum_joint / num_samples);
}

void Sea_SetDesiredTorque(float torque_nm) {
    if (torque_nm > g_cfg.torque_max) torque_nm = g_cfg.torque_max;
    if (torque_nm < -g_cfg.torque_max) torque_nm = -g_cfg.torque_max;
    g_state.torque_desired = torque_nm;
}

/**
 * @brief Обробник високопріоритетного таймерного переривання 1 кГц (dt = 0.001 с)
 */
void Sea_Timer1kHz_ISR(void) {
    const float dt = 0.001f;

    /* 1. Читання сирих кутів з двох енкодерів AS5047P */
    g_state.raw_rotor = Sea_ReadEncoderSPI(1);
    g_state.raw_joint = Sea_ReadEncoderSPI(2);

    /* 2. Обчислення кутів у радіанах з урахуванням нульових зсувів */
    int32_t diff_rotor = (int32_t)g_state.raw_rotor - (int32_t)g_cfg.enc_rotor_zero;
    int32_t diff_joint = (int32_t)g_state.raw_joint - (int32_t)g_cfg.enc_joint_zero;

    /* Нормалізація в межах одного оберту [0; 2*PI] */
    if (diff_rotor < 0) diff_rotor += 16384;
    if (diff_joint < 0) diff_joint += 16384;

    g_state.theta_rotor_rad = ((float)diff_rotor / ENCODER_RESOLUTION) * MATH_TWO_PI;
    g_state.theta_joint_rad = ((float)diff_joint / ENCODER_RESOLUTION) * MATH_TWO_PI;

    /* 3. Деформація торсіонного елемента SEA за редуктором N:1 */
    float theta_gear_output = g_state.theta_rotor_rad / g_cfg.gear_ratio;
    g_state.theta_deflect_rad = theta_gear_output - g_state.theta_joint_rad;

    /* 4. Оцінка фактичного крутного моменту за законом Гука */
    g_state.torque_measured = g_cfg.k_spring * g_state.theta_deflect_rad;

    /* Захист від механічного перевантаження */
    if (fabsf(g_state.torque_measured) >= g_cfg.torque_max) {
        g_state.is_overloaded = true;
        g_state.current_q_cmd = 0.0f;
        return;
    }

    /* 5. Розрахунок помилки контуру моменту */
    g_state.torque_error = g_state.torque_desired - g_state.torque_measured;

    /* Інтегральна складова з обмеженням анти-вінд-ап */
    g_state.integral_accum += g_cfg.ki * g_state.torque_error * dt;
    if (g_state.integral_accum > g_cfg.i_max) g_state.integral_accum = g_cfg.i_max;
    if (g_state.integral_accum < -g_cfg.i_max) g_state.integral_accum = -g_cfg.i_max;

    /* Диференціальна складова */
    float derivative = (g_state.torque_error - g_state.prev_error) / dt;
    g_state.prev_error = g_state.torque_error;

    /* Компенсація сили тертя редуктора (Feedforward) */
    float friction_comp = 0.0f;
    if (fabsf(g_state.torque_desired) > 0.05f) {
        friction_comp = (g_state.torque_desired > 0) ? g_cfg.coulomb_friction : -g_cfg.coulomb_friction;
    }

    /* 6. Формування сигналу керування струмом q-осі */
    float i_q = (g_cfg.kp * g_state.torque_error) + g_state.integral_accum + (g_cfg.kd * derivative) + friction_comp;

    /* Насичення струму згідно з обмеженням інвертора */
    if (i_q > g_cfg.i_max) i_q = g_cfg.i_max;
    if (i_q < -g_cfg.i_max) i_q = -g_cfg.i_max;

    g_state.current_q_cmd = i_q;
}

const SeaState_t* Sea_GetState(void) {
    return &g_state;
}
