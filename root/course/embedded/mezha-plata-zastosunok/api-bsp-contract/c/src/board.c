#include "bsp/board.h"

#include "bsp/port.h"
#include "env_sensors.h"

/*
 * Топологія плати живе ТУТ і більше ніде. Застосунок не знає ні номерів
 * виводів, ні полярності, ні того, що домен сенсорів вимикається P-канальним
 * ключем із активним низьким рівнем на затворі.
 */

typedef struct {
    bsp_pin_t pin;
    bool      active_high; /**< true — світиться при лог. 1 на виводі */
    bool      open_drain;  /**< true — вивід із відкритим стоком (спільний анод) */
} led_desc_t;

typedef struct {
    bsp_pin_t gate;             /**< затвор силового ключа домену */
    bool      gate_active_high; /**< рівень, що ВІДКРИВАЄ ключ */
    uint16_t  settle_ms;        /**< заряд блокувальних конденсаторів домену */
    bool      owns_i2c;         /**< домен живить давачі на шині I2C */
} power_desc_t;

static const led_desc_t s_leds[BOARD_LED_ID_MAX] = {
    /* SYSTEM_STATUS */ { { BSP_GPIO_PORT_A, 5u }, true,  false },
    /* WARNING       */ { { BSP_GPIO_PORT_B, 0u }, false, false },
    /* COMMS         */ { { BSP_GPIO_PORT_B, 1u }, false, true  },
};

static const power_desc_t s_domains[BOARD_POWER_DOMAIN_MAX] = {
    /* SENSORS */ { { BSP_GPIO_PORT_C, 13u }, false, 15u, true  },
    /* RADIO   */ { { BSP_GPIO_PORT_C, 14u }, false, 20u, false },
    /* DISPLAY */ { { BSP_GPIO_PORT_C, 15u }, false, 10u, false },
};

static const bsp_pin_t s_i2c_scl = { BSP_GPIO_PORT_B, 6u };
static const bsp_pin_t s_i2c_sda = { BSP_GPIO_PORT_B, 7u };
/* Лінія STAT контролера заряду: активний низький рівень. */
static const bsp_pin_t s_charger_stat = { BSP_GPIO_PORT_A, 1u };

#define BOARD_ADC_CH_VBAT       4u
#define BOARD_VBAT_DIVIDER      2u   /* резистивний дільник 1:2 */
#define BOARD_ADC_FULL_SCALE    4095u
#define BOARD_VREFINT_CAL_MV    3000u /* заводський код знято при 3.000 В */
#define BOARD_BUS_LOCK_TIMEOUT  20u
#define BOARD_FLUSH_TIMEOUT_MS  50u

static bool              s_initialized;
static bool              s_domain_on[BOARD_POWER_DOMAIN_MAX];
static uint32_t          s_domain_ready_ms[BOARD_POWER_DOMAIN_MAX];
static board_led_state_t s_led_state[BOARD_LED_ID_MAX];

/* --------------------------------------------------------------- індикація */

static void led_apply(const led_desc_t *desc, bool on)
{
    if (desc->open_drain) {
        /* Спільний анод: світимо, притискаючи катод до землі; гасимо — в Hi-Z. */
        if (on) {
            bsp_port_pin_mode(desc->pin, BSP_PIN_MODE_OUTPUT_OD);
            bsp_port_pin_write(desc->pin, false);
        } else {
            bsp_port_pin_mode(desc->pin, BSP_PIN_MODE_INPUT);
        }
        return;
    }

    bsp_port_pin_mode(desc->pin, BSP_PIN_MODE_OUTPUT_PP);
    bsp_port_pin_write(desc->pin, desc->active_high ? on : !on);
}

bsp_status_t board_led_set(board_led_id_t led, board_led_state_t state)
{
    if ((unsigned)led >= (unsigned)BOARD_LED_ID_MAX) {
        return BSP_STATUS_ERR_INVALID_PARAM;
    }
    if (state != BOARD_LED_STATE_OFF && state != BOARD_LED_STATE_ON) {
        return BSP_STATUS_ERR_INVALID_PARAM;
    }
    if (!s_initialized) {
        return BSP_STATUS_ERR_NOT_INIT;
    }

    /* Один запис у регістр BSRR — операція атомарна, тож дозволена і в ISR. */
    led_apply(&s_leds[led], state == BOARD_LED_STATE_ON);
    s_led_state[led] = state;
    return BSP_STATUS_OK;
}

bsp_status_t board_led_toggle(board_led_id_t led)
{
    if ((unsigned)led >= (unsigned)BOARD_LED_ID_MAX) {
        return BSP_STATUS_ERR_INVALID_PARAM;
    }
    /* Стан беремо з тіньової копії: вивід із відкритим стоком читати марно. */
    return board_led_set(led, s_led_state[led] == BOARD_LED_STATE_ON
                                  ? BOARD_LED_STATE_OFF
                                  : BOARD_LED_STATE_ON);
}

/* ------------------------------------------------------- життєвий цикл */

static void domains_all_off(void)
{
    for (unsigned i = 0; i < (unsigned)BOARD_POWER_DOMAIN_MAX; ++i) {
        const power_desc_t *desc = &s_domains[i];

        bsp_port_pin_mode(desc->gate, BSP_PIN_MODE_OUTPUT_PP);
        bsp_port_pin_write(desc->gate, !desc->gate_active_high);
        s_domain_on[i] = false;
    }
}

bsp_status_t board_init(void)
{
    bsp_status_t status;

    if (s_initialized) {
        return BSP_STATUS_OK;
    }

    BSP_TRY(bsp_port_clock_init());

    /* Перше, що робимо, — гарантовано розмикаємо всі силові ключі. */
    domains_all_off();

    for (unsigned i = 0; i < (unsigned)BOARD_LED_ID_MAX; ++i) {
        led_apply(&s_leds[i], false);
        s_led_state[i] = BOARD_LED_STATE_OFF;
    }

    /*
     * Виводи знеструмленого домену тримаємо в аналоговому режимі: інакше
     * через ESD-діоди давача підтечеться живлення з ліній шини.
     */
    bsp_port_pin_mode(s_i2c_scl, BSP_PIN_MODE_ANALOG);
    bsp_port_pin_mode(s_i2c_sda, BSP_PIN_MODE_ANALOG);
    bsp_port_pin_mode(s_charger_stat, BSP_PIN_MODE_INPUT_PU);

    status = bsp_port_adc_init();
    if (status != BSP_STATUS_OK) {
        return status;
    }

    env_sensors_invalidate();
    s_initialized = true;
    return BSP_STATUS_OK;
}

bsp_status_t board_deinit(void)
{
    if (!s_initialized) {
        return BSP_STATUS_OK;
    }

    for (unsigned i = 0; i < (unsigned)BOARD_POWER_DOMAIN_MAX; ++i) {
        (void)board_power_domain_set((board_power_domain_t)i, false);
    }
    for (unsigned i = 0; i < (unsigned)BOARD_LED_ID_MAX; ++i) {
        led_apply(&s_leds[i], false);
        bsp_port_pin_mode(s_leds[i].pin, BSP_PIN_MODE_ANALOG);
        s_led_state[i] = BOARD_LED_STATE_OFF;
    }

    bsp_port_adc_deinit();
    s_initialized = false;
    return BSP_STATUS_OK;
}

/* ------------------------------------------------------------- живлення */

bsp_status_t board_power_domain_set(board_power_domain_t domain, bool enable)
{
    const power_desc_t *desc;

    if ((unsigned)domain >= (unsigned)BOARD_POWER_DOMAIN_MAX) {
        return BSP_STATUS_ERR_INVALID_PARAM;
    }
    if (!s_initialized) {
        return BSP_STATUS_ERR_NOT_INIT;
    }
    if (bsp_port_in_isr()) {
        /* Функція блокує на десятки мілісекунд — у перериванні це заборонено. */
        return BSP_STATUS_ERR_UNSUPPORTED;
    }

    desc = &s_domains[domain];

    if (enable) {
        if (s_domain_on[domain]) {
            return BSP_STATUS_OK;
        }

        bsp_port_pin_write(desc->gate, desc->gate_active_high);
        /* Плавний заряд блокувальних конденсаторів: раніше шину чіпати не можна. */
        bsp_port_delay_us((uint32_t)desc->settle_ms * 1000u);

        if (desc->owns_i2c) {
            const bsp_status_t status = bsp_port_i2c_init();

            if (status != BSP_STATUS_OK) {
                /* Відкат: живлення не лишаємо ввімкненим при мертвій шині. */
                bsp_port_pin_write(desc->gate, !desc->gate_active_high);
                return status;
            }
            env_sensors_invalidate();
        }

        s_domain_on[domain] = true;
        s_domain_ready_ms[domain] = bsp_port_tick_ms();
        return BSP_STATUS_OK;
    }

    if (!s_domain_on[domain]) {
        return BSP_STATUS_OK;
    }

    if (desc->owns_i2c) {
        /* Спершу Hi-Z на лініях, і лише потім знімаємо живлення. */
        bsp_port_i2c_deinit();
        bsp_port_pin_mode(s_i2c_scl, BSP_PIN_MODE_ANALOG);
        bsp_port_pin_mode(s_i2c_sda, BSP_PIN_MODE_ANALOG);
        env_sensors_invalidate();
    }
    bsp_port_pin_write(desc->gate, !desc->gate_active_high);
    s_domain_on[domain] = false;
    return BSP_STATUS_OK;
}

/* -------------------------------------------------------------- батарея */

/* Розрядна крива Li-Ion: напруга спокою → залишковий заряд. */
static uint8_t battery_percent(uint32_t mv)
{
    static const struct {
        uint16_t mv;
        uint8_t  percent;
    } curve[] = {
        { 4200u, 100u }, { 4000u, 85u }, { 3850u, 70u }, { 3700u, 50u },
        { 3600u, 30u },  { 3500u, 15u }, { 3400u,  7u }, { 3000u,  0u },
    };
    const size_t n = sizeof curve / sizeof curve[0];

    if (mv >= curve[0].mv) {
        return 100u;
    }
    for (size_t i = 1; i < n; ++i) {
        if (mv >= curve[i].mv) {
            /* Лінійна інтерполяція між сусідніми точками таблиці. */
            const uint32_t span_mv = (uint32_t)curve[i - 1].mv - curve[i].mv;
            const uint32_t span_pc = (uint32_t)curve[i - 1].percent - curve[i].percent;

            return (uint8_t)(curve[i].percent + ((mv - curve[i].mv) * span_pc) / span_mv);
        }
    }
    return 0u;
}

bsp_status_t board_get_battery_metrics(board_battery_metrics_t *out_metrics)
{
    uint16_t raw_vref = 0;
    uint16_t raw_vbat = 0;
    uint32_t vdda_mv;
    uint32_t vbat_mv;

    if (out_metrics == NULL) {
        return BSP_STATUS_ERR_INVALID_PARAM;
    }
    if (!s_initialized) {
        return BSP_STATUS_ERR_NOT_INIT;
    }

    BSP_TRY(bsp_port_adc_read_avg16(BSP_PORT_ADC_CH_VREFINT, &raw_vref));
    if (raw_vref == 0u) {
        /* Опорне джерело не запустилося — рахувати немає від чого. */
        return BSP_STATUS_ERR_POWER_FAULT;
    }
    BSP_TRY(bsp_port_adc_read_avg16(BOARD_ADC_CH_VBAT, &raw_vbat));

    /* Живлення АЦП відновлюємо із заводської константи, а не припускаємо 3.3 В. */
    vdda_mv = (BOARD_VREFINT_CAL_MV * (uint32_t)bsp_port_vrefint_cal()) / raw_vref;
    vbat_mv = ((uint32_t)raw_vbat * vdda_mv * BOARD_VBAT_DIVIDER) / BOARD_ADC_FULL_SCALE;

    out_metrics->voltage_mv      = (uint16_t)vbat_mv;
    out_metrics->charge_percent  = battery_percent(vbat_mv);
    out_metrics->is_charging     = !bsp_port_pin_read(s_charger_stat);
    out_metrics->is_critical_low = (vbat_mv < BOARD_BATTERY_CRITICAL_MV);

    if (vbat_mv < BOARD_BATTERY_CUTOFF_MV) {
        /* Структуру заповнено, але це вже аварія: час зберігатися й засинати. */
        return BSP_STATUS_ERR_POWER_FAULT;
    }
    return BSP_STATUS_OK;
}

/* ------------------------------------------------------ давачі й шина */

/*
 * Відновлення затиснутої шини: ведений, якого перервали посеред байта, тримає
 * SDA у нулі. Дев'ять тактів SCL дають йому доклацати транзакцію, після чого
 * ми вручну формуємо STOP.
 */
static void i2c_bus_recover(void)
{
    bsp_port_i2c_deinit();

    bsp_port_pin_mode(s_i2c_scl, BSP_PIN_MODE_OUTPUT_OD);
    bsp_port_pin_write(s_i2c_scl, true);
    bsp_port_pin_mode(s_i2c_sda, BSP_PIN_MODE_INPUT_PU);

    for (unsigned i = 0; i < 9u && !bsp_port_pin_read(s_i2c_sda); ++i) {
        bsp_port_pin_write(s_i2c_scl, false);
        bsp_port_delay_us(5u);
        bsp_port_pin_write(s_i2c_scl, true);
        bsp_port_delay_us(5u);
    }

    /* STOP: фронт SDA 0→1 при високому SCL. */
    bsp_port_pin_mode(s_i2c_sda, BSP_PIN_MODE_OUTPUT_OD);
    bsp_port_pin_write(s_i2c_sda, false);
    bsp_port_delay_us(5u);
    bsp_port_pin_write(s_i2c_scl, true);
    bsp_port_delay_us(5u);
    bsp_port_pin_write(s_i2c_sda, true);
    bsp_port_delay_us(5u);

    (void)bsp_port_i2c_init();
    env_sensors_invalidate();
}

bsp_status_t board_read_environment(board_env_metrics_t *out_env)
{
    bsp_status_t status;
    uint32_t elapsed_ms;

    if (out_env == NULL) {
        return BSP_STATUS_ERR_INVALID_PARAM;
    }
    if (!s_initialized) {
        return BSP_STATUS_ERR_NOT_INIT;
    }
    if (bsp_port_in_isr()) {
        /* Блокуючий обмін по I2C у перериванні зірвав би реальний час. */
        return BSP_STATUS_ERR_UNSUPPORTED;
    }
    if (!s_domain_on[BOARD_POWER_DOMAIN_SENSORS]) {
        return BSP_STATUS_ERR_NOT_INIT;
    }

    /* Різниця беззнакових коректна й на переповненні лічильника тиків. */
    elapsed_ms = bsp_port_tick_ms() - s_domain_ready_ms[BOARD_POWER_DOMAIN_SENSORS];
    if (elapsed_ms < BOARD_SENSOR_WARMUP_MS) {
        bsp_port_delay_us((BOARD_SENSOR_WARMUP_MS - elapsed_ms) * 1000u);
    }

    /* Шина спільна: транзакцію накриваємо м'ютексом самі, не турбуючи застосунок. */
    BSP_TRY(bsp_port_bus_lock(BOARD_BUS_LOCK_TIMEOUT));

    status = env_sensors_read(out_env);
    if (status == BSP_STATUS_ERR_BUS_FAULT) {
        i2c_bus_recover();
    }

    bsp_port_bus_unlock();
    return status;
}

/* ----------------------------------------------------------------- сон */

bsp_status_t board_enter_low_power(board_sleep_mode_t mode, uint32_t timeout_ms)
{
    bsp_status_t status;

    if (mode != BOARD_SLEEP_MODE_LIGHT && mode != BOARD_SLEEP_MODE_DEEP) {
        return BSP_STATUS_ERR_INVALID_PARAM;
    }
    if (!s_initialized) {
        return BSP_STATUS_ERR_NOT_INIT;
    }
    if (bsp_port_in_isr()) {
        return BSP_STATUS_ERR_UNSUPPORTED;
    }

    /* Спершу дочікуємо DMA й UART: зупинити тактування посеред кадру = втрата даних. */
    BSP_TRY(bsp_port_flush_async_io(BOARD_FLUSH_TIMEOUT_MS));

    (void)board_power_domain_set(BOARD_POWER_DOMAIN_SENSORS, false);
    if (mode == BOARD_SLEEP_MODE_DEEP) {
        (void)board_power_domain_set(BOARD_POWER_DOMAIN_RADIO, false);
        (void)board_power_domain_set(BOARD_POWER_DOMAIN_DISPLAY, false);

        /* Виводи індикаторів в аналоговий режим: жодного струму через підтяжки. */
        for (unsigned i = 0; i < (unsigned)BOARD_LED_ID_MAX; ++i) {
            led_apply(&s_leds[i], false);
            bsp_port_pin_mode(s_leds[i].pin, BSP_PIN_MODE_ANALOG);
        }
        bsp_port_adc_deinit();
    }

    status = bsp_port_enter_stop(mode == BOARD_SLEEP_MODE_DEEP, timeout_ms);

    if (mode == BOARD_SLEEP_MODE_DEEP) {
        /* Після зупинки генератора тактування піднімається наново. */
        BSP_TRY(bsp_port_clock_init());
        BSP_TRY(bsp_port_adc_init());
        for (unsigned i = 0; i < (unsigned)BOARD_LED_ID_MAX; ++i) {
            led_apply(&s_leds[i], s_led_state[i] == BOARD_LED_STATE_ON);
        }
    }
    return status;
}

/* -------------------------------------------------------------- час */

uint32_t board_get_tick_ms(void)
{
    return bsp_port_tick_ms();
}

void board_delay_us(uint32_t us)
{
    bsp_port_delay_us(us);
}
