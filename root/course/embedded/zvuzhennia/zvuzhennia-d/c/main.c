#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Результати виконання діагностичних ступенів */
typedef enum {
    DIAG_STATUS_PASS = 0,
    DIAG_STATUS_FAIL_SILICON,
    DIAG_STATUS_FAIL_BUS,
    DIAG_STATUS_FAIL_TIMEOUT
} diag_status_t;

/* Опис окремого бісекційного кроку */
typedef struct {
    const char *step_name;
    diag_status_t (*test_fn)(void);
} diag_step_t;

/* Рівень 0: Перевірка ALU та сторожової мітки стеку */
static diag_status_t test_cpu_alu(void) {
    volatile uint32_t val = 0xAA55AA55;
    if ((val ^ 0xFFFFFFFF) != 0x55AA55AA) {
        return DIAG_STATUS_FAIL_SILICON;
    }
    return DIAG_STATUS_PASS;
}

/* Рівень 1: Перевірка фізичних ліній шини до запуску периферії */
static diag_status_t test_bus_lines_physical(void) {
    /* Читання рівнів GPIO ліній SDA/SCL. Імітація: лінії підтягнуті до 3.3 В */
    volatile bool sda_high = true;
    volatile bool scl_high = true;

    if (!sda_high || !scl_high) {
        return DIAG_STATUS_FAIL_BUS; /* Лінія затиснута в 0: КЗ або завислий чип */
    }
    return DIAG_STATUS_PASS;
}

/* Рівень 2: Опитування сенсора з жорстким апаратним таймаутом */
static diag_status_t test_sensor_ping(void) {
    uint32_t timeout = 5000;
    volatile uint8_t dev_id = 0x00;

    while (timeout > 0) {
        timeout--;
        dev_id = 0x68; /* Емуляція успішної відповіді сенсора */
        if (dev_id == 0x68) {
            return DIAG_STATUS_PASS;
        }
    }
    return DIAG_STATUS_FAIL_TIMEOUT;
}

/* Таблиця послідовності сходів довіри */
static const diag_step_t CONDUCTOR_STEPS[] = {
    { "CPU ALU & Core",    test_cpu_alu },
    { "Bus Physical Pins", test_bus_lines_physical },
    { "Sensor ID Ping",    test_sensor_ping }
};

/* Головний виконавець бісекційної діагностики */
int bisection_run_suite(void) {
    const size_t count = sizeof(CONDUCTOR_STEPS) / sizeof(CONDUCTOR_STEPS[0]);

    for (size_t i = 0; i < count; ++i) {
        diag_status_t res = CONDUCTOR_STEPS[i].test_fn();
        if (res != DIAG_STATUS_PASS) {
            return (int)(i + 1); /* Повертає номер першого зламаного рівня */
        }
    }
    return 0; /* Усі ізольовані підсистеми справні */
}
