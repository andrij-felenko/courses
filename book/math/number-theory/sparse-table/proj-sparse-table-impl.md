# ⚙️ Програмна реалізація розрідженої таблиці на C та C++

Розріджена таблиця (англ. *Sparse Table*) — це високоефективна статична структура даних, яка забезпечує виконання запитів мінімуму, максимуму або найбільшого спільного дільника на відрізку за константний час `O(1)` після передобчислення за `O(N log N)`.

Нижче наведено повну інженерну реалізацію узагальненої розрідженої таблиці, оптимізованої для сучасних процесорних архітектур із використанням апаратних бітових інструкцій для миттєвого обчислення двійкового логарифма.

## Архітектура та вибір схеми розміщення в пам'яті

Найважливішим інженерним рішенням при проектуванні розрідженої таблиці є вибір порядку індексації в пам'яті:
1. **Рівневе розміщення `ST[k][i]` (Row-major by level):** Усі елементи рівня `k` лежать у пам'яті неперервним блоком. Під час побудови таблиці обчислення рівня `k` читає дані з сусідніх комірок попереднього рівня `k - 1`, що забезпечує ідеальну просторову локальність даних та дозволяє процесору задіяти апаратний передзавантажувач ліній кешу (Hardware Prefetcher).
2. **Позиційне розміщення `ST[i][k]` (Column-major):** Стрибки між різними значеннями `i` на фіксованому рівні призводять до постійних промахів кешу L1/L2.

З цієї причини в обох реалізаціях використовується суцільний плоский масив, де комірка `(k, i)` адресується за індексом `k * N + i`.

### Механізм взаємодії з процесорним кешем

Сучасні процесори зчитують дані з оперативної пам'яті лініями фіксованого розміру (зазвичай 64 байти). При роботі з 32-бітними цілими числами одна кеш-лінія вміщує рівно 16 сусідніх елементів масиву. 

При рівневій схемі `ST[k][i]` внутрішній цикл заповнення рівня `k` виконує послідовне лінійне сканування:
- Поточний елемент `ST[k - 1][i]` та його сусіди зчитуються з уже завантаженої в L1-кеш лінії.
- Зміщений елемент `ST[k - 1][i + 2^(k - 1)]` утворює другий паралельний потік послідовного читання.
- Блок апаратного передзавантаження (Hardware Stream Prefetcher) виявляє лінійний доступ і автоматично підтягує наступні кеш-лінії з оперативної пам'яті до того, як ядро CPU надішле явну інструкцію читання. Завдяки цьому фаза передобчислення працює на максимальній пропускній здатності шини пам'яті.

При використанні неоптимальної схеми `ST[i][k]` відстань між сусідніми кроками циклу становить `K = ⌊log₂ N⌋ + 1` слів. Для великих масивів це руйнує просторову локальність: кожне звернення вимагає окремої кеш-лінії, що призводить до каскадного вимивання даних (Cache Thrashing) та сповільнює побудову у 3–5 разів.

## Повна реалізація узагальненої структури

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>

/* Тип бінарної ідемпотентної операції */
typedef int32_t (*sparse_op_fn)(int32_t a, int32_t b);

/* Базові арифметичні операції для числових напівґраток */
static inline int32_t op_min(int32_t a, int32_t b) {
    return (a < b) ? a : b;
}

static inline int32_t op_max(int32_t a, int32_t b) {
    return (a > b) ? a : b;
}

static inline int32_t op_gcd(int32_t a, int32_t b) {
    while (b != 0) {
        int32_t t = a % b;
        a = b;
        b = t;
    }
    return (a < 0) ? -a : a;
}

/* Структура розрідженої таблиці */
typedef struct {
    int32_t *table;      /* Плоский масив розміром K * n */
    size_t n;            /* Кількість елементів у масиві */
    size_t max_k;        /* Кількість рівнів степенів двійки */
    sparse_op_fn op;     /* Вказівник на бінарну операцію */
} sparse_table_t;

/* Обчислення k = floor(log2(len)) за один такт через CLZ */
static inline uint32_t fast_log2(uint32_t len) {
    assert(len > 0);
    return 31 - (uint32_t)__builtin_clz(len);
}

/* Створення та ініціалізація розрідженої таблиці */
sparse_table_t *sparse_table_create(const int32_t *arr, size_t n, sparse_op_fn op) {
    if (arr == NULL || n == 0 || op == NULL) {
        return NULL;
    }

    sparse_table_t *st = (sparse_table_t *)malloc(sizeof(sparse_table_t));
    if (st == NULL) return NULL;

    st->n = n;
    st->op = op;
    st->max_k = (size_t)fast_log2((uint32_t)n) + 1;

    /* Виділення пам'яті під K * N елементів */
    st->table = (int32_t *)malloc(st->max_k * st->n * sizeof(int32_t));
    if (st->table == NULL) {
        free(st);
        return NULL;
    }

    /* Рівень k = 0: копіюємо вихідний масив */
    for (size_t i = 0; i < n; ++i) {
        st->table[0 * st->n + i] = arr[i];
    }

    /* Рівні k >= 1: рекурентне об'єднання блоків */
    for (size_t k = 1; k < st->max_k; ++k) {
        size_t half_len = (size_t)1 << (k - 1);
        size_t cur_len = (size_t)1 << k;

        for (size_t i = 0; i + cur_len <= n; ++i) {
            int32_t left_val = st->table[(k - 1) * st->n + i];
            int32_t right_val = st->table[(k - 1) * st->n + (i + half_len)];
            st->table[k * st->n + i] = st->op(left_val, right_val);
        }
    }

    return st;
}

/* Виконання запиту на відрізку [l, r] за O(1) */
int32_t sparse_table_query(const sparse_table_t *st, size_t l, size_t r) {
    assert(st != NULL);
    assert(l <= r && r < st->n);

    uint32_t len = (uint32_t)(r - l + 1);
    uint32_t k = fast_log2(len);
    size_t block_len = (size_t)1 << k;

    int32_t left_block = st->table[k * st->n + l];
    int32_t right_block = st->table[k * st->n + (r - block_len + 1)];

    return st->op(left_block, right_block);
}

/* Звільнення ресурсів */
void sparse_table_destroy(sparse_table_t *st) {
    if (st != NULL) {
        free(st->table);
        free(st);
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <numeric>
#include <concepts>
#include <span>
#include <bit>
#include <cstdint>
#include <cassert>
#include <algorithm>

/* Концепт бінарної ідемпотентної операції */
template <typename Op, typename T>
concept IdempotentOp = requires(Op op, T a, T b) {
    { op(a, b) } -> std::convertible_to<T>;
};

/* Шаблонний клас розрідженої таблиці (C++20) */
template <typename T, typename Op = std::ranges::min>
requires IdempotentOp<Op, T>
class SparseTable {
public:
    explicit SparseTable(std::span<const T> data, Op op = Op{})
        : n_(data.size()), op_(op) {
        if (n_ == 0) return;

        max_k_ = std::bit_width(static_cast<unsigned int>(n_));
        table_.resize(max_k_ * n_);

        /* Рівень k = 0: копіюємо базові елементи */
        for (std::size_t i = 0; i < n_; ++i) {
            at(0, i) = data[i];
        }

        /* Рівні k >= 1: динамічне програмування */
        for (std::size_t k = 1; k < max_k_; ++k) {
            std::size_t half_len = std::size_t{1} << (k - 1);
            std::size_t cur_len = std::size_t{1} << k;

            for (std::size_t i = 0; i + cur_len <= n_; ++i) {
                at(k, i) = op_(at(k - 1, i), at(k - 1, i + half_len));
            }
        }
    }

    /* Запит на відрізку [l, r] за O(1) */
    [[nodiscard]] T query(std::size_t l, std::size_t r) const {
        assert(l <= r && r < n_);
        
        auto len = static_cast<unsigned int>(r - l + 1);
        std::size_t k = std::bit_width(len) - 1;
        std::size_t block_len = std::size_t{1} << k;

        return op_(at(k, l), at(k, r - block_len + 1));
    }

    [[nodiscard]] std::size_t size() const noexcept { return n_; }
    [[nodiscard]] bool empty() const noexcept { return n_ == 0; }

private:
    std::size_t n_{0};
    std::size_t max_k_{0};
    Op op_{};
    std::vector<T> table_{};

    [[nodiscard]] inline T& at(std::size_t k, std::size_t i) noexcept {
        return table_[k * n_ + i];
    }

    [[nodiscard]] inline const T& at(std::size_t k, std::size_t i) const noexcept {
        return table_[k * n_ + i];
    }
};

/* Спеціалізований функтор для операції НСД */
struct GcdOp {
    template <std::integral T>
    constexpr T operator()(T a, T b) const noexcept {
        return std::gcd(a, b);
    }
};
```
:::

## Покроковий розбір виконання запиту на рівні регістрів CPU

Розглянемо, як виконується запит `query(l, r)` після компіляції в машинний код на архітектурі x86-64 або ARM64:
1. **Обчислення довжини:** Регістри `L` та `R` передаються через конвенцію виклику (наприклад, `rdi` та `rsi`). Різниця `len = r - l + 1` обчислюється однією арифметичною інструкцією `sub` / `add`.
2. **Апаратне бітове сканування:** Інструкція `lzcnt eax, edi` (або `clz` на ARM) підраховує кількість провідних нульових бітів у регістрі `len`. Показник `k` отримується відніманням від 31. Ця операція не потребує звернень до пам'яті та виконується без розгалужень за 1 машинний такт.
3. **Обчислення зсуву блоку:** Інструкція бітового зсуву `shl` (або `lsl`) обчислює довжину блоку `1 << k`. Початковий індекс правого блоку `r - (1 << k) + 1` обчислюється за одну інструкцію `lea` або `sub`.
4. **Зчитування з таблиці:** Адреси `table[k * N + l]` та `table[k * N + (r - (1 << k) + 1)]` транслюються в прямі інструкції завантаження `mov`.
5. **Фінальна редукція:** Для мінімуму виконується умовна пересилка `cmp + cmovl`, яка обирає менше з двох чисел без умовного переходу. Для НСД викликається функція Евкліда.

Весь шлях виконання запиту мінімуму складається лише з 6–8 машинних інструкцій і займає приблизно 2–3 наносекунди, що робить розріджену таблицю однією з найшвидших структур в обчислювальній практиці.

## Векторизація побудови через SIMD (AVX2 та NEON)

Оскільки операція об'єднання двох блоків `ST[k][i] = min(ST[k-1][i], ST[k-1][i + 2^(k-1)])` виконується незалежно для всіх позицій `i`, внутрішній цикл побудови ідеально піддається автоматичній та явній векторній оптимізації (SIMD — Single Instruction, Multiple Data):

- **Архітектура x86-64 (AVX2):** Регістри `ymm` шириною 256 бітів вміщують вісім 32-бітних чисел. Інструкція `_mm256_min_epi32` обчислює мінімуми для восьми пар сусідніх блоків одночасно за один такт процесора.
- **Архітектура ARM (NEON):** Векторні регістри `v` шириною 128 бітів обробляють чотири 32-бітні числа за допомогою інструкції `vminq_s32`.

Завдяки рівневому розміщенню `ST[k][i]` сучасні компілятори (GCC з прапорцем `-O3 -mavx2` або Clang) автоматично виконують автовекторизацію внутрішнього циклу, прискорюючи фазу передобчислення у 4–7 разів порівняно з неоптимізованим кодом.

## Тестовий драйвер та верифікація коректності

Нижче наведено зразок верифікаційної програми, яка перевіряє коректність розрідженої таблиці для мінімуму (RMQ) та найбільшого спільного дільника (Range GCD) шляхом порівняння з наївним лінійним пошуком.

:::tabs
```c
int main(void) {
    /* Тестовий масив */
    const int32_t data[] = {14, 9, 3, 7, 2, 5, 8, 12, 19, 6};
    const size_t n = sizeof(data) / sizeof(data[0]);

    sparse_table_t *st_min = sparse_table_create(data, n, op_min);
    assert(st_min != NULL);

    /* Тестування всіх можливих відрізків [l, r] для RMQ */
    for (size_t l = 0; l < n; ++l) {
        for (size_t r = l; r < n; ++r) {
            int32_t expected = data[l];
            for (size_t i = l + 1; i <= r; ++i) {
                if (data[i] < expected) expected = data[i];
            }

            int32_t actual = sparse_table_query(st_min, l, r);
            assert(actual == expected);
        }
    }
    printf("RMQ (C): Усі тести успішно пройдено!\n");
    sparse_table_destroy(st_min);

    /* Тестування для операції НСД */
    const int32_t gcd_data[] = {24, 36, 60, 48, 18, 90, 42, 56};
    const size_t gcd_n = sizeof(gcd_data) / sizeof(gcd_data[0]);

    sparse_table_t *st_gcd = sparse_table_create(gcd_data, gcd_n, op_gcd);
    assert(st_gcd != NULL);

    /* Перевірка конкретного запиту [1, 5] */
    /* Елементи: 36, 60, 48, 18, 90 -> gcd = 6 */
    int32_t res_gcd = sparse_table_query(st_gcd, 1, 5);
    assert(res_gcd == 6);
    printf("Range GCD (C): Запит [1, 5] = %d (очікувано 6) — Успіх!\n", res_gcd);

    sparse_table_destroy(st_gcd);
    return 0;
}
```
```cpp
int main() {
    const std::vector<int> data = {14, 9, 3, 7, 2, 5, 8, 12, 19, 6};

    // Розріджена таблиця мінімумів
    SparseTable<int, auto(*)(int, int) -> int> st_min(
        data, [](int a, int b) { return std::min(a, b); });

    for (std::size_t l = 0; l < data.size(); ++l) {
        for (std::size_t r = l; r < data.size(); ++r) {
            int expected = *std::min_element(data.begin() + l, data.begin() + r + 1);
            int actual = st_min.query(l, r);
            assert(actual == expected);
        }
    }
    std::cout << "RMQ (C++): Усі тести успішно пройдено!\n";

    // Розріджена таблиця найбільшого спільного дільника
    const std::vector<int> gcd_data = {24, 36, 60, 48, 18, 90, 42, 56};
    SparseTable<int, GcdOp> st_gcd(gcd_data);

    int res_gcd = st_gcd.query(1, 5);
    assert(res_gcd == 6);
    std::cout << "Range GCD (C++): Запит [1, 5] = " << res_gcd << " (очікувано 6) — Успіх!\n";

    return 0;
}
```
:::

## Інженерні пастки та крайові випадки

1. **Невизначена поведінка бітових інструкцій при нулі:** Інструкція `__builtin_clz(0)` або інструкція x86 `BSR` над нульовим регістром є апаратно невизначеною поведінкою (Undefined Behavior). Оскільки довжина запиту `len = r - l + 1` для валідного відрізка завжди `≥ 1`, аргумент функції завжди строго додатний. Проте при обробці зовнішніх даних обов'язково слід валідувати межі `l <= r`.
2. **Переповнення бітового зсуву на великих масивах:** Вираз `1 << k` при використанні 32-бітного знакового цілого переповнюється при `k = 31`. Для роботи з великими масивами обов'язково використовувати `(size_t)1 << k` або `1ULL << k`.
3. **Пам'ять для неповних рівнів:** На рівні `k` коректними є лише індекси `i ≤ n - 2^k`. Спроба звернутися до `ST[k][i]` при `i > n - 2^k` призведе до зчитування невизначеного сміття, хоча логіка запиту `O(1)` завжди обирає такі індекси `l` та `r - 2^k + 1`, які гарантовано лежать у межах валідного діапазону.
4. **Передача поліморфних операцій:** У мові C виклик операції через вказівник на функцію `sparse_op_fn` створює непрямий виклик (англ. *indirect call*), що перешкоджає інлайнінгу компілятором. У критичних за швидкістю ділянках коду функцію оператора (наприклад, `op_min`) хардкодять безпосередньо в тіло циклу, або передають як аргумент макросу. У C++ завдяки шаблонам `template <typename Op>` та лямбда-функціям компілятор повністю інлайнить оператор `op_`, генеруючи оптимальний код без накладних витрат на виклик функцій.
5. **Запити нульової довжини та діапазони з одного елемента:** Запит `[l, l]` має довжину `len = 1`, для якої `k = 0`. Обидва блоки вказують на `ST[0][l]`, а підсумковий результат повертає значення єдиного елемента `a[l]` за один крок без спеціальних гілок `if (l == r)`.
