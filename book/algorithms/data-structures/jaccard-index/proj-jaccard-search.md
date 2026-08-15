# ⚙️ Практична реалізація швидкого пошуку за схожістю Жаккара

У цій практичній вставці розкрито реалізацію алгоритмів точного обчислення індексу Жаккара, шинглування тексту, побудови інвертованого індексу з префіксним відсіюванням та генерації імовірнісних сигнатур MinHash мовами C та C++.

Наведені рішення побудовано з урахуванням високих вимог до системної продуктивності: мінімізації кількості виділень динамічної пам'яті, забезпечення високої кеш-локальності при доступі до послідовних масивів та оптимізації алгоритмічної складності.

## 1. Точне обчислення індексу Жаккара

Для обчислення схожості між двома відсортованими масивами 64-бітних цілих чисел (які є хеш-значеннями `k`-грам або унікальними ідентифікаторами елементів) застосовують лінійний алгоритм двох вказівників.

Алгоритм послідовно порівнює елементи двох впорядкованих масивів `a` та `b`. На кожному кроці порівнюються поточні значення за вказівниками `i` та `j`. Якщо значення однакові, елемент належить перетину `A ∩ B`, тому лічильник перетину збільшується, а обидва вказівники просуваються на наступну позицію. Якщо значення елемента в першому масиві менше за значення в другому, вказівник першого масиву зміщується праворуч, і навпаки.

Загальна кількість унікальних елементів об'єднання `|A ∪ B|` обчислюється за формулою включення-виключення `|A ∪ B| = |A| + |B| - |A ∩ B|`. Це усуває потребу у фізичному виділенні додаткового масиву для збереження об'єднання у динамічній пам'яті, що дає значну економію ресурсів при мільйонах порівнянь.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

// Точний розрахунок індексу Жаккара для двох відсортованих масивів C
double jaccard_exact_sorted(const uint64_t *a, size_t len_a,
                            const uint64_t *b, size_t len_b) {
    if (len_a == 0 && len_b == 0) return 1.0;
    if (len_a == 0 || len_b == 0) return 0.0;

    size_t i = 0, j = 0;
    size_t intersection_cnt = 0;

    while (i < len_a && j < len_b) {
        if (a[i] == b[j]) {
            intersection_cnt++;
            i++;
            j++;
        } else if (a[i] < b[j]) {
            i++;
        } else {
            j++;
        }
    }

    size_t union_cnt = len_a + len_b - intersection_cnt;
    return (double)intersection_cnt / (double)union_cnt;
}
```
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <span>

// Ідіоматичний C++20 варіант із використанням std::span
double jaccard_exact_sorted(std::span<const uint64_t> a, 
                            std::span<const uint64_t> b) {
    if (a.empty() && b.empty()) return 1.0;
    if (a.empty() || b.empty()) return 0.0;

    size_t i = 0, j = 0;
    size_t intersection_cnt = 0;

    while (i < a.size() && j < b.size()) {
        if (a[i] == b[j]) {
            intersection_cnt++;
            i++;
            j++;
        } else if (a[i] < b[j]) {
            i++;
        } else {
            j++;
        }
    }

    size_t union_cnt = a.size() + b.size() - intersection_cnt;
    return static_cast<double>(intersection_cnt) / static_cast<double>(union_cnt);
}
```
:::

Часова складність даного алгоритму становить `O(|A| + |B|)` операцій порівняння, а просторова складність за пам'яттю дорівнює `O(1)`. Оскільки доступ до масивів відбувається строго послідовно, алгоритм забезпечує максимальну кеш-локальність для процесорів та піддається автоматичній векторизації компілятором.

## 2. Шинглування та побудова k-грам

Перед обчисленням схожості вхідний неструктурований текст перетворюють на відсортований масив хеш-значень `k`-грам за допомогою ковзного вікна.

Процедура шинглування виконує такі етапи обробки:
1. **Перевірка довжини вхідних даних:** Якщо довжина тексту менша за ширину вікна `k`, перетворення неможливе, і функція повертає порожній результат.
2. **Сканування ковзним вікном:** Вікно шириною `k` символів зсувається вздовж тексту на один символ за крок. Для кожного знайденого підрядка обчислюється 64-бітне хеш-значення. У версії для C застосовується хеш-функція FNV-1a, а у C++ — стандартний `std::hash<std::string_view>`.
3. **Сортування масиву хешів:** Утворений масив хеш-значень сортується за зростанням для підготовки до фази вилучення дублікатів та послідовного порівняння.
4. **Ущільнення та дедублікація:** У версії C вилучення повторюваних хешів виконується за один прохід ущільненням масиву на місці, а у C++ — стандартним ідіоматичним викликом `std::sort` та `std::unique`.

:::tabs
```c
#include <string.h>

// Хеш-функція FNV-1a для підрядків
static uint64_t fnv1a_hash(const char *str, size_t len) {
    uint64_t hash = 14695981039346656037ULL;
    for (size_t i = 0; i < len; ++i) {
        hash ^= (uint64_t)(unsigned char)str[i];
        hash *= 1099511628211ULL;
    }
    return hash;
}

// Допоміжна функція порівняння для qsort
static int compare_u64(const void *a, const void *b) {
    uint64_t arg1 = *(const uint64_t *)a;
    uint64_t arg2 = *(const uint64_t *)b;
    if (arg1 < arg2) return -1;
    if (arg1 > arg2) return 1;
    return 0;
}

// Побудова унікального відсортованого масиву хешів k-грам мовою C
size_t create_shingles_c(const char *text, size_t k, uint64_t **out_shingles) {
    size_t text_len = strlen(text);
    if (text_len < k) {
        *out_shingles = NULL;
        return 0;
    }

    size_t count = text_len - k + 1;
    uint64_t *raw = (uint64_t *)malloc(count * sizeof(uint64_t));
    if (!raw) return 0;

    for (size_t i = 0; i < count; ++i) {
        raw[i] = fnv1a_hash(text + i, k);
    }

    qsort(raw, count, sizeof(uint64_t), compare_u64);

    // Дедублікація на місці
    size_t unique_cnt = 0;
    for (size_t i = 0; i < count; ++i) {
        if (i == 0 || raw[i] != raw[i - 1]) {
            raw[unique_cnt++] = raw[i];
        }
    }

    *out_shingles = raw;
    return unique_cnt;
}
```
```cpp
#include <string_view>
#include <vector>
#include <algorithm>
#include <string>

// Ідіоматична C++ реалізація класу шинглування
class Shingler {
public:
    static std::vector<uint64_t> create_shingles(std::string_view text, size_t k) {
        if (text.size() < k) return {};

        size_t count = text.size() - k + 1;
        std::vector<uint64_t> shingles;
        shingles.reserve(count);

        std::hash<std::string_view> hasher;
        for (size_t i = 0; i < count; ++i) {
            shingles.push_back(hasher(text.substr(i, k)));
        }

        std::sort(shingles.begin(), shingles.end());
        shingles.erase(std::unique(shingles.begin(), shingles.end()), shingles.end());

        return shingles;
    }
};
```
:::

Часова складність побудови відсортованого масиву шинглів визначається етапом сортування і становить `O(N · log N)` операцій, де `N = len(text) - k + 1`. Використання хеш-значень замість вихідних підрядків зменшує потрібну пам'ять у `k` разів та прискорює подальші порівняння.

## 3. Генератор сигнатур MinHash

Алгоритм MinHash застосовує `K` універсальних хеш-функцій вида `h_i(x) = (a_i · x + b_i) mod p` для стиснення відсортованого масиву шинглів до сигнатури фіксованої довжини `K` цілих чисел.

Параметри хеш-функцій генеруються випадковим чином за таких умов:
- `a_i` — випадкове ціле число з інтервалу `[1, p - 1]`.
- `b_i` — випадкове ціле число з інтервалу `[0, p - 1]`.
- `p` — велике просте число (наприклад, `4294967311ULL`), що перевищує максимальне значення елементів.

Для кожного індексу `i ∈ {0, ..., K - 1}` функція обчислює хеш-значення для всіх шинглів даного документа й вибирає з них мінімальне значення `min_h`. Масив з `K` знайдених мінімумів утворює підсумкову сигнатуру MinHash.

:::tabs
```c
typedef struct {
    uint64_t a;
    uint64_t b;
} minhash_func_t;

typedef struct {
    size_t k_funcs;
    minhash_func_t *funcs;
    uint64_t prime;
} minhash_generator_t;

minhash_generator_t* minhash_init(size_t k_funcs) {
    minhash_generator_t *gen = (minhash_generator_t*)malloc(sizeof(minhash_generator_t));
    if (!gen) return NULL;

    gen->k_funcs = k_funcs;
    gen->prime = 4294967311ULL; // Велике просте число > 2^32
    gen->funcs = (minhash_func_t*)malloc(k_funcs * sizeof(minhash_func_t));

    for (size_t i = 0; i < k_funcs; ++i) {
        gen->funcs[i].a = (uint64_t)rand() % (gen->prime - 1) + 1;
        gen->funcs[i].b = (uint64_t)rand() % gen->prime;
    }
    return gen;
}

void minhash_compute(const minhash_generator_t *gen, 
                     const uint64_t *shingles, size_t shingle_cnt,
                     uint64_t *out_sig) {
    for (size_t i = 0; i < gen->k_funcs; ++i) {
        uint64_t min_h = UINT64_MAX;
        uint64_t a = gen->funcs[i].a;
        uint64_t b = gen->funcs[i].b;
        uint64_t p = gen->prime;

        for (size_t j = 0; j < shingle_cnt; ++j) {
            uint64_t h = (a * shingles[j] + b) % p;
            if (h < min_h) {
                min_h = h;
            }
        }
        out_sig[i] = min_h;
    }
}

double minhash_similarity_c(const uint64_t *sig_a, const uint64_t *sig_b, size_t k_funcs) {
    size_t matches = 0;
    for (size_t i = 0; i < k_funcs; ++i) {
        if (sig_a[i] == sig_b[i]) {
            matches++;
        }
    }
    return (double)matches / (double)k_funcs;
}

void minhash_free(minhash_generator_t *gen) {
    if (gen) {
        free(gen->funcs);
        free(gen);
    }
}
```
```cpp
#include <random>
#include <memory>
#include <cstdint>

// Оптимізований C++ клас генерації MinHash сигнатур з генератором Mersenne Twister
class MinHashGenerator {
public:
    struct HashParam {
        uint64_t a;
        uint64_t b;
    };

    explicit MinHashGenerator(size_t k_funcs, uint64_t seed = 42) 
        : k_funcs_(k_funcs), prime_(4294967311ULL) {
        std::mt19937_64 rng(seed);
        std::uniform_int_distribution<uint64_t> dist_a(1, prime_ - 1);
        std::uniform_int_distribution<uint64_t> dist_b(0, prime_ - 1);

        params_.reserve(k_funcs_);
        for (size_t i = 0; i < k_funcs_; ++i) {
            params_.push_back({dist_a(rng), dist_b(rng)});
        }
    }

    [[nodiscard]] std::vector<uint64_t> compute(std::span<const uint64_t> shingles) const {
        std::vector<uint64_t> sig(k_funcs_, UINT64_MAX);
        for (size_t i = 0; i < k_funcs_; ++i) {
            const auto& [a, b] = params_[i];
            for (uint64_t item : shingles) {
                uint64_t h = (a * item + b) % prime_;
                if (h < sig[i]) sig[i] = h;
            }
        }
        return sig;
    }

    static double similarity(std::span<const uint64_t> sig_a, std::span<const uint64_t> sig_b) {
        if (sig_a.size() != sig_b.size() || sig_a.empty()) return 0.0;
        size_t matches = 0;
        for (size_t i = 0; i < sig_a.size(); ++i) {
            if (sig_a[i] == sig_b[i]) matches++;
        }
        return static_cast<double>(matches) / static_cast<double>(sig_a.size());
    }

private:
    size_t k_funcs_;
    uint64_t prime_;
    std::vector<HashParam> params_;
};
```
:::

Оцінка схожості двох сигнатур виконується за один прохід масиву довжиною `K` зі складністю `O(K)`. Обчислювальна вартість генерації сигнатури становить `O(K · |A|)` під час первинної обробки документа.

## 4. Демонстраційний приклад роботи

Готова демонстраційна програма ілюструє повний цикл обробки: шинглування текстових рядків, точний розрахунок за відсортованими масивами та імовірнісну оцінку MinHash.

:::tabs
```c
int main(void) {
    const char *doc1 = "пошук за схожістю індекс жаккара алгоритми";
    const char *doc2 = "пошук за схожістю індекс жаккара структури";

    uint64_t *shingles1 = NULL, *shingles2 = NULL;
    size_t len1 = create_shingles_c(doc1, 4, &shingles1);
    size_t len2 = create_shingles_c(doc2, 4, &shingles2);

    double exact_j = jaccard_exact_sorted(shingles1, len1, shingles2, len2);
    printf("Точний коефіцієнт Жаккара: %.4f\n", exact_j);

    // Розрахунок MinHash
    size_t K = 128;
    minhash_generator_t *gen = minhash_init(K);

    uint64_t *sig1 = (uint64_t*)malloc(K * sizeof(uint64_t));
    uint64_t *sig2 = (uint64_t*)malloc(K * sizeof(uint64_t));

    minhash_compute(gen, shingles1, len1, sig1);
    minhash_compute(gen, shingles2, len2, sig2);

    double approx_j = minhash_similarity_c(sig1, sig2, K);
    printf("Оцінка MinHash (K=%1u): %.4f\n", (unsigned)K, approx_j);

    free(shingles1);
    free(shingles2);
    free(sig1);
    free(sig2);
    minhash_free(gen);
    return 0;
}
```
```cpp
int main() {
    std::string doc1 = "пошук за схожістю індекс жаккара алгоритми";
    std::string doc2 = "пошук за схожістю індекс жаккара структури";

    auto sh1 = Shingler::create_shingles(doc1, 4);
    auto sh2 = Shingler::create_shingles(doc2, 4);

    double exact_j = jaccard_exact_sorted(sh1, sh2);
    std::cout << "Точний коефіцієнт Жаккара: " << exact_j << "\n";

    MinHashGenerator gen(128);
    auto sig1 = gen.compute(sh1);
    auto sig2 = gen.compute(sh2);

    double approx_j = MinHashGenerator::similarity(sig1, sig2);
    std::cout << "Оцінка MinHash (K=128): " << approx_j << "\n";

    return 0;
}
```
:::

## 5. Погалузева оптимізація та розмірно-префіксне відсіювання

Під час побудови систем масового пошуку пар кандидатів (All-Pairs Similarity Search) на мільйонах документів точне порівняння кожного з кожним є занадто повільним. Для прискорення застосовують розмірний та префіксний фільтри.

Розмірний фільтр за короткий час `O(1)` перевіряє, чи виконується умова `threshold * len_a <= len_b && len_b <= len_a / threshold`. Якщо розміри множин `|A|` та `|B|` не задовольняють цю нерівність, функція повертає `false`, відсіюючи кандидата без звернення до його елементів.

Префіксний фільтр вимагає побудови інвертованого індексу лише для перших `p_A = |A| - ⌈τ · |A|⌉ + 1` найрідкісніших елементів відсортованої множини. Якщо два документи не мають жодного спільного елемента у своїх префіксах, їхній коефіцієнт Жаккара гарантовано буде нижчим за поріг `τ`.

Завдяки поєднанню розмірного та префіксного відсіювання кількість необхідних парних порівнянь скорочується на 95–99%, що дозволяє обробляти великі масиви даних у реальному часі.

## 6. Типові пастки та інженерні рекомендації

Під час розробки високонавантажених систем пошуку схожості розробники часто припускаються таких типових помилок:

1. **Ділення на нуль при обробці порожніх множин:** Якщо обидві вхідні множини є порожніми (`len_a == 0` та `len_b == 0`), точний алгоритм зобов'язаний явно повертати `1.0` без виконання ділення `0 / 0`.
2. **Арифметичне переповнення 64-бітних цілих:** Вирази вида `(a * item + b)` у генераторі MinHash можуть перевищити межу `2^64 - 1` при добутку великих 64-бітних чисел. Для запобігання переповнення цілочисельний модуль `p` вибирають близько `2^32` (наприклад, `4294967311ULL`), або застосовують 128-бітовий тип `__int128_t` у компіляторах GCC та Clang.
3. **Використання слабких генераторів випадкових чисел:** Використання стандартного `rand()` для генерації коефіцієнтів `a` та `b` у C призводить до корельованих хеш-функцій. У промислових системах рекомендується застосовувати генератор `std::mt19937_64` (C++) або криптографічний псевдовипадковий генератор.
4. **Обробка кодування UTF-8:** При шинглуванні базованому на бітах чи байтах підрядки можуть розсікати багатобайтові символи UTF-8 у середині кодової позиції. Для обробки національних алфавітів перед шинглюванням текст декодують у послідовність 32-бітних Unicode кодових точок (`char32_t`).
