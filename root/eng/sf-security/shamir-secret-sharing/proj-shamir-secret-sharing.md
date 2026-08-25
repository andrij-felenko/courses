# ⚙️ Реалізація порогової схеми Шаміра над полем GF(256)

Для практичного використання порогової схеми розділення секрету в сучасних програмних системах (наприклад, для розділення master-паролів, приватних ключів шифрування AES або криптографічних сід-фраз гаманців) математичні обчислення проводять не над велетенськими простими числами, а над скінченними полями Галуа характеристики 2, зокрема над полем `GF(256)` або `GF(2²⁵⁶)`.

Поле `GF(256)` надзвичайно зручне для обчислювальної техніки, оскільки кожен його елемент точно відповідає одному восьмибітовому байту (значенню від 0 до 255). Алгебраїчне додавання в `GF(256)` реалізується як побітова операція «виключного АБО» (`XOR`, оператор `^`), що виконується процесором за один такт. Проте множення й ділення елементів поля є складнішими операціями, оскільки вони вимагають обчислення добутку двочленів за модулем незвідного полінома.

У цій вставці наведено розгорнуті реалізації генерації часток та відновлення секрету мовами C та C++ з використанням канонічного незвідного полінома `p(x) = x⁸ + x⁴ + x³ + x + 1` (із геші-кодом `0x11B`, відомим за стандартом симетричного шифрування AES/Rijndael).

---

### Математичний алгоритм та таблиці поля GF(256)

1. **Незвідний поліном та генератор поля:** Поле `GF(256)` будується як фактор-кільце поліномів за модулем незвідного полінома `p(x) = x⁸ + x⁴ + x³ + x + 1` (у шістнадцятковому вигляді `0x11B`). Елемент `α = 3` (у двоіндексному представленні `x + 1`) є примітивним елементом (генератором) поля `GF(256)`. Ми будуємо два покажчикові масиви: `gf_exp[512]` для степенів генератора `αⁱ mod p(x)` та `gf_log[256]` для зворотного пошуку показника степеня `i = log_α(val)`.
2. **Оптимізація розміру таблиці gf_exp:** Зверніть увагу, що масив `gf_exp` має розмір 512 елементів, а не 256. Це зроблено свідомо для прискорення обчислень: сума двох логарифмів `gf_log[a] + gf_log[b]` може досягати `254 + 254 = 508`. Завдяки дублюванню перших 255 елементів у другу половину масиву (`gf_exp[i] = gf_exp[i - 255]` при `i ≥ 255`), нам не потрібно виконувати умову або операцію взяття модуля `% 255` під час кожного множення.
3. **Арифметика множення двох байтів:** Добуток `a · b` обчислюється за логарифмічною тотожністю:
   ```
   a · b = gf_exp[gf_log[a] + gf_log[b]]
   ```
   за умови, що обидва множники ненульові. Якщо хоча б один із множників дорівнює 0, добуток тотожно дорівнює 0.
4. **Арифметика ділення двох байтів:** Частка `a / b` обчислюється як:
   ```
   a / b = gf_exp[gf_log[a] - gf_log[b] + 255]
   ```
   Додавання константи 255 гарантує відсутність від'ємних індексів під час віднімання логарифмів у масиві.
5. **Побайтове розділення секрету:** Оскільки секрет є довільною послідовністю `N` байтів, дилер обробляє кожен байт окремо. Для кожного байта секрету `S` створюється незалежний випадковий поліном:
   ```
   f(x) = (S + a₁ x + a₂ x² + ... + aₖ₋₁ xᵏ⁻¹) mod GF(256)
   ```
6. **Відновлення через інтерполяційний поліном Лагранжа:** Для відновлення байта секрету за `k` наявними частками `(xᵢ, yᵢ)` обчислюються базисні значення полінома Лагранжа у точці `x = 0`:
   ```
   ℓᵢ(0) = ∏ (xⱼ / (xⱼ ⊕ xᵢ))   [для всіх j від 1 до k, де j ≠ i]
   S = ⨁ (yᵢ · ℓᵢ(0))            [побітове сумування XOR]
   ```

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define GF_POLY 0x11B
#define FIELD_SIZE 256

static uint8_t gf_exp[512];
static uint8_t gf_log[FIELD_SIZE];
static int gf_initialized = 0;

/* Ініціалізація таблиць поля Галуа GF(256) з генератором alpha = 3 */
static void gf_init(void) {
    if (gf_initialized) return;
    uint8_t x = 1;
    for (int i = 0; i < 255; i++) {
        gf_exp[i] = x;
        gf_log[x] = (uint8_t)i;
        /* Множення x на alpha (3 = 2 XOR 1) */
        uint16_t x2 = (uint16_t)(x << 1);
        if (x2 & 0x100) x2 ^= GF_POLY;
        x ^= (uint8_t)x2;
    }
    for (int i = 255; i < 512; i++) {
        gf_exp[i] = gf_exp[i - 255];
    }
    gf_log[0] = 0; /* Невизначено, обробляється окремо */
    gf_initialized = 1;
}

static uint8_t gf_mul(uint8_t a, uint8_t b) {
    if (a == 0 || b == 0) return 0;
    return gf_exp[gf_log[a] + gf_log[b]];
}

static uint8_t gf_div(uint8_t a, uint8_t b) {
    if (b == 0) return 0; /* Помилка: ділення на нуль */
    if (a == 0) return 0;
    return gf_exp[gf_log[a] - gf_log[b] + 255];
}

typedef struct {
    uint8_t x;       /* Ідентифікатор учасника (x != 0) */
    uint8_t *data;   /* Масив значень y для кожного байта секрету */
    size_t len;      /* Довжина секрету в байтах */
} ShareC;

/* Генерація n часток для секрету довжиною secret_len байт з порогом k */
ShareC* create_shares_c(const uint8_t *secret, size_t secret_len, int k, int n) {
    gf_init();
    if (k < 1 || k > n || n >= FIELD_SIZE || secret == NULL) return NULL;

    ShareC *shares = (ShareC*)malloc(sizeof(ShareC) * n);
    if (!shares) return NULL;

    for (int i = 0; i < n; i++) {
        shares[i].x = (uint8_t)(i + 1);
        shares[i].len = secret_len;
        shares[i].data = (uint8_t*)malloc(secret_len);
    }

    uint8_t *coeffs = (uint8_t*)malloc(k);

    for (size_t byte_idx = 0; byte_idx < secret_len; byte_idx++) {
        coeffs[0] = secret[byte_idx]; /* Секрет це вільний член f(0) */
        for (int c = 1; c < k; c++) {
            coeffs[c] = (uint8_t)(rand() % 256); /* У реальності: CSPRNG */
        }

        for (int i = 0; i < n; i++) {
            uint8_t x_val = shares[i].x;
            uint8_t y_val = coeffs[0];
            uint8_t x_pow = 1;

            for (int c = 1; c < k; c++) {
                x_pow = gf_mul(x_pow, x_val);
                y_val ^= gf_mul(coeffs[c], x_pow);
            }
            shares[i].data[byte_idx] = y_val;
        }
    }

    free(coeffs);
    return shares;
}

/* Відновлення секрету за k частками через інтерполяцію Лагранжа */
uint8_t* reconstruct_secret_c(const ShareC *shares, int k, size_t *out_len) {
    gf_init();
    if (shares == NULL || k < 1) return NULL;

    size_t secret_len = shares[0].len;
    uint8_t *secret = (uint8_t*)calloc(secret_len, sizeof(uint8_t));
    if (!secret) return NULL;

    for (size_t byte_idx = 0; byte_idx < secret_len; byte_idx++) {
        uint8_t reconstructed_byte = 0;

        for (int i = 0; i < k; i++) {
            uint8_t xi = shares[i].x;
            uint8_t yi = shares[i].data[byte_idx];

            /* Обчислення базисного полінома Лагранжа li(0) */
            uint8_t li_0 = 1;
            for (int j = 0; j < k; j++) {
                if (i == j) continue;
                uint8_t xj = shares[j].x;
                /* li(0) *= xj / (xj ^ xi) */
                uint8_t num = xj;
                uint8_t den = xj ^ xi;
                li_0 = gf_mul(li_0, gf_div(num, den));
            }
            reconstructed_byte ^= gf_mul(yi, li_0);
        }
        secret[byte_idx] = reconstructed_byte;
    }

    *out_len = secret_len;
    return secret;
}

void free_shares_c(ShareC *shares, int n) {
    if (!shares) return;
    for (int i = 0; i < n; i++) {
        free(shares[i].data);
    }
    free(shares);
}
```

```cpp
#include <iostream>
#include <vector>
#include <array>
#include <random>
#include <stdexcept>
#include <span>
#include <cstdint>

class GaloisField256 {
private:
    static constexpr uint16_t GF_POLY = 0x11B;
    std::array<uint8_t, 512> exp_table{};
    std::array<uint8_t, 256> log_table{};

    GaloisField256() {
        uint8_t x = 1;
        for (int i = 0; i < 255; ++i) {
            exp_table[i] = x;
            log_table[x] = static_cast<uint8_t>(i);
            uint16_t x2 = static_cast<uint16_t>(x << 1);
            if (x2 & 0x100) x2 ^= GF_POLY;
            x ^= static_cast<uint8_t>(x2);
        }
        for (int i = 255; i < 512; ++i) {
            exp_table[i] = exp_table[i - 255];
        }
        log_table[0] = 0;
    }

public:
    static const GaloisField256& instance() {
        static GaloisField256 instance;
        return instance;
    }

    [[nodiscard]] uint8_t multiply(uint8_t a, uint8_t b) const noexcept {
        if (a == 0 || b == 0) return 0;
        return exp_table[log_table[a] + log_table[b]];
    }

    [[nodiscard]] uint8_t divide(uint8_t a, uint8_t b) const {
        if (b == 0) throw std::invalid_argument("Ділення на нуль у GF(256)");
        if (a == 0) return 0;
        return exp_table[log_table[a] - log_table[b] + 255];
    }
};

struct Share {
    uint8_t x{0};
    std::vector<uint8_t> data;
};

class ShamirSecretSharing {
public:
    static std::vector<Share> split(std::span<const uint8_t> secret, size_t k, size_t n) {
        if (k < 1 || k > n || n >= 256) {
            throw std::invalid_argument("Некоректні параметри порогу (k, n)");
        }

        const auto& gf = GaloisField256::instance();
        std::vector<Share> shares(n);
        for (size_t i = 0; i < n; ++i) {
            shares[i].x = static_cast<uint8_t>(i + 1);
            shares[i].data.resize(secret.size());
        }

        std::random_device rd;
        std::mt19937 rng(rd());
        std::uniform_int_distribution<int> dist(0, 255);

        std::vector<uint8_t> coeffs(k);

        for (size_t byte_idx = 0; byte_idx < secret.size(); ++byte_idx) {
            coeffs[0] = secret[byte_idx];
            for (size_t c = 1; c < k; ++c) {
                coeffs[c] = static_cast<uint8_t>(dist(rng));
            }

            for (size_t i = 0; i < n; ++i) {
                uint8_t x_val = shares[i].x;
                uint8_t y_val = coeffs[0];
                uint8_t x_pow = 1;

                for (size_t c = 1; c < k; ++c) {
                    x_pow = gf.multiply(x_pow, x_val);
                    y_val ^= gf.multiply(coeffs[c], x_pow);
                }
                shares[i].data[byte_idx] = y_val;
            }
        }

        return shares;
    }

    static std::vector<uint8_t> reconstruct(std::span<const Share> selected_shares, size_t k) {
        if (selected_shares.size() < k || k < 1) {
            throw std::invalid_argument("Недостатня кількість часток для відновлення");
        }

        const auto& gf = GaloisField256::instance();
        const size_t secret_len = selected_shares[0].data.size();
        std::vector<uint8_t> secret(secret_len, 0);

        for (size_t byte_idx = 0; byte_idx < secret_len; ++byte_idx) {
            uint8_t reconstructed_byte = 0;

            for (size_t i = 0; i < k; ++i) {
                uint8_t xi = selected_shares[i].x;
                uint8_t yi = selected_shares[i].data[byte_idx];

                uint8_t li_0 = 1;
                for (size_t j = 0; j < k; ++j) {
                    if (i == j) continue;
                    uint8_t xj = selected_shares[j].x;
                    uint8_t num = xj;
                    uint8_t den = xj ^ xi;
                    li_0 = gf.multiply(li_0, gf.divide(num, den));
                }
                reconstructed_byte ^= gf.multiply(yi, li_0);
            }
            secret[byte_idx] = reconstructed_byte;
        }

        return secret;
    }
};
```
:::

---

### Порівняльний аналіз реалізацій та архітектурні відмінності

Реалізації мовами C та C++ демонструють принципову різницю в підходах до управління ресурсами, потокобезпечності та безпеки даних під час створення криптографічних модулів:

1. **Управління пам'яттю та RAII:** У версії C++ створення контейнерів `std::vector` та використання семантики переміщення гарантує автоматичне вивільнення оперативної пам'яті під час виходу з области видимості. У сирій реалізації C розробник мусить вручну контролювати парні виклики `malloc()` та `free()`, що при виникненні помилок може призводити до витоку криптографічних даних або аварійного завершення програми.
2. **Інкапсуляція та потокобезпечність:** Реалізація на C++ загортає логіку арифметики `GF(256)` у безпечний синглтон-клас `GaloisField256` із закритими таблицями `exp_table` та `log_table`. Починаючи зі стандарту C++11, ініціалізація локальних статичних змінних (Meyers Singleton) є строго потокобезпечною на рівні мови. Натомість версія на C спирається на глобальний прапорець `gf_initialized` без атоміків або м'ютексів, що при паралельному виклику з двох threads може спричинити стан гонитви (race condition).
3. **Безпечна передача даних:** Вкладинка C++ використовує сучасний стандартний обгортковий тип `std::span<const uint8_t>`, який надає безпечний доступ до неперервної послідовності байтів без створення коштовних копій та без ризику виходу за межі буфера. Реалізація на C змушена передавати сирий вказівник `const uint8_t*` разом з окремим аргументом довжини `size_t secret_len`.

---

### Практичні пастки та безпекові застереження

- **Якість криптографічного генератора випадкових чисел:** Використання базових системних функцій на зразок `rand()` чи `std::mt19937` наведено виключно з демонстраційною метою. У реальних системах безпеки випадкові коефіцієнти полінома `a₁, ..., aₖ₋₁` повинні вибиратися виключно через криптографічно стійкі генератори (CSPRNG): `/dev/urandom` або системний виклик `getrandom()` у Linux, `arc4random()` у BSD/macOS або API `BCryptGenRandom` у Windows. Псевдовипадковість зі слабкою ентропією повністю руйнує досконалу таємність схеми.
- **Очищення секретних даних у оперативній пам'яті:** Після створення часток масиви коефіцієнтів та початкового секрету повинні бути суворо перезаписані нулями за допомогою функцій на зразок `explicit_bzero()` або `sodium_memzero()`. Звичайні виклики `free()` чи деструктори C++ можуть бути оптимізовані компілятором (Dead Store Elimination) і не гарантують негайного стирання даних із фізичної пам'яті RAM, лишаючи їх уразливими для атак через аналіз дампів пам'яті.
- **Унікальність ідентифікаторів `xᵢ`:** Ідентифікатори всіх учасників повинні бути суворо унікальними ненульовими значеннями (`xᵢ ∈ [1, 255]`). Видача двом різним учасникам часток із однаковим значенням `xᵢ` унеможливлює відновлення, а випадкова видача `x = 0` миттєво розкриє сам секрет відповідній особі.
- **Захист від атак по побічних каналах (Side-Channel Attacks):** Операції табличного пошуку `exp_table[log_table[a] + log_table[b]]` звертаються до пам'яті за індексами, які залежать від секретних даних. На сучасних процесорах з кеш-пам'яттю це може створювати витік через затримки кешування (Cache Timing Attacks). У високозахищених сертифікованих криптобібліотеках ділення й множення реалізують безтабличним способом у постійному часі (*constant-time algorithms*).
