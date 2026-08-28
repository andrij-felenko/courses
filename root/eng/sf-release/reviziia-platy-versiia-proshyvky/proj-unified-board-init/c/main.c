#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Перелік підтримуваних апаратних ревізій */
typedef enum {
    BOARD_REV_UNKNOWN = 0,
    BOARD_REV_A       = 1,
    BOARD_REV_B       = 2,
    BOARD_REV_C       = 3
} board_rev_t;

/* Структура сирих даних акселерометра */
typedef struct {
    int16_t x;
    int16_t y;
    int16_t z;
} imu_raw_data_t;

/* Таблиця віртуальних методів (VTable) для сенсора IMU */
typedef struct {
    bool (*init)(void);
    bool (*read_accel)(imu_raw_data_t *data);
    bool (*sleep)(void);
} imu_ops_t;

/* Таблиця віртуальних методів для мікросхеми Flash-пам'яті */
typedef struct {
    bool (*init)(uint8_t cs_pin);
    bool (*read)(uint32_t addr, uint8_t *buf, size_t len);
    bool (*write)(uint32_t addr, const uint8_t *buf, size_t len);
    bool (*erase_sector)(uint32_t addr);
} flash_ops_t;

/* Дескриптор апаратної ревізії плати */
typedef struct {
    board_rev_t rev;
    const char *name;
    uint8_t spi_cs_pin;
    const imu_ops_t *imu_driver;
    const flash_ops_t *flash_driver;
} board_descriptor_t;

/* --- Драйвер Bosch BMI160 (Rev A) --- */
static bool bmi160_init(void) { return true; }
static bool bmi160_read_accel(imu_raw_data_t *d) { d->x = 10; d->y = 20; d->z = 980; return true; }
static bool bmi160_sleep(void) { return true; }

static const imu_ops_t g_bmi160_ops = {
    .init = bmi160_init,
    .read_accel = bmi160_read_accel,
    .sleep = bmi160_sleep
};

/* --- Драйвер Bosch BMI270 (Rev B / C) --- */
static bool bmi270_init(void) { return true; }
static bool bmi270_read_accel(imu_raw_data_t *d) { d->x = 12; d->y = 22; d->z = 981; return true; }
static bool bmi270_sleep(void) { return true; }

static const imu_ops_t g_bmi270_ops = {
    .init = bmi270_init,
    .read_accel = bmi270_read_accel,
    .sleep = bmi270_sleep
};

/* --- Драйвер Winbond W25Q128 (Rev A / B) --- */
static bool w25q_init(uint8_t cs) { (void)cs; return true; }
static bool w25q_read(uint32_t a, uint8_t *b, size_t l) { (void)a; (void)b; (void)l; return true; }
static bool w25q_write(uint32_t a, const uint8_t *b, size_t l) { (void)a; (void)b; (void)l; return true; }
static bool w25q_erase(uint32_t a) { (void)a; return true; }

static const flash_ops_t g_w25q_ops = {
    .init = w25q_init,
    .read = w25q_read,
    .write = w25q_write,
    .erase_sector = w25q_erase
};

/* --- Драйвер Macronix MX25L128 (Rev C) --- */
static bool mx25l_init(uint8_t cs) { (void)cs; return true; }
static bool mx25l_read(uint32_t a, uint8_t *b, size_t l) { (void)a; (void)b; (void)l; return true; }
static bool mx25l_write(uint32_t a, const uint8_t *b, size_t l) { (void)a; (void)b; (void)l; return true; }
static bool mx25l_erase(uint32_t a) { (void)a; return true; }

static const flash_ops_t g_mx25l_ops = {
    .init = mx25l_init,
    .read = mx25l_read,
    .write = mx25l_write,
    .erase_sector = mx25l_erase
};

/* Статична таблиця конфігурацій (розміщується у .rodata пам'яті Flash) */
static const board_descriptor_t BOARD_REGISTRY[] = {
    { BOARD_REV_A, "Rev A (2023)", 4,  &g_bmi160_ops, &g_w25q_ops },
    { BOARD_REV_B, "Rev B (2024)", 4,  &g_bmi270_ops, &g_w25q_ops },
    { BOARD_REV_C, "Rev C (2025)", 13, &g_bmi270_ops, &g_mx25l_ops }
};

#define BOARD_REGISTRY_SIZE (sizeof(BOARD_REGISTRY) / sizeof(BOARD_REGISTRY[0]))

/* Поточний активний контекст плати */
typedef struct {
    const board_descriptor_t *descriptor;
    bool is_initialized;
} board_context_t;

static board_context_t g_board_ctx;

/* Апаратне зчитування та класифікація коду ADC */
static board_rev_t board_detect_revision_from_adc(uint16_t adc_counts) {
    if (adc_counts < 400) {
        return BOARD_REV_A;      /* 0.0V (GND) */
    } else if (adc_counts >= 1700 && adc_counts <= 2400) {
        return BOARD_REV_B;      /* 1.65V (VDD / 2) */
    } else if (adc_counts >= 3700) {
        return BOARD_REV_C;      /* 3.3V (VDD) */
    }
    return BOARD_REV_UNKNOWN;    /* Некоректний рівень напруги */
}

/* Головна функція раннього зв'язування на етапі запуску */
bool board_early_init(uint16_t adc_raw_value) {
    board_rev_t rev = board_detect_revision_from_adc(adc_raw_value);
    if (rev == BOARD_REV_UNKNOWN) {
        g_board_ctx.descriptor = NULL;
        g_board_ctx.is_initialized = false;
        return false;
    }

    for (size_t i = 0; i < BOARD_REGISTRY_SIZE; ++i) {
        if (BOARD_REGISTRY[i].rev == rev) {
            g_board_ctx.descriptor = &BOARD_REGISTRY[i];
            
            /* Ініціалізація периферії через відповідні VTable */
            bool imu_ok = g_board_ctx.descriptor->imu_driver->init();
            bool flash_ok = g_board_ctx.descriptor->flash_driver->init(
                g_board_ctx.descriptor->spi_cs_pin
            );
            
            g_board_ctx.is_initialized = (imu_ok && flash_ok);
            return g_board_ctx.is_initialized;
        }
    }

    return false;
}

/* Публічні уніфіковані виклики для прикладного коду */
bool board_imu_get_acceleration(imu_raw_data_t *out_data) {
    if (!g_board_ctx.is_initialized || !g_board_ctx.descriptor) {
        return false;
    }
    return g_board_ctx.descriptor->imu_driver->read_accel(out_data);
}
