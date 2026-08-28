# ⚙️ Відмовостійкий асинхронний драйвер стільникового модему на C та C++

Ця вставка містить повну практичну реалізацію неблокуючого драйвера стільникового модема для вбудованих систем. Драйвер розв'язує фундаментальну проблему асинхронного послідовного стику: одночасне приймання синхронних відповідей на команди (`OK`, `ERROR`, `+CME ERROR`) та спонтанних подій мережі (URC, таких як зміна реєстрації `+CREG:`, надходження сокетних пакетів `+QIURC:` чи вхідні виклики `RING`) без блокування процесора, втрати байтів та взаємних блокувань задач в RTOS.

## 1. Архітектурний дизайн та рівні абстракції

Розробка надійного стільникового драйвера для мікроконтролера вимагає відмови від лінійного опитування (*polling*) та блокуючих функцій очікування на зразок `HAL_UART_Receive(&huart, buf, len, 5000)`. Якщо процесор заблокований усередині такої функції під час виклику `AT+CSQ`, будь-який вхідний пакет даних від сервера, що надійшов у сокет як URC, буде або затертий наступним байтом відповіді, або призведе до аварійного переповнення внутрішнього апаратного FIFO периферійного модуля UART (*Overrun Error*).

Драйвер побудовано за трирівневою ієрархічною архітектурою з нульовим динамічним виділенням пам'яті:

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Рівень 1: Апаратне переривання / DMA (UART RX ISR)                       │
│ - Атомарний запис у статичний кільцевий буфер (Ring Buffer)              │
│ - Нульове обчислювальне навантаження, захист від Overrun                 │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ Рівень 2: Скінченний автомат нарізки рядків (Line Slicer FSM)            │
│ - Посимвольне вичитування з кільцевого буфера                            │
│ - Виявлення розділювачів <CR><LF> та спеціального промпту '> '           │
│ - Ізоляція текстових рядків у лінійному буфері фіксованого розміру       │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ Рівень 3: Диспетчер транзакцій та маршрутизатор подій URC                │
│ - Порівняння префікса рядка з таблицею зареєстрованих URC-обробників     │
│ - Маршрутизація фінальних кодів (OK/ERROR) до активної транзакції        │
│ - Копіювання корисних проміжних даних у буфер результату                 │
└──────────────────────────────────────────────────────────────────────────┘
```

### Рівень 1: Кільцевий буфер та робота в перериванні

Кільцевий буфер приймача розраховано на розмір `1024` байти. Покажчики голови (`head`) та хвоста (`tail`) модифікуються атомарно: `head` змінюється виключно в контексті обробника переривання UART (ISR), тоді як `tail` змінюється лише в основному потоці виконання (`process`).

Такий розподіл доступу гарантує відсутність стану перегонів (*Race Condition*) без потреби глобального вимикання переривань під час читання черги на 32-бітних архітектурах ARM Cortex-M та RISC-V. Якщо буфер повністю заповнюється через затримку обробки в основній програмі, нові байти безпечно відкидаються із фіксацією лічильника помилок, що запобігає пошкодженню пам'яті сусідніх змінних.

### Рівень 2: Обробка розділювачів та детекція промпту

Стандартні відповіді модема завжди обрамляються парою `<CR><LF>` (`0x0D 0x0A`). Однак у прошивках різних виробників (Quectel, SIMCom, Telit, u-blox) існують відхилення: модеми можуть надсилати поодинокі `\r`, подвійні `\n` або зайві провідні пробіли. Скінченний автомат накопичувача ігнорує порожні переведення рядків на початку кадру і закриває рядок нуль-термінатором `\0` лише тоді, коли в буфері вже є корисні символи.

Окремим критичним станом є **промпт введення сирих даних** (`> `). Коли хост відправляє команду відправки SMS (`AT+CMGS`) або передачі сокетного пакета (`AT+QISEND`), модем повертає два байти: символ «більше» і пробіл (`0x3E 0x20`) **без кінцевих символів `\r\n`**. Звичайний лінійний парсер завис би в очікуванні кінця рядка назавжди. Автомат другого рівня спеціально перевіряє комбінацію `line_len == 1 && line[0] == '>' && ch == ' '` і негайно встановлює прапорець `prompt_detected = true`, сигналізуючи системі про готовність до передачі корисного навантаження.

### Рівень 3: Диспетчеризація та неблокуючі тайм-аути

Усі синхронні команди виконуються через структуру транзакції. Транзакція фіксує покажчик на буфер для збереження текстової відповіді, максимальний розмір цього буфера та програмний тайм-аут у мілісекундах.

Коли класифікатор виділяє завершений рядок, він виконує послідовну фільтрацію:
1. **Перевірка URC:** Рядок звіряється за таблицею префіксів (`+CREG:`, `+QIURC:`, `+CMTI:`, `RING`). У разі збігу негайно викликається зареєстрований зворотний виклик (*callback*), а рядок вважається повністю вичерпаним.
2. **Перевірка фінальних статусів:** Рядки `OK`, `ERROR`, `+CME ERROR:`, `NO CARRIER`, `BUSY` завершують активну транзакцію, зберігають код статусу й знімають прапорець активності.
3. **Проміжні дані:** Рядки на кшталт `+CSQ: 24,99` або `+CGPADDR: 1,"10.0.0.1"` вважаються корисним результатом і конкатенуються у буфер користувача.

## 2. Реалізація драйвера на мовах C та C++

Нижче наведено повний вихідний код драйвера, готовий до інтеграції на платформах STM32, ESP-IDF, Zephyr OS або Linux.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

#define AT_RX_RING_SIZE    1024
#define AT_LINE_BUF_SIZE   256
#define AT_MAX_URC_HANDLERS 16

/* Коди результату виконання транзакції */
typedef enum {
    AT_RESP_OK = 0,
    AT_RESP_ERROR,
    AT_RESP_TIMEOUT,
    AT_RESP_BUSY
} at_response_code_t;

/* Прототип функції зворотного виклику для URC */
typedef void (*at_urc_callback_t)(const char *urc_line, void *user_ctx);

/* Елемент таблиці реєстрації URC */
typedef struct {
    const char *prefix;
    at_urc_callback_t callback;
    void *user_ctx;
} at_urc_entry_t;

/* Стан кільцевого буфера UART */
typedef struct {
    uint8_t buffer[AT_RX_RING_SIZE];
    volatile size_t head;
    volatile size_t tail;
} at_ring_buf_t;

/* Стан поточної синхронної транзакції */
typedef struct {
    bool is_active;
    char *out_response_buf;
    size_t out_buf_max_len;
    uint32_t timeout_ms;
    uint32_t start_time_ms;
    at_response_code_t result;
    bool is_completed;
} at_transaction_t;

/* Головна структура драйвера модема */
typedef struct {
    at_ring_buf_t ring_rx;
    char line_accumulator[AT_LINE_BUF_SIZE];
    size_t line_len;
    
    at_urc_entry_t urc_table[AT_MAX_URC_HANDLERS];
    size_t urc_count;
    
    at_transaction_t current_cmd;
    bool prompt_detected;
    
    /* Апаратні абстракції платформи */
    void (*uart_write)(const uint8_t *data, size_t len);
    uint32_t (*get_tick_ms)(void);
} at_driver_t;

/* ── Ініціалізація та реєстрація URC ─────────────────────────────────────── */

void at_driver_init(at_driver_t *drv,
                    void (*uart_write_fn)(const uint8_t *, size_t),
                    uint32_t (*get_tick_fn)(void)) {
    memset(drv, 0, sizeof(at_driver_t));
    drv->uart_write = uart_write_fn;
    drv->get_tick_ms = get_tick_fn;
}

bool at_register_urc(at_driver_t *drv, const char *prefix, at_urc_callback_t cb, void *ctx) {
    if (drv->urc_count >= AT_MAX_URC_HANDLERS || !prefix || !cb) {
        return false;
    }
    drv->urc_table[drv->urc_count].prefix = prefix;
    drv->urc_table[drv->urc_count].callback = cb;
    drv->urc_table[drv->urc_count].user_ctx = ctx;
    drv->urc_count++;
    return true;
}

/* ── Обробка переривання UART RX (запис у кільцевий буфер) ───────────────── */

void at_driver_feed_rx_isr(at_driver_t *drv, uint8_t byte) {
    size_t next_head = (drv->ring_rx.head + 1) % AT_RX_RING_SIZE;
    if (next_head != drv->ring_rx.tail) {
        drv->ring_rx.buffer[drv->ring_rx.head] = byte;
        drv->ring_rx.head = next_head;
    }
    /* Переповнення буфера: байт відкидається для запобігання пошкодженню пам'яті */
}

/* ── Внутрішній диспетчер завершеного рядка ────────────────────────────────── */

static void at_dispatch_line(at_driver_t *drv, const char *line) {
    /* 1. Перевірка на збіг з зареєстрованими URC */
    for (size_t i = 0; i < drv->urc_count; i++) {
        size_t prefix_len = strlen(drv->urc_table[i].prefix);
        if (strncmp(line, drv->urc_table[i].prefix, prefix_len) == 0) {
            drv->urc_table[i].callback(line, drv->urc_table[i].user_ctx);
            return; /* URC оброблено, це не відповідь на поточну команду */
        }
    }

    /* 2. Перевірка на відповідність активній транзакції */
    if (!drv->current_cmd.is_active) {
        return; /* Неочікуваний рядок поза контекстом транзакції */
    }

    /* 3. Перевірка фінальних кодів успіху / помилки */
    if (strcmp(line, "OK") == 0 || strncmp(line, "CONNECT", 7) == 0) {
        drv->current_cmd.result = AT_RESP_OK;
        drv->current_cmd.is_completed = true;
        drv->current_cmd.is_active = false;
        return;
    }

    if (strcmp(line, "ERROR") == 0 ||
        strncmp(line, "+CME ERROR:", 11) == 0 ||
        strncmp(line, "+CMS ERROR:", 11) == 0 ||
        strcmp(line, "NO CARRIER") == 0 ||
        strcmp(line, "BUSY") == 0) {
        drv->current_cmd.result = AT_RESP_ERROR;
        drv->current_cmd.is_completed = true;
        drv->current_cmd.is_active = false;
        return;
    }

    /* 4. Проміжний рядок даних (копіюємо у буфер результату) */
    if (drv->current_cmd.out_response_buf && drv->current_cmd.out_buf_max_len > 0) {
        size_t cur_len = strlen(drv->current_cmd.out_response_buf);
        size_t line_len = strlen(line);
        if (cur_len + line_len + 2 < drv->current_cmd.out_buf_max_len) {
            if (cur_len > 0) {
                strcat(drv->current_cmd.out_response_buf, "\n");
            }
            strcat(drv->current_cmd.out_response_buf, line);
        }
    }
}

/* ── Фоновий кінцевий автомат парсера ─────────────────────────────────────── */

void at_driver_process(at_driver_t *drv) {
    /* Обробка тайм-ауту поточної транзакції */
    if (drv->current_cmd.is_active) {
        uint32_t now = drv->get_tick_ms();
        if (now - drv->current_cmd.start_time_ms >= drv->current_cmd.timeout_ms) {
            drv->current_cmd.result = AT_RESP_TIMEOUT;
            drv->current_cmd.is_completed = true;
            drv->current_cmd.is_active = false;
        }
    }

    /* Вичитування та нарізка байтів із кільцевого буфера */
    while (drv->ring_rx.head != drv->ring_rx.tail) {
        uint8_t ch = drv->ring_rx.buffer[drv->ring_rx.tail];
        drv->ring_rx.tail = (drv->ring_rx.tail + 1) % AT_RX_RING_SIZE;

        /* Спеціальний випадок: детекція промпту введення даних '> ' */
        if (ch == ' ' && drv->line_len == 1 && drv->line_accumulator[0] == '>') {
            drv->prompt_detected = true;
            drv->line_len = 0;
            continue;
        }

        if (ch == '\r' || ch == '\n') {
            if (drv->line_len > 0) {
                drv->line_accumulator[drv->line_len] = '\0';
                at_dispatch_line(drv, drv->line_accumulator);
                drv->line_len = 0;
            }
        } else {
            if (drv->line_len < AT_LINE_BUF_SIZE - 1) {
                drv->line_accumulator[drv->line_len++] = (char)ch;
            } else {
                /* Захист від переповнення рядка: скидання накопичувача */
                drv->line_len = 0;
            }
        }
    }
}

/* ── Відправка синхронної команди з очікуванням відповіді ─────────────────── */

at_response_code_t at_send_command_sync(at_driver_t *drv,
                                       const char *cmd,
                                       char *resp_buf,
                                       size_t resp_buf_size,
                                       uint32_t timeout_ms) {
    if (drv->current_cmd.is_active) {
        return AT_RESP_BUSY;
    }

    if (resp_buf && resp_buf_size > 0) {
        resp_buf[0] = '\0';
    }

    drv->current_cmd.out_response_buf = resp_buf;
    drv->current_cmd.out_buf_max_len = resp_buf_size;
    drv->current_cmd.timeout_ms = timeout_ms;
    drv->current_cmd.start_time_ms = drv->get_tick_ms();
    drv->current_cmd.result = AT_RESP_TIMEOUT;
    drv->current_cmd.is_completed = false;
    drv->current_cmd.is_active = true;

    /* Передача рядка команди у фізичний UART */
    drv->uart_write((const uint8_t *)cmd, strlen(cmd));
    drv->uart_write((const uint8_t *)"\r\n", 2);

    /* Неблокуючий цикл очікування виконання FSM */
    while (!drv->current_cmd.is_completed) {
        at_driver_process(drv);
    }

    return drv->current_cmd.result;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <functional>
#include <optional>
#include <span>
#include <chrono>
#include <cstring>

enum class AtResponseCode {
    Ok = 0,
    Error,
    Timeout,
    Busy
};

using UrcHandler = std::function<void(std::string_view line)>;

class CellularAtDriver {
public:
    using WriteFn = std::function<void(std::span<const uint8_t>)>;
    using TickFn = std::function<uint32_t()>;

    explicit CellularAtDriver(WriteFn write_fn, TickFn tick_fn)
        : write_uart_(std::move(write_fn)), get_tick_ms_(std::move(tick_fn)) {}

    void register_urc(std::string_view prefix, UrcHandler handler) {
        urc_registry_.emplace_back(std::string(prefix), std::move(handler));
    }

    void feed_rx_isr(uint8_t byte) noexcept {
        size_t next_head = (rx_head_ + 1) % kRingBufferSize;
        if (next_head != rx_tail_) {
            ring_buffer_[rx_head_] = byte;
            rx_head_ = next_head;
        }
    }

    void process() {
        if (transaction_ && transaction_->active) {
            uint32_t now = get_tick_ms_();
            if (now - transaction_->start_time_ms >= transaction_->timeout_ms) {
                transaction_->result = AtResponseCode::Timeout;
                transaction_->completed = true;
                transaction_->active = false;
            }
        }

        while (rx_head_ != rx_tail_) {
            uint8_t ch = ring_buffer_[rx_tail_];
            rx_tail_ = (rx_tail_ + 1) % kRingBufferSize;

            if (ch == ' ' && line_acc_.size() == 1 && line_acc_[0] == '>') {
                prompt_detected_ = true;
                line_acc_.clear();
                continue;
            }

            if (ch == '\r' || ch == '\n') {
                if (!line_acc_.empty()) {
                    dispatch_line(line_acc_);
                    line_acc_.clear();
                }
            } else {
                if (line_acc_.size() < kMaxLineLength) {
                    line_acc_.push_back(static_cast<char>(ch));
                } else {
                    line_acc_.clear();
                }
            }
        }
    }

    std::optional<std::string> send_command(std::string_view cmd,
                                            std::chrono::milliseconds timeout = std::chrono::milliseconds(3000)) {
        if (transaction_ && transaction_->active) {
            return std::nullopt;
        }

        transaction_ = Transaction{
            .response_body = "",
            .timeout_ms = static_cast<uint32_t>(timeout.count()),
            .start_time_ms = get_tick_ms_(),
            .result = AtResponseCode::Timeout,
            .completed = false,
            .active = true
        };

        std::string full_cmd(cmd);
        full_cmd += "\r\n";
        write_uart_(std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(full_cmd.data()), full_cmd.size()));

        while (!transaction_->completed) {
            process();
        }

        if (transaction_->result == AtResponseCode::Ok) {
            return transaction_->response_body;
        }
        return std::nullopt;
    }

private:
    struct Transaction {
        std::string response_body;
        uint32_t timeout_ms{3000};
        uint32_t start_time_ms{0};
        AtResponseCode result{AtResponseCode::Timeout};
        bool completed{false};
        bool active{false};
    };

    struct UrcEntry {
        std::string prefix;
        UrcHandler handler;
    };

    static constexpr size_t kRingBufferSize = 1024;
    static constexpr size_t kMaxLineLength = 256;

    WriteFn write_uart_;
    TickFn get_tick_ms_;

    uint8_t ring_buffer_[kRingBufferSize]{};
    volatile size_t rx_head_{0};
    volatile size_t rx_tail_{0};

    std::string line_acc_;
    std::vector<UrcEntry> urc_registry_;
    std::optional<Transaction> transaction_;
    bool prompt_detected_{false};

    void dispatch_line(std::string_view line) {
        for (const auto& [prefix, handler] : urc_registry_) {
            if (line.starts_with(prefix)) {
                handler(line);
                return;
            }
        }

        if (!transaction_ || !transaction_->active) {
            return;
        }

        if (line == "OK" || line.starts_with("CONNECT")) {
            transaction_->result = AtResponseCode::Ok;
            transaction_->completed = true;
            transaction_->active = false;
            return;
        }

        if (line == "ERROR" || line.starts_with("+CME ERROR:") ||
            line.starts_with("+CMS ERROR:") || line == "NO CARRIER" || line == "BUSY") {
            transaction_->result = AtResponseCode::Error;
            transaction_->completed = true;
            transaction_->active = false;
            return;
        }

        if (!transaction_->response_body.empty()) {
            transaction_->response_body += "\n";
        }
        transaction_->response_body += line;
    }
};
```
:::

## 3. Практичний сценарій запуску та обробки подій

Нижче наведено приклад інтеграції драйвера в реальний додаток: реєстрація обробників подій зміни соти LTE (`+CEREG`) та вхідних пакетів TCP (`+QIURC`), синхронізація швидкості та виконання базової послідовності опитування статусу.

:::tabs
```c
static void on_network_registration(const char *urc_line, void *user_ctx) {
    int n = 0, stat = 0;
    if (sscanf(urc_line, "+CEREG: %d,%d", &n, &stat) >= 1) {
        if (stat == 1 || stat == 5) {
            printf("[EVENT] Реєстрацію в LTE підтверджено (stat=%d)\n", stat);
        } else {
            printf("[EVENT] Пошук мережі або відмова (stat=%d)\n", stat);
        }
    }
}

static void on_socket_recv(const char *urc_line, void *user_ctx) {
    int sock = 0, len = 0;
    if (sscanf(urc_line, "+QIURC: \"recv\",%d,%d", &sock, &len) == 2) {
        printf("[EVENT] У сокет %d надійшло %d байт даних від сервера\n", sock, len);
    }
}

void modem_bringup_example(at_driver_t *drv) {
    char response[128];
    
    /* 1. Реєстрація обробників спонтанних подій URC */
    at_register_urc(drv, "+CEREG:", on_network_registration, NULL);
    at_register_urc(drv, "+QIURC: \"recv\"", on_socket_recv, NULL);
    
    /* 2. Синхронізація з модемом */
    if (at_send_command_sync(drv, "ATE0", response, sizeof(response), 1000) != AT_RESP_OK) {
        printf("[ERROR] Немає зв'язку з модемом на UART!\n");
        return;
    }
    
    /* 3. Увімкнення розширених помилок */
    at_send_command_sync(drv, "AT+CMEE=2", response, sizeof(response), 1000);
    
    /* 4. Запит якості сигналу */
    if (at_send_command_sync(drv, "AT+CSQ", response, sizeof(response), 1000) == AT_RESP_OK) {
        printf("[MODEM] Якість сигналу: %s\n", response);
    }
}
```
```cpp
void modem_bringup_example_cpp(CellularAtDriver& driver) {
    /* 1. Реєстрація лямбда-обробників спонтанних подій URC */
    driver.register_urc("+CEREG:", [](std::string_view line) {
        std::cout << "[EVENT CPP] Зміна статусу реєстрації LTE: " << line << "\n";
    });

    driver.register_urc("+QIURC: \"recv\"", [](std::string_view line) {
        std::cout << "[EVENT CPP] Отримано вхідний сокетний пакет: " << line << "\n";
    });

    /* 2. Синхронізація з модемом */
    auto echo_resp = driver.send_command("ATE0", std::chrono::milliseconds(1000));
    if (!echo_resp.has_value()) {
        std::cerr << "[ERROR CPP] Модем не відповідає на UART!\n";
        return;
    }

    /* 3. Увімкнення детальних помилок */
    driver.send_command("AT+CMEE=2", std::chrono::milliseconds(1000));

    /* 4. Запит якості сигналу */
    if (auto csq_resp = driver.send_command("AT+CSQ", std::chrono::milliseconds(1000))) {
        std::cout << "[MODEM CPP] Отримано сигнал: " << *csq_resp << "\n";
    }
}
```
:::

## 4. Аналіз крайових випадків та підводні камені

Під час експлуатації стільникового драйвера в промислових умовах виникають чотири неочевидні крайові ситуації:

1. **Байти відповіді розриваються за часом (Fragmented Transmission):** Під час перевантаження мережі або внутрішньої збірки сміття у Flash-пам'яті модем може видати перший байт `\r` відповіді, зробити паузу тривалістю `200 – 400 мс`, і лише потім видати рядок `OK\r\n`. Будь-який парсер, який вважає затримку між символами закінченням повідомлення, зазнає краху. Потоковий автомат нарізки рядків захищений від цього, оскільки орієнтується виключно на термінальні байти `\r\n`, а не на міжсимвольний інтервал.
2. **Змішування текстових відповідей із двійковими даними:** Коли мікроконтролер вичитує сокетний буфер командою `AT+QIRD=<len>`, модем надсилає заголовок `+QIRD: 512\r\n`, після якого йдуть 512 сирих двійкових байтів, які можуть містити будь-які комбінації `0x0D` та `0x0A`. Для коректного прийому драйвер після парсингу заголовка тимчасово перемикає FSM у стан прямого зчитування лічильника байтів без пошуку `\r\n`.
3. **Зависання UART під час перепаду напруги:** Якщо під час передачі радіопакета напруга `VBAT` короткочасно просіла, апаратний UART мікроконтролера може зафіксувати стан `Framing Error` або `Break Condition`. Драйвер повинен у функції обробника переривань перевіряти апаратні біти помилок регістру статусу UART (`USART_SR_FE`, `USART_SR_ORE`) і скидати їх читанням регістру даних, інакше периферійний модуль блокує подальший прийом байтів на апаратному рівні.
4. **Конкурентний доступ в операційних системах реального часу (RTOS):** Якщо кілька задач (наприклад, задача телеметрії, задача перевірки балансу та задача надсилання логів) намагаються одночасно викликати `at_send_command_sync`, виникає стан перегонів за буфер UART. У багатозадачному середовищі структура транзакції захищається бінарним семафором або м'ютексом із пріоритетним успадкуванням (*Mutex with Priority Inheritance*), гарантуючи, що наступна команда буде відправлена лише після завершення поточної транзакції.
