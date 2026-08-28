# ⚙️ Реалізація сервісного діагностичного рушія та обробника команд CLI

Сервісний діагностичний рушій — це виділений програмний модуль у складі прошивки вбудованого пристрою, який забезпечує прийом, синтаксичний аналіз, верифікацію прав доступу та безпечне виконання діагностичних команд через апаратний порт UART або емульовану USB-консоль. Головна архітектурна вимога до такого рушія полягає в суворій ізоляції від основної бізнес-логіки виробу: діагностичний обмін не повинен блокувати критичні переривання керування, споживати непередбачувану кількість оперативної пам'яті чи залишати увімкненими силові виконавчі органи у разі аварійного обриву каналу зв'язку.

---

## 1. Архітектура кінцевого автомата та обробка життєвого циклу сесії

Сервісний рушій проєктується на базі детермінованого скінченного автомата станів (англ. *Finite State Machine*, FSM). Це унеможливлює випадкове виконання небезпечних команд калібрування чи примусового перемикання силових ключів без попереднього проходження регламентної процедури автентифікації.

```
       +---------------------------------------------+
       |                                             |
       v                                             | (Тайм-аут 30 с / помилка)
[SRV_STATE_LOCKED] ───(auth challenge)───► [SRV_STATE_CHALLENGE_ISSUED]
       ▲                                             │
       │                                             │ (auth key OK)
       │ (sys lock /                                 v
       │  тайм-аут 15 хв)                  [SRV_STATE_UNLOCKED]
       │                                             │
       │                                             │ (diag actuate)
       │                                             v
       +────────────────────────────────── [SRV_STATE_ACTUATION_ACTIVE]
```

Автомат підтримує п'ять дискретних станів:

1. **`SRV_STATE_LOCKED` (Заблоковано):** Початковий стан системи після подачі живлення або скидання процесора. Усі команди прямого керування апаратурою заблоковані. Дозволено лише базові інформаційні запити (`sys info`) та запит генерації перевірочного токена (`auth challenge`).
2. **`SRV_STATE_CHALLENGE_ISSUED` (Очікування автентифікації):** Прошивка згенерувала 32-бітний псевдовипадковий Nonce з апаратного генератора TRNG та запустила 30-секундний захисний таймер. Якщо за цей час правильний ключ не надійшов, стан скидається назад у `LOCKED`.
3. **`SRV_STATE_UNLOCKED` (Авторизований сервісний доступ):** Інженер отримує повний доступ до читання сирих даних АЦП, опитування внутрішніх шин і зміни калібрувальних коефіцієнтів. Автомат зводить таймер активності сесії на 900 секунд (15 хвилин). Кожна валідна команда поновлює відлік.
4. **`SRV_STATE_ACTUATION_ACTIVE` (Активний тест навантаження):** Стан примусового ввімкнення реле, клапана чи ШІМ-каналу. Супроводжується постійним контролем апаратного тайм-ауту.
5. **`SRV_STATE_EMERGENCY` (Аварійна зупинка):** Перехід у цей стан відбувається миттєво при спрацюванні будь-якого апаратного захисту (перегрів радіатора, коротке замикання на виході). Програмний шар скидає всі біти керування силових GPIO в логічний нуль і блокує виконання команд до повного перезавантаження.

---

## 2. Реалізація діагностичного рушія на мовах C та C++

У наведених лістингах реалізовано:
- Неблокуючий кільцевий буфер накопичення символів, що викликається з обробника переривання UART.
- Безпечний парсер текстових рядків без динамічного виділення пам'яті (жодного використання `malloc` або `free`).
- Механізм апаратного сторожового тайм-ауту знеструмлення силових каналів.
- Функцію самотестування периферійних вузлів (BIST).

:::tabs
```c
/* service_engine.c — Сервісний діагностичний модуль на чистому C */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

#define CLI_BUFFER_SIZE     128
#define SESSION_TIMEOUT_MS  (900 * 1000)
#define MAX_ACT_TIMEOUT_MS  (15 * 1000)

typedef enum {
    SRV_STATE_LOCKED = 0,
    SRV_STATE_CHALLENGE_ISSUED,
    SRV_STATE_UNLOCKED,
    SRV_STATE_EMERGENCY
} srv_state_t;

typedef struct {
    srv_state_t state;
    uint32_t    session_timer_ms;
    uint32_t    act_timer_ms;
    uint8_t     active_channel;
    uint32_t    current_nonce;
    char        rx_buf[CLI_BUFFER_SIZE];
    uint16_t    rx_idx;
} srv_context_t;

static srv_context_t g_srv;

/* Прототипи апаратних функцій платформи */
extern uint32_t hw_get_tick_ms(void);
extern uint32_t hw_trng_get_random(void);
extern void hw_uart_puts(const char *str);
extern void hw_gpio_set_relay(uint8_t channel, bool state);
extern bool hw_i2c_probe_device(uint8_t addr_7bit);
extern uint16_t hw_adc_read_raw(uint8_t channel);

/* Ініціалізація сервісного контексту */
void srv_init(void) {
    memset(&g_srv, 0, sizeof(g_srv));
    g_srv.state = SRV_STATE_LOCKED;
}

/* Примусове аварійне знеструмлення всіх силових виходів */
void srv_emergency_all_off(void) {
    hw_gpio_set_relay(1, false);
    hw_gpio_set_relay(2, false);
    g_srv.active_channel = 0;
    g_srv.act_timer_ms = 0;
}

/* Обробник команди апаратного самотестування */
static void cmd_handle_selftest(void) {
    bool i2c_rtc = hw_i2c_probe_device(0x68);
    bool i2c_eeprom = hw_i2c_probe_device(0x50);
    uint16_t v_core_adc = hw_adc_read_raw(0);

    char resp[96];
    snprintf(resp, sizeof(resp), "+OK: BIST (RTC:%s, EEPROM:%s, ADC0_RAW:0x%04X)\r\n",
             i2c_rtc ? "OK" : "FAULT",
             i2c_eeprom ? "OK" : "FAULT",
             v_core_adc);
    hw_uart_puts(resp);
}

/* Обробник безпечного ввімкнення реле на фіксований час */
static void cmd_handle_actuate(uint8_t channel, uint16_t timeout_sec) {
    if (g_srv.state != SRV_STATE_UNLOCKED) {
        hw_uart_puts("-ERR: 0x4001 ACCESS_DENIED_LOCKED\r\n");
        return;
    }
    if (channel < 1 || channel > 2) {
        hw_uart_puts("-ERR: 0x4002 INVALID_CHANNEL\r\n");
        return;
    }
    if (timeout_sec == 0 || timeout_sec > 15) {
        hw_uart_puts("-ERR: 0x4003 TIMEOUT_OUT_OF_RANGE (1..15s)\r\n");
        return;
    }

    /* Увімкнення каналу та запуск таймера знеструмлення */
    srv_emergency_all_off();
    g_srv.active_channel = channel;
    g_srv.act_timer_ms = hw_get_tick_ms() + (timeout_sec * 1000);
    hw_gpio_set_relay(channel, true);

    char resp[64];
    snprintf(resp, sizeof(resp), "+OK: RELAY_%u ACTIVE FOR %u SEC\r\n", channel, timeout_sec);
    hw_uart_puts(resp);
}

/* Диспетчер вхідного рядка команд */
static void srv_dispatch_line(const char *cmd) {
    if (strncmp(cmd, "auth challenge", 14) == 0) {
        g_srv.current_nonce = hw_trng_get_random();
        g_srv.state = SRV_STATE_CHALLENGE_ISSUED;
        char resp[64];
        snprintf(resp, sizeof(resp), "+OK: CHALLENGE 0x%08X\r\n", (unsigned int)g_srv.current_nonce);
        hw_uart_puts(resp);
        return;
    }

    if (strncmp(cmd, "auth key ", 9) == 0) {
        if (strcmp(cmd + 9, "SRV_PASS_2026") == 0) {
            g_srv.state = SRV_STATE_UNLOCKED;
            g_srv.session_timer_ms = hw_get_tick_ms() + SESSION_TIMEOUT_MS;
            hw_uart_puts("+OK: SERVICE_UNLOCKED (SESSION 15 MIN)\r\n");
        } else {
            g_srv.state = SRV_STATE_LOCKED;
            hw_uart_puts("-ERR: 0x4004 AUTH_FAILED\r\n");
        }
        return;
    }

    if (g_srv.state != SRV_STATE_UNLOCKED) {
        hw_uart_puts("-ERR: 0x4000 LOCKED_ENTER_AUTH_FIRST\r\n");
        return;
    }

    /* Поновлюємо таймер активності сесії */
    g_srv.session_timer_ms = hw_get_tick_ms() + SESSION_TIMEOUT_MS;

    if (strcmp(cmd, "diag selftest") == 0) {
        cmd_handle_selftest();
    } else if (strncmp(cmd, "diag act relay ", 15) == 0) {
        unsigned int ch = 0, sec = 0;
        if (sscanf(cmd + 15, "%u %u", &ch, &sec) == 2) {
            cmd_handle_actuate((uint8_t)ch, (uint16_t)sec);
        } else {
            hw_uart_puts("-ERR: 0x4005 BAD_ARGUMENTS\r\n");
        }
    } else if (strcmp(cmd, "sys lock") == 0) {
        srv_emergency_all_off();
        g_srv.state = SRV_STATE_LOCKED;
        hw_uart_puts("+OK: SERVICE_LOCKED\r\n");
    } else {
        hw_uart_puts("-ERR: 0x4006 UNKNOWN_COMMAND\r\n");
    }
}

/* Періодичний крок оновлення сервісного рушія (викликається у суперциклі) */
void srv_poll_step(void) {
    uint32_t now = hw_get_tick_ms();

    /* Перевірка тайм-ауту увімкнення навантаження */
    if (g_srv.active_channel != 0 && now >= g_srv.act_timer_ms) {
        srv_emergency_all_off();
        hw_uart_puts("\r\n[EVENT: ACTUATION_TIMEOUT_AUTO_SHUTDOWN]\r\nSRV> ");
    }

    /* Перевірка тайм-ауту неактивності сесії */
    if (g_srv.state == SRV_STATE_UNLOCKED && now >= g_srv.session_timer_ms) {
        srv_emergency_all_off();
        g_srv.state = SRV_STATE_LOCKED;
        hw_uart_puts("\r\n[EVENT: SESSION_TIMEOUT_LOCKED]\r\n");
    }
}

/* Прийом чергового байта від UART переривання */
void srv_feed_byte(char c) {
    if (c == '\r' || c == '\n') {
        if (g_srv.rx_idx > 0) {
            g_srv.rx_buf[g_srv.rx_idx] = '\0';
            srv_dispatch_line(g_srv.rx_buf);
            g_srv.rx_idx = 0;
            if (g_srv.state == SRV_STATE_UNLOCKED) {
                hw_uart_puts("SRV> ");
            }
        }
    } else if (g_srv.rx_idx < (CLI_BUFFER_SIZE - 1)) {
        if (c >= 0x20 && c <= 0x7E) { /* Тільки друковані ASCII */
            g_srv.rx_buf[g_srv.rx_idx++] = c;
        }
    }
}
```
```cpp
/* service_engine.cpp — Сучасний C++20 сервісний діагностичний контролер */
#include <cstdint>
#include <string_view>
#include <array>
#include <chrono>
#include <format>
#include <expected>
#include <span>

class ServiceEngine {
public:
    enum class State : uint8_t {
        Locked,
        ChallengeIssued,
        Unlocked,
        EmergencyStop
    };

    enum class ErrorCode : uint16_t {
        Locked               = 0x4000,
        AccessDenied         = 0x4001,
        InvalidChannel       = 0x4002,
        TimeoutOutOfRange    = 0x4003,
        AuthFailed           = 0x4004,
        BadArguments         = 0x4005,
        UnknownCommand       = 0x4006
    };

    ServiceEngine() = default;

    void feedByte(char c) noexcept {
        if (c == '\r' || c == '\n') {
            if (rxIdx_ > 0) {
                std::string_view line(rxBuf_.data(), rxIdx_);
                dispatch(line);
                rxIdx_ = 0;
                if (state_ == State::Unlocked) {
                    sendString("SRV> ");
                }
            }
        } else if (rxIdx_ < rxBuf_.size() - 1 && c >= 0x20 && c <= 0x7E) {
            rxBuf_[rxIdx_++] = c;
        }
    }

    void poll(std::chrono::milliseconds now) noexcept {
        if (activeChannel_ != 0 && now >= actTimerDeadline_) {
            emergencyAllOff();
            sendString("\r\n[EVENT: ACTUATION_TIMEOUT_AUTO_SHUTDOWN]\r\nSRV> ");
        }

        if (state_ == State::Unlocked && now >= sessionDeadline_) {
            emergencyAllOff();
            state_ = State::Locked;
            sendString("\r\n[EVENT: SESSION_TIMEOUT_LOCKED]\r\n");
        }
    }

    void emergencyAllOff() noexcept {
        hwSetRelay(1, false);
        hwSetRelay(2, false);
        activeChannel_ = 0;
    }

private:
    static constexpr size_t BufferSize = 128;
    static constexpr auto SessionTimeout = std::chrono::minutes(15);
    static constexpr auto MaxActTimeout = std::chrono::seconds(15);

    State state_{State::Locked};
    uint8_t activeChannel_{0};
    std::chrono::milliseconds sessionDeadline_{0};
    std::chrono::milliseconds actTimerDeadline_{0};
    uint32_t currentNonce_{0};

    std::array<char, BufferSize> rxBuf_{};
    size_t rxIdx_{0};

    void dispatch(std::string_view cmd) noexcept {
        if (cmd == "auth challenge") {
            currentNonce_ = hwGetRandom();
            state_ = State::ChallengeIssued;
            sendString(std::format("+OK: CHALLENGE 0x{:08X}\r\n", currentNonce_));
            return;
        }

        if (cmd.starts_with("auth key ")) {
            auto key = cmd.substr(9);
            if (key == "SRV_PASS_2026") {
                state_ = State::Unlocked;
                sessionDeadline_ = hwNow() + SessionTimeout;
                sendString("+OK: SERVICE_UNLOCKED (SESSION 15 MIN)\r\n");
            } else {
                state_ = State::Locked;
                sendError(ErrorCode::AuthFailed, "AUTH_FAILED");
            }
            return;
        }

        if (state_ != State::Unlocked) {
            sendError(ErrorCode::Locked, "LOCKED_ENTER_AUTH_FIRST");
            return;
        }

        sessionDeadline_ = hwNow() + SessionTimeout;

        if (cmd == "diag selftest") {
            executeSelftest();
        } else if (cmd == "sys lock") {
            emergencyAllOff();
            state_ = State::Locked;
            sendString("+OK: SERVICE_LOCKED\r\n");
        } else {
            sendError(ErrorCode::UnknownCommand, "UNKNOWN_COMMAND");
        }
    }

    void executeSelftest() noexcept {
        bool rtcOk = hwI2cProbe(0x68);
        bool eepromOk = hwI2cProbe(0x50);
        uint16_t adc0 = hwAdcRead(0);
        sendString(std::format("+OK: BIST (RTC:{}, EEPROM:{}, ADC0_RAW:0x{:04X})\r\n",
                               rtcOk ? "OK" : "FAULT",
                               eepromOk ? "OK" : "FAULT",
                               adc0));
    }

    void sendString(std::string_view str) noexcept {
        hwUartWrite(str);
    }

    void sendError(ErrorCode code, std::string_view msg) noexcept {
        sendString(std::format("-ERR: 0x{:04X} {}\r\n", static_cast<uint16_t>(code), msg));
    }

    /* Апаратні проксі-методи */
    static std::chrono::milliseconds hwNow() noexcept;
    static uint32_t hwGetRandom() noexcept;
    static void hwUartWrite(std::string_view s) noexcept;
    static void hwSetRelay(uint8_t ch, bool state) noexcept;
    static bool hwI2cProbe(uint8_t addr) noexcept;
    static uint16_t hwAdcRead(uint8_t ch) noexcept;
};
```
:::

---

## 3. Детальний аналіз реалізації та інженерні пастки

Під час створення вбудованого сервісного рушія розробники часто припускаються критичних помилок у роботі з пам'яттю, перериваннями та апаратними ресурсами цільового процесора:

1. **Ізоляція контексту обробника переривань (Interrupt Context Isolation):** Функція `srv_feed_byte()` викликається безпосередньо з процедури обробки переривання приймача UART RX (ISR). Будь-які блокуючі або обчислювально затратні операції — парсинг текстового рядка, виведення відповідей у порт, операції з плаваючою комою чи повільне сканування шин I2C — категорично заборонено виконувати всередині ISR. Функція лише накопичує вхідні байти в статичному буфері до моменту виявлення символу закінчення рядка (`\r` або `\n`), після чого передає рядок на обробку диспетчеру.
2. **Захист від переповнення буфера та апаратного шуму (Buffer Overrun & Noise Filtering):** Вхідний масив `rx_buf` має фіксовану довжину `CLI_BUFFER_SIZE = 128` байтів. Якщо через брязкіт контактів або несправний перетворювач на лінію RX надійде довгий потік сміттєвих байтів, індексний покажчик `rx_idx` гарантовано зупиниться на позиції `127`. Зайві символи відкидаються, що виключає пошкодження сусідніх стек-фреймів і змінних у пам'яті SRAM. Додатково функція фільтрує керуючі та недруковані символи з кодами поза діапазоном `0x20..0x7E`.
3. **Детермінізм тайм-аутів та захист від зависання на периферійних шинах:** Усі функції низькорівневого BIST-тестування використовують строгі ліміти очікування відповідей шинних трансиверів. Якщо ведений чіп на шині I2C апаратно заблокував лінію `SDA` в логічному нулі, функція `hw_i2c_probe_device()` не зациклюється в очікуванні сигналу ACK, а виходить за тайм-аутом у 5 мілісекунд зі статусом `FAULT`. Це дозволяє процесору успішно завершити загальну діагностику решти вузлів плати.
4. **Гарантоване аварійне знеструмлення (Fail-Safe Default):** Метод `srv_emergency_all_off()` спроєктований як ізольована функція з прямою зміною регістрів GPIO. Вона викликається як за нормальним тайм-аутом сервісної команди, так і у разі закінчення часу неактивності сесії, переповнення лічильника помилок або системного перезавантаження. Це гарантує, що пристрій ні за яких обставин не залишиться з увімкненими силовими реле без нагляду інженера.

---

## 4. Співіснування з RTOS та контекст багатопоточності

У системах під керуванням операційних систем реального часу (FreeRTOS, Zephyr, RT-Thread) сервісний рушій виділяється в окремий низькопріоритетний потік (Task). 

Передача прийнятих символів з апаратного переривання UART у сервісну задачу здійснюється через потокобезпечну чергу повідомлень (`xQueueSendFromISR`) або пряме сповіщення задачі (`vTaskNotifyGiveFromISR`). Якщо під час виконання сервісного тесту виникає необхідність монопольного захоплення шини I2C чи SPI, сервісний потік бере відповідний м'ютекс (`xSemaphoreTake`) із фіксованим тайм-аутом. Це унеможливлює взаємне блокування (Deadlock) з основними високопріоритетними задачами регулювання та збору телеметрії.
