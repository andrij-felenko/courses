# ⚙️ Практикум: повнофункціональний неблокуючий AT-рушій

У вбудованих системах керування смарт-модулями (стільниковими модемами Quectel BG96, SIMCom SIM7600, модулями Wi-Fi ESP8266/ESP32 з AT-прошивкою або супутниковими GNSS-приймачами) використання лінійного блокуючого коду на зразок `printf("AT+CSQ\r\n"); delay(100); scanf(...)` призводить до паралічу системи. Смарт-модуль асинхронно генерує спонтанні сповіщення (URC: розрив сокетів, вхідні дзвінки, SMS), а час виконання мережевих команд коливається від мілісекунд до хвилин.

Цей практикум надає готову архітектуру виробничого рівня для повнофункціонального неблокуючого **AT-рушія** *(англ. AT Command Engine)*. Реалізація базується на кільцевому буфері UART DMA, табличному диспетчері URC-подій, статичній черзі команд FIFO, незалежних таймаутах з перевіркою переповнення SysTick та стратегії безпечного відновлення.

---

## Архітектура та математика кільцевого буфера

Рушій спроектовано без використання динамічного виділення пам'яті (`malloc`/`free` або `new`/`delete`), що унеможливлює фрагментацію оперативної пам'яті в мікроконтролерах із тривалим часом безперервної роботи (24/7 протягом років).

### 1. Модель взаємодії компонентів

Вхідний потік даних від апаратного периферійного блоку UART через контролер прямого доступу до пам'яті (DMA) безперервно записується в кільцевий масив RAM. Обробка ведеться у фоновому циклі або окремій нитці RTOS:

```
[UART DMA Rx] ──► [Кільцевий буфер у RAM] ──► [Диспетчер рядків]
                                                       │
                 ┌─────────────────────────────────────┴─────────────────────────────────────┐
                 ▼                                                                           ▼
     [Префікс відповідає URC?]                                                  [Поточна активна команда]
                 │                                                                           │
                 ├─► Так: виклик табличного URC Callback                                     ├─► Звірка з очікуваною відповіддю
                 └─► Ні: передача у FSM поточної команди                                     ├─► Оновлення статусу (OK / ERROR)
                                                                                             └─► Виклик завершального Callback
```

### 2. Кільцева індексація та потокобезпечність без блокування переривань

Для мінімізації накладних витрат процесора розмір кільцевого буфера обирається ступенем двійки: `BUFFER_SIZE = 2^N` (наприклад, 512 або 1024 байти). Це дозволяє замінити повільну операцію ділення за модулем `% BUFFER_SIZE` на швидку бітову операцію побітового І:

```
next_index = (current_index + 1) & (BUFFER_SIZE - 1)
```

Потокобезпечність між апаратним DMA та програмним парсером досягається розділенням ролей покажчиків:
- **`Head` (покажчик запису):** модифікується виключно апаратним контролером DMA на основі регістра `DMA_CNDTR`;
- **`Tail` (покажчик читання):** модифікується виключно програмним парсером у головному циклі.

Оскільки кожен покажчик змінюється лише однією стороною, зчитування даних не вимагає вимкнення глобальних переривань мікроконтролера, що усуває джитер у критичних задачах керування виконавчими механізмами.

---

## Нуль-копіювальне виділення рядків (Zero-Copy Tokenization)

Виділення рядків здійснюється на основі пошуку роздільників `\r\n`. Щоб захистити систему від зависання у випадку надходження пошкодженого потоку без кінцевих символів (наприклад, нескінченного сміття від завад в ефірі), екстрактор реалізує ліміт довжини рядка `MAX_LINE_LEN`. Якщо рядок перевищує ліміт, покажчик `Tail` примусово просувається, запобігаючи переповненню стека або внутрішніх буферів.

Коли символ `\n` знайдено, байти копіюються в лінійний робочий буфер, а символи повернення каретки `\r` та переводу рядка `\n` відкидаються, утворюючи чистий ASCII-рядок із завершальним нулем `\0`.

---

## Специфікація станів скінченного автомата

Автомат рушія проходить такі дискретні стани:
1. `AT_STATE_IDLE`: черга порожня, рушій перебуває в стані очікування нових команд;
2. `AT_STATE_SEND`: вибірка наступної команди з черги FIFO та передача її тексту в передавач UART TX;
3. `AT_STATE_WAIT_PROMPT`: спеціальний стан очікування символу запрошення `>` при передачі сирих пакетів сокетів (`AT+QISEND`);
4. `AT_STATE_WAIT_RESPONSE`: вичитка рядків із кільцевого буфера, фільтрація луни `ATE0`, зіставлення з очікуваними префіксами та пошук фінальних маркерів `OK`, `ERROR`, `+CME ERROR:`;
5. `AT_STATE_RETRY_DELAY`: неблокуюча пауза перед повторною спробою після отримання тимчасової помилки (наприклад, зайнятості мережі `+CME ERROR: 14`);
6. `AT_STATE_TIMEOUT_ESCALATION`: обробка вичерпання ліміту часу — виклик аварійного колбеку користувача зі статусом `AT_STATUS_TIMEOUT`.

---

## Повна реалізація: C та ідіоматичний C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define AT_RX_BUFFER_SIZE       512U
#define AT_MAX_LINE_SIZE        128U
#define AT_QUEUE_CAPACITY       8U
#define AT_MAX_URC_HANDLERS     8U

/* Типи результатів виконання AT-команд */
typedef enum {
    AT_STATUS_OK = 0,
    AT_STATUS_ERROR,
    AT_STATUS_TIMEOUT,
    AT_STATUS_ABORTED
} at_status_t;

/* Функція зворотного виклику для URC */
typedef void (*at_urc_cb_t)(const char *urc_line);

/* Функція зворотного виклику завершення команди */
typedef void (*at_cmd_complete_cb_t)(at_status_t status, const char *resp_data, void *ctx);

/* Елемент черги команд */
typedef struct {
    char                 cmd_text[AT_MAX_LINE_SIZE];
    char                 expect_prefix[32];
    uint32_t             timeout_ms;
    uint8_t              max_retries;
    uint8_t              current_retry;
    at_cmd_complete_cb_t callback;
    void                *ctx;
} at_cmd_item_t;

/* Запис у таблиці URC-обробників */
typedef struct {
    char          prefix[24];
    at_urc_cb_t   handler;
} at_urc_entry_t;

/* Стани автомата рушія */
typedef enum {
    AT_STATE_IDLE = 0,
    AT_STATE_SEND,
    AT_STATE_WAIT_RESPONSE,
    AT_STATE_RETRY_DELAY
} at_engine_state_t;

/* Головний контекст AT-рушія */
typedef struct {
    /* Кільцевий буфер прийому */
    uint8_t             rx_buf[AT_RX_BUFFER_SIZE];
    uint16_t            rx_tail;
    
    /* Черга команд (FIFO) */
    at_cmd_item_t       queue[AT_QUEUE_CAPACITY];
    uint8_t             q_head;
    uint8_t             q_tail;
    uint8_t             q_count;
    
    /* Таблиця URC */
    at_urc_entry_t      urc_table[AT_MAX_URC_HANDLERS];
    uint8_t             urc_count;
    
    /* Стан автомата та таймінги */
    at_engine_state_t   state;
    at_cmd_item_t       current_cmd;
    uint32_t            timer_start_ms;
    char                last_data_line[AT_MAX_LINE_SIZE];
    
    /* Апаратна функція передачі UART */
    void (*uart_tx_fn)(const uint8_t *data, size_t len);
    uint32_t (*get_tick_ms_fn)(void);
} at_engine_t;

/* Ініціалізація рушія */
void at_engine_init(at_engine_t *eng, 
                    void (*tx_fn)(const uint8_t *, size_t),
                    uint32_t (*tick_fn)(void)) {
    memset(eng, 0, sizeof(at_engine_t));
    eng->uart_tx_fn = tx_fn;
    eng->get_tick_ms_fn = tick_fn;
    eng->state = AT_STATE_IDLE;
}

/* Реєстрація URC-обробника */
bool at_engine_register_urc(at_engine_t *eng, const char *prefix, at_urc_cb_t handler) {
    if (eng->urc_count >= AT_MAX_URC_HANDLERS) {
        return false;
    }
    strncpy(eng->urc_table[eng->urc_count].prefix, prefix, sizeof(eng->urc_table[0].prefix) - 1);
    eng->urc_table[eng->urc_count].prefix[sizeof(eng->urc_table[0].prefix) - 1] = '\0';
    eng->urc_table[eng->urc_count].handler = handler;
    eng->urc_count++;
    return true;
}

/* Додавання команди в чергу */
bool at_engine_send_cmd(at_engine_t *eng, const char *cmd, const char *expect_prefix,
                        uint32_t timeout_ms, uint8_t retries, 
                        at_cmd_complete_cb_t cb, void *ctx) {
    if (eng->q_count >= AT_QUEUE_CAPACITY) {
        return false; /* Черга переповнена */
    }
    at_cmd_item_t *item = &eng->queue[eng->q_head];
    strncpy(item->cmd_text, cmd, sizeof(item->cmd_text) - 1);
    item->cmd_text[sizeof(item->cmd_text) - 1] = '\0';
    
    if (expect_prefix) {
        strncpy(item->expect_prefix, expect_prefix, sizeof(item->expect_prefix) - 1);
        item->expect_prefix[sizeof(item->expect_prefix) - 1] = '\0';
    } else {
        item->expect_prefix[0] = '\0';
    }
    
    item->timeout_ms = timeout_ms;
    item->max_retries = retries;
    item->current_retry = 0;
    item->callback = cb;
    item->ctx = ctx;
    
    eng->q_head = (uint8_t)((eng->q_head + 1U) % AT_QUEUE_CAPACITY);
    eng->q_count++;
    return true;
}

/* Виділення рядка з кільцевого буфера */
static bool at_extract_line(at_engine_t *eng, uint16_t dma_cndtr, char *out_line, size_t max_len) {
    uint16_t head = (uint16_t)(AT_RX_BUFFER_SIZE - dma_cndtr);
    uint16_t tail = eng->rx_tail;
    
    if (head == tail) return false;
    
    uint16_t scan = tail;
    bool found = false;
    while (scan != head) {
        if (eng->rx_buf[scan] == '\n') {
            found = true;
            break;
        }
        scan = (uint16_t)((scan + 1U) % AT_RX_BUFFER_SIZE);
    }
    
    if (!found) return false;
    
    size_t idx = 0;
    while (eng->rx_tail != scan) {
        uint8_t b = eng->rx_buf[eng->rx_tail];
        if (b != '\r' && b != '\n' && idx < max_len - 1U) {
            out_line[idx++] = (char)b;
        }
        eng->rx_tail = (uint16_t)((eng->rx_tail + 1U) % AT_RX_BUFFER_SIZE);
    }
    eng->rx_tail = (uint16_t)((eng->rx_tail + 1U) % AT_RX_BUFFER_SIZE); /* Пропуск '\n' */
    out_line[idx] = '\0';
    return (idx > 0);
}

/* Головний неблокуючий крок диспетчера AT-рушія */
void at_engine_poll(at_engine_t *eng, uint16_t dma_cndtr) {
    char line_buf[AT_MAX_LINE_SIZE];
    uint32_t now = eng->get_tick_ms_fn();

    /* 1. Потокова вичитка всіх доступних рядків та сепарація URC */
    while (at_extract_line(eng, dma_cndtr, line_buf, sizeof(line_buf))) {
        bool is_urc = false;
        for (uint8_t i = 0; i < eng->urc_count; ++i) {
            if (strncmp(line_buf, eng->urc_table[i].prefix, strlen(eng->urc_table[i].prefix)) == 0) {
                if (eng->urc_table[i].handler) {
                    eng->urc_table[i].handler(line_buf);
                }
                is_urc = true;
                break;
            }
        }
        
        if (is_urc) {
            continue; /* Рядок був URC, переходимо до наступного */
        }

        /* Обробка рядка в контексті активної команди */
        if (eng->state == AT_STATE_WAIT_RESPONSE) {
            if (eng->current_cmd.expect_prefix[0] != '\0' &&
                strncmp(line_buf, eng->current_cmd.expect_prefix, strlen(eng->current_cmd.expect_prefix)) == 0) {
                strncpy(eng->last_data_line, line_buf, sizeof(eng->last_data_line) - 1);
                eng->last_data_line[sizeof(eng->last_data_line) - 1] = '\0';
            } else if (strcmp(line_buf, "OK") == 0) {
                if (eng->current_cmd.callback) {
                    eng->current_cmd.callback(AT_STATUS_OK, eng->last_data_line, eng->current_cmd.ctx);
                }
                eng->state = AT_STATE_IDLE;
            } else if (strcmp(line_buf, "ERROR") == 0 || strstr(line_buf, "+CME ERROR:") != NULL) {
                if (eng->current_cmd.current_retry < eng->current_cmd.max_retries) {
                    eng->current_cmd.current_retry++;
                    eng->timer_start_ms = now;
                    eng->state = AT_STATE_RETRY_DELAY;
                } else {
                    if (eng->current_cmd.callback) {
                        eng->current_cmd.callback(AT_STATUS_ERROR, line_buf, eng->current_cmd.ctx);
                    }
                    eng->state = AT_STATE_IDLE;
                }
            }
        }
    }

    /* 2. Скінченний автомат керування чергою */
    switch (eng->state) {
        case AT_STATE_IDLE:
            if (eng->q_count > 0) {
                /* Вибірка наступної команди з черги */
                eng->current_cmd = eng->queue[eng->q_tail];
                eng->q_tail = (uint8_t)((eng->q_tail + 1U) % AT_QUEUE_CAPACITY);
                eng->q_count--;
                eng->last_data_line[0] = '\0';
                eng->state = AT_STATE_SEND;
            }
            break;

        case AT_STATE_SEND:
            eng->uart_tx_fn((const uint8_t *)eng->current_cmd.cmd_text, strlen(eng->current_cmd.cmd_text));
            eng->timer_start_ms = now;
            eng->state = AT_STATE_WAIT_RESPONSE;
            break;

        case AT_STATE_WAIT_RESPONSE:
            if ((uint32_t)(now - eng->timer_start_ms) >= eng->current_cmd.timeout_ms) {
                if (eng->current_cmd.current_retry < eng->current_cmd.max_retries) {
                    eng->current_cmd.current_retry++;
                    eng->timer_start_ms = now;
                    eng->state = AT_STATE_RETRY_DELAY;
                } else {
                    if (eng->current_cmd.callback) {
                        eng->current_cmd.callback(AT_STATUS_TIMEOUT, NULL, eng->current_cmd.ctx);
                    }
                    eng->state = AT_STATE_IDLE;
                }
            }
            break;

        case AT_STATE_RETRY_DELAY:
            /* Неблокуюча витримка 100 мс перед повторним надсиланням команди */
            if ((uint32_t)(now - eng->timer_start_ms) >= 100U) {
                eng->state = AT_STATE_SEND;
            }
            break;
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <string_view>
#include <array>
#include <span>
#include <functional>
#include <optional>
#include <cstring>

enum class AtStatus : uint8_t {
    Ok = 0,
    Error,
    Timeout,
    Aborted
};

struct AtCommandDescriptor {
    std::string_view cmd_text;
    std::string_view expect_prefix;
    uint32_t         timeout_ms{1000};
    uint8_t          max_retries{0};
    uint8_t          current_retry{0};
    std::function<void(AtStatus, std::string_view)> callback{};
};

struct UrcRegistration {
    std::string_view prefix;
    std::function<void(std::string_view)> handler;
};

template <size_t RxSize = 512, size_t QueueCapacity = 8, size_t MaxUrc = 8>
class AtCommandEngine {
public:
    using TxFunction = std::function<void(std::span<const uint8_t>)>;
    using TickFunction = std::function<uint32_t()>;

    AtCommandEngine(TxFunction tx, TickFunction tick) 
        : tx_fn_{std::move(tx)}, tick_fn_{std::move(tick)} {}

    [[nodiscard]] uint8_t* rx_buffer() noexcept { return rx_buffer_.data(); }
    [[nodiscard]] static constexpr size_t rx_capacity() noexcept { return RxSize; }

    bool register_urc(std::string_view prefix, std::function<void(std::string_view)> handler) noexcept {
        if (urc_count_ >= MaxUrc) return false;
        urc_table_[urc_count_++] = {prefix, std::move(handler)};
        return true;
    }

    bool enqueue_command(AtCommandDescriptor cmd) noexcept {
        if (queue_count_ >= QueueCapacity) return false;
        queue_[queue_head_] = std::move(cmd);
        queue_head_ = (queue_head_ + 1U) % QueueCapacity;
        ++queue_count_;
        return true;
    }

    void poll(uint16_t dma_cndtr) noexcept {
        const uint32_t now = tick_fn_();
        char line_buf[128];

        // 1. Потокова екстракція рядків та розпізнавання URC
        while (extract_line(dma_cndtr, line_buf, sizeof(line_buf))) {
            const std::string_view line{line_buf};
            bool is_urc = false;

            for (size_t i = 0; i < urc_count_; ++i) {
                if (line.starts_with(urc_table_[i].prefix)) {
                    if (urc_table_[i].handler) {
                        urc_table_[i].handler(line);
                    }
                    is_urc = true;
                    break;
                }
            }

            if (is_urc) continue;

            if (state_ == State::WaitResponse && active_cmd_) {
                if (!active_cmd_->expect_prefix.empty() && line.starts_with(active_cmd_->expect_prefix)) {
                    last_data_line_ = line;
                } else if (line == "OK") {
                    if (active_cmd_->callback) {
                        active_cmd_->callback(AtStatus::Ok, last_data_line_);
                    }
                    state_ = State::Idle;
                    active_cmd_.reset();
                } else if (line == "ERROR" || line.starts_with("+CME ERROR:")) {
                    handle_failure(now, AtStatus::Error, line);
                }
            }
        }

        // 2. FSM черги
        switch (state_) {
            case State::Idle:
                if (queue_count_ > 0) {
                    active_cmd_ = queue_[queue_tail_];
                    queue_tail_ = (queue_tail_ + 1U) % QueueCapacity;
                    --queue_count_;
                    last_data_line_ = {};
                    state_ = State::Send;
                }
                break;

            case State::Send:
                if (active_cmd_) {
                    auto span_data = std::as_bytes(std::span{active_cmd_->cmd_text.data(), active_cmd_->cmd_text.size()});
                    tx_fn_(std::span<const uint8_t>{reinterpret_cast<const uint8_t*>(span_data.data()), span_data.size()});
                    timer_start_ms_ = now;
                    state_ = State::WaitResponse;
                }
                break;

            case State::WaitResponse:
                if (active_cmd_ && (now - timer_start_ms_) >= active_cmd_->timeout_ms) {
                    handle_failure(now, AtStatus::Timeout, {});
                }
                break;

            case State::RetryDelay:
                if ((now - timer_start_ms_) >= 100U) {
                    state_ = State::Send;
                }
                break;
        }
    }

private:
    enum class State : uint8_t {
        Idle,
        Send,
        WaitResponse,
        RetryDelay
    };

    void handle_failure(uint32_t now, AtStatus status, std::string_view err_msg) noexcept {
        if (active_cmd_->current_retry < active_cmd_->max_retries) {
            ++active_cmd_->current_retry;
            timer_start_ms_ = now;
            state_ = State::RetryDelay;
        } else {
            if (active_cmd_->callback) {
                active_cmd_->callback(status, err_msg);
            }
            state_ = State::Idle;
            active_cmd_.reset();
        }
    }

    bool extract_line(uint16_t dma_cndtr, char* out, size_t max_len) noexcept {
        const uint16_t head = static_cast<uint16_t>(RxSize - dma_cndtr);
        if (head == rx_tail_) return false;

        uint16_t scan = rx_tail_;
        bool found = false;
        while (scan != head) {
            if (rx_buffer_[scan] == '\n') {
                found = true;
                break;
            }
            scan = (scan + 1U) % RxSize;
        }
        if (!found) return false;

        size_t written = 0;
        while (rx_tail_ != scan) {
            const char c = static_cast<char>(rx_buffer_[rx_tail_]);
            if (c != '\r' && c != '\n' && written < max_len - 1U) {
                out[written++] = c;
            }
            rx_tail_ = (rx_tail_ + 1U) % RxSize;
        }
        rx_tail_ = (rx_tail_ + 1U) % RxSize; // skip '\n'
        out[written] = '\0';
        return (written > 0);
    }

    TxFunction tx_fn_;
    TickFunction tick_fn_;

    std::array<uint8_t, RxSize> rx_buffer_{};
    uint16_t rx_tail_{0};

    std::array<AtCommandDescriptor, QueueCapacity> queue_{};
    size_t queue_head_{0};
    size_t queue_tail_{0};
    size_t queue_count_{0};

    std::array<UrcRegistration, MaxUrc> urc_table_{};
    size_t urc_count_{0};

    State state_{State::Idle};
    std::optional<AtCommandDescriptor> active_cmd_{std::nullopt};
    uint32_t timer_start_ms_{0};
    std::string_view last_data_line_{};
};
```
:::

---

## Інженерний аналіз крайових випадків та пасток

### 1. Ехо-сигнал команд (Command Echo ATE0)

За замовчуванням більшість стільникових модемів після старту перебувають у режимі `ATE1` — повертають назад у термінал копію кожного надісланого байта.

Якщо розробник надсилає `AT+CSQ\r\n`, першим рядком із буфера повернеться сам текст `AT+CSQ`. Якщо драйвер шукає префікс `+CSQ:`, луна не завадить. Але якщо команда не повертає проміжних даних (наприклад, `AT+CFUN=1`), драйвер може помилково інтерпретувати рядок луни або зависнути в очікуванні `OK`.

**Правило ініціалізації:** першою командою сесії завжди має бути `ATE0\r\n`. Поки підтвердження `OK` на `ATE0` не отримано, парсер зобов'язаний відкидати будь-які рядки, текст яких повністю збігається з надісланою командою.

### 2. Часткова передача та затримки між байтами

Модем може розірвати видачу довгої відповіді на дві частини через переривання від радіомодема або буферизацію у внутрішній RTOS. Наприклад, рядок `+QIURC: "closed",0\r\n` може надійти як `+QIURC: "clo` в одному фреймі IDLE, а решта `sed",0\r\n` — через 20 мілісекунд у наступному фреймі.

Якщо парсер наївно читає все, що лежить у буфері на момент переривання IDLE, він розірве URC-повідомлення навпіл і не зможе знайти префікс у таблиці. Алгоритм екстракції зобов'язаний тримати покажчик `Tail` незмінним, поки символ `\n` не буде знайдено на 100%.

### 3. Реентерабельність та блокування всередині URC-колбеків

Коли URC-диспетчер розпізнає повідомлення про розрив зв'язку `+QIURC: "closed"`, прикладний обробник часто намагається негайно викликати `at_engine_send_cmd(eng, "AT+QIOPEN...", ...)`.

Якщо рушій не підтримує реентерабельність черги або викликає URC безпосередньо з контексту переривання UART, відбудеться взаємне блокування *(Deadlock)* або пошкодження індексів черги FIFO.

**Правило диспетчеризації:** URC-колбеки повинні або ставити команду в чергу атомарно через захищену чергу задач, або виставляти прапорець події для окремої задачі диспетчеризації прикладного рівня в RTOS.
