# ⚙️ Програмна реалізація протоколу Шнорра та його симулятора

Практичне розуміння механізмів нульового розголошення вимагає побудови програмної реалізації трьох основних ролей будь-якої криптографічної доказової системи: інтерактивного доводжувача, верифікатора та симулятора. Нижче наведено повну розробку інтерактивного протоколу Шнорра для доведення знання дискретного логарифма над модулем скінченного поля, а також симулятора, що будує невідрізнюваний транскрипт без використання секретного ключа, та екстрактора знань.

Для наочності алгебраїчної структури використовується циклічна група за модулем простого числа `p = 23` з порядком підгрупи `q = 11` та генератором `g = 2`. Усі три компоненти — реальне виконання, симуляція без секрету та екстракція знань — реалізовані мовами C та C++.

## 1. Архітектурні компоненти криптографічного модуля

Програмний комплекс складається з чотирьох взаємопов'язаних системних модулів:

1. **Математичне ядро підгрупи:** Функції піднесення до степеня за модулем (`power_mod`) та обчислення оберненого елемента за розширеним алгоритмом Евкліда (`mod_inverse`). Ці операції реалізують базову алгебру скінченного поля `F_p`. Алгоритм піднесення до степеня використовує бінарний метод (піднесення до квадрата та множення), що працює за логарифмічний час `O(log exp)`. Розширений алгоритм Евкліда знаходить цілі числа `x` та `y`, такі що `a · x + m · y = gcd(a, m) = 1`.
2. **Сесійний транскрипт:** Структура `SchnorrTranscript`, яка фіксує потрійний запис взаємодії `(R, e, s)`: зобов'язання доводжувача `R = gʳ mod p`, випадковий виклик верифікатора `e ∈ Z_q` та підсумкову відповідь `s = (r + e · x) mod q`.
3. **Алгоритм симуляції (HVZK Simulator):** Функція, яка приймає лише публічний ключ `Y` та бажаний виклик `e`, обчислюючи зобов'язання `R` у зворотному порядку за формулою `R = gˢ · Y⁻ᵉ mod p`. Цей модуль підтверджує властивість чесного верифікатора.
4. **Екстрактор знань (Knowledge Extractor):** Алгоритм, який моделює перемотування доводжувача й обчислює секретний ключ `x` із двох транскриптів `t1` та `t2`, що мають однакове зобов'язання `R`, але різні виклики `e₁ ≠ e₂`.

### Потік даних та послідовність кроків між компонентами системи

Процес верифікації проходить чотири послідовні фази. На першій фазі доводжувач обирає випадкове значення ентропії `r` та фіксує зобов'язання `R`. На другій фазі верифікатор генерує некорельований випадковий виклик `e`. На третій фазі доводжувач обчислює лінійну комбінацію `s = r + e·x mod q`. На четвертій фазі верифікатор обчислює дві сторони рівняння й порівнює `gˢ mod p` з добутком `(R · Yᵉ) mod p`.

Кожна фаза має суворі часові межі та вимоги до обробки пам'яті. Усі криптографічні типи передаються за посиланням або через стек, щоб запобігти витоку секретних ключів у динамічну купу. Обробка помилок під час виконання контролюється поверненням булевих прапорців або `std::optional`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

/* Прості криптографічні параметри для демонстрації */
/* p = 23, q = 11, g = 2 (порядок елемента 2 у Z_23* дорівнює 11) */
#define MOD_P 23LL
#define ORDER_Q 11LL
#define GEN_G 2LL

/* Швидке піднесення до степеня за модулем: (base^exp) % mod */
static int64_t power_mod(int64_t base, int64_t exp, int64_t mod) {
    int64_t result = 1;
    base = base % mod;
    while (exp > 0) {
        if (exp % 2 == 1) {
            result = (result * base) % mod;
        }
        base = (base * base) % mod;
        exp /= 2;
    }
    return result;
}

/* Обчислення оберненого елемента за модулем через розширений алгоритм Евкліда */
static int64_t mod_inverse(int64_t a, int64_t m) {
    int64_t m0 = m, t, q;
    int64_t x0 = 0, x1 = 1;
    if (m == 1) return 0;
    while (a > 1) {
        q = a / m;
        t = m;
        m = a % m;
        a = t;
        t = x0;
        x0 = x1 - q * x0;
        x1 = t;
    }
    if (x1 < 0) x1 += m0;
    return x1;
}

/* Структура для зберігання транскрипту взаємодії */
typedef struct {
    int64_t commitment_R;  /* R = g^r mod p */
    int64_t challenge_e;   /* e ∈ [0, q-1] */
    int64_t response_s;    /* s = (r + e * x) mod q */
} SchnorrTranscript;

/* Крок 1: Реальне виконання між Доводжувачем та Верифікатором */
bool run_real_protocol(int64_t secret_x, int64_t random_r, int64_t challenge_e, SchnorrTranscript *out_transcript) {
    /* Обчислення публічного ключа Y = g^x mod p */
    int64_t public_Y = power_mod(GEN_G, secret_x, MOD_P);

    /* 1. Доводжувач надсилає зобов'язання R = g^r mod p */
    int64_t R = power_mod(GEN_G, random_r, MOD_P);

    /* 2. Доводжувач обчислює відповідь s = (r + e * x) mod q */
    int64_t s = (random_r + challenge_e * secret_x) % ORDER_Q;

    out_transcript->commitment_R = R;
    out_transcript->challenge_e = challenge_e;
    out_transcript->response_s = s;

    /* 3. Верифікатор перевіряє: g^s ≡ R * Y^e (mod p) */
    int64_t left_side = power_mod(GEN_G, s, MOD_P);
    int64_t Y_to_e = power_mod(public_Y, challenge_e, MOD_P);
    int64_t right_side = (R * Y_to_e) % MOD_P;

    printf("[Реальний протокол] P(x=%lld): R=%lld, e=%lld, s=%lld -> Перевірка: %lld == %lld\n",
           secret_x, R, challenge_e, s, left_side, right_side);

    return left_side == right_side;
}

/* Крок 2: Симулятор чесного верифікатора (HVZK Simulator) */
/* Симулятор НЕ ZНАЄ secret_x! Він згенеровує валідний транскрипт навпаки */
SchnorrTranscript run_hvzk_simulator(int64_t public_Y, int64_t sim_challenge_e, int64_t sim_response_s) {
    SchnorrTranscript transcript;
    transcript.challenge_e = sim_challenge_e;
    transcript.response_s = sim_response_s;

    /* Симулятор обчислює фальшиве зобов'язання R = g^s * Y^(-e) mod p */
    int64_t g_to_s = power_mod(GEN_G, sim_response_s, MOD_P);
    int64_t Y_to_e = power_mod(public_Y, sim_challenge_e, MOD_P);
    int64_t Y_to_minus_e = mod_inverse(Y_to_e, MOD_P);

    transcript.commitment_R = (g_to_s * Y_to_minus_e) % MOD_P;

    /* Перевіряємо рівність верифікатора для симульованого транскрипту */
    int64_t check_left = power_mod(GEN_G, transcript.response_s, MOD_P);
    int64_t check_right = (transcript.commitment_R * Y_to_e) % MOD_P;

    printf("[Симулятор HVZK] БЕЗ СЕКРЕТУ: R=%lld, e=%lld, s=%lld -> Перевірка: %lld == %lld\n",
           transcript.commitment_R, transcript.challenge_e, transcript.response_s, check_left, check_right);

    return transcript;
}

/* Крок 3: Екстрактор знань (Knowledge Extractor) */
/* Видобуває секрет x з двох транскриптів із однаковим R, але різними e1 != e2 */
int64_t extract_secret(const SchnorrTranscript *t1, const SchnorrTranscript *t2) {
    if (t1->commitment_R != t2->commitment_R) {
        fprintf(stderr, "Помилка екстрактора: зобов'язання R не збігаються!\n");
        return -1;
    }
    if (t1->challenge_e == t2->challenge_e) {
        fprintf(stderr, "Помилка екстрактора: однакові виклики e!\n");
        return -1;
    }

    int64_t delta_s = (t1->response_s - t2->response_s + ORDER_Q) % ORDER_Q;
    int64_t delta_e = (t1->challenge_e - t2->challenge_e + ORDER_Q) % ORDER_Q;
    int64_t inv_delta_e = mod_inverse(delta_e, ORDER_Q);

    int64_t extracted_x = (delta_s * inv_delta_e) % ORDER_Q;
    return extracted_x;
}

int main(void) {
    int64_t secret_x = 7; /* Секретний ключ доводжувача */
    int64_t public_Y = power_mod(GEN_G, secret_x, MOD_P);
    printf("--- Запуск реального протоколу Шнорра ---\n");
    printf("Публічний ключ Y = g^x mod p -> %lld = %lld^%lld mod %lld\n", public_Y, GEN_G, secret_x, MOD_P);

    SchnorrTranscript t1, t2;
    int64_t random_r = 4;

    /* Виконання 1: e = 3 */
    bool ok1 = run_real_protocol(secret_x, random_r, 3, &t1);
    /* Виконання 2 (з тим самим r): e = 8 */
    bool ok2 = run_real_protocol(secret_x, random_r, 8, &t2);

    if (ok1 && ok2) {
        printf("\n--- Запуск екстрактора знань ---\n");
        int64_t recovered_x = extract_secret(&t1, &t2);
        printf("Відновлений секретний ключ x = %lld (Очікувалось: %lld)\n", recovered_x, secret_x);
    }

    printf("\n--- Запуск симулятора (без секретного ключа) ---\n");
    SchnorrTranscript sim_t = run_hvzk_simulator(public_Y, 5, 9);
    (void)sim_t;

    return 0;
}
```
```cpp
#include <iostream>
#include <optional>
#include <stdexcept>
#include <cstdint>

namespace zk {

/* Математичні криптографічні параметри групи */
struct GroupParams {
    std::int64_t mod_p{23};
    std::int64_t order_q{11};
    std::int64_t generator_g{2};
};

/* Специфікація транскрипту Шнорра */
struct Transcript {
    std::int64_t commitment_R;
    std::int64_t challenge_e;
    std::int64_t response_s;
};

class SchnorrProtocol {
private:
    GroupParams params_;

public:
    explicit SchnorrProtocol(GroupParams params = {}) : params_(params) {}

    [[nodiscard]] std::int64_t power_mod(std::int64_t base, std::int64_t exp, std::int64_t mod) const {
        std::int64_t res = 1;
        base %= mod;
        while (exp > 0) {
            if (exp & 1) res = (res * base) % mod;
            base = (base * base) % mod;
            exp >>= 1;
        }
        return res;
    }

    [[nodiscard]] std::int64_t mod_inverse(std::int64_t a, std::int64_t m) const {
        std::int64_t m0 = m, t{}, q{};
        std::int64_t x0 = 0, x1 = 1;
        if (m == 1) return 0;
        while (a > 1) {
            q = a / m;
            t = m;
            m = a % m;
            a = t;
            t = x0;
            x0 = x1 - q * x0;
            x1 = t;
        }
        if (x1 < 0) x1 += m0;
        return x1;
    }

    /* Верифікація транскрипту: g^s == R * Y^e (mod p) */
    [[nodiscard]] bool verify(std::int64_t public_Y, const Transcript& t) const {
        std::int64_t left = power_mod(params_.generator_g, t.response_s, params_.mod_p);
        std::int64_t Y_e = power_mod(public_Y, t.challenge_e, params_.mod_p);
        std::int64_t right = (t.commitment_R * Y_e) % params_.mod_p;
        return left == right;
    }

    /* Інтерактивний доводжувач (Prover) */
    [[nodiscard]] Transcript prove(std::int64_t secret_x, std::int64_t random_r, std::int64_t challenge_e) const {
        std::int64_t R = power_mod(params_.generator_g, random_r, params_.mod_p);
        std::int64_t s = (random_r + challenge_e * secret_x) % params_.order_q;
        return Transcript{R, challenge_e, s};
    }

    /* Симулятор (Simulator) — генерує валідний транскрипт БЕЗ secrets */
    [[nodiscard]] Transcript simulate(std::int64_t public_Y, std::int64_t sim_e, std::int64_t sim_s) const {
        std::int64_t g_s = power_mod(params_.generator_g, sim_s, params_.mod_p);
        std::int64_t Y_e = power_mod(public_Y, sim_e, params_.mod_p);
        std::int64_t inv_Y_e = mod_inverse(Y_e, params_.mod_p);
        std::int64_t R_sim = (g_s * inv_Y_e) % params_.mod_p;
        return Transcript{R_sim, sim_e, sim_s};
    }

    /* Екстрактор знань (Knowledge Extractor) */
    [[nodiscard]] std::optional<std::int64_t> extract(const Transcript& t1, const Transcript& t2) const {
        if (t1.commitment_R != t2.commitment_R || t1.challenge_e == t2.challenge_e) {
            return std::nullopt;
        }
        std::int64_t delta_s = (t1.response_s - t2.response_s + params_.order_q) % params_.order_q;
        std::int64_t delta_e = (t1.challenge_e - t2.challenge_e + params_.order_q) % params_.order_q;
        std::int64_t inv_delta_e = mod_inverse(delta_e, params_.order_q);
        return (delta_s * inv_delta_e) % params_.order_q;
    }
};

} // namespace zk

int main() {
    zk::GroupParams params;
    zk::SchnorrProtocol protocol(params);

    constexpr std::int64_t secret_x = 7;
    const std::int64_t public_Y = protocol.power_mod(params.generator_g, secret_x, params.mod_p);

    std::cout << "[C++ ZK Engine] Публічний ключ Y = " << public_Y << '\n';

    // 1. Чесна взаємодія
    auto t1 = protocol.prove(secret_x, 4, 3);
    bool is_valid = protocol.verify(public_Y, t1);
    std::cout << "[C++ Real Proof] Валідність доказу: " << std::boolalpha << is_valid << '\n';

    // 2. Симуляція без секрету
    auto sim_t = protocol.simulate(public_Y, 5, 9);
    bool is_sim_valid = protocol.verify(public_Y, sim_t);
    std::cout << "[C++ Simulator] Валідність симульованого доказу: " << is_sim_valid << '\n';

    // 3. Екстракція секрету
    auto t2 = protocol.prove(secret_x, 4, 8);
    auto extracted = protocol.extract(t1, t2);
    if (extracted.has_value()) {
        std::cout << "[C++ Extractor] Відновлений секрет x = " << extracted.value() << '\n';
    }

    return 0;
}
```
:::

## 2. Покроковий аналіз виконання та арифметичні пастки

Розглянемо послідовність дій під час запуску функції `extract_secret()` на прикладі реальних чисел.

Початкові дані: `secret_x = 7`, `random_r = 4`, `order_q = 11`.
- **Транскрипт 1:** `e₁ = 3`. Відповідь `s₁ = (4 + 3 · 7) mod 11 = 25 mod 11 = 3`.
- **Транскрипт 2:** `e₂ = 8`. Відповідь `s₂ = (4 + 8 · 7) mod 11 = 60 mod 11 = 5`.

Обчислення екстрактора:
1. `delta_s = (s₁ - s₂ + 11) % 11 = (3 - 5 + 11) % 11 = 9`.
2. `delta_e = (e₁ - e₂ + 11) % 11 = (3 - 8 + 11) % 11 = 6`.
3. Обернений елемент до `6 mod 11`: підбираємо `inv_delta_e`, таке що `6 · inv_delta_e ≡ 1 mod 11`. Оскільки `6 · 2 = 12 ≡ 1 mod 11`, `inv_delta_e = 2`.
4. Відновлений секрет: `x = (delta_s · inv_delta_e) mod 11 = (9 · 2) mod 11 = 18 mod 11 = 7`.

Секретний ключ `7` відновлено ідеально!

### Головні розробницькі пастки та крайові випадки

1. **Від'ємні залишки в операторі `%` мов C та C++:** На відміну от математичного визначення залишку від ділення, де залишок завжди лежить у діапазоні `[0, m-1]`, оператор `%` у мовах C (стандарт C99) та C++ (стандарт C++11) виконується як truncation в бік нуля. Якщо різниця `delta_s = t1.response_s - t2.response_s` виявиться від'ємною, операція `delta_s % ORDER_Q` поверне від'ємне число. Додавання `ORDER_Q` нормалізує значення у додатну область і гарантує коректність роботи подальших модульних алгоритмів.
2. **Повторне використання монет випадковості (Nonce Reuse Attack):** У реалізації екстрактора знань `extract_secret()` наочно продемонстровано, що відбувається, коли доводжувач використовує одне й те саме значення `random_r` для відповіді на два різних виклики `e1 != e2`. Екстрактор будує систему з двох лінійних рівнянь і миттєво обчислює секретний ключ `x`. У підписах Schnorr та EdDSA це призводить до повної компрометації приватного ключа користувача.
3. **Симуляція vs Реальне виконання:** Функція `run_hvzk_simulator` є прямим доказом властивості HVZK. Симулятор приймає параметри `sim_e` та `sim_s` як вхідні дані й обчислює `R = gˢ · Y⁻ᵉ mod p`. Отриманий транскрипт `(R, sim_e, sim_s)` проходитиме верифікацію `verify()` з результатом `true`. Це показує, що без прив'язки часового порядку або хешування входів транскрипт не доводить володіння секретом третьому спостерігачу.
4. **Ідіоматичні відмінності C та C++ реалізацій:** Версія мовою C++ демонструє ідіоматичний підхід до розробки криптографічних бібліотек: використання `std::optional` замість спеціальних від'ємних кодів помилок, капсуляція параметрів групи `GroupParams` всередині класу `SchnorrProtocol`, та позначення методів як `[[nodiscard]]` для запобігання ігноруванню результатів перевірки.
5. **Вимоги до сталого часу виконання (Constant-Time Execution):** Подана реалізація призначена для демонстрації теорії. Виробничий криптографічний код повинен замінити циклічне піднесення до степеня та розширений алгоритм Евкліда на алгоритми з постійним часом виконання (без розгалужень залежно від значень бітів секретного ключа), щоб усунути витік секретного ключа через вимірювання часу виконання на CPU або атак бічних каналів.
6. **Очищення секретної пам'яті:** Усі змінні, що містять секретний ключ `secret_x` та випадкове `random_r`, у промислових системах мають затиратися безпечною функцією (наприклад, `explicit_bzero` або `memset_s`) одразу після використання, щоб запобігти дампу пам'яті.
7. **Обробка помилок оберненого елемента:** Якщо число `a` та модуль `m` не є взаємно простими (`gcd(a, m) != 1`), оберненого елемента за модулем не існує. Модуль `mod_inverse` повинен обробляти цей крайовий випадок і повертати нуль або генерувати виключну ситуацію `std::invalid_argument`.
