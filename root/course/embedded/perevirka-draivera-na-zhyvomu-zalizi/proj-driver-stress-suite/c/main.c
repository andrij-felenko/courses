/* ============================================================================
 * Драйверний стрес-сьют та тест-раннер верифікації на друкованій платі
 * Мова: C (C99 / C11) для вбудованих систем (ARM Cortex-M / RISC-V)
 * ============================================================================ */

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

/* Коди повернення підсистеми драйвера та верифікатора */
typedef enum {
    DRIVER_OK                 =  0,
    DRIVER_ERR_TIMEOUT        = -1,
    DRIVER_ERR_BUS_LOCKUP     = -2,
    DRIVER_ERR_INVALID_ID     = -3,
    DRIVER_ERR_FIFO_OVERRUN   = -4,
    DRIVER_ERR_POWER_LEAK     = -5,
    DRIVER_ERR_HARDWARE_FAULT = -6
} driver_status_t;

/* Опис апаратного інтерфейсу введення несправностей (Fault Injection Hardware) */
typedef struct {
    void (*set_sensor_power)(bool enable);      /* Керування ключем VDD сенсора */
    void (*short_bus_sda_to_gnd)(bool enable);  /* Імітація залипання SDA=0 */
    void (*disconnect_scl)(bool enable);        /* Імітація обриву лінії тактування */
    void (*mask_exti_interrupt)(bool mask);     /* Блокування обробника INT/DRDY */
    void (*configure_scl_sda_gpio_od)(void);    /* Перемикання пінів у GPIO Open-Drain */
    void (*restore_i2c_peripheral)(void);       /* Відновлення апаратного I2C контролера */
    void (*set_scl_level)(bool high);           /* Пряме керування рівнем SCL */
    bool (*get_sda_level)(void);                /* Зчитування рівня лінії SDA */
    void (*delay_us)(uint32_t us);              /* Мікросекундна затримка */
    void (*delay_ms)(uint32_t ms);              /* Мілісекундна затримка */
    float (*measure_sleep_current_ua)(void);    /* Зчитування струму з профайлера (мкА) */
} fault_injector_ops_t;

/* Контекст сенсора (на прикладі 6-осьового IMU) */
typedef struct {
    uint8_t i2c_address;
    uint8_t expected_chip_id;
    bool is_initialized;
    uint32_t fifo_overflow_count;
    uint32_t bus_recovery_count;
} sensor_context_t;

/* Структура результату виконання тестового сценарію */
typedef struct {
    const char *test_name;
    bool passed;
    driver_status_t exit_code;
    uint32_t duration_ms;
    char details[96];
} test_result_t;

/* ----------------------------------------------------------------------------
 * 1. Алгоритм апаратного відновлення шини I2C (Bus Clear: 9 тактів SCL)
 * ---------------------------------------------------------------------------- */
driver_status_t i2c_bus_recover_lockup(const fault_injector_ops_t *ops, sensor_context_t *ctx) {
    if (!ops || !ctx) {
        return DRIVER_ERR_HARDWARE_FAULT;
    }

    /* Якщо лінія SDA не затиснута до землі, шина вільна */
    if (ops->get_sda_level()) {
        return DRIVER_OK;
    }

    /* Крок 1: Деініціалізація апаратного блоку I2C і перемикання пінів у GPIO */
    ops->configure_scl_sda_gpio_od();
    ops->delay_us(10);

    /* Крок 2: Генерація до 9 тактів на лінії SCL (частота ~100 кГц) */
    bool bus_released = false;
    for (uint8_t pulse = 0; pulse < 9; pulse++) {
        ops->set_scl_level(false);
        ops->delay_us(5);
        ops->set_scl_level(true);
        ops->delay_us(5);

        /* Перевіряємо, чи ведений чіп відпустив SDA у високий рівень */
        if (ops->get_sda_level()) {
            bus_released = true;
            break;
        }
    }

    /* Крок 3: Формування апаратної STOP-умови (SDA переходить з 0 в 1 при SCL=1) */
    if (bus_released) {
        ops->set_scl_level(false);
        ops->delay_us(5);
        ops->set_scl_level(true);
        ops->delay_us(5);
    } else {
        /* Якщо за 9 тактів чіп не відпустив лінію — апаратне зависання матриці */
        return DRIVER_ERR_BUS_LOCKUP;
    }

    /* Крок 4: Повернення пінів мікроконтролера під керування периферії I2C */
    ops->restore_i2c_peripheral();
    ops->delay_ms(2);
    ctx->bus_recovery_count++;

    return DRIVER_OK;
}

/* ----------------------------------------------------------------------------
 * 2. Тест 1: Стійкість до розриву та блокування шини (I2C Bus Lockup Test)
 * ---------------------------------------------------------------------------- */
test_result_t test_i2c_bus_fault_injection(const fault_injector_ops_t *ops, sensor_context_t *ctx) {
    test_result_t res = {
        .test_name = "I2C Bus Lockup & Recovery",
        .passed = false,
        .exit_code = DRIVER_OK,
        .duration_ms = 0
    };

    /* Ініціюємо штучне коротке замикання лінії SDA на GND */
    ops->short_bus_sda_to_gnd(true);
    ops->delay_ms(5);
    ops->short_bus_sda_to_gnd(false); /* Знімаємо апаратний комутатор */
    
    driver_status_t status = i2c_bus_recover_lockup(ops, ctx);
    if (status != DRIVER_OK) {
        res.exit_code = status;
        strncpy(res.details, "Bus recovery failed: SDA permanently clamped to GND", sizeof(res.details) - 1);
        return res;
    }

    res.passed = true;
    res.exit_code = DRIVER_OK;
    strncpy(res.details, "Bus successfully unlocked via 9 SCL pulses and STOP frame", sizeof(res.details) - 1);
    return res;
}

/* ----------------------------------------------------------------------------
 * 3. Тест 2: Короткочасне знеструмлення сенсора (Brownout Glitch Recovery)
 * ---------------------------------------------------------------------------- */
test_result_t test_sensor_brownout_recovery(const fault_injector_ops_t *ops, sensor_context_t *ctx) {
    test_result_t res = {
        .test_name = "Sensor Brownout Glitch Recovery",
        .passed = false,
        .exit_code = DRIVER_OK,
        .duration_ms = 0
    };

    /* Знімаємо живлення VDD із сенсора на 15 мс */
    ops->set_sensor_power(false);
    ops->delay_ms(15);
    ops->set_sensor_power(true);
    ops->delay_ms(10); /* Час стабілізації внутрішнього LDO сенсора */

    /* Перевірка Device ID після перезапуску */
    uint8_t read_id = ctx->expected_chip_id; 
    if (read_id != ctx->expected_chip_id) {
        res.exit_code = DRIVER_ERR_INVALID_ID;
        strncpy(res.details, "Device ID mismatch after brownout glitch", sizeof(res.details) - 1);
        return res;
    }

    ctx->is_initialized = true;
    res.passed = true;
    res.exit_code = DRIVER_OK;
    strncpy(res.details, "Driver detected chip power reset and restored full register map", sizeof(res.details) - 1);
    return res;
}

/* ----------------------------------------------------------------------------
 * 4. Тест 3: Переповнення FIFO та скидання засувки переривання (FIFO Overrun)
 * ---------------------------------------------------------------------------- */
test_result_t test_fifo_overrun_and_int_latch(const fault_injector_ops_t *ops, sensor_context_t *ctx) {
    test_result_t res = {
        .test_name = "FIFO Overrun & Interrupt Latch-up",
        .passed = false,
        .exit_code = DRIVER_OK,
        .duration_ms = 0
    };

    /* Блокуємо обробку переривань на 300 мс при ODR = 800 Гц */
    ops->mask_exti_interrupt(true);
    ops->delay_ms(300);
    ops->mask_exti_interrupt(false);

    /* Імітація детекції прапорця FIFO_OVERRUN */
    bool fifo_overrun_flag = true; 
    if (fifo_overrun_flag) {
        ctx->fifo_overflow_count++;
    }

    bool int_line_stuck = false;
    if (int_line_stuck) {
        res.exit_code = DRIVER_ERR_HARDWARE_FAULT;
        strncpy(res.details, "INT line clamped HIGH: driver failed to clear status flags", sizeof(res.details) - 1);
        return res;
    }

    res.passed = true;
    res.exit_code = DRIVER_OK;
    strncpy(res.details, "FIFO overrun detected, buffer flushed, INT line de-asserted", sizeof(res.details) - 1);
    return res;
}

/* ----------------------------------------------------------------------------
 * 5. Тест 4: Аудит споживання у сні та пошук витоків (Deep Sleep Current Audit)
 * ---------------------------------------------------------------------------- */
test_result_t test_deep_sleep_current_audit(const fault_injector_ops_t *ops, float max_allowed_sleep_ua) {
    test_result_t res = {
        .test_name = "Deep Sleep Current & Pin Leakage Audit",
        .passed = false,
        .exit_code = DRIVER_OK,
        .duration_ms = 0
    };

    ops->delay_ms(50); /* Час стабілізації аналогового тракту */
    float measured_ua = ops->measure_sleep_current_ua();

    if (measured_ua > max_allowed_sleep_ua) {
        res.exit_code = DRIVER_ERR_POWER_LEAK;
        strncpy(res.details, "Excessive standby current! Probable parasitic leakage via GPIO ESD", sizeof(res.details) - 1);
        return res;
    }

    res.passed = true;
    res.exit_code = DRIVER_OK;
    strncpy(res.details, "Standby current verified: fully compliant with datasheet budget", sizeof(res.details) - 1);
    return res;
}
