#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Регістри та константи гіпотетичного MEMS-давача */
#define DEV_I2C_ADDR             (0x68U)
#define REG_CHIP_ID              (0x00U)
#define EXPECTED_CHIP_ID         (0xEA)

#define REG_RESET_CTRL           (0x10U)
#define BIT_SW_RESET             (1U << 7)
#define BIT_DEVICE_READY         (1U << 0)

#define REG_RANGE_CTRL           (0x18U)
#define REG_ODR_FILTER           (0x19U)
#define REG_PWR_MODE             (0x1AU)
#define VAL_PWR_ACTIVE           (0x01U)

/* Часові параметри bring-up (у мілісекундах) */
#define TIME_POR_BOOT_MS         (25U)
#define TIME_RESET_WAIT_MS       (10U)
#define TIME_POLL_TIMEOUT_MS     (100U)
#define TIME_ANALOG_SETTLE_MS    (15U)
#define MAX_INIT_RETRIES         (3U)
#define BASE_BACKOFF_MS          (50U)

/* Типи результатів виконання операцій */
typedef enum {
    BUS_OK = 0,
    BUS_ERR_NACK,
    BUS_ERR_TIMEOUT
} bus_status_t;

/* Стани кінцевого автомата ініціалізації */
typedef enum {
    FSM_STATE_POWER_ON_DELAY = 0,
    FSM_STATE_SEND_RESET,
    FSM_STATE_POLL_READY,
    FSM_STATE_VERIFY_CHIP_ID,
    FSM_STATE_WRITE_CONFIG,
    FSM_STATE_READBACK_VERIFY,
    FSM_STATE_ACTIVATE,
    FSM_STATE_SETTLING_DELAY,
    FSM_STATE_READY,
    FSM_STATE_RETRY_BACKOFF,
    FSM_STATE_FAULT_SAFE
} dev_fsm_state_t;

/* Елемент таблиці конфігурації регістрів */
typedef struct {
    uint8_t reg;
    uint8_t val;
    uint8_t mask; /* Маска значущих бітів для Read-Back (без RO/Reserved) */
} reg_config_entry_t;

/* Контекст драйвера пристрою */
typedef struct {
    dev_fsm_state_t state;
    uint32_t state_enter_time;
    uint32_t timeout_time;
    uint8_t config_idx;
    uint8_t retry_count;
    bool fault_flag;
} dev_driver_t;

/* Таблиця конфігурації робочих параметрів */
static const reg_config_entry_t INIT_CONFIG_TABLE[] = {
    { REG_RANGE_CTRL, 0x02U, 0x0FU }, /* Діапазон ±4g, маска бітів 0..3 */
    { REG_ODR_FILTER, 0x34U, 0x7FU }, /* ODR 100 Гц + фільтр DLPF 40 Гц */
};
#define CONFIG_TABLE_SIZE (sizeof(INIT_CONFIG_TABLE) / sizeof(INIT_CONFIG_TABLE[0]))

/* Прототипи апаратних функцій шини (надаються BSP/HAL) */
extern uint32_t platform_get_millis(void);
extern bus_status_t platform_i2c_write(uint8_t dev_addr, uint8_t reg, uint8_t val);
extern bus_status_t platform_i2c_read(uint8_t dev_addr, uint8_t reg, uint8_t *val);
extern void platform_bus_recover(void);
extern void platform_notify_fault(const char *reason);

/* Ініціалізація структури драйвера */
void dev_driver_init(dev_driver_t *drv) {
    drv->state = FSM_STATE_POWER_ON_DELAY;
    drv->state_enter_time = platform_get_millis();
    drv->timeout_time = 0;
    drv->config_idx = 0;
    drv->retry_count = 0;
    drv->fault_flag = false;
}

/* Перехід автомата в стан повторної спроби або фатальної аварії */
static void trigger_retry_or_fail(dev_driver_t *drv, const char *reason) {
    drv->retry_count++;
    if (drv->retry_count <= MAX_INIT_RETRIES) {
        platform_bus_recover();
        drv->state = FSM_STATE_RETRY_BACKOFF;
        drv->state_enter_time = platform_get_millis();
        /* Експоненційний відкат: 50 мс, 100 мс, 200 мс */
        drv->timeout_time = BASE_BACKOFF_MS * (1U << (drv->retry_count - 1U));
    } else {
        drv->state = FSM_STATE_FAULT_SAFE;
        drv->fault_flag = true;
        platform_notify_fault(reason);
    }
}

/* Неблокуючий крок ітерації автомата (викликається в головному циклі) */
void dev_driver_step(dev_driver_t *drv) {
    uint32_t now = platform_get_millis();
    uint8_t val = 0;

    switch (drv->state) {
        case FSM_STATE_POWER_ON_DELAY:
            if ((now - drv->state_enter_time) >= TIME_POR_BOOT_MS) {
                drv->state = FSM_STATE_SEND_RESET;
            }
            break;

        case FSM_STATE_SEND_RESET:
            if (platform_i2c_write(DEV_I2C_ADDR, REG_RESET_CTRL, BIT_SW_RESET) == BUS_OK) {
                drv->state = FSM_STATE_POLL_READY;
                drv->state_enter_time = now;
                drv->timeout_time = now + TIME_POLL_TIMEOUT_MS;
            } else {
                trigger_retry_or_fail(drv, "NACK on SW_RESET");
            }
            break;

        case FSM_STATE_POLL_READY:
            /* Перші кілька мілісекунд чип перезапускається і може давати NACK */
            if ((now - drv->state_enter_time) < TIME_RESET_WAIT_MS) {
                break;
            }
            if (platform_i2c_read(DEV_I2C_ADDR, REG_RESET_CTRL, &val) == BUS_OK) {
                /* Самоочищення біта скидання та готовність ядра */
                if ((val & BIT_SW_RESET) == 0 && (val & BIT_DEVICE_READY)) {
                    drv->state = FSM_STATE_VERIFY_CHIP_ID;
                }
            }
            if (now > drv->timeout_time && drv->state == FSM_STATE_POLL_READY) {
                trigger_retry_or_fail(drv, "Timeout waiting for ready flag");
            }
            break;

        case FSM_STATE_VERIFY_CHIP_ID:
            if (platform_i2c_read(DEV_I2C_ADDR, REG_CHIP_ID, &val) == BUS_OK) {
                if (val == EXPECTED_CHIP_ID) {
                    drv->config_idx = 0;
                    drv->state = FSM_STATE_WRITE_CONFIG;
                } else {
                    trigger_retry_or_fail(drv, "Invalid CHIP_ID");
                }
            } else {
                trigger_retry_or_fail(drv, "Bus error reading CHIP_ID");
            }
            break;

        case FSM_STATE_WRITE_CONFIG:
            if (drv->config_idx < CONFIG_TABLE_SIZE) {
                const reg_config_entry_t *entry = &INIT_CONFIG_TABLE[drv->config_idx];
                if (platform_i2c_write(DEV_I2C_ADDR, entry->reg, entry->val) == BUS_OK) {
                    drv->state = FSM_STATE_READBACK_VERIFY;
                } else {
                    trigger_retry_or_fail(drv, "Write config error");
                }
            } else {
                drv->state = FSM_STATE_ACTIVATE;
            }
            break;

        case FSM_STATE_READBACK_VERIFY: {
            const reg_config_entry_t *entry = &INIT_CONFIG_TABLE[drv->config_idx];
            if (platform_i2c_read(DEV_I2C_ADDR, entry->reg, &val) == BUS_OK) {
                /* Порівнюємо виключно біти за маскою */
                if ((val & entry->mask) == (entry->val & entry->mask)) {
                    drv->config_idx++;
                    drv->state = FSM_STATE_WRITE_CONFIG;
                } else {
                    trigger_retry_or_fail(drv, "Read-back verify mismatch");
                }
            } else {
                trigger_retry_or_fail(drv, "Read-back bus error");
            }
            break;
        }

        case FSM_STATE_ACTIVATE:
            if (platform_i2c_write(DEV_I2C_ADDR, REG_PWR_MODE, VAL_PWR_ACTIVE) == BUS_OK) {
                drv->state = FSM_STATE_SETTLING_DELAY;
                drv->state_enter_time = now;
            } else {
                trigger_retry_or_fail(drv, "Activation command error");
            }
            break;

        case FSM_STATE_SETTLING_DELAY:
            if ((now - drv->state_enter_time) >= TIME_ANALOG_SETTLE_MS) {
                drv->state = FSM_STATE_READY;
                drv->retry_count = 0; /* Скидаємо лічильник після успішного запуску */
            }
            break;

        case FSM_STATE_RETRY_BACKOFF:
            if ((now - drv->state_enter_time) >= drv->timeout_time) {
                /* Повертаємося до початкового стану затримки живлення */
                drv->state = FSM_STATE_POWER_ON_DELAY;
                drv->state_enter_time = now;
            }
            break;

        case FSM_STATE_READY:
        case FSM_STATE_FAULT_SAFE:
        default:
            /* Кінцеві стани: нормальна робота або зафіксована аварія */
            break;
    }
}

bool dev_driver_is_ready(const dev_driver_t *drv) {
    return drv->state == FSM_STATE_READY;
}
