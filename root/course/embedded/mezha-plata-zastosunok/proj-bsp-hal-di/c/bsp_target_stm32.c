/* --- bsp_target_stm32.c: Реалізація для цільового мікроконтролера --- */
#include "supervisor.h"
#include "stm32f4xx_hal.h"

extern ADC_HandleTypeDef hadc1;
extern I2C_HandleTypeDef hi2c1;

static bsp_status_t target_led_set(board_led_id_t led, board_led_state_t state) {
    GPIO_PinState ps = (state == BOARD_LED_STATE_ON) ? GPIO_PIN_SET : GPIO_PIN_RESET;
    if (led == BOARD_LED_ID_SYSTEM_STATUS) {
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12, ps);
        return BSP_STATUS_OK;
    } else if (led == BOARD_LED_ID_WARNING) {
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, ps);
        return BSP_STATUS_OK;
    }
    return BSP_STATUS_ERR_INVALID_PARAM;
}

static bsp_status_t target_power_set(board_power_domain_t domain, bool enable) {
    if (domain == BOARD_POWER_DOMAIN_SENSORS) {
        // P-MOSFET ключ (Active-Low): 0 — увімкнено, 1 — знеструмлено
        HAL_GPIO_WritePin(GPIOE, GPIO_PIN_3, enable ? GPIO_PIN_RESET : GPIO_PIN_SET);
        if (enable) {
            HAL_Delay(15); // Затримка заряду фільтрів
        }
        return BSP_STATUS_OK;
    }
    return BSP_STATUS_ERR_UNSUPPORTED;
}

static bsp_status_t target_get_battery(board_battery_metrics_t *m) {
    HAL_ADC_Start(&hadc1);
    if (HAL_ADC_PollForConversion(&hadc1, 10) == HAL_OK) {
        uint32_t raw = HAL_ADC_GetValue(&hadc1);
        // Дільник R1=100кОм, R2=200кОм -> V_bat = V_pin * 1.5
        uint32_t v_pin_mv = (raw * 3300) / 4095;
        m->voltage_mv = (uint16_t)((v_pin_mv * 3) / 2);
        m->charge_percent = (m->voltage_mv > 4200) ? 100 : (m->voltage_mv < 3000 ? 0 : (m->voltage_mv - 3000) / 12);
        return BSP_STATUS_OK;
    }
    return BSP_STATUS_ERR_TIMEOUT;
}

static bsp_status_t target_read_env(board_env_metrics_t *env) {
    uint8_t raw[6] = {0};
    // Читання BME280 за адресою 0x76
    if (HAL_I2C_Mem_Read(&hi2c1, 0x76 << 1, 0xF7, 1, raw, 6, 50) == HAL_OK) {
        int32_t temp_raw = (raw[3] << 12) | (raw[4] << 4) | (raw[5] >> 4);
        env->temperature_centi_c = (int16_t)((temp_raw * 100) / 5120);
        return BSP_STATUS_OK;
    }
    return BSP_STATUS_ERR_BUS_FAULT;
}

static bsp_status_t target_enter_sleep(board_sleep_mode_t m, uint32_t ms) {
    (void)ms;
    if (m == BOARD_SLEEP_MODE_DEEP) {
        HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
        return BSP_STATUS_OK;
    }
    return BSP_STATUS_ERR_UNSUPPORTED;
}

const bsp_driver_t stm32_bsp_driver = {
    .led_set = target_led_set,
    .power_domain_set = target_power_set,
    .get_battery_metrics = target_get_battery,
    .read_environment = target_read_env,
    .enter_low_power = target_enter_sleep
};
