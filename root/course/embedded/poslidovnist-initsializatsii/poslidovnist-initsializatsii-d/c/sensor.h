#ifndef SENSOR_H
#define SENSOR_H

#include <stdint.h>
#include <stdbool.h>

/* --- Регістрова карта навчального MEMS-давача ----------------------------
 * Карта стилізована, але замкнена сама на себе: рівно її реалізує модель чипа
 * в platform_sim.c. Типи доступу підписані так, як їх дає даташит.
 */
#define SENSOR_WHO_AM_I_VALUE 0x6CU

#define REG_RESET_CTRL 0x06U /* R/W: біт 7 SW_RESET, самоочисний */
#define REG_STATUS     0x07U /* RO:  біт 0 READY, біт 7 DRDY */
#define REG_WHO_AM_I   0x0FU /* RO:  заводський ідентифікатор моделі */
#define REG_INT_CFG    0x10U /* Крок 1: електрика виводу INT */
#define REG_RANGE      0x11U /* Крок 2: шкала і робочі осі */
#define REG_FILTER     0x12U /* Крок 3: ODR і смуга DLPF */
#define REG_INT_EN     0x13U /* Крок 4: маски переривань і режим FIFO */
#define REG_PWR        0x14U /* Крок 5: режим живлення */

#define BIT_SW_RESET     (1U << 7)
#define BIT_STATUS_READY (1U << 0)
#define BIT_STATUS_DRDY  (1U << 7)
#define BIT_FILTER_READY (1U << 7) /* RO всередині конфігураційного регістра */

/* Крок 1: вивід INT об'єднаний з іншим давачем у Wired-OR, отже Open-Drain */
#define INT_CFG_OPEN_DRAIN (1U << 0)
#define INT_CFG_ACTIVE_LOW (1U << 1)
#define INT_CFG_LATCHED    (1U << 2)
#define INT_CFG_CARE_MASK  0x07U

/* Крок 2: шкала ±8g, усі три осі увімкнені; біт 6 — фабрична константа 1 */
#define RANGE_FS_8G     (0x02U << 0)
#define RANGE_AXIS_XYZ  (0x07U << 2)
#define RANGE_CARE_MASK 0x1FU

/* Крок 3: ODR 104 Гц, DLPF 50 Гц; біт 7 віддає апаратний прапорець FILT_RDY */
#define FILTER_ODR_104HZ (0x04U << 0)
#define FILTER_DLPF_50HZ (0x02U << 4)
#define FILTER_CARE_MASK 0x3FU

/* Крок 4: переривання за готовністю даних, FIFO у режимі Stream */
#define INT_EN_DRDY      (1U << 0)
#define INT_EN_FIFO_WM   (1U << 1)
#define FIFO_MODE_STREAM (0x02U << 2)
#define INT_EN_CARE_MASK 0x0FU

/* Крок 5: режим живлення та час прогріву аналогового фронтенду */
#define PWR_MODE_STANDBY   0x00U
#define PWR_MODE_NORMAL    0x01U
#define PWR_MODE_CARE_MASK 0x03U
#define T_SETTLING_MS      25U

/* --- Типи драйвера ------------------------------------------------------ */

typedef enum {
    INIT_OK = 0,
    INIT_ERR_BUS,      /* NACK або залипла шина */
    INIT_ERR_TIMEOUT,  /* чип не підняв прапорець готовності у відведений час */
    INIT_ERR_WRONG_ID, /* на адресі відповідає не той кремній */
    INIT_ERR_VERIFY    /* Read-Back показав, що конфігурація не зафіксувалась */
} init_result_t;

const char *init_result_str(init_result_t result);

typedef enum {
    DEVICE_STATE_UNINITIALIZED = 0,
    DEVICE_STATE_READY,
    DEVICE_STATE_FAULT
} device_state_t;

/* Неблокуюча витримка часу виходу на режим після подачі VDD */
typedef struct {
    uint32_t power_on_timestamp;
    bool     power_stable;
} sensor_power_guard_t;

/* Одне поле конфігурації разом із маскою значущих (R/W) розрядів */
typedef struct {
    uint8_t reg_addr;
    uint8_t target_val;
    uint8_t care_mask;
} reg_verify_entry_t;

typedef struct {
    uint8_t        addr;
    const char    *name;
    bool           critical;   /* чи блокує його відмова роботу виробу */
    uint32_t       boot_ms;    /* t_boot із даташита плюс запас */
    device_state_t state;
    init_result_t  last_error;
    uint8_t        attempts_used;
} sensor_t;

/* power_guard.c */
void sensor_start_power_timer(sensor_power_guard_t *guard);
bool sensor_is_power_ready(sensor_power_guard_t *guard, uint32_t required_boot_ms);
void sensor_power_off(sensor_power_guard_t *guard);

/* sensor_probe.c */
init_result_t sensor_software_reset(uint8_t dev_addr);
init_result_t sensor_check_id(uint8_t dev_addr);
init_result_t sensor_data_ready(uint8_t dev_addr, bool *out_ready);

/* sensor_config.c */
init_result_t sensor_write_verified(uint8_t dev_addr, const reg_verify_entry_t *entry);
init_result_t sensor_apply_config(uint8_t dev_addr, uint8_t *out_failed_reg);

/* bus_recovery.c */
void i2c_bus_recover(uint8_t dev_addr);

/* sensor_bringup.c */
init_result_t sensor_bringup(sensor_t *dev);
void sensor_rollback(sensor_t *dev, init_result_t reason);

#endif /* SENSOR_H */
