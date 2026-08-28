#include <stdint.h>
#include <stdbool.h>

/* Абстрактний інтерфейс операцій акселерометра */
typedef struct {
    bool (*init)(void);
    bool (*get_axes)(int16_t *x, int16_t *y, int16_t *z);
    bool (*set_power_mode)(uint8_t mode);
} accel_driver_ops_t;

/* --- Реалізація для ревізії Rev A (BMI160) --- */
static bool bmi160_init_hw(void) {
    /* Запис у регістри BMI160 через I2C адресу 0x68 */
    return true;
}

static bool bmi160_read_hw(int16_t *x, int16_t *y, int16_t *z) {
    *x = 0; *y = 0; *z = 1000;
    return true;
}

const accel_driver_ops_t g_bmi160_driver = {
    .init = bmi160_init_hw,
    .get_axes = bmi160_read_hw,
    .set_power_mode = NULL
};

/* --- Реалізація для ревізій Rev B та Rev C (BMI270) --- */
static bool bmi270_init_hw(void) {
    /* Завантаження мікрокоду ініціалізації в BMI270 через адресу 0x69 */
    return true;
}

static bool bmi270_read_hw(int16_t *x, int16_t *y, int16_t *z) {
    *x = 1; *y = -1; *z = 998;
    return true;
}

const accel_driver_ops_t g_bmi270_driver = {
    .init = bmi270_init_hw,
    .get_axes = bmi270_read_hw,
    .set_power_mode = NULL
};

/* Глобальний покажчик активного драйвера */
static const accel_driver_ops_t *g_active_accel = NULL;

/* Ініціалізація активного драйвера за результатами детектування */
bool board_bind_accel_driver(uint8_t board_rev) {
    if (board_rev == 1) {             /* Rev A */
        g_active_accel = &g_bmi160_driver;
    } else if (board_rev == 2 || board_rev == 3) { /* Rev B або Rev C */
        g_active_accel = &g_bmi270_driver;
    } else {
        g_active_accel = NULL;
        return false;
    }
    return g_active_accel->init();
}

/* Публічна функція для прикладного рівня: чистий виклик без жодних if-else */
bool sensor_get_acceleration(int16_t *x, int16_t *y, int16_t *z) {
    if (!g_active_accel || !g_active_accel->get_axes) {
        return false;
    }
    return g_active_accel->get_axes(x, y, z);
}
