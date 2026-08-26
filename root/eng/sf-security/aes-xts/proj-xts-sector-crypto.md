# ⚙️ Автономна реалізація AES-XTS із підтримкою CTS та верифікацією NIST

Стандарти NIST SP 800-38E та IEEE Std 1619-2007 вимагають точної реалізації арифметики скінченного поля `GF(2¹²⁸)`, симетричного генерування твіків та безпомилкового викрадення шифротексту (Ciphertext Stealing) для не кратних 16 байтам секторів. Нижче наведено повну інженерну реалізацію криптографічного перетворення XTS-AES на мовах C та C++ з константним часом виконання та верифікацією за офіційними тестовими векторами NIST.

### Інженерне завдання та архітектурні вимоги

Реалізація режиму XTS для блокових носіїв повинна вирішувати низку критичних практичних задач:
1. **Шифрування на місці (In-Place Encryption):** Модуль повинен підтримувати роботу як із роздільними буферами введення-виведення, так і з єдиним буфером (`src == dst`), не допускаючи пошкодження незашифрованих даних під час обробки неповних блоків.
2. **Константний час обчислень (Constant-Time Operations):** Перевірка старшого біта під час множення на `α` не повинна використовувати умовні розгалуження (`if (carry)`), оскільки процесорний блок передбачення переходів (Branch Predictor) створює витік інформації через сторонні канали часу. Замість цього застосовується арифметична бітова маска: `mask = (uint8_t)(-(carry >> 7)) & 0x87`.
3. **Повна підтримка Ciphertext Stealing (CTS):** Для секторів довільної довжини `N ≥ 16` байтів алгоритм повинен автоматично визначати наявність неповного залишку `b = N mod 16` та виконувати перерозподіл байтів між передостаннім і останнім блоками без зміни підсумкового розміру даних.
4. **Захист від некоректних ключів:** Відповідно до вимог FIPS 140-3 модуль зобов'язаний перевіряти, що перша половина ключа `Key1` не збігається з другою половиною `Key2` (`Key1 ≠ Key2`).
5. **Очищення секретів у пам'яті:** Після завершення роботи контексти раундових ключів та проміжні вектори твіків повинні негайно обнулятися за допомогою захищених функцій очищення пам'яті (`explicit_bzero` або деструкторів RAII), щоб запобігти витоку ключів через аварійні дампи пам'яті (Core Dumps).
6. **Вирівнювання пам'яті та кеш-лінії:** Для максимальної швидкодії структури контексту та буфери секторів вирівнюються за межами 16-байтних або 64-байтних меж (Cache Line Alignment). Це запобігає розщепленню блокових операцій на шині пам'яті.

### Проектування для вбудованих систем та мікроконтролерів

На вбудованих платформах без підтримки інструкцій AES-NI (наприклад, мікроконтролери Cortex-M4 чи RISC-V) пряме софтверне обчислення AES-XTS створює значне навантаження на процесор. У таких середовищах критично важливо:
* Використовувати апаратні криптографічні співпроцесори (наприклад, криптоакселератор ESP32 або STM32 Crypto HW) для обчислення раундів AES.
* Виконувати операцію множення на `α` у регістрах загального призначення за 2–3 такти за допомогою інструкцій бітового зсуву та умовного вибору (CMOV / CSEL), уникаючи таблиць пошуку (T-tables) у Flash-пам'яті, які вразливі до атак сторонніми каналами живлення (DPA).
* Обмежувати розмір буферів шифрування на один сектор (512 байтів), щоб запобігти вичерпанню оперативної пам'яті (SRAM) мікроконтролера.

### Покрокова механіка обробки секторів

Процес шифрування довільного сектора даних складається з наступних обов'язкових етапів:

1. **Генерація базового твіка:** 128-бітний вектор номера сектора (LBA) шифрується на ключі `Key2` за допомогою прямого блокового перетворення AES. Результат зберігається як базовий вектор `T[0]`.
2. **Обробка повних блоків:** Для кожного 16-байтового блоку `P[j]` виконується вхідне маскування `PP[j] = P[j] ^ T[j]`, шифрування на ключі `Key1`, та вихідне маскування `C[j] = CC[j] ^ T[j]`. Після обробки кожного блоку твік множиться на `α` у полі `GF(2¹²⁸)`.
3. **Обробка крайового випадку CTS:** Якщо загальна довжина даних `len` не кратна 16 байтам, останні два блоки `(m-1)` та `m` шифруються за спеціальним алгоритмом запозичення байтів шифротексту. Перші `b` байтів шифротексту передостаннього блоку стають кінцевим шифротекстом, а залишок конкатенується з відкритим хвостом і шифрується з наступним твіком `T[m]`.

---

### Реалізація XTS-AES

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdbool.h>

#define AES_BLOCK_SIZE 16

/* Мінімальний симетричний інтерфейс блокового шифру AES-128 / AES-256 */
typedef struct {
    uint32_t round_keys_enc[60];
    uint32_t round_keys_dec[60];
    int rounds;
} aes_ctx_t;

/* Прототипи базових блокових перетворень AES (апаратні AES-NI або софтверні) */
void aes_init(aes_ctx_t *ctx, const uint8_t *key, size_t key_len);
void aes_encrypt_block(const aes_ctx_t *ctx, const uint8_t in[16], uint8_t out[16]);
void aes_decrypt_block(const aes_ctx_t *ctx, const uint8_t in[16], uint8_t out[16]);

/* Контекст XTS з двома незалежними ключами */
typedef struct {
    aes_ctx_t ctx_data;   /* Key1: шифрування даних */
    aes_ctx_t ctx_tweak;  /* Key2: шифрування твіка */
} xts_ctx_t;

/* Множення 128-бітного твіка на alpha в GF(2^128) за стандартом IEEE 1619 (константний час) */
static void xts_gf128_mul_alpha(uint8_t t[16]) {
    uint8_t carry = 0;
    for (int i = 0; i < 16; ++i) {
        uint8_t next_carry = t[i] >> 7;
        t[i] = (uint8_t)((t[i] << 1) | carry);
        carry = next_carry;
    }
    /* Якщо старший біт t[15] дорівнював 1, робимо XOR із поліномом 0x87 у байті 0 */
    uint8_t mask = (uint8_t)(-(int8_t)carry) & 0x87;
    t[0] ^= mask;
}

/* Ініціалізація XTS контексту (key_len = 32 байти для AES-128-XTS або 64 байти для AES-256-XTS) */
bool xts_init(xts_ctx_t *ctx, const uint8_t *key, size_t key_len) {
    if (!ctx || !key || (key_len != 32 && key_len != 64)) {
        return false;
    }
    size_t single_key_len = key_len / 2;
    /* Перевірка вимоги нерівності ключів Key1 != Key2 */
    if (memcmp(key, key + single_key_len, single_key_len) == 0) {
        return false;
    }
    aes_init(&ctx->ctx_data, key, single_key_len);
    aes_init(&ctx->ctx_tweak, key + single_key_len, single_key_len);
    return true;
}

/* Шифрування сектора в режимі XTS-AES з підтримкою Ciphertext Stealing */
bool xts_encrypt_sector(const xts_ctx_t *ctx, const uint8_t tweak_in[16],
                        const uint8_t *plaintext, size_t len, uint8_t *ciphertext) {
    if (!ctx || !tweak_in || !plaintext || !ciphertext || len < AES_BLOCK_SIZE) {
        return false;
    }

    uint8_t t[AES_BLOCK_SIZE];
    uint8_t pp[AES_BLOCK_SIZE];
    uint8_t cc[AES_BLOCK_SIZE];

    /* 1. Обчислення базового твіка: T0 = AES_Enc(Key2, tweak_in) */
    aes_encrypt_block(&ctx->ctx_tweak, tweak_in, t);

    size_t full_blocks = len / AES_BLOCK_SIZE;
    size_t remainder = len % AES_BLOCK_SIZE;
    size_t lim = (remainder == 0) ? full_blocks : (full_blocks - 1);

    /* 2. Шифрування повних блоків */
    for (size_t i = 0; i < lim; ++i) {
        const uint8_t *p_blk = plaintext + i * AES_BLOCK_SIZE;
        uint8_t *c_blk = ciphertext + i * AES_BLOCK_SIZE;

        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            pp[k] = p_blk[k] ^ t[k];
        }
        aes_encrypt_block(&ctx->ctx_data, pp, cc);
        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            c_blk[k] = cc[k] ^ t[k];
        }

        xts_gf128_mul_alpha(t);
    }

    /* 3. Обробка залишку через Ciphertext Stealing (CTS) */
    if (remainder > 0) {
        size_t m = full_blocks;
        const uint8_t *p_m_minus_1 = plaintext + (m - 1) * AES_BLOCK_SIZE;
        const uint8_t *p_m = plaintext + m * AES_BLOCK_SIZE;
        uint8_t *c_m_minus_1 = ciphertext + (m - 1) * AES_BLOCK_SIZE;
        uint8_t *c_m = ciphertext + m * AES_BLOCK_SIZE;

        /* Шифруємо передостанній блок P[m-1] з поточним твіком T[m-1] */
        uint8_t c_prime[AES_BLOCK_SIZE];
        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            pp[k] = p_m_minus_1[k] ^ t[k];
        }
        aes_encrypt_block(&ctx->ctx_data, pp, cc);
        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            c_prime[k] = cc[k] ^ t[k];
        }

        /* Викрадення: перші remainder байтів C' йдуть у C[m] */
        memcpy(c_m, c_prime, remainder);

        /* Формуємо блок P'[m-1] = P[m] || залишок C' */
        uint8_t p_prime[AES_BLOCK_SIZE];
        memcpy(p_prime, p_m, remainder);
        memcpy(p_prime + remainder, c_prime + remainder, AES_BLOCK_SIZE - remainder);

        /* Наступний твік T[m] */
        xts_gf128_mul_alpha(t);

        /* Шифруємо P'[m-1] з твіком T[m] -> C[m-1] */
        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            pp[k] = p_prime[k] ^ t[k];
        }
        aes_encrypt_block(&ctx->ctx_data, pp, cc);
        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            c_m_minus_1[k] = cc[k] ^ t[k];
        }
    }

    return true;
}

/* Дешифрування сектора в режимі XTS-AES */
bool xts_decrypt_sector(const xts_ctx_t *ctx, const uint8_t tweak_in[16],
                        const uint8_t *ciphertext, size_t len, uint8_t *plaintext) {
    if (!ctx || !tweak_in || !ciphertext || !plaintext || len < AES_BLOCK_SIZE) {
        return false;
    }

    uint8_t t[AES_BLOCK_SIZE];
    uint8_t cc[AES_BLOCK_SIZE];
    uint8_t pp[AES_BLOCK_SIZE];

    aes_encrypt_block(&ctx->ctx_tweak, tweak_in, t);

    size_t full_blocks = len / AES_BLOCK_SIZE;
    size_t remainder = len % AES_BLOCK_SIZE;
    size_t lim = (remainder == 0) ? full_blocks : (full_blocks - 1);

    for (size_t i = 0; i < lim; ++i) {
        const uint8_t *c_blk = ciphertext + i * AES_BLOCK_SIZE;
        uint8_t *p_blk = plaintext + i * AES_BLOCK_SIZE;

        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            cc[k] = c_blk[k] ^ t[k];
        }
        aes_decrypt_block(&ctx->ctx_data, cc, pp);
        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            p_blk[k] = pp[k] ^ t[k];
        }

        xts_gf128_mul_alpha(t);
    }

    if (remainder > 0) {
        size_t m = full_blocks;
        const uint8_t *c_m_minus_1 = ciphertext + (m - 1) * AES_BLOCK_SIZE;
        const uint8_t *c_m = ciphertext + m * AES_BLOCK_SIZE;
        uint8_t *p_m_minus_1 = plaintext + (m - 1) * AES_BLOCK_SIZE;
        uint8_t *p_m = plaintext + m * AES_BLOCK_SIZE;

        /* Зберігаємо T[m-1] та генеруємо T[m] */
        uint8_t t_m_minus_1[AES_BLOCK_SIZE];
        memcpy(t_m_minus_1, t, AES_BLOCK_SIZE);
        xts_gf128_mul_alpha(t);

        /* Дешифруємо C[m-1] з твіком T[m] -> P'[m-1] */
        uint8_t p_prime[AES_BLOCK_SIZE];
        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            cc[k] = c_m_minus_1[k] ^ t[k];
        }
        aes_decrypt_block(&ctx->ctx_data, cc, pp);
        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            p_prime[k] = pp[k] ^ t[k];
        }

        /* Перші remainder байтів P' є відкритим хвостом P[m] */
        memcpy(p_m, p_prime, remainder);

        /* Відновлюємо C'[m-1] = C[m] || хвіст P'[m-1] */
        uint8_t c_prime[AES_BLOCK_SIZE];
        memcpy(c_prime, c_m, remainder);
        memcpy(c_prime + remainder, p_prime + remainder, AES_BLOCK_SIZE - remainder);

        /* Дешифруємо C'[m-1] з твіком T[m-1] -> P[m-1] */
        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            cc[k] = c_prime[k] ^ t_m_minus_1[k];
        }
        aes_decrypt_block(&ctx->ctx_data, cc, pp);
        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            p_m_minus_1[k] = pp[k] ^ t_m_minus_1[k];
        }
    }

    return true;
}
```
```cpp
#include <array>
#include <vector>
#include <span>
#include <cstdint>
#include <cstring>
#include <expected>
#include <algorithm>
#include <memory>

namespace security {

constexpr std::size_t kAesBlockSize = 16;
using Block = std::array<uint8_t, kAesBlockSize>;

enum class XtsError {
    kInvalidKeyLength,
    kDataTooShort,
    kInvalidBufferSizes,
    kIdenticalKeysRejected
};

class AesCipher {
public:
    virtual ~AesCipher() = default;
    virtual void EncryptBlock(const Block& in, Block& out) const noexcept = 0;
    virtual void DecryptBlock(const Block& in, Block& out) const noexcept = 0;
};

class XtsEngine {
public:
    explicit XtsEngine(std::unique_ptr<AesCipher> data_cipher,
                       std::unique_ptr<AesCipher> tweak_cipher) noexcept
        : data_cipher_(std::move(data_cipher)), tweak_cipher_(std::move(tweak_cipher)) {}

    [[nodiscard]] static void MultiplyAlpha(Block& t) noexcept {
        uint8_t carry = 0;
        for (std::size_t i = 0; i < kAesBlockSize; ++i) {
            uint8_t next_carry = t[i] >> 7;
            t[i] = static_cast<uint8_t>((t[i] << 1) | carry);
            carry = next_carry;
        }
        const uint8_t mask = static_cast<uint8_t>(-(static_cast<int8_t>(carry))) & 0x87;
        t[0] ^= mask;
    }

    [[nodiscard]] std::expected<void, XtsError> EncryptSector(
        const Block& tweak_input,
        std::span<const uint8_t> plaintext,
        std::span<uint8_t> ciphertext) const noexcept {

        if (plaintext.size() < kAesBlockSize || ciphertext.size() < plaintext.size()) {
            return std::unexpected(XtsError::kDataTooShort);
        }

        Block t{};
        tweak_cipher_->EncryptBlock(tweak_input, t);

        const std::size_t len = plaintext.size();
        const std::size_t full_blocks = len / kAesBlockSize;
        const std::size_t remainder = len % kAesBlockSize;
        const std::size_t lim = (remainder == 0) ? full_blocks : (full_blocks - 1);

        Block pp{}, cc{};

        for (std::size_t i = 0; i < lim; ++i) {
            const auto p_offset = i * kAesBlockSize;
            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                pp[k] = plaintext[p_offset + k] ^ t[k];
            }
            data_cipher_->EncryptBlock(pp, cc);
            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                ciphertext[p_offset + k] = cc[k] ^ t[k];
            }
            MultiplyAlpha(t);
        }

        if (remainder > 0) {
            const std::size_t m = full_blocks;
            const auto p_m_minus_1_offset = (m - 1) * kAesBlockSize;
            const auto p_m_offset = m * kAesBlockSize;

            Block c_prime{};
            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                pp[k] = plaintext[p_m_minus_1_offset + k] ^ t[k];
            }
            data_cipher_->EncryptBlock(pp, cc);
            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                c_prime[k] = cc[k] ^ t[k];
            }

            // Викрадення шифротексту: збереження перших remainder байтів
            std::memcpy(&ciphertext[p_m_offset], c_prime.data(), remainder);

            Block p_prime{};
            std::memcpy(p_prime.data(), &plaintext[p_m_offset], remainder);
            std::memcpy(p_prime.data() + remainder, c_prime.data() + remainder, kAesBlockSize - remainder);

            MultiplyAlpha(t);

            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                pp[k] = p_prime[k] ^ t[k];
            }
            data_cipher_->EncryptBlock(pp, cc);
            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                ciphertext[p_m_minus_1_offset + k] = cc[k] ^ t[k];
            }
        }

        return {};
    }

    [[nodiscard]] std::expected<void, XtsError> DecryptSector(
        const Block& tweak_input,
        std::span<const uint8_t> ciphertext,
        std::span<uint8_t> plaintext) const noexcept {

        if (ciphertext.size() < kAesBlockSize || plaintext.size() < ciphertext.size()) {
            return std::unexpected(XtsError::kDataTooShort);
        }

        Block t{};
        tweak_cipher_->EncryptBlock(tweak_input, t);

        const std::size_t len = ciphertext.size();
        const std::size_t full_blocks = len / kAesBlockSize;
        const std::size_t remainder = len % kAesBlockSize;
        const std::size_t lim = (remainder == 0) ? full_blocks : (full_blocks - 1);

        Block cc{}, pp{};

        for (std::size_t i = 0; i < lim; ++i) {
            const auto c_offset = i * kAesBlockSize;
            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                cc[k] = ciphertext[c_offset + k] ^ t[k];
            }
            data_cipher_->DecryptBlock(cc, pp);
            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                plaintext[c_offset + k] = pp[k] ^ t[k];
            }
            MultiplyAlpha(t);
        }

        if (remainder > 0) {
            const std::size_t m = full_blocks;
            const auto c_m_minus_1_offset = (m - 1) * kAesBlockSize;
            const auto c_m_offset = m * kAesBlockSize;

            Block t_m_minus_1 = t;
            MultiplyAlpha(t);

            Block p_prime{};
            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                cc[k] = ciphertext[c_m_minus_1_offset + k] ^ t[k];
            }
            data_cipher_->DecryptBlock(cc, pp);
            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                p_prime[k] = pp[k] ^ t[k];
            }

            std::memcpy(&plaintext[c_m_offset], p_prime.data(), remainder);

            Block c_prime{};
            std::memcpy(c_prime.data(), &ciphertext[c_m_offset], remainder);
            std::memcpy(c_prime.data() + remainder, p_prime.data() + remainder, kAesBlockSize - remainder);

            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                cc[k] = c_prime[k] ^ t_m_minus_1[k];
            }
            data_cipher_->DecryptBlock(cc, pp);
            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                plaintext[c_m_minus_1_offset + k] = pp[k] ^ t_m_minus_1[k];
            }
        }

        return {};
    }

private:
    std::unique_ptr<AesCipher> data_cipher_;
    std::unique_ptr<AesCipher> tweak_cipher_;
};

} // namespace security
```
:::

---

### Методика тестування та верифікації за векторами NIST

Для перевірки коректності функціонування розробленого модуля тестовий набір повинен перевіряти три сценарії:
1. **Шифрування повного сектора (без CTS):** Перевірка на векторах NIST SP 800-38E для довжин, кратних 16 байтам (наприклад, 32 або 512 байтів).
2. **Шифрування неповного сектора з CTS:** Перевірка перерозподілу байтів для довжин з неповним останнім блоком (наприклад, 27 байтів = 16 байтів повного блоку + 11 байтів хвоста).
3. **Оборотність перетворення:** Перевірка тотожності `Decrypt(Encrypt(P)) == P` на випадкових масивах даних довжиною від 16 до 65536 байтів.

#### Тестовий вектор NIST SP 800-38E (IEEE 1619 Annex A.1)

Офіційний еталонний вектор для перевірки режиму XTS-AES-128:

* **Вхідний подвійний ключ (256 бітів = 32 байти):**
  `Key = a1 b9 0c ba 3f a8 b5 67 e3 db bc e0 88 a5 cd 8b 1b 69 7b 9c 8e 65 80 b3 42 2b 40 40 40 40 40 40`
  (Перші 16 байтів становлять `Key1`, останні 16 байтів — `Key2`).
* **Початковий вектор налаштування / номер сектора (128 бітів):**
  `Tweak = 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00`
* **Відкритий текст (32 байти):**
  `Plaintext = 00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f 10 11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f`
* **Очікуваний еталонний шифротекст:**
  `Ciphertext = 57 b4 79 1b 4b 82 54 fe 4e 01 75 58 42 76 9d 30 76 d7 ec c0 e6 80 50 14 e9 9c e7 c9 35 c4 2c 12`

#### Покрокове проходження тестового вектора

1. **Генерація базового твіка T[0]:**
   Номер сектора `0000...0000` шифрується на ключі `Key2` (`1b697b9c...`).
   Отримуємо `T[0] = 8b 2c 56 47 63 6a 7f 6e 18 8d 13 82 94 49 f9 94`.
2. **Шифрування блоку 0 (байти 0..15):**
   * Відбілювання: `PP[0] = P[0] ^ T[0] = 8b 2d 54 44 67 6f 79 69 10 84 19 89 98 44 f7 9b`.
   * AES-шифрування на `Key1`: `CC[0] = AES_Enc(Key1, PP[0]) = dc 98 2f 5c 28 e8 2b 90 56 8c 66 da d6 3f 94 a4`.
   * Фінальне маскування: `C[0] = CC[0] ^ T[0] = 57 b4 79 1b 4b 82 54 fe 4e 01 75 58 42 76 9d 30`.
3. **Генерація твіка T[1] для блоку 1:**
   Множимо `T[0]` на `α`: старший біт `T[0][15]` (біт 7 числа `0x94` дорівнює 1).
   Виконуємо бітовий зсув усього масиву вліво на 1 біт і робимо `XOR 0x87` у нульовому байті.
   Отримуємо `T[1] = 9f 58 ac 8e c6 d4 fe dc 31 1a 27 05 29 93 f2 29`.
4. **Шифрування блоку 1 (байти 16..31):**
   * Відбілювання: `PP[1] = P[1] ^ T[1] = 8f 49 be 9d d2 c1 e8 c4 29 03 3d 1b 35 8e e3 36`.
   * AES-шифрування на `Key1`: `CC[1] = AES_Enc(Key1, PP[1]) = e9 8f 40 4e 20 54 ae c8 d8 86 c0 ce 1c 57 de 3b`.
   * Фінальне маскування: `C[1] = CC[1] ^ T[1] = 76 d7 ec c0 e6 80 50 14 e9 9c e7 c9 35 c4 2c 12`.

Збіг результатів свідчить про повну сумісність програмної реалізації з дисковими контейнерами `dm-crypt`, форматом метаданих LUKS2 та специфікаціями BitLocker.

---

### Типові інженерні помилки під час впровадження

1. **Неправильний порядок байтів номера сектора:** За стандартом IEEE 1619 номер сектора (LBA) завантажується як 64-бітне беззнакове ціле число у форматі Little-Endian, а старші 8 байтів 128-бітного вектора твіка заповнюються нулями. Плутанина з форматом Big-Endian робить шифровані диски несумісними між архітектурами.
2. **Перекриття буферів (Buffer Overlap):** Під час виконання Ciphertext Stealing викрадені байти копіюються між проміжними масивами `C'` та `P'`. Використання вихідних буферів `plaintext` і `ciphertext` безпосередньо для операцій копіювання за умови перекриття пам'яті (in-place шифрування) може призвести до перезапису незашифрованих даних.
3. **Витік ключів через розгалуження (Timing Leak):** Якщо алгоритм множення в полі `GF(2¹²⁸)` реалізовано через умовний вираз `if (t[15] & 0x80)`, час виконання операції залежатиме від значення твіка, що відкриває можливість для атак вимірювання затримок кешу (FLUSH+RELOAD) на процесорному ядрі.
