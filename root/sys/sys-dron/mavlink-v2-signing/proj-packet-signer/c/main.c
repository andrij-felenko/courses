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
