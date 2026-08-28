#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Коди результатів діагностичного тесту */
typedef enum {
    TEST_RES_PASS = 0,
    TEST_RES_FAIL_HARDWARE,
    TEST_RES_FAIL_TIMEOUT,
    TEST_RES_FAIL_INTEGRITY
} test_result_t;

/* Опис діагностичного ступеня */
typedef struct {
    const char *name;
    test_result_t (*run_test)(void);
    uint32_t timeout_us;
} diagnostic_step_t;

/* Сходинка 0: Перевірка сторожової мітки стеку та цілісності ALU */
static test_result_t test_core_and_stack(void) {
    volatile uint32_t canary = 0xDEADBEEF;
    volatile uint32_t a = 0x12345678;
    volatile uint32_t b = 0x87654321;
    
    if ((a ^ b) != 0x95511559) {
        return TEST_RES_FAIL_HARDWARE;
    }
    if (canary != 0xDEADBEEF) {
        return TEST_RES_FAIL_INTEGRITY;
    }
    return TEST_RES_PASS;
}

/* Сходинка 1: Маршовий тест локальної ділянки SRAM */
static test_result_t test_sram_patterns(void) {
    static volatile uint32_t test_buffer[32];
    const size_t len = sizeof(test_buffer) / sizeof(test_buffer[0]);
    
    /* Запис і перевірка шахового патерну 0x55555555 */
    for (size_t i = 0; i < len; ++i) {
        test_buffer[i] = 0x55555555UL;
    }
    for (size_t i = 0; i < len; ++i) {
        if (test_buffer[i] != 0x55555555UL) {
            return TEST_RES_FAIL_INTEGRITY;
        }
        test_buffer[i] = 0xAAAAAAAAUL; /* Інверсія */
    }
    for (size_t i = 0; i < len; ++i) {
        if (test_buffer[i] != 0xAAAAAAAAUL) {
            return TEST_RES_FAIL_INTEGRITY;
        }
    }
    return TEST_RES_PASS;
}

/* Сходинка 2: Ізольована перевірка стану ліній шини I2C (GPIO probe) */
static test_result_t test_i2c_bus_idle(void) {
    /* Симуляція читання фізичного стану ліній SDA / SCL перед стартом модуля.
       У реальному MCU: gpio_get_level(SDA_PIN) && gpio_get_level(SCL_PIN) */
    volatile bool sda_high = true;
    volatile bool scl_high = true;

    if (!sda_high || !scl_high) {
        /* Лінія затиснута до землі: апаратне КЗ або завислий ведений чип */
        return TEST_RES_FAIL_HARDWARE;
    }
    return TEST_RES_PASS;
}

/* Сходинка 3: Опитування ID сенсора з жорстким лічильником таймауту */
static test_result_t test_sensor_id_ping(void) {
    uint32_t timeout_counter = 10000;
    volatile uint8_t device_id = 0x00;
    
    /* Імітація обміну: читання регістра WHO_AM_I */
    while (timeout_counter > 0) {
        timeout_counter--;
        /* Запис/читання шини. Для тесту емулюємо успішну відповідь 0x68 */
        device_id = 0x68;
        if (device_id == 0x68) {
            return TEST_RES_PASS;
        }
    }
    return TEST_RES_FAIL_TIMEOUT;
}

/* Таблиця сходинок бісекційного кондуктора */
static const diagnostic_step_t DIAG_SUITE[] = {
    { "Core & Stack Integrity", test_core_and_stack, 100 },
    { "Internal SRAM March",    test_sram_patterns,   500 },
    { "I2C Bus Physical Lines", test_i2c_bus_idle,    200 },
    { "Sensor ID Verification", test_sensor_id_ping,  2000 }
};

/* Головний виконавець бісекційної самоперевірки */
int run_bisection_diagnostics(void) {
    const size_t total_steps = sizeof(DIAG_SUITE) / sizeof(DIAG_SUITE[0]);
    
    for (size_t i = 0; i < total_steps; ++i) {
        test_result_t res = DIAG_SUITE[i].run_test();
        if (res != TEST_RES_PASS) {
            /* Локалізовано дефект: рівень i ізолює винуватця */
            return (int)(i + 1); /* Повертаємо номер зламаної сходинки */
        }
    }
    return 0; /* Усі ізольовані тести пройдено успішно */
}
