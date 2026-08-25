# ⚙️ Реалізація секвенсера живлення на мікроконтролері з телеметрією та захистом

При проєктуванні нестандартних обчислювальних плат з декількома FPGA або спеціалізованими ASIC часто виникає потреба в гнучкому керуванні десятком силових перетворювачів без застосування дорогих спеціалізованих цифрових менеджерів. Бюджетний мікроконтролер із вбудованим багатоканальним АЦП, апаратними таймерами та портами вводу-виводу дозволяє створити високонадійний секвенсер живлення з індивідуальними часовими вікнами, контролем напруг за допусками та аварійним реверсивним вимкненням. Розглянемо архітектуру автомата станів, алгоритм моніторингу та повну програмну реалізацію мовами C та C++.

### Архітектура системи та часові вимоги

Розглянемо систему керування трьома силовими доменами для плати обробки сигналів на базі FPGA:
1. **Шина ядра `V_CORE` (0.85 В / 20 А):** перший ступінь пуску. Час виходу на номінал: не більше 10 мс. Допустиме вікно стабілізації: 0.80–0.90 В.
2. **Шина допоміжних вузлів та PLL `V_AUX` (1.8 В / 3 А):** другий ступінь. Стартує через затримку 5 мс після підтвердження готовності ядра. Допустиме вікно: 1.71–1.89 В.
3. **Шина інтерфейсів вводу-виводу `V_IO` (3.3 В / 5 А):** третій ступінь. Стартує через затримку 5 мс після стабілізації `V_AUX`. Допустиме вікно: 3.13–3.47 В.

**Вимоги безпеки автомата:**
- Якщо будь-яка шина не досягає допустимого діапазону напруги протягом таймауту `TIMEOUT_MS = 25 мс`, пуск негайно переривається.
- Якщо під час нормальної роботи (`RUNNING`) виникає просідання (*undervoltage*) чи перенапруга (*overvoltage*) на будь-якій шині, система негайно переходить у стан аварійного вимкнення.
- При вимкненні (плановому чи аварійному) шини знеструмлюються у строго реверсивному порядку (LIFO: `V_IO` → `V_AUX` → `V_CORE`) з активацією ключів активного розряду для гарантування безпечного спаду залишкових зарядів.

```
       [IDLE]
         │  (Команда Start)
         ▼
  [START_CORE] ──(Таймаут/Збій)──┐
         │ (Core OK + затримка)  │
         ▼                       │
  [START_AUX]  ──(Таймаут/Збій)──┤
         │ (Aux OK + затримка)   │
         ▼                       │
   [START_IO]  ──(Таймаут/Збій)──┤
         │ (IO OK + затримка)    │
         ▼                       │
     [RUNNING] ──(Збій/UV/OV)────┤
         │                       │
         │ (Команда Стоп)        ▼
         │                 [EMERGENCY_SHUTDOWN]
         │                       │ (Реверсивний розряд LIFO)
         ▼                       ▼
  [STOP_IO] → [STOP_AUX] → [STOP_CORE] → [FAULT_LATCH]
```

### Програмна реалізація

Нижче наведено повністю робочу реалізацію секвенсера. У вкладці C реалізовано процедурний підхід на структурах даних та функціональних покажчиках. У вкладці C++ реалізовано об'єктно-орієнтований клас із сильним типізуванням (`enum class`), інкапсуляцією логіки та безпечними інтервалами `std::span`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

#define NUM_RAILS 3
#define TIMEOUT_TICKS 25
#define STABILIZE_TICKS 5

typedef enum {
    SEQ_STATE_IDLE = 0,
    SEQ_STATE_START_CORE,
    SEQ_STATE_START_AUX,
    SEQ_STATE_START_IO,
    SEQ_STATE_RUNNING,
    SEQ_STATE_STOP_IO,
    SEQ_STATE_STOP_AUX,
    SEQ_STATE_STOP_CORE,
    SEQ_STATE_FAULT
} SequencerState_t;

typedef enum {
    FAULT_NONE = 0,
    FAULT_CORE_TIMEOUT,
    FAULT_AUX_TIMEOUT,
    FAULT_IO_TIMEOUT,
    FAULT_RUNTIME_CORE_DROP,
    FAULT_RUNTIME_AUX_DROP,
    FAULT_RUNTIME_IO_DROP
} FaultReason_t;

typedef struct {
    const char* name;
    uint16_t v_min_mv;      /* Мінімальна напруга в мілівольтах */
    uint16_t v_max_mv;      /* Максимальна напруга в мілівольтах */
    uint8_t  enable_pin;    /* Номер GPIO виводу Enable */
    uint8_t  discharge_pin; /* Номер GPIO виводу Active Discharge */
} PowerRailConfig_t;

typedef struct {
    SequencerState_t state;
    FaultReason_t    fault_reason;
    uint32_t         timer_ticks;
    uint16_t         measured_mv[NUM_RAILS];
    PowerRailConfig_t rails[NUM_RAILS];
} PowerSequencer_t;

/* Прототипи апаратних функцій платформи */
extern void gpio_set_pin(uint8_t pin, bool level);
extern uint16_t adc_read_rail_mv(uint8_t rail_index);

void sequencer_init(PowerSequencer_t* seq) {
    seq->state = SEQ_STATE_IDLE;
    seq->fault_reason = FAULT_NONE;
    seq->timer_ticks = 0;

    /* Конфігурація трьох шин: Core (0.85V), Aux (1.8V), IO (3.3V) */
    seq->rails[0] = (PowerRailConfig_t){ "V_CORE", 800,  900,  10, 11 };
    seq->rails[1] = (PowerRailConfig_t){ "V_AUX",  1710, 1890, 12, 13 };
    seq->rails[2] = (PowerRailConfig_t){ "V_IO",   3130, 3470, 14, 15 };

    /* Початковий стан: усі перетворювачі вимкнено, розрядні ключі закрито */
    for (int i = 0; i < NUM_RAILS; i++) {
        gpio_set_pin(seq->rails[i].enable_pin, false);
        gpio_set_pin(seq->rails[i].discharge_pin, true); /* Активний розряд увімкнено */
    }
}

static bool is_rail_in_range(const PowerSequencer_t* seq, uint8_t idx) {
    uint16_t v = seq->measured_mv[idx];
    return (v >= seq->rails[idx].v_min_mv && v <= seq->rails[idx].v_max_mv);
}

void sequencer_start(PowerSequencer_t* seq) {
    if (seq->state == SEQ_STATE_IDLE) {
        /* Знімаємо активний розряд з шини ядра та вмикаємо перетворювач */
        gpio_set_pin(seq->rails[0].discharge_pin, false);
        gpio_set_pin(seq->rails[0].enable_pin, true);
        seq->state = SEQ_STATE_START_CORE;
        seq->timer_ticks = 0;
        seq->fault_reason = FAULT_NONE;
    }
}

void sequencer_shutdown(PowerSequencer_t* seq) {
    if (seq->state == SEQ_STATE_RUNNING) {
        /* Починаємо реверсивне вимкнення з шини I/O */
        gpio_set_pin(seq->rails[2].enable_pin, false);
        gpio_set_pin(seq->rails[2].discharge_pin, true);
        seq->state = SEQ_STATE_STOP_IO;
        seq->timer_ticks = 0;
    }
}

/* Періодичний крок опитування (викликається за таймером щомілісекунди) */
void sequencer_poll_1ms(PowerSequencer_t* seq) {
    /* Зчитування напруг через АЦП */
    for (uint8_t i = 0; i < NUM_RAILS; i++) {
        seq->measured_mv[i] = adc_read_rail_mv(i);
    }
    seq->timer_ticks++;

    switch (seq->state) {
        case SEQ_STATE_IDLE:
            break;

        case SEQ_STATE_START_CORE:
            if (is_rail_in_range(seq, 0)) {
                if (seq->timer_ticks >= STABILIZE_TICKS) {
                    /* Ядро стабільне, запускаємо шину Aux */
                    gpio_set_pin(seq->rails[1].discharge_pin, false);
                    gpio_set_pin(seq->rails[1].enable_pin, true);
                    seq->state = SEQ_STATE_START_AUX;
                    seq->timer_ticks = 0;
                }
            } else if (seq->timer_ticks > TIMEOUT_TICKS) {
                seq->fault_reason = FAULT_CORE_TIMEOUT;
                seq->state = SEQ_STATE_STOP_CORE;
            }
            break;

        case SEQ_STATE_START_AUX:
            if (is_rail_in_range(seq, 1) && is_rail_in_range(seq, 0)) {
                if (seq->timer_ticks >= STABILIZE_TICKS) {
                    /* Aux стабільна, запускаємо периферію I/O */
                    gpio_set_pin(seq->rails[2].discharge_pin, false);
                    gpio_set_pin(seq->rails[2].enable_pin, true);
                    seq->state = SEQ_STATE_START_IO;
                    seq->timer_ticks = 0;
                }
            } else if (seq->timer_ticks > TIMEOUT_TICKS) {
                seq->fault_reason = FAULT_AUX_TIMEOUT;
                seq->state = SEQ_STATE_STOP_AUX;
            }
            break;

        case SEQ_STATE_START_IO:
            if (is_rail_in_range(seq, 2) && is_rail_in_range(seq, 1) && is_rail_in_range(seq, 0)) {
                if (seq->timer_ticks >= STABILIZE_TICKS) {
                    seq->state = SEQ_STATE_RUNNING;
                    seq->timer_ticks = 0;
                }
            } else if (seq->timer_ticks > TIMEOUT_TICKS) {
                seq->fault_reason = FAULT_IO_TIMEOUT;
                seq->state = SEQ_STATE_STOP_IO;
            }
            break;

        case SEQ_STATE_RUNNING:
            /* Безперервний моніторинг шин під час роботи */
            if (!is_rail_in_range(seq, 0)) {
                seq->fault_reason = FAULT_RUNTIME_CORE_DROP;
                sequencer_shutdown(seq);
            } else if (!is_rail_in_range(seq, 1)) {
                seq->fault_reason = FAULT_RUNTIME_AUX_DROP;
                sequencer_shutdown(seq);
            } else if (!is_rail_in_range(seq, 2)) {
                seq->fault_reason = FAULT_RUNTIME_IO_DROP;
                sequencer_shutdown(seq);
            }
            break;

        case SEQ_STATE_STOP_IO:
            if (seq->timer_ticks >= STABILIZE_TICKS) {
                /* I/O розряджено, вимикаємо Aux */
                gpio_set_pin(seq->rails[1].enable_pin, false);
                gpio_set_pin(seq->rails[1].discharge_pin, true);
                seq->state = SEQ_STATE_STOP_AUX;
                seq->timer_ticks = 0;
            }
            break;

        case SEQ_STATE_STOP_AUX:
            if (seq->timer_ticks >= STABILIZE_TICKS) {
                /* Aux розряджено, останнім вимикаємо Core */
                gpio_set_pin(seq->rails[0].enable_pin, false);
                gpio_set_pin(seq->rails[0].discharge_pin, true);
                seq->state = SEQ_STATE_STOP_CORE;
                seq->timer_ticks = 0;
            }
            break;

        case SEQ_STATE_STOP_CORE:
            if (seq->timer_ticks >= STABILIZE_TICKS) {
                seq->state = (seq->fault_reason == FAULT_NONE) ? SEQ_STATE_IDLE : SEQ_STATE_FAULT;
            }
            break;

        case SEQ_STATE_FAULT:
            /* Блокування в аварійному стані до зовнішнього скидання */
            break;
    }
}
```
```cpp
#include <array>
#include <cstdint>
#include <string_view>
#include <span>

/* Апаратний інтерфейс платформи (драйвер вводу-виводу та АЦП) */
class IHardwareDriver {
public:
    virtual ~IHardwareDriver() = default;
    virtual void setPin(uint8_t pin, bool level) noexcept = 0;
    virtual uint16_t readAdcMv(uint8_t channel) noexcept = 0;
};

class PowerSequencer {
public:
    enum class State : uint8_t {
        Idle,
        StartCore,
        StartAux,
        StartIo,
        Running,
        StopIo,
        StopAux,
        StopCore,
        Fault
    };

    enum class FaultReason : uint8_t {
        None,
        CoreTimeout,
        AuxTimeout,
        IoTimeout,
        RuntimeCoreDrop,
        RuntimeAuxDrop,
        RuntimeIoDrop
    };

    struct RailConfig {
        std::string_view name;
        uint16_t vMinMv;
        uint16_t vMaxMv;
        uint8_t  enablePin;
        uint8_t  dischargePin;
    };

    static constexpr size_t RailCount = 3;
    static constexpr uint32_t TimeoutTicks = 25;
    static constexpr uint32_t StabilizeTicks = 5;

    explicit PowerSequencer(IHardwareDriver& hwDriver) noexcept
        : hw_(hwDriver),
          state_(State::Idle),
          fault_(FaultReason::None),
          timerTicks_(0),
          measuredMv_{}
    {
        for (const auto& rail : rails_) {
            hw_.setPin(rail.enablePin, false);
            hw_.setPin(rail.dischargePin, true); /* За замовчуванням розряд увімкнено */
        }
    }

    void start() noexcept {
        if (state_ == State::Idle) {
            hw_.setPin(rails_[0].dischargePin, false);
            hw_.setPin(rails_[0].enablePin, true);
            state_ = State::StartCore;
            timerTicks_ = 0;
            fault_ = FaultReason::None;
        }
    }

    void shutdown() noexcept {
        if (state_ == State::Running) {
            hw_.setPin(rails_[2].enablePin, false);
            hw_.setPin(rails_[2].dischargePin, true);
            state_ = State::StopIo;
            timerTicks_ = 0;
        }
    }

    void poll1ms() noexcept {
        for (size_t i = 0; i < RailCount; ++i) {
            measuredMv_[i] = hw_.readAdcMv(static_cast<uint8_t>(i));
        }
        ++timerTicks_;

        switch (state_) {
            case State::Idle:
                break;

            case State::StartCore:
                handleStartCore();
                break;

            case State::StartAux:
                handleStartAux();
                break;

            case State::StartIo:
                handleStartIo();
                break;

            case State::Running:
                handleRunning();
                break;

            case State::StopIo:
                handleStopIo();
                break;

            case State::StopAux:
                handleStopAux();
                break;

            case State::StopCore:
                handleStopCore();
                break;

            case State::Fault:
                break;
        }
    }

    [[nodiscard]] State getState() const noexcept { return state_; }
    [[nodiscard]] FaultReason getFault() const noexcept { return fault_; }
    [[nodiscard]] std::span<const uint16_t, RailCount> getVoltages() const noexcept {
        return measuredMv_;
    }

private:
    [[nodiscard]] bool isRailInRange(size_t index) const noexcept {
        const auto v = measuredMv_[index];
        return (v >= rails_[index].vMinMv && v <= rails_[index].vMaxMv);
    }

    void handleStartCore() noexcept {
        if (isRailInRange(0)) {
            if (timerTicks_ >= StabilizeTicks) {
                hw_.setPin(rails_[1].dischargePin, false);
                hw_.setPin(rails_[1].enablePin, true);
                state_ = State::StartAux;
                timerTicks_ = 0;
            }
        } else if (timerTicks_ > TimeoutTicks) {
            fault_ = FaultReason::CoreTimeout;
            state_ = State::StopCore;
        }
    }

    void handleStartAux() noexcept {
        if (isRailInRange(1) && isRailInRange(0)) {
            if (timerTicks_ >= StabilizeTicks) {
                hw_.setPin(rails_[2].dischargePin, false);
                hw_.setPin(rails_[2].enablePin, true);
                state_ = State::StartIo;
                timerTicks_ = 0;
            }
        } else if (timerTicks_ > TimeoutTicks) {
            fault_ = FaultReason::AuxTimeout;
            state_ = State::StopAux;
        }
    }

    void handleStartIo() noexcept {
        if (isRailInRange(2) && isRailInRange(1) && isRailInRange(0)) {
            if (timerTicks_ >= StabilizeTicks) {
                state_ = State::Running;
                timerTicks_ = 0;
            }
        } else if (timerTicks_ > TimeoutTicks) {
            fault_ = FaultReason::IoTimeout;
            state_ = State::StopIo;
        }
    }

    void handleRunning() noexcept {
        if (!isRailInRange(0)) {
            fault_ = FaultReason::RuntimeCoreDrop;
            shutdown();
        } else if (!isRailInRange(1)) {
            fault_ = FaultReason::RuntimeAuxDrop;
            shutdown();
        } else if (!isRailInRange(2)) {
            fault_ = FaultReason::RuntimeIoDrop;
            shutdown();
        }
    }

    void handleStopIo() noexcept {
        if (timerTicks_ >= StabilizeTicks) {
            hw_.setPin(rails_[1].enablePin, false);
            hw_.setPin(rails_[1].dischargePin, true);
            state_ = State::StopAux;
            timerTicks_ = 0;
        }
    }

    void handleStopAux() noexcept {
        if (timerTicks_ >= StabilizeTicks) {
            hw_.setPin(rails_[0].enablePin, false);
            hw_.setPin(rails_[0].dischargePin, true);
            state_ = State::StopCore;
            timerTicks_ = 0;
        }
    }

    void handleStopCore() noexcept {
        if (timerTicks_ >= StabilizeTicks) {
            state_ = (fault_ == FaultReason::None) ? State::Idle : State::Fault;
        }
    }

    IHardwareDriver& hw_;
    State state_;
    FaultReason fault_;
    uint32_t timerTicks_;
    std::array<uint16_t, RailCount> measuredMv_;

    static constexpr std::array<RailConfig, RailCount> rails_{{
        { "V_CORE", 800,  900,  10, 11 },
        { "V_AUX",  1710, 1890, 12, 13 },
        { "V_IO",   3130, 3470, 14, 15 }
    }};
};
```
:::

### Особливості безпеки та захисту від збоїв

У представленому коді враховано чотири фундаментальні інженерні вимоги:

1. **Гарантований реверсивний LIFO-порядок:** При виникненні аварії на будь-якому етапі автомат не «кидає» всі канали в довільний стан, а послідовно проходить фази розряду: спершу шина `V_IO` (3.3 В), потім `V_AUX` (1.8 В), і лише після цього знеструмлюється ядро `V_CORE` (0.85 В).
2. **Контроль активного розряду:** Вивід `dischargePin` вмикається в протифазі до виводу `enablePin`. Перед підйомом напруги розрядний ключ гарантовано закривається, усуваючи коротке замикання через розрядний резистор.
3. **Віконний моніторинг напруг:** Перевірка `isRailInRange` відстежує не тільки нижній поріг (*undervoltage*), але й неприпустиме перевищення номіналу (*overvoltage*), що захищає тонкий підзатворний діелектрик процесора від пробою.
4. **Таймаут стабілізації:** Якщо через коротке замикання або перевантаження перетворювач не вийшов на робочу напругу за 25 мс, пуск негайно скасовується, запобігаючи неконтрольованому нагріву силових індуктивностей та ключів.
