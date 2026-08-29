#ifndef DEV_DRIVER_H
#define DEV_DRIVER_H

#include <stdbool.h>
#include <stdint.h>

/* Регістри та константи гіпотетичного MEMS-давача */
#define DEV_I2C_ADDR          (0x68U)
#define REG_CHIP_ID           (0x00U)
#define EXPECTED_CHIP_ID      (0xEAU)

#define REG_RESET_CTRL        (0x10U)
#define BIT_SW_RESET          (1U << 7)
#define BIT_DEVICE_READY      (1U << 0)

#define REG_RANGE_CTRL        (0x18U)
#define REG_ODR_FILTER        (0x19U)
#define BIT_DATA_READY        (1U << 7) /* RO-статус усередині REG_ODR_FILTER */
#define REG_PWR_MODE          (0x1AU)
#define VAL_PWR_ACTIVE        (0x01U)

/* Часові параметри bring-up (мілісекунди) */
#define TIME_POR_BOOT_MS      (25U)  /* старт LDO та цифрового ядра після подачі V_DD */
#define TIME_RESET_WAIT_MS    (10U)  /* пауза після SW_RESET, доки ядро не підніметься */
#define TIME_POLL_TIMEOUT_MS  (100U) /* стеля очікування біта готовності */
#define TIME_ANALOG_SETTLE_MS (15U)  /* заспокоєння аналогового тракту */
#define MAX_INIT_RETRIES      (3U)
#define BASE_BACKOFF_MS       (50U)

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

/* Елемент таблиці конфігурації.
   mask — значущі біти регістра: усе, що поза нею (RO-статуси, зарезервовані
   розряди), під час Read-Back ігнорується. */
typedef struct {
    uint8_t reg;
    uint8_t val;
    uint8_t mask;
} reg_config_entry_t;

/* Контекст драйвера. Жодних глобальних змінних: скільки чипів на шині —
   стільки й екземплярів, кожен крокує незалежно. */
typedef struct {
    dev_fsm_state_t state;
    uint32_t state_enter_ms;  /* мітка входу в поточний стан */
    uint32_t backoff_ms;      /* тривалість поточної паузи відкату */
    const reg_config_entry_t *config;
    uint8_t config_count;
    uint8_t config_idx;
    uint8_t retry_count;
    const char *fault_reason; /* NULL, доки автомат не впав у FAULT_SAFE */
} dev_driver_t;

/* Робоча таблиця конфігурації давача */
extern const reg_config_entry_t DEV_DEFAULT_CONFIG[2];
#define DEV_DEFAULT_CONFIG_SIZE (2U)

/* config/count — таблиця регістрів; на стенді сюди підсовують спотворену,
   щоб перевірити компаратор Read-Back. */
void dev_driver_init(dev_driver_t *drv, const reg_config_entry_t *config, uint8_t count);

/* Один неблокуючий крок. Викликається з while(1) або з періодичної задачі RTOS. */
void dev_driver_step(dev_driver_t *drv);

bool dev_driver_is_ready(const dev_driver_t *drv);
bool dev_driver_is_fault(const dev_driver_t *drv);
const char *dev_driver_state_name(dev_fsm_state_t state);

#endif /* DEV_DRIVER_H */
