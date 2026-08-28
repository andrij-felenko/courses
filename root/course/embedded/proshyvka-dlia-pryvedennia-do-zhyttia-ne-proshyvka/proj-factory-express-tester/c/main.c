#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define TEST_REPORT_MAX_LEN 1024
#define I2C_TIMEOUT_CYCLES  5000
#define SPI_TIMEOUT_CYCLES  8000

typedef enum {
    TEST_RES_PASS = 0,
    TEST_RES_FAIL = 1,
    TEST_RES_TIMEOUT = 2,
    TEST_RES_BUS_LOCKED = 3,
    TEST_RES_INVALID_ID = 4
} test_result_t;

typedef struct {
    const char* name;
    test_result_t (*run)(char* err_msg, uint32_t max_err_len);
    uint32_t execution_time_us;
} test_case_t;

/* Симуляція апаратного таймера мікросекунд */
static inline uint32_t timer_get_us(void) {
    extern volatile uint32_t g_system_us_ticks;
    return g_system_us_ticks;
}

/* 1. Маршовий тест оперативної пам'яті (March C- Pattern) */
test_result_t test_ram_march_c(char* err_msg, uint32_t max_err_len) {
    #define RAM_TEST_WORDS 256
    static uint32_t test_buffer[RAM_TEST_WORDS];
    volatile uint32_t* ram = test_buffer;
    size_t n = RAM_TEST_WORDS;

    /* Фаза 1: ↕(w0) — запис нулів */
    for (size_t i = 0; i < n; i++) {
        ram[i] = 0x00000000;
    }

    /* Фаза 2: ⇑(r0, w1) — читання 0, запис 1 */
    for (size_t i = 0; i < n; i++) {
        if (ram[i] != 0x00000000) {
            strncpy(err_msg, "RAM: SAF0/TF fault at phase 2", max_err_len);
            return TEST_RES_FAIL;
        }
        ram[i] = 0xFFFFFFFF;
    }

    /* Фаза 3: ⇑(r1, w0) — читання 1, запис 0 */
    for (size_t i = 0; i < n; i++) {
        if (ram[i] != 0xFFFFFFFF) {
            strncpy(err_msg, "RAM: SAF1/TF fault at phase 3", max_err_len);
            return TEST_RES_FAIL;
        }
        ram[i] = 0x00000000;
    }

    /* Фаза 4: ⇓(r0, w1) — збіжне читання 0, запис 1 */
    for (size_t i = n; i > 0; i--) {
        size_t idx = i - 1;
        if (ram[idx] != 0x00000000) {
            strncpy(err_msg, "RAM: Coupling fault at phase 4", max_err_len);
            return TEST_RES_FAIL;
        }
        ram[idx] = 0xFFFFFFFF;
    }

    /* Фаза 5: ⇓(r1, w0) — читання 1, запис 0 */
    for (size_t i = n; i > 0; i--) {
        size_t idx = i - 1;
        if (ram[idx] != 0xFFFFFFFF) {
            strncpy(err_msg, "RAM: Coupling fault at phase 5", max_err_len);
            return TEST_RES_FAIL;
        }
        ram[idx] = 0x00000000;
    }

    /* Фаза 6: ↕(r0) — фінальна верифікація нулів */
    for (size_t i = 0; i < n; i++) {
        if (ram[i] != 0x00000000) {
            strncpy(err_msg, "RAM: Retention fault at phase 6", max_err_len);
            return TEST_RES_FAIL;
        }
    }

    return TEST_RES_PASS;
}

/* 2. Апаратне відновлення та сканування I2C шини */
extern void gpio_set_i2c_scl(bool level);
extern void gpio_set_i2c_sda(bool level);
extern bool gpio_get_i2c_sda(void);
extern void gpio_set_i2c_mode_gpio(void);
extern void gpio_set_i2c_mode_peripheral(void);
extern bool hal_i2c_read_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t* val, uint32_t timeout);

static void i2c_bus_recovery_sequence(void) {
    gpio_set_i2c_mode_gpio();
    gpio_set_i2c_sda(true);

    /* Генерація 9 імпульсів SCL для вивільнення завислого slave */
    for (int i = 0; i < 9; i++) {
        gpio_set_i2c_scl(false);
        for (volatile int d = 0; d < 20; d++);
        gpio_set_i2c_scl(true);
        for (volatile int d = 0; d < 20; d++);
        if (gpio_get_i2c_sda()) {
            break; /* Ведений відпустив шину */
        }
    }

    /* Стоп-умова (SDA переходить з 0 в 1 при високому SCL) */
    gpio_set_i2c_scl(false);
    gpio_set_i2c_sda(false);
    for (volatile int d = 0; d < 20; d++);
    gpio_set_i2c_scl(true);
    for (volatile int d = 0; d < 20; d++);
    gpio_set_i2c_sda(true);

    gpio_set_i2c_mode_peripheral();
}

test_result_t test_i2c_sensors(char* err_msg, uint32_t max_err_len) {
    i2c_bus_recovery_sequence();

    /* Перевірка IMU ICM-42688 (I2C адреса 0x68, регістр WHO_AM_I 0x75, очікується 0x47) */
    uint8_t imu_id = 0;
    if (!hal_i2c_read_reg(0x68, 0x75, &imu_id, I2C_TIMEOUT_CYCLES)) {
        strncpy(err_msg, "I2C: IMU (0x68) NACK / Timeout", max_err_len);
        return TEST_RES_TIMEOUT;
    }
    if (imu_id != 0x47) {
        strncpy(err_msg, "I2C: IMU ID mismatch (expected 0x47)", max_err_len);
        return TEST_RES_INVALID_ID;
    }

    /* Перевірка барометра BMP390 (I2C адреса 0x77, регістр CHIP_ID 0x00, очікується 0x60) */
    uint8_t baro_id = 0;
    if (!hal_i2c_read_reg(0x77, 0x00, &baro_id, I2C_TIMEOUT_CYCLES)) {
        strncpy(err_msg, "I2C: Barometer (0x77) NACK / Timeout", max_err_len);
        return TEST_RES_TIMEOUT;
    }
    if (baro_id != 0x60) {
        strncpy(err_msg, "I2C: Barometer ID mismatch (expected 0x60)", max_err_len);
        return TEST_RES_INVALID_ID;
    }

    return TEST_RES_PASS;
}

/* 3. Перевірка SPI Flash JEDEC ID */
extern void hal_spi_cs_select(bool active);
extern void hal_spi_transfer(const uint8_t* tx, uint8_t* rx, size_t len);

test_result_t test_spi_nor_flash(char* err_msg, uint32_t max_err_len) {
    uint8_t cmd[4] = {0x9F, 0x00, 0x00, 0x00}; /* JEDEC Read ID command */
    uint8_t resp[4] = {0};

    hal_spi_cs_select(true);
    hal_spi_transfer(cmd, resp, sizeof(cmd));
    hal_spi_cs_select(false);

    uint8_t mfg_id = resp[1];
    uint8_t mem_type = resp[2];
    uint8_t capacity = resp[3];

    /* Перевірка на Winbond W25Q128 (0xEF, 0x40, 0x18) */
    if (mfg_id == 0x00 || mfg_id == 0xFF) {
        strncpy(err_msg, "SPI Flash: MISO stuck at 0/1 (no response)", max_err_len);
        return TEST_RES_BUS_LOCKED;
    }
    if (mfg_id != 0xEF || capacity != 0x18) {
        strncpy(err_msg, "SPI Flash: Unknown JEDEC ID / Capacity", max_err_len);
        return TEST_RES_INVALID_ID;
    }

    return TEST_RES_PASS;
}

/* Таблиця тестового набору */
static test_case_t g_suite[] = {
    {"RAM_MARCH_C", test_ram_march_c, 0},
    {"I2C_WHO_AM_I", test_i2c_sensors, 0},
    {"SPI_FLASH_ID", test_spi_nor_flash, 0}
};

/* Виконання всіх тестів та формування вихідного звіту */
extern void uart_send_string(const char* str);

void test_runner_execute_all(void) {
    char report[TEST_REPORT_MAX_LEN] = "{\"fct_report\":[";
    bool all_passed = true;
    size_t count = sizeof(g_suite) / sizeof(g_suite[0]);

    for (size_t i = 0; i < count; i++) {
        char err_buf[64] = {0};
        uint32_t t_start = timer_get_us();
        test_result_t res = g_suite[i].run(err_buf, sizeof(err_buf));
        uint32_t t_elapsed = timer_get_us() - t_start;
        g_suite[i].execution_time_us = t_elapsed;

        if (res != TEST_RES_PASS) {
            all_passed = false;
        }

        /* Додавання результату до JSON */
        const char* status_str = (res == TEST_RES_PASS) ? "PASS" : "FAIL";
        strcat(report, "{\"test\":\"");
        strcat(report, g_suite[i].name);
        strcat(report, "\",\"status\":\"");
        strcat(report, status_str);
        strcat(report, "\"}");
        if (i + 1 < count) {
            strcat(report, ",");
        }
    }

    strcat(report, "],\"verdict\":\"");
    strcat(report, all_passed ? "PASS" : "FAIL");
    strcat(report, "\"}\r\n");

    uart_send_string(report);
}
