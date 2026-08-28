# ⚙️ Кінцевий автомат керування режимами та розрахунок енергоспоживання модема

У цьому проєкті реалізовано надійний неблокувальний кінцевий автомат (FSM, Finite State Machine) для керування життєвим циклом стільникового модема у вбудованих системах, розрахунку балансу енергоспоживання між поколіннями зв'язку (2G GSM, 4G Cat.1bis та 5G RedCap), проектування буферної ємності шини живлення та захисту від апаратних збоїв.

---

### Розрахунок ємності буферного конденсатора шини живлення

Під час вибору покоління стільникового зв'язку ключовим апаратним обмеженням є піковий струм передавача `I_peak` та тривалість імпульсу `t_burst`. Якщо внутрішній опір джерела живлення (батареї або LDO) `R_int` занадто високий, імпульс струму створює падіння напруги `ΔV = I_peak · R_int`. Коли напруга на виводах модема опускається нижче порогу вимкнення (Brownout Reset, типово 3.3 В для 2G або 3.1 В для 4G), внутрішній контролер живлення модема негайно вимикає пристрій.

Для компенсації імпульсу паралельно шині живлення встановлюють буферний конденсатор із низьким еквівалентним послідовним опором (Low ESR). Необхідна ємність розраховується за формулою балансу заряду:

```
C ≥ (I_peak - I_source) · t_burst / ΔV_max
```

де:
- `I_peak` — максимальний струм передавача під час випромінювання максимальної потужності;
- `I_source` — максимальний тривалий струм, який здатне віддати первинне джерело живлення;
- `t_burst` — тривалість найдовшого безперервного імпульсу передачі;
- `ΔV_max` — максимально допустиме просідання напруги на шині живлення без перезавантаження модема (типово 0.3–0.4 В).

#### Порівняння вимог до буферної ємності за поколіннями

1. **2G GSM / GPRS (Class 10):**
   - `I_peak = 2.0 А`, `I_source = 0.5 А`, `t_burst = 577 мкс` (один TDMA-слот), `ΔV_max = 0.3 В`.
   - `C ≥ (2.0 - 0.5) · 0.000577 / 0.3 = 2885 мкФ`.
   - **Апаратне рішення:** потрібна батарея танталових або полімерних конденсаторів ємністю не менше 2200–3300 мкФ з ESR < 50 мОм або іоністор (суперконденсатор).
   - **Небезпека пускового струму (Inrush Current):** розряджений конденсатор на 2200 мкФ під час подачі живлення спричиняє короткочасне коротке замикання, що може призвести до спрацьовування плати захисту літієвого акумулятора (BMS). Потрібно застосовувати схему м'якого старту (Soft-Start) або обмежувальний резистор.

2. **4G LTE Cat.1bis / 5G RedCap:**
   - Завдяки модуляції SC-FDMA передавач випромінює потужність рівномірно (без імпульсів 2 А).
   - `I_peak = 0.25 А`, `I_source = 0.15 А`, тривалість плавної зміни `t_step = 1.0 мс`, `ΔV_max = 0.2 В`.
   - `C ≥ (0.25 - 0.15) · 0.001 / 0.2 = 500 мкФ` (на практиці вистачає двох керамічних конденсаторів X7R по 100 мкФ).

---

### Розрахунок енергетичного бюджету та автономності пристрою

Сумарний заряд `Q_total`, витрачений за один сеанс передачі телеметрії, складається з кількох фаз:

```
Q_total = Q_boot + Q_net_search + Q_tx_rx + Q_active + Q_sleep
```

де кожна складова обчислюється як інтеграл струму за часом `Q = I · t`.

#### Порівняльний розрахунок автономності для батареї ємністю 2000 мА·год (період сесії 1 година):

1. **Застарілий 2G GPRS трекер:**
   - Фаза завантаження та пошуку мережі: струм 60 мА протягом 15 секунд (`900 мА·с`).
   - Фаза передачі пакета даних: середній струм 180 мА протягом 5 секунд (`900 мА·с`).
   - Фаза простою (Idle/DRX без PSM, оскільки 2G не підтримує глибокий сон): струм 2.5 мА протягом 3540 секунд (`8850 мА·с`).
   - Сумарний заряд за сеанс: `10650 мА·с = 2.96 мА·год`.
   - **Час автономної роботи:** `2000 / 2.96 = 675 годин ≈ 28 діб`.

2. **Сучасний 4G Cat.1bis / 5G RedCap модуль із підтримкою PSM:**
   - Завдяки збереженню контексту IP-сесії в пам'яті ядра мережі повторна реєстрація (Attach) не потрібна:
   - Пробудження та передача даних: струм 100 мА протягом 1.8 секунди (`180 мА·с`).
   - Активний таймер `T3324` (очікування відповіді сервера): струм 12 мА протягом 4 секунд (`48 мА·с`).
   - Фаза глибокого сну PSM: струм 3.5 мкА протягом 3594.2 секунди (`12.6 мА·с`).
   - Сумарний заряд за сеанс: `240.6 мА·с = 0.0668 мА·год`.
   - **Час автономної роботи:** `2000 / 0.0668 = 29940 годин ≈ 3.4 роки` (у 44 рази довше за 2G при тому самому акумуляторі).

---

### Архітектура кінцевого автомата (FSM) модема

Кінцевий автомат керує послідовністю переходів між станами з урахуванням тайм-аутів та стратегії експоненційного відступу (Exponential Backoff) у разі тимчасової втрати покриття оператора:

```
[POWER_OFF] ──(PWRKEY pulse)──> [BOOT_WAIT] ──(AT sync)──> [RAT_CONFIG]
                                                                │
   ┌────────────────────────────────────────────────────────────┘
   ▼
[NET_SEARCH] ──(CEREG=1/5)──> [DATA_TRANSMIT] ──(Success)──> [WAIT_PSM / SLEEP]
   ▲                                 │                               │
   │ (Link Loss)                     │ (Fail)                        │ (Timer Wakeup)
   └─────────────────────────────────┴───────────────────────────────┘
```

---

### Реалізація драйвера керування модемом

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef enum {
    MODEM_RAT_2G_GSM = 12,
    MODEM_RAT_4G_LTE = 28,
    MODEM_RAT_5G_NR  = 30,
    MODEM_RAT_AUTO   = 255
} ModemRat_t;

typedef enum {
    STATE_POWER_OFF,
    STATE_PULSE_PWRKEY,
    STATE_WAIT_BOOT,
    STATE_SYNC_AT,
    STATE_CONFIG_RAT,
    STATE_WAIT_NETWORK,
    STATE_TRANSMIT_DATA,
    STATE_ENTER_PSM,
    STATE_ERROR_RECOVERY
} FsmState_t;

typedef struct {
    FsmState_t state;
    ModemRat_t target_rat;
    uint32_t   state_timer_ms;
    uint32_t   backoff_interval_ms;
    uint8_t    retry_count;
    bool       network_registered;
    int16_t    rsrp_dbm;
    int8_t     rsrq_db;
} ModemDriver_t;

/* Апаратні виклики платформи (BSP) */
extern void bsp_gpio_set_pwrkey(bool level);
extern void bsp_gpio_set_dtr(bool level);
extern void bsp_uart_send_string(const char *str);
extern uint32_t bsp_get_tick_ms(void);

void modem_init(ModemDriver_t *drv, ModemRat_t rat) {
    drv->state = STATE_POWER_OFF;
    drv->target_rat = rat;
    drv->state_timer_ms = 0;
    drv->backoff_interval_ms = 1000;
    drv->retry_count = 0;
    drv->network_registered = false;
    drv->rsrp_dbm = -140;
    drv->rsrq_db = -20;
}

void modem_fsm_step(ModemDriver_t *drv, const char *uart_rx_line) {
    uint32_t now = bsp_get_tick_ms();

    switch (drv->state) {
        case STATE_POWER_OFF:
            bsp_gpio_set_pwrkey(true);
            drv->state_timer_ms = now;
            drv->state = STATE_PULSE_PWRKEY;
            break;

        case STATE_PULSE_PWRKEY:
            /* Імпульс PWRKEY тривалістю 800 мс для запуску внутрішнього PMIC */
            if (now - drv->state_timer_ms >= 800) {
                bsp_gpio_set_pwrkey(false);
                drv->state_timer_ms = now;
                drv->state = STATE_WAIT_BOOT;
            }
            break;

        case STATE_WAIT_BOOT:
            /* Очікування виходу інтерфейсу UART на робочий режим (2500 мс) */
            if (now - drv->state_timer_ms >= 2500) {
                drv->retry_count = 0;
                bsp_uart_send_string("ATE0\r\n");
                drv->state_timer_ms = now;
                drv->state = STATE_SYNC_AT;
            }
            break;

        case STATE_SYNC_AT:
            if (uart_rx_line && strstr(uart_rx_line, "OK")) {
                /* Налаштування покоління зв'язку через 3GPP команду +WS46 */
                if (drv->target_rat == MODEM_RAT_4G_LTE) {
                    bsp_uart_send_string("AT+WS46=28\r\n");
                } else if (drv->target_rat == MODEM_RAT_2G_GSM) {
                    bsp_uart_send_string("AT+WS46=12\r\n");
                } else {
                    bsp_uart_send_string("AT+WS46=255\r\n");
                }
                drv->state_timer_ms = now;
                drv->state = STATE_CONFIG_RAT;
            } else if (now - drv->state_timer_ms > 1000) {
                if (++drv->retry_count > 10) {
                    drv->state = STATE_ERROR_RECOVERY;
                } else {
                    bsp_uart_send_string("AT\r\n");
                    drv->state_timer_ms = now;
                }
            }
            break;

        case STATE_CONFIG_RAT:
            if (uart_rx_line && strstr(uart_rx_line, "OK")) {
                /* Увімкнення URC сповіщень реєстрації у 4G та перевірка мережі */
                bsp_uart_send_string("AT+CEREG=2;+CESQ\r\n");
                drv->state_timer_ms = now;
                drv->state = STATE_WAIT_NETWORK;
            } else if (now - drv->state_timer_ms > 3000) {
                drv->state = STATE_ERROR_RECOVERY;
            }
            break;

        case STATE_WAIT_NETWORK:
            if (uart_rx_line) {
                if (strstr(uart_rx_line, "+CEREG: 2,1") || strstr(uart_rx_line, "+CEREG: 2,5")) {
                    drv->network_registered = true;
                    drv->state = STATE_TRANSMIT_DATA;
                }
            }
            if (now - drv->state_timer_ms > 60000) {
                /* Тайм-аут пошуку мережі (60 с) -> перехід у сон для збереження АКБ */
                drv->state = STATE_ERROR_RECOVERY;
            }
            break;

        case STATE_TRANSMIT_DATA:
            /* Відправка бінарного телеметричного кадру на сервер */
            bsp_uart_send_string("AT+QMTOPEN=...\r\n");
            drv->state = STATE_ENTER_PSM;
            break;

        case STATE_ENTER_PSM:
            /* Активація режиму глибокого сну PSM з періодом 24 години */
            bsp_uart_send_string("AT+CPSMS=1,,,\"00111000\",\"00000010\"\r\n");
            bsp_gpio_set_dtr(true); /* Дозволити модему заснути по лінії DTR */
            break;

        case STATE_ERROR_RECOVERY:
            /* Експоненційний відступ: подвоєння паузи до максимуму 15 хвилин */
            drv->backoff_interval_ms = (drv->backoff_interval_ms * 2 < 900000) 
                                       ? drv->backoff_interval_ms * 2 : 900000;
            bsp_gpio_set_dtr(true);
            drv->state = STATE_POWER_OFF;
            break;
    }
}
```
```cpp
#include <cstdint>
#include <string_view>
#include <chrono>
#include <expected>
#include <array>
#include <span>

enum class ModemRat : uint8_t {
    Gsm2G = 12,
    Lte4G = 28,
    Nr5G  = 30,
    Auto  = 255
};

enum class FsmState : uint8_t {
    PowerOff,
    PulsePwrkey,
    WaitBoot,
    SyncAt,
    ConfigRat,
    WaitNetwork,
    TransmitData,
    EnterPsm,
    ErrorRecovery
};

enum class DriverError {
    Timeout,
    SimLocked,
    RegistrationDenied,
    HardwareFault
};

class CellularModem {
public:
    explicit CellularModem(ModemRat rat) noexcept
        : target_rat_(rat), state_(FsmState::PowerOff), backoff_(std::chrono::seconds(1)) {}

    void step(std::string_view rx_line, std::chrono::milliseconds now) noexcept {
        switch (state_) {
            case FsmState::PowerOff:
                set_pwrkey(true);
                state_timer_ = now;
                state_ = FsmState::PulsePwrkey;
                break;

            case FsmState::PulsePwrkey:
                if (now - state_timer_ >= std::chrono::milliseconds(800)) {
                    set_pwrkey(false);
                    state_timer_ = now;
                    state_ = FsmState::WaitBoot;
                }
                break;

            case FsmState::WaitBoot:
                if (now - state_timer_ >= std::chrono::milliseconds(2500)) {
                    retries_ = 0;
                    send_command("ATE0\r\n");
                    state_timer_ = now;
                    state_ = FsmState::SyncAt;
                }
                break;

            case FsmState::SyncAt:
                if (rx_line.find("OK") != std::string_view::npos) {
                    if (target_rat_ == ModemRat::Lte4G) {
                        send_command("AT+WS46=28\r\n");
                    } else if (target_rat_ == ModemRat::Gsm2G) {
                        send_command("AT+WS46=12\r\n");
                    } else {
                        send_command("AT+WS46=255\r\n");
                    }
                    state_timer_ = now;
                    state_ = FsmState::ConfigRat;
                } else if (now - state_timer_ >= std::chrono::seconds(1)) {
                    if (++retries_ > 10) {
                        state_ = FsmState::ErrorRecovery;
                    } else {
                        send_command("AT\r\n");
                        state_timer_ = now;
                    }
                }
                break;

            case FsmState::ConfigRat:
                if (rx_line.find("OK") != std::string_view::npos) {
                    send_command("AT+CEREG=2;+CESQ\r\n");
                    state_timer_ = now;
                    state_ = FsmState::WaitNetwork;
                } else if (now - state_timer_ >= std::chrono::seconds(3)) {
                    state_ = FsmState::ErrorRecovery;
                }
                break;

            case FsmState::WaitNetwork:
                if (rx_line.find("+CEREG: 2,1") != std::string_view::npos ||
                    rx_line.find("+CEREG: 2,5") != std::string_view::npos) {
                    registered_ = true;
                    state_ = FsmState::TransmitData;
                } else if (now - state_timer_ >= std::chrono::seconds(60)) {
                    state_ = FsmState::ErrorRecovery;
                }
                break;

            case FsmState::TransmitData:
                send_command("AT+QMTOPEN=...\r\n");
                state_ = FsmState::EnterPsm;
                break;

            case FsmState::EnterPsm:
                send_command("AT+CPSMS=1,,,\"00111000\",\"00000010\"\r\n");
                set_dtr(true);
                break;

            case FsmState::ErrorRecovery:
                backoff_ = std::min(backoff_ * 2, std::chrono::seconds(900));
                set_dtr(true);
                state_ = FsmState::PowerOff;
                break;
        }
    }

    [[nodiscard]] bool is_registered() const noexcept { return registered_; }
    [[nodiscard]] FsmState current_state() const noexcept { return state_; }

private:
    void send_command(std::string_view cmd) noexcept {
        /* Платформне надсилання байтів у UART */
    }

    void set_pwrkey(bool active) noexcept {
        /* Керування лінією PWRKEY через GPIO */
    }

    void set_dtr(bool active) noexcept {
        /* Керування лінією сну DTR */
    }

    ModemRat target_rat_;
    FsmState state_;
    std::chrono::milliseconds state_timer_{0};
    std::chrono::seconds backoff_;
    uint8_t retries_{0};
    bool registered_{false};
};
```
:::

---

### Пастки реалізації та інженерні крайові випадки

1. **Інтерференція асинхронних повідомлень (URC Race Condition):**
   Під час активного виконання AT-команд мережа може надіслати асинхронне сповіщення (наприклад, `+CEREG: 2` або `+CSQ: 18,99`). Якщо драйвер очікує рядок `OK` одразу після команди, вставка URC між рядками розриває простий строковий парсер. Парсер зобов'язаний спочатку відокремлювати всі відомі URC через префіксний пошук (`+CEREG:`, `+CESQ:`, `RING`, `NO CARRIER`), оновлювати атомарні змінні стану драйвера і лише потім передавати чистий буфер обробнику відповідей на команди.

2. **Виснаження батареї під час виходу із зони покриття (Out-of-Coverage Loop):**
   Якщо базові станції недоступні, модем на максимальній потужності передавача безперервно сканує всі доступні діапазони, споживаючи від 100 до 300 мА. За кілька годин такий режим повністю розряджає літієву батарею. Застосування алгоритму експоненційного відступу (паузи між спробами пошуку: 1 хв → 2 хв → 4 хв → 15 хв з переведенням модема в `AT+CFUN=0` або зняттям живлення) зберігає автономність пристрою на роки.

3. **Узгодження рівнів сигналів UART (1.8 В проти 3.3 В):**
   Більшість стільникових модулів мають логічні рівні цифрових виводів UART 1.8 В (V_IO = 1.8 В). Пряме підключення до 3.3-вольтового мікроконтролера гарантовано пробиває захисні діоди вхідних каскадів модема. Необхідно застосовувати двонаправлені перетворювачі рівнів (наприклад, TXS0108E або польові N-канальні MOSFET із підтяжками до відповідних шин живлення).
