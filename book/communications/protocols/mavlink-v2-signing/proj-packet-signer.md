# ⚙️ Реалізація рушія підпису та верифікації MAVLink 2

Розробка надійного зв'язку для автономних безпілотних систем вимагає безпомилкової реалізації криптографічного шару безпосередньо в контурі реального часу. Підпис повідомлень [MAVLink 2](book:communications/mavlink-packet) розв'язує фундаментальну задачу: захистити відкритий радіоканал телеметрії від активного зловмисника, здатного інжектувати підроблені накази або відтворювати перехоплені кадри керування. Цей проєкт розбирає повну, автономну та оптимізовану реалізацію рушія підпису та валідації пакетів, яку можна інтегрувати як у мікроконтролерні польотні прошивки на базі STM32, так і у високорівневі шлюзи телеметрії.

### Архітектура та етапи криптографічної обробки

Рушій підпису MAVLink 2 працює як проміжний шар між генератором бінарного кадру та фізичним драйвером передачі даних ([UART](book:communications/packet-design) або UDP-сокетом). Процес формування та перевірки підпису розбивається на чітко розмежовані фази:

```
[Вихідне повідомлення]
        │
        ▼
1. Застосування Zero-Trimming (відсікання нульових байтів у кінці payload)
        │
        ▼
2. Встановлення прапорця MAVLINK_IFLAG_SIGNED (0x01) у полі incompat_flags
        │
        ▼
3. Розрахунок контрольної суми CRC-16/MCRF4XX (включно із CRC_EXTRA)
        │
        ▼
4. Формування перших 7 байтів трейлера (Link ID + 48-бітний Timestamp)
        │
        ▼
5. Хешування: SHA-256(Secret_Key[32] + Header[10] + Payload[LEN] + CRC[2] + Link_ID[1] + Timestamp[6])
        │
        ▼
6. Обтинання хешу: копіювання перших 6 байтів SHA-256 у Signature Hash
        │
        ▼
[Готовий захищений кадр MAVLink 2 на дроті: Header + Payload + CRC + Trailer]
```

З боку приймача алгоритм виконує зворотні дії у суворій послідовності, де кожна наступна перевірка виконується лише після успішного проходження попередньої:

Спершу перевіряється стартовий байт кадру (`0xFD`) та наявність біта `0x01` у полі `incompat_flags`. Якщо біт піднято, розбірник очікує, що повна довжина пакета на 13 байтів більша за стандартну суму заголовка, корисних даних та двох байтів CRC.

Далі обчислюється контрольна сума кадру. Вона рахується від поля довжини `LEN` до кінця корисних даних `payload`, після чого до суми домішується байт `CRC_EXTRA` для перевірки узгодженості типів повідомлення. Якщо контрольна сума не збігається, пакет негайно знищується ще до виконання криптографічних функцій. Це захищає процесор від марного витрачання обчислювальних ресурсів на хешування випадково пошкодженого радіошумом сміття.

Після валідації CRC розбірник витягує з трейлера ідентифікатор каналу `link_id` та 48-бітний час `timestamp`. Виконується пошук сесії в таблиці активних потоків за триплетом `(sysid, compid, link_id)`. Отримане значення часу порівнюється зі збереженим: якщо вхідний час менший або рівний збереженому, пакет відхиляється як застарілий або як спроба повторного відтворення (replay attack).

Якщо перевірка часу успішна, приймач формує вхідний буфер із локального 256-бітного секретного ключа, отриманого кадру та перших 7 байтів трейлера, після чого розраховує SHA-256. Перші 6 байтів обчисленого хешу порівнюються з прийнятими байтами підпису за допомогою функції з постійним часом виконання (`constant-time comparison`), що запобігає атакам за сторонніми каналами через аналіз часу відгуку процесора.

Тільки у випадку повного збігу гешу стан потоку оновлюється новим значенням `timestamp`, а корисне навантаження передається до прикладного обробника команд.

### Повна реалізація рушія підпису: C та ідіоматичний C++

Нижче наведено самодостатній вихідний код рушія підпису. Реалізація містить вбудований компактний алгоритм SHA-256, макроси для роботи з 48-бітними цілими числами, керування таблицею потоків та функції підписання й валідації кадру.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAVLINK_STX_V2                0xFD
#define MAVLINK_IFLAG_SIGNED          0x01
#define MAVLINK_SIGNING_TRAILER_LEN   13
#define MAVLINK_MAX_SIGNING_STREAMS   16
#define MAVLINK_EPOCH_OFFSET_US       1420070400000000ULL

// Структура слота потоку для відстеження монотонного часу
typedef struct {
    uint8_t  link_id;
    uint8_t  sysid;
    uint8_t  compid;
    uint64_t last_timestamp;
    uint32_t last_activity_ms;
} mavlink_stream_entry_t;

// Контекст підпису MAVLink 2
typedef struct {
    uint8_t  secret_key[32];
    uint8_t  link_id;
    uint64_t current_timestamp;
    uint8_t  stream_count;
    mavlink_stream_entry_t streams[MAVLINK_MAX_SIGNING_STREAMS];
} mavlink_crypto_ctx_t;

// --- Вбудована оптимізована реалізація SHA-256 ---
typedef struct {
    uint32_t state[8];
    uint64_t bit_len;
    uint8_t  buffer[64];
} sha256_ctx_t;

static const uint32_t K[64] = {
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
};

#define ROR(x, n) (((x) >> (n)) | ((x) << (32 - (n))))
#define CH(x, y, z)  (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x, y, z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define EP0(x) (ROR(x, 2) ^ ROR(x, 13) ^ ROR(x, 22))
#define EP1(x) (ROR(x, 6) ^ ROR(x, 11) ^ ROR(x, 25))
#define SIG0(x) (ROR(x, 7) ^ ROR(x, 18) ^ ((x) >> 3))
#define SIG1(x) (ROR(x, 17) ^ ROR(x, 19) ^ ((x) >> 10))

static void sha256_transform(sha256_ctx_t *ctx, const uint8_t data[64]) {
    uint32_t a, b, c, d, e, f, g, h, w[64];
    for (int i = 0; i < 16; ++i) {
        w[i] = ((uint32_t)data[i*4] << 24) | ((uint32_t)data[i*4+1] << 16) |
               ((uint32_t)data[i*4+2] << 8)  | ((uint32_t)data[i*4+3]);
    }
    for (int i = 16; i < 64; ++i) {
        w[i] = SIG1(w[i-2]) + w[i-7] + SIG0(w[i-15]) + w[i-16];
    }
    a = ctx->state[0]; b = ctx->state[1]; c = ctx->state[2]; d = ctx->state[3];
    e = ctx->state[4]; f = ctx->state[5]; g = ctx->state[6]; h = ctx->state[7];
    for (int i = 0; i < 64; ++i) {
        uint32_t t1 = h + EP1(e) + CH(e, f, g) + K[i] + w[i];
        uint32_t t2 = EP0(a) + MAJ(a, b, c);
        h = g; g = f; f = e; e = d + t1;
        d = c; c = b; b = a; a = t1 + t2;
    }
    ctx->state[0] += a; ctx->state[1] += b; ctx->state[2] += c; ctx->state[3] += d;
    ctx->state[4] += e; ctx->state[5] += f; ctx->state[6] += g; ctx->state[7] += h;
}

static void sha256_init(sha256_ctx_t *ctx) {
    ctx->bit_len = 0;
    ctx->state[0] = 0x6a09e667; ctx->state[1] = 0xbb67ae85;
    ctx->state[2] = 0x3c6ef372; ctx->state[3] = 0xa54ff53a;
    ctx->state[4] = 0x510e527f; ctx->state[5] = 0x9b05688c;
    ctx->state[6] = 0x1f83d9ab; ctx->state[7] = 0x5be0cd19;
}

static void sha256_update(sha256_ctx_t *ctx, const uint8_t *data, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        ctx->buffer[(ctx->bit_len / 8) % 64] = data[i];
        ctx->bit_len += 8;
        if ((ctx->bit_len % 512) == 0) {
            sha256_transform(ctx, ctx->buffer);
        }
    }
}

static void sha256_final(sha256_ctx_t *ctx, uint8_t hash[32]) {
    size_t i = (ctx->bit_len / 8) % 64;
    ctx->buffer[i++] = 0x80;
    if (i > 56) {
        while (i < 64) ctx->buffer[i++] = 0x00;
        sha256_transform(ctx, ctx->buffer);
        i = 0;
    }
    while (i < 56) ctx->buffer[i++] = 0x00;
    for (int j = 7; j >= 0; --j) {
        ctx->buffer[56 + j] = (uint8_t)(ctx->bit_len >> ((7 - j) * 8));
    }
    sha256_transform(ctx, ctx->buffer);
    for (int j = 0; j < 8; ++j) {
        hash[j*4]   = (uint8_t)(ctx->state[j] >> 24);
        hash[j*4+1] = (uint8_t)(ctx->state[j] >> 16);
        hash[j*4+2] = (uint8_t)(ctx->state[j] >> 8);
        hash[j*4+3] = (uint8_t)(ctx->state[j]);
    }
}

// Побайтовий запис і читання 48-бітного цілого (Little-Endian)
static void put_uint48(uint8_t *p, uint64_t val) {
    p[0] = (uint8_t)(val >> 0);
    p[1] = (uint8_t)(val >> 8);
    p[2] = (uint8_t)(val >> 16);
    p[3] = (uint8_t)(val >> 24);
    p[4] = (uint8_t)(val >> 32);
    p[5] = (uint8_t)(val >> 40);
}

static uint64_t get_uint48(const uint8_t *p) {
    return ((uint64_t)p[0])       | (((uint64_t)p[1]) << 8)  |
           (((uint64_t)p[2]) << 16)| (((uint64_t)p[3]) << 24)|
           (((uint64_t)p[4]) << 32)| (((uint64_t)p[5]) << 40);
}

// Порівняння пам'яті з постійним часом виконання (Constant-Time)
static bool constant_time_memcmp6(const uint8_t *a, const uint8_t *b) {
    volatile uint8_t diff = 0;
    for (int i = 0; i < 6; ++i) {
        diff |= (a[i] ^ b[i]);
    }
    return (diff == 0);
}

// Ініціалізація контексту підпису
void mavlink_crypto_init(mavlink_crypto_ctx_t *ctx, const uint8_t key[32], uint8_t link_id, uint64_t start_ts) {
    memcpy(ctx->secret_key, key, 32);
    ctx->link_id = link_id;
    ctx->current_timestamp = start_ts;
    ctx->stream_count = 0;
    memset(ctx->streams, 0, sizeof(ctx->streams));
}

// Підписання вихідного кадру MAVLink 2
// packet_buf містить: Header(10B) + Payload(LEN) + CRC(2B)
// Функція додає 13 байтів трейлера та повертає новий загальний розмір
size_t mavlink_crypto_sign_packet(mavlink_crypto_ctx_t *ctx, uint8_t *packet_buf, size_t header_plus_payload_len) {
    // 1. Встановлюємо прапорець невідповідності SIGNED у заголовку
    packet_buf[2] |= MAVLINK_IFLAG_SIGNED; // incompat_flags — 3-й байт (зсув 2)

    // 2. Інкрементуємо локальний монотонний час
    ctx->current_timestamp++;

    // 3. Формуємо перші 7 байтів трейлера безпосередньо після CRC
    size_t trailer_offset = header_plus_payload_len + 2; // пропускаємо 2 байти CRC
    packet_buf[trailer_offset] = ctx->link_id;
    put_uint48(&packet_buf[trailer_offset + 1], ctx->current_timestamp);

    // 4. Обчислюємо SHA-256(Secret_Key + Packet_Bytes_Before_Signature)
    sha256_ctx_t sha;
    sha256_init(&sha);
    sha256_update(&sha, ctx->secret_key, 32);
    sha256_update(&sha, packet_buf, trailer_offset + 7); // весь пакет включно з link_id і timestamp

    uint8_t full_hash[32];
    sha256_final(&sha, full_hash);

    // 5. Записуємо перші 6 байтів гешу в поле Signature
    memcpy(&packet_buf[trailer_offset + 7], full_hash, 6);

    return trailer_offset + MAVLINK_SIGNING_TRAILER_LEN;
}

// Валідація вхідного кадру MAVLink 2
bool mavlink_crypto_verify_packet(mavlink_crypto_ctx_t *ctx, const uint8_t *packet_buf, size_t total_len, uint32_t now_ms) {
    if (total_len < 10 + 2 + MAVLINK_SIGNING_TRAILER_LEN) {
        return false; // Кадр занадто малий для вміщення підпису
    }
    if (packet_buf[0] != MAVLINK_STX_V2 || !(packet_buf[2] & MAVLINK_IFLAG_SIGNED)) {
        return false; // Не MAVLink v2 або біт підпису відсутній
    }

    uint8_t payload_len = packet_buf[1];
    size_t expected_total = 10 + payload_len + 2 + MAVLINK_SIGNING_TRAILER_LEN;
    if (total_len != expected_total) {
        return false; // Невідповідність розміру кадру
    }

    uint8_t sysid = packet_buf[5];
    uint8_t compid = packet_buf[6];
    size_t trailer_offset = 10 + payload_len + 2;
    uint8_t link_id = packet_buf[trailer_offset];
    uint64_t incoming_ts = get_uint48(&packet_buf[trailer_offset + 1]);
    const uint8_t *incoming_sig = &packet_buf[trailer_offset + 7];

    // Пошук слота потоку (sysid, compid, link_id)
    int stream_idx = -1;
    int oldest_idx = 0;
    uint32_t oldest_age = 0;

    for (int i = 0; i < ctx->stream_count; ++i) {
        if (ctx->streams[i].sysid == sysid &&
            ctx->streams[i].compid == compid &&
            ctx->streams[i].link_id == link_id) {
            stream_idx = i;
            break;
        }
        uint32_t age = now_ms - ctx->streams[i].last_activity_ms;
        if (age > oldest_age) {
            oldest_age = age;
            oldest_idx = i;
        }
    }

    // Перевірка монотонності часу
    if (stream_idx >= 0) {
        if (incoming_ts <= ctx->streams[stream_idx].last_timestamp) {
            return false; // Replay-атака: таймстемп не зріс!
        }
    }

    // Розрахунок очікуваного SHA-256
    sha256_ctx_t sha;
    sha256_init(&sha);
    sha256_update(&sha, ctx->secret_key, 32);
    sha256_update(&sha, packet_buf, trailer_offset + 7);

    uint8_t computed_hash[32];
    sha256_final(&sha, computed_hash);

    // Звірка підпису з постійним часом виконання
    if (!constant_time_memcmp6(computed_hash, incoming_sig)) {
        return false; // Підроблений або спотворений підпис!
    }

    // Оновлення таблиці стану потоків
    if (stream_idx < 0) {
        if (ctx->stream_count < MAVLINK_MAX_SIGNING_STREAMS) {
            stream_idx = ctx->stream_count++;
        } else {
            stream_idx = oldest_idx; // LRU заміщення
        }
        ctx->streams[stream_idx].sysid = sysid;
        ctx->streams[stream_idx].compid = compid;
        ctx->streams[stream_idx].link_id = link_id;
    }

    ctx->streams[stream_idx].last_timestamp = incoming_ts;
    ctx->streams[stream_idx].last_activity_ms = now_ms;

    return true; // Пакет автентичний та безпечний
}
```
```cpp
#include <array>
#include <span>
#include <vector>
#include <chrono>
#include <cstdint>
#include <algorithm>
#include <optional>

class MavlinkPacketSigner {
public:
    static constexpr uint8_t  kStxV2 = 0xFD;
    static constexpr uint8_t  kFlagSigned = 0x01;
    static constexpr size_t   kTrailerLen = 13;
    static constexpr size_t   kMaxStreams = 16;
    using KeyType = std::array<uint8_t, 32>;

    struct StreamEntry {
        uint8_t  link_id{0};
        uint8_t  sysid{0};
        uint8_t  compid{0};
        uint64_t last_timestamp{0};
        std::chrono::steady_clock::time_point last_seen{};
    };

    MavlinkPacketSigner(KeyType key, uint8_t link_id, uint64_t initial_timestamp)
        : secret_key_(key), link_id_(link_id), current_timestamp_(initial_timestamp) {}

    // Підписання вихідного пакета MAVLink v2
    std::vector<uint8_t> signPacket(std::span<const uint8_t> header_and_payload, uint16_t crc) {
        std::vector<uint8_t> frame;
        frame.reserve(header_and_payload.size() + 2 + kTrailerLen);
        
        // Копіюємо заголовок і корисні дані
        frame.insert(frame.end(), header_and_payload.begin(), header_and_payload.end());
        frame[2] |= kFlagSigned; // Виставляємо біт підпису в incompat_flags

        // Додаємо CRC-16 (Little-Endian)
        frame.push_back(static_cast<uint8_t>(crc & 0xFF));
        frame.push_back(static_cast<uint8_t>((crc >> 8) & 0xFF));

        // Формуємо трейлер: Link ID + Timestamp (48-bit)
        ++current_timestamp_;
        frame.push_back(link_id_);
        packUint48(frame, current_timestamp_);

        // Обчислюємо SHA-256 над [Secret Key] + [Frame Bytes Before Signature]
        auto hash = computeSha256(secret_key_, frame);

        // Додаємо перші 6 байтів гешу
        frame.insert(frame.end(), hash.begin(), hash.begin() + 6);
        return frame;
    }

    // Верифікація вхідного кадру
    [[nodiscard]] bool verifyPacket(std::span<const uint8_t> packet) {
        if (packet.size() < 10 + 2 + kTrailerLen || packet[0] != kStxV2 || !(packet[2] & kFlagSigned)) {
            return false;
        }

        const uint8_t payload_len = packet[1];
        const size_t expected_size = 10 + payload_len + 2 + kTrailerLen;
        if (packet.size() != expected_size) {
            return false;
        }

        const uint8_t sysid = packet[5];
        const uint8_t compid = packet[6];
        const size_t trailer_offset = 10 + payload_len + 2;
        const uint8_t incoming_link = packet[trailer_offset];
        const uint64_t incoming_ts = unpackUint48(packet.subspan(trailer_offset + 1, 6));

        // Перевірка монотонності часу в потоці
        auto stream_it = std::find_if(streams_.begin(), streams_.end(), [&](const StreamEntry& s) {
            return s.sysid == sysid && s.compid == compid && s.link_id == incoming_link;
        });

        if (stream_it != streams_.end() && incoming_ts <= stream_it->last_timestamp) {
            return false; // Відхилено: застарілий таймстемп або повтор!
        }

        // Обчислення очікуваного гешу SHA-256
        auto hash = computeSha256(secret_key_, packet.subspan(0, trailer_offset + 7));
        auto incoming_sig = packet.subspan(trailer_offset + 7, 6);

        if (!constantTimeEqual(incoming_sig, std::span<const uint8_t>(hash.data(), 6))) {
            return false; // Недійсний підпис
        }

        // Оновлення або реєстрація джерела в таблиці потоків
        auto now = std::chrono::steady_clock::now();
        if (stream_it != streams_.end()) {
            stream_it->last_timestamp = incoming_ts;
            stream_it->last_seen = now;
        } else {
            if (streams_.size() >= kMaxStreams) {
                // LRU витіснення
                auto oldest = std::min_element(streams_.begin(), streams_.end(),
                    [](const StreamEntry& a, const StreamEntry& b) { return a.last_seen < b.last_seen; });
                *oldest = {incoming_link, sysid, compid, incoming_ts, now};
            } else {
                streams_.push_back({incoming_link, sysid, compid, incoming_ts, now});
            }
        }

        return true;
    }

private:
    static void packUint48(std::vector<uint8_t>& dest, uint64_t val) {
        for (int i = 0; i < 6; ++i) {
            dest.push_back(static_cast<uint8_t>((val >> (i * 8)) & 0xFF));
        }
    }

    static uint64_t unpackUint48(std::span<const uint8_t> src) {
        uint64_t res = 0;
        for (int i = 0; i < 6; ++i) {
            res |= (static_cast<uint64_t>(src[i]) << (i * 8));
        }
        return res;
    }

    static bool constantTimeEqual(std::span<const uint8_t> a, std::span<const uint8_t> b) noexcept {
        if (a.size() != b.size()) return false;
        volatile uint8_t diff = 0;
        for (size_t i = 0; i < a.size(); ++i) {
            diff |= (a[i] ^ b[i]);
        }
        return diff == 0;
    }

    static std::array<uint8_t, 32> computeSha256(const KeyType& key, std::span<const uint8_t> data) {
        // Конкатенація ключа та даних у блоці SHA-256
        sha256_ctx_t sha;
        sha256_init(&sha);
        sha256_update(&sha, key.data(), key.size());
        sha256_update(&sha, data.data(), data.size());
        std::array<uint8_t, 32> out{};
        sha256_final(&sha, out.data());
        return out;
    }

    KeyType secret_key_;
    uint8_t link_id_;
    uint64_t current_timestamp_;
    std::vector<StreamEntry> streams_;
};
```
:::

### Покроковий розбір обчислення та трасування полів

Для глибшого розуміння того, що відбувається на рівні окремих байтів пам'яті, простежимо весь життєвий цикл формування захищеного кадру на прикладі реального повідомлення `HEARTBEAT` (MSG ID 0):

Припустимо, що автопілот із системною адресою `sysid = 1` та компонентом `compid = 1` готує до відправки повідомлення серцебиття на першому послідовному порту телеметрії (`link_id = 0`). Корисні дані повідомлення після відтинання нулів займають 9 байтів. Номер послідовності пакета дорівнює `seq = 42` (`0x2A`).

Спершу формується стандартний 10-байтовий заголовок MAVLink 2:
- Байт 0: `STX = 0xFD` (маркер MAVLink 2).
- Байт 1: `LEN = 0x09` (довжина корисних даних).
- Байт 2: `incompat_flags = 0x01` (встановлено біт `MAVLINK_IFLAG_SIGNED`).
- Байт 3: `compat_flags = 0x00`.
- Байт 4: `seq = 0x2A` (лічильник пакета).
- Байт 5: `sysid = 0x01`.
- Байт 6: `compid = 0x01`.
- Байти 7..9: `msgid = 0x00, 0x00, 0x00` (трибайтне 24-бітне значення типу повідомлення HEARTBEAT).

Далі у буфер записуються 9 байтів корисного навантаження (`payload`) та 2 байти контрольної суми CRC-16 (з урахуванням константи `CRC_EXTRA = 50` для повідомлення HEARTBEAT).

Після цього рушій береться за формування трейлера підпису. Поточний монотонний лічильник часу інкрементується до значення `125 000 000` (що відповідає 1250 секундам від базової епохи 2015 року). Це 64-бітне число перетворюється на 6 байтів у форматі little-endian:
- `0x125000000 = 0x00000007735940`
- У пам'яті байти розташовуються так: `0x40, 0x59, 0x73, 0x07, 0x00, 0x00`.

Разом із байтом `link_id = 0x00` формуються перші 7 байтів трейлера: `00 40 59 73 07 00 00`.

Тепер ініціалізується підсистема SHA-256. На вхід геш-функції послідовно передаються:
1. 32 байти секретного спільного ключа (наприклад, псевдовипадковий масив `0x3F, 0x8A, ...`).
2. 10 байтів заголовка кадру.
3. 9 байтів корисних даних.
4. 2 байти контрольної суми CRC-16.
5. 7 байтів початку трейлера (`link_id` + `timestamp`).

Сумарний розмір оброблюваного блоку становить: `32 + 10 + 9 + 2 + 7 = 60` байтів. Зверніть увагу: загальний розмір не перевищує 64 байти, тому весь розрахунок SHA-256 вкладається в один-єдиний цикл перетворення блоку `sha256_transform()`, що забезпечує максимальну швидкодію на мікроконтролері.

Геш-функція генерує 32 байти вихідного дайджесту, наприклад:
`A4 F9 21 D8 0C 3E 77 1B 90 ... B2`

З цього результату беруться рівно перші 6 байтів: `A4 F9 21 D8 0C 3E`, які дописуються у кінець буфера пакета як поле `Signature Hash`. Повний розмір готового до передачі в радіоефір кадру становить: `10 + 9 + 2 + 13 = 34` байти.

### Захист від атак за сторонніми каналами (Side-Channel Timing Attacks)

Особливу увагу в реалізації приділено функції перевірки підпису `constant_time_memcmp6()`. У класичних прикладних програмах розробники часто використовують стандартну бібліотечну функцію `memcmp()`. Проте для криптографічних протоколів це є критичною вразливістю.

Функція `memcmp()` виконує порівняння побайтово й негайно завершує роботу (`early exit`), щойно виявляє перший незбіг. Якщо зловмисник вгадав перший байт 6-байтового підпису, функція `memcmp()` виконає дві ітерації циклу замість однієї. За допомогою високоточних апаратних таймерів або мережевого аналізу джиттера пакетів атакуючий може виміряти цю мізерну різницю в кілька тактів процесора й послідовно підібрати всі 6 байтів підпису всього за `256 × 6 = 1536` запитів замість повного перебору 2⁴⁸ комбінацій.

У наведеній реалізації функція `constant_time_memcmp6()` гарантує однаковий час виконання незалежно від того, де саме знаходиться помилка:

:::tabs
```c
static bool constant_time_memcmp6(const uint8_t *a, const uint8_t *b) {
    volatile uint8_t diff = 0;
    for (int i = 0; i < 6; ++i) {
        diff |= (a[i] ^ b[i]);
    }
    return (diff == 0);
}
```
```cpp
[[nodiscard]] bool constantTimeEqual(std::span<const uint8_t, 6> a, std::span<const uint8_t, 6> b) noexcept {
    volatile uint8_t diff = 0;
    for (size_t i = 0; i < 6; ++i) {
        diff |= (a[i] ^ b[i]);
    }
    return diff == 0;
}
```
:::

Ключове слово `volatile` забороняє оптимізатору компілятора перетворити побітове накопичення різниці на достроковий вихід або векторну оптимізацію з умовними переходами. Цикл завжди чесно виконує рівно шість операцій XOR та шість операцій OR, унеможливлюючи будь-який витік інформації через час виконання.

### Безпека буферів та захист від переповнення пам'яті (Buffer Overrun Protection)

При розборі двійкових пакетів у вбудованих системах критично важливо гарантувати стійкість до спеціально сформованих шкідливих кадрів із підробленим полем довжини `LEN`.

Якщо зловмисник надішле кадр, де поле `LEN` встановлено у значення `255`, проте реальний фізичний розмір буфера становить лише 40 байтів, наївний розбірник спробує звернутися за адресою `packet_buf[10 + 255 + 2]`, що спричинить читання за межами виділеного буфера ОЗП (`out-of-bounds read`) або апаратний збій процесора `HardFault` через спробу доступу до неіснуючої сторінки пам'яті.

Функція `mavlink_crypto_verify_packet()` реалізує суворий попередній контроль меж:

:::tabs
```c
uint8_t payload_len = packet_buf[1];
size_t expected_total = 10 + payload_len + 2 + MAVLINK_SIGNING_TRAILER_LEN;
if (total_len != expected_total) {
    return false; // Невідповідність розміру кадру
}
```
```cpp
const uint8_t payload_len = packet[1];
const size_t expected_total = 10 + payload_len + 2 + kTrailerLen;
if (packet.size() != expected_total) {
    return false; // Невідповідність розміру кадру
}
```
:::
Перевірка зіставляє заявлену в заголовку довжину з фактично отриманою кількістю байтів від драйвера DMA. Якщо довжина хоча б на один байт відрізняється від математично розрахованої суми, кадр негайно відкидається без звернення до трейлера та без виклику геш-функції.

### Організація безкопійного виводу (Zero-Copy DMA TX Ring Buffers)

У польотних контролерах із високою інтенсивністю вихідного трафіку (наприклад, одночасна передача потоків орієнтації, сирих даних сенсорів і телеметрії GPS на швидкостях до 921600 бод) проміжне копіювання байтів на стек або у тимчасові буфери створює помітні накладні витрати пам'яті та процесорного часу.

Оптимальна архітектура передбачає формування та підписання кадру безпосередньо всередині кільцевого буфера передавача `TX Ring Buffer`. Задача-генератор виділяє суміжний блок у буфері розміром `10 + payload_len + 2 + 13` байтів, записує туди заголовок, заповнює корисні дані через прямий покажчик на структури повідомлення, розраховує CRC та підпис на місці (`in-place signing`), після чого передає дескриптор буфера контролеру DMA. Такий підхід виключає копіювання даних в ОЗП, мінімізує використання стека задачі FreeRTOS до кількох десятків байтів і гарантує відсутність блокувань ядра процесора під час роботи криптографічного конвеєра.

### Алгоритм заміщення слотів потоків (LRU) у ройових мережах

У складних сценаріях, коли на одній радіочастоті працює велика кількість безпілотних апаратів (рій дронів із 20+ одиниць) або коли наземна станція одночасно відстежує десятки апаратів через один шлюз, виникає крайовий випадок вичерпання таблиці потоків `MAVLINK_MAX_SIGNING_STREAMS` (16 слотів).

Якщо всі 16 слотів зайняті активними сесіями, а від нового апарата (`sysid = 17`) надходить перший підписаний кадр, рушій не повинен відкидати пакет або зависати. Алгоритм виконує пошук за принципом найменш використовуваного слота (Least Recently Used — LRU):

1. Для кожного слота `i` від 0 до 15 обчислюється вік останньої активності: `age_ms = current_time_ms - stream[i].last_activity_ms`.
2. Знаходиться слот із максимальним значенням `age_ms` (тобто апарат, від якого телеметрія не надходила найдовше).
3. Якщо вік цього слота перевищує встановлений таймаут втрати зв'язку (наприклад, 10 секунд), слот вважається застарілим і звільняється.
4. У звільнений слот записуються координати нового апарата `(sysid = 17, compid = 1, link_id = 0)` та початковий таймстемп з отриманого пакета.

Якщо ж усі 16 апаратів активні прямо зараз і шлють пакети кожні 100 мс, витіснення слота призведе до того, що під час наступного надходження пакета від витісненого апарата його слот знову буде перезаписано, спричинивши скидання лічильника `last_timestamp`. Для великих ройових мереж рекомендується збільшувати константу `MAVLINK_MAX_SIGNING_STREAMS` до 32 або 64 на етапі компіляції прошивки наземної станції.

### Продуктивність та апаратне прискорення SHA-256 на мікроконтролерах

Обчислювальна складність підпису MAVLink 2 визначається виключно швидкодією геш-функції SHA-256. Проведемо аналіз часу виконання операцій на типових бортових процесорах:

На мікроконтролері STM32F427 (ядро ARM Cortex-M4F на частоті 168 МГц) програмна реалізація SHA-256 для одного блоку розміром 64 байти потребує приблизно 850–900 тактів процесора. За тактової частоти 168 МГц це становить близько 5.1–5.4 мікросекунди. За темпу вихідної телеметрії 50 пакетів за секунду сумарне завантаження процесора на формування підписів складає менше 0.03% обчислювальної потужності ядра.

На сучасних польотних контролерах серії Pixhawk 6X на базі мікроконтролера STM32H743 (ядро Cortex-M7 на частоті 480 МГц) програмне гешування займає всього 1.4 мікросекунди. Крім того, чипи STM32 родин F4/F7/H7 містять вбудований апаратний криптографічний акселератор `HASH` (підтримує апаратний SHA-256 через прямий доступ до пам'яті DMA). Використання апаратного блоку скорочує час розрахунку до 0.4 мікросекунди без участі процесорного ядра, що дозволяє безперешкодно підписувати навіть високочастотні потоки сирих даних IMU на частотах 500–1000 Гц.

### Багатопотоковість та інтеграція в операційні системи реального часу (RTOS)

У польотних стеках під керуванням операційних систем реального часу (FreeRTOS, NuttX) формування пакетів MAVLink часто ініціюється з різних задач: навігаційна задача відправляє повідомлення `ATTITUDE` з частотою 50 Гц, задача планувальника надсилає звіти про місію, а фоновий потік обслуговує запити параметрів.

Оскільки екземпляр `mavlink_crypto_ctx_t` містить розділюваний стан (змінну `current_timestamp`), паралельний виклик функції `mavlink_crypto_sign_packet()` без синхронізації призведе до стану гонитви (race condition). Якщо два потоки одночасно зчитають однакове значення `current_timestamp`, вони можуть згенерувати два різні пакети з однаковим таймстемпом на одному й тому самому лінку. Приймач успішно прийме перший пакет, але негайно відкине другий як немонотонний!

Для усунення цієї проблеми в архітектурі PX4 та ArduPilot застосовують два підходи:

1. **М'ютексне блокування на рівні каналу:** перед початком пакування та підписання вихідного кадру задача захоплює двійковий семафор або м'ютекс відповідного каналу телеметрії (`pthread_mutex_lock`), звільняючи його лише після завершення запису в кільцевий буфер DMA.
2. **Атомарний інкремент таймстемпу:** поле `current_timestamp` оголошується як атомарний тип (`std::atomic<uint64_t>` або виклик GCC built-in `__atomic_fetch_add`), що гарантує унікальність і суворе монотонне зростання мітки часу навіть при виклику з переривань або паралельних RTOS-задач без блокування всього контуру передавача.

### Практичні рекомендації щодо обробки часових стрибків та збоїв

У процесі експлуатації систем із підписом виникають специфічні позаштатні ситуації, які вимагають передбаченої логіки відновлення:

1. **Холодний старт автопілота в польових умовах:** Якщо безпілотник вмикається в полі без доступу до сигналів супутників GNSS, його локальний годинник стартує з нуля (або зі збереженого в EEPROM значення). Якщо наземна станція вже працює й має точний час за GPS, виникає значний розрив між часовими шкалами. Завдяки тому, що кожна сторона перевіряє лише монотонність зростання відносно власного зафіксованого початкового часу для кожного відправника, різниця в абсолютних значеннях годинників дрона та станції не впливає на валідність підпису, якщо обидва таймстемпи стабільно зростають.
2. **Перестановка порядку пакетів у мережах UDP (Packet Reordering):** У радіолініях на базі Wi-Fi або мобільних мереж 4G/LTE пакети іноді приходять із порушенням хронологічного порядку (пакет із `ts = 1002` обганяє пакет із `ts = 1001`). За суворої перевірки монотонності запізнілий пакет `ts = 1001` буде відкинуто як replay-атаку. Для більшості потокових даних телеметрії це є абсолютно коректною поведінкою, оскільки застарілі кути нахилу чи висота більше не мають цінності для системи керування. Для надійних команд застосовується механізм підтвердження `COMMAND_ACK` ([команди MAVLink](book:communications/mavlink-commands)).
3. **Захист від переповнення 48-бітного таймстемпу:** Оскільки 48-бітний лічильник із дискретністю 10 мкс переповниться лише через 89.2 року безперервної роботи, у коді прошивок не потрібно реалізовувати складну логіку обробки циклічного переходу через нуль, що значно спрощує розбірник та підвищує загальну надійність вбудованого ПЗ.
4. **Виявлення та логування вторгнень (Intrusion Detection):** При виявленні кадрів із помилковим підписом або застарілим таймстемпом бортовий стек не просто скидає байти, а інкрементує лічильник атак `signing_errors` і генерує текстове сповіщення `STATUSTEXT` із рівнем `MAV_SEVERITY_WARNING` на пульт оператора, попереджаючи про наявність джерела радіоперешкод або активної спроби підміни керування в зоні польоту.
