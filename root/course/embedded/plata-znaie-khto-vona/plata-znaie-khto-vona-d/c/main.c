#include <stdint.h>
#include <stdbool.h>

/* Перелік апаратних версій пристрою */
typedef enum {
    BOARD_HW_UNKNOWN = 0,
    BOARD_HW_REV_1   = 1, /* Початкова ревізія: давач BMI270, екран ST7789 */
    BOARD_HW_REV_2   = 2  /* Серійна ревізія: давач LSM6DSO, екран ILI9341 */
} board_hw_rev_t;

/* Вектор вимірювань інерції */
typedef struct {
    float x;
    float y;
    float z;
} vector3f_t;

/* Абстрактний інтерфейс драйвера IMU */
typedef struct {
    bool (*init)(void);
    bool (*get_accel)(vector3f_t *acc);
    bool (*get_gyro)(vector3f_t *gyr);
} imu_interface_t;

/* Дескриптор апаратної конфігурації друкованої плати */
typedef struct {
    board_hw_rev_t         revision;
    const char            *name;
    uint8_t                spi_channel;
    uint16_t               cs_gpio_pin;
    const imu_interface_t *imu_ops;
} board_bsp_config_t;

/* Зовнішні конкретні драйвери для різних чипів */
extern const imu_interface_t g_bmi270_ops;
extern const imu_interface_t g_lsm6dso_ops;

/* Статична таблиця конфігурацій, що компілюється у Flash */
static const board_bsp_config_t g_supported_boards[] = {
    {
        .revision    = BOARD_HW_REV_1,
        .name        = "Device-Rev1.0",
        .spi_channel = 1,
        .cs_gpio_pin = 4, /* PA4 */
        .imu_ops     = &g_bmi270_ops
    },
    {
        .revision    = BOARD_HW_REV_2,
        .name        = "Device-Rev2.0",
        .spi_channel = 2,
        .cs_gpio_pin = 12, /* PB12 */
        .imu_ops     = &g_lsm6dso_ops
    }
};

#define SUPPORTED_BOARDS_COUNT (sizeof(g_supported_boards) / sizeof(g_supported_boards[0]))

/* Глобальний активний дескриптор поточної плати */
static const board_bsp_config_t *g_active_bsp = 0;

/* Функція ініціалізації шару BSP за зчитаним Board ID */
bool bsp_system_init(board_hw_rev_t detected_rev) {
    for (size_t i = 0; i < SUPPORTED_BOARDS_COUNT; ++i) {
        if (g_supported_boards[i].revision == detected_rev) {
            g_active_bsp = &g_supported_boards[i];
            
            /* Ініціалізація апаратної частини згідно з картою пінів */
            /* hal_spi_init(g_active_bsp->spi_channel); */
            /* hal_gpio_init_output(g_active_bsp->cs_gpio_pin); */

            /* Запуск драйвера конкретної мікросхеми */
            return g_active_bsp->imu_ops->init();
        }
    }
    return false; /* Невідома або непідтримувана ревізія */
}

/* Уніфікований виклик для прикладного рівня */
bool sensor_read_acceleration(vector3f_t *out_acc) {
    if (!g_active_bsp || !g_active_bsp->imu_ops) {
        return false;
    }
    return g_active_bsp->imu_ops->get_accel(out_acc);
}
