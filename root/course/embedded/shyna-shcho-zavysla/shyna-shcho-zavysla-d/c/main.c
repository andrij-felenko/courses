#include <stdint.h>
#include <stdbool.h>

// Типи підтримуваних інтерфейсних шин
typedef enum {
    BUS_TYPE_I2C = 0,
    BUS_TYPE_CAN,
    BUS_TYPE_RS485
} bus_type_t;

// Стан працездатності шини
typedef enum {
    BUS_STATE_OK = 0,
    BUS_STATE_WARNING,
    BUS_STATE_STUCK,
    BUS_STATE_RECOVERING,
    BUS_STATE_FATAL
} bus_state_t;

// Структура апаратного інтерфейсу GPIO для bit-banging I2C
typedef struct {
    void (*set_scl)(bool high);
    void (*set_sda)(bool high);
    bool (*get_scl)(void);
    bool (*get_sda)(void);
    void (*set_gpio_mode_opendrain)(void);
    void (*set_hw_i2c_mode)(void);
    void (*set_power_enable)(bool enable);
    void (*delay_us)(uint32_t us);
} i2c_hardware_ops_t;

// Структура конфігурації сторожа польових шин
typedef struct {
    bus_state_t state;
    uint32_t error_counter;
    uint32_t last_recovery_tick;
    uint32_t backoff_delay_ms;
    uint8_t  consecutive_failures;
} bus_monitor_t;

// ── 1. Процедура відновлення I2C 9 тактами SCL ─────────────────────────────
bool i2c_bus_recover_9clocks(const i2c_hardware_ops_t *ops) {
    if (!ops) return false;

    // Крок 1: Перемикаємо піни SCL/SDA з апаратного блоку на режим GPIO
    ops->set_gpio_mode_opendrain();
    ops->set_scl(true);
    ops->set_sda(true);
    ops->delay_us(10);

    // Крок 2: Якщо лінія SDA вже у високому рівні — перевіряємо SCL
    if (ops->get_sda() && ops->get_scl()) {
        ops->set_hw_i2c_mode();
        return true;
    }

    // Крок 3: Генеруємо до 9 тактів SCL, поки Slave не відпустить SDA
    for (int i = 0; i < 9; i++) {
        ops->set_scl(false);
        ops->delay_us(10);
        ops->set_scl(true);
        ops->delay_us(10);

        // Якщо Slave відпустив SDA — виходимо з циклу
        if (ops->get_sda()) {
            break;
        }
    }

    // Крок 4: Формуємо умову STOP (перепад SDA 0->1 при утримуваному SCL=1)
    ops->set_sda(false);
    ops->delay_us(10);
    ops->set_scl(true);
    ops->delay_us(10);
    ops->set_sda(true);
    ops->delay_us(10);

    // Крок 5: Перевіряємо результат розблокування
    bool success = ops->get_sda() && ops->get_scl();

    // Крок 6: Якщо 9 тактів не допомогли — аварійний скидання живленням (Power Cycle)
    if (!success && ops->set_power_enable) {
        ops->set_power_enable(false); // Вимикаємо ключ живлення датчиків
        ops->delay_us(15000);         // 15 мс на розряд ємностей C_decoupling
        ops->set_power_enable(true);  // Вмикаємо живлення знову
        ops->delay_us(10000);         // 10 мс на стабілізацію напруги
        success = ops->get_sda() && ops->get_scl();
    }

    // Повертаємо виводи під контроль апаратного модуля I2C
    ops->set_hw_i2c_mode();
    return success;
}

// ── 2. Обробник виходу CAN із стану Bus-Off з експоненційним бекофом ───────
typedef struct {
    uint32_t (*get_tec)(void);
    uint32_t (*get_rec)(void);
    bool (*is_bus_off)(void);
    void (*reset_controller)(void);
    void (*start_controller)(void);
} can_hardware_ops_t;

void can_monitor_process(bus_monitor_t *mon, const can_hardware_ops_t *ops, uint32_t current_tick_ms) {
    if (!mon || !ops) return;

    if (ops->is_bus_off()) {
        mon->state = BUS_STATE_STUCK;

        // Перевіряємо, чи вичерпано час експоненційної затримки (Backoff)
        if (current_tick_ms - mon->last_recovery_tick >= mon->backoff_delay_ms) {
            mon->last_recovery_tick = current_tick_ms;
            mon->consecutive_failures++;

            // Експоненційне збільшення паузи: 50мс -> 200мс -> 1000мс -> 5000мс
            if (mon->consecutive_failures == 1) mon->backoff_delay_ms = 50;
            else if (mon->consecutive_failures == 2) mon->backoff_delay_ms = 200;
            else if (mon->consecutive_failures == 3) mon->backoff_delay_ms = 1000;
            else mon->backoff_delay_ms = 5000;

            // Ручний контрольований перезапуск CAN-контролера
            ops->reset_controller();
            ops->start_controller();
            mon->state = BUS_STATE_RECOVERING;
        }
    } else {
        uint32_t tec = ops->get_tec();
        uint32_t rec = ops->get_rec();

        if (tec < 96 && rec < 96) {
            mon->state = BUS_STATE_OK;
            mon->consecutive_failures = 0;
            mon->backoff_delay_ms = 50;
        } else if (tec >= 128 || rec >= 128) {
            mon->state = BUS_STATE_WARNING; // Error Passive
        }
    }
}
