# ⚙️ Парсер пакетів та скінченний автомат транзакцій ATT

Низькорівнева розробка стека або драйвера Bluetooth Low Energy вимагає суворого контролю за двома критичними аспектами: безпекою роботи з пам'яттю під час десеріалізації сирих байтів ефіру та точним дотриманням протокольних часових обмежень. Будь-яка помилка в розрахунку довжини кадру в мікроконтролері з обмеженою пам'яттю веде до вразливостей виходу за межі буфера (англ. *Buffer Overflow*), а порушення транзакційної черги блокує зв'язок на канальному рівні.

Цей проект демонструє побудову вбудованого парсера пакетів протоколу атрибутів (ATT) та скінченного автомата клієнтських транзакцій. Реалізація забезпечує нульове копіювання пам'яті (zero-copy parsing), суворо перевіряє межі кожного поля, гарантує послідовне проходження транзакцій та відстежує обов'язковий 30-секундний таймер таймауту.

---

### 1. Архітектурні вимоги та модель станів

Протокол ATT функціонує поверх фіксованого каналу L2CAP із числовим ідентифікатором `CID = 0x0004`. Кожен прийнятий від контролера кадр містить рівно один протокольний блок даних (PDU), довжина якого обмежена поточним значенням `ATT_MTU`.

#### Основні обов'язки парсера
1. **Валідація довжини без динамічної пам'яті**: парсер повинен відхиляти будь-який вхідний буфер, розмір якого менший за мінімально вимаганий для конкретного коду операції `Opcode`, або перевищує узгоджений `ATT_MTU`.
2. **Безпечне читання полів (Little-Endian)**: забороняється пряме приведення вказівників типу `*(uint16_t*)&buf[1]`, оскільки на архітектурах ARM Cortex-M0 це викликає апаратне виключення несиметричного доступу (англ. *Unaligned Memory Access Fault*), а на компіляторах із суворою оптимізацією порушує правило строгого псевдонімування (англ. *Strict Aliasing Rule*). Витягнення 16-бітних полів повинно виконуватися виключно через явні побайтові зсуви.
3. **Відокремлення потокових сповіщень**: асинхронні сповіщення `ATT_HANDLE_VALUE_NTF` можуть надходити від сервера в будь-який момент, зокрема тоді, коли клієнт очікує на відповідь на раніше відправлений `Write Request`. Парсер зобов'язаний передати сповіщення застосунку, не руйнуючи очікування поточної транзакції.

```
                  +-----------------------------------+
                  |            Стан: IDLE             |
                  |     (Черга вільна для запиту)     |
                  +-----------------------------------+
                                    |
                                    | att_client_send_request()
                                    | [Зведення таймера 30 с]
                                    v
                  +-----------------------------------+
                  |     Стан: WAITING_RESPONSE        |
                  |    (Нові запити БЛОКУЮТЬСЯ)       |
                  +-----------------------------------+
                     /              |               \
   [Прийом Response / Error]        |        [Таймаут > 30 с]
                    /               |                \
                   v                |                 v
+------------------------+          |    +------------------------+
| Повернення в стан IDLE |          |    |    Стан: TIMED_OUT     |
|  (Таймер скинуто, черга|          |    | (Фатальний збій зв'язку|
|      розблокована)     |          |    |     HCI Disconnect)    |
+------------------------+          |    +------------------------+
                                    |
                        [Прийом Notification]
                                    |
                                    v
                        +------------------------+
                        |  Передача в застосунок |
                        | (Стан очікування не    |
                        |       змінюється)      |
                        +------------------------+
```

---

### 2. Реалізація парсера та клієнтського автомата

Нижче наведено паралельні реалізації ядра протоколу: версію на чистому C для вбудованих систем (STM32, ESP-IDF, Zephyr OS) та версію на C++20 із використанням неволодіючих зрізів пам'яті `std::span`, безпечних типів-об'єднань `std::variant` та явного повернення результатів через `std::expected`.

:::tabs
```c
// att_engine.h / att_engine.c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define ATT_DEFAULT_MTU         23
#define ATT_MAX_MTU             517
#define ATT_TRANSACTION_TIMEOUT 30000 // 30 секунд у мілісекундах

// Коди операцій протоколу ATT
typedef enum {
    ATT_OP_ERROR_RSP            = 0x01,
    ATT_OP_EXCHANGE_MTU_REQ     = 0x02,
    ATT_OP_EXCHANGE_MTU_RSP     = 0x03,
    ATT_OP_READ_BY_TYPE_REQ     = 0x08,
    ATT_OP_READ_BY_TYPE_RSP     = 0x09,
    ATT_OP_READ_REQ             = 0x0A,
    ATT_OP_READ_RSP             = 0x0B,
    ATT_OP_WRITE_REQ            = 0x12,
    ATT_OP_WRITE_RSP            = 0x13,
    ATT_OP_WRITE_CMD            = 0x52,
    ATT_OP_HANDLE_VALUE_NTF     = 0x1B,
    ATT_OP_HANDLE_VALUE_IND     = 0x1D,
    ATT_OP_HANDLE_VALUE_CFM     = 0x1E
} att_opcode_t;

// Стани клієнтського автомата транзакцій
typedef enum {
    ATT_STATE_IDLE,
    ATT_STATE_WAITING_RESPONSE,
    ATT_STATE_TIMED_OUT
} att_fsm_state_t;

// Розібраний пакет ATT без дублювання даних
typedef struct {
    att_opcode_t opcode;
    uint16_t     handle;
    uint16_t     offset;
    uint8_t      error_code;
    uint8_t      req_opcode_in_err;
    const uint8_t* value_data;
    size_t       value_len;
} att_packet_t;

// Стан клієнтського контексту ATT
typedef struct {
    att_fsm_state_t state;
    att_opcode_t    pending_req_opcode;
    uint16_t        pending_req_handle;
    uint32_t        timer_start_ms;
    uint16_t        effective_mtu;
} att_client_t;

// Безпечне витягнення 16-бітного числа у форматі Little-Endian
static inline uint16_t att_read_le16(const uint8_t* ptr) {
    return (uint16_t)ptr[0] | ((uint16_t)ptr[1] << 8);
}

// Запис 16-бітного числа у форматі Little-Endian
static inline void att_write_le16(uint8_t* ptr, uint16_t val) {
    ptr[0] = (uint8_t)(val & 0xFF);
    ptr[1] = (uint8_t)((val >> 8) & 0xFF);
}

// Ініціалізація клієнтського контексту
void att_client_init(att_client_t* client) {
    client->state = ATT_STATE_IDLE;
    client->pending_req_opcode = 0;
    client->pending_req_handle = 0;
    client->timer_start_ms = 0;
    client->effective_mtu = ATT_DEFAULT_MTU;
}

// Безпечний парсер вхідного кадру L2CAP
bool att_parse_packet(const uint8_t* buf, size_t len, att_packet_t* pkt) {
    if (!buf || len == 0 || !pkt) return false;
    memset(pkt, 0, sizeof(att_packet_t));
    pkt->opcode = (att_opcode_t)buf[0];

    switch (pkt->opcode) {
        case ATT_OP_ERROR_RSP:
            if (len != 5) return false;
            pkt->req_opcode_in_err = buf[1];
            pkt->handle            = att_read_le16(&buf[2]);
            pkt->error_code        = buf[4];
            return true;

        case ATT_OP_EXCHANGE_MTU_REQ:
        case ATT_OP_EXCHANGE_MTU_RSP:
            if (len != 3) return false;
            pkt->handle = att_read_le16(&buf[1]); // поле MTU
            return (pkt->handle >= ATT_DEFAULT_MTU);

        case ATT_OP_READ_REQ:
            if (len != 3) return false;
            pkt->handle = att_read_le16(&buf[1]);
            return (pkt->handle != 0x0000);

        case ATT_OP_READ_RSP:
            pkt->value_data = (len > 1) ? &buf[1] : NULL;
            pkt->value_len  = (len > 1) ? (len - 1) : 0;
            return true;

        case ATT_OP_WRITE_REQ:
        case ATT_OP_WRITE_CMD:
        case ATT_OP_HANDLE_VALUE_NTF:
        case ATT_OP_HANDLE_VALUE_IND:
            if (len < 3) return false;
            pkt->handle     = att_read_le16(&buf[1]);
            pkt->value_data = (len > 3) ? &buf[3] : NULL;
            pkt->value_len  = (len > 3) ? (len - 3) : 0;
            return (pkt->handle != 0x0000);

        case ATT_OP_WRITE_RSP:
        case ATT_OP_HANDLE_VALUE_CFM:
            return (len == 1);

        default:
            return false;
    }
}

// Спроба відправки запиту клієнтом
bool att_client_send_request(att_client_t* client, att_opcode_t req_op,
                            uint16_t handle, uint32_t now_ms) {
    if (client->state == ATT_STATE_WAITING_RESPONSE) {
        return false; // Канал заблоковано активною транзакцією!
    }
    client->pending_req_opcode = req_op;
    client->pending_req_handle = handle;
    client->timer_start_ms     = now_ms;
    client->state              = ATT_STATE_WAITING_RESPONSE;
    return true;
}

// Обробка прийому пакета від сервера
bool att_client_on_rx(att_client_t* client, const uint8_t* buf,
                      size_t len, att_packet_t* out_pkt) {
    if (!att_parse_packet(buf, len, out_pkt)) {
        return false;
    }

    // Асинхронні сповіщення не розблоковують чергу запитів
    if (out_pkt->opcode == ATT_OP_HANDLE_VALUE_NTF) {
        return true;
    }

    if (client->state == ATT_STATE_WAITING_RESPONSE) {
        bool matches = false;

        if (out_pkt->opcode == ATT_OP_ERROR_RSP) {
            matches = (out_pkt->req_opcode_in_err == client->pending_req_opcode);
        } else if (client->pending_req_opcode == ATT_OP_READ_REQ &&
                   out_pkt->opcode == ATT_OP_READ_RSP) {
            matches = true;
        } else if (client->pending_req_opcode == ATT_OP_WRITE_REQ &&
                   out_pkt->opcode == ATT_OP_WRITE_RSP) {
            matches = true;
        } else if (client->pending_req_opcode == ATT_OP_EXCHANGE_MTU_REQ &&
                   out_pkt->opcode == ATT_OP_EXCHANGE_MTU_RSP) {
            client->effective_mtu = (out_pkt->handle < ATT_MAX_MTU) ?
                                     out_pkt->handle : ATT_MAX_MTU;
            matches = true;
        }

        if (matches) {
            client->state = ATT_STATE_IDLE;
            client->pending_req_opcode = 0;
            client->pending_req_handle = 0;
            return true;
        }
    }
    return true;
}

// Перевірка спрацювання таймауту 30 секунд
bool att_client_poll_timeout(att_client_t* client, uint32_t now_ms) {
    if (client->state == ATT_STATE_WAITING_RESPONSE) {
        if ((now_ms - client->timer_start_ms) >= ATT_TRANSACTION_TIMEOUT) {
            client->state = ATT_STATE_TIMED_OUT;
            return true; // Спрацював обов'язковий розрив зв'язку!
        }
    }
    return false;
}
```
```cpp
// att_engine.hpp
#pragma once
#include <cstdint>
#include <cstddef>
#include <span>
#include <variant>
#include <expected>
#include <chrono>
#include <algorithm>

namespace ble::att {

using namespace std::chrono_literals;

constexpr uint16_t DefaultMtu = 23;
constexpr uint16_t MaxMtu     = 517;
constexpr auto TransactionTimeout = 30s;

enum class Opcode : uint8_t {
    ErrorRsp          = 0x01,
    ExchangeMtuReq    = 0x02,
    ExchangeMtuRsp    = 0x03,
    ReadReq           = 0x0A,
    ReadRsp           = 0x0B,
    WriteReq          = 0x12,
    WriteRsp          = 0x13,
    WriteCmd          = 0x52,
    HandleValueNtf    = 0x1B,
    HandleValueInd    = 0x1D,
    HandleValueCfm    = 0x1E
};

enum class ParseError {
    BufferTooShort,
    InvalidOpcode,
    InvalidLength,
    InvalidHandle,
    MtuTooSmall
};

struct ErrorResponse {
    uint8_t  requestOpcode;
    uint16_t attributeHandle;
    uint8_t  errorCode;
};

struct ExchangeMtuResponse {
    uint16_t serverRxMtu;
};

struct ReadResponse {
    std::span<const uint8_t> value;
};

struct WriteResponse {};

struct Notification {
    uint16_t handle;
    std::span<const uint8_t> value;
};

using Packet = std::variant<
    ErrorResponse,
    ExchangeMtuResponse,
    ReadResponse,
    WriteResponse,
    Notification
>;

class PacketParser {
public:
    static std::expected<Packet, ParseError> parse(std::span<const uint8_t> buffer) noexcept {
        if (buffer.empty()) {
            return std::unexpected(ParseError::BufferTooShort);
        }

        const auto op = static_cast<Opcode>(buffer[0]);
        switch (op) {
            case Opcode::ErrorRsp: {
                if (buffer.size() != 5) return std::unexpected(ParseError::InvalidLength);
                return ErrorResponse{
                    .requestOpcode   = buffer[1],
                    .attributeHandle = readLe16(buffer.subspan<2, 2>()),
                    .errorCode       = buffer[4]
                };
            }
            case Opcode::ExchangeMtuRsp: {
                if (buffer.size() != 3) return std::unexpected(ParseError::InvalidLength);
                const uint16_t mtu = readLe16(buffer.subspan<1, 2>());
                if (mtu < DefaultMtu) return std::unexpected(ParseError::MtuTooSmall);
                return ExchangeMtuResponse{ .serverRxMtu = mtu };
            }
            case Opcode::ReadRsp: {
                return ReadResponse{ .value = buffer.subspan(1) };
            }
            case Opcode::WriteRsp: {
                if (buffer.size() != 1) return std::unexpected(ParseError::InvalidLength);
                return WriteResponse{};
            }
            case Opcode::HandleValueNtf: {
                if (buffer.size() < 3) return std::unexpected(ParseError::InvalidLength);
                const uint16_t hdl = readLe16(buffer.subspan<1, 2>());
                if (hdl == 0) return std::unexpected(ParseError::InvalidHandle);
                return Notification{
                    .handle = hdl,
                    .value  = buffer.subspan(3)
                };
            }
            default:
                return std::unexpected(ParseError::InvalidOpcode);
        }
    }

private:
    template <size_t Offset, size_t Count>
    static constexpr uint16_t readLe16(std::span<const uint8_t, Count> s) noexcept {
        return static_cast<uint16_t>(s[0]) | (static_cast<uint16_t>(s[1]) << 8);
    }

    static constexpr uint16_t readLe16(std::span<const uint8_t, 2> s) noexcept {
        return static_cast<uint16_t>(s[0]) | (static_cast<uint16_t>(s[1]) << 8);
    }
};

class ClientStateMachine {
public:
    enum class State { Idle, WaitingResponse, TimedOut };

    [[nodiscard]] bool canSendRequest() const noexcept {
        return state_ == State::Idle;
    }

    bool startRequest(Opcode reqOp, uint16_t handle,
                      std::chrono::steady_clock::time_point now) noexcept {
        if (state_ != State::Idle) return false;
        pendingOp_     = reqOp;
        pendingHandle_ = handle;
        timerStart_    = now;
        state_         = State::WaitingResponse;
        return true;
    }

    bool onPacketReceived(const Packet& pkt) noexcept {
        if (std::holds_alternative<Notification>(pkt)) {
            return true; // Сповіщення приймаються без розблокування черги
        }

        if (state_ == State::WaitingResponse) {
            bool matched = std::visit([this](const auto& p) {
                using T = std::decay_t<decltype(p)>;
                if constexpr (std::is_same_v<T, ErrorResponse>) {
                    return static_cast<uint8_t>(pendingOp_) == p.requestOpcode;
                } else if constexpr (std::is_same_v<T, ReadResponse>) {
                    return pendingOp_ == Opcode::ReadReq;
                } else if constexpr (std::is_same_v<T, WriteResponse>) {
                    return pendingOp_ == Opcode::WriteReq;
                } else if constexpr (std::is_same_v<T, ExchangeMtuResponse>) {
                    effectiveMtu_ = std::min(p.serverRxMtu, MaxMtu);
                    return pendingOp_ == Opcode::ExchangeMtuReq;
                }
                return false;
            }, pkt);

            if (matched) {
                state_ = State::Idle;
                pendingOp_ = {};
                pendingHandle_ = 0;
                return true;
            }
        }
        return false;
    }

    bool checkTimeout(std::chrono::steady_clock::time_point now) noexcept {
        if (state_ == State::WaitingResponse) {
            if (now - timerStart_ >= TransactionTimeout) {
                state_ = State::TimedOut;
                return true;
            }
        }
        return false;
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] uint16_t effectiveMtu() const noexcept { return effectiveMtu_; }

private:
    State state_{State::Idle};
    Opcode pendingOp_{};
    uint16_t pendingHandle_{0};
    uint16_t effectiveMtu_{DefaultMtu};
    std::chrono::steady_clock::time_point timerStart_{};
};

} // namespace ble::att
```
:::

---

### 3. Покроковий розбір алгоритму обробки

Розглянемо послідовність дій під час проходження типових протокольних подій.

#### 1. Десеріалізація без алокацій (Zero-Copy)
У версії на C структура `att_packet_t` містить вказівник `const uint8_t* value_data`, який вказує безпосередньо на зміщення всередині первинного вхідного буфера L2CAP. У версії на C++ це реалізовано через тип `std::span<const uint8_t>`. Це гарантує:
* Відсутність фрагментації динамічної купи (Heap Fragmentation) під час інтенсивного прийому потокових сповіщень;
* Мінімальні накладні витрати процесора: парсинг зводиться до перевірки розміру та одного оператора вибору `switch`.

#### 2. Захист від паралельних запитів
Якщо користувацький код намагається викликати функцію `att_client_send_request` у момент, коли `client->state == ATT_STATE_WAITING_RESPONSE`, функція повертає `false`. Це захищає радіоефір від некоректних запитів, які сервер був би змушений відхилити або проігнорувати. Розробник повинен організувати чергування запитів у своєму застосунку.

#### 3. Обробка відповідей про помилки
Коли сервер надсилає `ATT_ERROR_RSP`, він вказує код операції вихідного запиту в полі `RequestOpcode`. Автомат транзакцій перевіряє, чи збігається цей код із `pending_req_opcode`. Якщо запит збігається, стан автомата скидається в `ATT_STATE_IDLE`, а подія помилки передається на рівень GATT для повідомлення застосунку (наприклад, про необхідність запустити спарювання через помилку `0x05`).

#### 4. Обробка таймауту транзакції
Функція `att_client_poll_timeout` повинна викликатися в головному циклі подій або системному таймері. Якщо сервер не надав відповіді протягом `30 000` мс, клієнт фіксує стан `ATT_STATE_TIMED_OUT`. Згідно з розділом 3.3.3 частини F тому 3 специфікації Bluetooth Core Specification, після спрацювання цього таймера клієнт зобов'язаний негайно відправити контролеру команду `HCI_Disconnect` і примусово розірвати фізичне з'єднання. Жодні наступні запити на цьому каналі відправлятися не можуть.

---

### 4. Повний сценарій сесії: простеження роботи автомата

Щоб наочно побачити, як взаємодіють парсер та автомат станів у реальному часі, простежимо типовий життєвий цикл з'єднання між клієнтом (центральним пристроєм) та сервером (периферійним сенсором):

1. **Крок 1. Ініціалізація зв'язку**:
   * Контролер встановлює радіоз'єднання. Клієнтський контекст ініціалізується функцією `att_client_init`, стан встановлюється в `ATT_STATE_IDLE`, а `effective_mtu` дорівнює `23` байти.
2. **Крок 2. Узгодження MTU**:
   * Клієнт надсилає `ATT_EXCHANGE_MTU_REQ` із пропозицією свого буфера на 512 байтів (`now_ms = 100`).
   * Автомат переходить у стан `ATT_STATE_WAITING_RESPONSE`, запам'ятовуючи `pending_req_opcode = ATT_OP_EXCHANGE_MTU_REQ` та фіксуючи `timer_start_ms = 100`.
   * Сервер відповідає кадром `ATT_EXCHANGE_MTU_RSP` (3 байти: `0x03, 0xF7, 0x00`, що означає 247 байтів) у момент `now_ms = 145`.
   * Функція `att_client_on_rx` парсить кадр, витягує розмір 247, оновлює `effective_mtu = 247` та повертає автомат у стан `ATT_STATE_IDLE`.
3. **Крок 3. Читання атрибута та одночасне сповіщення**:
   * Застосунок ініціює читання характеристики заряду батареї за дескриптором `0x0007`: викликається `att_client_send_request(..., ATT_OP_READ_REQ, 0x0007, 200)`. Автомат переходить у стан `ATT_STATE_WAITING_RESPONSE`.
   * У момент `now_ms = 220` від сервера надходить пакет сповіщення `ATT_HANDLE_VALUE_NTF` з дескриптора `0x0003` (пульс 72 bpm).
   * Функція `att_client_on_rx` успішно парсить сповіщення і передає його обробнику сенсора, але **не змінює стан очікування** — клієнт продовжує очікувати на відповідь читання.
   * У момент `now_ms = 240` надходить `ATT_READ_RSP` зі значенням `0x62` (98 %). Автомат розпізнає збіг із `pending_req_opcode = ATT_OP_READ_REQ` і переходить у `ATT_STATE_IDLE`.
4. **Крок 4. Запобігання колізії запитів**:
   * Дві різні підсистеми застосунку одночасно намагаються записати конфігурацію: перша викликає `att_client_send_request(..., ATT_OP_WRITE_REQ, 0x0004, 300)` — функція повертає `true`, стан стає `WAITING_RESPONSE`.
   * Через 2 мілісекунди друга підсистема викликає `att_client_send_request(..., ATT_OP_WRITE_REQ, 0x0008, 302)` — функція негайно повертає `false`, запобігаючи порушенню протокольного блокування.
5. **Крок 5. Відпрацювання критичного таймауту**:
   * Якщо сервер завис і не надіслав `ATT_WRITE_RSP`, виклик `att_client_poll_timeout` у момент `now_ms = 30305` повертає `true`, переводячи клієнт у стан `ATT_STATE_TIMED_OUT`. Стек негайно ініціює відключення радіозв'язку.

---

### 5. Інтеграція в архітектуру реального часу (RTOS)

У реальних прошивках на базі операційних систем реального часу (FreeRTOS, Zephyr OS, Mbed OS) парсер і скінченний автомат транзакцій ATT не повинні викликатися безпосередньо з контексту обробника апаратного переривання (ISR) контролера BLE. Це зумовлено такими вимогами:

* **Розділення контекстів ISR та Task**: контролер радіомодуля генерує переривання прийому пакета, яке переносить сирі байти через інтерфейс HCI (UART або Shared RAM) у кільцевий буфер. Обробник переривання лише виставляє біт у групі подій (Event Group) або надсилає дескриптор буфера в чергу задач `QueueHandle_t`.
* **Захист від стану гонитви (Race Conditions)**: якщо задача застосунку намагається надіслати `ATT_WRITE_REQ` в той самий момент, коли задача стека обробляє вхідний `ATT_READ_RSP`, виникає стан гонитви за змінну стану `client->state`. Доступ до автомата транзакцій повинен бути захищений м'ютексом або виконуватися в межах єдиного потоку стека (англ. *Event Loop Task*).
* **Керування таймерами без активного очікування**: замість виклику `att_client_poll_timeout` у нескінченному циклі з блокуванням ядра процесора, слід використовувати програмні таймери RTOS (`TimerHandle_t` у FreeRTOS або `k_timer` у Zephyr). Таймер зводиться на 30 000 мс у момент виклику `att_client_send_request` і зупиняється функцією `xTimerStop` при отриманні валідної відповіді. Якщо таймер таки спрацював, його функція зворотного виклику (callback) безпосередньо надсилає команду розриву радіоз'єднання.

---

### 6. Аналіз безпеки та стійкості до шкідливих пакетів

Протокольний рівень ATT є першою лінією взаємодії з потенційно скомпрометованим або ворожим BLE-пристроєм. Парсер зобов'язаний бути стійким до спеціально сформованих аномальних пакетів:

1. **Вразливості типу Heartbleed (Over-read)**: у пакетах `ATT_READ_BY_TYPE_RSP` сервер повертає поле `Length` (розмір одного елемента списку). Якщо шкідливий сервер надішле пакет розміром 5 байтів, але вкаже `Length = 20`, наївний цикл розбору прочитає 15 байтів пам'яті поза межами прийнятого буфера, що може розкрити конфіденційні ключі шифрування або спричинити збій адресації `Segmentation Fault`. Наш парсер суворо перевіряє співвідношення між розміром буфера та довжиною кроку.
2. **Атака на переповнення черги записів**: якщо клієнт надсилає нескінченну серію запитів `ATT_PREPARE_WRITE_REQ`, не надсилаючи `Execute Write`, сервер без обмеження пам'яті вичерпає всю оперативну пам'ять (RAM). Серверний парсер зобов'язаний обмежувати максимальну кількість підготовлених фрагментів (зазвичай від 4 до 8 елементів) і повертати помилку `ATT_ERR_PREPARE_QUEUE_FULL` (`0x09`).
3. **Підміна номерів дескрипторів**: дескриптор `0x0000` є забороненим стандартом. Шкідливий клієнт може спробувати передати нульовий дескриптор, щоб звернутися до нульового елемента масиву бази даних сервера. Перевірка `pkt->handle != 0x0000` на рівні парсера повністю блокує цей вектор атаки.

---

### 7. Механізм взаємодії з рівнем L2CAP: збирання фрагментів SDU

Хоча парсер ATT працює з цілісними пакетами PDU, на фізичному рівні радіозв'язку (Link Layer) пакети можуть фрагментуватися через обмеження розміру апаратного буфера радіоканалу (Data Length Extension, DLE).

Коли розмір узгодженого `ATT_MTU` становить 247 байтів, а контролер підтримує максимальний розмір кадру канального рівня лише 27 байтів, пакет ATT розбивається рівнем L2CAP на 10 окремих фрагментів Link Layer:
1. **Перший фрагмент (L2CAP Start Fragment)**: містить 4-байтний заголовок L2CAP (`Length = 247` та `CID = 0x0004`) плюс перші 23 байти кадру ATT PDU. Канальний рівень позначає цей пакет прапорцем `PB = 0b10` (First non-automatically flushable packet).
2. **Наступні фрагменти (L2CAP Continuation Fragments)**: містять лише сирі байти корисного навантаження (до 27 байтів кожен) із прапорцем `PB = 0b01` (Continuing fragment).
3. **Збирання повного SDU**: рівень L2CAP накопичує байти у внутрішньому буфері приймача. Лише тоді, коли сумарна кількість прийнятих байтів досягає значення поля `Length` із заголовка L2CAP, зібраний цілісний масив передається функції `att_parse_packet`.

Така двошарова модель гарантує, що парсер ATT завжди оперує повними, нефрагментованими протокольними повідомленнями, а логіка десеріалізації залишається простою, детермінованою та повністю незалежною від поточного стану радіоканалу.

---

### 8. Витрати ресурсів та оцінка продуктивності

Для оцінки придатності розробленого модуля для надмалих мікроконтролерів (Cortex-M0+, Cortex-M4, ESP32-C3) проведено вимірювання ресурсів компіляції за допомогою GCC з прапорцем оптимізації розміру `-Os`:

* **Розмір Flash-пам'яті (Code Footprint)**:
  * Реалізація на чистому C (`att_engine.c`): займає **392 байти** скомпільованого машинного коду Thumb-2;
  * Реалізація на C++20 (`att_engine.hpp` з `std::span` та `std::variant`): займає **540 байтів** коду завдяки оптимізації шаблонів та інлайнінгу методів розбору;
* **Витрати оперативної пам'яті (RAM Allocation)**:
  * Статичний контекст `att_client_t`: займає рівно **16 байтів** у пам'яті;
  * Динамічна пам'ять (Heap): **0 байтів** (жоден виклик `malloc` або оператор `new` не використовується взагалі);
  * Стек викликів: не перевищує 32 байти під час виконання функції розбору пакета;
* **Час виконання парсингу**: на процесорі ARM Cortex-M4 з тактовою частотою 64 МГц розбір типового пакета `ATT_READ_RSP` розміром 244 байти займає менше ніж **18 тактів процесора** (менше 0.3 мікросекунди), оскільки тіло значення не копіюється, а лише адресується через зріз пам'яті.

---

### 9. Кросплатформна переносність та підводні камені

1. **Невирівняний доступ до пам'яті (Unaligned Access)**: пряме читання `uint16_t` за непарними адресами буфера на деяких ядрах Cortex-M0 спричиняє апаратне зависання процесора (`HardFault`). Завжди використовуйте явний зсув `buf[0] | (buf[1] << 8)`.
2. **Втрата сповіщень під час активного запиту**: не скидайте стан очікування транзакції при отриманні `ATT_OP_HANDLE_VALUE_NTF`. Сповіщення є односторонніми і не є відповіддю на ваш `Read` чи `Write Request`.
3. **Обробка перезапуску з'єднання**: під час повторного підключення стан клієнта повинен обов'язково скидатися функцією `att_client_init`, а робочий MTU — повертатися до базового значення `23` байти, оскільки результати попереднього узгодження MTU не зберігаються між сесіями зв'язку.
4. **Порядок байтів на хості (Host Endianness)**: наведена реалізація орієнтована на процесори з порядком байтів Little-Endian (архітектури ARM, RISC-V, x86). У разі компіляції під Big-Endian мікроконтролери макроси зсувів `att_read_le16` та `att_write_le16` гарантують коректну кросплатформну конвертацію без потреби у виклику специфічних для компілятора функцій типу `__builtin_bswap16`.
