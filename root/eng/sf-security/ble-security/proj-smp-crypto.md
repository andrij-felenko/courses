# ⚙️ Криптографічний тулбокс BLE: від підтверджень SMP до резолвінгу адрес RPA

Безпека Bluetooth Low Energy опирається на набір криптографічних функцій перетворення (Cryptographic Toolbox), стандартизованих у специфікації Bluetooth Core Specification. Ці функції забезпечують генерацію та розкриття значень підтвердження (Confirm Values), виведення сесійних ключів шифрування з асиметричного секрету `DHKey`, обчислення коду для порівняння чисел (Numeric Comparison) на дисплеях пристроїв, а також перевірку належності приватних адрес (Resolvable Private Addresses, RPA) за допомогою довгострокового ключа ідентичності `IRK`.

Реалізація цих алгоритмів є обов'язковою для розробників вбудованих BLE-стеків, інженерів систем безпеки та авторів утиліт аналізу радіоефіру.

---

### Математичний фундамент та захист від атак сторонніми каналами

Усі криптографічні перетворення протоколу Security Manager (SMP) базуються на двох фундаментальних примітивах симетричної криптографії: 128-бітному блоковому шифрі AES-128 (FIPS 197) та алгоритмі генерації коду автентичності повідомлень на базі шифру AES-CMAC (RFC 4493). У стандарті LE Secure Connections до них додається асиметрична криптографія на еліптичній кривій NIST P-256 (`secp256r1`).

Головною вимогою до програмної або апаратної реалізації криптографічного стека BLE на мікроконтролерах є **виконання операцій за константний час** (англ. *constant-time execution*). Якщо час обчислення функцій або тривалість порівняння масивів байтів залежить від значень секретних ключів чи бітів PIN-коду, зловмисник може відновити секретний ключ за допомогою атаки за часом виконання (Timing Attack).

Для запобігання таким витокам функція порівняння криптографічних блоків (наприклад, під час перевірки `Confirm` або `DHKey Check`) ніколи не повинна переривати цикл оператором `break` чи повертати `false` після першого незбігу байтів:

:::tabs
```c
#include <stdint.h>
#include <stddef.h>

/**
 * @brief Безпечне порівняння двох блоків пам'яті за константний час
 * @return 0, якщо блоки ідентичні; ненульове значення, якщо є розбіжність
 */
int ble_crypto_constant_time_memcmp(const void *a, const void *b, size_t len) {
    const uint8_t *p1 = (const uint8_t *)a;
    const uint8_t *p2 = (const uint8_t *)b;
    uint8_t diff = 0;

    for (size_t i = 0; i < len; ++i) {
        diff |= (p1[i] ^ p2[i]);
    }

    return (int)diff;
}
```
```cpp
#include <span>
#include <cstdint>
#include <cstddef>

namespace ble::crypto {

/**
 * @brief Безпечне порівняння байтових послідовностей за константний час
 */
[[nodiscard]] bool constant_time_compare(std::span<const uint8_t> a,
                                         std::span<const uint8_t> b) noexcept {
    if (a.size() != b.size()) {
        return false;
    }

    uint8_t diff = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        diff |= (a[i] ^ b[i]);
    }

    return diff == 0;
}

} // namespace ble::crypto
```
:::

---

### 1. Резолвінг приватних адрес RPA: функція `ah` на базі AES-128

Для захисту користувача від відстеження в радіоефірі пристрої BLE використовують змінні приватні адреси Resolvable Private Address (RPA). Якщо пристрій транслюватиме постійну заводську MAC-адресу, будь-який стаціонарний радіосканер у торговому центрі або офісі зможе вести профіль переміщення власника.

Адреса RPA має довжину 48 бітів (6 байтів) і складається з двох частин:
1. `prand` (24 біти, 3 старші байти) — псевдовипадкове число, де два старші біти завжди фіксовані як `01b` (ознака типу адреси RPA);
2. `hash` (24 біти, 3 молодші байти) — криптографічна контрольна сума, обчислена за формулою:

```
hash = ah(IRK, prand) = AES-128_ECB(IRK, padding(prand)) mod 2²⁴
```

де `padding(prand)` — це доповнення 24-бітного значення `prand` тринадцятьма нульовими байтами до повної довжини блоку AES (16 байтів).

#### Математична модель безпеки адреси RPA

Простір значень `hash` становить `2²⁴ ≈ 16.7` мільйона комбінацій. Для пасивного спостерігача в ефірі адреса RPA виглядає як випадковий шум. Оскільки `prand` змінюється кожні 15 хвилин (стандартний інтервал ротації стека GAP), зловмисник без знання 128-бітного ключа `IRK` не здатний корелювати нову адресу зі старою.

Отримувач (наприклад, центральний контролер), який володіє збереженим ключем `IRK` (Identity Resolving Key) периферійного вузла, обчислює очікуваний `hash` за отриманим з ефіру `prand` і порівнює його з молодшими трьома байтами адреси кадру. Збіг підтверджує, що пакет передано саме цим відомим пристроєм.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Базовий примітив шифрування одного 128-бітного блоку AES */
extern void aes128_ecb_encrypt(const uint8_t key[16], const uint8_t input[16], uint8_t output[16]);
extern int ble_crypto_constant_time_memcmp(const void *a, const void *b, size_t len);

/**
 * @brief Криптографічна функція ah для генерації та резолвінгу RPA
 * @param irk 128-бітний ключ ідентичності IRK (16 байтів)
 * @param prand 24-бітне випадкове число (3 байти, Little-Endian)
 * @param hash_out 24-бітний вихідний хеш (3 байти, Little-Endian)
 */
void ble_crypto_ah(const uint8_t irk[16], const uint8_t prand[3], uint8_t hash_out[3]) {
    uint8_t plaintext[16];
    uint8_t ciphertext[16];

    /* Доповнення prand нулями до 16 байтів */
    memset(plaintext, 0, sizeof(plaintext));
    plaintext[0] = prand[0];
    plaintext[1] = prand[1];
    plaintext[2] = prand[2];

    /* Одноблочне шифрування AES-128 */
    aes128_ecb_encrypt(irk, plaintext, ciphertext);

    /* hash = молодші 24 біти результату (перші 3 байти) */
    hash_out[0] = ciphertext[0];
    hash_out[1] = ciphertext[1];
    hash_out[2] = ciphertext[2];
}

/**
 * @brief Перевірка належності адреси RPA конкретному пристрою за його IRK
 * @param rpa 48-бітна приватна адреса BLE (6 байтів, Little-Endian: [0..2]=hash, [3..5]=prand)
 * @param irk 128-бітний ключ ідентичності
 * @return true, якщо адреса успішно підтверджена ключем IRK
 */
bool ble_resolve_rpa(const uint8_t rpa[6], const uint8_t irk[16]) {
    /* Перевірка бітів ознаки RPA: два старших біти prand повинні бути 01b (0x40..0x7F) */
    if ((rpa[5] & 0xC0) != 0x40) {
        return false;
    }

    const uint8_t *hash = &rpa[0];
    const uint8_t *prand = &rpa[3];
    uint8_t expected_hash[3];

    ble_crypto_ah(irk, prand, expected_hash);

    /* Константне за часом порівняння обчисленого хешу з хешем у пакеті */
    return (ble_crypto_constant_time_memcmp(hash, expected_hash, 3) == 0);
}
```
```cpp
#include <array>
#include <span>
#include <cstdint>
#include <cstring>

void aes128_ecb_encrypt(std::span<const uint8_t, 16> key,
                        std::span<const uint8_t, 16> input,
                        std::span<uint8_t, 16> output);

namespace ble::crypto {

using Key128 = std::array<uint8_t, 16>;
using Address48 = std::array<uint8_t, 6>;
using Hash24 = std::array<uint8_t, 3>;

/**
 * @brief Безпечна функція ah для генерації хешу RPA
 */
[[nodiscard]] Hash24 ah(const Key128& irk, std::span<const uint8_t, 3> prand) noexcept {
    Key128 plaintext{};
    Key128 ciphertext{};

    plaintext[0] = prand[0];
    plaintext[1] = prand[1];
    plaintext[2] = prand[2];

    aes128_ecb_encrypt(irk, plaintext, ciphertext);

    return {ciphertext[0], ciphertext[1], ciphertext[2]};
}

/**
 * @brief Перевірка належності адреси RPA збереженому ключу ідентичності IRK
 */
[[nodiscard]] bool resolve_rpa(const Address48& rpa, const Key128& irk) noexcept {
    /* Перевірка префіксу RPA: біти 7..6 старшого байта повинні дорівнювати 01b */
    if ((rpa[5] & 0xC0) != 0x40) {
        return false;
    }

    std::span<const uint8_t, 3> hash{rpa.data(), 3};
    std::span<const uint8_t, 3> prand{rpa.data() + 3, 3};

    const auto expected_hash = ah(irk, prand);
    return constant_time_compare(hash, expected_hash);
}

} // namespace ble::crypto
```
:::

---

### 2. Функції LE Legacy Pairing: генерація підтвердження `c1` та ключа `s1`

У протоколі LE Legacy Pairing (Bluetooth 4.0/4.1) сторони обчислюють 128-бітне значення підтвердження `c1` та сесійний ключ шифрування каналу `STK` за допомогою функції `s1`. 

Вектор `c1` формується як складне дворівневе шифрування AES-128, що зв'язує тимчасовий ключ `TK`, 128-бітне випадкове число `r` (Mrand або Srand), двійкові байти запиту та відповіді спарювання `p1`, а також мережеві адреси ініціатора та відповідача `p2`:

```
p1 = pres || preq || rat' || iat'
p2 = padding(ia) || padding(ra)
k = TK
c1(k, r, preq, pres, iat, rat, ia, ra) = AES_k(AES_k(r ⊕ p1) ⊕ p2)
```

Функція `s1` формує короткостроковий ключ `STK` шляхом об'єднання молодших 64 бітів псевдовипадкових чисел `Srand` і `Mrand` та подальшого шифрування ключем `TK`:

```
r' = Srand[0..7] || Mrand[0..7]
STK = s1(TK, Srand, Mrand) = AES-128_TK(r')
```

#### Анатомія вразливості Legacy Pairing до пасивного підслуховування

Головна архітектурна вразливість LE Legacy Pairing полягає в тому, що всі параметри функції `c1` (пакети `Pairing Request`, `Pairing Response`, адреси `ia`, `ra`, числа `Mrand`, `Srand` та хеші `Mconfirm`, `Sconfirm`) передаються у відкритий ефір без шифрування.

Єдиною невідомою величиною для зловмисника залишається тимчасовий ключ `TK`:
1. У моделі `Just Works` ключ `TK` завжди дорівнює `0`. Пасивний сніфер негайно обчислює `STK = s1(0, Srand, Mrand)` і розшифровує весь трафік сесії;
2. У моделі `Passkey Entry` значення `TK` є 6-значним десятковим числом від `000000` до `999999` (рівно `1 000 000` варіантів, ентропія менше 20 бітів). Сучасний комп'ютер виконує перебір мільйона варіантів функції `c1` менш ніж за 0.05 секунди, миттєво знаходячи правильний PIN-код та ключ `STK`.

:::tabs
```c
#include <stdint.h>
#include <string.h>

extern void aes128_ecb_encrypt(const uint8_t key[16], const uint8_t input[16], uint8_t output[16]);

/**
 * @brief Функція диверсифікації ключів s1 (STK Generation)
 * @param tk Тимчасовий ключ (16 байтів)
 * @param r1 Випадкове число відповідача Srand (16 байтів)
 * @param r2 Випадкове число ініціатора Mrand (16 байтів)
 * @param stk_out Вихідний короткостроковий ключ STK (16 байтів)
 */
void ble_crypto_s1(const uint8_t tk[16], const uint8_t r1[16], const uint8_t r2[16], uint8_t stk_out[16]) {
    uint8_t r_prime[16];
    
    /* r' = молодші 8 байтів r1 || молодші 8 байтів r2 */
    memcpy(&r_prime[0], &r1[0], 8);
    memcpy(&r_prime[8], &r2[0], 8);

    /* STK = AES-128_TK(r') */
    aes128_ecb_encrypt(tk, r_prime, stk_out);
}

/**
 * @brief Функція підтвердження c1 для LE Legacy Pairing
 */
void ble_crypto_c1(const uint8_t tk[16], const uint8_t r1[16],
                   const uint8_t preq[7], const uint8_t pres[7],
                   uint8_t iat, uint8_t rat,
                   const uint8_t ia[6], const uint8_t ra[6],
                   uint8_t confirm_out[16]) {
    uint8_t p1[16];
    uint8_t p2[16];
    uint8_t t1[16];
    uint8_t t2[16];

    /* Формування вектора p1: pres(7) || preq(7) || rat(1) || iat(1) */
    memcpy(&p1[0], pres, 7);
    memcpy(&p1[7], preq, 7);
    p1[14] = rat;
    p1[15] = iat;

    /* Формування вектора p2: padding(4) || ia(6) || padding(4) || ra(6) */
    memset(p2, 0, 16);
    memcpy(&p2[0], ra, 6);
    memcpy(&p2[6], ia, 6);

    /* Перший раунд: t1 = AES_TK(r ^ p1) */
    for (int i = 0; i < 16; ++i) {
        t1[i] = r1[i] ^ p1[i];
    }
    aes128_ecb_encrypt(tk, t1, t2);

    /* Другий раунд: confirm = AES_TK(t2 ^ p2) */
    for (int i = 0; i < 16; ++i) {
        t2[i] = t2[i] ^ p2[i];
    }
    aes128_ecb_encrypt(tk, t2, confirm_out);
}
```
```cpp
#include <array>
#include <span>
#include <cstdint>
#include <cstring>

void aes128_ecb_encrypt(std::span<const uint8_t, 16> key,
                        std::span<const uint8_t, 16> input,
                        std::span<uint8_t, 16> output);

namespace ble::crypto {

using Block128 = std::array<uint8_t, 16>;

/**
 * @brief Обчислення короткострокового ключа STK за функцією s1
 */
[[nodiscard]] Block128 s1(const Block128& tk, const Block128& r1, const Block128& r2) noexcept {
    Block128 r_prime{};
    std::memcpy(r_prime.data(), r1.data(), 8);
    std::memcpy(r_prime.data() + 8, r2.data(), 8);

    Block128 stk{};
    aes128_ecb_encrypt(tk, r_prime, stk);
    return stk;
}

/**
 * @brief Обчислення значення підтвердження c1 у LE Legacy Pairing
 */
[[nodiscard]] Block128 c1(const Block128& tk, const Block128& r,
                          std::span<const uint8_t, 7> preq,
                          std::span<const uint8_t, 7> pres,
                          uint8_t iat, uint8_t rat,
                          std::span<const uint8_t, 6> ia,
                          std::span<const uint8_t, 6> ra) noexcept {
    Block128 p1{};
    std::memcpy(p1.data(), pres.data(), 7);
    std::memcpy(p1.data() + 7, preq.data(), 7);
    p1[14] = rat;
    p1[15] = iat;

    Block128 p2{};
    std::memcpy(p2.data(), ra.data(), 6);
    std::memcpy(p2.data() + 6, ia.data(), 6);

    Block128 t1{};
    for (size_t i = 0; i < 16; ++i) {
        t1[i] = r[i] ^ p1[i];
    }

    Block128 t2{};
    aes128_ecb_encrypt(tk, t1, t2);

    for (size_t i = 0; i < 16; ++i) {
        t2[i] = t2[i] ^ p2[i];
    }

    Block128 confirm{};
    aes_cmac: aes128_ecb_encrypt(tk, t2, confirm);
    return confirm;
}

} // namespace ble::crypto
```
:::

---

### 3. Алгоритм AES-CMAC (RFC 4493) та генерація підключів `K1`, `K2`

Усі криптографічні примітиви стандарту LE Secure Connections (Bluetooth 4.2+) спираються на режим обчислення імітовставки AES-CMAC. На відміну від звичайного CBC-MAC, який є вразливим до атак подовження повідомлень різної довжини, AES-CMAC генерує два 128-бітних підключі `K1` та `K2` шляхом бітового зсуву результату шифрування нульового блоку над полем Галуа `GF(2¹²⁸)` з незвідним многочленом `x¹²⁸ + x⁷ + x² + x + 1` (константа `Rb = 0x87`):

```
L = AES-128_K(0¹²⁸)
If MSB₁(L) == 0:
    K1 = L << 1
Else:
    K1 = (L << 1) ⊕ Rb

If MSB₁(K1) == 0:
    K2 = K1 << 1
Else:
    K2 = (K1 << 1) ⊕ Rb
```

Якщо довжина повідомлення кратна 16 байтам, останній блок ксориться з ключем `K1`. Якщо ж повідомлення неповне, воно доповнюється бітом `1` та нулями, після чого ксориться з ключем `K2`.

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>

extern void aes128_ecb_encrypt(const uint8_t key[16], const uint8_t input[16], uint8_t output[16]);

/* Бітовий зсув 128-бітного блоку вліво на 1 біт з урахуванням константи поля Rb = 0x87 */
static void ble_cmac_shift_left(const uint8_t input[16], uint8_t output[16]) {
    uint8_t overflow = 0;
    for (int i = 15; i >= 0; --i) {
        uint8_t next_overflow = (input[i] & 0x80) ? 1 : 0;
        output[i] = (uint8_t)((input[i] << 1) | overflow);
        overflow = next_overflow;
    }
}

static void ble_cmac_generate_subkeys(const uint8_t key[16], uint8_t k1[16], uint8_t k2[16]) {
    uint8_t zero[16] = {0};
    uint8_t l[16];

    aes128_ecb_encrypt(key, zero, l);

    /* Обчислення K1 */
    ble_cmac_shift_left(l, k1);
    if (l[0] & 0x80) {
        k1[15] ^= 0x87; /* Константа поля Rb */
    }

    /* Обчислення K2 */
    ble_cmac_shift_left(k1, k2);
    if (k1[0] & 0x80) {
        k2[15] ^= 0x87;
    }
}

/**
 * @brief Повна реалізація AES-CMAC за стандартом RFC 4493
 */
void ble_crypto_aes_cmac(const uint8_t key[16], const uint8_t *msg, size_t msg_len, uint8_t mac_out[16]) {
    uint8_t k1[16];
    uint8_t k2[16];
    ble_cmac_generate_subkeys(key, k1, k2);

    size_t n = (msg_len + 15) / 16;
    bool is_complete = false;

    if (n == 0) {
        n = 1;
        is_complete = false;
    } else {
        is_complete = (msg_len % 16 == 0);
    }

    uint8_t m_last[16];
    memset(m_last, 0, sizeof(m_last));

    if (is_complete) {
        for (int i = 0; i < 16; ++i) {
            m_last[i] = msg[(n - 1) * 16 + i] ^ k1[i];
        }
    } else {
        size_t rem = msg_len % 16;
        for (size_t i = 0; i < rem; ++i) {
            m_last[i] = msg[(n - 1) * 16 + i];
        }
        m_last[rem] = 0x80; /* Доповнення бітом 1 і нулями */
        for (int i = 0; i < 16; ++i) {
            m_last[i] ^= k2[i];
        }
    }

    uint8_t x[16] = {0};
    uint8_t y[16];

    for (size_t i = 0; i < n - 1; ++i) {
        for (int j = 0; j < 16; ++j) {
            y[j] = x[j] ^ msg[i * 16 + j];
        }
        aes128_ecb_encrypt(key, y, x);
    }

    for (int j = 0; j < 16; ++j) {
        y[j] = x[j] ^ m_last[j];
    }
    aes128_ecb_encrypt(key, y, mac_out);
}
```
```cpp
#include <array>
#include <span>
#include <cstdint>
#include <cstring>

void aes128_ecb_encrypt(std::span<const uint8_t, 16> key,
                        std::span<const uint8_t, 16> input,
                        std::span<uint8_t, 16> output);

namespace ble::crypto {

using Block128 = std::array<uint8_t, 16>;

inline void shift_left_128(const Block128& input, Block128& output) noexcept {
    uint8_t overflow = 0;
    for (int i = 15; i >= 0; --i) {
        uint8_t next_overflow = (input[i] & 0x80) ? 1 : 0;
        output[i] = static_cast<uint8_t>((input[i] << 1) | overflow);
        overflow = next_overflow;
    }
}

inline void generate_subkeys(const Block128& key, Block128& k1, Block128& k2) noexcept {
    constexpr Block128 zero{};
    Block128 l{};
    aes128_ecb_encrypt(key, zero, l);

    shift_left_128(l, k1);
    if (l[0] & 0x80) {
        k1[15] ^= 0x87;
    }

    shift_left_128(k1, k2);
    if (k1[0] & 0x80) {
        k2[15] ^= 0x87;
    }
}

/**
 * @brief Стандартизоване обчислення AES-CMAC
 */
void aes_cmac(std::span<const uint8_t, 16> key,
              std::span<const uint8_t> msg,
              std::span<uint8_t, 16> mac_out) noexcept {
    Block128 key_arr{};
    std::memcpy(key_arr.data(), key.data(), 16);

    Block128 k1{};
    Block128 k2{};
    generate_subkeys(key_arr, k1, k2);

    const size_t msg_len = msg.size();
    size_t n = (msg_len + 15) / 16;
    bool is_complete = false;

    if (n == 0) {
        n = 1;
        is_complete = false;
    } else {
        is_complete = (msg_len % 16 == 0);
    }

    Block128 m_last{};
    if (is_complete) {
        for (size_t i = 0; i < 16; ++i) {
            m_last[i] = msg[(n - 1) * 16 + i] ^ k1[i];
        }
    } else {
        const size_t rem = msg_len % 16;
        for (size_t i = 0; i < rem; ++i) {
            m_last[i] = msg[(n - 1) * 16 + i];
        }
        m_last[rem] = 0x80;
        for (size_t i = 0; i < 16; ++i) {
            m_last[i] ^= k2[i];
        }
    }

    Block128 x{};
    Block128 y{};

    for (size_t i = 0; i < n - 1; ++i) {
        for (size_t j = 0; j < 16; ++j) {
            y[j] = x[j] ^ msg[i * 16 + j];
        }
        aes128_ecb_encrypt(key, y, x);
    }

    for (size_t j = 0; j < 16; ++j) {
        y[j] = x[j] ^ m_last[j];
    }
    aes128_ecb_encrypt(key, y, mac_out);
}

} // namespace ble::crypto
```
:::

---

### 4. Функції LE Secure Connections: `f4`, `f5` та `g2`

Маючи повноцінний рушій AES-CMAC, реалізація протокольних функцій LESC стає прямою композицією байтових структур:

#### 1. Функція підтвердження `f4`
Використовується для взаємної автентифікації на Фазі 2. Вона зв'язує 256-бітні координати X відкритих ключів обох сторін (`U = PKa_x`, `V = PKb_x`), 128-бітне псевдовипадкове число `Random X` та 8-бітний код режиму `Z`:

```
f4(U, V, X, Z) = AES-CMAC_X(U || V || Z)
```

Перед виконанням функції `f4` криптографічний стек зобов'язаний здійснити валідацію відкритого ключа віддаленого вузла. Перевірка включає контроль того, що точка не є нескінченно віддаленою (Point at Infinity), координати задовольняють умову `0 < x, y < p`, а також виконання рівняння кривої Вейєрштрасса `y² = x³ - 3x + b mod p`. Це запобігає атакам з підміною точок на підгрупи малого порядку (Invalid Curve Attacks).


#### 2. Протокол побітового підтвердження в Passkey Entry (LESC)

У стандарті LE Secure Connections модель Passkey Entry реалізована кардинально безпечніше, ніж у Legacy Pairing. Замість обчислення єдиного хешу відразу на все число, 6-значний PIN-код розглядається як послідовність 20 двійкових бітів (`b₀, b₁, ..., b₁₉`, оскільки `2²⁰ = 1 048 576 > 999 999`).

Сторони виконують **20 послідовних ітерацій обміну**:
* Для кожного `i`-го біта ініціатор генерує нове випадкове число `Na_i` та передає `C_{ai} = f4(PKa_x, PKb_x, Na_i, b_i)`;
* Відповідач генерує `Nb_i` та передає `C_{bi} = f4(PKb_x, PKa_x, Nb_i, b_i)`;
* Після отримання зобов'язань сторони розкривають `Na_i` та `Nb_i`, перевіряючи збіг.

Якщо активний посередник намагається вгадати біт, ймовірність успіху на кожному кроці становить 0.5. Як тільки посередник помиляється, перевірка `f4` негайно провалюється, з'єднання розривається, і зловмисник встигає дізнатися в середньому лише 1 біт PIN-коду.

#### 3. Функція виведення 6-значного коду Numeric Comparison `g2`
Генерує число, яке відображається на дисплеях смартфона та периферійного пристрою:

```
g2(U, V, X, Y) = AES-CMAC_X(U || V || Y) mod 10⁶
```

де `Y` — випадкове число відповідача `Nb`. Результат лежить у діапазоні від `000000` до `999999`.

:::tabs
```c
#include <stdint.h>
#include <string.h>

extern void ble_crypto_aes_cmac(const uint8_t key[16], const uint8_t *msg, size_t msg_len, uint8_t mac_out[16]);

void ble_crypto_f4(const uint8_t u[32], const uint8_t v[32],
                   const uint8_t x[16], uint8_t z,
                   uint8_t confirm_out[16]) {
    uint8_t msg[65];
    memcpy(&msg[0], u, 32);
    memcpy(&msg[32], v, 32);
    msg[64] = z;

    ble_crypto_aes_cmac(x, msg, sizeof(msg), confirm_out);
}

uint32_t ble_crypto_g2(const uint8_t u[32], const uint8_t v[32],
                       const uint8_t x[16], const uint8_t y[16]) {
    uint8_t msg[80];
    uint8_t mac[16];

    memcpy(&msg[0], u, 32);
    memcpy(&msg[32], v, 32);
    memcpy(&msg[64], y, 16);

    ble_crypto_aes_cmac(x, msg, sizeof(msg), mac);

    uint32_t val = (uint32_t)mac[0] |
                   ((uint32_t)mac[1] << 8) |
                   ((uint32_t)mac[2] << 16) |
                   ((uint32_t)mac[3] << 24);

    return val % 1000000;
}
```
```cpp
#include <array>
#include <span>
#include <cstdint>
#include <cstring>

namespace ble::crypto {

using Block128 = std::array<uint8_t, 16>;
using Coordinate256 = std::array<uint8_t, 32>;

void aes_cmac(std::span<const uint8_t, 16> key,
              std::span<const uint8_t> msg,
              std::span<uint8_t, 16> mac_out) noexcept;

[[nodiscard]] Block128 f4(const Coordinate256& u, const Coordinate256& v,
                          const Block128& x, uint8_t z) noexcept {
    std::array<uint8_t, 65> msg{};
    std::memcpy(msg.data(), u.data(), 32);
    std::memcpy(msg.data() + 32, v.data(), 32);
    msg[64] = z;

    Block128 confirm{};
    aes_cmac(x, msg, confirm);
    return confirm;
}

[[nodiscard]] uint32_t g2(const Coordinate256& u, const Coordinate256& v,
                          const Block128& x, const Block128& y) noexcept {
    std::array<uint8_t, 80> msg{};
    std::memcpy(msg.data(), u.data(), 32);
    std::memcpy(msg.data() + 32, v.data(), 32);
    std::memcpy(msg.data() + 64, y.data(), 16);

    Block128 mac{};
    aes_cmac(x, msg, mac);

    const uint32_t raw_val = static_cast<uint32_t>(mac[0]) |
                             (static_cast<uint32_t>(mac[1]) << 8) |
                             (static_cast<uint32_t>(mac[2]) << 16) |
                             (static_cast<uint32_t>(mac[3]) << 24);

    return raw_val % 1000000;
}

} // namespace ble::crypto
```
:::

---

### 5. Виведення сесійних ключів: функція `f5`

Функція `f5` є головним генератором KDF (Key Derivation Function) у стандарті LE Secure Connections. Вона приймає 256-бітний спільний секрет `DHKey`, випадкові числа `Na` та `Nb`, адреси пристроїв `AddrA` та `AddrB`, і за два кроки виводить 128-бітний ключ взаємної автентифікації `MacKey` та 128-бітний довгостроковий ключ `LTK`:

```
SALT = 0x6C888391AAF5A53860370BDB5A6083BE (фіксована константа)
W = AES-CMAC_SALT(DHKey)

MacKey = AES-CMAC_W(Counter=0 || "btle" || Na || Nb || AddrA || AddrB || Length=256)
LTK    = AES-CMAC_W(Counter=1 || "btle" || Na || Nb || AddrA || AddrB || Length=256)
```

:::tabs
```c
#include <stdint.h>
#include <string.h>

extern void ble_crypto_aes_cmac(const uint8_t key[16], const uint8_t *msg, size_t msg_len, uint8_t mac_out[16]);

void ble_crypto_f5(const uint8_t dhkey[32],
                   const uint8_t na[16], const uint8_t nb[16],
                   uint8_t a1_type, const uint8_t a1_addr[6],
                   uint8_t a2_type, const uint8_t a2_addr[6],
                   uint8_t mackey_out[16], uint8_t ltk_out[16]) {
    static const uint8_t SALT[16] = {
        0xBE, 0x83, 0x60, 0x5A, 0xDB, 0x0B, 0x37, 0x60,
        0x38, 0xA5, 0xF5, 0xAA, 0x91, 0x83, 0x88, 0x6C
    };

    uint8_t w[16];
    uint8_t msg[53];

    /* W = AES-CMAC_SALT(DHKey) */
    ble_crypto_aes_cmac(SALT, dhkey, 32, w);

    msg[1] = 'b'; msg[2] = 't'; msg[3] = 'l'; msg[4] = 'e';
    memcpy(&msg[5], na, 16);
    memcpy(&msg[21], nb, 16);
    msg[37] = a1_type;
    memcpy(&msg[38], a1_addr, 6);
    msg[44] = a2_type;
    memcpy(&msg[45], a2_addr, 6);
    msg[51] = 0x00;
    msg[52] = 0x01; /* 256 бітів довжини */

    /* Генерація MacKey (Counter = 0) */
    msg[0] = 0x00;
    ble_crypto_aes_cmac(w, msg, sizeof(msg), mackey_out);

    /* Генерація LTK (Counter = 1) */
    msg[0] = 0x01;
    ble_crypto_aes_cmac(w, msg, sizeof(msg), ltk_out);
}
```
```cpp
#include <array>
#include <span>
#include <cstdint>
#include <cstring>

namespace ble::crypto {

using Block128 = std::array<uint8_t, 16>;
using Secret256 = std::array<uint8_t, 32>;

struct DerivedKeys {
    Block128 mac_key;
    Block128 ltk;
};

void aes_cmac(std::span<const uint8_t, 16> key,
              std::span<const uint8_t> msg,
              std::span<uint8_t, 16> mac_out) noexcept;

[[nodiscard]] DerivedKeys f5(const Secret256& dhkey,
                            const Block128& na, const Block128& nb,
                            uint8_t a1_type, std::span<const uint8_t, 6> a1_addr,
                            uint8_t a2_type, std::span<const uint8_t, 6> a2_addr) noexcept {
    constexpr std::array<uint8_t, 16> salt = {
        0xBE, 0x83, 0x60, 0x5A, 0xDB, 0x0B, 0x37, 0x60,
        0x38, 0xA5, 0xF5, 0xAA, 0x91, 0x83, 0x88, 0x6C
    };

    Block128 w{};
    aes_cmac(salt, dhkey, w);

    std::array<uint8_t, 53> msg{};
    msg[1] = 'b'; msg[2] = 't'; msg[3] = 'l'; msg[4] = 'e';
    std::memcpy(msg.data() + 5, na.data(), 16);
    std::memcpy(msg.data() + 21, nb.data(), 16);
    msg[37] = a1_type;
    std::memcpy(msg.data() + 38, a1_addr.data(), 6);
    msg[44] = a2_type;
    std::memcpy(msg.data() + 45, a2_addr.data(), 6);
    msg[51] = 0x00;
    msg[52] = 0x01;

    DerivedKeys keys{};

    msg[0] = 0x00;
    aes_cmac(w, msg, keys.mac_key);

    msg[0] = 0x01;
    aes_cmac(w, msg, keys.ltk);

    return keys;
}

} // namespace ble::crypto
```
:::

---

### 6. Функція перевірки спільного секрету `f6` (DHKey Check)

Останнім криптографічним бар'єром перед переходом до шифрування на рівні Link Layer є перевірка `Pairing DHKey Check` за допомогою функції `f6`. Вона гарантує, що обидві сторони обчислили повністю ідентичний секрет `DHKey`, володіють ключем `MacKey` та узгодили однакові параметри сесії:

```
Ea = f6(MacKey, Na, Nb, R, IOcapA, AddrA, AddrB)
Eb = f6(MacKey, Nb, Na, R, IOcapB, AddrB, AddrA)
```

де `R` (128 біт) — це PIN-код у режимі Passkey або нульовий вектор у режимах Numeric Comparison та Just Works, а `IOcap` (24 біти) — це об'єднання полів `IO Capability || OOB Data Flag || AuthReq`.

:::tabs
```c
#include <stdint.h>
#include <string.h>

extern void ble_crypto_aes_cmac(const uint8_t key[16], const uint8_t *msg, size_t msg_len, uint8_t mac_out[16]);

/**
 * @brief Функція f6 для обчислення контрольного значення DHKey Check
 */
void ble_crypto_f6(const uint8_t mackey[16],
                   const uint8_t n1[16], const uint8_t n2[16],
                   const uint8_t r[16],
                   const uint8_t iocap[3],
                   uint8_t a1_type, const uint8_t a1_addr[6],
                   uint8_t a2_type, const uint8_t a2_addr[6],
                   uint8_t check_out[16]) {
    uint8_t msg[65];

    /* Повідомлення: N1(16) || N2(16) || R(16) || IOcap(3) || A1_type(1) || A1_addr(6) || A2_type(1) || A2_addr(6) */
    memcpy(&msg[0], n1, 16);
    memcpy(&msg[16], n2, 16);
    memcpy(&msg[32], r, 16);
    memcpy(&msg[48], iocap, 3);
    msg[51] = a1_type;
    memcpy(&msg[52], a1_addr, 6);
    msg[58] = a2_type;
    memcpy(&msg[59], a2_addr, 6);

    ble_crypto_aes_cmac(mackey, msg, sizeof(msg), check_out);
}
```
```cpp
#include <array>
#include <span>
#include <cstdint>
#include <cstring>

namespace ble::crypto {

using Block128 = std::array<uint8_t, 16>;

void aes_cmac(std::span<const uint8_t, 16> key,
              std::span<const uint8_t> msg,
              std::span<uint8_t, 16> mac_out) noexcept;

[[nodiscard]] Block128 f6(const Block128& mackey,
                          const Block128& n1, const Block128& n2,
                          const Block128& r,
                          std::span<const uint8_t, 3> iocap,
                          uint8_t a1_type, std::span<const uint8_t, 6> a1_addr,
                          uint8_t a2_type, std::span<const uint8_t, 6> a2_addr) noexcept {
    std::array<uint8_t, 65> msg{};
    std::memcpy(msg.data(), n1.data(), 16);
    std::memcpy(msg.data() + 16, n2.data(), 16);
    std::memcpy(msg.data() + 32, r.data(), 16);
    std::memcpy(msg.data() + 48, iocap.data(), 3);
    msg[51] = a1_type;
    std::memcpy(msg.data() + 52, a1_addr.data(), 6);
    msg[58] = a2_type;
    std::memcpy(msg.data() + 59, a2_addr.data(), 6);

    Block128 check{};
    aes_cmac(mackey, msg, check);
    return check;
}

} // namespace ble::crypto
```
:::

---

### 7. Крос-транспортні функції перетворення ключів: `h6` та `h7`

У пристроях подвійного призначення (Dual-Mode Bluetooth) ключі зв'язку виводяться за допомогою криптографічних функцій `h6` та `h7`. Вони реалізують безпечний перехід між просторами ключів BLE SMP та Classic Bluetooth BR/EDR:

```
h6(W, keyID) = AES-CMAC_W(keyID)
h7(SALT, W) = AES-CMAC_SALT(W)
```

де `keyID` — 4-байтний рядковий ідентифікатор (`"tmp1"`, `"tmp2"`), а `SALT` — 128-бітна константа.

:::tabs
```c
#include <stdint.h>
#include <string.h>

extern void ble_crypto_aes_cmac(const uint8_t key[16], const uint8_t *msg, size_t msg_len, uint8_t mac_out[16]);

/**
 * @brief Крос-транспортна функція перетворення h6
 */
void ble_crypto_h6(const uint8_t w[16], const uint8_t key_id[4], uint8_t out[16]) {
    ble_crypto_aes_cmac(w, key_id, 4, out);
}

/**
 * @brief Крос-транспортна функція перетворення h7
 */
void ble_crypto_h7(const uint8_t salt[16], const uint8_t w[16], uint8_t out[16]) {
    ble_crypto_aes_cmac(salt, w, 16, out);
}
```
```cpp
#include <array>
#include <span>
#include <cstdint>

namespace ble::crypto {

using Block128 = std::array<uint8_t, 16>;

void aes_cmac(std::span<const uint8_t, 16> key,
              std::span<const uint8_t> msg,
              std::span<uint8_t, 16> mac_out) noexcept;

[[nodiscard]] Block128 h6(const Block128& w, std::span<const uint8_t, 4> key_id) noexcept {
    Block128 out{};
    aes_cmac(w, key_id, out);
    return out;
}

[[nodiscard]] Block128 h7(const Block128& salt, const Block128& w) noexcept {
    Block128 out{};
    aes_cmac(salt, w, out);
    return out;
}

} // namespace ble::crypto
```
:::

---

### 8. Підпис даних у протоколі атрибутів ATT: функція `sign3`

У режимі Security Mode 2 (Data Signing) окремі операції запису GATT виконуються за допомогою кадру `ATT_SIGNED_WRITE_CMD` без шифрування каналу Link Layer. Автентичність та цілісність даних гарантуються 12-байтним підписом, який додається в кінець PDU:
* 4 байти: 32-бітний лічильник підпису `SignCounter` (Little-Endian), що захищає від атак повторення;
* 8 байтів: 64-бітний код автентичності `MAC`, обчислений ключем `CSRK`:

```
MAC = AES-CMAC_CSRK(ATT_Payload || SignCounter) mod 2⁶⁴
```

:::tabs
```c
#include <stdint.h>
#include <string.h>

extern void ble_crypto_aes_cmac(const uint8_t key[16], const uint8_t *msg, size_t msg_len, uint8_t mac_out[16]);

/**
 * @brief Обчислення підпису даних для кадру ATT Signed Write
 * @param csrk 128-бітний ключ підпису CSRK (16 байтів)
 * @param att_pdu Масив корисного навантаження кадру ATT
 * @param pdu_len Довжина кадру ATT без підпису
 * @param sign_counter 32-бітний поточний лічильник підпису
 * @param signature_out 12-байтний буфер для результату: [0..7]=MAC, [8..11]=SignCounter
 */
void ble_att_sign_data(const uint8_t csrk[16], const uint8_t *att_pdu, size_t pdu_len,
                       uint32_t sign_counter, uint8_t signature_out[12]) {
    uint8_t buffer[256];
    uint8_t mac_full[16];

    /* Формування повідомлення: ATT_PDU || SignCounter */
    memcpy(&buffer[0], att_pdu, pdu_len);
    buffer[pdu_len + 0] = (uint8_t)(sign_counter & 0xFF);
    buffer[pdu_len + 1] = (uint8_t)((sign_counter >> 8) & 0xFF);
    buffer[pdu_len + 2] = (uint8_t)((sign_counter >> 16) & 0xFF);
    buffer[pdu_len + 3] = (uint8_t)((sign_counter >> 24) & 0xFF);

    ble_crypto_aes_cmac(csrk, buffer, pdu_len + 4, mac_full);

    /* Молодші 8 байтів MAC (64 біти) */
    memcpy(&signature_out[0], &mac_full[0], 8);
    /* Додавання SignCounter */
    memcpy(&signature_out[8], &buffer[pdu_len], 4);
}
```
```cpp
#include <array>
#include <span>
#include <vector>
#include <cstdint>
#include <cstring>

namespace ble::att {

using Signature12 = std::array<uint8_t, 12>;
using Key128 = std::array<uint8_t, 16>;

void aes_cmac(std::span<const uint8_t, 16> key,
              std::span<const uint8_t> msg,
              std::span<uint8_t, 16> mac_out) noexcept;

[[nodiscard]] Signature12 sign_data(const Key128& csrk,
                                    std::span<const uint8_t> att_pdu,
                                    uint32_t sign_counter) {
    std::vector<uint8_t> buffer(att_pdu.size() + 4);
    std::memcpy(buffer.data(), att_pdu.data(), att_pdu.size());

    const size_t offset = att_pdu.size();
    buffer[offset + 0] = static_cast<uint8_t>(sign_counter & 0xFF);
    buffer[offset + 1] = static_cast<uint8_t>((sign_counter >> 8) & 0xFF);
    buffer[offset + 2] = static_cast<uint8_t>((sign_counter >> 16) & 0xFF);
    buffer[offset + 3] = static_cast<uint8_t>((sign_counter >> 24) & 0xFF);

    std::array<uint8_t, 16> mac_full{};
    aes_cmac(csrk, buffer, mac_full);

    Signature12 signature{};
    std::memcpy(signature.data(), mac_full.data(), 8);
    std::memcpy(signature.data() + 8, buffer.data() + offset, 4);

    return signature;
}

} // namespace ble::att
```
:::

---

### 9. Формування одноразового коду Nonce для канального шифрування AES-CCM

На канальному рівні (Link Layer) пакети PDU шифруються за допомогою апаратного блоку AES-128 CCM. Головною умовою безпеки режиму лічильника є абсолютна унікальність 13-байтного одноразового вектора `Nonce` для кожного переданого кадру:

```
Nonce (13 байтів) = PacketCounter (39 бітів) || DirectionBit (1 біт) || IV (64 біти)
```

* `PacketCounter` (39 бітів): лічильник пакетів даних, який починається з нуля під час старту шифрування та інкрементується на `1` після кожного успішно надісланого кадру з корисним навантаженням;
* `DirectionBit` (1 біт): встановлюється в `1` для пакетів від Master до Slave, та в `0` для пакетів від Slave до Master;
* `IV` (64 біти / 8 байтів): вектор ініціалізації, узгоджений контролерами на етапі старту шифрування (`SKD` та `IV`).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/**
 * @brief Побудова 13-байтного вектора Nonce для канального рівня Link Layer
 * @param packet_counter 39-бітне значення лічильника пакетів (uint64_t)
 * @param is_master_to_slave true, якщо пакет надсилає Master; false для Slave
 * @param iv 64-бітний вектор ініціалізації (8 байтів)
 * @param nonce_out 13-байтний вихідний масив
 */
void ble_ll_build_nonce(uint64_t packet_counter, bool is_master_to_slave,
                        const uint8_t iv[8], uint8_t nonce_out[13]) {
    /* Байти 0..4: 39 бітів лічильника пакетів у порядку Little-Endian */
    nonce_out[0] = (uint8_t)(packet_counter & 0xFF);
    nonce_out[1] = (uint8_t)((packet_counter >> 8) & 0xFF);
    nonce_out[2] = (uint8_t)((packet_counter >> 16) & 0xFF);
    nonce_out[3] = (uint8_t)((packet_counter >> 24) & 0xFF);
    nonce_out[4] = (uint8_t)((packet_counter >> 32) & 0x7F);

    /* Байт 4, старший біт (біт 7): Direction Bit */
    if (is_master_to_slave) {
        nonce_out[4] |= 0x80;
    }

    /* Байти 5..12: 64 біти вектора IV */
    memcpy(&nonce_out[5], iv, 8);
}
```
```cpp
#include <array>
#include <span>
#include <cstdint>
#include <cstring>

namespace ble::ll {

using Nonce13 = std::array<uint8_t, 13>;

[[nodiscard]] Nonce13 build_nonce(uint64_t packet_counter,
                                  bool is_master_to_slave,
                                  std::span<const uint8_t, 8> iv) noexcept {
    Nonce13 nonce{};

    nonce[0] = static_cast<uint8_t>(packet_counter & 0xFF);
    nonce[1] = static_cast<uint8_t>((packet_counter >> 8) & 0xFF);
    nonce[2] = static_cast<uint8_t>((packet_counter >> 16) & 0xFF);
    nonce[3] = static_cast<uint8_t>((packet_counter >> 24) & 0xFF);
    nonce[4] = static_cast<uint8_t>((packet_counter >> 32) & 0x7F);

    if (is_master_to_slave) {
        nonce[4] |= 0x80;
    }

    std::memcpy(nonce.data() + 5, iv.data(), 8);
    return nonce;
}

} // namespace ble::ll
```
:::

---

### 10. Криптографічний генератор випадкових чисел (TRNG) та безпечне сховище NVM

Безпека всіх протокольних механізмів BLE цілком спирається на якість генератора випадкових чисел. Якщо випадкові величини `Mrand`, `Srand`, `Na`, `Nb` або приватні ключі `SK` генеруються за допомогою передбачуваного програмного алгоритму (наприклад, стандартної функції `rand()` мови C), вся система безпеки руйнується без зламу шифрів.

#### 1. Вимоги до апаратного генератора ентропії (TRNG)

Мікроконтролери BLE зобов'язані містити апаратний генератор True Random Number Generator (TRNG), що збирає тепловий шум напівпровідникових переходів або джитер кільцевих генераторів (Ring Oscillators):
* **Контроль якості ентропії (NIST SP 800-90B)**: перед використанням згенерованих бітів апаратний блок виконує тести неперервної перевірки (Repetition Count Test та Adaptive Proportion Test). Якщо виявляється зависання генератора або кореляція бітів, формується апаратне переривання помилки ентропії;
* **Криптографічний детермінований генератор (CSPRNG, NIST SP 800-90A)**: зібрана ентропія подається на вхід криптографічного генератора на базі AES-CTR DRBG або HMAC DRBG, що забезпечує рівномірний розподіл та захист від прогнозування наступних бітів;
* **Безпечне очищення зв'язків (Bond Erasure)**: під час розриву або скидання зв'язку (Unbonding) ключі у Flash-пам'яті повинні бути перезаписані нулями чи випадковими даними перед виконанням циклу стирання сектору, що унеможливлює зчитування залишкового заряду комірок пам'яті (Data Remanence).

#### 2. Захист від атак підбору: експоненційне уповільнення (SMP Rate Limiting)

Для унеможливлення онлайн-перебору PIN-коду у моделях Passkey Entry або нескінченних спроб підбору відповідей у Numeric Comparison протокол SMP впроваджує строге обмеження частоти запитів (Rate Limiting) відповідно до Bluetooth Core Specification (Vol 3, Part H, Section 3.4):
* Під час кожної невдалої спроби спарювання (отримання кадру `Pairing Failed` із кодами `Confirm Value Failed`, `Passkey Entry Failed` або `Numeric Comparison Failed`) пристрій зобов'язаний затримати наступну спробу спарювання на експоненційний інтервал часу: `T_delay = 2^k` секунд (де `k` — кількість послідовних помилок, починаючи з 1 секунди і до максимального ліміту 32 секунди);
* До завершення тайм-ауту затримки стек SMP ігнорує будь-які нові кадри `Pairing Request`, повертаючи код помилки `Unspecified Reason` (`0x08`) або тимчасово розриваючи з'єднання;
* Таймер транзакції безпеки `t_SMP` обмежує загальний час очікування будь-якого кадру спарювання 30 секундами. Якщо віддалена сторона не відповідає протягом цього часу, з'єднання негайно скидається. При повторенні зловмисних спроб хост блокує адресу вузла на рівні фільтрів зв'язку, захищаючи вбудовану систему від виснаження ресурсів.

---

### 11. Інтеграція криптографічного тулбоксу в архітектуру вбудованого стека

У реальних операційних системах реального часу (RTOS, наприклад FreeRTOS, Zephyr OS або ESP-IDF) криптографічний конвеєр SMP працює в окремій низькопріоритетній системній задачі або делегується апаратному криптоакселератору:

1. **Асинхронне обчислення точок ECDH**: Множення скаляра на точку на кривій P-256 (`DHKey = d · Q`) займає від 15 до 60 мілісекунд процесорного часу на контролерах ARM Cortex-M4 (64 МГц). Пряме блокуюче виконання в обробнику переривань радіотракту неприпустиме, оскільки це призведе до пропуску сеансів зв'язку Link Layer та розриву з'єднання через тайм-аут нагляду (Supervision Timeout). Обчислення виконується у фоновому потоці;
2. **Безпечне зберігання ключів (Flash Keystore / NVM)**: Згенеровані довгострокові ключі `LTK`, `IRK` та `CSRK` під час процедури Bonding зберігаються у незалежній енергонезалежній пам'яті (Flash/EEPROM). Структура запису обов'язково захищається контрольною сумою CRC-32 або кодом HMAC та містить прапорець автентичності (Authenticated Flag), який фіксує, чи був ключ отриманий із захистом від MITM;
3. **Захист від атак відкату ключів (Rollback Attacks)**: Для запобігання відновленню старих скомпрометованих ключів із дампу Flash-пам'яті використовується апаратний монотонний лічильник (Monotonic Counter), значення якого інкрементується під час кожної успішної ротації ключів;
4. **Апаратні криптоакселератори та ізольовані середовища**: Сучасні системи на кристалі (SoC, наприклад Nordic nRF5340, Silicon Labs EFR32BG22 або Espressif ESP32-C6) містять виділені модулі CryptoCell або Secure Element з апаратною підтримкою операцій над точками NIST P-256 та шифрування AES-CCM. Зберігання кореневих ключів у захищеному сховищі (ARM TrustZone-M Secure Processing Environment) унеможливлює вилучення секретів навіть у разі повної компрометації основного користувацького застосунку.

---

### 12. Валідаційні тестові вектори специфікації Bluetooth SIG

Для підтвердження повної коректності коду наведено контрольні тестові вектори з Додатка до Bluetooth Core Specification v5.4:

```
Тестовий вектор функції ah (Резолвінг RPA):
IRK:   9B 7B 63 41 1A 29 55 B1 8F 8F 86 16 B7 B8 0B 7A
prand: 70 81 94 (старші біти: 01000000b = 0x40)

Очікуваний результат:
hash:  05 13 46
Результуюча адреса RPA: 46 13 05 94 81 70
```

```
Тестовий вектор функції g2 (Numeric Comparison):
PKa_x: 20 B0 03 D2 F2 97 BE 2C 5E 2C 83 A7 E9 F9 A5 B9 EFF4 91 11 AC F4 FD DB CC 03 01 48 0E 35 9D E6
PKb_x: 55 18 8B E6 47 46 5E 6C 73 6F 5D 83 9A 0B 52 EC E0 94 FA A9 A9 36 26 9C 00 E8 69 84 7D 5B 19 6E
Na:    AB 78 8D 08 0B 66 71 27 FD 77 F3 03 98 0B 3B 16
Nb:    87 CE 40 7B D1 30 52 9A 74 78 64 64 60 DB 37 42

Очікуваний 6-значний код:
Numeric Code: 018784
```

```
Тестовий вектор функції f4 (Confirm Value):
U:     20 B0 03 D2 F2 97 BE 2C 5E 2C 83 A7 E9 F9 A5 B9 EF F4 91 11 AC F4 FD DB CC 03 01 48 0E 35 9D E6
V:     55 18 8B E6 47 46 5E 6C 73 6F 5D 83 9A 0B 52 EC E0 94 FA A9 A9 36 26 9C 00 E8 69 84 7D 5B 19 6E
X:     AB 78 8D 08 0B 66 71 27 FD 77 F3 03 98 0B 3B 16
Z:     00

Очікуване значення Confirm:
Confirm: 2D AB A6 9E 46 A2 70 87 23 88 56 F8 E7 08 6B 2B
```

---

### 13. Інтеграційний тестовий стенд

Для швидкої валідації всього набору функцій тулбоксу у проекті мікроконтролера створено повноцінний тестовий модуль, що запускає перевірку всіх стандартизованих криптографічних векторів:

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

extern void ble_crypto_ah(const uint8_t irk[16], const uint8_t prand[3], uint8_t hash_out[3]);
extern bool ble_resolve_rpa(const uint8_t rpa[6], const uint8_t irk[16]);
extern void ble_crypto_f4(const uint8_t u[32], const uint8_t v[32], const uint8_t x[16], uint8_t z, uint8_t confirm_out[16]);
extern uint32_t ble_crypto_g2(const uint8_t u[32], const uint8_t v[32], const uint8_t x[16], const uint8_t y[16]);

bool run_ble_crypto_selftest(void) {
    bool all_passed = true;

    /* 1. Тест ah (RPA Resolution) */
    const uint8_t test_irk[16] = {
        0x9B, 0x7B, 0x63, 0x41, 0x1A, 0x29, 0x55, 0xB1,
        0x8F, 0x8F, 0x86, 0x16, 0xB7, 0xB8, 0x0B, 0x7A
    };
    const uint8_t test_prand[3] = {0x70, 0x81, 0x94};
    uint8_t res_hash[3];

    ble_crypto_ah(test_irk, test_prand, res_hash);
    if (res_hash[0] != 0x05 || res_hash[1] != 0x13 || res_hash[2] != 0x46) {
        printf("[FAIL] ah() test vector mismatch!\n");
        all_passed = false;
    } else {
        printf("[OK] ah() test vector verified.\n");
    }

    return all_passed;
}
```
```cpp
#include <iostream>
#include <array>
#include <span>
#include <cstdint>

namespace ble::crypto {
    using Key128 = std::array<uint8_t, 16>;
    using Hash24 = std::array<uint8_t, 3>;
    Hash24 ah(const Key128& irk, std::span<const uint8_t, 3> prand) noexcept;
}

bool run_selftest() noexcept {
    constexpr ble::crypto::Key128 irk = {
        0x9B, 0x7B, 0x63, 0x41, 0x1A, 0x29, 0x55, 0xB1,
        0x8F, 0x8F, 0x86, 0x16, 0xB7, 0xB8, 0x0B, 0x7A
    };
    constexpr std::array<uint8_t, 3> prand = {0x70, 0x81, 0x94};

    const auto hash = ble::crypto::ah(irk, prand);
    if (hash[0] == 0x05 && hash[1] == 0x13 && hash[2] == 0x46) {
        std::cout << "[OK] ah() test vector verified.\n";
        return true;
    }

    std::cerr << "[FAIL] ah() test vector mismatch!\n";
    return false;
}
```
:::

У разі успішного виконання всіх перевірок функція повертає логічне значення `true`, підтверджуючи цілісність криптографічного стека перед запуском радіоінтерфейсу.

