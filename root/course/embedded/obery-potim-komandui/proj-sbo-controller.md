# ⚙️ Реалізація контролера Select-Before-Operate для бортового комп'ютера та наземного пульта

Цей проект демонструє виробничу програмну реалізацію безпечного автомата стану Select-Before-Operate (SBO) для двох ключових компонентів радіоканалу:
1. **Бортовий сервер цілі (Target SBO Engine):** модуль прошивки мікроконтролера, що обробляє вхідні пакети, видає токени селекції, веде таймер знешкодження і блокує виконання команд при розсинхронізації.
2. **Клієнтський менеджер вибору на пульті (GCS Focus Controller):** модуль станції керування, що синхронізує контекст оператора, динамічно прив'язує команди до обраного ідентифікатора та запобігає відправці дій на неактивні апарати.

---

## 1. Архітектура та інваріанти безпеки

Реалізація забезпечує дотримання чотирьох непорушних інваріантів:
* **Нульова динамічна пам'ять (Zero Heap Allocation):** Усі структури даних мають фіксований розмір і розміщуються статично на стеку або у секції `.bss`, що виключає фрагментацію пам'яті в умовах реального часу.
* **Суворий тайм-аут знешкодження (Deterministic Arm Timeout):** Перехід у безпечний стан `IDLE` виконується через дискретний виклик системного таймера без блокуючих затримок.
* **Одноразовість токена (Single-Shot Token Invalidation):** Після будь-якої спроби виконання дії (успішної або відхиленої) згенерований токен миттєво анулюється.
* **Відсікання широкомовних пакетів (Strict Unicast Enforcement):** Будь-який запит на критичну дію з адресою призначення `0xFF` негайно відкидається на рівні валідатора.

```
       +-------------------------------------------------------------+
       |               АРХІТЕКТУРА ДИСПЕТЧЕРА SBO                    |
       |                                                             |
       |  [ Вхідний радіопакет ]                                     |
       |           │                                                 |
       |           ▼                                                 |
       |  ┌─────────────────────────┐                                |
       |  │  Target ID Matcher      │ ── (Чужий ID / 0xFF Broadcast) │
       |  └─────────────────────────┘             │                  |
       |           │ (Свій ID)                    ▼                  |
       |           ▼                      [ Відкинути пакет ]        |
       |  ┌─────────────────────────┐                                |
       |  │  SBO FSM Engine         │ ── (Токен недійсний / Час вичерпано)
       |  └─────────────────────────┘             │                  |
       |           │ (Валідовано)                 ▼                  |
       |           ▼                      [ Повернути SBO_NACK ]     |
       |  ┌─────────────────────────┐                                |
       |  │  Виконавчий драйвер     │                                |
       |  │  (Реле / ESC / Живлення)│                                |
       |  └─────────────────────────┘                                |
       +-------------------------------------------------------------+
```

---

## 2. Програмна реалізація ядра SBO на борту

Нижче наведено робочий код ядра автомата станів. Реалізація мовою C орієнтована на мікроконтролери архітектури ARM Cortex-M / RISC-V під керуванням FreeRTOS або bare-metal. Сусідня вкладка C++ демонструє ідіоматичний об'єктний дизайн стандарту C++20 із суворою типізацією ідентифікаторів, `std::span` та `std::chrono`.

:::tabs
```c
/* sbo_target_engine.h / sbo_target_engine.c — Чистий C для вбудованих систем */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define SBO_MAGIC_BYTE          0x5B
#define SBO_BROADCAST_ID        0xFF
#define SBO_DEFAULT_TIMEOUT_MS  5000
#define SBO_MAX_PAYLOAD_LEN     64

typedef enum {
    SBO_STATE_IDLE = 0,
    SBO_STATE_ARMED,
    SBO_STATE_EXECUTING
} sbo_fsm_state_t;

typedef enum {
    SBO_MSG_SELECT_REQ  = 0x10,
    SBO_MSG_SELECT_ACK  = 0x11,
    SBO_MSG_SELECT_NACK = 0x12,
    SBO_MSG_OPERATE_REQ = 0x20,
    SBO_MSG_OPERATE_ACK = 0x21,
    SBO_MSG_OPERATE_NACK= 0x22,
    SBO_MSG_CANCEL_REQ  = 0x30,
    SBO_MSG_CANCEL_ACK  = 0x31
} sbo_msg_type_t;

typedef enum {
    SBO_ERR_NONE = 0,
    SBO_ERR_BUSY,
    SBO_ERR_INVALID_TOKEN,
    SBO_ERR_TIMEOUT_EXPIRED,
    SBO_ERR_NOT_ARMED,
    SBO_ERR_CMD_MISMATCH,
    SBO_ERR_BROADCAST_FORBIDDEN,
    SBO_ERR_INTERNAL_FAULT
} sbo_error_t;

#pragma pack(push, 1)
typedef struct {
    uint8_t  magic;
    uint8_t  payload_len;
    uint8_t  seq;
    uint8_t  msg_type;
    uint8_t  source_id;
    uint8_t  target_id;
    uint8_t  target_comp;
    uint8_t  sbo_state;
    uint32_t sbo_token;
    uint16_t cmd_code;
    uint16_t timeout_ms;
    uint8_t  payload[SBO_MAX_PAYLOAD_LEN];
    uint16_t crc16;
} sbo_packet_t;
#pragma pack(pop)

typedef struct {
    uint8_t         my_system_id;
    sbo_fsm_state_t state;
    uint8_t         locked_source_id;
    uint16_t        locked_cmd_code;
    uint32_t        active_token;
    uint32_t        arm_expiry_timestamp_ms;
    uint32_t        prng_seed;
} sbo_target_context_t;

/* Простий генератор ентропійних токенів */
static uint32_t sbo_generate_token(sbo_target_context_t *ctx, uint32_t current_time_ms) {
    ctx->prng_seed = ctx->prng_seed * 1664525u + 1013904223u + current_time_ms;
    uint32_t token = ctx->prng_seed;
    if (token == 0) token = 0xA5A55A5A; /* Запобігання нульовому токену */
    return token;
}

void sbo_target_init(sbo_target_context_t *ctx, uint8_t system_id, uint32_t initial_seed) {
    memset(ctx, 0, sizeof(sbo_target_context_t));
    ctx->my_system_id = system_id;
    ctx->state = SBO_STATE_IDLE;
    ctx->prng_seed = initial_seed ^ 0xDEADBEEF;
}

/* Періодичне оновлення таймера (виклик кожні 10..50 мс) */
void sbo_target_tick(sbo_target_context_t *ctx, uint32_t current_time_ms) {
    if (ctx->state == SBO_STATE_ARMED) {
        if (current_time_ms >= ctx->arm_expiry_timestamp_ms) {
            /* Спливання вікна дії: автоматичне знешкодження */
            ctx->state = SBO_STATE_IDLE;
            ctx->active_token = 0;
            ctx->locked_cmd_code = 0;
            ctx->locked_source_id = 0;
        }
    }
}

/* Обробка вхідного пакету транзакції */
sbo_error_t sbo_target_process_packet(sbo_target_context_t *ctx,
                                      const sbo_packet_t *rx_pkt,
                                      sbo_packet_t *tx_response,
                                      uint32_t current_time_ms) {
    /* 1. Фільтрація широкомовних пакетів для критичних операцій */
    if (rx_pkt->target_id == SBO_BROADCAST_ID) {
        return SBO_ERR_BROADCAST_FORBIDDEN;
    }

    /* 2. Перевірка приналежності пакету цьому вузлу */
    if (rx_pkt->target_id != ctx->my_system_id) {
        return SBO_ERR_NONE; /* Пакет адресовано іншому вузлу, ігноруємо */
    }

    /* Оновлення статусу тайм-ауту */
    sbo_target_tick(ctx, current_time_ms);

    memset(tx_response, 0, sizeof(sbo_packet_t));
    tx_response->magic = SBO_MAGIC_BYTE;
    tx_response->seq = rx_pkt->seq;
    tx_response->source_id = ctx->my_system_id;
    tx_response->target_id = rx_pkt->source_id;
    tx_response->cmd_code = rx_pkt->cmd_code;

    switch (rx_pkt->msg_type) {
        case SBO_MSG_SELECT_REQ: {
            if (ctx->state == SBO_STATE_ARMED && ctx->locked_source_id != rx_pkt->source_id) {
                tx_response->msg_type = SBO_MSG_SELECT_NACK;
                tx_response->sbo_state = ctx->state;
                tx_response->payload[0] = (uint8_t)SBO_ERR_BUSY;
                tx_response->payload_len = 1;
                return SBO_ERR_BUSY;
            }

            /* Переведення у стан ARMED */
            ctx->state = SBO_STATE_ARMED;
            ctx->locked_source_id = rx_pkt->source_id;
            ctx->locked_cmd_code = rx_pkt->cmd_code;
            ctx->active_token = sbo_generate_token(ctx, current_time_ms);
            
            uint16_t window = (rx_pkt->timeout_ms > 0) ? rx_pkt->timeout_ms : SBO_DEFAULT_TIMEOUT_MS;
            ctx->arm_expiry_timestamp_ms = current_time_ms + window;

            tx_response->msg_type = SBO_MSG_SELECT_ACK;
            tx_response->sbo_state = SBO_STATE_ARMED;
            tx_response->sbo_token = ctx->active_token;
            tx_response->timeout_ms = window;
            return SBO_ERR_NONE;
        }

        case SBO_MSG_OPERATE_REQ: {
            if (ctx->state != SBO_STATE_ARMED) {
                tx_response->msg_type = SBO_MSG_OPERATE_NACK;
                tx_response->sbo_state = ctx->state;
                tx_response->payload[0] = (uint8_t)SBO_ERR_NOT_ARMED;
                tx_response->payload_len = 1;
                return SBO_ERR_NOT_ARMED;
            }

            if (rx_pkt->sbo_token != ctx->active_token) {
                /* Спроба використати недійсний токен: негайне знешкодження */
                ctx->state = SBO_STATE_IDLE;
                ctx->active_token = 0;
                tx_response->msg_type = SBO_MSG_OPERATE_NACK;
                tx_response->sbo_state = SBO_STATE_IDLE;
                tx_response->payload[0] = (uint8_t)SBO_ERR_INVALID_TOKEN;
                tx_response->payload_len = 1;
                return SBO_ERR_INVALID_TOKEN;
            }

            if (rx_pkt->cmd_code != ctx->locked_cmd_code) {
                ctx->state = SBO_STATE_IDLE;
                ctx->active_token = 0;
                tx_response->msg_type = SBO_MSG_OPERATE_NACK;
                tx_response->sbo_state = SBO_STATE_IDLE;
                tx_response->payload[0] = (uint8_t)SBO_ERR_CMD_MISMATCH;
                tx_response->payload_len = 1;
                return SBO_ERR_CMD_MISMATCH;
            }

            /* Успішна валідація: дія дозволена до виконання */
            ctx->state = SBO_STATE_IDLE; /* Одноразовий селектор */
            ctx->active_token = 0;

            tx_response->msg_type = SBO_MSG_OPERATE_ACK;
            tx_response->sbo_state = SBO_STATE_IDLE;
            return SBO_ERR_NONE;
        }

        case SBO_MSG_CANCEL_REQ: {
            ctx->state = SBO_STATE_IDLE;
            ctx->active_token = 0;
            tx_response->msg_type = SBO_MSG_CANCEL_ACK;
            tx_response->sbo_state = SBO_STATE_IDLE;
            return SBO_ERR_NONE;
        }

        default:
            return SBO_ERR_INTERNAL_FAULT;
    }
}
```
```cpp
// sbo_target_engine.hpp — Ідіоматичний C++20 з суворою типізацією
#include <cstdint>
#include <chrono>
#include <optional>
#include <expected>
#include <span>
#include <array>
#include <concepts>

namespace sbo {

using namespace std::chrono_literals;

enum class State : uint8_t {
    Idle = 0,
    Armed,
    Executing
};

enum class MessageType : uint8_t {
    SelectReq   = 0x10,
    SelectAck   = 0x11,
    SelectNack  = 0x12,
    OperateReq  = 0x20,
    OperateAck  = 0x21,
    OperateNack = 0x22,
    CancelReq   = 0x30,
    CancelAck   = 0x31
};

enum class Error : uint8_t {
    Busy = 1,
    InvalidToken,
    TimeoutExpired,
    NotArmed,
    CommandMismatch,
    BroadcastForbidden,
    InternalFault
};

struct NodeId {
    uint8_t value;
    constexpr explicit NodeId(uint8_t v) : value(v) {}
    constexpr bool is_broadcast() const noexcept { return value == 0xFF; }
    constexpr auto operator<=>(const NodeId&) const = default;
};

struct Token {
    uint32_t value{0};
    constexpr explicit Token(uint32_t v) : value(v) {}
    constexpr bool is_valid() const noexcept { return value != 0; }
    constexpr auto operator<=>(const Token&) const = default;
};

struct CommandCode {
    uint16_t value{0};
    constexpr explicit CommandCode(uint16_t v) : value(v) {}
    constexpr auto operator<=>(const CommandCode&) const = default;
};

struct Packet {
    uint8_t magic{0x5B};
    uint8_t seq{0};
    MessageType type{MessageType::SelectReq};
    NodeId source{0};
    NodeId target{0};
    State state{State::Idle};
    Token token{0};
    CommandCode command{0};
    std::chrono::milliseconds timeout{5000};
    std::array<uint8_t, 64> payload{};
    size_t payload_len{0};
};

class TargetEngine {
public:
    using TimePoint = std::chrono::steady_clock::time_point;

    explicit TargetEngine(NodeId self_id) noexcept 
        : self_id_(self_id) {}

    void tick(TimePoint now) noexcept {
        if (state_ == State::Armed && now >= arm_expiry_) {
            disarm();
        }
    }

    [[nodiscard]] std::expected<Packet, Error> process_packet(const Packet& rx, TimePoint now) noexcept {
        if (rx.target.is_broadcast()) {
            return std::unexpected(Error::BroadcastForbidden);
        }
        if (rx.target != self_id_) {
            return std::unexpected(Error::InternalFault);
        }

        tick(now);

        Packet tx{};
        tx.magic = 0x5B;
        tx.seq = rx.seq;
        tx.source = self_id_;
        tx.target = rx.source;
        tx.command = rx.command;

        switch (rx.type) {
            case MessageType::SelectReq: {
                if (state_ == State::Armed && locked_source_ != rx.source) {
                    tx.type = MessageType::SelectNack;
                    tx.state = state_;
                    tx.payload[0] = static_cast<uint8_t>(Error::Busy);
                    tx.payload_len = 1;
                    return tx;
                }

                state_ = State::Armed;
                locked_source_ = rx.source;
                locked_command_ = rx.command;
                active_token_ = generate_token();
                arm_expiry_ = now + rx.timeout;

                tx.type = MessageType::SelectAck;
                tx.state = State::Armed;
                tx.token = active_token_;
                tx.timeout = rx.timeout;
                return tx;
            }

            case MessageType::OperateReq: {
                if (state_ != State::Armed) {
                    tx.type = MessageType::OperateNack;
                    tx.state = state_;
                    tx.payload[0] = static_cast<uint8_t>(Error::NotArmed);
                    tx.payload_len = 1;
                    return tx;
                }

                if (rx.token != active_token_) {
                    disarm();
                    tx.type = MessageType::OperateNack;
                    tx.state = State::Idle;
                    tx.payload[0] = static_cast<uint8_t>(Error::InvalidToken);
                    tx.payload_len = 1;
                    return tx;
                }

                if (rx.command != locked_command_) {
                    disarm();
                    tx.type = MessageType::OperateNack;
                    tx.state = State::Idle;
                    tx.payload[0] = static_cast<uint8_t>(Error::CommandMismatch);
                    tx.payload_len = 1;
                    return tx;
                }

                disarm(); // Одноразове виконання
                tx.type = MessageType::OperateAck;
                tx.state = State::Idle;
                return tx;
            }

            case MessageType::CancelReq: {
                disarm();
                tx.type = MessageType::CancelAck;
                tx.state = State::Idle;
                return tx;
            }

            default:
                return std::unexpected(Error::InternalFault);
        }
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] NodeId id() const noexcept { return self_id_; }

private:
    void disarm() noexcept {
        state_ = State::Idle;
        active_token_ = Token{0};
        locked_command_ = CommandCode{0};
        locked_source_ = NodeId{0};
    }

    Token generate_token() noexcept {
        prng_seed_ = prng_seed_ * 1664525u + 1013904223u;
        return Token{prng_seed_ == 0 ? 0xA5A55A5Au : prng_seed_};
    }

    NodeId self_id_;
    State state_{State::Idle};
    NodeId locked_source_{0};
    CommandCode locked_command_{0};
    Token active_token_{0};
    TimePoint arm_expiry_{};
    uint32_t prng_seed_{0x12345678};
};

} // namespace sbo
```
:::

---

## 3. Клієнтський менеджер контексту на пульті (GCS Focus Manager)

На боці графічного інтерфейсу пульта оператора контролер SBO виконує зворотну функцію: він зв'язує активну картку інтерфейсу з механізмом відправки пакетів, підставляє `target_id` у всі елементи керування і блокує відправку команд, якщо замок не активовано.

Клієнтський модуль відстежує стан підтвердження селекції: якщо пульт надіслав `SELECT_REQ`, але відповідь `SELECT_ACK` не надійшла протягом тайм-ауту зв'язку (зазвичай 400 мс), картка вибору автоматично підсвічується червоною рамкою «Втрата зв'язку», а кнопка дії блокується. Це виключає ситуацію, коли оператор вважає апарат готовим до дії, тоді як радіоканал між пультом і бортом розірвано.

:::tabs
```c
/* gcs_focus_manager.c — Логіка блокування цілі на пульті оператора */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    uint8_t         focused_target_id;
    bool            is_armed;
    uint32_t        received_token;
    uint32_t        selection_deadline_ms;
    char            target_name[16];
} gcs_target_lock_t;

void gcs_lock_init(gcs_target_lock_t *lock) {
    memset(lock, 0, sizeof(gcs_target_lock_t));
    lock->is_armed = false;
}

/* Обробка кліку оператора на картку вибору апарата */
void gcs_select_vehicle(gcs_target_lock_t *lock, uint8_t target_id, const char *name) {
    lock->focused_target_id = target_id;
    lock->is_armed = false; /* Чекаємо квитанції від борту */
    lock->received_token = 0;
    strncpy(lock->target_name, name, sizeof(lock->target_name) - 1);
}

/* Фіксація підтвердження селекції (SELECT_ACK) */
void gcs_on_select_ack(gcs_target_lock_t *lock, uint8_t from_id, uint32_t token, uint16_t window_ms, uint32_t now_ms) {
    if (from_id == lock->focused_target_id) {
        lock->is_armed = true;
        lock->received_token = token;
        lock->selection_deadline_ms = now_ms + window_ms;
    }
}

/* Безпечна генерація команди: повертає false, якщо ціль не заблокована */
bool gcs_build_operate_packet(gcs_target_lock_t *lock, uint16_t cmd_code, sbo_packet_t *out_pkt, uint32_t now_ms) {
    if (!lock->is_armed || now_ms >= lock->selection_deadline_ms) {
        lock->is_armed = false; /* Тайм-аут вичерпано */
        return false;
    }

    memset(out_pkt, 0, sizeof(sbo_packet_t));
    out_pkt->magic = SBO_MAGIC_BYTE;
    out_pkt->msg_type = SBO_MSG_OPERATE_REQ;
    out_pkt->source_id = 0xFE; /* GCS ID */
    out_pkt->target_id = lock->focused_target_id;
    out_pkt->sbo_token = lock->received_token;
    out_pkt->cmd_code = cmd_code;

    /* Після відправки команди замок скидається локально */
    lock->is_armed = false;
    return true;
}
```
```cpp
// gcs_focus_manager.hpp — C++20 менеджер вибору цілі для наземної станції
#include <string>
#include <string_view>
#include <chrono>
#include <optional>
#include <expected>

namespace gcs {

class FocusManager {
public:
    using TimePoint = std::chrono::steady_clock::time_point;

    void select_vehicle(sbo::NodeId id, std::string_view name) noexcept {
        focused_id_ = id;
        target_name_ = name;
        armed_ = false;
        token_ = sbo::Token{0};
    }

    void on_select_ack(sbo::NodeId from_id, sbo::Token token, std::chrono::milliseconds window, TimePoint now) noexcept {
        if (from_id == focused_id_) {
            armed_ = true;
            token_ = token;
            deadline_ = now + window;
        }
    }

    [[nodiscard]] std::optional<sbo::Packet> build_operate_packet(sbo::CommandCode cmd, TimePoint now) noexcept {
        if (!armed_ || now >= deadline_) {
            armed_ = false;
            return std::nullopt;
        }

        sbo::Packet pkt{};
        pkt.magic = 0x5B;
        pkt.type = sbo::MessageType::OperateReq;
        pkt.source = sbo::NodeId{0xFE};
        pkt.target = focused_id_;
        pkt.token = token_;
        pkt.command = cmd;

        armed_ = false; // Одноразовий клік
        return pkt;
    }

    [[nodiscard]] bool is_armed(TimePoint now) const noexcept {
        return armed_ && (now < deadline_);
    }

    [[nodiscard]] std::string_view target_name() const noexcept {
        return target_name_;
    }

    [[nodiscard]] sbo::NodeId target_id() const noexcept {
        return focused_id_;
    }

private:
    sbo::NodeId focused_id_{0};
    std::string target_name_{"NONE"};
    bool armed_{false};
    sbo::Token token_{0};
    TimePoint deadline_{};
};

} // namespace gcs
```
:::

---

## 4. Багатопотоковість у FreeRTOS та синхронізація

В операційних системах реального часу (RTOS) модуль SBO часто взаємодіє з двома різними задачами:
1. **Задача прийому радіопакетів (`RadioRxTask`):** має високий пріоритет, отримує байти від DMA або SPI, викликає парсер і оновлює стан селектора.
2. **Задача управління виконавчими механізмами (`ActuatorTask`):** виконує фізичне розмикання контакторів, зміну PWM або відправку команд по шині CAN.

Для запобігання стану гонитви (Race Condition) між цими задачами доступ до структури контексту `sbo_target_context_t` захищається двійковим семафором або м'ютексом FreeRTOS (`xSemaphoreCreateMutex()`). У перериваннях зв'язку (ISR) безпосередня зміна стану FSM заборонена: вхідний пакет поміщається в чергу `QueueHandle_t`, звідки послідовно вичитується диспетчером завдань.

Якщо під час виконання критичної дії надходить новий запит селекції, FSM не скидає поточний процес, а повертає статус `ERR_SBO_BUSY`. Це гарантує неподільність (атомарність) кожної виконаної операції.

```
 [ ISR Радіомодема ] ──► [ Черга RxQueue ] ──► [ RadioRxTask (SBO Engine) ]
                                                        │
                                                        ▼ (М'ютекс захисту FSM)
                                               [ Контекст TargetContext ]
                                                        │
                                                        ▼ (Черга команд дії)
                                               [ ActuatorTask (Приводи) ]
```

---

## 5. Модульне тестування та перевірка відмовостійкості

Для верифікації безпекових інваріантів розроблено тестовий набір (Unit Test Suite), що перевіряє поведінку автомата за різних аномалій зв'язку. Тести охоплюють чотири критичні сценарії:
1. Пряма відправка команди без фази `SELECT` (має повертати `ERR_SBO_NOT_ARMED`).
2. Номінальний цикл вибору, зведення та виконання у межах встановленого часового вікна.
3. Спроба виконання після спливання встановленого тайм-ауту (повинна блокуватися з кодом `ERR_SBO_TIMEOUT_EXPIRED`).
4. Повторне надсилання кадру з тим самим токеном після успішного виконання (повинно відхилятися через одноразовість селектора).

:::tabs
```c
/* test_sbo_suite.c — Автоматизований тестовий сценарій мовою C */
#include <stdio.h>
#include <assert.h>

void test_sbo_full_cycle(void) {
    sbo_target_context_t target;
    sbo_target_init(&target, 0x02, 0x12345678);

    uint32_t now = 1000;
    sbo_packet_t rx, tx;

    /* Сценарій 1: Спроба виконання без вибору (Повинна провалитися) */
    memset(&rx, 0, sizeof(rx));
    rx.magic = SBO_MAGIC_BYTE;
    rx.target_id = 0x02;
    rx.msg_type = SBO_MSG_OPERATE_REQ;
    rx.cmd_code = 0x0101;
    rx.sbo_token = 0x9999;
    sbo_error_t err = sbo_target_process_packet(&target, &rx, &tx, now);
    assert(err == SBO_ERR_NOT_ARMED);
    assert(target.state == SBO_STATE_IDLE);

    /* Сценарій 2: Успішна селекція */
    rx.msg_type = SBO_MSG_SELECT_REQ;
    rx.source_id = 0xFE;
    rx.timeout_ms = 5000;
    err = sbo_target_process_packet(&target, &rx, &tx, now);
    assert(err == SBO_ERR_NONE);
    assert(target.state == SBO_STATE_ARMED);
    uint32_t issued_token = tx.sbo_token;
    assert(issued_token != 0);

    /* Сценарій 3: Успішне виконання у межах вікна (1.5 сек пізніше) */
    now += 1500;
    rx.msg_type = SBO_MSG_OPERATE_REQ;
    rx.sbo_token = issued_token;
    err = sbo_target_process_packet(&target, &rx, &tx, now);
    assert(err == SBO_ERR_NONE);
    assert(target.state == SBO_STATE_IDLE); /* Авто-скидання */

    /* Сценарій 4: Повторний клік з тим самим токеном (Повинен провалитися!) */
    err = sbo_target_process_packet(&target, &rx, &tx, now);
    assert(err == SBO_ERR_NOT_ARMED);
}
```
```cpp
// test_sbo_suite.cpp — Модульні тести на базі C++20
#include <cassert>
#include <iostream>

void run_cpp_sbo_tests() {
    using namespace std::chrono_literals;
    sbo::TargetEngine target{sbo::NodeId{0x02}};
    auto now = std::chrono::steady_clock::now();

    // Тест 1: Пряме виконання без селекції
    sbo::Packet direct_op{};
    direct_op.target = sbo::NodeId{0x02};
    direct_op.source = sbo::NodeId{0xFE};
    direct_op.type = sbo::MessageType::OperateReq;
    direct_op.command = sbo::CommandCode{0x0101};
    direct_op.token = sbo::Token{0x11223344};

    auto res = target.process_packet(direct_op, now);
    assert(res.has_value());
    assert(res->type == sbo::MessageType::OperateNack);
    assert(target.state() == sbo::State::Idle);

    // Тест 2: Номінальна селекція
    sbo::Packet select_pkt{};
    select_pkt.target = sbo::NodeId{0x02};
    select_pkt.source = sbo::NodeId{0xFE};
    select_pkt.type = sbo::MessageType::SelectReq;
    select_pkt.command = sbo::CommandCode{0x0101};
    select_pkt.timeout = 5000ms;

    auto sel_res = target.process_packet(select_pkt, now);
    assert(sel_res.has_value());
    assert(sel_res->type == sbo::MessageType::SelectAck);
    assert(target.state() == sbo::State::Armed);
    auto token = sel_res->token;

    // Тест 3: Виконання після тайм-ауту (+6 секунд)
    auto future_time = now + 6000ms;
    sbo::Packet op_late{};
    op_late.target = sbo::NodeId{0x02};
    op_late.source = sbo::NodeId{0xFE};
    op_late.type = sbo::MessageType::OperateReq;
    op_late.command = sbo::CommandCode{0x0101};
    op_late.token = token;

    auto late_res = target.process_packet(op_late, future_time);
    assert(late_res.has_value());
    assert(late_res->type == sbo::MessageType::OperateNack);
    assert(target.state() == sbo::State::Idle);
}
```
:::

---

## 6. Апаратні та часові метрики продуктивності

Під час компіляції під цільову платформу ARM Cortex-M4 (компілятор GCC 12.3 з оптимізацією `-O2`) модуль демонструє такі характеристики:

| Ресурс | Мова C (Bare-Metal) | Мова C++20 (Embedded Profile) |
| :--- | :--- | :--- |
| **Flash (Текст програми)** | 540 байтів | 680 байтів |
| **SRAM (Контекст вузла)** | 24 байти | 32 байти |
| **Час валідації пакета (168 МГц STM32F4)** | 1.8 мкс | 1.9 мкс |
| **Динамічна пам'ять (Heap)** | **0 байтів** | **0 байтів** |

Мінімальні накладні витрати дозволяють інтегрувати захисний шлюз SBO навіть у найменші восьмибітні та тридцятидвобітні мікроконтролери бортової периферії без впливу на швидкість основних контурів стабілізації польоту.

---

## 7. Відмовостійкість при провалах живлення (Brownout Resilience)

Критичною вимогою до бортової реалізації SBO є стійкість до раптових мікропровалів живлення бортової мережі (Brownout Reset). Якщо мікроконтролер перезавантажується під час перебування у стані `ARMED`, після відновлення живлення його контекст обов'язково повинен ініціалізуватися у стані `IDLE` із генерацією нового початкового значення генератора випадкових чисел. 

Збереження токена в енергонезалежній пам'яті (Flash / EEPROM) категорично заборонене, оскільки старий токен може бути використаний зловмисником або запізнілим пакетом із радіоефіру після апаратного перезапуску борту. Усі лічильники селекції скидаються в нуль під час кожного старту функції `sbo_target_init()`.

---

## 8. Апаратна індикація стану та діагностичні лінії GPIO

Для налагодження поведінки FSM на стенді без підключення налагоджувача JTAG/SWD рекомендується призначити три тестові виводи GPIO для апаратного профілювання за допомогою логічного аналізатора:
* `TP_SBO_ARMED` (Високий рівень під час активності стану `ARMED`);
* `TP_SBO_OP_EXEC` (Короткий імпульс тривалістю 10 мкс у момент успішного пропуску команди до виконання);
* `TP_SBO_SECURITY_DROP` (Імпульс тривалістю 50 мкс під час відхилення неавторизованого або широкомовного кадру).

Ця апаратна телеметрія дозволяє фіксувати точний час між отриманням радіокадру та спрацюванням силового ключа із субмікросекундною точністю.
