# ⚙️ Реалізація брокера SSE з докачуванням та парсера кадрів WebSocket

У високонавантажених сервісах сповіщень головне навантаження припадає не на генерацію бізнес-подій, а на утримання десятків тисяч відкритих клієнтських каналів і коректну обробку мережевих збоїв.

Для практичного освоєння протоколів реалізуємо ключові компоненти шлюзу реального часу:
1. **Брокер Server-Sent Events (SSE)** з кільцевим буфером історії, який автоматично відновлює потік і досилає пропущені події за заголовком `Last-Event-ID`.
2. **Низькорівневий декодер та енкодер кадрів WebSocket (RFC 6455)**, який розбирає бітові прапорці, декодує змінну довжину, знімає XOR-маскування та виконує криптографічне узгодження рукостискання.
3. **Модуль перевірки та авторизації рукостискання**, що захищає шлюз від міжсайтового викрадення сокетів (*Cross-Site WebSocket Hijacking*).

## Архітектура брокера SSE з докачуванням

Клієнтське з'єднання SSE може обірватися будь-якої миті через таймаут проміжного маршрутизатора або перемикання мережі. Якщо сервер просто транслює нові події у сокет, під час розриву клієнт втратить частину повідомлень безповоротно.

Щоб гарантувати доставку без пропусків (семантика *at-least-once*), брокер утримує **кільцевий буфер** (англ. *ring buffer*) фіксованої місткості `N`. Кожна подія отримує монотонно зростаючий числовий ідентифікатор `id`. При перепідключенні клієнт надсилає заголовок `Last-Event-ID: K`. Брокер перевіряє свій буфер:
- якщо `K` знаходиться в межах збереженого вікна, брокер негайно відправляє всі події з номерами від `K + 1` до найновішої;
- якщо `K` вже витіснений із буфера (клієнт був офлайн занадто довго), брокер надсилає спеціальну подію синхронізації або повний знімок стану.

```
Кільцевий буфер подій (розмір = 4):
Позиції буфера:  [ 0 ]      [ 1 ]      [ 2 ]      [ 3 ]
Збережені id:    id: 104    id: 105    id: 106    id: 107  (найновіша)
Найстаріша доступна подія: 104

Клієнт надіслав Last-Event-ID = 105:
-> Брокер досилає з буфера події з id 106 та 107
-> Переводить клієнта в режим очікування нових подій у прямому ефірі
```

### Розрахунок пам'яті та розміру буфера

Розмір кільцевого буфера обирають з огляду на інтенсивність потоку подій `λ` (подій на секунду) та максимальний очікуваний час перепідключення клієнта `T_reconnect` (зазвичай від 3 до 15 секунд):

```
Мінімальна місткість буфера N = λ · T_reconnect
```

Для каналу котирувань із частотою 100 подій/с та вікном перепідключення 10 секунд буфер має містити щонайменше 1000 елементів. Якщо середня подія займає 256 байтів, один кільцевий буфер потребує лише 256 КБ оперативної пам'яті. У системі з тисячею незалежних каналів це складає близько 250 МБ, що цілком уміщається в пам'ять одного вузла.

### Обробка крайових випадків у буфері

1. **Клієнт відстає занадто сильно:** якщо `Last-Event-ID` менший за найстаріший `id` у буфері, досилати часткові дані не можна — це створить дірку в історії бізнес-логіки. Сервер повинен надіслати подію `event: resync` із повним дампом стану або вимогою перезавантажити інтерфейс.
2. **Переповнення лічильника ідентифікаторів:** 64-бітне ціле число `uint64_t` виключає ризик переповнення за весь час життя системи (при генерації мільйона подій на секунду лічильник вичерпається лише через 584 тисячі років).

## Бітова анатомія та рукостискання WebSocket

У протоколі WebSocket робота складається з двох послідовних фаз: HTTP-рукостискання з генерацією криптографічної відповіді та безпосередній обмін бінарними кадрами.

### Криптографічне рукостискання (Handshake)

Клієнт ініціює перехід на WebSocket звичайним HTTP-запитом:

```http
GET /chat HTTP/1.1
Host: server.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
Origin: https://example.com
```

Сервер зобов'язаний виконати перевірку заголовків:
1. Перевірити наявність `Upgrade: websocket` та `Connection: Upgrade` (без урахування регістру).
2. Перевірити версію протоколу `Sec-WebSocket-Version: 13`. Якщо версія не підтримується, сервер повертає статус `426 Upgrade Required` із заголовком `Sec-WebSocket-Version: 13`.
3. Перевірити заголовок `Origin`. Оскільки браузери надсилають куки автентифікації разом із запитом рукостискання, шлюз повинен перевіряти, що домен у полі `Origin` є дозволеним. Це критичний захист від атак *Cross-Site WebSocket Hijacking (CSWSH)*, коли зловмисний сайт відкриває WebSocket до API банку від імені авторизованого користувача.

4. Перевірити наявність прикладного підпротоколу `Sec-WebSocket-Protocol` (наприклад, `json`, `wamp.2.json` або `graphql-ws`). Якщо клієнт запитує конкретний підпротокол, а сервер його підтримує, сервер зобов'язаний повернути узгоджене ім'я у заголовку `Sec-WebSocket-Protocol` відповіді `101 Switching Protocols`. Це дозволяє клієнту й серверу домовитися про формат прикладних повідомлень ще на етапі транспортного рукостискання, уникаючи зайвих обмінів службовими повідомленнями після встановлення сокета.
5. Обробити розширення транспорту `Sec-WebSocket-Extensions` (зокрема `permessage-deflate` для стиснення корисного навантаження алгоритмом DEFLATE). Якщо розширення прийнято, сервер активує використання біта `RSV1` у заголовках кадрів для позначення стиснених блоків.

Після перевірки сервер зчитує 24-символьний рядок `Sec-WebSocket-Key`, конкатенує його зі стандартним магічним GUID `258EAFA5-E914-47DA-95CA-C5AB0DC85B11`, обчислює 160-бітний геш SHA-1 і закодує результат у Base64:

```
Key:         dGhlIHNhbXBsZSBub25jZQ==
GUID:        258EAFA5-E914-47DA-95CA-C5AB0DC85B11
Конкатенація: dGhlIHNhbXBsZSBub25jZQ==258EAFA5-E914-47DA-95CA-C5AB0DC85B11
SHA-1 (hex): b3 7a 4f 2c c0 62 4f 16 90 d6 46 06 cf 38 59 45 b2 be c4 ea
Base64:      s3pPLMBiTxaQ1kYGzzhZRbK+xOo=
```

Сервер повертає клієнтові статус `101 Switching Protocols` із заголовком `Sec-WebSocket-Accept: s3pPLMBiTxaQ1kYGzzhZRbK+xOo=`. Будь-яка невідповідність цього рядка змушує клієнт негайно розірвати TCP-з'єднання.

### Формат заголовка кадру (RFC 6455)

Після успішного рукостискання сокет перемикається у режим кадрового обміну:
- **FIN (1 біт):** ознака завершального кадру фрагментованого повідомлення (1 — останній або єдиний кадр, 0 — передача продовжується).
- **RSV1, RSV2, RSV3 (по 1 біту):** зарезервовано для узгоджених розширень (наприклад, компресії `permessage-deflate`). Якщо розширення не узгоджені, будь-який ненульовий біт є фатальною помилкою протоколу (код 1002).
- **Opcode (4 біти):** код операції (`0x1` — текст UTF-8, `0x2` — бінарні дані, `0x8` — закриття, `0x9` — Ping, `0xA` — Pong).
- **MASK (1 біт):** прапорець маскування. Кадри від клієнта до сервера **обов'язково** мають `MASK = 1`. Кадри від сервера до клієнта **завжди** мають `MASK = 0`.
- **Payload len (7 бітів):** якщо значення `0..125`, це точна довжина тіла. Якщо `126`, наступні 2 байти містять 16-бітне беззнакове число у мережевому порядку байтів (*big-endian*). Якщо `127`, наступні 8 байтів містять 64-бітне число.
- **Masking-key (4 байти):** присутній тільки якщо `MASK = 1`. Використовується для побайтового зняття маски операцією XOR.

### Механізм XOR-маскування та векторна оптимізація

Маскування захищає проміжні кешуючі проксі-сервери від підміни запитів. Формула зняття маски з байта за індексом `i`:

```
unmasked_byte[i] = raw_byte[i] ⊕ mask_key[i mod 4]
```

Побайтова операція XOR створює помітний оверхед процесора на гігабітних потоках. Для оптимізації 4-байтовий ключ дублюють у 64-бітне машинне слово:

```
uint64_t mask64 = ((uint64_t)mask32 << 32) | mask32;
```

Після цього маску знімають блоками по 8 байтів за одну інструкцію процесора, а решту 1–7 байтів на кінці обробляють скалярним циклом. Сучасні сервери з підтримкою інструкцій AVX2 або ARM NEON використовують 256-бітні векторні регістри, обробляючи по 32 байти за один такт.

## Програмна реалізація

Наведемо повну реалізацію брокера SSE з кільцевим буфером і декодера/енкодера WebSocket мовами C та C++. Обидва варіанти містять повноцінну логіку буферизації, розбору змінної довжини заголовка та безпечної роботи з пам'яттю.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <optional>
#include <span>
#include <cstdint>
#include <cstring>
#include <algorithm>

// ═════════════════════════════════════════════════════════════════════════════
// 1. БРОКЕР SERVER-SENT EVENTS (SSE) З КІЛЬЦЕВИМ БУФЕРОМ
// ═════════════════════════════════════════════════════════════════════════════

struct SseEvent {
    uint64_t id{0};
    std::string event_type;
    std::string data;

    // Форматування події у канонічний текстовий формат SSE
    [[nodiscard]] std::string serialize() const {
        std::string out;
        out.reserve(data.size() + event_type.size() + 64);
        out += "id: " + std::to_string(id) + "\n";
        if (!event_type.empty()) {
            out += "event: " + event_type + "\n";
        }
        out += "data: " + data + "\n\n";
        return out;
    }
};

class SseRingBuffer {
public:
    explicit SseRingBuffer(size_t capacity)
        : capacity_(capacity), buffer_(capacity), head_(0), count_(0), next_id_(1) {}

    // Додавання нової події до кільцевого буфера
    uint64_t push_event(std::string_view event_type, std::string_view data) {
        uint64_t current_id = next_id_++;
        size_t index = (head_ + count_) % capacity_;

        buffer_[index] = SseEvent{
            .id = current_id,
            .event_type = std::string(event_type),
            .data = std::string(data)
        };

        if (count_ < capacity_) {
            count_++;
        } else {
            head_ = (head_ + 1) % capacity_; // Витіснення найстарішої події
        }
        return current_id;
    }

    // Отримання пропущених подій після last_seen_id
    [[nodiscard]] std::vector<SseEvent> get_events_since(uint64_t last_seen_id) const {
        std::vector<SseEvent> missed;
        if (count_ == 0) return missed;

        uint64_t oldest_id = buffer_[head_].id;
        uint64_t newest_id = buffer_[(head_ + count_ - 1) % capacity_].id;

        // Якщо клієнт уже бачив найновіше
        if (last_seen_id >= newest_id) return missed;

        // Визначаємо зміщення старту досилки
        size_t start_offset = 0;
        if (last_seen_id >= oldest_id) {
            start_offset = static_cast<size_t>(last_seen_id - oldest_id + 1);
        }

        for (size_t i = start_offset; i < count_; ++i) {
            missed.push_back(buffer_[(head_ + i) % capacity_]);
        }
        return missed;
    }

    [[nodiscard]] size_t size() const noexcept { return count_; }
    [[nodiscard]] uint64_t newest_id() const noexcept { return next_id_ - 1; }

private:
    size_t capacity_;
    std::vector<SseEvent> buffer_;
    size_t head_;
    size_t count_;
    uint64_t next_id_;
};

// ═════════════════════════════════════════════════════════════════════════════
// 2. ДЕКОДЕР ТА ЕНКОДЕР КАДРІВ WEBSOCKET (RFC 6455)
// ═════════════════════════════════════════════════════════════════════════════

enum class WsOpcode : uint8_t {
    Continuation = 0x0,
    Text         = 0x1,
    Binary       = 0x2,
    Close        = 0x8,
    Ping         = 0x9,
    Pong         = 0xA
};

struct WsFrame {
    bool fin{false};
    WsOpcode opcode{WsOpcode::Text};
    bool masked{false};
    std::vector<uint8_t> payload;
};

class WsFrameParser {
public:
    enum class ParseStatus {
        Ok,
        NeedMoreData,
        ProtocolError
    };

    // Розбір сирого буфера байтів
    static std::pair<ParseStatus, std::optional<WsFrame>> parse(
        std::span<const uint8_t> input, size_t& bytes_consumed
    ) {
        bytes_consumed = 0;
        if (input.size() < 2) {
            return {ParseStatus::NeedMoreData, std::nullopt};
        }

        uint8_t byte0 = input[0];
        uint8_t byte1 = input[1];

        bool fin = (byte0 & 0x80) != 0;
        uint8_t rsv = (byte0 & 0x70) >> 4;
        if (rsv != 0) {
            // RSV біти не узгоджені — критична помилка протоколу
            return {ParseStatus::ProtocolError, std::nullopt};
        }

        auto opcode = static_cast<WsOpcode>(byte0 & 0x0F);
        bool masked = (byte1 & 0x80) != 0;
        uint64_t payload_len = byte1 & 0x7F;

        size_t header_len = 2;

        if (payload_len == 126) {
            if (input.size() < header_len + 2) {
                return {ParseStatus::NeedMoreData, std::nullopt};
            }
            payload_len = (static_cast<uint64_t>(input[2]) << 8) | input[3];
            header_len += 2;
        } else if (payload_len == 127) {
            if (input.size() < header_len + 8) {
                return {ParseStatus::NeedMoreData, std::nullopt};
            }
            payload_len = 0;
            for (size_t i = 0; i < 8; ++i) {
                payload_len = (payload_len << 8) | input[header_len + i];
            }
            header_len += 8;
        }

        uint8_t mask_key[4] = {0};
        if (masked) {
            if (input.size() < header_len + 4) {
                return {ParseStatus::NeedMoreData, std::nullopt};
            }
            std::memcpy(mask_key, input.data() + header_len, 4);
            header_len += 4;
        }

        if (input.size() < header_len + payload_len) {
            return {ParseStatus::NeedMoreData, std::nullopt};
        }

        WsFrame frame;
        frame.fin = fin;
        frame.opcode = opcode;
        frame.masked = masked;
        frame.payload.resize(payload_len);

        const uint8_t* payload_src = input.data() + header_len;
        for (size_t i = 0; i < payload_len; ++i) {
            if (masked) {
                frame.payload[i] = payload_src[i] ^ mask_key[i % 4];
            } else {
                frame.payload[i] = payload_src[i];
            }
        }

        bytes_consumed = header_len + payload_len;
        return {ParseStatus::Ok, frame};
    }

    // Складання серверного кадру (завжди без маски)
    static std::vector<uint8_t> build_server_frame(
        WsOpcode opcode, std::span<const uint8_t> payload, bool fin = true
    ) {
        std::vector<uint8_t> out;
        uint8_t byte0 = (fin ? 0x80 : 0x00) | (static_cast<uint8_t>(opcode) & 0x0F);
        out.push_back(byte0);

        size_t len = payload.size();
        if (len <= 125) {
            out.push_back(static_cast<uint8_t>(len)); // MASK = 0
        } else if (len <= 0xFFFF) {
            out.push_back(126);
            out.push_back(static_cast<uint8_t>((len >> 8) & 0xFF));
            out.push_back(static_cast<uint8_t>(len & 0xFF));
        } else {
            out.push_back(127);
            for (int i = 7; i >= 0; --i) {
                out.push_back(static_cast<uint8_t>((len >> (i * 8)) & 0xFF));
            }
        }

        out.insert(out.end(), payload.begin(), payload.end());
        return out;
    }
};
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

/* ═════════════════════════════════════════════════════════════════════════════
 * 1. БРОКЕР SERVER-SENT EVENTS (SSE) З КІЛЬЦЕВИМ БУФЕРОМ НА C
 * ═════════════════════════════════════════════════════════════════════════════ */

#define MAX_EVENT_DATA 1024
#define MAX_EVENT_NAME 64

typedef struct {
    uint64_t id;
    char event_type[MAX_EVENT_NAME];
    char data[MAX_EVENT_DATA];
} sse_event_t;

typedef struct {
    sse_event_t *events;
    size_t capacity;
    size_t head;
    size_t count;
    uint64_t next_id;
} sse_ring_buffer_t;

sse_ring_buffer_t* sse_buffer_create(size_t capacity) {
    sse_ring_buffer_t *rb = (sse_ring_buffer_t*)malloc(sizeof(sse_ring_buffer_t));
    if (!rb) return NULL;
    rb->events = (sse_event_t*)calloc(capacity, sizeof(sse_event_t));
    if (!rb->events) {
        free(rb);
        return NULL;
    }
    rb->capacity = capacity;
    rb->head = 0;
    rb->count = 0;
    rb->next_id = 1;
    return rb;
}

void sse_buffer_free(sse_ring_buffer_t *rb) {
    if (rb) {
        free(rb->events);
        free(rb);
    }
}

uint64_t sse_buffer_push(sse_ring_buffer_t *rb, const char *event_type, const char *data) {
    uint64_t current_id = rb->next_id++;
    size_t index = (rb->head + rb->count) % rb->capacity;

    rb->events[index].id = current_id;
    strncpy(rb->events[index].event_type, event_type ? event_type : "", MAX_EVENT_NAME - 1);
    rb->events[index].event_type[MAX_EVENT_NAME - 1] = '\0';
    strncpy(rb->events[index].data, data ? data : "", MAX_EVENT_DATA - 1);
    rb->events[index].data[MAX_EVENT_DATA - 1] = '\0';

    if (rb->count < rb->capacity) {
        rb->count++;
    } else {
        rb->head = (rb->head + 1) % rb->capacity; /* витіснення найстарішої */
    }
    return current_id;
}

/* Форматування події у вихідний рядок */
int sse_format_event(const sse_event_t *ev, char *dest, size_t max_len) {
    if (ev->event_type[0] != '\0') {
        return snprintf(dest, max_len, "id: %llu\nevent: %s\ndata: %s\n\n",
                        (unsigned long long)ev->id, ev->event_type, ev->data);
    }
    return snprintf(dest, max_len, "id: %llu\ndata: %s\n\n",
                    (unsigned long long)ev->id, ev->data);
}

/* ═════════════════════════════════════════════════════════════════════════════
 * 2. ДЕКОДЕР КАДРІВ WEBSOCKET (RFC 6455) НА C
 * ═════════════════════════════════════════════════════════════════════════════ */

typedef enum {
    WS_OP_CONTINUATION = 0x0,
    WS_OP_TEXT         = 0x1,
    WS_OP_BINARY       = 0x2,
    WS_OP_CLOSE        = 0x8,
    WS_OP_PING         = 0x9,
    WS_OP_PONG         = 0xA
} ws_opcode_t;

typedef enum {
    WS_PARSE_OK = 0,
    WS_PARSE_NEED_MORE_DATA = 1,
    WS_PARSE_PROTOCOL_ERROR = 2
} ws_parse_status_t;

typedef struct {
    bool fin;
    ws_opcode_t opcode;
    bool masked;
    uint8_t *payload;
    size_t payload_len;
} ws_frame_t;

ws_parse_status_t ws_parse_frame(
    const uint8_t *buf, size_t buf_len,
    ws_frame_t *out_frame, size_t *bytes_consumed
) {
    *bytes_consumed = 0;
    if (buf_len < 2) return WS_PARSE_NEED_MORE_DATA;

    uint8_t byte0 = buf[0];
    uint8_t byte1 = buf[1];

    bool fin = (byte0 & 0x80) != 0;
    uint8_t rsv = (byte0 & 0x70) >> 4;
    if (rsv != 0) return WS_PARSE_PROTOCOL_ERROR;

    ws_opcode_t opcode = (ws_opcode_t)(byte0 & 0x0F);
    bool masked = (byte1 & 0x80) != 0;
    uint64_t payload_len = byte1 & 0x7F;
    size_t header_len = 2;

    if (payload_len == 126) {
        if (buf_len < header_len + 2) return WS_PARSE_NEED_MORE_DATA;
        payload_len = ((uint64_t)buf[2] << 8) | buf[3];
        header_len += 2;
    } else if (payload_len == 127) {
        if (buf_len < header_len + 8) return WS_PARSE_NEED_MORE_DATA;
        payload_len = 0;
        for (size_t i = 0; i < 8; ++i) {
            payload_len = (payload_len << 8) | buf[header_len + i];
        }
        header_len += 8;
    }

    uint8_t mask_key[4] = {0};
    if (masked) {
        if (buf_len < header_len + 4) return WS_PARSE_NEED_MORE_DATA;
        memcpy(mask_key, buf + header_len, 4);
        header_len += 4;
    }

    if (buf_len < header_len + payload_len) {
        return WS_PARSE_NEED_MORE_DATA;
    }

    out_frame->fin = fin;
    out_frame->opcode = opcode;
    out_frame->masked = masked;
    out_frame->payload_len = (size_t)payload_len;
    out_frame->payload = (uint8_t*)malloc(out_frame->payload_len + 1);
    if (!out_frame->payload) return WS_PARSE_PROTOCOL_ERROR;

    const uint8_t *src = buf + header_len;
    for (size_t i = 0; i < out_frame->payload_len; ++i) {
        out_frame->payload[i] = masked ? (src[i] ^ mask_key[i % 4]) : src[i];
    }
    out_frame->payload[out_frame->payload_len] = '\0'; /* зручність для тексту */

    *bytes_consumed = header_len + (size_t)payload_len;
    return WS_PARSE_OK;
}
```
:::

## Покроковий аналіз роботи та інженерні пастки

Розглянемо детально, які інженерні виклики виникають під час експлуатації парсера та буфера у виробничому середовищі під реальним навантаженням.

### 1. Фрагментація кадру в потоковому сокеті TCP

Мережевий протокол TCP є потоковим транспортом без збереження меж повідомлень. Якщо клієнт відправляє WebSocket-кадр розміром 64 КБ, операційна система може доставити його у застосунок кількома десятками фрагментів довільного розміру (наприклад, по 1460 байтів — типовий розмір MSS для мереж Ethernet).

Парсер реалізований як **потоковий автомат без стану** (англ. *stateless streaming parser*):
- Якщо у вхідному буфері менше 2 байтів, функція повертає `NeedMoreData` з нульовим споживанням байтів (`bytes_consumed = 0`).
- Якщо заголовок вказує довжину 126 або 127, парсер перевіряє наявність додаткових 2 чи 8 байтів розширеного поля довжини.
- Якщо заголовок розібрано повністю, але все тіло кадру ще не надійшло, парсер знову сигналізує `NeedMoreData`. Викликач залишає всі непрочитані байти у буфері й повертається до очікування події від epoll.

Такий підхід виключає копіювання недочитаних даних і забезпечує стійкість до будь-якої фрагментації пакетів.

### 2. Керівні кадри проти інформаційних

Згідно з RFC 6455, кадри діляться на дві суворі категорії:
- **Інформаційні (Data Frames, коди 0x1 Text, 0x2 Binary, 0x0 Continuation):** несуть корисне навантаження застосунку, можуть мати гігабайтні розміри та підтримують розбиття на кілька фрагментів (кадри з `FIN = 0` та наступні кадри продовження з кодом `0x0`).
- **Керівні (Control Frames, коди 0x8 Close, 0x9 Ping, 0xA Pong):** призначені для управління станом з'єднання.

Для керівних кадрів стандарт встановлює три жорсткі обмеження:
1. Максимальна довжина тіла керівного кадру — **не більше 125 байтів** (довжина завжди 7-бітна, поля 126 та 127 заборонені).
2. Керівний кадр **ніколи не фрагментується** (`FIN = 1` обов'язковий). Будь-який керівний кадр із `FIN = 0` є фатальною помилкою протоколу.
3. Керівний кадр **може вклинюватися всередину фрагментованого інформаційного повідомлення**. Якщо сервер отримує послідовність `[Text FIN=0] -> [Ping FIN=1] -> [Continuation FIN=1]`, він зобов'язаний негайно відповісти кадровим `Pong`, не скидаючи акумулятор незавершеного текстового повідомлення.

### 3. Процедура закриття з'єднання (Close Handshake)

Згідно з RFC 6455, коректне закриття сокета вимагає двостороннього узгодження:
- Сторона-ініціатор надсилає керівний кадр Close (`opcode = 0x8`). Перші два байти тіла містять 16-бітний числовий код стану (наприклад, `1000 Normal Closure` або `1001 Going Away`), за якими слідує опціональне текстове пояснення у форматі UTF-8.
- Одержувач кадру Close зобов'язаний відправити у відповідь свій власний кадр Close і лише після цього закрити підлеглий TCP-сокет.
- Якщо сокет обірвався раптово без попереднього обміну кадрами закриття, клієнтський API реєструє статус `1006 Abnormal Closure`.

### 4. Захист від вичерпання пам'яті (Memory Bombs)

Зловмисний клієнт може надіслати кадр із заголовком `FIN = 0` або `payload_len = 0xFFFFFFFFFFFFFFFF` (16 ексабайтів), змушуючи сервер виділити гігабайти пам'яті під буфер збирання.

У промисловому шлюзі обов'язково встановлюють ліміти:
- `MAX_FRAME_SIZE` (наприклад, 1 МБ) — якщо `payload_len` перевищує цю межу, сервер негайно розриває з'єднання з кодом `1009 Message Too Big`.
- `MAX_MESSAGE_SIZE` (наприклад, 8 МБ) — сумарний ліміт для всіх фрагментів одного логічного повідомлення.
- Обмеження часу збирання фрагментованого повідомлення (наприклад, не більше 30 секунд між першим кадром з `FIN = 0` та завершальним кадром). Якщо клієнт затягує передачу, акумулятор скидається, а сокет закривається.

### 5. Зворотний тиск (Backpressure) та стратегії скидання при повільному клієнті

Якщо сервер генерує події зі швидкістю 1000 повідомлень/с, а клієнт працює через повільну мобільну мережу 2G і вичитує сокет зі швидкістю 50 повідомлень/с, вихідний буфер ядра Linux (`SO_SNDBUF`) миттєво переповниться.

При використанні неблокуючих сокетів виклик `send()` поверне помилку `EAGAIN` або `EWOULDBLOCK`. Сервер має два варіанти поведінки:
1. **Черга на рівні процесу з пороговим витісненням:** зберігати невідправлені події в пам'яті до певної межі (наприклад, 1000 елементів), після чого примусово закрити сокет як завислий з кодом `1008 Policy Violation`.
2. **Пропуск проміжних оновлень (Conflation):** для біржових цін або координат транспорту замінювати застарілі значення в черзі найновішими, відправляючи клієнтові лише актуальний зріз стану.

### 6. Інтеграція з циклом подій (epoll) та таймерами пульсу

У системах, що обслуговують 50 000 одночасних підключень, виділення окремого системного потоку на кожне з'єднання (*thread-per-connection*) витратить понад 400 ГБ пам'яті лише на системні стеки потоків. Тому пуш-сервери будуються виключно на неблокуючому мультиплексуванні вводу-виводу:

```
epoll_create1(0) -> epoll_ctl(EPOLL_CTL_ADD, client_fd, EPOLLIN | EPOLLET)
```

Кожне підключення зв'язується з таймером неактивності (*inactivity timer*):
- Якщо від клієнта немає даних понад 30 секунд, сервер надсилає кадр `Ping` (`opcode = 0x9`).
- Якщо клієнт не відповів кадром `Pong` (`opcode = 0xA`) протягом 10 секунд, сокет вважається «напіввідкритим» (*half-open*), негайно закривається викликом `close(fd)`, а ресурси буфера повертаються в пул.

Це захищає ядро операційної системи від нагромадження сокетів-привидів, коли клієнтський пристрій раптово втратив живлення або вийшов із зони покриття без відправлення завершального TCP-пакета `FIN`.

### 7. Векторизоване розсилання (Scatter-Gather I/O)

Коли бізнес-подію потрібно розіслати тисячі підписників однієї кімнати, наївний цикл по сокетах із викликом `send()` на кожен дескриптор витрачає тисячі системних викликів і створює гігантський оверхед контекстних перемикань процесора.

Для оптимізації розсилання застосовують системний виклик `writev()` або `sendmsg()` із векторними масивами `struct iovec`. Подія кодується у WebSocket-кадр один раз у спільній пам'яті, після чого вказівник на готовий буфер передається ядру для масового копіювання у сокети підписників, досягаючи пропускної здатності в мільйони повідомлень на секунду на одному фізичному сервері.

### 8. Керування пулом пам'яті та кеш-лініями

При 100 000 постійних підключень часті динамічні алокації `malloc`/`free` для кожного кадру призводять до фрагментації купи та деградації продуктивності алокатора пам'яті.

Для запобігання деградації впроваджують арени пам'яті та вирівнювання структур:
- Кожне з'єднання утримує фіксовані блоки читання та запису (наприклад, по 4 КБ), виділені з єдиного масиву при старті процесу.
- Структури стану клієнтів вирівнюються за розміром лінії кешу процесора (64 байти на архітектурах x86-64 та ARM64) за допомогою специфікатора `alignas(64)`. Це виключає явище хибного розділення пам'яті (*false sharing*), коли робочі потоки epoll на різних ядрах конкурують за одну лінію кешу L1/L2.
- Тіла великих широкомовних повідомлень алокуються з глобального пулу сторінок із лічильником посилань (*reference counting*). Це дозволяє транслювати одне й те саме повідомлення тисячам сокетів без створення локальних копій у просторі користувача.

### 9. Налаштування проксі-серверів (Nginx та HAProxy)

Перед шлюзом застосунку зазвичай розміщують зворотний проксі-сервер для термінації TLS-сертифікатів. Якщо проксі налаштовано некоректно, стрімінг зламається.

Типова конфігурація для Nginx:

```nginx
location /events {
    proxy_pass http://backend_sse;
    proxy_set_header Connection '';
    proxy_http_version 1.1;
    proxy_buffering off;
    proxy_cache off;
    proxy_read_timeout 24h;
    chunked_transfer_encoding off;
}

location /ws {
    proxy_pass http://backend_ws;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 3600s;
}
```

Ключова директива `proxy_buffering off` для SSE запобігає затримці подій у внутрішньому 4-кілобайтовому буфері Nginx, гарантуючи миттєву доставку кожного фрейму клієнтові.

### 10. Тестування та валідація за допомогою Autobahn Testsuite

Для перевірки відповідності сервера вимогам RFC 6455 індустріальним стандартом є пакет **Autobahn Testsuite** (понад 500 автоматизованих тестів на безпеку та сумісність).

Він перевіряє найсуворіші крайові випадки:
- Коректність валідації UTF-8 у текстових кадрах (якщо хоча б один байт порушує кодування UTF-8, сервер зобов'язаний закрити сокет із кодом `1007 Invalid Frame Payload`).
- Дзеркальне повернення корисного навантаження у кадрах Ping -> Pong.
- Миттєве відхилення клієнтських кадрів без маски (`MASK = 0`) із кодом `1002 Protocol Error`.
- Заборону фрагментації для керівних кадрів і контроль максимальної довжини у 125 байтів.

### 11. Наскрізний життєвий цикл сесії

Розглянемо часову шкалу обслуговування клієнта на практичному прикладі біржового термінала:

```
[Час t = 0.00с] Клієнт відкриває GET /stream (SSE). Сервер призначає клієнтові буфер і транслює події id: 101, 102, 103.
[Час t = 4.10с] Користувач заходить у ліфт; з'єднання обривається на рівні TCP.
[Час t = 4.15с] Сервер генерує нові події id: 104, 105, 106, записуючи їх у SseRingBuffer.
[Час t = 8.50с] Клієнт відновлює мережу й надсилає запит GET /stream (Last-Event-ID: 103).
[Час t = 8.52с] Сервер викликає get_events_since(103), знаходить події 104, 105, 106 і миттєво відправляє їх пачкою.
[Час t = 8.55с] Потік переходить у синхронний режим очікування нових подій id >= 107.
```

Завдяки кільцевому буферу біржовий термінал не втратив жодної зміни ціни, а користувач навіть не помітив тимчасового збою зв'язку.
