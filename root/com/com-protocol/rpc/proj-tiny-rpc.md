# ⚙️ Реалізація компактного двійкового RPC-рушія з кодуванням Varint

Коли для вбудованих систем, мікроконтролерів (STM32, ESP32) або високопродуктивного міжпроцесного обміну (IPC) на базі спільної пам'яті gRPC є надто важким через залежність від стека HTTP/2, динамічних виділень пам'яті та важких бібліотек парсингу, базові принципи RPC реалізують на чистому двійковому транспорті. Цей проєкт демонструє мінімальний діючий каркас RPC: серіалізатор чисел змінної довжини Varint, двійковий протокол кадрування із заголовком запиту, клієнтський стаб і серверний скелетон із таблицею диспетчеризації методів.

### Постановка задачі та архітектура повідомлень

Необхідно реалізувати механізм віддаленого виклику двох типізованих процедур:
1. `Method 1: Add(a, b)` — додавання двох 64-бітних цілих чисел;
2. `Method 2: GetStats(node_id)` — запит діагностичного стану вузла за числовим ідентифікатором.

Щоб мінімізувати накладні витрати на передачу, протокол відмовляється від текстових ключів JSON та фіксованих 8-байтових полів, використовуючи компактне кодування заголовка за принципом TLV (Tag-Length-Value).

Формат двійкового кадру в мережі складається з чотирьох числових полів змінної довжини та тіла повідомлення:

```
+----------------+------------------+-------------------+-------------------+-------------------+
| Call-ID (Var)  | Method-ID (Var)  | Status-Code (Var) | Payload-Len (Var) | Payload (Bytes)   |
+----------------+------------------+-------------------+-------------------+-------------------+
```

- `Call-ID` — беззнакове число для прив'язки відповіді до запиту в клієнтській черзі очікувань, що дозволяє асинхронно відправляти кілька паралельних запитів;
- `Method-ID` — унікальний числовий ідентифікатор викликаної процедури (у відповіді дублює значення запиту);
- `Status-Code` — статус виконання операції: `0` для успіху (`RPC_OK`), `1` для невідомого методу (`RPC_ERR_NOT_FOUND`), `2` для помилки аргументів (`RPC_ERR_INVALID_ARG`), `3` для помилки десеріалізації (`RPC_ERR_DECODE`);
- `Payload-Len` — кількість байтів корисного навантаження аргументів запиту або результату відповіді;
- `Payload` — сирі серіалізовані байти параметрів (числа, рядки або структури).

---

### Механізм роботи кодека Base-128 Varint

Числа змінної довжини дозволяють упакувати невеликі ідентифікатори (0..127) в один байт замість восьми.

1. **Кодування (`encode_varint`):**
   - Доки число більше або дорівнює `128` (`0x80`), молодші 7 бітів виділяються маскою `value & 0x7F`, об'єднуються зі встановленим старшим бітом продовження `| 0x80` і записуються в буфер.
   - Число зсувається вправо на 7 бітів: `value >>= 7`.
   - Останній залишок записується з нульовим 8-м бітом.
2. **Декодування (`decode_varint`):**
   - Зчитується байт за байтом. Нижні 7 бітів зсуваються вліво на поточне зміщення `shift` і додаються до акумулятора `result |= (byte & 0x7F) << shift`.
   - Якщо старший біт дорівнює нулю (`(byte & 0x80) == 0`), декодування числа успішно завершено.
   - Якщо `shift >= 64`, парсер фіксує переповнення та аварійно перериває читання для захисту пам'яті.

---

### Реалізація двійкового RPC-рушія

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#define RPC_OK 0
#define RPC_ERR_NOT_FOUND 1
#define RPC_ERR_INVALID_ARG 2
#define RPC_ERR_DECODE 3
#define MAX_VARINT_BYTES 10

/* ── 1. Кодек чисел змінної довжини Base-128 Varint ── */
size_t encode_varint(uint64_t value, uint8_t *out) {
    size_t i = 0;
    while (value >= 0x80) {
        out[i++] = (uint8_t)((value & 0x7F) | 0x80);
        value >>= 7;
    }
    out[i++] = (uint8_t)(value & 0x7F);
    return i;
}

bool decode_varint(const uint8_t *buf, size_t len, size_t *offset, uint64_t *val) {
    uint64_t result = 0;
    int shift = 0;
    size_t cur = *offset;

    while (cur < len) {
        uint8_t byte = buf[cur++];
        result |= (uint64_t)(byte & 0x7F) << shift;
        if ((byte & 0x80) == 0) {
            *offset = cur;
            *val = result;
            return true;
        }
        shift += 7;
        if (shift >= 64) return false; /* Захист від переповнення розрядності */
    }
    return false; /* Буфер закінчився раніше термінального байта */
}

/* ── 2. Структура RPC повідомлення ── */
typedef struct {
    uint64_t call_id;
    uint64_t method_id;
    uint64_t status;
    uint8_t  payload[256];
    size_t   payload_len;
} RpcMessage;

size_t serialize_rpc(const RpcMessage *msg, uint8_t *out) {
    size_t off = 0;
    off += encode_varint(msg->call_id, out + off);
    off += encode_varint(msg->method_id, out + off);
    off += encode_varint(msg->status, out + off);
    off += encode_varint(msg->payload_len, out + off);
    memcpy(out + off, msg->payload, msg->payload_len);
    return off + msg->payload_len;
}

bool deserialize_rpc(const uint8_t *buf, size_t len, RpcMessage *msg) {
    size_t off = 0;
    uint64_t plen = 0;
    if (!decode_varint(buf, len, &off, &msg->call_id)) return false;
    if (!decode_varint(buf, len, &off, &msg->method_id)) return false;
    if (!decode_varint(buf, len, &off, &msg->status)) return false;
    if (!decode_varint(buf, len, &off, &plen)) return false;
    if (off + plen > len || plen > sizeof(msg->payload)) return false;
    
    msg->payload_len = (size_t)plen;
    memcpy(msg->payload, buf + off, plen);
    return true;
}

/* ── 3. Серверна логіка та скелетон ── */
typedef uint64_t (*RpcHandler)(const uint8_t *req, size_t req_len, uint8_t *resp, size_t *resp_len);

uint64_t handle_add(const uint8_t *req, size_t req_len, uint8_t *resp, size_t *resp_len) {
    size_t off = 0;
    uint64_t a, b;
    if (!decode_varint(req, req_len, &off, &a) || !decode_varint(req, req_len, &off, &b)) {
        return RPC_ERR_INVALID_ARG;
    }
    uint64_t sum = a + b;
    *resp_len = encode_varint(sum, resp);
    return RPC_OK;
}

void server_dispatch(const uint8_t *in_buf, size_t in_len, uint8_t *out_buf, size_t *out_len) {
    RpcMessage req, resp;
    if (!deserialize_rpc(in_buf, in_len, &req)) {
        *out_len = 0;
        return;
    }

    resp.call_id = req.call_id;
    resp.method_id = req.method_id;
    resp.payload_len = 0;

    if (req.method_id == 1) { /* Метод 1: Add */
        resp.status = handle_add(req.payload, req.payload_len, resp.payload, &resp.payload_len);
    } else {
        resp.status = RPC_ERR_NOT_FOUND;
    }
    *out_len = serialize_rpc(&resp, out_buf);
}

/* ── 4. Клієнтський стаб ── */
bool rpc_client_add(uint64_t a, uint64_t b, uint64_t *result) {
    uint8_t tx_buf[512], rx_buf[512];
    RpcMessage req = { .call_id = 1001, .method_id = 1, .status = RPC_OK };
    
    /* Маршалінг параметрів у тіло запиту */
    req.payload_len = encode_varint(a, req.payload);
    req.payload_len += encode_varint(b, req.payload + req.payload_len);

    size_t tx_len = serialize_rpc(&req, tx_buf);
    size_t rx_len = 0;

    /* Емуляція транспорту через виклик сервера */
    server_dispatch(tx_buf, tx_len, rx_buf, &rx_len);

    /* Демаршалінг відповіді */
    RpcMessage resp;
    if (!deserialize_rpc(rx_buf, rx_len, &resp)) return false;
    if (resp.call_id != req.call_id || resp.status != RPC_OK) return false;

    size_t off = 0;
    return decode_varint(resp.payload, resp.payload_len, &off, result);
}

int main(void) {
    uint64_t res = 0;
    if (rpc_client_add(150, 350, &res)) {
        printf("C RPC Add(150, 350) returned: %llu\n", (unsigned long long)res);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <expected>
#include <unordered_map>
#include <functional>
#include <cstdint>
#include <cstring>

enum class RpcStatus : uint64_t {
    Ok = 0,
    NotFound = 1,
    InvalidArgument = 2,
    DecodeError = 3
};

struct RpcMessage {
    uint64_t call_id{0};
    uint64_t method_id{0};
    RpcStatus status{RpcStatus::Ok};
    std::vector<uint8_t> payload;
};

class VarintCodec {
public:
    static void encode(uint64_t value, std::vector<uint8_t>& out) {
        while (value >= 0x80) {
            out.push_back(static_cast<uint8_t>((value & 0x7F) | 0x80));
            value >>= 7;
        }
        out.push_back(static_cast<uint8_t>(value & 0x7F));
    }

    static std::expected<uint64_t, RpcStatus> decode(std::span<const uint8_t> buf, size_t& offset) {
        uint64_t result = 0;
        int shift = 0;
        while (offset < buf.size()) {
            uint8_t byte = buf[offset++];
            result |= static_cast<uint64_t>(byte & 0x7F) << shift;
            if ((byte & 0x80) == 0) {
                return result;
            }
            shift += 7;
            if (shift >= 64) return std::unexpected(RpcStatus::DecodeError);
        }
        return std::unexpected(RpcStatus::DecodeError);
    }
};

class RpcSerializer {
public:
    static std::vector<uint8_t> pack(const RpcMessage& msg) {
        std::vector<uint8_t> out;
        VarintCodec::encode(msg.call_id, out);
        VarintCodec::encode(msg.method_id, out);
        VarintCodec::encode(static_cast<uint64_t>(msg.status), out);
        VarintCodec::encode(msg.payload.size(), out);
        out.insert(out.end(), msg.payload.begin(), msg.payload.end());
        return out;
    }

    static std::expected<RpcMessage, RpcStatus> unpack(std::span<const uint8_t> buf) {
        size_t off = 0;
        auto cid = VarintCodec::decode(buf, off);
        auto mid = VarintCodec::decode(buf, off);
        auto st  = VarintCodec::decode(buf, off);
        auto len = VarintCodec::decode(buf, off);

        if (!cid || !mid || !st || !len) return std::unexpected(RpcStatus::DecodeError);
        if (off + *len > buf.size()) return std::unexpected(RpcStatus::DecodeError);

        RpcMessage msg;
        msg.call_id = *cid;
        msg.method_id = *mid;
        msg.status = static_cast<RpcStatus>(*st);
        msg.payload.assign(buf.begin() + off, buf.begin() + off + *len);
        return msg;
    }
};

/* ── 3. Диспетчер сервера та скелетон ── */
class RpcServer {
public:
    using Handler = std::function<std::expected<std::vector<uint8_t>, RpcStatus>(std::span<const uint8_t>)>;

    void register_handler(uint64_t method_id, Handler handler) {
        handlers_[method_id] = std::move(handler);
    }

    std::vector<uint8_t> dispatch(std::span<const uint8_t> request_bytes) {
        auto req = RpcSerializer::unpack(request_bytes);
        if (!req) return {};

        RpcMessage resp;
        resp.call_id = req->call_id;
        resp.method_id = req->method_id;

        auto it = handlers_.find(req->method_id);
        if (it == handlers_.end()) {
            resp.status = RpcStatus::NotFound;
        } else {
            auto res = it->second(req->payload);
            if (res) {
                resp.status = RpcStatus::Ok;
                resp.payload = std::move(*res);
            } else {
                resp.status = res.error();
            }
        }
        return RpcSerializer::pack(resp);
    }

private:
    std::unordered_map<uint64_t, Handler> handlers_;
};

/* ── 4. Клієнтський стаб для виклику арифметичних методів ── */
class CalculatorClient {
public:
    explicit CalculatorClient(RpcServer& server) : server_(server) {}

    std::expected<uint64_t, RpcStatus> add(uint64_t a, uint64_t b) {
        RpcMessage req;
        req.call_id = ++next_call_id_;
        req.method_id = 1; // Method Add
        VarintCodec::encode(a, req.payload);
        VarintCodec::encode(b, req.payload);

        auto wire_req = RpcSerializer::pack(req);
        auto wire_resp = server_.dispatch(wire_req);

        auto resp = RpcSerializer::unpack(wire_resp);
        if (!resp) return std::unexpected(RpcStatus::DecodeError);
        if (resp->status != RpcStatus::Ok) return std::unexpected(resp->status);

        size_t off = 0;
        return VarintCodec::decode(resp->payload, off);
    }

private:
    RpcServer& server_;
    uint64_t next_call_id_{0};
};

int main() {
    RpcServer server;
    server.register_handler(1, [](std::span<const uint8_t> req) -> std::expected<std::vector<uint8_t>, RpcStatus> {
        size_t off = 0;
        auto a = VarintCodec::decode(req, off);
        auto b = VarintCodec::decode(req, off);
        if (!a || !b) return std::unexpected(RpcStatus::InvalidArgument);

        std::vector<uint8_t> out;
        VarintCodec::encode(*a + *b, out);
        return out;
    });

    CalculatorClient client(server);
    auto sum = client.add(1024, 2048);
    if (sum) {
        std::cout << "C++ RPC Add(1024, 2048) = " << *sum << std::endl;
    }
    return 0;
}
```
:::

---

### Покрокове трасування байтів під час виклику

Простежимо точний вигляд двійкового потоку для виклику `Add(150, 350)` з ідентифікатором `Call-ID = 1001`:

1. **Пакування аргументів клієнта:**
   - Число `150` (`0x96`) кодується як Varint `0x96 0x01` (2 байти);
   - Число `350` (`0x015E`) кодується як Varint `0xDE 0x02` (2 байти);
   - Тіло корисного навантаження `Payload` містить 4 байти: `[0x96, 0x01, 0xDE, 0x02]`.
2. **Формування заголовка запиту:**
   - `Call-ID = 1001` кодується як `0xE9 0x07` (2 байти);
   - `Method-ID = 1` кодується як `0x01` (1 байт);
   - `Status-Code = 0` кодується як `0x00` (1 байт);
   - `Payload-Len = 4` кодується як `0x04` (1 байт).
   - **Загальний розмір пакета запиту:** рівно 9 байтів.
   - *Для порівняння:* еквівалентний JSON-запит `{"call_id":1001,"method":"Add","params":[150,350]}` важить 53 байти (майже в 6 разів більше).
3. **Обчислення на сервері:**
   - Сервер демаршалізує аргументи, обчислює суму `150 + 350 = 500` (`0x01F4`).
   - Число `500` пакується у Varint `0xF4 0x03` (2 байти).
4. **Формування відповіді:**
   - `Call-ID = 1001` (`0xE9 0x07`), `Method-ID = 1` (`0x01`), `Status-Code = 0` (`0x00`), `Payload-Len = 2` (`0x02`), `Payload` (`0xF4 0x03`).
   - **Загальний розмір пакета відповіді:** рівно 7 байтів.

---

### Пастки реалізації, безпека пам'яті та крайові випадки

1. **Атака нескінченного розкодування (Varint Bomb):**
   Зловмисник може надіслати потік байтів, у якому кожен байт має встановлений старший біт `0x80` (наприклад, `0xFF 0xFF 0xFF...`). Якщо функція декодування не перевіряє лічильник зсуву `shift < 64`, програма входить у нескінченний цикл або виконує невизначену поведінку при зсуві 64-бітного цілого на 64+ бітів. Перевірка `if (shift >= 64) return false;` є обов'язковою вимогою безпеки.

2. **Захист від переповнення буфера (Out-of-Bounds Check):**
   При читанні довжини `Payload-Len` значення може бути фальсифіковане (наприклад, заявлено `1 000 000` байтів при фактичному розмірі пакету в 20 байтів). Десеріалізатор зобов'язаний суворо перевіряти умову `off + plen <= len`, перш ніж звертатися до пам'яті, інакше виникає падіння процесу (Segmentation Fault) або витік неініціалізованої пам'яті ядра/стека назовні.

3. **Зіставлення Call-ID в асинхронному середовищі:**
   При передачі повідомлень через реальний TCP-сокет або чергу повідомлень сервер може обробляти повільні та швидкі запити паралельно. Відповідь на `Call-ID = 2` може прийти раніше, ніж відповідь на `Call-ID = 1`. Клієнтський стаб не має права припускати послідовний порядок відповідей: він повинен зберігати активні дескриптори викликів у геш-таблиці та шукати потрібний зворотний виклик за отриманим `Call-ID`.

4. **Розрив кадру на межі TCP-пакетів:**
   Потоковий сокет TCP не гарантує, що один виклик `send()` на клієнті відповідатиме одному виклику `recv()` на сервері. Якщо заголовок або тіло RPC-повідомлення розділилися між двома сегментами TCP, десеріалізатор повинен накопичувати байти в кільцевому буфері (Ring Buffer) до повного зчитування довжини `Payload-Len`, перш ніж передавати повідомлення диспетчеру скелетона.

5. **Ідіоматичні відмінності реалізацій C та C++:**
   У версії мовою C виділення пам'яті під буфери фіксоване (`uint8_t tx_buf[512]`), що ідеально для мікроконтролерів без динамічної купи, але накладає жорсткі межі на розмір повідомлення. Версія на C++23 спирається на `std::span` для неволодіючого безпечного перегляду пам'яті без зайвих копіювань, динамічні вектори `std::vector<uint8_t>` для гнучкого зростання розміру та тип `std::expected<T, RpcStatus>` для строгого повернення результату або коду помилки без винятків.
