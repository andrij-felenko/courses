/**
 * @file vl53l0x_array.c
 * @brief Реалізація драйвера масиву лазерних ToF-давачів VL53L0X.
 *
 * Драйвер забезпечує процедурне керування лініями XSHUT, перевірку завантаження внутрішнього
 * мікрокоду, запис нових I2C-адрес у регістр 0x8A, налаштування генерації переривань на
 * виводах GPIO1 (INT) та асинхронне вилучення виміряних дистанцій.
 */

#include "vl53l0x_array.h"

/* ========================================================================== */
/*                      ПРИВАТНІ ДОПОМІЖНІ ФУНКЦІЇ                            */
/* ========================================================================== */

/**
 * @brief Запис 8-бітного значення в регістр VL53L0X.
 */
static vl53l0x_err_t vl53l0x_write_reg(uint8_t dev_addr, uint8_t reg, uint8_t val)
{
    if (hal_i2c_write_reg(dev_addr, reg, val) != HAL_I2C_OK) {
        return VL53L0X_ERR_I2C;
    }
    return VL53L0X_OK;
}

/**
 * @brief Зчитання 8-бітного значення з регістра VL53L0X.
 */
static vl53l0x_err_t vl53l0x_read_reg(uint8_t dev_addr, uint8_t reg, uint8_t *p_val)
{
    if (hal_i2c_read_reg(dev_addr, reg, p_val) != HAL_I2C_OK) {
        return VL53L0X_ERR_I2C;
    }
    return VL53L0X_OK;
}

/**
 * @brief Базове налаштування SPAD-матриці (Single Photon Avalanche Diode) та внутрішніх регістрів.
 */
static vl53l0x_err_t vl53l0x_load_default_tuning(vl53l0x_dev_t *dev)
{
    vl53l0x_err_t status = VL53L0X_OK;
    uint8_t addr = dev->current_addr;

    /* Послідовність розконсервації внутрішнього блоку керування живленням та оптикою */
    status |= vl53l0x_write_reg(addr, 0x88, 0x00);
    status |= vl53l0x_write_reg(addr, 0x80, 0x01);
    status |= vl53l0x_write_reg(addr, 0xFF, 0x01);
    status |= vl53l0x_write_reg(addr, 0x00, 0x00);

    /* Налаштування порогових значень сигналу та чутливості SPAD */
    status |= vl53l0x_write_reg(addr, 0x91, 0x3C);
    status |= vl53l0x_write_reg(addr, 0x00, 0x01);
    status |= vl53l0x_write_reg(addr, 0xFF, 0x00);
    status |= vl53l0x_write_reg(addr, 0x80, 0x00);

    if (status != VL53L0X_OK) {
        return VL53L0X_ERR_CALIBRATION;
    }
    return VL53L0X_OK;
}

/* ========================================================================== */
/*                         ПУБЛІЧНІ ФУНКЦІЇ ДРАЙВЕРА                          */
/* ========================================================================== */

void vl53l0x_array_hardware_reset_all(VL53L0X_Array_t *arr)
{
    if (arr == NULL) {
        return;
    }

    for (uint8_t i = 0; i < arr->count; i++) {
        /* Примусове переведення лінії XSHUT у 0V повністю вимикає внутрішню периферію чипа */
        hal_gpio_write(arr->dev[i].xshut_pin, false);
        arr->dev[i].state = VL53L0X_STATE_SHUTDOWN;
        arr->dev[i].current_addr = VL53L0X_DEFAULT_I2C_ADDR;
        arr->dev[i].data_ready_flag = false;
        arr->dev[i].last_distance_mm = 0;
        arr->dev[i].range_status = 255;
    }

    /* Пауза для гарантованого розрядження ємностей живлення внутрішнього контролера */
    hal_delay_ms(10);
}

vl53l0x_err_t vl53l0x_sensor_poweron_and_readdress(vl53l0x_dev_t *dev, uint8_t new_i2c_addr)
{
    if (dev == NULL || new_i2c_addr == 0 || new_i2c_addr > 0x7F) {
        return VL53L0X_ERR_INVALID_PARAM;
    }

    /* 1. Виведення чипа зі стану скидання шляхом подачі HIGH на лінію XSHUT */
    hal_gpio_write(dev->xshut_pin, true);
    dev->state = VL53L0X_STATE_BOOTING;

    /* 2. Затримка t_boot (щонайменше 1.2 мс) для завантаження NVM ROM VL53L0X */
    hal_delay_ms(5);

    /* 3. Перевірка наявності чипа за стандартною фабричною адресою 0x29 */
    uint8_t model_id = 0;
    if (vl53l0x_read_reg(VL53L0X_DEFAULT_I2C_ADDR, VL53L0X_REG_IDENTIFICATION_MODEL_ID, &model_id) != VL53L0X_OK) {
        dev->state = VL53L0X_STATE_ERROR;
        dev->error_count++;
        return VL53L0X_ERR_I2C;
    }

    if (model_id != VL53L0X_EXPECTED_DEVICE_ID) {
        dev->state = VL53L0X_STATE_ERROR;
        dev->error_count++;
        return VL53L0X_ERR_WRONG_ID;
    }

    /* 4. Запис нової 7-бітної адреси у регістр I2C_SLAVE_DEVICE_ADDRESS (0x8A) */
    uint8_t reg_val = new_i2c_addr & 0x7FU;
    if (vl53l0x_write_reg(VL53L0X_DEFAULT_I2C_ADDR, VL53L0X_REG_I2C_SLAVE_DEVICE_ADDRESS, reg_val) != VL53L0X_OK) {
        dev->state = VL53L0X_STATE_ERROR;
        dev->error_count++;
        return VL53L0X_ERR_I2C;
    }

    /* Оновлюємо поточну адресу в контексті структури */
    dev->current_addr = new_i2c_addr;

    /* 5. Перевірка зворотного зв'язку за новою адресою */
    uint8_t verify_id = 0;
    if (vl53l0x_read_reg(dev->current_addr, VL53L0X_REG_IDENTIFICATION_MODEL_ID, &verify_id) != VL53L0X_OK ||
        verify_id != VL53L0X_EXPECTED_DEVICE_ID) {
        dev->state = VL53L0X_STATE_ERROR;
        dev->error_count++;
        return VL53L0X_ERR_I2C;
    }

    dev->state = VL53L0X_STATE_ADDRESS_ASSIGNED;
    return VL53L0X_OK;
}

vl53l0x_err_t vl53l0x_sensor_init_device(vl53l0x_dev_t *dev)
{
    if (dev == NULL || dev->state != VL53L0X_STATE_ADDRESS_ASSIGNED) {
        return VL53L0X_ERR_INVALID_PARAM;
    }

    /* 1. Завантаження базових тюнінг-параметрів SPAD-матриці */
    if (vl53l0x_load_default_tuning(dev) != VL53L0X_OK) {
        dev->state = VL53L0X_STATE_ERROR;
        return VL53L0X_ERR_CALIBRATION;
    }

    /* 2. Конфігурація генерації переривання GPIO1 (INT) за наявності нового вимірювання.
     * Значення 0x04 означає active-low / active-high сигнал при готовності нового кадру. */
    if (vl53l0x_write_reg(dev->current_addr, VL53L0X_REG_SYSTEM_INTERRUPT_CONFIG_GPIO, 0x04) != VL53L0X_OK) {
        dev->state = VL53L0X_STATE_ERROR;
        return VL53L0X_ERR_I2C;
    }

    /* 3. Первинне скидання прапорця переривання */
    if (vl53l0x_clear_interrupt(dev) != VL53L0X_OK) {
        dev->state = VL53L0X_STATE_ERROR;
        return VL53L0X_ERR_I2C;
    }

    dev->state = VL53L0X_STATE_READY;
    return VL53L0X_OK;
}

vl53l0x_err_t vl53l0x_array_init(VL53L0X_Array_t *arr, const uint8_t *target_addrs, uint8_t sensor_count)
{
    if (arr == NULL || target_addrs == NULL || sensor_count == 0 || sensor_count > VL53L0X_MAX_ARRAY_SIZE) {
        return VL53L0X_ERR_INVALID_PARAM;
    }

    arr->count = sensor_count;
    arr->is_initialized = false;

    /* 1. Переведення всіх сенсорів у стан апаратного скидання (XSHUT = LOW) */
    vl53l0x_array_hardware_reset_all(arr);

    /* 2. Послідовна розконсервація та налаштування кожного сенсора окремо */
    for (uint8_t i = 0; i < arr->count; i++) {
        vl53l0x_dev_t *dev = &arr->dev[i];
        dev->id = i;

        /* Розконсервація XSHUT та встановлення нової I2C адреси */
        vl53l0x_err_t err = vl53l0x_sensor_poweron_and_readdress(dev, target_addrs[i]);
        if (err != VL53L0X_OK) {
            return err;
        }

        /* Налаштування SPAD матриці та переривань */
        err = vl53l0x_sensor_init_device(dev);
        if (err != VL53L0X_OK) {
            return err;
        }
    }

    arr->is_initialized = true;
    return VL53L0X_OK;
}

vl53l0x_err_t vl53l0x_start_continuous(vl53l0x_dev_t *dev)
{
    if (dev == NULL || dev->state != VL53L0X_STATE_READY) {
        return VL53L0X_ERR_INVALID_PARAM;
    }

    /* Режим 0x02 переводить VL53L0X у безперервний цикл лазерних імпульсів і вимірювання ToF */
    if (vl53l0x_write_reg(dev->current_addr, VL53L0X_REG_SYSRANGE_START, 0x02) != VL53L0X_OK) {
        dev->state = VL53L0X_STATE_ERROR;
        return VL53L0X_ERR_I2C;
    }

    dev->state = VL53L0X_STATE_RANGING;
    return VL53L0X_OK;
}

vl53l0x_err_t vl53l0x_read_distance_async(vl53l0x_dev_t *dev, uint16_t *p_distance_mm)
{
    if (dev == NULL || p_distance_mm == NULL) {
        return VL53L0X_ERR_INVALID_PARAM;
    }

    /* Зчитаємо буфер 12 байтів починаючи з 0x14 (RESULT_RANGE_STATUS) для отримання статусу та відстані */
    uint8_t buffer[12];
    if (hal_i2c_read_multi(dev->current_addr, VL53L0X_REG_RESULT_RANGE_STATUS, buffer, 12) != HAL_I2C_OK) {
        dev->error_count++;
        return VL53L0X_ERR_I2C;
    }

    /* Апаратний статус вимірювання (біти [7:3] першого байта) */
    dev->range_status = (buffer[0] >> 3) & 0x0F;

    /* Дистанція в мм знаходиться у 10-му та 11-му байтах бувера (відповідає регістру 0x28 MSB, 0x29 LSB) */
    uint16_t raw_dist = ((uint16_t)buffer[10] << 8) | buffer[11];

    dev->last_distance_mm = raw_dist;
    *p_distance_mm = raw_dist;
    dev->read_count++;

    /* Обов'язкове скидання апаратного прапорця переривання у давачі для наступного заміру */
    vl53l0x_clear_interrupt(dev);

    /* Скидаємо програмний прапорець readiness */
    dev->data_ready_flag = false;

    return VL53L0X_OK;
}

vl53l0x_err_t vl53l0x_clear_interrupt(vl53l0x_dev_t *dev)
{
    if (dev == NULL) {
        return VL53L0X_ERR_INVALID_PARAM;
    }

    /* Запис 0x01 у регістр 0x0B скидає внутрішню засувку переривання VL53L0X */
    return vl53l0x_write_reg(dev->current_addr, VL53L0X_REG_SYSTEM_INTERRUPT_CLEAR, 0x01);
}
