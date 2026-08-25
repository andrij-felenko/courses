# ⚙️ Реалізація евристики Фіата — Шаміра: підпис Шнорра на C та C++

Практичне застосування евристики Фіата — Шаміра вимагає точного дотримання криптографічних специфікацій при обчисленні хеш-виклику та модифікації стану транскрипту. Заміна інтерактивного діалогу на детерміноване обчислення хешу створює специфічні ризики реалізації. Якщо імплантація зобов'язання `α` або вхідного повідомлення `m` виявиться неповною чи буде містити помилки вирівнювання типів, система стане вразливою до фальсифікації підписів та доказів.

У цій практичній вставці розглянуто повну реалізацію схеми цифрового підпису Шнорра, яка застосовує евристику Фіата — Шаміра для перетворення інтерактивного доведення знання дискретного логарифма на неінтерактивний цифровий підпис над простою циклічною групою. Наведено два альтернативні варіанти коду: низькорівнева реалізація мовою C та ідіоматичний об'єктно-орієнтований модуль мовою C++20.

## 1. Архітектурні вимоги та безпека реалізації

При перенесенні евристики Фіата — Шаміра у практичний код необхідно дотримуватися кількох критичних криптографічних правил:

1. **Генерація криптографічно стійких випадкових одноразових чисел (CSPRNG Nonce):** 
   Для кожного нового підпису випадкова величина `r` повинна обиратися з криптографічно стійкого генератора випадкових чисел (`/dev/urandom`, `getrandom()` у Linux або `BCryptGenRandom()` у Windows). Використання стандартного `rand()` із C-бібліотеки або повторне використання одного й того самого `r` для двох різних повідомлень призводить до катастрофічного витоку приватного ключа.

2. **Захист від атак через побічні канали (Constant-Time Execution):** 
   Піднесення до степеня за модулем `mod_pow` та операції множення в полі повинні виконуватися за постійний час, незалежно від значень бітів секретного ключа `x` або випадкового `r`. Використання звичайних розгалужень `if (exp & 1)` у продакшн-коді створює часовий побічний канал (timing side-channel), який дозволяє атакуючому вилучити приватний ключ шляхом вимірювання мікросекундних затримок виконання процесора.

3. **Суворе уникнення слабкого перетворення (Strong Context Binding):** 
   Функція обчислення виклику `crypto_hash_challenge()` повинна поглинати не лише зобов'язання `α`, але й публічний ключ `pk`, ідентифікатор протоколу та повний текст повідомлення `m`.

## 2. Реалізація алгоритму Фіата — Шаміра / Шнорра

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

/* Прості параметри для демонстрації арифметики у групі Z_p */
#define GROUP_P 23  /* Простий модуль групи */
#define GROUP_Q 11  /* Порядок підгрупи (q = (p - 1) / 2) */
#define GROUP_G 4   /* Генератор підгрупи порядку q */

typedef struct {
    uint8_t alpha; /* Комітмент α = g^r mod p */
    uint8_t gamma; /* Відповідь γ = (r + β * x) mod q */
} schnorr_signature_t;

/* Проста хеш-функція H(m || alpha) mod q для навчальної реалізації */
static uint8_t crypto_hash_challenge(const uint8_t *msg, size_t len, uint8_t alpha) {
    uint32_t hash_val = 5381;
    for (size_t i = 0; i < len; ++i) {
        hash_val = ((hash_val << 5) + hash_val) ^ msg[i];
    }
    hash_val = ((hash_val << 5) + hash_val) ^ alpha;
    return (uint8_t)(hash_val % GROUP_Q);
}

/* Швидке піднесення до степеня за модулем */
static uint8_t mod_pow(uint32_t base, uint32_t exp, uint32_t mod) {
    uint32_t result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1) {
            result = (result * base) % mod;
        }
        base = (base * base) % mod;
        exp /= 2;
    }
    return (uint8_t)result;
}

/* Генерація ключової пари: sk = x ∈ Z_q, pk = y = g^x mod p */
bool schnorr_key_gen(uint8_t *sk, uint8_t *pk) {
    if (!sk || !pk) return false;
    *sk = 7; /* Приклад секретного ключа (x < q) */
    *pk = mod_pow(GROUP_G, *sk, GROUP_P);
    return true;
}

/* Створення підпису Фіата — Шаміра: σ = (α, γ) */
bool schnorr_sign(const uint8_t *msg, size_t msg_len, uint8_t sk, schnorr_signature_t *sig) {
    if (!msg || !sig) return false;

    /* 1. Випадковий одноразовий елемент r ∈ Z_q */
    uint8_t r = 5; /* Випадкова величина r (у продакшн — CSPRNG) */

    /* 2. Обчислення зобов'язання (Commitment) α = g^r mod p */
    sig->alpha = mod_pow(GROUP_G, r, GROUP_P);

    /* 3. Евристика Фіата — Шаміра: β = H(m || α) mod q */
    uint8_t beta = crypto_hash_challenge(msg, msg_len, sig->alpha);

    /* 4. Обчислення відповіді (Response) γ = (r + β * sk) mod q */
    sig->gamma = (r + beta * sk) % GROUP_Q;

    return true;
}

/* Перевірка підпису Фіата — Шаміра: g^γ =?= α * y^β mod p */
bool schnorr_verify(const uint8_t *msg, size_t msg_len, uint8_t pk, const schnorr_signature_t *sig) {
    if (!msg || !sig) return false;

    /* 1. Реконструкція виклику: β' = H(m || α) mod q */
    uint8_t beta_prime = crypto_hash_challenge(msg, msg_len, sig->alpha);

    /* 2. Обчислення LHS = g^γ mod p */
    uint8_t lhs = mod_pow(GROUP_G, sig->gamma, GROUP_P);

    /* 3. Обчислення RHS = (α * y^β') mod p */
    uint8_t y_to_beta = mod_pow(pk, beta_prime, GROUP_P);
    uint8_t rhs = (sig->alpha * y_to_beta) % GROUP_P;

    return (lhs == rhs);
}

int main(void) {
    uint8_t sk = 0, pk = 0;
    schnorr_key_gen(&sk, &pk);

    const uint8_t message[] = "Fiat-Shamir Transformation";
    size_t msg_len = sizeof(message) - 1;

    schnorr_signature_t sig;
    if (!schnorr_sign(message, msg_len, sk, &sig)) {
        fprintf(stderr, "Помилка створення підпису\n");
        return EXIT_FAILURE;
    }

    printf("Сформовано підпис Фіата — Шаміра:\n");
    printf("  Комітмент α = %u\n", sig.alpha);
    printf("  Відповідь  γ = %u\n", sig.gamma);

    bool is_valid = schnorr_verify(message, msg_len, pk, &sig);
    printf("Результат перевірки підпису: %s\n", is_valid ? "УСПІХ (Дійсний)" : "ПОМИЛКА (Недійсний)");

    return is_valid ? EXIT_SUCCESS : EXIT_FAILURE;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <span>
#include <numeric>
#include <expected>
#include <cstdint>

namespace crypto::fiat_shamir {

constexpr uint32_t GroupP = 23;
constexpr uint32_t GroupQ = 11;
constexpr uint32_t GroupG = 4;

struct Signature {
    uint8_t alpha{0}; // Commitment α = g^r mod p
    uint8_t gamma{0}; // Response γ = (r + β * x) mod q
};

struct KeyPair {
    uint8_t secret_key{0};
    uint8_t public_key{0};
};

enum class CryptoError {
    InvalidParameter,
    SigningFailed,
    VerificationFailed
};

class SchnorrScheme {
public:
    static uint8_t mod_pow(uint32_t base, uint32_t exp, uint32_t mod) noexcept {
        uint32_t result = 1;
        base %= mod;
        while (exp > 0) {
            if (exp & 1) {
                result = (result * base) % mod;
            }
            base = (base * base) % mod;
            exp >>= 1;
        }
        return static_cast<uint8_t>(result);
    }

    static uint8_t hash_challenge(std::span<const uint8_t> message, uint8_t alpha) noexcept {
        uint32_t hash_val = 5381;
        for (uint8_t byte : message) {
            hash_val = ((hash_val << 5) + hash_val) ^ byte;
        }
        hash_val = ((hash_val << 5) + hash_val) ^ alpha;
        return static_cast<uint8_t>(hash_val % GroupQ);
    }

    static KeyPair generate_keypair() noexcept {
        uint8_t sk = 7; // Навчальний секретний ключ
        uint8_t pk = mod_pow(GroupG, sk, GroupP);
        return KeyPair{.secret_key = sk, .public_key = pk};
    }

    static std::expected<Signature, CryptoError> sign(
        std::span<const uint8_t> message,
        uint8_t secret_key
    ) noexcept {
        if (message.empty() || secret_key >= GroupQ) {
            return std::unexpected(CryptoError::InvalidParameter);
        }

        uint8_t r = 5; // Навчальна випадкова величина
        uint8_t alpha = mod_pow(GroupG, r, GroupP);
        uint8_t beta = hash_challenge(message, alpha);
        uint8_t gamma = static_cast<uint8_t>((r + beta * secret_key) % GroupQ);

        return Signature{.alpha = alpha, .gamma = gamma};
    }

    static bool verify(
        std::span<const uint8_t> message,
        uint8_t public_key,
        const Signature& sig
    ) noexcept {
        if (message.empty()) return false;

        uint8_t beta_prime = hash_challenge(message, sig.alpha);
        uint8_t lhs = mod_pow(GroupG, sig.gamma, GroupP);
        uint8_t rhs = static_cast<uint8_t>((sig.alpha * mod_pow(public_key, beta_prime, GroupP)) % GroupP);

        return (lhs == rhs);
    }
};

} // namespace crypto::fiat_shamir

int main() {
    using namespace crypto::fiat_shamir;

    auto keys = SchnorrScheme::generate_keypair();
    std::string_view msg_text = "Fiat-Shamir Transformation";
    auto msg_bytes = std::span<const uint8_t>(
        reinterpret_cast<const uint8_t*>(msg_text.data()),
        msg_text.size()
    );

    auto sig_result = SchnorrScheme::sign(msg_bytes, keys.secret_key);
    if (!sig_result) {
        std::cerr << "Помилка підписання повідомлення\n";
        return 1;
    }

    const auto& sig = *sig_result;
    std::cout << "Сформовано підпис Фіата — Шаміра (C++20):\n"
              << "  α = " << static_cast<int>(sig.alpha) << "\n"
              << "  γ = " << static_cast<int>(sig.gamma) << "\n";

    bool valid = SchnorrScheme::verify(msg_bytes, keys.public_key, sig);
    std::cout << "Статус верифікації: " << (valid ? "УСПІХ" : "ПОМИЛКА") << "\n";

    return valid ? 0 : 1;
}
```
:::

## 3. Детальний розбір алгоритмічних кроків

Процес формування та перевірки підпису складається з чотирьох чітко розмежованих стадій:

1. **Стадія підготовки випадкового стану (Initialization & Nonce Generation):**
   Алгоритм підписання обирає свіжу випадкову величину `r` у межах поля `Z_q`. Головна вимога — абсолютна унікальність `r` для кожного виклику `schnorr_sign`. Якщо доводжувач повторно використає те саме `r` для підписання двох різних повідомлень `m1` та `m2`, це створить два підписи `(α, γ1)` та `(α, γ2)`. Оскільки `α` однакова, виклики виявляться різними: `β1 = H(m1 || α)` та `β2 = H(m2 || α)`. Будь-який спостерігач зможе миттєво відняти два рівняння `γ1 - γ2 = (β1 - β2) · x` і обчислити приватний ключ `x = (γ1 - γ2) / (β1 - β2) mod q`. Саме ця помилка реалізації у 2010 році призвела до знаменитого злому закритих ключів консолі Sony PlayStation 3.

2. **Стадія обчислення зобов'язання (Commitment Phase):**
   Доводжувач підносить генератор групи `g` до степеня `r` за модулем `p`: `α = g^r mod p`. Значення `α` виступає одноразовим публічним ключем для поточного підпису і надсилається або додається до структури підпису `schnorr_signature_t`.

3. **Стадія згортання виклику через Фіат — Шамір (Challenge Squeeze):**
   Хеш-функція `crypto_hash_challenge()` приймає потік байтів повідомлення `msg` та значення `α`. Завдяки детермінованості хешу верифікатор зможе незалежно відтворити те саме значення `β = H(m || α)`.

4. **Стадія відповіді та верифікації (Response & Verification Phase):**
   Доводжувач обчислює відповідь `γ = (r + β · x) mod q`. Верифікатор перевіряє тотожність `g^γ = α · y^β mod p`. Оскільки верифікація вимагає лише одного піднесення до степеня для `g^γ` та одного для `y^β` (які можна обчислити паралельно або за допомогою алгоритму Штрауса-Штайнберга для подвійного піднесення до степеня), перевірка підпису Шнорра є набагато швидшою за перевірку підпису RSA.

## 4. Граничні випадки та валідація параметрів

При розробці криптографічно стійких модулів підпису необхідно опрацьовувати серію граничних випадків:

- **Нульовий або вироджений скаляр (`r = 0` або `x = 0`):** Якщо секретне `r = 0` або ключ `x = 0`, зобов'язання `α = g^0 = 1`. Алгоритм підписання зобов'язаний відхиляти такі значення, оскільки вони призводять до виходу з генеративної підгрупи `Z_q`.
- **Перевірка належності підгрупі (Subgroup Membership Check):** Верифікатор перед обчисленням `g^γ = α · y^β` повинен переконатися, що отриманий публічний ключ `y` та зобов'язання `α` належать підгрупі порядку `q` (тобто `y^q ≡ 1 mod p` та `α^q ≡ 1 mod p`). Якщо публічна точка лежить у підгрупі малого порядку, атакуючий може застосувати атаку Поліга — Хеллмана для вилучення часткової інформації про приватний ключ.
- **Формати серіалізації підпису:** Складові підпису `(α, γ)` серіалізуються у компактний 64-байтовий потік байтів (у біткойн-стандарті BIP-340 підпис за допомогою Фіата — Шаміра стискається до 64 байтів, де перші 32 байти це x-координата точкового комітменту, а останні 32 байти — скаляр відповіді).

## 5. Простеження викликів та захист оперативної пам'яті

У високонавантажених криптографічних сервісах системне простеження виконання системних викликів генерації випадкових чисел здійснюється через інтерфейс `tracepoints` ядра Linux (`sys_enter_getrandom` та `sys_exit_getrandom`). 

Для захисту секретних значень `x` та `r` в оперативній пам'яті застосовуються системні виклики POSIX:
- `mlock(sk_buffer, size)` — забороняє вивантаження сторінки пам'яті із секретним ключем у дисковий файл підкачки (swap area).
- `explicit_bzero(r_buffer, size)` або `C23 memset_s()` — гарантує стирання одноразового числа `r` з регістрів та стеку одразу після обчислення `γ`, запобігаючи витоку через дампи пам'яті при збоях процесу (coredump).

## 6. Порівняльний аналіз реалізацій C та C++20

| Критерій порівняння | Реалізація мовою C | Реалізація мовою C++20 |
| :--- | :--- | :--- |
| **Управління пам'яттю** | Сирі вказівники `const uint8_t *msg`, вимагає ручної перевірки `NULL`. | Використання `std::span<const uint8_t>`, відсутність вказівникової арифметики. |
| **Обробка помилок** | Повернення `bool` та передача результату через вихідний вказівник. | Використання типізованого `std::expected<Signature, CryptoError>`. |
| **Інкапсуляція типів** | Структура `schnorr_signature_t` із відкритими полями. | Модуль у власному просторі імен `crypto::fiat_shamir`. |
| **Оптимізація та семантика** | Ручне вирівнювання структур та статичні функції. | `constexpr` параметри та inline-розгортання методів. |

> 🔧 **Навіщо це.** Слабкий Фіат — Шамір виникає тоді, коли програміст опускає вхідні дані `message` чи параметри `context` із функції хешування `crypto_hash_challenge()`. Якщо хешувати лише зобов'язання `alpha`, криптографічна прив'язка до тексту повідомлення зникає, що дозволяє атакуючому переносити один і той самий підпис на будь-які інші документи.
