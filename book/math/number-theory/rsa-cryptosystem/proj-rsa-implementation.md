# ⚙️ Практична реалізація RSA: генерація, CRT-прискорення та доповнення OAEP

Практична реалізація криптосистеми RSA у промислових криптографічних бібліотеках вимагає суворого дотримання вимог безпеки на кожному рівні: від обчислення модульного піднесення до степеня зі сталим часом виконання (Constant-Time Exponentiation) для запобігання часовим побічним каналам до прискорення розшифрування за допомогою Китайської теореми про лишки (CRT), оптимізації Монтгомері та захисту від оракулів доповнення через схемотехніку OAEP (Optimal Asymmetric Encryption Padding).

У цьому матеріалі наведено повноцінний алгоритмічний огляд, математичне простеження довгих чисел та готові ідіоматичні реалізації базових механізмів RSA мовами C та C++.

---

## Представлення великих чисел та редукція Монтгомері

Криптографічні розрахунки RSA вимагають виконання арифметичних операцій над числами розрядністю 2048, 3072 або 4096 біт. Оскільки апаратні регістри сучасних процесорів обмежені 64 бітами, такі числа описуються у пам'яті як масиви машинного слова (так звані *лімби* чи *limbs*):

```
A = ∑_{i=0}^{n-1} a[i] · Bⁱ,   де B = 2⁶⁴
```

Найбільш затратною операцією у піднесенні до степеня є ділення за модулем `N` для знаходження остачі після кожного множення. Класичне ділення «у стовпчик» (алгоритм Дональда Кнута) вимагає значної кількості ділень машинного слова.

Для усунення повільного ділення у промислових реалізаціях використовується **множення Монтгомері** (Montgomery Multiplication). Воно переводить числа у спеціальне просторове представлення `A' = A · R mod N` (де `R = 2ᵏ > N` — степінь двійки). У цьому просторі добуток `A' · B' mod N` обчислюється за допомогою лише додавань, множень та зсувів бітів без жодної операції ділення на `N`!

---

## Імовірнісний тест простоти Міллера — Рабіна

Генерація простих чисел `p` та `q` вимагає створення випадкових кандидатур та їх перевірки на простоту. Для чисел розміром 1024 біти детермінована перевірка діленням є неможливою. Використовується імовірнісний алгоритм Міллера — Рабіна.

Для кандидатського числа `n` подаємо `n − 1 = 2ˢ · d`, де `d` — непарне число. Алгоритм обирає випадкову основу `a ∈ [2, n − 2]` і перевіряє умови:
1. `aᵈ ≡ 1 (mod n)`
2. Існує таке `r ∈ [0, s − 1]`, що `a^(2ʳ · d) ≡ n − 1 (mod n)`.

Якщо жодна з умов не виконується, число `n` є складеним. Якщо перевірку пройдено для `k` незалежно обраних основ `a`, імовірність того, що число `n` є складеним, не перевищує `(1/4)ᵏ`. Для `k = 64` імовірність помилки стає меншою за $2^{-128}$, що перевищує надійність апаратних компонентів процесора.

---

## Алгоритмічний каскад та складність обчислень

Обчислювальний процес розшифрування RSA безпосередньо за формулою `m = cᵈ mod N` вимагає роботи з числами бітової довжини 2048, 3072 або 4096 біт. Ззвичайне піднесення до степеня через послідовні множення мав би складність `O(d)` операцій, що є обчислювально нездійсненним для 2048-бітних чисел.

Використання бінарного алгоритму «піднесення до квадрата та множення» (Square-and-Multiply) зменшує кількість множень до `O(log d)` (близько 1.5 · k множень для k-бітного степеня). При цьому кожне крок піднесення до квадрата виконується зі сталим часом, щоб унеможливити атаки типу Timing Attack, коли зловмисник вимірює наносекундні затримки у виконанні процесора і відновлює біти приватного ключа `d`.

Проте розшифрування можна додатково прискорити у 4 рази завдяки CRT-оптимізації (Garner's Recombination Algorithm). Замість піднесення до степеня за модулем `N` розрядністю 2048 біт створюються дві незалежні операції за модулями `p` та `q` розрядністю 1024 біти.

Оскільки кубічна складність множення `O(k³)` для k-бітних чисел при зменшенні довжини операнда вдвічі знижує трудомісткість одного множення у `2³ = 8` разів, два 1024-бітних піднесення виконуються за `2 · (1/8) = 1/4` часу від вихідної операції.

```
Класичне розшифрування:  cᵈ mod N           (1 операція над 2048 біт)  ──► Час: 100%
CRT-прискорене:         c_p^(d_p) mod p     (2 операції над 1024 біт)  ──► Час: ~25%
                        c_q^(d_q) mod q
```

---

## Ідіоматична реалізація алгоритмів RSA

Нижче наведено порівняльний код для обчислення модульного піднесення до степеня та прискореного CRT-розшифрування. У вкладці C++ продемонстровано RAII-безпечні контейнери, безпечну роботу з пам'яттю, концепти та відсутність мануального звільнення ресурсів.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// Базова структура приватного ключа RSA з CRT-компонентами
typedef struct {
    uint64_t n;     // Modulus N = p * q
    uint64_t d;     // Private exponent d
    uint64_t p;     // Prime p
    uint64_t q;     // Prime q
    uint64_t dp;    // d_p = d mod (p - 1)
    uint64_t dq;    // d_q = d mod (q - 1)
    uint64_t qinv;  // q_inv = q^(-1) mod p
} rsa_private_key_t;

// Модульне множення для запобігання переповненню uint64_t
static uint64_t mul_mod(uint64_t a, uint64_t b, uint64_t m) {
    uint64_t res = 0;
    a %= m;
    while (b > 0) {
        if (b & 1) {
            res = (res + a) % m;
        }
        a = (a * 2) % m;
        b >>= 1;
    }
    return res;
}

// Модульне піднесення до степеня зі сталим часом кроку (Square-and-Multiply)
uint64_t rsa_mod_pow(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) {
            result = mul_mod(result, base, mod);
        }
        base = mul_mod(base, base, mod);
        exp >>= 1;
    }
    return result;
}

// Прискорене CRT-розшифрування за алгоритмом Гарнера
bool rsa_decrypt_crt(uint64_t ciphertext, const rsa_private_key_t *key, uint64_t *out_msg) {
    if (!key || !out_msg || ciphertext >= key->n) {
        return false;
    }

    // 1. Зменшення за модулями p та q
    uint64_t cp = ciphertext % key->p;
    uint64_t cq = ciphertext % key->q;

    // 2. Незалежні піднесення до степенів
    uint64_t mp = rsa_mod_pow(cp, key->dp, key->p);
    uint64_t mq = rsa_mod_pow(cq, key->dq, key->q);

    // 3. Рекомбінація Гарнера: h = (qinv * (mp - mq + p)) mod p
    uint64_t diff = (mp >= mq) ? (mp - mq) : (mp + key->p - (mq % key->p));
    uint64_t h = mul_mod(key->qinv, diff, key->p);

    // 4. Підсумкове повідомлення: m = mq + h * q
    *out_msg = mq + h * key->q;
    return true;
}

// Захищене зачищення пам'яті приватного ключа
void rsa_secure_wipe_key(rsa_private_key_t *key) {
    if (key) {
        volatile uint8_t *p = (volatile uint8_t *)key;
        size_t n = sizeof(rsa_private_key_t);
        while (n--) {
            *p++ = 0;
        }
    }
}

int main(void) {
    // Демонстраційні прості числа (у реальності 1024+ біт)
    // p = 61, q = 53, n = 3233, e = 17, d = 2753
    rsa_private_key_t key = {
        .n = 3233, .d = 2753,
        .p = 61,   .q = 53,
        .dp = 2753 % 60,  // 53
        .dq = 2753 % 52,  // 49
        .qinv = 38        // 53^(-1) mod 61 = 38
    };

    uint64_t message = 65; // Символ 'A'
    uint64_t ciphertext = rsa_mod_pow(message, 17, key.n);
    printf("Зашифровано (%lu) -> Шифротекст: %lu\n", message, ciphertext);

    uint64_t decrypted = 0;
    if (rsa_decrypt_crt(ciphertext, &key, &decrypted)) {
        printf("CRT-розшифровано -> Текст: %lu\n", decrypted);
    }

    rsa_secure_wipe_key(&key);
    return 0;
}
```
```cpp
#include <iostream>
#include <optional>
#include <stdexcept>
#include <cstdint>
#include <concepts>
#include <algorithm>
#include <span>

namespace crypto {

struct RsaPrivateKey {
    std::uint64_t n{};     // Modulus N
    std::uint64_t d{};     // Private exponent d
    std::uint64_t p{};     // Prime p
    std::uint64_t q{};     // Prime q
    std::uint64_t dp{};    // d mod (p-1)
    std::uint64_t dq{};    // d mod (q-1)
    std::uint64_t qinv{};  // q^(-1) mod p

    ~RsaPrivateKey() noexcept {
        volatile std::uint8_t* ptr = reinterpret_cast<volatile std::uint8_t*>(this);
        std::fill_n(ptr, sizeof(RsaPrivateKey), 0);
    }
};

class RsaEngine {
private:
    static constexpr std::uint64_t mul_mod(std::uint64_t a, std::uint64_t b, std::uint64_t m) noexcept {
        std::uint64_t res = 0;
        a %= m;
        while (b > 0) {
            if (b & 1) {
                res = (res + a) % m;
            }
            a = (a * 2) % m;
            b >>= 1;
        }
        return res;
    }

public:
    static constexpr std::uint64_t mod_pow(std::uint64_t base, std::uint64_t exp, std::uint64_t mod) noexcept {
        std::uint64_t result = 1;
        base %= mod;
        while (exp > 0) {
            if (exp & 1) {
                result = mul_mod(result, base, mod);
            }
            base = mul_mod(base, base, mod);
            exp >>= 1;
        }
        return result;
    }

    [[nodiscard]] static std::optional<std::uint64_t> decrypt_crt(
        std::uint64_t ciphertext, 
        const RsaPrivateKey& key) noexcept 
    {
        if (ciphertext >= key.n) {
            return std::nullopt;
        }

        const std::uint64_t cp = ciphertext % key.p;
        const std::uint64_t cq = ciphertext % key.q;

        const std::uint64_t mp = mod_pow(cp, key.dp, key.p);
        const std::uint64_t mq = mod_pow(cq, key.dq, key.q);

        const std::uint64_t diff = (mp >= mq) ? (mp - mq) : (mp + key.p - (mq % key.p));
        const std::uint64_t h = mul_mod(key.qinv, diff, key.p);

        return mq + h * key.q;
    }
};

} // namespace crypto

int main() {
    crypto::RsaPrivateKey key{
        .n = 3233, .d = 2753,
        .p = 61,   .q = 53,
        .dp = 53,  .dq = 49,
        .qinv = 38
    };

    constexpr std::uint64_t message = 65;
    constexpr std::uint64_t e = 17;

    const std::uint64_t ciphertext = crypto::RsaEngine::mod_pow(message, e, key.n);
    std::cout << "C++ RSA Encrypted: " << ciphertext << '\n';

    if (const auto decrypted = crypto::RsaEngine::decrypt_crt(ciphertext, key)) {
        std::cout << "C++ RSA Decrypted via CRT: " << *decrypted << '\n';
    }
    return 0;
}
```
:::

---

## Пастки практичної реалізації та захист

1. **Відсутність доповнення (Textbook RSA):** Шифрування повідомлення напряму як `mᵉ mod N` є детермінованим. Два однакових повідомлення дадуть одинаковий шифротекст, що дозволяє спостерігачу перевіряти гіпотези. Використання схем доповнення **PKCS#1 v1.5** або **OAEP** додає випадкову сіль (salt), роблячи шифрування ймовірнісним.
2. **Атака на помилки обчислення CRT (Bellcore Attack):** Якщо під час розшифрування за допомогою CRT на апаратному рівні (внаслідок збою живлення чи внесення завади) стається помилка в обчисленні `m_p`, а `m_q` обчислюється вірно, виходить зіпсований шифротекст `c'`. Атакуючий обчислює `НСД(c'ᵉ − m, N)` і миттєво отримує один із простих дільників `q`! Для захисту перед видачею результату система повинна перевіряти тотожність `(m')ᵉ ≡ c mod N` або використовувати подвійні перевірки.
3. **Захист від часових атак (Blinding / Blinded Exponentiation):** Щоб захистити піднесення до степеня від вимірювання часу та аналізу потужності (SPA/DPA), використовують метод «сліпого» розшифрування. Перед розшифруванням шифротекст `c` множиться на випадковий фактор `rᵉ mod N`: `c' = (c · rᵉ) mod N`. Після розшифрування `m' = (c')ᵈ mod N = m · r mod N` результат ділиться на `r mod N`, отримуючи `m`. Оскільки обчислення виконуються над випадковим `c'`, витоки часу нічого не повідомляють про справжній шифротекст `c`.
4. **Очищення секретів у пам'яті (Secure Zeroization):** По закінченню роботи з приватним ключем його компоненти у пам'яті RAM повинні бути негайно зачищені. Звичайний `memset()` може бути оптимізований і викинутий компілятором як «невикористовуваний присвоєння» (dead store elimination). Необхідно використовувати `explicit_bzero()`, `OPENSSL_cleanse()` або `volatile` вказівники (у C++) чи деструктори з гарантованим затиранням.
