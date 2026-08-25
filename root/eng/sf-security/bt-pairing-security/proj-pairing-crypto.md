# ⚙️ Практика: Криптографічні примітиви LE Secure Connections на C та C++

У специфікації Bluetooth Core 4.2+ (LE Secure Connections) усі процедури підтвердження, взаємної автентифікації, генерації довгострокових сеансових ключів та розрахунку 6-значних кодів Numeric Comparison базуються на єдиному криптографічному алгоритмі — **AES-CMAC** (Cipher-based Message Authentication Code, стандартизованому в RFC 4493).

Розробка надійного та захищеного стека безпеки вимагає точного розуміння внутрішньої математики скінченних полів, правил доповнення блоків, порядку байтів та захисту від атак через вимірювання часу виконання.

### 1. Математичні засади алгоритму AES-CMAC

Алгоритм AES-CMAC є вдосконаленням класичного коду автентифікації повідомлень CBC-MAC, позбавленим його фундаментальної вразливості до атак подовження повідомлення (Message Extension Attacks) для повідомлень змінної довжини. Стійкість досягається за рахунок генерації двох додаткових 128-бітних підключів `K1` та `K2`, які накладаються операцією XOR на останній блок даних перед фінальним шифруванням.

#### Генерація підключів у полі Галуа GF(2¹²⁸)
Генерація підключів спирається на множення на примітивний елемент `x` у полі Галуа `GF(2¹²⁸)`, визначеному незвідним поліномом:
```
P(x) = x¹²⁸ + x⁷ + x² + x + 1
```

1. Спершу обчислюється проміжний 128-бітний блок `L = AES-128_K(0¹²⁸)` шляхом шифрування нульового блоку на головному ключі `K`.
2. Якщо старший біт блоку `L` дорівнює 0 (`msb(L) == 0`), то перший підключ `K1 = L << 1` (звичайний бітовий зсув вліво на 1 розряд).
3. Якщо `msb(L) == 1`, то зсунутий блок коригується додаванням константи поля: `K1 = (L << 1) ⊕ R_128`, де `R_128 = 0x87` (тобто молодший байт масиву маскується значенням `0x87`).
4. Другий підключ `K2` генерується аналогічно з `K1`:
   * Якщо `msb(K1) == 0`, то `K2 = K1 << 1`;
   * Якщо `msb(K1) == 1`, то `K2 = (K1 << 1) ⊕ 0x87`.

#### Правила доповнення та ланцюжок CBC
Повідомлення `M` довжиною `len` байтів розбивається на `n` блоків по 16 байтів:
* **Повний останній блок:** Якщо довжина повідомлення кратна 16 байтам і `len > 0`, останній блок `M_n` модифікується підключем `K1`: `M_n* = M_n ⊕ K1`.
* **Неповний останній блок:** Якщо довжина не кратна 16 байтам (або повідомлення порожнє, `len = 0`), до залишку додається біт `1` (байт `0x80`), далі простір заповнюється нулями до 16 байтів, і результат модифікується підключем `K2`: `M_n* = (M_n || 10...0) ⊕ K2`.

Після підготовки блоків виконується стандартне CBC-шифрування з нульовим вектором ініціалізації `C0 = 0¹²⁸`. Фінальний блок `C_n` стає 128-бітним значенням імітовставки CMAC.

---

### 2. Реалізація криптографічних примітивів на C та C++

Нижче наведено самодостатню реалізацію алгоритмів AES-CMAC, функції зобов'язання `f4`, функції генерації коду звірки `g2` та захищеного порівняння за сталий час.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define AES_BLOCK_SIZE 16

/* Зсув 128-бітного блоку вліво на 1 біт у порядку Big-Endian */
static void cmac_shift_left(const uint8_t *in, uint8_t *out) {
    uint8_t overflow = 0;
    for (int i = 15; i >= 0; --i) {
        out[i] = (uint8_t)((in[i] << 1) | overflow);
        overflow = (uint8_t)((in[i] & 0x80) ? 1 : 0);
    }
}

/* Генерація підключів K1 та K2 згідно з RFC 4493 */
static void cmac_generate_subkeys(const uint8_t *key, uint8_t *k1, uint8_t *k2,
                                  void (*aes128_encrypt)(const uint8_t*, const uint8_t*, uint8_t*)) {
    uint8_t zero[AES_BLOCK_SIZE] = {0};
    uint8_t l[AES_BLOCK_SIZE];
    aes128_encrypt(key, zero, l);

    /* Обчислення K1 = (L << 1) ^ (msb(L) ? 0x87 : 0) */
    cmac_shift_left(l, k1);
    if (l[0] & 0x80) {
        k1[15] ^= 0x87;
    }

    /* Обчислення K2 = (K1 << 1) ^ (msb(K1) ? 0x87 : 0) */
    cmac_shift_left(k1, k2);
    if (k1[0] & 0x80) {
        k2[15] ^= 0x87;
    }
}

/* Обчислення AES-CMAC для довільної довжини повідомлення */
void aes_cmac(const uint8_t *key, const uint8_t *msg, size_t len, uint8_t *mac,
              void (*aes128_encrypt)(const uint8_t*, const uint8_t*, uint8_t*)) {
    uint8_t k1[AES_BLOCK_SIZE], k2[AES_BLOCK_SIZE];
    cmac_generate_subkeys(key, k1, k2, aes128_encrypt);

    size_t n_blocks = (len + AES_BLOCK_SIZE - 1) / AES_BLOCK_SIZE;
    if (n_blocks == 0) {
        n_blocks = 1;
    }

    bool last_block_complete = (len > 0) && (len % AES_BLOCK_SIZE == 0);
    uint8_t x[AES_BLOCK_SIZE] = {0};
    uint8_t y[AES_BLOCK_SIZE];

    for (size_t i = 0; i < n_blocks - 1; ++i) {
        for (size_t b = 0; b < AES_BLOCK_SIZE; ++b) {
            y[b] = x[b] ^ msg[i * AES_BLOCK_SIZE + b];
        }
        aes128_encrypt(key, y, x);
    }

    /* Обробка останнього блоку з підключем K1 або K2 */
    uint8_t last_block[AES_BLOCK_SIZE] = {0};
    size_t last_len = len - (n_blocks - 1) * AES_BLOCK_SIZE;
    if (last_block_complete) {
        for (size_t b = 0; b < AES_BLOCK_SIZE; ++b) {
            last_block[b] = msg[(n_blocks - 1) * AES_BLOCK_SIZE + b] ^ k1[b];
        }
    } else {
        if (last_len > 0) {
            memcpy(last_block, msg + (n_blocks - 1) * AES_BLOCK_SIZE, last_len);
        }
        last_block[last_len] = 0x80; /* Доповнення 1000... */
        for (size_t b = 0; b < AES_BLOCK_SIZE; ++b) {
            last_block[b] ^= k2[b];
        }
    }

    for (size_t b = 0; b < AES_BLOCK_SIZE; ++b) {
        y[b] = x[b] ^ last_block[b];
    }
    aes128_encrypt(key, y, mac);
}

/* Функція зобов'язання f4 (Commitment):
   C_a = AES-CMAC_N_a(PKa_x || PKb_x || Z) */
void bt_smp_f4(const uint8_t *pka_x, const uint8_t *pkb_x, const uint8_t *nonce,
               uint8_t z_flag, uint8_t *confirm_out,
               void (*aes128_encrypt)(const uint8_t*, const uint8_t*, uint8_t*)) {
    uint8_t msg[65];
    memcpy(msg, pka_x, 32);
    memcpy(msg + 32, pkb_x, 32);
    msg[64] = z_flag;

    aes_cmac(nonce, msg, sizeof(msg), confirm_out, aes128_encrypt);
}

/* Розрахунок 6-значного коду Numeric Comparison g2:
   V = AES-CMAC_N_a(PKa_x || PKb_x || N_b)[0..3] mod 10^6 */
uint32_t bt_smp_g2(const uint8_t *pka_x, const uint8_t *pkb_x,
                   const uint8_t *na, const uint8_t *nb,
                   void (*aes128_encrypt)(const uint8_t*, const uint8_t*, uint8_t*)) {
    uint8_t msg[80];
    memcpy(msg, pka_x, 32);
    memcpy(msg + 32, pkb_x, 32);
    memcpy(msg + 64, nb, 16);

    uint8_t mac[16];
    aes_cmac(na, msg, sizeof(msg), mac, aes128_encrypt);

    /* Молодші 4 байти в форматі Little-Endian */
    uint32_t raw_val = ((uint32_t)mac[0]) |
                       (((uint32_t)mac[1]) << 8) |
                       (((uint32_t)mac[2]) << 16) |
                       (((uint32_t)mac[3]) << 24);

    return raw_val % 1000000U;
}

/* Захищене порівняння за сталий час проти атак через аналіз часу */
bool bt_smp_constant_time_eq16(const uint8_t *a, const uint8_t *b) {
    uint8_t diff = 0;
    for (size_t i = 0; i < 16; ++i) {
        diff |= (a[i] ^ b[i]);
    }
    return diff == 0;
}
```
```cpp
#include <array>
#include <span>
#include <cstdint>
#include <functional>
#include <algorithm>

namespace bluetooth::crypto {

inline constexpr std::size_t aes_block_size = 16;

using Block = std::array<std::uint8_t, aes_block_size>;
using PointCoord = std::array<std::uint8_t, 32>;
using Nonce = std::array<std::uint8_t, 16>;

using AesEncryptFn = std::function<void(std::span<const std::uint8_t, 16> key,
                                       std::span<const std::uint8_t, 16> in,
                                       std::span<std::uint8_t, 16> out)>;

namespace detail {

constexpr void shift_left(std::span<const std::uint8_t, aes_block_size> in,
                         std::span<std::uint8_t, aes_block_size> out) noexcept {
    std::uint8_t overflow = 0;
    for (int i = static_cast<int>(aes_block_size) - 1; i >= 0; --i) {
        out[i] = static_cast<std::uint8_t>((in[i] << 1) | overflow);
        overflow = static_cast<std::uint8_t>((in[i] & 0x80) ? 1 : 0);
    }
}

void generate_subkeys(std::span<const std::uint8_t, 16> key,
                      Block& k1, Block& k2,
                      const AesEncryptFn& encrypt) {
    Block zero{};
    Block l{};
    encrypt(key, zero, l);

    shift_left(l, k1);
    if (l[0] & 0x80) {
        k1[15] ^= 0x87;
    }

    shift_left(k1, k2);
    if (k1[0] & 0x80) {
        k2[15] ^= 0x87;
    }
}

} // namespace detail

Block aes_cmac(std::span<const std::uint8_t, 16> key,
               std::span<const std::uint8_t> message,
               const AesEncryptFn& encrypt) {
    Block k1{}, k2{};
    detail::generate_subkeys(key, k1, k2, encrypt);

    const auto len = message.size();
    std::size_t n_blocks = (len + aes_block_size - 1) / aes_block_size;
    if (n_blocks == 0) {
        n_blocks = 1;
    }

    const bool last_complete = (len > 0) && (len % aes_block_size == 0);
    Block x{};
    Block y{};

    for (std::size_t i = 0; i < n_blocks - 1; ++i) {
        for (std::size_t b = 0; b < aes_block_size; ++b) {
            y[b] = x[b] ^ message[i * aes_block_size + b];
        }
        encrypt(key, y, x);
    }

    Block last_block{};
    const std::size_t last_len = len - (n_blocks - 1) * aes_block_size;
    if (last_complete) {
        for (std::size_t b = 0; b < aes_block_size; ++b) {
            last_block[b] = message[(n_blocks - 1) * aes_block_size + b] ^ k1[b];
        }
    } else {
        if (last_len > 0) {
            std::copy_n(message.data() + (n_blocks - 1) * aes_block_size, last_len, last_block.data());
        }
        last_block[last_len] = 0x80;
        for (std::size_t b = 0; b < aes_block_size; ++b) {
            last_block[b] ^= k2[b];
        }
    }

    for (std::size_t b = 0; b < aes_block_size; ++b) {
        y[b] = x[b] ^ last_block[b];
    }
    Block mac{};
    encrypt(key, y, mac);
    return mac;
}

/* Функція криптографічного зобов'язання f4 */
Block calculate_f4(const PointCoord& pka_x, const PointCoord& pkb_x,
                   const Nonce& nonce, std::uint8_t z_flag,
                   const AesEncryptFn& encrypt) {
    std::array<std::uint8_t, 65> msg{};
    std::copy_n(pka_x.data(), 32, msg.data());
    std::copy_n(pkb_x.data(), 32, msg.data() + 32);
    msg[64] = z_flag;

    return aes_cmac(nonce, msg, encrypt);
}

/* Розрахунок 6-значного коду Numeric Comparison g2 */
std::uint32_t calculate_g2(const PointCoord& pka_x, const PointCoord& pkb_x,
                           const Nonce& na, const Nonce& nb,
                           const AesEncryptFn& encrypt) {
    std::array<std::uint8_t, 80> msg{};
    std::copy_n(pka_x.data(), 32, msg.data());
    std::copy_n(pkb_x.data(), 32, msg.data() + 32);
    std::copy_n(nb.data(), 16, msg.data() + 64);

    const Block mac = aes_cmac(na, msg, encrypt);

    const std::uint32_t raw_val = static_cast<std::uint32_t>(mac[0]) |
                                 (static_cast<std::uint32_t>(mac[1]) << 8) |
                                 (static_cast<std::uint32_t>(mac[2]) << 16) |
                                 (static_cast<std::uint32_t>(mac[3]) << 24);

    return raw_val % 1000000U;
}

/* Захищене порівняння за сталий час (Constant-time equality) */
[[nodiscard]] bool constant_time_compare(std::span<const std::uint8_t, 16> a,
                                         std::span<const std::uint8_t, 16> b) noexcept {
    std::uint8_t diff = 0;
    for (std::size_t i = 0; i < 16; ++i) {
        diff |= static_cast<std::uint8_t>(a[i] ^ b[i]);
    }
    return diff == 0;
}

} // namespace bluetooth::crypto
```
:::

---

### 3. Функції деривації ключів f5, f6 та крос-транспортний протокол h6/h7

#### Функція f5 (генерація MacKey та LTK)
Функція `f5` виводить 256 біт сеансового матеріалу зі спільного секрету `DHKey` (координата `x` точки `Z` на еліптичній кривій P-256) за схемою HKDF-подібної структури на базі AES-CMAC:

1. Спершу обчислюється ключ зв'язку `T = AES-CMAC_Salt(DHKey)`, де `Salt` — фіксована 128-бітна константа:
   ```
   Salt = 0x6C888391AAF5A53860370BDB5A6083BE
   ```
2. Потім генеруються два блоки по 128 біт із лічильниками `0x00` та `0x01`:
   ```
   MacKey = AES-CMAC_T(0x00 || "btle" || N_a || N_b || A_1 || A_2 || 0x0100)
   LTK    = AES-CMAC_T(0x01 || "btle" || N_a || N_b || A_1 || A_2 || 0x0100)
   ```
   де `N_a, N_b` — 128-бітні випадкові числа сторін, `A_1, A_2` — 7-байтні структури адрес вузлів (`Address_Type (1B) || BD_ADDR (6B)`), а `0x0100` — 16-бітне позначення довжини виходу (256 біт).

#### Функція перевірки f6 (DHKey Check)
Функція `f6` гарантує, що обидві сторони обчислили ідентичний `DHKey` і володіють узгодженим `MacKey`, перш ніж активувати шифрування каналу:
```
E_a = AES-CMAC_MacKey(N_a || N_b || R || IOCap_A || A_1 || A_2)
E_b = AES-CMAC_MacKey(N_b || N_a || R || IOCap_B || A_2 || A_1)
```
де `R` — 128-бітне число (для Numeric Comparison `R = 0`, для Passkey `R = passkey`, для OOB `R = r_oob`).

#### Крос-транспортні функції h6 та h7 (CTKD)
Для виведення ключа класичного Bluetooth `LinkKey` із довгострокового ключа `LTK` стандарту LE Secure Connections застосовується функція `h6`:
```
LinkKey = AES-CMAC_LTK("tmp1" || "br/edr")
```
Якщо обидва пристрої заявили підтримку розширення `CT2` у полі `AuthReq`, використовується вдосконалена функція `h7`, яка замість простого текстового префіксу застосовує диверсифікацію через сіль:
```
LinkKey = AES-CMAC_IL("br/edr"), де IL = AES-CMAC_Salt(LTK)
```

---

### 4. Верифікація за еталонними тестовими векторами Bluetooth SIG

Для перевірки коректності програмної реалізації додаток Bluetooth Core Specification Vol 3, Part H, Appendix C надає офіційні еталонні вектори:

1. **Тестовий вектор f4 (Commitment):**
   * Відкритий ключ `PK_a (X)`: `0x2c31a47b57798b5e8c336d66b301383777e85a7eedfa6a44664c4247ab648d65`
   * Відкритий ключ `PK_b (X)`: `0x90a1229793389512acf300873e7e63413a4dd94a241e3a897f410528f0a13671`
   * Випадкове число `N_a`: `0x75140e34750e79e14e7c0944f6d1b2a6`
   * Прапорець `Z`: `0x00`
   * Еталонний результат `C_a`: `0x2d8774a9be0a470d0096218d25514a29`
2. **Тестовий вектор g2 (Numeric Comparison):**
   * Вхідні точки `PK_a(X)` та `PK_b(X)` з прикладу f4
   * Числа `N_a`: `0x75140e34750e79e14e7c0944f6d1b2a6`, `N_b`: `0xd842440a3e2646f8828c89b704e62add`
   * Повний 128-бітний вихід CMAC: `0xe39d34dae3d74c0496453418c8810723`
   * Молодші 4 байти у форматі Little-Endian: `0xda349de3 = 3660881379`
   * Код на екрані `V = 3660881379 mod 1000000 = 881379`.

---

### 5. Критичні пастки розробки та аналіз атак через вимірювання часу

#### Пастка порядку байтів (Endianness Mismatch)
Стандарт RFC 4493 визначає алгоритми AES та CMAC для даних у порядку **Big-Endian** (найстарший байт перший). Водночас специфікація Bluetooth Core Vol 3 Part H визначає всі пакети SMP, координати відкритих ключів еліптичних кривих `(X, Y)` та випадкові числа `Nonce` у порядку **Little-Endian** (наймолодший байт перший).

Якщо програмний стек передає байти в криптографічний драйвер апаратного прискорювача (наприклад, у криптомодуль ESP32 або STM32 Crypto HAL) без попередньої зміни порядку байтів на протилежний, результуючий геш буде розраховано від дзеркально оберненого масиву. Це найпоширеніша причина, чому пристрої різних виробників не можуть завершити фазу `DHKey Check` і скидають з'єднання з кодом `DHKey Check Failed (0x0B)`.

#### Атаки за часом виконання на функцію перевірки (Timing Attacks)
Найнебезпечніша помилка розробника — використання бібліотечних функцій порівняння пам'яті зі змінним часом виконання:

:::tabs
```c
/* Вразливий підхід у C: memcmp завершується на першому незбігу */
if (memcmp(local_eb, remote_eb, 16) == 0) {
    /* Небезпечно: вразливо до атак за часом! */
}
```
```cpp
// Вразливий підхід у C++: std::equal без сталого часу
if (std::equal(local_eb.begin(), local_eb.end(), remote_eb.begin())) {
    // Небезпечно: вразливо до атак за часом!
}
```
:::

Функція `memcmp()` оптимізована для швидкодії й перериває виконання на **першому ж байті, що не збігся**. Зловмисник, вимірюючи час між відправкою підробленого пакета `Pairing DHKey Check` та моментом надходження кадру `Pairing Failed`, може з точністю до мікросекунд визначити, скільки перших байтів було вгадано правильно. Це дозволяє методом послідовного підбору знайти всі 16 байтів автентифікаційного вектора за 4096 запитів (16 × 256) замість 2¹²⁸ повного перебору.

Правильна реалізація зобов'язана виконувати операцію порозрядного складання за модулем 2 (`XOR`) для всіх байтів масиву без жодних ранніх виходів із циклу (`constant-time XOR`), як це продемонстровано у функції `bt_smp_constant_time_eq16()`.
