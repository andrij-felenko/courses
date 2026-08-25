# Специфікація параметрів та API постквантових стандартів ML-KEM та ML-DSA

Довідник системних параметрів, типів даних, математичних макросів та інтерфейсів виклику для постквантових решіткових стандартів NIST (FIPS 203 та FIPS 204).

## 1. Специфікація параметрів ML-KEM (FIPS 203 / CRYSTALS-Kyber)

ML-KEM побудований на алгебраїчній модульній решітці над кільцем кругових поліномів `R_q = Z_q[X] / (X²⁵⁶ + 1)`. Усі алгебраїчні обчислення виконуються з коефіцієнтами над скінченним полем `Z_q`.

### Основні математичні константи
- **Розмірність поліномів `n`**: `256` (кількість коефіцієнтів у кожному поліномі).
- **Модуль `q`**: `3329` (просте число, для якого виконується умова `q ≡ 1 (mod 2n)`, що дозволяє розкласти багаточлен `X²⁵⁶ + 1` на 128 лінійних множників над `Z_q`).
- **Первісний корінь `γ`**: `17` (первісний 256-й корінь з одиниці в `Z_q`, де `17²⁵⁶ ≡ 1 mod 3329`).
- **Розмір блоку NTT**: `128` пар коефіцієнтів першого степеня.

### Конфігурації за рівнями безпеки (NIST Security Categories)

Параметризація ML-KEM вибирається таким чином, щоб задовольнити вимоги трьох стандартних категорій безпеки NIST:

1. **ML-KEM-512**: Використовує малий векторний модуль `k = 2`. Ця конфігурація забезпечує рівень безпеки Категорії 1 (еквівалент стійкості ключа AES-128 проти класичного та квантового перебору). Розмір публічного ключа становить рівно 800 байт, секретного ключа — 1632 байти, а результуючого шифротексту — 768 байт.
2. **ML-KEM-768**: Використовує векторний модуль `k = 3`. Це основна рекомендована конфігурація загального призначення (Категорія 3 NIST, еквівалент AES-192). Вона забезпечує оптимальний баланс швидкодії та надійності. Розмір публічного ключа становить 1184 байти, секретного ключа — 2400 байт, а шифротексту — 1088 байт.
3. **ML-KEM-1024**: Використовує розширений векторний модуль `k = 4` для захисту військового та державного рівня (Категорія 5 NIST, еквівалент AES-256). Розмір публічного ключа становить 1568 байт, секретного ключа — 3168 байт, а шифротексту — 1568 байт.

У всіх трьох конфігураціях довжина згенерованого спільного сесійного секрету `ss` залишається незмінною і дорівнює 32 байтам (256 біт).

### Функції стиснення та розпакування даних

Діапазон коефіцієнтів `Z_q` становить `[0, 3328]`. Щоб зменшити підсумковий розмір шифротексту, коефіцієнти векторів поліномів піддаються стисненню за допомогою втратного округлення за формулою:

```
Compress_q(x, d) = ⌈ (2^d / q) · x ⌋  mod 2^d
Decompress_q(y, d) = ⌈ (q / 2^d) · y ⌋
```

Де `d` — кількість збережених біт. При розпакуванні `Decompress_q` відновлене значення `x'` відрізняється від вихідного `x` не більше ніж на `⌈q / 2^(d+1)⌉`, що сприймається алгоритмом як додатковий малий шум і легко усувається на етапі округлення при розшифруванні.

## 2. API інтерфейсу ML-KEM (FIPS 203)

Нижче наведено специфікацію системного API. У вкладці C показано сирі виклики з урахуванням покажчиків і розмірів буферів, а у вкладці C++ — сучасне C++20 обгортання з використанням `std::span` та `std::array`.

:::tabs
```c
#ifndef ML_KEM_H
#define ML_KEM_H

#include <stddef.h>
#include <stdint.h>

#define MLKEM768_PUBLICKEYBYTES  1184
#define MLKEM768_SECRETKEYBYTES  2400
#define MLKEM768_CIPHERTEXTBYTES 1088
#define MLKEM768_BYTES           32

typedef enum {
    MLKEM_SUCCESS = 0,
    MLKEM_ERROR_RNG_FAILED = -1,
    MLKEM_ERROR_INVALID_CIPHERTEXT = -2,
    MLKEM_ERROR_BUFFER_TOO_SMALL = -3,
    MLKEM_ERROR_CORRUPTED_KEY = -4
} mlkem_status_t;

mlkem_status_t crypto_kem_keypair(
    uint8_t pk[MLKEM768_PUBLICKEYBYTES],
    uint8_t sk[MLKEM768_SECRETKEYBYTES]
);

mlkem_status_t crypto_kem_enc(
    uint8_t ct[MLKEM768_CIPHERTEXTBYTES],
    uint8_t ss[MLKEM768_BYTES],
    const uint8_t pk[MLKEM768_PUBLICKEYBYTES]
);

mlkem_status_t crypto_kem_dec(
    uint8_t ss[MLKEM768_BYTES],
    const uint8_t ct[MLKEM768_CIPHERTEXTBYTES],
    const uint8_t sk[MLKEM768_SECRETKEYBYTES]
);

#endif // ML_KEM_H
```
```cpp
#ifndef ML_KEM_HPP
#define ML_KEM_HPP

#include <array>
#include <span>
#include <system_error>
#include <cstdint>

namespace mlkem768 {

constexpr std::size_t PublicKeyBytes  = 1184;
constexpr std::size_t SecretKeyBytes  = 2400;
constexpr std::size_t CiphertextBytes = 1088;
constexpr std::size_t SharedSecretBytes = 32;

using PublicKey    = std::array<std::uint8_t, PublicKeyBytes>;
using SecretKey    = std::array<std::uint8_t, SecretKeyBytes>;
using Ciphertext   = std::array<std::uint8_t, CiphertextBytes>;
using SharedSecret = std::array<std::uint8_t, SharedSecretBytes>;

struct KeyPair {
    PublicKey  pk;
    SecretKey  sk;
};

struct EncapsulationResult {
    Ciphertext   ct;
    SharedSecret ss;
};

class KEM {
public:
    static KeyPair generate_keypair();
    static EncapsulationResult encapsulate(std::span<const std::uint8_t, PublicKeyBytes> pk);
    static SharedSecret decapsulate(std::span<const std::uint8_t, CiphertextBytes> ct,
                                    std::span<const std::uint8_t, SecretKeyBytes> sk);
};

} // namespace mlkem768

#endif // ML_KEM_HPP
```
:::

### Детальний розбір механізму роботи точок входу API

Процедура `crypto_kem_keypair` приймає два вказівники на вихідні байтові масиви. Усередині функції виконується звернення до системного джерела випадковості для отримання двох 32-байтних векторів `d` та `z`. Вектор `d` подається на хеш-функцію SHA-3/SHAKE-128 для розгортання матриці `A` та вектора шумів. Результатом є упаковка коефіцієнтів поліномів у стиснений байтовий масив публічного ключа `pk`. Секретний ключ `sk` містить не лише коефіцієнти векторів `s`, а й повну копію публічного ключа `pk`, хеш від публічного ключа `H(pk)`, а також маскувальний вектор `z`, необхідний для неявного відхилення зіпсованих шифротекстів.

Функція `crypto_kem_enc` генерує 32-байтний випадковий вектор повідомлення `m`, обчислює його хеш разом із `H(pk)` для отримання випадкового зерна кодування та вектора шумів, будує шифротекстові поліноми `c₁` та `c₂`, після чого виконує їхнє стиснення за допомогою макросів `Compress_q`. Результат інкапсуляції складається з масиву шифротексту `ct` та 32-байтного спільного сесійного секрету `ss`.

Процедура `crypto_kem_dec` виконує розшифрування шифротексту за допомогою секретного вектора `s`. Після цього вона застосовує знамениту **трансформацію Фуджісакі–Окамото (Fujisaki-Okamoto transform)**: алгоритм повторно шифрує відновлене повідомлення `m'` за допомогою публічного ключа `pk` і порівнює отриманий шифротекст `ct'` із наданим шифротекстом `ct`. Якщо масиви збігаються, повертається справжній сесійний секрет `ss`. Якщо ж виявлено бодай один відмінний біт (що свідчить про спробу підробки або атаки адаптивно обраного шифротексту IND-CCA2), функція не видає код помилки, а детерміновано обчислює псевдовипадковий вектор від `z` та `ct`. Цей механізм «неявного відхилення» позбавляє зловмисника інформаційного оракула.

## 3. Специфікація параметрів ML-DSA (FIPS 204 / CRYSTALS-Dilithium)

ML-DSA використовує схему підпису на основі підходу Фіата-Шаміра з абортами над модульними решітками.

### Основні математичні константи ML-DSA
- **Модуль `q`**: `8380417` (`2²³ - 2¹³ + 1`, просте число, придатне для швидкого NTT).
- **Розмірність поліномів `n`**: `256`.
- **Краплі зсуву `d`**: `13` біт (для розбиття коефіцієнтів на старші та молодші біти).

### Конфігурації варіантів цифрового підпису ML-DSA

1. **ML-DSA-44**: Використовує матрицю розмірності `4 × 4` над кільцем `R_q`. Відповідає Категорії 2 безпеки NIST. Розмір публічного ключа становить 1312 байт, секретного ключа — 2560 байт, а цифрового підпису — 2420 байт.
2. **ML-DSA-65**: Використовує матрицю `6 × 5` (Категорія 3 NIST, аналог AES-192). Є основним рекомендованим стандартом для підпису документів, TLS-сертифікатів та програмного забезпечення. Публічний ключ має розмір 1952 байти, секретний ключ — 4032 байти, підпис — 3309 байт.
3. **ML-DSA-87**: Використовує розширену матрицю `8 × 7` (Категорія 5 NIST, аналог AES-256). Публічний ключ становить 2592 байти, секретний ключ — 4896 байт, а підпис — 4627 байт.

## 4. API інтерфейсу ML-DSA (FIPS 204)

:::tabs
```c
#ifndef ML_DSA_H
#define ML_DSA_H

#include <stddef.h>
#include <stdint.h>

#define MLDSA65_PUBLICKEYBYTES 1952
#define MLDSA65_SECRETKEYBYTES 4032
#define MLDSA65_SIGBYTES       3309

typedef enum {
    MLDSA_SUCCESS = 0,
    MLDSA_ERROR_INVALID_SIGNATURE = -1,
    MLDSA_ERROR_VERIFICATION_FAILED = -2,
    MLDSA_ERROR_RNG = -3
} mldsa_status_t;

mldsa_status_t crypto_sign_keypair(
    uint8_t pk[MLDSA65_PUBLICKEYBYTES],
    uint8_t sk[MLDSA65_SECRETKEYBYTES]
);

mldsa_status_t crypto_sign_signature(
    uint8_t sig[MLDSA65_SIGBYTES],
    size_t *siglen,
    const uint8_t *msg,
    size_t msglen,
    const uint8_t sk[MLDSA65_SECRETKEYBYTES]
);

mldsa_status_t crypto_sign_verify(
    const uint8_t sig[MLDSA65_SIGBYTES],
    size_t siglen,
    const uint8_t *msg,
    size_t msglen,
    const uint8_t pk[MLDSA65_PUBLICKEYBYTES]
);

#endif // ML_DSA_H
```
```cpp
#ifndef ML_DSA_HPP
#define ML_DSA_HPP

#include <array>
#include <span>
#include <system_error>
#include <cstdint>

namespace mldsa65 {

constexpr std::size_t PublicKeyBytes = 1952;
constexpr std::size_t SecretKeyBytes = 4032;
constexpr std::size_t SignatureBytes = 3309;

using PublicKey = std::array<std::uint8_t, PublicKeyBytes>;
using SecretKey = std::array<std::uint8_t, SecretKeyBytes>;
using Signature = std::array<std::uint8_t, SignatureBytes>;

struct KeyPair {
    PublicKey pk;
    SecretKey sk;
};

class DigitalSignature {
public:
    static KeyPair generate_keypair();
    static Signature sign(std::span<const std::uint8_t> message,
                          std::span<const std::uint8_t, SecretKeyBytes> sk);
    static bool verify(std::span<const std::uint8_t> message,
                       std::span<const std::uint8_t, SignatureBytes> signature,
                       std::span<const std::uint8_t, PublicKeyBytes> pk);
};

} // namespace mldsa65

#endif // ML_DSA_HPP
```
:::

### Процедура створення та перевірки підпису у коді

Функція `crypto_sign_signature` виконує розгортання матриці `A` з зерна секретного ключа, генерує випадковий маскувальний вектор `y` та обчислює його векторне множення `w = A · y`. Після цього вектор `w` розбивається на старші та молодші біти за допомогою макросу `HighBits`. Хеш від повідомлення та старших біт `w` утворює виклик `c`. Кандидат підпису обчислюється як `z = y + c · s`.

Критичноважливим етапом є процедура **відхилення (rejection sampling)**: функція перевіряє, чи не перевищують коефіцієнти векторів `z` та `r₀` встановлені межі `γ₁ - β`. Якщо межу порушено (що могло б дати статистичний витік інформації про секретний ключ `s`), кандидат підпису скасовується, лічильник спроб збільшується, і процедура повторюється з новим випадковим вектором `y`.

Функція `crypto_sign_verify` розпаковує публічний ключ `pk` та підпис `sig`, відбудовує вектори, обчислює значення `w' = A · z - c · t` і перевіряє, чи збігається хеш від старших біт `w'` із записаним у підписі значенням `c`.

## 5. Типові помилки інтеграції та застереження безпеки

1. **Незмінність часу виконання (Constant-Time Execution)**: Реалізація порівняння шифротекстів у `crypto_kem_dec` та обчислення поліномів обов'язково повинна бути виконана у коді зі сталими циклами виконання, незалежно від значень коефіцієнтів. Використання звичайного `memcmp` відкриває уразливість до витоку секретного ключа через хронометричні атаки (timing attacks).
2. **Безпека переповнення буфера**: Оскільки ключі решіткових стандартів мають розміри від 1 до 4 кілобайт (на відміну від 32 байт у Ed25519), виділення буферів на стеку у функціях із обмеженим стеком (наприклад, у ядрах ОС чи мікроконтролерах) може призвести до пробою стека (stack overflow). Використовуйте динамічне виділення або статичні захищені арени.
3. **Гібридні схеми (Hybrid Key Exchange)**: Під час транзитного переходу на постквантову криптографію регулятори (BSI, ANSSI, NIST) рекомендують використовувати комбіновані ключі (наприклад, `X25519 + ML-KEM-768`). У такому разі сесійний ключ обчислюється як `KDF(ss_x25519 || ss_mlkem)`. Це гарантує, що зламати систему неможливо, доки хоча б один із двох алгоритмів залишається стійким.
