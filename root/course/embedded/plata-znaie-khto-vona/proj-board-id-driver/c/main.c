#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Перелік підтримуваних ревізій плати */
typedef enum {
    BOARD_REV_UNKNOWN = 0x00,
    BOARD_REV_A       = 0x01, /* Прототип: BMI270 на SPI1, Display ST7789  */
    BOARD_REV_B       = 0x02, /* Серія: LSM6DSO на SPI2, Display ILI9341   */
    BOARD_REV_C       = 0x03, /* Оптимізована: ICM42688 на SPI1, ST7789V3  */
    BOARD_REV_COUNT
} board_rev_t;

/* Тристабільний стан конфігураційного піна */
typedef enum {
    PIN_STATE_PULL_DOWN = 0, /* Зовнішній резистор на GND */
    PIN_STATE_PULL_UP   = 1, /* Зовнішній резистор на VDD */
    PIN_STATE_FLOATING  = 2  /* Вивід не підключений (Hi-Z) */
} pin_tristate_t;

/* Діапазон напруг для АЦП-селектора ревізії (12-бітний АЦП, Vref = 3300 мВ) */
typedef struct {
    uint16_t    raw_min;   /* Нижній поріг коду АЦП */
    uint16_t    raw_max;   /* Верхній поріг коду АЦП */
    board_rev_t revision;  /* Відповідна ревізія */
} adc_rev_window_t;

/* Абстрактний інтерфейс давача інерції (IMU) */
typedef struct imu_driver_s imu_driver_t;
struct imu_driver_s {
    bool (*init)(void);
    bool (*read_accel)(float *x, float *y, float *z);
    bool (*read_gyro)(float *x, float *y, float *z);
    void (*sleep)(void);
};

/* Дескриптор апаратної конфігурації конкретної плати */
typedef struct {
    board_rev_t         revision;
    const char         *board_name;
    uint8_t             spi_bus_index;
    uint16_t            cs_pin_mask;
    float               accel_gain_correction;
    const imu_driver_t *imu_driver;
} board_descriptor_t;

/* Апаратно-залежні заглушки периферії */
extern uint16_t hal_adc_read_raw(uint8_t channel);
extern void     hal_gpio_set_mode_input(uint8_t pin);
extern void     hal_gpio_set_pullup(uint8_t pin);
extern void     hal_gpio_set_pulldown(uint8_t pin);
extern void     hal_gpio_set_floating(uint8_t pin);
extern bool     hal_gpio_read(uint8_t pin);
extern void     hal_delay_us(uint32_t us);

/* Таблиця вікон напруг для 4 можливих ревізій на 1 піні АЦП */
static const adc_rev_window_t g_adc_rev_windows[] = {
    { .raw_min = 0,    .raw_max = 500,  .revision = BOARD_REV_A }, /* ~0.2 В: дільник 100k/6.8k */
    { .raw_min = 800,  .raw_max = 1400, .revision = BOARD_REV_B }, /* ~0.9 В: дільник 100k/39k  */
    { .raw_min = 1700, .raw_max = 2300, .revision = BOARD_REV_C }, /* ~1.65 В: дільник 100k/100k */
};

#define ADC_WINDOW_COUNT (sizeof(g_adc_rev_windows) / sizeof(g_adc_rev_windows[0]))
#define ADC_OVERSAMPLE_COUNT 16

/* Сортування масиву для обчислення медіани */
static void sort_u16(uint16_t *buf, size_t len) {
    for (size_t i = 0; i < len - 1; ++i) {
        for (size_t j = i + 1; j < len; ++j) {
            if (buf[i] > buf[j]) {
                uint16_t tmp = buf[i];
                buf[i] = buf[j];
                buf[j] = tmp;
            }
        }
    }
}

/* Зчитування ревізії через резистивний дільник АЦП */
board_rev_t board_id_read_adc(uint8_t adc_channel) {
    uint16_t samples[ADC_OVERSAMPLE_COUNT];

    for (size_t i = 0; i < ADC_OVERSAMPLE_COUNT; ++i) {
        samples[i] = hal_adc_read_raw(adc_channel);
        hal_delay_us(50);
    }

    sort_u16(samples, ADC_OVERSAMPLE_COUNT);
    /* Беремо медіану для відкидання імпульсних наведень */
    uint16_t median_val = samples[ADC_OVERSAMPLE_COUNT / 2];

    for (size_t i = 0; i < ADC_WINDOW_COUNT; ++i) {
        if (median_val >= g_adc_rev_windows[i].raw_min &&
            median_val <= g_adc_rev_windows[i].raw_max) {
            return g_adc_rev_windows[i].revision;
        }
    }
    return BOARD_REV_UNKNOWN;
}

/* Тристабільне детектування стану одного цифрового піна */
pin_tristate_t board_id_detect_pin_tristate(uint8_t pin) {
    hal_gpio_set_mode_input(pin);

    /* Тест 1: вмикаємо внутрішню підтяжку до живлення */
    hal_gpio_set_pullup(pin);
    hal_delay_us(100);
    bool read_with_pullup = hal_gpio_read(pin);

    /* Тест 2: вмикаємо внутрішню підтяжку до землі */
    hal_gpio_set_pulldown(pin);
    hal_delay_us(100);
    bool read_with_pulldown = hal_gpio_read(pin);

    /* Відключаємо підтяжки для запобігання витоку струму */
    hal_gpio_set_floating(pin);

    if (read_with_pullup && !read_with_pulldown) {
        /* Лінія повторила внутрішню підтяжку -> зовнішнього резистора немає */
        return PIN_STATE_FLOATING;
    } else if (read_with_pullup && read_with_pulldown) {
        /* Лінія завжди HIGH -> зовнішній резистор до VDD переміг внутрішній pull-down */
        return PIN_STATE_PULL_UP;
    } else {
        /* Лінія завжди LOW -> зовнішній резистор до GND переміг внутрішній pull-up */
        return PIN_STATE_PULL_DOWN;
    }
}

/* Реалізації драйверів IMU для різних ревізій */
static bool bmi270_init(void) { /* Ініціалізація BMI270 */ return true; }
static bool bmi270_read_acc(float *x, float *y, float *z) { *x = 0.0f; *y = 0.0f; *z = 1.0f; return true; }
static bool bmi270_read_gyr(float *x, float *y, float *z) { *x = 0.0f; *y = 0.0f; *z = 0.0f; return true; }
static void bmi270_sleep(void) {}

static const imu_driver_t g_bmi270_driver = {
    .init = bmi270_init, .read_accel = bmi270_read_acc,
    .read_gyro = bmi270_read_gyr, .sleep = bmi270_sleep
};

static bool lsm6dso_init(void) { /* Ініціалізація LSM6DSO */ return true; }
static bool lsm6dso_read_acc(float *x, float *y, float *z) { *x = 0.01f; *y = -0.02f; *z = 0.99f; return true; }
static bool lsm6dso_read_gyr(float *x, float *y, float *z) { *x = 0.0f; *y = 0.0f; *z = 0.0f; return true; }
static void lsm6dso_sleep(void) {}

static const imu_driver_t g_lsm6dso_driver = {
    .init = lsm6dso_init, .read_accel = lsm6dso_read_acc,
    .read_gyro = lsm6dso_read_gyr, .sleep = lsm6dso_sleep
};

/* Статична таблиця дескрипторів плат у Flash-пам'яті */
static const board_descriptor_t g_board_descriptors[] = {
    {
        .revision              = BOARD_REV_A,
        .board_name            = "SensorNode-v1.2-RevA",
        .spi_bus_index         = 1,
        .cs_pin_mask           = (1u << 4),
        .accel_gain_correction = 1.002f,
        .imu_driver            = &g_bmi270_driver,
    },
    {
        .revision              = BOARD_REV_B,
        .board_name            = "SensorNode-v2.0-RevB",
        .spi_bus_index         = 2,
        .cs_pin_mask           = (1u << 12),
        .accel_gain_correction = 0.995f,
        .imu_driver            = &g_lsm6dso_driver,
    }
};

#define DESCRIPTORS_COUNT (sizeof(g_board_descriptors) / sizeof(g_board_descriptors[0]))

/* Пошук дескриптора за ревізією */
const board_descriptor_t *bsp_get_descriptor(board_rev_t rev) {
    for (size_t i = 0; i < DESCRIPTORS_COUNT; ++i) {
        if (g_board_descriptors[i].revision == rev) {
            return &g_board_descriptors[i];
        }
    }
    return NULL;
}
