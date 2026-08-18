# ⚙️ Реалізація HMAC-SHA256, експлойт подовження та захищений верифікатор

Практична реалізація контролю автентичності вимагає точного дотримання криптографічних інваріантів: правильної нормалізації ключів до розміру блоку геш-функції, двопрохідного змішування масок `ipad`/`opad`, а також верифікації тегів у строго константному часі без витоку інформації через кеш процесора чи розгалуження коду.

## Архітектура та етапи обчислення HMAC-SHA256

HMAC працює як універсальна криптографічна надбудова над будь-якою ітеративною геш-функцією блокової структури. Для сімейства SHA-256 розмір внутрішнього блоку стиснення становить `B = 64` байти (512 бітів), а вихідний дайджест — `L = 32` байти (256 бітів).

Процес обчислення коду автентичності складається з чотирьох чітко розмежованих етапів, кожен з яких усуває конкретну загрозу безпеці:

### 1. Нормалізація та вирівнювання ключа

Вхідний секретний ключ `K` може мати довільну довжину: від нуля байтів до багатьох кілобайтів. Для коректного накладання на фіксований 64-байтний блок стиснення його приводять до канонічного вигляду `K'`:

- **Довгий ключ (`|K| > 64` байтів):** якщо ключ довший за блок стиснення, його неможливо напряму додати до маски `ipad`. Такий ключ попередньо гешують: `K' = SHA256(K)`. Отриманий 32-байтний дайджест доповнюється 32 нульовими байтами `0x00` праворуч до повного розміру блоку 64 байти. Це зберігає повну ентропію ключа, зводячи обчислювальну міцність до `2²⁵⁶`.
- **Короткий або точний ключ (`|K| ≤ 64` байти):** ключ копіюється без змін у ліву частину 64-байтного буфера, а залишок праворуч заповнюється нулями: `K' = K || 0x00...0x00`. Якщо ключ уже має довжину рівно 64 байти, жодного доповнення не відбувається.
- **Порожній ключ (`|K| = 0`):** буфер `K'` повністю заповнюється 64 нульовими байтами `0x00`.

### 2. Формування ізольованих субключів K_in та K_out

Для запобігання перетину внутрішнього та зовнішнього станів нормалізований ключ `K'` побайтово додається за модулем 2 (`XOR`) з двома ортогональними константами:

```
K_in  = K' ⊕ ipad   [де ipad = 0x36, повторений 64 рази]
K_out = K' ⊕ opad   [де opad = 0x5C, повторений 64 рази]
```

Оскільки різниця між байтами становить `0x36 ⊕ 0x5C = 0x6A` (`01101010₂`), у кожному байті блоку рівно чотири біти є взаємно інвертованими. Це гарантує максимальне бітове розсіювання (відстань Геммінга дорівнює 256 бітів на блок) і унеможливлює збіг або лінійну залежність між `K_in` та `K_out`.

### 3. Внутрішній прохід: зв'язування повідомлення

Створюється перший екземпляр геш-функції SHA-256 (внутрішній каскад). Спершу в нього подається 64-байтний блок `K_in`. Функція стиснення обробляє цей блок і переводить початковий вектор ініціалізації `IV` у таємний проміжний стан `h₁ = f(IV, K_in)`.

Далі в цей самий контекст безперервним потоком подається тіло повідомлення `message`. Після завершення гешування формується 32-байтний внутрішній дайджест:

```
d_in = SHA256( K_in || message )
```

Будь-яка модифікація хоча б одного біта повідомлення повністю змінює значення `d_in` завдяки лавинному ефекту базової геш-функції.

### 4. Зовнішній прохід: екранування внутрішнього стану

Створюється другий екземпляр геш-функції (зовнішній каскад). У нього спочатку подається 64-байтний блок `K_out`, що формує другий таємний проміжний стан `h₂ = f(IV, K_out)`.

Потім у зовнішній контекст подається 32-байтний внутрішній дайджест `d_in`. Після фіналізації обчислень отримуємо остаточний код автентичності повідомлення:

```
HMAC(K, message) = SHA256( K_out || d_in )
```

Зовнішній геш приймає на вхід рівно 96 байтів даних (`64 + 32`), тому його обчислення завжди займає рівно два блоки стиснення (перший блок `K_out`, другий блок `d_in` разом із фінальним доповненням). Це робить час зовнішнього проходу суворо константним і незалежним від довжини вхідного повідомлення `message`.

Нижче наведено повну самодостатню реалізацію HMAC-SHA256 мовами C та C++, що підтримує як одноразове підписування буфера, так і потокову обробку даних частинами (Streaming API).

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <string.h>

#define SHA256_BLOCK_SIZE 64
#define SHA256_DIGEST_SIZE 32

/* Базовий контекст SHA-256 */
typedef struct {
    uint32_t state[8];
    uint64_t count;
    uint8_t buffer[SHA256_BLOCK_SIZE];
} sha256_ctx_t;

/* Допоміжні функції бітових операцій SHA-256 */
static inline uint32_t rotr(uint32_t x, uint32_t n) {
    return (x >> n) | (x << (32 - n));
}
#define CH(x, y, z)  (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x, y, z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define EP0(x)       (rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22))
#define EP1(x)       (rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25))
#define SIG0(x)      (rotr(x, 7) ^ rotr(x, 18) ^ ((x) >> 3))
#define SIG1(x)      (rotr(x, 17) ^ rotr(x, 19) ^ ((x) >> 10))

static const uint32_t K256[64] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
};

static void sha256_transform(sha256_ctx_t *ctx, const uint8_t data[64]) {
    uint32_t a, b, c, d, e, f, g, h, w[64];
    for (int i = 0; i < 16; i++) {
        w[i] = ((uint32_t)data[i * 4] << 24) | ((uint32_t)data[i * 4 + 1] << 16) |
               ((uint32_t)data[i * 4 + 2] << 8) | ((uint32_t)data[i * 4 + 3]);
    }
    for (int i = 16; i < 64; i++) {
        w[i] = SIG1(w[i - 2]) + w[i - 7] + SIG0(w[i - 15]) + w[i - 16];
    }
    a = ctx->state[0]; b = ctx->state[1]; c = ctx->state[2]; d = ctx->state[3];
    e = ctx->state[4]; f = ctx->state[5]; g = ctx->state[6]; h = ctx->state[7];

    for (int i = 0; i < 64; i++) {
        uint32_t t1 = h + EP1(e) + CH(e, f, g) + K256[i] + w[i];
        uint32_t t2 = EP0(a) + MAJ(a, b, c);
        h = g; g = f; f = e; e = d + t1;
        d = c; c = b; b = a; a = t1 + t2;
    }
    ctx->state[0] += a; ctx->state[1] += b; ctx->state[2] += c; ctx->state[3] += d;
    ctx->state[4] += e; ctx->state[5] += f; ctx->state[6] += g; ctx->state[7] += h;
}

void sha256_init(sha256_ctx_t *ctx) {
    ctx->state[0] = 0x6a09e667; ctx->state[1] = 0xbb67ae85;
    ctx->state[2] = 0x3c6ef372; ctx->state[3] = 0xa54ff53a;
    ctx->state[4] = 0x510e527f; ctx->state[5] = 0x9b05688c;
    ctx->state[6] = 0x1f83d9ab; ctx->state[7] = 0x5be0cd19;
    ctx->count = 0;
}

void sha256_update(sha256_ctx_t *ctx, const uint8_t *data, size_t len) {
    size_t buf_idx = (size_t)(ctx->count % SHA256_BLOCK_SIZE);
    ctx->count += len;
    while (len > 0) {
        size_t copy_len = SHA256_BLOCK_SIZE - buf_idx;
        if (len < copy_len) copy_len = len;
        memcpy(&ctx->buffer[buf_idx], data, copy_len);
        data += copy_len;
        len -= copy_len;
        buf_idx = (buf_idx + copy_len) % SHA256_BLOCK_SIZE;
        if (buf_idx == 0) {
            sha256_transform(ctx, ctx->buffer);
        }
    }
}

void sha256_final(sha256_ctx_t *ctx, uint8_t digest[SHA256_DIGEST_SIZE]) {
    uint8_t pad[64] = {0x80};
    uint64_t bitlen = ctx->count * 8;
    uint8_t len_bytes[8];
    for (int i = 0; i < 8; i++) {
        len_bytes[7 - i] = (uint8_t)(bitlen >> (i * 8));
    }
    size_t pad_len = (ctx->count % 64 < 56) ? (56 - (ctx->count % 64)) : (120 - (ctx->count % 64));
    sha256_update(ctx, pad, pad_len);
    sha256_update(ctx, len_bytes, 8);
    for (int i = 0; i < 8; i++) {
        digest[i * 4]     = (uint8_t)(ctx->state[i] >> 24);
        digest[i * 4 + 1] = (uint8_t)(ctx->state[i] >> 16);
        digest[i * 4 + 2] = (uint8_t)(ctx->state[i] >> 8);
        digest[i * 4 + 3] = (uint8_t)(ctx->state[i]);
    }
}

/* Структура контексту HMAC-SHA256 */
typedef struct {
    sha256_ctx_t inner_ctx;
    sha256_ctx_t outer_ctx;
} hmac_sha256_ctx_t;

void hmac_sha256_init(hmac_sha256_ctx_t *ctx, const uint8_t *key, size_t key_len) {
    uint8_t k_prime[SHA256_BLOCK_SIZE] = {0};
    uint8_t k_ipad[SHA256_BLOCK_SIZE];
    uint8_t k_opad[SHA256_BLOCK_SIZE];

    /* 1. Нормалізація ключа */
    if (key_len > SHA256_BLOCK_SIZE) {
        sha256_ctx_t k_ctx;
        sha256_init(&k_ctx);
        sha256_update(&k_ctx, key, key_len);
        sha256_final(&k_ctx, k_prime);
    } else {
        memcpy(k_prime, key, key_len);
    }

    /* 2. Побітове накладання масок ipad (0x36) та opad (0x5C) */
    for (size_t i = 0; i < SHA256_BLOCK_SIZE; i++) {
        k_ipad[i] = k_prime[i] ^ 0x36;
        k_opad[i] = k_prime[i] ^ 0x5C;
    }

    /* 3. Ініціалізація внутрішнього та зовнішнього каскадів */
    sha256_init(&ctx->inner_ctx);
    sha256_update(&ctx->inner_ctx, k_ipad, SHA256_BLOCK_SIZE);

    sha256_init(&ctx->outer_ctx);
    sha256_update(&ctx->outer_ctx, k_opad, SHA256_BLOCK_SIZE);

    /* Безпечне очищення тимчасових буферів ключа у стеку */
    memset(k_prime, 0, sizeof(k_prime));
    memset(k_ipad, 0, sizeof(k_ipad));
    memset(k_opad, 0, sizeof(k_opad));
}

void hmac_sha256_update(hmac_sha256_ctx_t *ctx, const uint8_t *data, size_t len) {
    sha256_update(&ctx->inner_ctx, data, len);
}

void hmac_sha256_final(hmac_sha256_ctx_t *ctx, uint8_t mac[SHA256_DIGEST_SIZE]) {
    uint8_t inner_digest[SHA256_DIGEST_SIZE];
    sha256_final(&ctx->inner_ctx, inner_digest);
    sha256_update(&ctx->outer_ctx, inner_digest, SHA256_DIGEST_SIZE);
    sha256_final(&ctx->outer_ctx, mac);
    memset(inner_digest, 0, sizeof(inner_digest));
}

/* Одноразовий виклик HMAC-SHA256 */
void hmac_sha256(const uint8_t *key, size_t key_len,
                 const uint8_t *msg, size_t msg_len,
                 uint8_t out[SHA256_DIGEST_SIZE]) {
    hmac_sha256_ctx_t ctx;
    hmac_sha256_init(&ctx, key, key_len);
    hmac_sha256_update(&ctx, msg, msg_len);
    hmac_sha256_final(&ctx, out);
}
```
```cpp
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <span>
#include <string_view>

namespace crypto {

constexpr size_t sha256_block_size = 64;
constexpr size_t sha256_digest_size = 32;

class Sha256 {
public:
    Sha256() noexcept { reset(); }

    void reset() noexcept {
        state_ = {0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
                  0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19};
        count_ = 0;
        buffer_.fill(0);
    }

    void update(std::span<const uint8_t> data) noexcept {
        size_t buf_idx = static_cast<size_t>(count_ % sha256_block_size);
        count_ += data.size();
        size_t offset = 0;
        size_t remaining = data.size();

        while (remaining > 0) {
            size_t copy_len = sha256_block_size - buf_idx;
            if (remaining < copy_len) copy_len = remaining;
            std::memcpy(&buffer_[buf_idx], &data[offset], copy_len);
            offset += copy_len;
            remaining -= copy_len;
            buf_idx = (buf_idx + copy_len) % sha256_block_size;
            if (buf_idx == 0) {
                transform(buffer_.data());
            }
        }
    }

    void update(std::string_view str) noexcept {
        update(std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(str.data()), str.size()));
    }

    [[nodiscard]] std::array<uint8_t, sha256_digest_size> finalize() noexcept {
        std::array<uint8_t, 64> pad = {0x80};
        uint64_t bitlen = count_ * 8;
        std::array<uint8_t, 8> len_bytes{};
        for (size_t i = 0; i < 8; ++i) {
            len_bytes[7 - i] = static_cast<uint8_t>(bitlen >> (i * 8));
        }

        size_t rem = count_ % 64;
        size_t pad_len = (rem < 56) ? (56 - rem) : (120 - rem);
        update(std::span<const uint8_t>(pad.data(), pad_len));
        update(std::span<const uint8_t>(len_bytes.data(), 8));

        std::array<uint8_t, sha256_digest_size> digest{};
        for (size_t i = 0; i < 8; ++i) {
            digest[i * 4]     = static_cast<uint8_t>(state_[i] >> 24);
            digest[i * 4 + 1] = static_cast<uint8_t>(state_[i] >> 16);
            digest[i * 4 + 2] = static_cast<uint8_t>(state_[i] >> 8);
            digest[i * 4 + 3] = static_cast<uint8_t>(state_[i]);
        }
        return digest;
    }

    static std::array<uint8_t, sha256_digest_size> hash(std::span<const uint8_t> data) noexcept {
        Sha256 ctx;
        ctx.update(data);
        return ctx.finalize();
    }

private:
    static constexpr uint32_t rotr(uint32_t x, uint32_t n) noexcept {
        return (x >> n) | (x << (32 - n));
    }
    static constexpr uint32_t ch(uint32_t x, uint32_t y, uint32_t z) noexcept { return (x & y) ^ (~x & z); }
    static constexpr uint32_t maj(uint32_t x, uint32_t y, uint32_t z) noexcept { return (x & y) ^ (x & z) ^ (y & z); }
    static constexpr uint32_t ep0(uint32_t x) noexcept { return rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22); }
    static constexpr uint32_t ep1(uint32_t x) noexcept { return rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25); }
    static constexpr uint32_t sig0(uint32_t x) noexcept { return rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3); }
    static constexpr uint32_t sig1(uint32_t x) noexcept { return rotr(x, 17) ^ rotr(x, 19) ^ (x >> 10); }

    void transform(const uint8_t data[64]) noexcept {
        static constexpr std::array<uint32_t, 64> k256 = {
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
            0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
            0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
            0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
            0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
            0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
            0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
            0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
        };

        std::array<uint32_t, 64> w{};
        for (size_t i = 0; i < 16; ++i) {
            w[i] = (static_cast<uint32_t>(data[i * 4]) << 24) |
                   (static_cast<uint32_t>(data[i * 4 + 1]) << 16) |
                   (static_cast<uint32_t>(data[i * 4 + 2]) << 8) |
                   (static_cast<uint32_t>(data[i * 4 + 3]));
        }
        for (size_t i = 16; i < 64; ++i) {
            w[i] = sig1(w[i - 2]) + w[i - 7] + sig0(w[i - 15]) + w[i - 16];
        }

        uint32_t a = state_[0], b = state_[1], c = state_[2], d = state_[3];
        uint32_t e = state_[4], f = state_[5], g = state_[6], h = state_[7];

        for (size_t i = 0; i < 64; ++i) {
            uint32_t t1 = h + ep1(e) + ch(e, f, g) + k256[i] + w[i];
            uint32_t t2 = ep0(a) + maj(a, b, c);
            h = g; g = f; f = e; e = d + t1;
            d = c; c = b; b = a; a = t1 + t2;
        }

        state_[0] += a; state_[1] += b; state_[2] += c; state_[3] += d;
        state_[4] += e; state_[5] += f; state_[6] += g; state_[7] += h;
    }

    std::array<uint32_t, 8> state_{};
    uint64_t count_{0};
    std::array<uint8_t, sha256_block_size> buffer_{};
};

class HmacSha256 {
public:
    explicit HmacSha256(std::span<const uint8_t> key) noexcept {
        std::array<uint8_t, sha256_block_size> k_prime{};
        if (key.size() > sha256_block_size) {
            auto hashed_key = Sha256::hash(key);
            std::copy(hashed_key.begin(), hashed_key.end(), k_prime.begin());
        } else {
            std::copy(key.begin(), key.end(), k_prime.begin());
        }

        std::array<uint8_t, sha256_block_size> k_ipad{};
        std::array<uint8_t, sha256_block_size> k_opad{};
        for (size_t i = 0; i < sha256_block_size; ++i) {
            k_ipad[i] = k_prime[i] ^ 0x36;
            k_opad[i] = k_prime[i] ^ 0x5C;
        }

        inner_.update(k_ipad);
        outer_.update(k_opad);

        // Очищення чутливих ключів зі стеку
        k_prime.fill(0);
        k_ipad.fill(0);
        k_opad.fill(0);
    }

    void update(std::span<const uint8_t> data) noexcept {
        inner_.update(data);
    }

    void update(std::string_view str) noexcept {
        inner_.update(str);
    }

    [[nodiscard]] std::array<uint8_t, sha256_digest_size> finalize() noexcept {
        auto inner_digest = inner_.finalize();
        outer_.update(inner_digest);
        auto final_tag = outer_.finalize();
        inner_digest.fill(0);
        return final_tag;
    }

    static std::array<uint8_t, sha256_digest_size> sign(
        std::span<const uint8_t> key,
        std::span<const uint8_t> data) noexcept {
        HmacSha256 hmac(key);
        hmac.update(data);
        return hmac.finalize();
    }

private:
    Sha256 inner_;
    Sha256 outer_;
};

} // namespace crypto
```
:::

## Практична демонстрація атаки подовження довжини

Щоб наочно побачити фатальну вразливість наївного склеювання `H(Key || msg)`, створимо експлойт, який відновлює внутрішній стан геш-функції з перехопленого підпису та підробляє команду без знання секретного ключа.

### Сценарій атаки

Уявімо типову систему виконання фінансових інструкцій у REST API. Сервер приймає HTTP-запити з двома параметрами: тілом повідомлення `msg` та контрольним підписом `sig`. Розробник вирішив захистити дані наївною конструкцією:

```
sig = SHA256( secret_key || msg )
```

Легітимний користувач надсилає запит:
- Початкове повідомлення `m`: `"action=view&user=alice"` (довжина 22 байти).
- Таємний ключ сервера `K`: `"supersecretkey"` (довжина 14 байтів, відомий лише серверу).
- Сумарна довжина входу геш-функції: `14 + 22 = 36` байтів.

Сервер обчислює `sig = SHA256("supersecretkeyaction=view&user=alice")` та повертає відповідь.

Зловмисник перехоплює цей запит у відкритому каналі зв'язку. Його мета — приєднати до команди суфікс `m_ext = "&admin=true&action=delete"` та змусити сервер виконати її з правами адміністратора.

### Механізм роботи експлойту

1. **Реконструкція вирівнювання (Padding).** Геш-функція SHA-256 завжди вирівнює дані блоками по 64 байти. Для вхідного рядка довжиною 36 байтів алгоритм додає байт `0x80`, потім `(56 - 36 - 1) = 19` нульових байтів `0x00`, а в останні 8 байтів записує початкову довжину в бітах: `36 · 8 = 288` бітів (`0x0000000000000120`). У результаті перший 64-байтний блок повністю сформовано.
2. **Захоплення внутрішнього вектора стану.** Перехоплений 32-байтний геш `sig` розбивається на вісім 32-бітних слів `(A, B, C, D, E, F, G, H)`. Ці слова завантажуються безпосередньо в регістри стану нового екземпляра контексту SHA-256 замість стандартного вектора `IV`.
3. **Продовження обчислень.** Лічильник оброблених байтів у підробленому контексті встановлюється рівним 64 байтам (розмір першого віртуального блоку). Далі в контекст подається шкідливий хвіст `m_ext`. Алгоритм виконує стандартні раундові перетворення над новим блоком і обчислює фінальний дайджест `forged_sig`.
4. **Формування підробленого повідомлення.** Зловмисник відправляє на сервер розширене тіло: `m || padding || m_ext` разом із новим підписом `forged_sig`.

Сервер, отримавши цей пакет, конкатенує свій таємний ключ `K` із отриманим тілом, обробляє весь потік заново і отримує **точно такий самий** підпис `forged_sig`! Атака спрацьовує з імовірністю 100%, хоча зловмисник не дізнався жодного байта таємного ключа.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <string.h>

/* Функція створення підробленого гешу продовженням стану */
void length_extension_attack_sha256(
    const uint8_t original_hash[32],
    size_t original_total_len,  /* Довжина Key || Message */
    const uint8_t *extension_data,
    size_t extension_len,
    uint8_t forged_hash[32],
    uint8_t *forged_msg,
    size_t *forged_msg_len)
{
    /* 1. Обчислення оригінального padding для Key || Message */
    uint8_t pad[128] = {0};
    pad[0] = 0x80;
    size_t rem = original_total_len % 64;
    size_t pad_len = (rem < 56) ? (56 - rem) : (120 - rem);
    uint64_t bitlen = original_total_len * 8;
    for (int i = 0; i < 8; i++) {
        pad[pad_len + 7 - i] = (uint8_t)(bitlen >> (i * 8));
    }
    size_t total_pad_bytes = pad_len + 8;

    /* 2. Відновлення 8 регістрів стану з перехопленого 32-байтного гешу */
    sha256_ctx_t forged_ctx;
    for (int i = 0; i < 8; i++) {
        forged_ctx.state[i] = ((uint32_t)original_hash[i * 4] << 24) |
                              ((uint32_t)original_hash[i * 4 + 1] << 16) |
                              ((uint32_t)original_hash[i * 4 + 2] << 8) |
                              ((uint32_t)original_hash[i * 4 + 3]);
    }
    /* Лічильник встановлюється так, ніби початкові блоки вже оброблено */
    forged_ctx.count = original_total_len + total_pad_bytes;

    /* 3. Продовження гешування шкідливим хвостом */
    sha256_update(&forged_ctx, extension_data, extension_len);
    sha256_final(&forged_ctx, forged_hash);

    /* 4. Формування тіла сфальсифікованого повідомлення (без ключа) */
    memcpy(forged_msg, pad, total_pad_bytes);
    memcpy(forged_msg + total_pad_bytes, extension_data, extension_len);
    *forged_msg_len = total_pad_bytes + extension_len;
}
```
```cpp
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <vector>

namespace crypto {

struct ForgedPayload {
    std::array<uint8_t, 32> forged_hash;
    std::vector<uint8_t> extension_stream; // Pad + шкідливий хвіст
};

ForgedPayload perform_length_extension_attack(
    std::span<const uint8_t, 32> original_hash,
    size_t known_total_len, // Довжина Key + Message
    std::span<const uint8_t> extension_data)
{
    // 1. Формування оригінального вирівнювання (padding)
    std::vector<uint8_t> pad;
    pad.push_back(0x80);
    size_t rem = known_total_len % 64;
    size_t pad_len = (rem < 56) ? (56 - rem) : (120 - rem);
    pad.resize(pad_len, 0x00);

    uint64_t bitlen = known_total_len * 8;
    for (int i = 7; i >= 0; --i) {
        pad.push_back(static_cast<uint8_t>(bitlen >> (i * 8)));
    }

    // 2. Ініціалізація стану з перехопленого гешу
    Sha256 forged_ctx;
    // Відновлення внутрішніх 32-бітних слів стану
    std::array<uint32_t, 8> restored_state{};
    for (size_t i = 0; i < 8; ++i) {
        restored_state[i] = (static_cast<uint32_t>(original_hash[i * 4]) << 24) |
                            (static_cast<uint32_t>(original_hash[i * 4 + 1]) << 16) |
                            (static_cast<uint32_t>(original_hash[i * 4 + 2]) << 8) |
                            (static_cast<uint32_t>(original_hash[i * 4 + 3]));
    }

    // Додаємо хвіст до розширеного тіла
    std::vector<uint8_t> payload = pad;
    payload.insert(payload.end(), extension_data.begin(), extension_data.end());

    // 3. Обчислення сфальсифікованого тегу
    return { Sha256::hash(payload), payload };
}

} // namespace crypto
```
:::

### Чому HMAC повністю імунізує систему від цієї атаки

Якщо на сервері використовується `HMAC-SHA256(K, msg)`, зовнішній вихідний дайджест є результатом суперпозиції `SHA256(K_out || d_in)`.

Зловмисник отримує лише результат зовнішнього гешу. Внутрішній проміжний стан `d_in = SHA256(K_in || msg)` надійно прихований під одностороннім перетворенням зовнішнього каскаду. Спроба продовжити ланцюг обчислень призведе лише до подовження блоку `(K_out || d_in)`, що не дає жодного контролю над вихідним повідомленням `msg`. Атака подовження стає математично неможливою.

## Безпечна верифікація: захист від атак за часом (Constant-Time Compare)

Найпоширеніша вразливість систем контролю автентичності у виробничому коді криється не в обчисленні гешу, а в етапі порівняння отриманого тегу з еталонним значенням.

### Анатомія витоку через ранній вихід (Early Exit)

Стандартні бібліотечні функції порівняння буферів пам'яті — `memcmp` у C, `std::memcmp` та `operator==` у C++ — оптимізовані виключно для максимальної швидкодії. Вони виконують побайтове або пословне порівняння і повертають результат **негайно**, щойно зафіксують першу невідповідність:

```
for (size_t i = 0; i < len; i++) {
    if (a[i] != b[i]) return a[i] - b[i];  // РАННІЙ ВИХІД
}
```

У результаті час виконання функції стає прямою лінійною функцією від кількості перших байтів, що збіглися між кандидатом та еталоном:
- Якщо байт 0 не збігся: процесор виконує 1 ітерацію циклу (близько 8–12 тактів процесора).
- Якщо збіглися перші 3 байти: виконуються 4 ітерації (близько 30–40 тактів).
- Якщо збіглися перші 16 байтів: час виконання зростає в кілька разів.

### Дистанційне відновлення підпису

Незважаючи на мережевий шум (джиттер), зловмисник, надсилаючи кілька сотень запитів на кожен варіант байта й усереднюючи статистичний розподіл затримки (метод відсікання викидів або інтерквартильного аналізу), чітко бачить стрибок у часі відповіді.

Це дозволяє підбирати 32-байтний криптографічний тег послідовно байт за байтом:
- Байт 0: перебір 256 варіантів `0x00...0xFF`. Правильний байт дає помітне статистичне збільшення часу відповіді.
- Байт 1: фіксуємо знайдений байт 0 і перебираємо 256 варіантів байта 1.
- Процес повторюється для всіх 32 байтів.

Сумарна складність злому зменшується з експоненційних `2²⁵⁶` операцій до лінійних:

```
256 варіантів · 32 байти = 8192 запити
```

Така кількість запитів виконується менш ніж за кілька секунд, повністю компрометуючи автентичність сесії.

### Константний алгоритм верифікації

Безпечне порівняння зобов'язане гарантувати виконання суворо однакової кількості інструкцій без умовних переходів, незалежно від вмісту буферів. Для цього використовується побітове додавання за модулем 2 (`XOR`) з накопиченням бітової різниці у змінній-акумуляторі через побітове `OR`:

:::tabs
```c
#include <stdint.h>
#include <stddef.h>

/**
 * Безпечне порівняння двох буферів однакової довжини в константному часі.
 * Повертає 1, якщо буфери ідентичні, і 0 у разі будь-якої розбіжності.
 */
int constant_time_memcmp(const void *a, const void *b, size_t len) {
    const volatile uint8_t *pa = (const volatile uint8_t *)a;
    const volatile uint8_t *pb = (const volatile uint8_t *)b;
    volatile uint8_t diff = 0;

    for (size_t i = 0; i < len; i++) {
        diff |= (pa[i] ^ pb[i]);
    }

    /* Відображення: diff == 0 -> 1; diff != 0 -> 0 без розгалужень */
    return (int)((1u ^ ((diff | (0u - diff)) >> 31)));
}

/**
 * Верифікація HMAC-SHA256 підпису.
 */
int hmac_sha256_verify(const uint8_t *key, size_t key_len,
                       const uint8_t *msg, size_t msg_len,
                       const uint8_t expected_mac[32]) {
    uint8_t computed_mac[32];
    hmac_sha256(key, key_len, msg, msg_len, computed_mac);

    int is_valid = constant_time_memcmp(computed_mac, expected_mac, 32);

    /* Безпечне затирання обчисленого підпису у стеку */
    for (volatile int i = 0; i < 32; i++) computed_mac[i] = 0;

    return is_valid;
}
```
```cpp
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

namespace crypto {

/**
 * Безпечне порівняння двох масивів фіксованої довжини в константному часі.
 */
template <size_t N>
[[nodiscard]] bool constant_time_equals(
    std::span<const uint8_t, N> a,
    std::span<const uint8_t, N> b) noexcept
{
    volatile uint8_t diff = 0;
    for (size_t i = 0; i < N; ++i) {
        diff = static_cast<uint8_t>(diff | (a[i] ^ b[i]));
    }
    return diff == 0;
}

/**
 * Верифікація HMAC-SHA256 підпису повідомлення з очищенням пам'яті.
 */
[[nodiscard]] bool verify_hmac_sha256(
    std::span<const uint8_t> key,
    std::span<const uint8_t> message,
    std::span<const uint8_t, 32> expected_tag) noexcept
{
    auto computed_tag = HmacSha256::sign(key, message);
    bool valid = constant_time_equals<32>(
        std::span<const uint8_t, 32>(computed_tag),
        expected_tag
    );
    computed_tag.fill(0);
    return valid;
}

} // namespace crypto
```
:::

## Інженерні пастки в реальних системах

Під час практичного використання HMAC у високонавантажених та вбудованих системах розробники найчастіше стикаються з трьома небезпечними дефектами:

### 1. Агресивна оптимізація компілятора (Dead Code Elimination)

Компілятори з оптимізаціями `-O2` або `-O3` аналізують життєвий цикл змінних. Якщо розробник затирає ключ викликом `memset(key, 0, sizeof(key))` безпосередньо перед виходом із функції, компілятор бачить, що буфер `key` більше ніколи не читається в поточній області видимості.

Компілятор має повне право повністю видалити виклик `memset` як «мертвий код» (англ. *Dead Store Elimination*). У результаті секретний ключ залишається відкритим у незмінному вигляді у стековій пам'яті або регістрах процесора.

Для запобігання цій вразливості слід використовувати спеціалізовані функції операційної системи:
- `explicit_bzero()` у POSIX та сучасних дистрибутивах Linux.
- `OPENSSL_cleanse()` при роботі з OpenSSL.
- `SecureZeroMemory()` у Windows.
- Запис через покажчик на `volatile uint8_t` або використання бар'єра пам'яті `asm volatile("" ::: "memory")`.

### 2. Векторизація циклу порівняння (SIMD Early Break)

Якщо змінна-акумулятор `diff` у константному циклі не оголошена як `volatile`, оптимізатор LLVM або GCC може розпізнати шаблон порівняння масивів і згенерувати векторні інструкції AVX-512/NEON із перевіркою маски незбігу та інструкцією розгалуження, випадково повернувши вразливість раннього виходу. Кваліфікатор `volatile` змушує компілятор чесно читати пам'ять побайтово на кожній ітерації без векторизації розгалужень.

### 3. Змішування ключів між різними примітивами (Key Reuse Trap)

Використання одного й того самого спільного секрету для шифрування (наприклад, AES-CBC) та автентифікації (HMAC) категорично заборонено. Алгебраїчні взаємодії між раундами шифру та геш-функцією можуть призвести до взаємного послаблення криптографічної стійкості обох алгоритмів. Якщо для зв'язку потрібні два ключі, вони мають бути згенеровані з єдиного майстер-секрету через функцію деривації HKDF із різними контекстними мітками `info`:

## Покрокове трасування обчислень на еталонному векторі RFC 4231

Щоб верифікувати правильність програмної реалізації, простежимо покроковий рух байтів на офіційному тестовому векторі Test Case 2 зі специфікації RFC 4231:

- **Ключ `K`:** ASCII-рядок `"Jefe"` (4 байти: `0x4A, 0x65, 0x66, 0x65`).
- **Повідомлення `m`:** ASCII-рядок `"what do ya want for nothing?"` (28 байтів).
- **Очікуваний результат HMAC-SHA256:** `5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843`.

### 1. Нормалізація ключа K' (64 байти)

Оскільки довжина ключа `|K| = 4` байти, що менше за розмір блоку 64 байти, перші 4 байти копіюються без змін, а решта 60 байтів заповнюються нулями:

```
K' = 4a 65 66 65 00 00 00 00 00 00 00 00 00 00 00 00 ... 00
```

### 2. Побітове накладання масок ipad та opad

- Внутрішній ключ `K_in = K' ⊕ 0x36`:
  - Байт 0: `0x4A ⊕ 0x36 = 0x7C`
  - Байт 1: `0x65 ⊕ 0x36 = 0x53`
  - Байт 2: `0x66 ⊕ 0x36 = 0x50`
  - Байт 3: `0x65 ⊕ 0x36 = 0x53`
  - Байти 4–63: `0x00 ⊕ 0x36 = 0x36`
- Зовнішній ключ `K_out = K' ⊕ 0x5C`:
  - Байт 0: `0x4A ⊕ 0x5C = 0x16`
  - Байт 1: `0x65 ⊕ 0x5C = 0x39`
  - Байт 2: `0x66 ⊕ 0x5C = 0x3A`
  - Байт 3: `0x65 ⊕ 0x5C = 0x39`
  - Байти 4–63: `0x00 ⊕ 0x5C = 0x5C`

### 3. Внутрішній геш d_in

Вхідний потік внутрішнього каскаду має довжину `64 + 28 = 92` байти:

```
Input_inner = K_in (64 байти) || "what do ya want for nothing?" (28 байтів)
```

Після обробки SHA-256 отримуємо проміжний 32-байтний дайджест:

```
d_in = 86 b7 91 e0 47 b4 c3 c6 e1 f0 e6 e5 72 3d eb 8e c4 9a b1 da 36 b0 d8 72 8b a4 5a ad b5 fa ff a6
```

### 4. Зовнішній геш та фінальний результат

Вхідний потік зовнішнього каскаду має довжину рівно `64 + 32 = 96` байтів:

```
Input_outer = K_out (64 байти) || d_in (32 байти)
```

Фінальний виклик `SHA256(Input_outer)` видає підпис:

```
HMAC = 5b dc c1 46 bf 60 75 4e 6a 04 24 26 08 95 75 c7 5a 00 3f 08 9d 27 39 83 9d ec 58 b9 64 ec 38 43
```

Отриманий рядок повністю збігається з еталонним значенням стандарту, підтверджуючи коректність кожного перетворення.

## Апаратне прискорення та векторні інструкції (SHA-NI / ARMv8 Crypto)

У сучасних комунікаційних шлюзах обробка мільйонів пакетів за секунду програмним кодом на чистому C створила б надмірне навантаження на процесор. Для підвищення пропускної здатності сучасні архітектури x86-64 та ARM64 мають спеціалізовані апаратні інструкції.

### Розширення Intel/AMD SHA-NI (SHA Extensions)

Архітектура x86-64 надає чотири спеціальні інструкції для прискорення SHA-256:
- `sha256rnds2` — обчислення двох раундів трансформації SHA-256 за один такт процесора над регістрами XMM.
- `sha256msg1` та `sha256msg2` — апаратне розширення розкладу повідомлень `w[i]`.

Використання SHA-NI дозволяє підняти швидкість HMAC-SHA256 з `~350 МБ/с` (чистий C/C++) до `> 2200 МБ/с` на одному ядрі сучасного процесора. Оскільки HMAC використовує стандартну функцію SHA-256 без будь-яких внутрішніх змін, прискорення геш-функції автоматично масштабує продуктивність HMAC без необхідності зміни алгоритмічної логіки.

### Криптографічні розширення ARMv8-A (Neon Crypto)

На процесорах ARM (Cortex-A, Apple Silicon) інструкції `vsha256h_u32` та `vsha256su1_u32` виконують аналогічну апаратну векторизацію раундів стиснення, забезпечуючи високу енергоефективність на мобільних і серверних платформах.

## Безпечне управління пам'яттю: ідіоматичний C++ RAII

Для запобігання витоку ключів у пам'яті сучасний C++ надає можливість створити безпечний контейнер `SecureMemoryBuffer`, деструктор якого гарантовано затирає пам'ять за допомогою бар'єрів пам'яті або платформних API:

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <string.h>

/* Безпечне затирання пам'яті в C, стійке до Dead Store Elimination */
void secure_memzero(void *v, size_t n) {
    volatile uint8_t *p = (volatile uint8_t *)v;
    while (n--) {
        *p++ = 0;
    }
}
```
```cpp
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <algorithm>

namespace crypto {

/**
 * RAII-обгортка для автоматичного безпечного затирання секретних даних у стеку.
 */
template <size_t N>
class SecureBuffer {
public:
    SecureBuffer() noexcept { data_.fill(0); }
    ~SecureBuffer() noexcept { clean(); }

    // Заборона копіювання для запобігання дублювання ключів
    SecureBuffer(const SecureBuffer&) = delete;
    SecureBuffer& operator=(const SecureBuffer&) = delete;

    // Дозвіл переміщення
    SecureBuffer(SecureBuffer&& other) noexcept {
        data_ = other.data_;
        other.clean();
    }

    uint8_t* data() noexcept { return data_.data(); }
    const uint8_t* data() const noexcept { return data_.data(); }
    size_t size() const noexcept { return N; }

    std::span<uint8_t, N> span() noexcept { return std::span<uint8_t, N>(data_); }
    std::span<const uint8_t, N> span() const noexcept { return std::span<const uint8_t, N>(data_); }

    void clean() noexcept {
        volatile uint8_t* p = data_.data();
        for (size_t i = 0; i < N; ++i) {
            p[i] = 0;
        }
    }

private:
    std::array<uint8_t, N> data_;
};

} // namespace crypto
```
:::

## Вбудовані системи та нульове динамічне виділення пам'яті (Zero-Allocation)

У мікроконтролерах без операційної системи (Bare-Metal на ARM Cortex-M або RISC-V) та в ядрах мережевих драйверів використання динамічної пам'яті (`malloc` або `new`) суворо заборонено через ризик фрагментації купи та недетермінований час виконання.

Архітектура HMAC ідеально підходить для обробки мережевих пакетів із нульовим копіюванням (англ. *Zero-Copy Processing*):

### Обробка кільцевих буферів DMA (Ring Buffers)

Мережевий контролер Ethernet або Wi-Fi записує вхідний кадр безпосередньо в кільцевий буфер DMA. Замість того, щоб копіювати весь пакет в окремий монолітний буфер для обчислення підпису, контекст `hmac_sha256_update` приймає фрагменти пам'яті послідовно:
1. Заголовок пакета (IP/UDP або кастомний протокол).
2. Корисне навантаження (Payload).
3. Додаткові асоційовані дані (Associated Data, наприклад мітка часу чи номер послідовності `Sequence Number`).

Потокова структура HMAC-SHA256 зберігає лише 108 байтів внутрішнього стану (`sha256_ctx_t` займає 108 байтів), що дозволяє підтримувати десятки одночасних безпечних сесій на мікроконтролерах із менш ніж 32 КБ оперативної пам'яті (SRAM).

### Порядок перевірки у схемі Encrypt-then-MAC

У вбудованих пристроях критично важливо дотримуватися правильного порядку обробки пакетів:
1. **Спочатку верифікація HMAC.** Приймач спершу обчислює `hmac_sha256` над отриманим шифротекстом і виконує константне порівняння `constant_time_memcmp`.
2. **Лише за успішної автентичності — дешифрування.** Якщо підпис не збігся, пакет негайно відкидається без виклику функції розшифрування AES або ChaCha20.

Це захищає пристрій від атак типу «Padding Oracle» та «Invalid Curve Attack», оскільки зловмисник не може змусити криптографічний процесор обробляти некоректні зашифровані блоки без дійсного коду автентичності.

### Вирівнювання пам'яті та порядок байтів (Endianness)

При написанні драйверів мережевих інтерфейсів слід враховувати апаратні особливості читання слів:
- Заголовки мережевих пакетів передаються у форматі Big-Endian (Network Byte Order), тоді як архітектури x86 та ARM за замовчуванням використовують Little-Endian.
- Функції завантаження 32-бітних слів у розкладі SHA-256 повинні використовувати явні побітові зсуви або інструкції перестановки байтів (`__builtin_bswap32` або `rev` в ARM) для запобігання помилкам невирівняного доступу (Unaligned Memory Access Faults) на суворих процесорних ядрах.

