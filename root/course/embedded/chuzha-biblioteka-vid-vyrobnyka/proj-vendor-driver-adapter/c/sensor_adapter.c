/*
 * Ізолюючий адаптер: єдине місце у прошивці, де взагалі згадується
 * вендорський SDK. Далі за цей файл його типи не виходять.
 */
#include "sensor_adapter.h"

#include "rtos_port.h"
#include "vendor/vendor_sensor.h"

#include <string.h>

#define ADAPTER_POOL_SIZE   2U
#define MEASURE_TIMEOUT_MS  200U
#define MEASURE_POLL_US     2000U

struct sensor_adapter {
    vendor_sensor_dev_t vendor_dev;  /* стан чужого драйвера живе тут */
    sys_i2c_bus_t *bus;
    sys_mutex_t lock;
    uint8_t i2c_addr;
    bool in_use;
    bool initialized;
};

/*
 * Статичний пул замість купи: пам'ять дескрипторів відома компонувальнику,
 * а не з'ясовується в польоті. Слотів рівно стільки, скільки давачів на платі.
 */
static struct sensor_adapter g_pool[ADAPTER_POOL_SIZE];

/* --- Містки: єдиний код, який знає, що колбек і шина — різні світи. --- */

static int8_t bridge_read(uint8_t reg_addr, uint8_t *data, uint32_t len,
                          void *intf_ptr)
{
    struct sensor_adapter *adapter;

    if (intf_ptr == NULL || data == NULL || len == 0U) {
        return VENDOR_E_NULL_PTR;
    }
    /* intf_ptr — це той самий вказівник, який ми поклали в дескриптор:
       так статична функція без параметрів стану знаходить свою шину. */
    adapter = (struct sensor_adapter *)intf_ptr;
    return adapter->bus->read_reg(adapter->bus->bus_ctx, adapter->i2c_addr,
                                  reg_addr, data, (size_t)len)
               ? VENDOR_OK
               : VENDOR_E_COMM_FAIL;
}

static int8_t bridge_write(uint8_t reg_addr, const uint8_t *data, uint32_t len,
                           void *intf_ptr)
{
    struct sensor_adapter *adapter;

    if (intf_ptr == NULL || data == NULL || len == 0U) {
        return VENDOR_E_NULL_PTR;
    }
    adapter = (struct sensor_adapter *)intf_ptr;
    return adapter->bus->write_reg(adapter->bus->bus_ctx, adapter->i2c_addr,
                                   reg_addr, data, (size_t)len)
               ? VENDOR_OK
               : VENDOR_E_COMM_FAIL;
}

static void bridge_delay(uint32_t period_us, void *intf_ptr)
{
    (void)intf_ptr;   /* затримка глобальна, контекст їй не потрібен */
    sys_delay_us(period_us);
}

/* Переклад кодів SDK у системні: вендорські числа далі не йдуть. */
static sys_status_t map_vendor_error(int8_t rc)
{
    switch (rc) {
    case VENDOR_OK:             return SYS_OK;
    case VENDOR_E_NULL_PTR:     return SYS_ERR_PARAM;
    case VENDOR_E_COMM_FAIL:    return SYS_ERR_COMM;
    case VENDOR_E_DEV_NOT_FOUND: return SYS_ERR_DEVICE;
    case VENDOR_E_CALIB:        return SYS_ERR_CALIB;
    default:                    return SYS_ERR_COMM;
    }
}

static struct sensor_adapter *take_slot(void)
{
    for (uint32_t i = 0U; i < ADAPTER_POOL_SIZE; ++i) {
        if (!g_pool[i].in_use) {
            memset(&g_pool[i], 0, sizeof(g_pool[i]));
            g_pool[i].in_use = true;
            return &g_pool[i];
        }
    }
    return NULL;
}

static void give_slot(struct sensor_adapter *adapter)
{
    sys_mutex_destroy(&adapter->lock);
    memset(adapter, 0, sizeof(*adapter));
    adapter->in_use = false;
}

sys_status_t sensor_adapter_acquire(sys_i2c_bus_t *bus, uint8_t i2c_addr,
                                    sensor_adapter_t **out)
{
    struct sensor_adapter *adapter;
    int8_t rc;

    if (bus == NULL || bus->read_reg == NULL || bus->write_reg == NULL ||
        out == NULL) {
        return SYS_ERR_PARAM;
    }
    *out = NULL;

    adapter = take_slot();
    if (adapter == NULL) {
        return SYS_ERR_NO_SLOT;
    }
    if (!sys_mutex_init(&adapter->lock)) {
        adapter->in_use = false;
        return SYS_ERR_NO_SLOT;
    }

    adapter->bus = bus;
    adapter->i2c_addr = i2c_addr;

    /* Прив'язка: адреса слота лягає в intf_ptr, і саме її драйвер поверне
       в кожен колбек. Тому слот не можна ні копіювати, ні переносити. */
    adapter->vendor_dev.intf_ptr = adapter;
    adapter->vendor_dev.read = bridge_read;
    adapter->vendor_dev.write = bridge_write;
    adapter->vendor_dev.delay_us = bridge_delay;

    rc = vendor_sensor_init(&adapter->vendor_dev);
    if (rc != VENDOR_OK) {
        /* Чип не піднявся — слот не лишаємо зайнятим. */
        give_slot(adapter);
        return map_vendor_error(rc);
    }

    adapter->initialized = true;
    *out = adapter;
    return SYS_OK;
}

void sensor_adapter_release(sensor_adapter_t *adapter)
{
    if (adapter == NULL || !adapter->in_use) {
        return;
    }
    if (adapter->initialized) {
        /* Сон — не косметика: у режимі normal чип продовжує міряти
           й тягнути струм навіть після того, як прошивка про нього забула.
           Код повернення тут вже нічого не змінює: шини може не бути. */
        (void)vendor_sensor_set_mode(&adapter->vendor_dev, VENDOR_MODE_SLEEP);
    }
    give_slot(adapter);
}

sys_status_t sensor_adapter_read(sensor_adapter_t *adapter, sensor_data_t *out)
{
    vendor_data_t raw = {0};
    sys_status_t st = SYS_OK;
    uint32_t started_ms;
    int8_t rc;

    if (adapter == NULL || out == NULL) {
        return SYS_ERR_PARAM;
    }
    memset(out, 0, sizeof(*out));   /* на будь-якій помилці читач бачить нулі */
    if (!adapter->initialized) {
        return SYS_ERR_PARAM;
    }

    if (!sys_mutex_lock(&adapter->lock)) {
        return SYS_ERR_COMM;
    }

    rc = vendor_sensor_set_mode(&adapter->vendor_dev, VENDOR_MODE_FORCED);
    if (rc != VENDOR_OK) {
        st = map_vendor_error(rc);
        goto unlock;
    }

    started_ms = sys_uptime_ms();
    for (;;) {
        uint8_t busy = 0U;

        rc = vendor_sensor_is_measuring(&adapter->vendor_dev, &busy);
        if (rc != VENDOR_OK) {
            st = map_vendor_error(rc);
            goto unlock;
        }
        if (busy == 0U) {
            break;
        }
        /* Опитування без стелі — це зависла задача. Різниця беззнакових
           лічильників коректна й через переповнення uptime. */
        if ((uint32_t)(sys_uptime_ms() - started_ms) > MEASURE_TIMEOUT_MS) {
            st = SYS_ERR_TIMEOUT;
            goto unlock;
        }
        sys_delay_us(MEASURE_POLL_US);
    }

    rc = vendor_sensor_get_data(&adapter->vendor_dev, &raw);
    if (rc != VENDOR_OK) {
        st = map_vendor_error(rc);
        goto unlock;
    }

    /* Переклад в SI: вендорський Q24.8 стає цілими Паскалями з округленням. */
    out->temperature_centi_deg = raw.temperature;
    out->pressure_pa = (uint32_t)((raw.pressure_q24_8 + 128U) / 256U);

unlock:
    /* Єдиний вихід із функції: блокування звільняється й на помилці теж. */
    sys_mutex_unlock(&adapter->lock);
    if (st != SYS_OK) {
        memset(out, 0, sizeof(*out));
    }
    return st;
}
