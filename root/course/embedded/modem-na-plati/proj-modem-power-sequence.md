# ⚙️ Драйвер апаратного керування та енергозбереження модема

Апаратне керування стільниковим модемом з боку мікроконтролера не зводиться до простого відправлення AT-команд у послідовний порт UART. Без надійного низькорівневого автомата станів, що контролює фізичні лінії `PWRKEY`, `STATUS`, `RESET_N`, `DTR` та переривання `RI`, вбудована система регулярно стикатиметься з зависаннями під час перезавантажень, втратою синхронізації після короткочасних збоїв живлення та перевитратою енергії акумулятора в режимах очікування.

Нижче наведено закінчену реалізацію неблокуючого апаратного драйвера керування стільниковим модемом на мовах C та ідіоматичному сучасному C++.

---

## 1. Архітектура автомата станів та часові вимоги

Драйвер реалізує неблокуючий скінченний автомат (Finite State Machine — FSM), який забезпечує повний контроль життєвого циклу модема без використання блокуючих затримок на зразок `delay_ms()`. Це дозволяє інтегрувати драйвер як у прості суперцикли (Super-Loop), так і в періодичні задачі операційних систем реального часу (FreeRTOS, Zephyr, RT-Thread).

```
   ┌─────────────┐
   │  POWER_OFF  │ ◄───────────────────────────┐
   └──────┬──────┘                             │
          │ request_power_on()                 │
          ▼                                    │
   ┌───────────────┐                           │
   │ PULSE_PWRKEY  │ (утримання 1000 мс)       │
   └──────┬────────┘                           │
          │ таймаут PWRKEY                     │
          ▼                                    │
   ┌───────────────┐                           │
   │  WAIT_STATUS  │ ───► [STATUS == HIGH] ──┐ │
   └──────┬────────┘                         │ │
          │ таймаут > 5000 мс                │ │
          ▼                                  ▼ │
   ┌───────────────┐                  ┌────────┴─────┐
   │RESET_RECOVERY │                  │ ACTIVE_READY │
   └───────────────┘                  └──────┬───────┘
                                             │ set_sleep(true) / RI
                                             ▼
                                      ┌──────────────┐
                                      │  SLEEP_MODE  │
                                      └──────────────┘
```

### Стани та правила переходів

1. **`POWER_OFF` (Модуль вимкнено):** початковий стан після подачі живлення на плату або після аварійного відключення. Лінія `STATUS` перебуває в низькому рівні (0 В).
2. **`PULSING_PWRKEY` (Імпульс увімкнення):** мікроконтролер притягує лінію `PWRKEY` до землі через вивід із відкритим стоком (Open-Drain). Тривалість імпульсу становить 1000 мс (для SIMCom SIM7600/SIM7080) або 500 мс (для Quectel BG95/EC25).
3. **`WAITING_STATUS` (Очікування завантаження ядра):** вивід `PWRKEY` відпускається у високоімпедансний стан. Драйвер очікує підйому сигналу `STATUS` у високий рівень (1.8 В). Якщо лінія підіймається в одиницю, модем успішно завантажив базову ОС, ініціалізував UART і готовий до роботи. Якщо протягом 5000 мс сигнал `STATUS` не з'явився, фіксується помилка старту.
4. **`ACTIVE_READY` (Робочий режим):** модем готовий приймати та обробляти AT-команди. UART активний.
5. **`SLEEP_MODE` (Енергоощадний сон):** лінія `DTR` піднята у високий рівень (HIGH). Модем вимикає тактування високошвидкісного інтерфейсу та переходить у режим eDRX або PSM зі струмом споживання менше ніж 1 мА.
6. **`RESET_RECOVERY` (Апаратне відновлення):** якщо модуль завис або не відповів на `PWRKEY`, драйвер генерує апаратний імпульс `RESET_N` тривалістю 250 мс, після чого повертається до очікування `STATUS`. Лічильник повторних спроб обмежує кількість циклів скидання для запобігання нескінченному перезавантаженню.

---

## 2. Реалізація драйвера

Драйвер ізольований від конкретного заліза за допомогою таблиці функцій зворотного виклику (Hardware Abstraction Layer — HAL), що дозволяє без змін переносити код між STM32, ESP32, nRF52 та Raspberry Pi Pico.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    MODEM_HW_OFF = 0,
    MODEM_HW_PULSING_PWRKEY,
    MODEM_HW_WAITING_STATUS,
    MODEM_HW_READY,
    MODEM_HW_SLEEP,
    MODEM_HW_RESET_RECOVERY,
    MODEM_HW_FAULT
} modem_hw_state_t;

typedef struct {
    void (*set_pwrkey)(bool low_active);
    void (*set_reset)(bool low_active);
    void (*set_dtr)(bool high_sleep);
    bool (*get_status)(void);
    uint32_t (*get_tick_ms)(void);
} modem_hal_t;

typedef struct {
    modem_hw_state_t state;
    uint32_t timer_start_ms;
    uint32_t pwrkey_pulse_ms;
    uint32_t boot_timeout_ms;
    uint8_t retry_count;
    bool ri_pending_event;
    modem_hal_t hal;
} modem_hw_driver_t;

void modem_hw_init(modem_hw_driver_t *drv, const modem_hal_t *hal) {
    drv->hal = *hal;
    drv->state = MODEM_HW_OFF;
    drv->pwrkey_pulse_ms = 1000;
    drv->boot_timeout_ms = 5000;
    drv->retry_count = 0;
    drv->ri_pending_event = false;

    drv->hal.set_pwrkey(false);
    drv->hal.set_reset(false);
    drv->hal.set_dtr(false);
}

void modem_hw_on_ri_isr(modem_hw_driver_t *drv) {
    drv->ri_pending_event = true;
}

void modem_hw_request_power_on(modem_hw_driver_t *drv) {
    if (drv->state == MODEM_HW_OFF || drv->state == MODEM_HW_FAULT) {
        drv->hal.set_pwrkey(true);
        drv->timer_start_ms = drv->hal.get_tick_ms();
        drv->state = MODEM_HW_PULSING_PWRKEY;
    }
}

void modem_hw_set_sleep(modem_hw_driver_t *drv, bool enable_sleep) {
    if (drv->state == MODEM_HW_READY && enable_sleep) {
        drv->hal.set_dtr(true);
        drv->state = MODEM_HW_SLEEP;
    } else if (drv->state == MODEM_HW_SLEEP && !enable_sleep) {
        drv->hal.set_dtr(false);
        drv->state = MODEM_HW_READY;
    }
}

void modem_hw_poll(modem_hw_driver_t *drv) {
    uint32_t now = drv->hal.get_tick_ms();

    switch (drv->state) {
        case MODEM_HW_PULSING_PWRKEY:
            if (now - drv->timer_start_ms >= drv->pwrkey_pulse_ms) {
                drv->hal.set_pwrkey(false);
                drv->timer_start_ms = now;
                drv->state = MODEM_HW_WAITING_STATUS;
            }
            break;

        case MODEM_HW_WAITING_STATUS:
            if (drv->hal.get_status()) {
                drv->state = MODEM_HW_READY;
                drv->retry_count = 0;
            } else if (now - drv->timer_start_ms >= drv->boot_timeout_ms) {
                if (drv->retry_count++ < 3) {
                    drv->hal.set_reset(true);
                    drv->timer_start_ms = now;
                    drv->state = MODEM_HW_RESET_RECOVERY;
                } else {
                    drv->state = MODEM_HW_FAULT;
                }
            }
            break;

        case MODEM_HW_RESET_RECOVERY:
            if (now - drv->timer_start_ms >= 250) {
                drv->hal.set_reset(false);
                drv->timer_start_ms = now;
                drv->state = MODEM_HW_WAITING_STATUS;
            }
            break;

        case MODEM_HW_SLEEP:
            if (drv->ri_pending_event) {
                drv->ri_pending_event = false;
                modem_hw_set_sleep(drv, false);
            }
            break;

        case MODEM_HW_READY:
        case MODEM_HW_OFF:
        case MODEM_HW_FAULT:
        default:
            break;
    }
}
```
```cpp
#include <chrono>
#include <cstdint>
#include <expected>
#include <functional>

enum class ModemState : uint8_t {
    Off,
    PulsingPwrkey,
    WaitingStatus,
    Ready,
    Sleep,
    ResetRecovery,
    Fault
};

enum class ModemError : uint8_t {
    BootTimeout,
    HardFault,
    InvalidState
};

struct ModemHalCallbacks {
    std::function<void(bool active_low)> set_pwrkey;
    std::function<void(bool active_low)> set_reset;
    std::function<void(bool high_sleep)> set_dtr;
    std::function<bool()> get_status;
};

class CellularModemHW {
public:
    using Milliseconds = std::chrono::milliseconds;

    explicit CellularModemHW(ModemHalCallbacks callbacks)
        : hal_(std::move(callbacks)),
          state_(ModemState::Off),
          pwrkey_pulse_(1000),
          boot_timeout_(5000),
          retry_count_(0),
          ri_pending_(false) {
        hal_.set_pwrkey(false);
        hal_.set_reset(false);
        hal_.set_dtr(false);
    }

    void on_ring_indicator_interrupt() noexcept {
        ri_pending_ = true;
    }

    std::expected<void, ModemError> request_power_on(Milliseconds now) {
        if (state_ == ModemState::Off || state_ == ModemState::Fault) {
            hal_.set_pwrkey(true);
            timer_start_ = now;
            state_ = ModemState::PulsingPwrkey;
            return {};
        }
        return std::unexpected(ModemError::InvalidState);
    }

    void set_sleep_mode(bool enable) {
        if (state_ == ModemState::Ready && enable) {
            hal_.set_dtr(true);
            state_ = ModemState::Sleep;
        } else if (state_ == ModemState::Sleep && !enable) {
            hal_.set_dtr(false);
            state_ = ModemState::Ready;
        }
    }

    void poll(Milliseconds now) {
        switch (state_) {
            case ModemState::PulsingPwrkey:
                if (now - timer_start_ >= pwrkey_pulse_) {
                    hal_.set_pwrkey(false);
                    timer_start_ = now;
                    state_ = ModemState::WaitingStatus;
                }
                break;

            case ModemState::WaitingStatus:
                if (hal_.get_status()) {
                    state_ = ModemState::Ready;
                    retry_count_ = 0;
                } else if (now - timer_start_ >= boot_timeout_) {
                    if (retry_count_++ < 3) {
                        hal_.set_reset(true);
                        timer_start_ = now;
                        state_ = ModemState::ResetRecovery;
                    } else {
                        state_ = ModemState::Fault;
                    }
                }
                break;

            case ModemState::ResetRecovery:
                if (now - timer_start_ >= Milliseconds(250)) {
                    hal_.set_reset(false);
                    timer_start_ = now;
                    state_ = ModemState::WaitingStatus;
                }
                break;

            case ModemState::Sleep:
                if (ri_pending_) {
                    ri_pending_ = false;
                    set_sleep_mode(false);
                }
                break;

            case ModemState::Ready:
            case ModemState::Off:
            case ModemState::Fault:
                break;
        }
    }

    [[nodiscard]] ModemState current_state() const noexcept {
        return state_;
    }

    [[nodiscard]] bool is_ready() const noexcept {
        return state_ == ModemState::Ready;
    }

private:
    ModemHalCallbacks hal_;
    ModemState state_;
    Milliseconds timer_start_{0};
    Milliseconds pwrkey_pulse_;
    Milliseconds boot_timeout_;
    uint8_t retry_count_;
    bool ri_pending_;
};
```
:::

---

## 3. Практичні підводні камені та типові помилки реалізації

1. **Конфігурація виводу Push-Pull замість Open-Drain на лінії `PWRKEY`:**
   Пін `PWRKEY` усередині модуля підтягнутий до внутрішньої шини 1.8 В або безпосередньо до `VBAT` через резистор. Якщо мікроконтролер працює від 3.3 В і його вивід сконфігуровано як Push-Pull, то при виставленні високого рівня напруга 3.3 В потрапляє на чутливий вхід PMIC модема. Це відкриває внутрішній захисний діод у прямий напрямок, спричиняє паразитне живлення ядра через сигнальну лінію та може призвести до теплового пробою вхідного каскаду. Вивід МК слід завжди конфігурувати як Open-Drain без зовнішньої підтяжки до 3.3 В або використовувати дискретний N-канальний польовий транзистор (BSS138).

2. **Передчасне надсилання AT-команд до завершення ініціалізації ядра:**
   Поширена помилка розробників-початківців — починати надсилати команду `AT\r` відразу після відпускання `PWRKEY`. Стільниковий модуль містить повноцінне процесорне ядро (часто на базі ARM Cortex-A7 чи DSP), якому для завантаження ядра Linux/ThreadX, зчитування калібрувальних таблиць з Flash-пам'яті та ініціалізації радіочастотних гетеродинів потрібно від 2 до 5 секунд. Спроба надсилати байти в неініціалізований UART призводить до переповнення вхідного апаратного буфера FIFO та зависання інтерфейсу. Драйвер зобов'язаний контролювати підйом сигналу `STATUS` перед відкриттям обміну.

3. **Зловживання лінією аварійного скидання `RESET_N`:**
   Сигнал `RESET_N` призначений виключно як крайній засіб порятунку від фатального зависання, коли модуль не реагує на AT-команди та `PWRKEY` понад 10–15 секунд. Часте смикання лінії `RESET_N` під час штатної роботи (наприклад, перед кожним сеансом передачі даних) призводить до раптового знеструмлення контролера флеш-пам'яті в момент запису службових журналів соти. Це викликає пошкодження файлової системи NVRAM/EFS, після чого модуль назавжди втрачає заводські калібрування і перестає реєструватися в мережі оператора.

4. **Втрата першого символу після виходу з режиму сну по лінії `DTR`:**
   Коли модем перебуває в режимі сну (`DTR = HIGH`), його внутрішній високочастотний генератор PLL вимкнено для економії енергії. При притягненні лінії `DTR` до нуля для передачі даних генератору потрібно від 10 до 25 мс для стабілізації частоти тактування UART. Якщо мікроконтролер почне передавати байти негайно після переводу `DTR` у LOW, перший символ (зазвичай літера `A` в команді `AT`) буде спотворений або втрачений, що викличе помилку таймауту відповіді.

5. **Інтеграція в RTOS та сторожовий таймер (Watchdog):**
   При запуску автомата в окремій задачі RTOS період виклику функції `poll()` зазвичай встановлюють на рівні 10–50 мс. Оскільки вся логіка побудована на неблокуючих перевірках мілісекундних міток, задача модема не монополізує процесорний час і дозволяє системному сторожовому таймеру (Independent Watchdog — IWDG) своєчасно отримувати скидання.
