/* bsp_target_stm32.c — усе, що знає про конкретний кремній і конкретну плату.
 *
 * Розводка: LED_STATUS = PB12, LED_WARN = PA4,
 *           ключ живлення давачів  = PE3 (P-MOSFET, активний нуль),
 *           ключ живлення радіо    = PE4 (P-MOSFET, активний нуль),
 *           АЦП батареї = ADC1 через дільник 100к/200к,
 *           BME280 на I2C1, адреса 0x76.
 */
#include "bsp_target_stm32.h"

#include "stm32f4xx_hal.h"

/* Дескриптори периферії створює згенерований CubeMX код. */
extern ADC_HandleTypeDef hadc1;
extern I2C_HandleTypeDef hi2c1;
extern RTC_HandleTypeDef hrtc;

/* Після виходу зі STOP ядро тактується від HSI — годинник треба підняти. */
void SystemClock_Config(void);

#define LED_STATUS_PORT   GPIOB
#define LED_STATUS_PIN    GPIO_PIN_12
#define LED_WARN_PORT     GPIOA
#define LED_WARN_PIN      GPIO_PIN_4
#define PWR_SENSORS_PORT  GPIOE
#define PWR_SENSORS_PIN   GPIO_PIN_3
#define PWR_RADIO_PORT    GPIOE
#define PWR_RADIO_PIN     GPIO_PIN_4

#define VREF_MV           3300u
#define ADC_FULL_SCALE    4095u
#define DIVIDER_NUM       3u      /* (R1+R2)/R2 = 300к/200к = 1.5 */
#define DIVIDER_DEN       2u

#define BME280_ADDR       (0x76u << 1)
#define BME280_ID         0x60u
#define BME280_REG_ID     0xD0u
#define BME280_REG_CALIB  0x88u
#define BME280_REG_CTRL_H 0xF2u
#define BME280_REG_STATUS 0xF3u
#define BME280_REG_CTRL_M 0xF4u
#define BME280_REG_DATA   0xF7u
#define BME280_FORCED_T2X 0x41u   /* osrs_t = x2, osrs_p = skip, mode = forced */
#define I2C_TIMEOUT_MS    50u

/* Калібрування температури читається один раз: воно прошите в NVM чипа
 * і не залежить від того, скільки разів давач знеструмлювали. */
static uint16_t s_dig_t1;
static int16_t  s_dig_t2;
static int16_t  s_dig_t3;
static bool     s_bme_ready;

static bsp_status_t bme_read(uint8_t reg, uint8_t *buf, uint16_t len)
{
    if (HAL_I2C_Mem_Read(&hi2c1, BME280_ADDR, reg, I2C_MEMADD_SIZE_8BIT,
                         buf, len, I2C_TIMEOUT_MS) != HAL_OK) {
        return BSP_STATUS_ERR_BUS_FAULT;
    }
    return BSP_STATUS_OK;
}

static bsp_status_t bme_write(uint8_t reg, uint8_t value)
{
    if (HAL_I2C_Mem_Write(&hi2c1, BME280_ADDR, reg, I2C_MEMADD_SIZE_8BIT,
                          &value, 1, I2C_TIMEOUT_MS) != HAL_OK) {
        return BSP_STATUS_ERR_BUS_FAULT;
    }
    return BSP_STATUS_OK;
}

static bsp_status_t target_led_set(board_led_id_t led, board_led_state_t state)
{
    const GPIO_PinState ps = (state == BOARD_LED_STATE_ON) ? GPIO_PIN_SET : GPIO_PIN_RESET;

    switch (led) {
    case BOARD_LED_ID_SYSTEM_STATUS:
        HAL_GPIO_WritePin(LED_STATUS_PORT, LED_STATUS_PIN, ps);
        return BSP_STATUS_OK;
    case BOARD_LED_ID_WARNING:
        HAL_GPIO_WritePin(LED_WARN_PORT, LED_WARN_PIN, ps);
        return BSP_STATUS_OK;
    default:
        return BSP_STATUS_ERR_INVALID_PARAM;
    }
}

static bsp_status_t target_power_set(board_power_domain_t domain, bool enable)
{
    /* Ключі на P-MOSFET: нуль на затворі — домен під напругою. */
    const GPIO_PinState ps = enable ? GPIO_PIN_RESET : GPIO_PIN_SET;

    switch (domain) {
    case BOARD_POWER_DOMAIN_SENSORS:
        HAL_GPIO_WritePin(PWR_SENSORS_PORT, PWR_SENSORS_PIN, ps);
        return BSP_STATUS_OK;
    case BOARD_POWER_DOMAIN_RADIO:
        HAL_GPIO_WritePin(PWR_RADIO_PORT, PWR_RADIO_PIN, ps);
        return BSP_STATUS_OK;
    default:
        return BSP_STATUS_ERR_INVALID_PARAM;
    }
}

static bsp_status_t target_get_battery(board_battery_metrics_t *m)
{
    if (m == NULL) {
        return BSP_STATUS_ERR_INVALID_PARAM;
    }
    if (HAL_ADC_Start(&hadc1) != HAL_OK) {
        return BSP_STATUS_ERR_BUS_FAULT;
    }
    if (HAL_ADC_PollForConversion(&hadc1, 10) != HAL_OK) {
        HAL_ADC_Stop(&hadc1);
        return BSP_STATUS_ERR_TIMEOUT;
    }

    const uint32_t raw = HAL_ADC_GetValue(&hadc1);
    HAL_ADC_Stop(&hadc1);

    const uint32_t v_pin_mv = (raw * VREF_MV) / ADC_FULL_SCALE;
    const uint32_t v_bat_mv = (v_pin_mv * DIVIDER_NUM) / DIVIDER_DEN;

    m->voltage_mv = (uint16_t)v_bat_mv;
    /* Груба лінійна оцінка 3000..4200 мВ; для Li-Ion цього досить,
     * бо рішення ухвалюються за напругою, а не за відсотками. */
    if (v_bat_mv >= 4200u) {
        m->charge_percent = 100u;
    } else if (v_bat_mv <= 3000u) {
        m->charge_percent = 0u;
    } else {
        m->charge_percent = (uint8_t)((v_bat_mv - 3000u) / 12u);
    }
    return BSP_STATUS_OK;
}

static bsp_status_t target_read_env(board_env_metrics_t *env)
{
    if (env == NULL) {
        return BSP_STATUS_ERR_INVALID_PARAM;
    }
    if (!s_bme_ready) {
        return BSP_STATUS_ERR_UNSUPPORTED;
    }

    /* Давач щойно ввімкнули з холодного стану — режим і передискретизацію
     * треба задавати заново на КОЖНЕ вимірювання. */
    bsp_status_t st = bme_write(BME280_REG_CTRL_H, 0x01u);   /* osrs_h = x1 */
    if (st != BSP_STATUS_OK) {
        return st;
    }
    st = bme_write(BME280_REG_CTRL_M, BME280_FORCED_T2X);
    if (st != BSP_STATUS_OK) {
        return st;
    }

    /* Одиничне перетворення при x2 триває близько 6 мс; чекаємо, поки
     * впаде біт measuring, але не довше 20 мс — інакше це не давач. */
    uint8_t status = 0x08u;
    for (uint32_t waited = 0; (status & 0x08u) != 0u; waited++) {
        if (waited > 20u) {
            return BSP_STATUS_ERR_TIMEOUT;
        }
        HAL_Delay(1);
        st = bme_read(BME280_REG_STATUS, &status, 1);
        if (st != BSP_STATUS_OK) {
            return st;
        }
    }

    uint8_t raw[6] = {0};
    st = bme_read(BME280_REG_DATA, raw, sizeof(raw));
    if (st != BSP_STATUS_OK) {
        return st;
    }

    const int32_t adc_t = ((int32_t)raw[3] << 12) | ((int32_t)raw[4] << 4) |
                          ((int32_t)raw[5] >> 4);
    if (adc_t == 0x80000) {   /* канал вимкнено — даних немає */
        return BSP_STATUS_ERR_BUS_FAULT;
    }

    /* Компенсація за формулою з даташита BME280 (розділ 4.2.3). */
    const int32_t var1 = (((adc_t >> 3) - ((int32_t)s_dig_t1 << 1)) * (int32_t)s_dig_t2) >> 11;
    const int32_t d    = (adc_t >> 4) - (int32_t)s_dig_t1;
    const int32_t var2 = (((d * d) >> 12) * (int32_t)s_dig_t3) >> 14;
    const int32_t t_fine = var1 + var2;

    env->temperature_centi_c = (int16_t)((t_fine * 5 + 128) >> 8);
    return BSP_STATUS_OK;
}

static bsp_status_t rtc_arm_wakeup(uint32_t timeout_ms)
{
    uint32_t seconds = timeout_ms / 1000u;
    if (seconds == 0u) {
        seconds = 1u;
    }
    if (seconds > 0xFFFFu) {   /* стеля 16-бітного лічильника на ck_spre */
        seconds = 0xFFFFu;
    }
    HAL_RTCEx_DeactivateWakeUpTimer(&hrtc);
    if (HAL_RTCEx_SetWakeUpTimer_IT(&hrtc, seconds - 1u,
                                    RTC_WAKEUPCLOCK_CK_SPRE_16BITS) != HAL_OK) {
        return BSP_STATUS_ERR_TIMEOUT;
    }
    return BSP_STATUS_OK;
}

static bsp_status_t target_enter_low_power(board_sleep_mode_t mode, uint32_t timeout_ms)
{
    const bsp_status_t st = rtc_arm_wakeup(timeout_ms);
    if (st != BSP_STATUS_OK) {
        return st;
    }

    if (mode == BOARD_SLEEP_MODE_DEEP) {
        HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
        /* Прокинулися: у STOP годинник скинувся на HSI. */
        SystemClock_Config();
    } else {
        /* У Sleep тик SysTick будив би ядро щомілісекунди — глушимо його. */
        HAL_SuspendTick();
        HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
        HAL_ResumeTick();
    }

    HAL_RTCEx_DeactivateWakeUpTimer(&hrtc);
    return BSP_STATUS_OK;
}

static void target_delay_ms(uint32_t ms)
{
    HAL_Delay(ms);
}

static uint32_t target_uptime_ms(void)
{
    return HAL_GetTick();
}

bsp_status_t stm32_bsp_init(void)
{
    /* Безпечний стан: індикатори згашені, обидва домени знеструмлені. */
    (void)target_led_set(BOARD_LED_ID_SYSTEM_STATUS, BOARD_LED_STATE_OFF);
    (void)target_led_set(BOARD_LED_ID_WARNING, BOARD_LED_STATE_OFF);
    (void)target_power_set(BOARD_POWER_DOMAIN_SENSORS, false);
    (void)target_power_set(BOARD_POWER_DOMAIN_RADIO, false);

    /* Щоб прочитати калібрування, давач треба ненадовго ввімкнути. */
    (void)target_power_set(BOARD_POWER_DOMAIN_SENSORS, true);
    HAL_Delay(15);

    bsp_status_t st;
    uint8_t id = 0;
    uint8_t calib[6] = {0};

    st = bme_read(BME280_REG_ID, &id, 1);
    if (st == BSP_STATUS_OK && id != BME280_ID) {
        st = BSP_STATUS_ERR_UNSUPPORTED;   /* на шині щось інше */
    }
    if (st == BSP_STATUS_OK) {
        st = bme_read(BME280_REG_CALIB, calib, sizeof(calib));
    }
    if (st == BSP_STATUS_OK) {
        s_dig_t1 = (uint16_t)(calib[0] | ((uint16_t)calib[1] << 8));
        s_dig_t2 = (int16_t)(calib[2] | ((uint16_t)calib[3] << 8));
        s_dig_t3 = (int16_t)(calib[4] | ((uint16_t)calib[5] << 8));
        s_bme_ready = true;
    }

    (void)target_power_set(BOARD_POWER_DOMAIN_SENSORS, false);
    return st;
}

const bsp_driver_t stm32_bsp_driver = {
    .led_set             = target_led_set,
    .power_domain_set    = target_power_set,
    .get_battery_metrics = target_get_battery,
    .read_environment    = target_read_env,
    .enter_low_power     = target_enter_low_power,
    .delay_ms            = target_delay_ms,
    .uptime_ms           = target_uptime_ms
};
