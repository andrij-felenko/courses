# ⚙️ Практикум: неблокуючий автомат ініціалізації периферійного чипа

У вбудованих системах реального часу блокуючі затримки `delay_ms(50)` під час запуску периферійних чипів неприпустимі, якщо пристрій одночасно керує критичними виконавчими механізмами, опитує аварійні кінцевики або підтримує мережеві протоколи. Якщо зовнішній давач зависає або не відповідає на шині, наївний блокуючий цикл ініціалізації паралізує весь мікроконтролер.

Цей практикум демонструє повну реалізацію асинхронного кінцевого автомата *(англ. Non-blocking Finite State Machine, FSM)* ініціалізації цифрового давача (на прикладі комбінованого сенсора руху) з апаратними затримками POR, програмним скиданням, перевіркою ідентифікатора кристала, табличною конфігурацією з верифікацією Read-Back, експоненційним відкатом спроб *(exponential backoff)* та аварійним переходом у безпечний стан *(Safe State)*.

---

## Архітектура автомата станів

Кінцевий автомат пристрою керується системними мілісекундними мітками часу без жодного блокування основного циклу виконання `main()` або планувальника RTOS.

Кожен виклик диспетчера `dev_driver_step()` виконує швидку перевірку умов: поточний стан, час перебування у стані та наявність апаратних подій на шині. Якщо час чергової затримки ще не сплив, функція миттєво повертає керування іншим задачам системи. Це дозволяє обслуговувати кілька незалежних зовнішніх мікросхем паралельно на одній або різних шинах без взаємного блокування.

Автомат проходить такі послідовні фази:
1. `STATE_POWER_ON_DELAY`: очікування стабілізації напруги живлення V_DD та завершення внутрішнього старту LDO чипа (t_boot ≈ 25 мс);
2. `STATE_SEND_RESET`: генерація команди програмного скидання (`SW_RESET`);
3. `STATE_POLL_READY`: очікування зняття біта зайнятості та самоочищення прапорця перезавантаження з таймаутом;
4. `STATE_VERIFY_CHIP_ID`: зчитування регістра `WHO_AM_I` та валідація апаратного номера кристала;
5. `STATE_WRITE_CONFIG`: послідовний запис регістрів конфігурації з таблиці налаштувань;
6. `STATE_READBACK_VERIFY`: зворотне зчитування кожного записаного регістра, накладання маски значущих бітів і порівняння;
7. `STATE_ACTIVATE`: переведення сенсора в робочий режим вимірювання;
8. `STATE_SETTLING_DELAY`: витримка часу заспокоєння та прогріву аналогового тракту (t_settling ≈ 15 мс);
9. `STATE_READY`: пристрій повністю ініціалізовано, давач готовий до регулярного постачання валідних вибірок;
10. `STATE_RETRY_BACKOFF`: обробка збою транзакції — відлік експоненційної паузи перед повторною спробою;
11. `STATE_FAULT_SAFE`: вичерпано ліміт спроб — фіксація відмови та перехід системи в аварійний захищений стан.

---

## Повна реалізація: C та ідіоматичний C++

:::tabs
```c
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
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <chrono>
#include <string_view>

namespace embedded {

using namespace std::chrono_literals;

enum class BusStatus {
    Ok = 0,
    Nack,
    Timeout
};

enum class FsmState {
    PowerOnDelay,
    SendReset,
    PollReady,
    VerifyChipId,
    WriteConfig,
    ReadbackVerify,
    Activate,
    SettlingDelay,
    Ready,
    RetryBackoff,
    FaultSafe
};

struct RegConfigEntry {
    uint8_t reg;
    uint8_t val;
    uint8_t mask;
};

// Інтерфейс апаратної шини I2C
class II2cBus {
public:
    virtual ~II2cBus() = default;
    virtual BusStatus write(uint8_t dev_addr, uint8_t reg, uint8_t val) = 0;
    virtual BusStatus read(uint8_t dev_addr, uint8_t reg, uint8_t &val) = 0;
    virtual void recover() = 0;
};

// Драйвер надійного запуску пристрою
class SafeSensorDriver {
public:
    static constexpr uint8_t DevAddress = 0x68;
    static constexpr uint8_t RegChipId = 0x00;
    static constexpr uint8_t ExpectedChipId = 0xEA;
    static constexpr uint8_t RegResetCtrl = 0x10;
    static constexpr uint8_t BitSwReset = 1U << 7;
    static constexpr uint8_t BitDeviceReady = 1U << 0;
    static constexpr uint8_t RegPwrMode = 0x1A;
    static constexpr uint8_t ValPwrActive = 0x01;

    static constexpr auto TimePorBoot = 25ms;
    static constexpr auto TimeResetWait = 10ms;
    static constexpr auto TimePollTimeout = 100ms;
    static constexpr auto TimeAnalogSettle = 15ms;
    static constexpr auto BaseBackoff = 50ms;
    static constexpr uint8_t MaxRetries = 3;

    explicit SafeSensorDriver(II2cBus &bus) : bus_(bus) {}

    void reset() {
        state_ = FsmState::PowerOnDelay;
        state_enter_time_ = get_current_time();
        timeout_duration_ = 0ms;
        config_idx_ = 0;
        retry_count_ = 0;
        fault_reason_ = {};
    }

    void step() {
        const auto now = get_current_time();
        uint8_t val = 0;

        switch (state_) {
            case FsmState::PowerOnDelay:
                if (now - state_enter_time_ >= TimePorBoot) {
                    state_ = FsmState::SendReset;
                }
                break;

            case FsmState::SendReset:
                if (bus_.write(DevAddress, RegResetCtrl, BitSwReset) == BusStatus::Ok) {
                    state_ = FsmState::PollReady;
                    state_enter_time_ = now;
                } else {
                    trigger_retry_or_fail("NACK on SW_RESET");
                }
                break;

            case FsmState::PollReady:
                if (now - state_enter_time_ < TimeResetWait) {
                    break;
                }
                if (bus_.read(DevAddress, RegResetCtrl, val) == BusStatus::Ok) {
                    if ((val & BitSwReset) == 0 && (val & BitDeviceReady)) {
                        state_ = FsmState::VerifyChipId;
                        break;
                    }
                }
                if (now - state_enter_time_ >= TimePollTimeout) {
                    trigger_retry_or_fail("Timeout waiting for ready flag");
                }
                break;

            case FsmState::VerifyChipId:
                if (bus_.read(DevAddress, RegChipId, val) == BusStatus::Ok) {
                    if (val == ExpectedChipId) {
                        config_idx_ = 0;
                        state_ = FsmState::WriteConfig;
                    } else {
                        trigger_retry_or_fail("Invalid CHIP_ID");
                    }
                } else {
                    trigger_retry_or_fail("Bus error reading CHIP_ID");
                }
                break;

            case FsmState::WriteConfig:
                if (config_idx_ < config_table_.size()) {
                    const auto &entry = config_table_[config_idx_];
                    if (bus_.write(DevAddress, entry.reg, entry.val) == BusStatus::Ok) {
                        state_ = FsmState::ReadbackVerify;
                    } else {
                        trigger_retry_or_fail("Write config error");
                    }
                } else {
                    state_ = FsmState::Activate;
                }
                break;

            case FsmState::ReadbackVerify: {
                const auto &entry = config_table_[config_idx_];
                if (bus_.read(DevAddress, entry.reg, val) == BusStatus::Ok) {
                    if ((val & entry.mask) == (entry.val & entry.mask)) {
                        config_idx_++;
                        state_ = FsmState::WriteConfig;
                    } else {
                        trigger_retry_or_fail("Read-back verify mismatch");
                    }
                } else {
                    trigger_retry_or_fail("Read-back bus error");
                }
                break;
            }

            case FsmState::Activate:
                if (bus_.write(DevAddress, RegPwrMode, ValPwrActive) == BusStatus::Ok) {
                    state_ = FsmState::SettlingDelay;
                    state_enter_time_ = now;
                } else {
                    trigger_retry_or_fail("Activation command error");
                }
                break;

            case FsmState::SettlingDelay:
                if (now - state_enter_time_ >= TimeAnalogSettle) {
                    state_ = FsmState::Ready;
                    retry_count_ = 0;
                }
                break;

            case FsmState::RetryBackoff:
                if (now - state_enter_time_ >= timeout_duration_) {
                    state_ = FsmState::PowerOnDelay;
                    state_enter_time_ = now;
                }
                break;

            case FsmState::Ready:
            case FsmState::FaultSafe:
            default:
                break;
        }
    }

    [[nodiscard]] bool is_ready() const noexcept {
        return state_ == FsmState::Ready;
    }

    [[nodiscard]] bool is_fault() const noexcept {
        return state_ == FsmState::FaultSafe;
    }

    [[nodiscard]] std::string_view fault_reason() const noexcept {
        return fault_reason_;
    }

private:
    static std::chrono::milliseconds get_current_time();

    void trigger_retry_or_fail(std::string_view reason) {
        retry_count_++;
        if (retry_count_ <= MaxRetries) {
            bus_.recover();
            state_ = FsmState::RetryBackoff;
            state_enter_time_ = get_current_time();
            timeout_duration_ = BaseBackoff * (1U << (retry_count_ - 1U));
        } else {
            state_ = FsmState::FaultSafe;
            fault_reason_ = reason;
        }
    }

    II2cBus &bus_;
    FsmState state_{FsmState::PowerOnDelay};
    std::chrono::milliseconds state_enter_time_{0};
    std::chrono::milliseconds timeout_duration_{0};
    size_t config_idx_{0};
    uint8_t retry_count_{0};
    std::string_view fault_reason_{};

    static constexpr std::array<RegConfigEntry, 2> config_table_{{
        {0x18, 0x02, 0x0F}, // Range ±4g
        {0x19, 0x34, 0x7F}  // ODR 100Hz + DLPF
    }};
};

} // namespace embedded
```
:::

---

## Інженерний розбір крайових випадків та відмовостійкості

### 1. Безпека розрахунку інтервалів часу без блокувань

Усі перевірки затримок в автоматі реалізовано через різницю беззнакових цілих чисел: `(now - state_enter_time) >= duration`.

Ця математика строго гарантує правильну роботу навіть у момент переповнення системного лічильника мілісекунд (для 32-бітного лічильника `SysTick` це відбувається приблизно раз на 49.7 доби безперервної роботи). Завдяки властивостям арифметики за модулем $2^{32}$ для беззнакових чисел типу `uint32_t`, вираз `(now - state_enter_time)` завжди обчислює коректний пройдений інтервал часу без додаткових умовних переходів `if (now < state_enter_time)`.

### 2. Гонка станів між `SW_RESET` та першим читанням

Після отримання команди скидання цифрове ядро чипа вимикає генератор або блокує скінченний автомат шини на 1–5 мс. Спроба виконати читання одразу на наступній мікросекунді поверне `NACK` на шині I2C. В автоматі обов'язково передбачається міжумовна затримка `TIME_RESET_WAIT_MS`.

Якщо не дотримуватися цієї паузи, драйвер отримає помилку `NACK`, сприйме її як фізичний обрив зв'язку та марно витратить ліміт повторних спроб ще до того, як кремній взагалі завершить внутрішній цикл перезавантаження.

### 3. Неперевірені Read-Only біти під час Read-Back

Якщо конфігураційний регістр містить прапорці стану (наприклад, біт готовності даних `DRDY` або біти переповнення `OVERRUN`), зчитування поверне одиницю в біті статусу, навіть коли конфігурація записана вірно. 

Маска `entry.mask` зобов'язана обнуляти всі неконфігуровані розряди перед порівнянням. Пряме побайтове порівняння призводить до нескінченних хибних спрацьовувань помилки верифікації на робочому залізі.

### 4. Залипання шини під час апаратного скидання

Якщо скидання викликане нестабільністю живлення, ведений пристрій міг зупинитися посеред байтової передачі, затиснувши лінію `SDA` в низькому рівні. У функції `trigger_retry_or_fail()` обов'язково викликається процедура генерації 9 тактів `SCL` *(I2C Bus Recovery)* перед перезапуском ініціалізації.

Без цієї процедури лінія SDA залишиться затиснутою в нулі, і жодна повторна транзакція типу `START` фізично не зможе сформуватися на шині, перетворивши тимчасовий збій на постійне зависання периферії.

### 5. Інтеграція в архітектуру системи

У додатках без операційної системи функція `dev_driver_step()` викликається в тілі нескінченного циклу `while(1)` поруч з іншими диспетчерами задач.

В операційних системах реального часу (FreeRTOS чи Zephyr) FSM оформлюється у вигляді періодичної задачі, яка викликається раз на 5–10 мс. Після переходу в стан `STATE_READY` задача може сповістити інші потоки про готовність сенсора через механізм подій *(Event Group)* або семафор.

### 6. Лабораторне тестування методом ін'єкції несправностей (Fault Injection)

Для верифікації стійкості автомата ініціалізації на стенді розробки застосовують три обов'язкові тести:
- **Штучний NACK:** тимчасове відключення лінії живлення давача під час виконання команди `SW_RESET` (перевірка входу в стан `STATE_RETRY_BACKOFF` та виходу в `STATE_FAULT_SAFE`);
- **Штучна розбіжність Read-Back:** підміна одного байта в таблиці `INIT_CONFIG_TABLE` на заборонену конфігурацію (перевірка компаратора та реакції на Mismatch);
- **Імітація повільного POR:** подача живлення через регульований лабораторний блок із часом наростання 50 мс (перевірка захисту від передчасних транзакцій на шині).
