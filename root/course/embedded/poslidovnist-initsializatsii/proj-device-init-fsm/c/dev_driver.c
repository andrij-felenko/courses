#include "dev_driver.h"
#include "platform.h"

/* Діапазон ±4g: значущі біти 0..3, решта регістра зарезервована.
   ODR 100 Гц + DLPF 40 Гц: біт 7 — це RO-статус DRDY, тому маска 0x7F.
   Пряме побайтове порівняння тут давало б вічний Mismatch на живому залізі. */
const reg_config_entry_t DEV_DEFAULT_CONFIG[2] = {
    { REG_RANGE_CTRL, 0x02U, 0x0FU },
    { REG_ODR_FILTER, 0x34U, 0x7FU },
};

static void enter_state(dev_driver_t *drv, dev_fsm_state_t state, uint32_t now)
{
    drv->state = state;
    drv->state_enter_ms = now;
}

/* Уся часова арифметика автомата — тут. Різниця беззнакових коректна
   і в момент переповнення лічильника, тож жодних if (now < enter). */
static bool elapsed(const dev_driver_t *drv, uint32_t now, uint32_t span_ms)
{
    return (uint32_t)(now - drv->state_enter_ms) >= span_ms;
}

/* Збій транзакції: або чергова спроба з експоненційним відкатом,
   або фіксація відмови й безпечний стан. */
static void trigger_retry_or_fail(dev_driver_t *drv, uint32_t now, const char *reason)
{
    drv->retry_count++;

    if (drv->retry_count <= MAX_INIT_RETRIES) {
        /* Ведений міг зупинитися посеред байта й затиснути SDA в нулі —
           без 9 тактів SCL наступний START просто не сформується. */
        platform_bus_recover();
        drv->backoff_ms = BASE_BACKOFF_MS << (drv->retry_count - 1U); /* 50, 100, 200 мс */
        enter_state(drv, FSM_STATE_RETRY_BACKOFF, now);
    } else {
        drv->fault_reason = reason;
        enter_state(drv, FSM_STATE_FAULT_SAFE, now);
        platform_notify_fault(reason);
    }
}

void dev_driver_init(dev_driver_t *drv, const reg_config_entry_t *config, uint8_t count)
{
    drv->config = config;
    drv->config_count = count;
    drv->backoff_ms = 0U;
    drv->config_idx = 0U;
    drv->retry_count = 0U;
    drv->fault_reason = NULL;
    enter_state(drv, FSM_STATE_POWER_ON_DELAY, platform_get_millis());
}

void dev_driver_step(dev_driver_t *drv)
{
    const uint32_t now = platform_get_millis();
    uint8_t val = 0U;

    switch (drv->state) {

    case FSM_STATE_POWER_ON_DELAY:
        /* Доки V_DD наростає й піднімається внутрішній LDO, чип на шині німий. */
        if (elapsed(drv, now, TIME_POR_BOOT_MS)) {
            enter_state(drv, FSM_STATE_SEND_RESET, now);
        }
        break;

    case FSM_STATE_SEND_RESET:
        if (platform_i2c_write(DEV_I2C_ADDR, REG_RESET_CTRL, BIT_SW_RESET) == BUS_OK) {
            enter_state(drv, FSM_STATE_POLL_READY, now);
        } else {
            trigger_retry_or_fail(drv, now, "NACK на команді SW_RESET");
        }
        break;

    case FSM_STATE_POLL_READY:
        /* Перші мілісекунди після скидання цифрове ядро вимкнене й відповідає
           NACK. Без цієї паузи драйвер спалив би ліміт спроб на власному ж
           скиданні, ще до того, як кремній устиг перезавантажитися. */
        if (!elapsed(drv, now, TIME_RESET_WAIT_MS)) {
            break;
        }
        if (platform_i2c_read(DEV_I2C_ADDR, REG_RESET_CTRL, &val) == BUS_OK) {
            /* Біт скидання самоочистився і ядро підняло прапорець готовності. */
            if ((val & BIT_SW_RESET) == 0U && (val & BIT_DEVICE_READY) != 0U) {
                enter_state(drv, FSM_STATE_VERIFY_CHIP_ID, now);
                break;
            }
        }
        if (elapsed(drv, now, TIME_POLL_TIMEOUT_MS)) {
            trigger_retry_or_fail(drv, now, "таймаут очікування біта готовності");
        }
        break;

    case FSM_STATE_VERIFY_CHIP_ID:
        if (platform_i2c_read(DEV_I2C_ADDR, REG_CHIP_ID, &val) != BUS_OK) {
            trigger_retry_or_fail(drv, now, "помилка шини при читанні WHO_AM_I");
        } else if (val != EXPECTED_CHIP_ID) {
            /* Чужий номер кристала теж проганяємо через відкат: на брудній шині
               це буває наслідком збитого байта, а не насправді іншим чипом.
               Якщо він стабільний — ліміт спроб доведе автомат до FAULT_SAFE. */
            trigger_retry_or_fail(drv, now, "невірний WHO_AM_I");
        } else {
            drv->config_idx = 0U;
            enter_state(drv, FSM_STATE_WRITE_CONFIG, now);
        }
        break;

    case FSM_STATE_WRITE_CONFIG:
        if (drv->config_idx >= drv->config_count) {
            enter_state(drv, FSM_STATE_ACTIVATE, now);
            break;
        }
        {
            const reg_config_entry_t *entry = &drv->config[drv->config_idx];
            if (platform_i2c_write(DEV_I2C_ADDR, entry->reg, entry->val) == BUS_OK) {
                enter_state(drv, FSM_STATE_READBACK_VERIFY, now);
            } else {
                trigger_retry_or_fail(drv, now, "помилка запису конфігурації");
            }
        }
        break;

    case FSM_STATE_READBACK_VERIFY:
        {
            const reg_config_entry_t *entry = &drv->config[drv->config_idx];
            if (platform_i2c_read(DEV_I2C_ADDR, entry->reg, &val) != BUS_OK) {
                trigger_retry_or_fail(drv, now, "помилка шини при Read-Back");
            } else if ((val & entry->mask) != (entry->val & entry->mask)) {
                /* Кремній не прийняв значення: заборонена комбінація,
                   не той банк регістрів або чип іще не вийшов зі скидання. */
                trigger_retry_or_fail(drv, now, "розбіжність Read-Back");
            } else {
                drv->config_idx++;
                enter_state(drv, FSM_STATE_WRITE_CONFIG, now);
            }
        }
        break;

    case FSM_STATE_ACTIVATE:
        if (platform_i2c_write(DEV_I2C_ADDR, REG_PWR_MODE, VAL_PWR_ACTIVE) == BUS_OK) {
            enter_state(drv, FSM_STATE_SETTLING_DELAY, now);
        } else {
            trigger_retry_or_fail(drv, now, "помилка переходу в робочий режим");
        }
        break;

    case FSM_STATE_SETTLING_DELAY:
        /* Перші вибірки після вмикання аналогового тракту недостовірні. */
        if (elapsed(drv, now, TIME_ANALOG_SETTLE_MS)) {
            drv->retry_count = 0U; /* запуск удався — ліміт спроб знову повний */
            enter_state(drv, FSM_STATE_READY, now);
        }
        break;

    case FSM_STATE_RETRY_BACKOFF:
        if (elapsed(drv, now, drv->backoff_ms)) {
            /* Починаємо з нуля: чип міг перезавантажитися по живленню. */
            drv->config_idx = 0U;
            enter_state(drv, FSM_STATE_POWER_ON_DELAY, now);
        }
        break;

    case FSM_STATE_READY:
    case FSM_STATE_FAULT_SAFE:
    default:
        /* Кінцеві стани: штатна робота або зафіксована аварія. */
        break;
    }
}

bool dev_driver_is_ready(const dev_driver_t *drv)
{
    return drv->state == FSM_STATE_READY;
}

bool dev_driver_is_fault(const dev_driver_t *drv)
{
    return drv->state == FSM_STATE_FAULT_SAFE;
}

const char *dev_driver_state_name(dev_fsm_state_t state)
{
    switch (state) {
    case FSM_STATE_POWER_ON_DELAY: return "POWER_ON_DELAY";
    case FSM_STATE_SEND_RESET:     return "SEND_RESET";
    case FSM_STATE_POLL_READY:     return "POLL_READY";
    case FSM_STATE_VERIFY_CHIP_ID: return "VERIFY_CHIP_ID";
    case FSM_STATE_WRITE_CONFIG:   return "WRITE_CONFIG";
    case FSM_STATE_READBACK_VERIFY:return "READBACK_VERIFY";
    case FSM_STATE_ACTIVATE:       return "ACTIVATE";
    case FSM_STATE_SETTLING_DELAY: return "SETTLING_DELAY";
    case FSM_STATE_READY:          return "READY";
    case FSM_STATE_RETRY_BACKOFF:  return "RETRY_BACKOFF";
    case FSM_STATE_FAULT_SAFE:     return "FAULT_SAFE";
    default:                       return "?";
    }
}
