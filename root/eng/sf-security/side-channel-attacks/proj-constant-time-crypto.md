# ⚙️ Реалізація алгоритмів постійного часу та захист від мікроархітектурних витоків

Класичні методи оптимізації програмного коду, розроблені теорією компіляторів для задач загального призначення, спрямовані на якомога швидше завершення обчислень: достроковий вихід із циклу при виявленні першої неспівпалої літери, умовні переходи на основі перевірки проміжних значень та використання таблиць підстановок для прискорення складних операцій. У криптографічному контексті кожна така «оптимізація» перетворюється на катастрофічний побічний канал витоку, який дозволяє віддаленому або локальному спостерігачеві повністю відновити секретні ключі без математичного злому алгоритму.

Нижче наведено повну архітектуру та перевірені реалізації криптографічних примітивів постійного часу (англ. *constant-time primitives*), які гарантують абсолютну незалежність часу виконання та адрес звернення до пам'яті від секретних даних, парадигму бітслайсингу (Bitslicing), безпечні табличні вибірки методом лінійного сканування, модуль модульної редукції без ділення, гарантоване очищення пам'яті проти оптимізацій видалення мертвого коду, захист від частотних витоків DVFS (Hertzbleed), інструментацію динамічного аналізу через Valgrind/CTgrind, а також статистичний стенд верифікації витоків за алгоритмом Dudect.

## 1. Фундаментальні правила та мікроархітектурні інваріанти

Для захисту від часових та мікроархітектурних кеш-атак (Flush+Reload, Prime+Probe) будь-яка програмна реалізація, що оперує секретними значеннями (ключами, випадковими числами, відкритими текстами), повинна суворо задовольняти три фундаментальні інваріанти:

1. **Жодних розгалужень за секретними даними (No Secret-Dependent Branches):** Умовні оператори `if`, `switch`, тернарні вирази `? :` та цикли з динамічними умовами зупинки не повинні залежати від секретних змінних. Розгалуження активують блок передбачення переходів процесора (англ. *Branch Prediction Unit, BPU*), заповнюють буфер історії переходів (англ. *Branch History Table, BHT*) та створюють вимірювані коливання часу виконання при помилковому передбаченні (англ. *branch misprediction penalty*), що становить від 15 до 25 тактів на сучасних суперскалярних ядрах x86 та ARM.
2. **Жодних звернень до пам'яті за секретними індексами (No Secret-Dependent Memory Accesses):** Адреса будь-якого читання чи запису в масив або таблицю повинна бути публічною і детермінованою. Операція виду `table[secret_byte]` завантажує відповідну лінію розміром 64 байти в кеш процесора (L1/L2), змінюючи стан кеш-ієрархії. Будь-який паралельний процес або віртуальна машина на тому самому фізичному ядрі може визначити завантажений рядок, вимірюючи час повторного доступу до пам'яті.
3. **Жодних інструкцій зі змінним часом виконання (No Variable-Time Instructions):** Деякі арифметичні інструкції процесора (наприклад, 64-бітне цілочисельне ділення `DIV`/`IDIV` на архітектурах x86 або операції зсуву на змінну кількість бітів на деяких вбудованих мікроконтролерах ARM Cortex-M0/M3) виконуються за різну кількість тактів залежно від величини або кількості старших нульових бітів операндів. Усі такі операції в критичних криптографічних шляхах мають бути замінені на регулярні побітові послідовності.

Усі логічні рішення, селекції даних та перестановки операндів повинні виконуватися виключно через побітову арифметику та маски.

## 2. Парадигма бітслайсингу (Bitslicing)

Альтернативою постійночасовим табличним вибіркам для блокових шифрів (AES, DES, Serpent, ChaCha20) є парадигма **бітслайсингу (Bitslicing)**, запропонована Елі Біхамом (Eli Biham) у 1997 році.

Замість того, щоб представляти стан шифру у вигляді масиву байтів та шукати результати S-box у таблицях пам'яті, бітслайсинг розглядає мікропроцесор як набір паралельних однобітних арифметико-логічних пристроїв (АЛП). Якщо процесор має 64-бітні регістри загального призначення або 256-бітні векторні регістри AVX2, він може одночасно обробляти 64 або 256 незалежних блоків шифрування.

Таблиця S-box перетворюється на чисту булеву логічну схему, складену виключно з логічних вентилів:
- `AND` (`&`);
- `OR` (`|`);
- `XOR` (`^`);
- `NOT` (`~`).

Оскільки в бітслайс-коді повністю відсутні інструкції читання з масивів за індексами (всі дані знаходяться виключно в регістрах процесора), алгоритм стає за побудовою абсолютно неуразливим до будь-яких кеш-атак (Flush+Reload, Prime+Probe, CacheBleed).

## 3. Умовний вибір без розгалужень (Constant-Time Select) та пастки компіляторів

Найпростішим завданням постійночасового програмування є вибір між двома змінними `x` та `y` залежно від секретного булевого прапорця `condition ∈ {0, 1}`: якщо `condition == 1`, повертається `x`, інакше `y`.

Математичний принцип ґрунтується на представленні від'ємних цілих чисел у доповняльному двійковому коді (Two's Complement). Якщо змінна `b` приймає значення `0` або `1`, то операція унарного мінуса `-b` породжує слово, у якому або всі біти дорівнюють нулю, або всі біти дорівнюють одиниці:
- Якщо `b = 0`: `-0 = 0x00000000` (двійкова маска з усіх нулів);
- Якщо `b = 1`: `-1 = 0xFFFFFFFF` (двійкова маска з усіх одиниць).

За допомогою отриманої маски вибір між `x` та `y` обчислюється через побітові операції XOR та AND:
```
mask = -(uint32_t)condition;
result = y ^ (mask & (x ^ y));
```

Якщо `condition = 1`, то `mask = 0xFFFFFFFF`. Тоді `mask & (x ^ y) = x ^ y`, а підсумковий результат `y ^ (x ^ y) = x`.
Якщо `condition = 0`, то `mask = 0x00000000`. Тоді `mask & (x ^ y) = 0`, а підсумковий результат `y ^ 0 = y`.

### Небезпека оптимізацій компілятора

Сучасні компілятори Clang та GCC, аналізуючи вираз `y ^ (-(uint32_t)condition & (x ^ y))` при увімкнених рівнях оптимізації `-O2` або `-O3`, розпізнають у цій побітовій формулі семантику умовного присвоєння `condition ? x : y`. Компілятор прагне оптимізувати машинний код і може згенерувати інструкцію умовного переходу `JNE/JE` або інструкцію умовного копіювання `CMOV`.

Хоча інструкція `CMOV` (Conditional Move) на багатьох сучасних процесорах виконується за фіксований 1 такт, на деяких мікроархітектурах (зокрема Intel Silvermont, Broadwell для деяких регістрових комбінацій та деяких ядрах ARM) `CMOV` реалізована мікрокодом зі спекулятивним виконанням або може зазнавати затримок залежно від готовності операндів. Більше того, якщо компілятор перетворить вираз на інструкцію умовного стрибка `JNE`, код миттєво стає вразливим до атак по BPU.

Для запобігання такій деструктивній оптимізації застосовують **бар'єр компілятора** (англ. *inline assembly barrier*). Інструкція `__asm__ volatile ("" : "+r" (mask))` повідомляє оптимізатору, що значення змінної `mask` може бути непрозоро змінене зовнішнім невідомим асемблерним блоком. Це змушує компілятор зберегти точну побітову послідовність обчислення.

:::tabs
```c
#include <stdint.h>
#include <stddef.h>

/* Бар'єр компілятора: запобігає перетворенню побітової маски на умовні стрибки */
static inline uint32_t ct_barrier_u32(uint32_t x) {
    #if defined(__GNUC__) || defined(__clang__)
    __asm__ volatile ("" : "+r" (x));
    #endif
    return x;
}

static inline uint8_t ct_barrier_u8(uint8_t x) {
    #if defined(__GNUC__) || defined(__clang__)
    __asm__ volatile ("" : "+r" (x));
    #endif
    return x;
}

/* Умовний вибір 32-бітного слова: повертає x, якщо condition == 1, інакше y */
uint32_t ct_select_u32(uint32_t condition, uint32_t x, uint32_t y) {
    uint32_t mask = -condition;
    mask = ct_barrier_u32(mask);
    return y ^ (mask & (x ^ y));
}

/* Умовний вибір для 8-бітного байта */
uint8_t ct_select_u8(uint8_t condition, uint8_t x, uint8_t y) {
    uint8_t mask = (uint8_t)(-(int8_t)condition);
    mask = ct_barrier_u8(mask);
    return (uint8_t)(y ^ (mask & (x ^ y)));
}

/* Умовне копіювання буфера: якщо condition == 1, dst = src, інакше dst не змінюється */
void ct_select_buffer(uint8_t condition, uint8_t *dst, const uint8_t *src, size_t len) {
    uint8_t mask = (uint8_t)(-(int8_t)condition);
    mask = ct_barrier_u8(mask);
    for (size_t i = 0; i < len; ++i) {
        dst[i] ^= mask & (src[i] ^ dst[i]);
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <concepts>

namespace crypto::constant_time {

/* Асемблерний бар'єр для захисту від шкідливих компіляторних перетворень */
template <std::unsigned_integral T>
[[nodiscard]] constexpr T barrier(T val) noexcept {
    #if defined(__GNUC__) || defined(__clang__)
    asm volatile ("" : "+r" (val));
    #endif
    return val;
}

/* Типобезпечний умовний вибір для довільних беззнакових цілих типів */
template <std::unsigned_integral T>
[[nodiscard]] constexpr T select(bool condition, T x, T y) noexcept {
    const T cond_val = condition ? static_cast<T>(1) : static_cast<T>(0);
    const T mask = barrier(static_cast<T>(-static_cast<T>(cond_val)));
    return y ^ (mask & (x ^ y));
}

/* Умовне оновлення діапазону пам'яті std::span */
void select_span(bool condition, std::span<uint8_t> dst, std::span<const uint8_t> src) noexcept {
    if (dst.size() != src.size()) {
        return;
    }
    const uint8_t cond_val = condition ? 1U : 0U;
    const uint8_t mask = barrier(static_cast<uint8_t>(-static_cast<int8_t>(cond_val)));
    for (size_t i = 0; i < dst.size(); ++i) {
        dst[i] ^= mask & (src[i] ^ dst[i]);
    }
}

} // namespace crypto::constant_time
```
:::

## 4. Порівняння пам'яті постійного часу (Constant-Time memcmp)

Стандартна функція мови C `memcmp(a, b, len)` або оператор `==` для контейнерів містять швидкий достроковий вихід: як тільки цикл знаходить перший неспівпалий байт, виконання переривається і функція повертає ненульову різницю.

У криптографічних протоколах (наприклад, перевірка коду автентифікації повідомлення HMAC або імітовставки Poly1305 в протоколі TLS) атакувальник надсилає серверу підроблені підписи. Якщо перший байт підробленого підпису невірний, `memcmp` завершується на першій ітерації циклу (наприклад, за 2 наносекунди). Якщо атакуючий правильно вгадав перший байт, функція перевірить два байти і завершиться за 4 наносекунди. Вимірюючи статистичний розподіл затримок мережевих відповідей сервера, супротивник байт за байтом підбирає дійсний криптографічний підпис для довільного повідомлення.

Безпечна версія `ct_memcmp` зобов'язана виконувати фіксовану кількість ітерацій незалежно від того, де саме виникла відмінність. Вона акумулює побітову різницю через оператор порозрядного АБО (`|=`) для всіх елементів масиву. Після завершення повного проходу акумулятор згортається в нормалізоване значення `0` (якщо блоки ідентичні) або `1` (якщо є хоча б один відмінний біт) без використання умовних операторів.

:::tabs
```c
#include <stdint.h>
#include <stddef.h>

/* Безпечне порівняння двох блоків пам'яті.
   Повертає 0, якщо блоки повністю ідентичні, та 1, якщо є хоча б одна відмінність.
   Час роботи строго пропорційний довжині len і не залежить від вмісту. */
int ct_memcmp(const void *a, const void *b, size_t len) {
    const uint8_t *pa = (const uint8_t *)a;
    const uint8_t *pb = (const uint8_t *)b;
    uint8_t diff = 0;

    for (size_t i = 0; i < len; ++i) {
        diff |= pa[i] ^ pb[i];
    }

    /* Згортання 8-бітного diff: якщо diff != 0, молодший біт результату стає 1.
       Вираз (-(int32_t)diff) генерує від'ємне число для будь-якого diff != 0,
       встановлюючи знаковий біт (31-й біт) в одиницю. */
    uint32_t acc = diff;
    acc = (acc | (uint32_t)(-(int32_t)acc)) >> 31;
    return (int)acc;
}

/* Перевірка на рівність двох чисел: повертає 1, якщо x == y, інакше 0 */
uint32_t ct_is_equal_u32(uint32_t x, uint32_t y) {
    uint32_t diff = x ^ y;
    return ((diff | (uint32_t)(-(int32_t)diff)) >> 31) ^ 1U;
}

/* Перевірка на менше: повертає 1, якщо x < y, інакше 0 */
uint32_t ct_is_less_u32(uint32_t x, uint32_t y) {
    /* x < y <=> різниця x - y генерує позику, або старші знакові біти відрізняються */
    uint32_t diff = x ^ y;
    uint32_t sub = x - y;
    uint32_t borrow = (x & ~y) | ((~diff) & sub);
    return (borrow >> 31) & 1U;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>

namespace crypto::constant_time {

/* Безпечне порівняння двох послідовностей байтів std::span */
[[nodiscard]] bool are_equal(std::span<const uint8_t> a, std::span<const uint8_t> b) noexcept {
    if (a.size() != b.size()) {
        return false;
    }

    uint8_t diff = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        diff |= (a[i] ^ b[i]);
    }

    const uint32_t acc = diff;
    const uint32_t is_zero = ((acc | static_cast<uint32_t>(-static_cast<int32_t>(acc))) >> 31) ^ 1U;
    return is_zero == 1U;
}

/* Перевірка відношення менше (x < y) без розгалужень */
template <std::unsigned_integral T>
[[nodiscard]] constexpr bool is_less(T x, T y) noexcept {
    const T diff = x ^ y;
    const T sub = x - y;
    const T borrow = (x & ~y) | ((~diff) & sub);
    constexpr size_t shift = (sizeof(T) * 8) - 1;
    return ((borrow >> shift) & static_cast<T>(1)) != static_cast<T>(0);
}

} // namespace crypto::constant_time
```
:::

## 5. Безпечні табличні вибірки постійного часу (Constant-Time Table Lookup)

Таблиці замін (S-boxes) у таких алгоритмах, як AES, DES або шахові алгоритми шифрування, традиційно реалізуються у вигляді масивів у пам'яті `uint8_t SBOX[256]`. Пряме звернення `y = SBOX[secret_index]` неминуче призводить до витоку індексу через кеш процесора (атаки Бернштейна, Flush+Reload).

Для усунення витоку застосовують техніку **повного лінійного сканування (Linear Scan Barrel Lookup)**: функція зчитує абсолютно всі 256 елементів таблиці з пам'яті в строго фіксованому порядку. Для кожного елемента обчислюється маска збігу індексу `mask = ct_is_equal_u32(i, secret_index)`, а шукане значення накопичується через побітове АБО (`result |= mask & table[i]`).

Оскільки процесор послідовно завантажує абсолютно всі рядки кешу таблиці в кожному раунді шифрування, стан кешу залишається повністю ідентичним незалежно від значення секретного байта.

:::tabs
```c
#include <stdint.h>
#include <stddef.h>

/* Безпечна вибірка елемента з 256-байтної таблиці без залежності адреси від секрету */
uint8_t ct_lookup_u8_table256(const uint8_t *table, uint8_t secret_index) {
    uint8_t result = 0;
    for (size_t i = 0; i < 256; ++i) {
        /* Обчислюємо маску: 0xFF якщо i == secret_index, інакше 0x00 */
        uint8_t diff = (uint8_t)(i ^ secret_index);
        uint32_t mask32 = ((uint32_t)diff | (uint32_t)(-(int32_t)diff)) >> 31;
        uint8_t match_mask = (uint8_t)((mask32 ^ 1U) * 0xFFU);

        #if defined(__GNUC__) || defined(__clang__)
        __asm__ volatile ("" : "+r" (match_mask));
        #endif

        result |= match_mask & table[i];
    }
    return result;
}

/* Безпечна вибірка 32-бітного слова з масиву розміром 16 елементів (наприклад, T-таблиці) */
uint32_t ct_lookup_u32_array16(const uint32_t *table, uint32_t secret_index) {
    uint32_t result = 0;
    for (uint32_t i = 0; i < 16; ++i) {
        uint32_t diff = i ^ secret_index;
        uint32_t is_match = ((diff | (uint32_t)(-(int32_t)diff)) >> 31) ^ 1U;
        uint32_t mask = -is_match;

        #if defined(__GNUC__) || defined(__clang__)
        __asm__ volatile ("" : "+r" (mask));
        #endif

        result |= mask & table[i];
    }
    return result;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>

namespace crypto::constant_time {

/* Постійночасова вибірка байта з довільної таблиці пам'яті */
[[nodiscard]] uint8_t lookup_u8(std::span<const uint8_t> table, uint8_t secret_idx) noexcept {
    uint8_t result = 0;
    for (size_t i = 0; i < table.size(); ++i) {
        const auto diff = static_cast<uint8_t>(i ^ secret_idx);
        const auto mask32 = (static_cast<uint32_t>(diff) |
                             static_cast<uint32_t>(-static_cast<int32_t>(diff))) >> 31;
        uint8_t match_mask = static_cast<uint8_t>((mask32 ^ 1U) * 0xFFU);
        match_mask = barrier(match_mask);

        result |= static_cast<uint8_t>(match_mask & table[i]);
    }
    return result;
}

/* Вибірка елемента довільного типу з фіксованого масиву std::array */
template <typename T, size_t N>
[[nodiscard]] T lookup_array(const std::array<T, N> &arr, size_t secret_idx) noexcept {
    T result{};
    auto *p_res = reinterpret_cast<uint8_t*>(&result);

    for (size_t i = 0; i < N; ++i) {
        const auto diff = static_cast<uint32_t>(i ^ secret_idx);
        const auto is_match = ((diff | static_cast<uint32_t>(-static_cast<int32_t>(diff))) >> 31) ^ 1U;
        const uint8_t mask = barrier(static_cast<uint8_t>(-static_cast<int8_t>(is_match)));

        const auto *p_elem = reinterpret_cast<const uint8_t*>(&arr[i]);
        for (size_t b = 0; b < sizeof(T); ++b) {
            p_res[b] |= static_cast<uint8_t>(mask & p_elem[b]);
        }
    }
    return result;
}

} // namespace crypto::constant_time
```
:::

## 6. Умовна перестановка значень без розгалужень (Conditional Swap, cswap)

В алгоритмах скалярного множення на еліптичних кривих (драбина Монтгомері, X25519) та обчисленні спільних дільників виникає необхідність поміняти місцями значення двох змінних або масивів `(a, b)`, якщо секретний біт `condition == 1`, і залишити їх на своїх місцях, якщо `condition == 0`.

Класична реалізація `if (condition) { swap(a, b); }` створює прямий побічний витік через різний час виконання гілок та шаблон передбачення переходів процесора. 

Алгоритм `cswap` виконує обмін за формулою:
```
mask = -(uint32_t)condition;
delta = mask & (a ^ b);
a ^= delta;
b ^= delta;
```

Розглянемо механізм роботи цієї формули:
1. Якщо `condition = 1`, то `mask = 0xFFFFFFFF`. Тоді `delta = 0xFFFFFFFF & (a ^ b) = a ^ b`.
   - `a_new = a ^ (a ^ b) = (a ^ a) ^ b = 0 ^ b = b`;
   - `b_new = b ^ (a ^ b) = (b ^ b) ^ a = 0 ^ a = a`.
   Значення `a` та `b` помінялися місцями за 3 побітові операції.
2. Якщо `condition = 0`, то `mask = 0x00000000`. Тоді `delta = 0 & (a ^ b) = 0`.
   - `a_new = a ^ 0 = a`;
   - `b_new = b ^ 0 = b`.
   Значення залишилися незмінними за ту саму кількість процесорних інструкцій і тактів.

:::tabs
```c
#include <stdint.h>
#include <stddef.h>

/* Умовна перестановка двох 64-бітних слів */
void ct_cswap_u64(uint64_t condition, uint64_t *a, uint64_t *b) {
    uint64_t mask = -condition;
    #if defined(__GNUC__) || defined(__clang__)
    __asm__ volatile ("" : "+r" (mask));
    #endif
    uint64_t delta = mask & (*a ^ *b);
    *a ^= delta;
    *b ^= delta;
}

/* Умовна перестановка масивів великих чисел (наприклад, 256-бітних координат точок кривої) */
void ct_cswap_arrays(uint8_t condition, uint8_t *a, uint8_t *b, size_t len) {
    uint8_t mask = (uint8_t)(-(int8_t)condition);
    #if defined(__GNUC__) || defined(__clang__)
    __asm__ volatile ("" : "+r" (mask));
    #endif
    for (size_t i = 0; i < len; ++i) {
        uint8_t delta = mask & (a[i] ^ b[i]);
        a[i] ^= delta;
        b[i] ^= delta;
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <utility>
#include <type_traits>

namespace crypto::constant_time {

/* Умовна перестановка двох довільних об'єктів однакового типу */
template <typename T>
requires std::is_trivially_copyable_v<T>
void cswap(bool condition, T &a, T &b) noexcept {
    auto *pa = reinterpret_cast<uint8_t*>(&a);
    auto *pb = reinterpret_cast<uint8_t*>(&b);
    const uint8_t cond_val = condition ? 1U : 0U;
    uint8_t mask = static_cast<uint8_t>(-static_cast<int8_t>(cond_val));
    mask = barrier(mask);

    for (size_t i = 0; i < sizeof(T); ++i) {
        const uint8_t delta = mask & (pa[i] ^ pb[i]);
        pa[i] ^= delta;
        pb[i] ^= delta;
    }
}

/* Умовна перестановка буферів пам'яті std::span */
void cswap_spans(bool condition, std::span<uint8_t> a, std::span<uint8_t> b) noexcept {
    if (a.size() != b.size()) {
        return;
    }
    const uint8_t cond_val = condition ? 1U : 0U;
    uint8_t mask = static_cast<uint8_t>(-static_cast<int8_t>(cond_val));
    mask = barrier(mask);

    for (size_t i = 0; i < a.size(); ++i) {
        const uint8_t delta = mask & (a[i] ^ b[i]);
        a[i] ^= delta;
        b[i] ^= delta;
    }
}

} // namespace crypto::constant_time
```
:::

## 7. Безпечна драбина Монтгомері для скалярного множення (Montgomery Ladder)

Наївне піднесення до степеня чи скалярне множення точки еліптичної кривої `k · P` методом «Double-and-Add» виконує операцію подвоєння точки на кожному біті скаляра, а операцію додавання — лише тоді, коли біт `k[i] == 1`. 

Це породжує дві фатальні вразливості:
1. **Простий аналіз потужності (SPA):** На осцилограмі споживання струму операція додавання точки `Add` відрізняється за формою та тривалістю від операції подвоєння `Double`. Атакувальник візуально зчитує всі біти секретного ключа з однієї траси.
2. **Таймінг-атака:** Загальний час операції прямо пропорційний кількості одиничних бітів у скалярі.

Драбина Монтгомері (англ. *Montgomery Ladder*, запропонована Пітером Монтгомері у 1987 році) позбавлена обох недоліків. Вона підтримує інваріант пари точок `R₁ - R₀ = P`. На кожному бітовому кроці виконується рівно одне подвоєння і рівно одне додавання точок у фіксованому порядку, а керування операндами здійснюється за допомогою викликів `cswap`.

:::tabs
```c
#include <stdint.h>
#include <stddef.h>

/* Спрощена структура точки на кривій Монтгомері в проективних координатах (X : Z) */
typedef struct {
    uint64_t x;
    uint64_t z;
} CurvePoint;

/* Арифметичний крок драбини: виконує диференційне додавання та подвоєння точок.
   В реальних криптосистемах тут виконуються польові множення та квадратури над GF(2^255 - 19). */
void montgomery_step(CurvePoint *r0, CurvePoint *r1, const CurvePoint *init_p) {
    /* Регулярна послідовність операцій без розгалужень */
    r0->x = r0->x + r1->x;
    r0->z = r0->z * init_p->x;
    r1->x = r1->x * r1->x;
    r1->z = r1->z + init_p->z;
}

/* Скалярне множення постійного часу (Montgomery Ladder) */
CurvePoint montgomery_ladder_ct(const uint8_t *scalar, size_t scalar_bytes, CurvePoint p) {
    CurvePoint r0 = { .x = 1, .z = 0 }; /* Нейтральний елемент (точка на нескінченності) */
    CurvePoint r1 = p;                   /* Початкова точка P */
    uint8_t prev_bit = 0;

    /* Обхід скаляра від старшого біта до молодшого */
    for (int i = (int)scalar_bytes - 1; i >= 0; --i) {
        uint8_t byte = scalar[i];
        for (int b = 7; b >= 0; --b) {
            uint8_t bit = (byte >> b) & 1;
            uint8_t swap = bit ^ prev_bit;

            /* Перестановка регістрів перед обчисленням залежно від зміни біта */
            ct_cswap_arrays(swap, (uint8_t*)&r0, (uint8_t*)&r1, sizeof(CurvePoint));
            montgomery_step(&r0, &r1, &p);

            prev_bit = bit;
        }
    }

    /* Фінальна нормалізуюча перестановка */
    ct_cswap_arrays(prev_bit, (uint8_t*)&r0, (uint8_t*)&r1, sizeof(CurvePoint));
    return r0;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>

namespace crypto::curve {

struct Point {
    uint64_t x{1};
    uint64_t z{0};
};

/* Арифметичний крок драбини Монтгомері */
void montgomery_step(Point &r0, Point &r1, const Point &base) noexcept {
    r0.x = r0.x + r1.x;
    r0.z = r0.z * base.x;
    r1.x = r1.x * r1.x;
    r1.z = r1.z + base.z;
}

/* Постійночасове скалярне множення точки еліптичної кривої */
[[nodiscard]] Point scalar_multiply_ct(std::span<const uint8_t> scalar, const Point &base) noexcept {
    Point r0{ .x = 1, .z = 0 };
    Point r1 = base;
    bool prev_bit = false;

    for (auto it = scalar.rbegin(); it != scalar.rend(); ++it) {
        const uint8_t byte = *it;
        for (int b = 7; b >= 0; --b) {
            const bool bit = ((byte >> b) & 1U) != 0;
            const bool swap_needed = bit ^ prev_bit;

            constant_time::cswap(swap_needed, r0, r1);
            montgomery_step(r0, r1, base);

            prev_bit = bit;
        }
    }

    constant_time::cswap(prev_bit, r0, r1);
    return r0;
}

} // namespace crypto::curve
```
:::

## 8. Модульна редукція без ділення (Constant-Time Barrett Reduction)

В арифметиці скінченних полів та алгоритмах постквантової криптографії (Kyber, Dilithium) постійно виникає операція зведення за модулем `r = a mod q`. Використання стандартного оператора `%` компілюється в інструкцію процесора `DIV`/`IDIV`, яка на більшості архітектур має змінний час виконання залежно від кількості значущих бітів операнда.

Редукція Барретта замінює повільне і нестабільне апаратне ділення на швидке множення з попередньо обчисленою константою `μ = ⌊2ᵏ / q⌋`.

Фінальна корекція результату, яка традиційно записується як `if (r >= q) r -= q;`, реалізується через побітову маску віднімання:

:::tabs
```c
#include <stdint.h>

/* Безпечна модульна редукція за модулем q (для q < 2^15) за алгоритмом Барретта */
uint16_t ct_barrett_reduce_u16(uint32_t a, uint16_t q, uint32_t mu, int k) {
    /* Оцінка частки: quotient ≈ ⌊a / q⌋ */
    uint32_t q_hat = (uint32_t)(((uint64_t)a * mu) >> k);
    uint32_t r = a - q_hat * q;

    /* Корекція: якщо r >= q, віднімаємо q без умовного розгалуження */
    uint32_t is_ge = ct_is_less_u32(r, q) ^ 1U;
    uint32_t mask = -is_ge;

    #if defined(__GNUC__) || defined(__clang__)
    __asm__ volatile ("" : "+r" (mask));
    #endif

    r -= mask & q;
    return (uint16_t)r;
}
```
```cpp
#include <cstdint>
#include <concepts>

namespace crypto::constant_time {

/* Постійночасова редукція Барретта для цілих типів */
template <std::unsigned_integral T, std::unsigned_integral T_Wide>
[[nodiscard]] constexpr T barrett_reduce(T_Wide a, T q, T_Wide mu, int k) noexcept {
    const T_Wide q_hat = (a * mu) >> k;
    T_Wide r = a - q_hat * q;

    const bool is_ge = !is_less(static_cast<T>(r), q);
    const T mask = barrier(static_cast<T>(-static_cast<int32_t>(is_ge ? 1 : 0)));

    r -= static_cast<T_Wide>(mask & q);
    return static_cast<T>(r);
}

} // namespace crypto::constant_time
```
:::

## 9. Гарантоване очищення секретної пам'яті (Secure Memory Zeroization)

Після завершення криптографічної операції всі буфери, що містили приватні ключі, проміжні стани або сесійні секрети, повинні бути негайно заповнені нулями. 

Класичний виклик `memset(secret_key, 0, sizeof(secret_key))` перед виходом із функції є найпоширенішою вразливістю. Оскільки буфер `secret_key` більше не використовується програмою після очищення, оптимізатор компілятора Clang/GCC застосовує оптимізацію видалення мертвого збереження (Dead Store Elimination, DSE) і **повністю видаляє виклик memset із скомпільованого бінарного коду**. У результаті секретні ключі залишаються у відкритому вигляді в оперативній пам'яті та на стеку програми.

Для гарантованого занулення пам'яті застосовують спеціальні неоптимізовувані функції `explicit_bzero` або цикли з `volatile`-вказівниками:

:::tabs
```c
#include <stdint.h>
#include <stddef.h>

/* Гарантоване занулення пам'яті, яке ніколи не видаляється компілятором */
void ct_secure_zero(void *ptr, size_t len) {
    #if defined(__STDC_LIB_EXT1__)
    memset_s(ptr, len, 0, len);
    #elif defined(_MSC_VER)
    SecureZeroMemory(ptr, len);
    #elif defined(__GLIBC__) || defined(__FreeBSD__) || defined(__OpenBSD__)
    explicit_bzero(ptr, len);
    #else
    volatile uint8_t *p = (volatile uint8_t *)ptr;
    while (len--) {
        *p++ = 0;
    }
    __asm__ volatile ("" : : "r" (ptr) : "memory");
    #endif
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <atomic>

namespace crypto::memory {

/* Безпечне стирання чутливих даних із пам'яті */
void secure_cleanse(std::span<uint8_t> buffer) noexcept {
    volatile uint8_t *p = buffer.data();
    for (size_t i = 0; i < buffer.size(); ++i) {
        p[i] = 0;
    }
    #if defined(__GNUC__) || defined(__clang__)
    asm volatile ("" : : "r" (buffer.data()) : "memory");
    #endif
}

} // namespace crypto::memory
```
:::

## 10. Захист від частотного побічного каналу DVFS (Hertzbleed)

У 2022 році дослідники відкрили нову категорію побічних каналів під назвою **Hertzbleed**. Вона показала, що навіть код із абсолютно однаковою кількістю процесорних інструкцій та відсутністю кеш-промахів може витікати через час виконання на сучасних процесорах Intel та AMD.

Причиною є технологія динамічного регулювання напруги та частоти (англ. *Dynamic Voltage and Frequency Scaling, DVFS*). Коли процесор обробляє дані з високою вагою Геммінґа (велика кількість одиниць), динамічна потужність `P = C · V² · f` зростає. Спеціальний мікроконтролер керування живленням процесора (Power Management Unit) фіксує перегрів або стрибок струму і автоматично знижує робочу тактову частоту процесора на кілька сотень мегагерц.

У результаті блок даних з більшою кількістю одиниць виконується за більший фізичний час у мілісекундах, хоча кількість тактів залишається незмінною.

Для захисту від атак класу Hertzbleed криптографічні бібліотеки застосовують маскування операндів або балансування обчислювального навантаження, гарантуючи, що середня вага Геммінґа оброблюваних блоків залишається постійною протягом усього часу роботи алгоритму.

## 11. Динамічний аналіз та інструментація пам'яті (CTgrind / Valgrind)

Автоматичний пошук порушень постійного часу під час виконання програми реалізується через розширення CTgrind для динамічного бінарного аналізатора Valgrind (ідея Адама Ленглі, Adam Langley).

Методологія ґрунтується на концепції відстеження розповсюдження міток конфіденційності (Dynamic Taint Tracking). Область пам'яті, що містить секретні дані (ключі шифрування, приватні скаляри, відкритий текст), позначається для емулятора Valgrind як «неініціалізована» за допомогою макросу `VALGRIND_MAKE_MEM_UNDEFINED(addr, len)`.

Коли процесорний емулятор Valgrind інтерпретує інструкції скомпільованого бінарного файлу:
- Усі арифметичні та побітові операції (XOR, AND, ADD) переносять статус «неініціалізовано» на вихідні регістри без генерації попереджень.
- Якщо програма намагається виконати інструкцію умовного переходу (`JZ`, `JNZ`, `CMOV`) або операцію розіменування пам'яті (`MOV RAX, [RDI + RDX]`), де умова або базовий індекс позначені як «неініціалізовані», Valgrind миттєво генерує фатальне попередження з повним трасуванням стеку: `Conditional jump or move depends on uninitialised value(s)`.

Після завершення критичної обробки публічний результат явно розсекречується викликом `VALGRIND_MAKE_MEM_DEFINED`.

:::tabs
```c
#include <stdint.h>
#include <stddef.h>

#if defined(USE_VALGRIND_CTGRIND)
#include <valgrind/memcheck.h>
#define CT_POISON(addr, len)   VALGRIND_MAKE_MEM_UNDEFINED(addr, len)
#define CT_UNPOISON(addr, len) VALGRIND_MAKE_MEM_DEFINED(addr, len)
#else
#define CT_POISON(addr, len)   ((void)0)
#define CT_UNPOISON(addr, len) ((void)0)
#endif

/* Приклад використання taint-аналізу для верифікації криптографічної обробки */
int verify_signature_instrumented(const uint8_t *secret_key, const uint8_t *sig, size_t len) {
    uint8_t expected_sig[32];
    
    /* 1. Позначаємо секретний ключ як отруєний (таємний) */
    CT_POISON(secret_key, 32);

    /* 2. Обчислюємо очікуваний підпис (усі проміжні значення автоматично отруюються) */
    for (size_t i = 0; i < 32; ++i) {
        expected_sig[i] = secret_key[i] ^ 0x36;
    }

    /* 3. Порівнюємо підписи безпечною функцією ct_memcmp */
    int is_valid = ct_memcmp(expected_sig, sig, len);

    /* 4. Результат перевірки розсекречуємо для прийняття рішення програмою */
    CT_UNPOISON(&is_valid, sizeof(is_valid));
    return is_valid;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>

#if defined(USE_VALGRIND_CTGRIND)
#include <valgrind/memcheck.h>
#endif

namespace crypto::analysis {

/* Обгортка для позначення конфіденційної пам'яті в середовищі Valgrind */
inline void poison_secret(const void *addr, size_t len) noexcept {
    #if defined(USE_VALGRIND_CTGRIND)
    VALGRIND_MAKE_MEM_UNDEFINED(addr, len);
    #else
    (void)addr; (void)len;
    #endif
}

inline void unpoison_public(const void *addr, size_t len) noexcept {
    #if defined(USE_VALGRIND_CTGRIND)
    VALGRIND_MAKE_MEM_DEFINED(addr, len);
    #else
    (void)addr; (void)len;
    #endif
}

template <typename T>
void poison_object(T &obj) noexcept {
    poison_secret(&obj, sizeof(T));
}

template <typename T>
void unpoison_object(T &obj) noexcept {
    unpoison_public(&obj, sizeof(T));
}

} // namespace crypto::analysis
```
:::

## 12. Автоматизований стенд тестування витоків часу (Dudect / Welch's t-test)

Для експериментальної верифікації відсутності витоків часу в розробленому програмному забезпеченні застосовується алгоритм **Dudect** (Reparaz et al., 2016), заснований на непараметричному тесті Велча (Welch's t-test).

Стенд збирає дві великі вибірки вимірювань часу в процесорних тактах за допомогою інструкції `RDTSC` / `RDTSCP`:
- **Клас A (Fixed):** фіксований вектор вхідних даних (наприклад, перевірка підпису, де всі байти повністю збігаються з еталоном);
- **Клас B (Random):** випадковий вектор вхідних даних (де перший або випадковий байт відрізняється).

Для розрахунку вибіркового середнього та дисперсії на льоту без збереження мільйонів замірів у пам'яті використовується стабільний однопрохідний алгоритм Велфорда (англ. *Welford's algorithm*).

Якщо обчислена статистика `|t| > 4.5`, нульова гіпотеза про однаковість розподілів часу відхиляється, і код визнається вразливим до побічних часових атак. Якщо після 100 000 ітерацій `|t| <= 4.5`, код успішно пройшов верифікацію.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>

#if defined(_MSC_VER)
#include <intrin.h>
#else
#include <x86intrin.h>
#endif

/* Однопрохідний чисельно стабільний акумулятор статистики Велфорда */
typedef struct {
    double mean;
    double m2;
    uint64_t count;
} OnlineStats;

void stats_update(OnlineStats *s, double val) {
    s->count++;
    double delta = val - s->mean;
    s->mean += delta / (double)s->count;
    double delta2 = val - s->mean;
    s->m2 += delta * delta2;
}

double stats_variance(const OnlineStats *s) {
    return s->count > 1 ? s->m2 / (double)(s->count - 1) : 0.0;
}

/* Обчислення статистики t-критерію Велча для двох незалежних вибірок */
double welch_t_statistic(const OnlineStats *a, const OnlineStats *b) {
    double var_a = stats_variance(a);
    double var_b = stats_variance(b);
    double num = a->mean - b->mean;
    double den = sqrt((var_a / (double)a->count) + (var_b / (double)b->count));
    return den > 0.0 ? num / den : 0.0;
}

/* Зчитування апаратного лічильника тактів із серіалізацією процесорного конвеєра */
static inline uint64_t read_tsc_serialized(void) {
    #if defined(_MSC_VER)
    return __rdtsc();
    #else
    unsigned int aux;
    return __rdtscp(&aux);
    #endif
}

/* Демонстраційний запуск верифікації функції ct_memcmp */
void run_dudect_verification(size_t num_measurements) {
    OnlineStats fixed_stats = {0};
    OnlineStats random_stats = {0};

    uint8_t key_fixed[32];
    uint8_t input_fixed[32];
    uint8_t input_random[32];

    for (int i = 0; i < 32; ++i) {
        key_fixed[i] = 0x5A;
        input_fixed[i] = 0x5A;
    }

    for (size_t i = 0; i < num_measurements; ++i) {
        /* Клас A: Ідентичні буфери */
        uint64_t t0 = read_tsc_serialized();
        volatile int r1 = ct_memcmp(key_fixed, input_fixed, 32);
        uint64_t t1 = read_tsc_serialized();
        (void)r1;
        stats_update(&fixed_stats, (double)(t1 - t0));

        /* Клас B: Випадковий неспівпалий буфер */
        for (int j = 0; j < 32; ++j) {
            input_random[j] = (uint8_t)rand();
        }
        uint64_t t2 = read_tsc_serialized();
        volatile int r2 = ct_memcmp(key_fixed, input_random, 32);
        uint64_t t3 = read_tsc_serialized();
        (void)r2;
        stats_update(&random_stats, (double)(t3 - t2));
    }

    double t_stat = welch_t_statistic(&fixed_stats, &random_stats);
    printf("TVLA Dudect Результат: t-значення = %.3f (вибірка %zu)\n", t_stat, num_measurements);
    if (fabs(t_stat) > 4.5) {
        printf("УВАГА: Виявлено статистичний витік часу (|t| > 4.5)!\n");
    } else {
        printf("УСПІХ: Код є стійким до часових побічних каналів (|t| <= 4.5).\n");
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <random>
#include <cmath>
#include <cstdint>

#if defined(_MSC_VER)
#include <intrin.h>
#else
#include <x86intrin.h>
#endif

namespace crypto::testing {

class OnlineVariance {
public:
    void add(double x) noexcept {
        ++count_;
        const double delta = x - mean_;
        mean_ += delta / static_cast<double>(count_);
        const double delta2 = x - mean_;
        m2_ += delta * delta2;
    }

    [[nodiscard]] double mean() const noexcept { return mean_; }
    [[nodiscard]] double variance() const noexcept {
        return count_ > 1 ? m2_ / static_cast<double>(count_ - 1) : 0.0;
    }
    [[nodiscard]] uint64_t count() const noexcept { return count_; }

private:
    double mean_{0.0};
    double m2_{0.0};
    uint64_t count_{0};
};

[[nodiscard]] double compute_welch_t(const OnlineVariance &a, const OnlineVariance &b) noexcept {
    const double var_a = a.variance();
    const double var_b = b.variance();
    const double num = a.mean() - b.mean();
    const double den = std::sqrt((var_a / static_cast<double>(a.count())) +
                                 (var_b / static_cast<double>(b.count())));
    return den > 0.0 ? num / den : 0.0;
}

[[nodiscard]] inline uint64_t rdtsc_fence() noexcept {
    #if defined(_MSC_VER)
    return __rdtsc();
    #else
    unsigned int aux;
    return __rdtscp(&aux);
    #endif
}

void verify_leakage(size_t iterations = 100'000) {
    OnlineVariance fixed_dist;
    OnlineVariance random_dist;

    std::array<uint8_t, 32> target_key{};
    target_key.fill(0xAA);

    std::array<uint8_t, 32> fixed_input = target_key;
    std::array<uint8_t, 32> random_input{};

    std::mt19937_64 rng(1337);
    std::uniform_int_distribution<uint32_t> dist_byte(0, 255);

    for (size_t i = 0; i < iterations; ++i) {
        // Вимірювання фіксованого класу
        const uint64_t t0 = rdtsc_fence();
        volatile bool eq1 = constant_time::are_equal(target_key, fixed_input);
        const uint64_t t1 = rdtsc_fence();
        (void)eq1;
        fixed_dist.add(static_cast<double>(t1 - t0));

        // Вимірювання випадкового класу
        for (auto &b : random_input) {
            b = static_cast<uint8_t>(dist_byte(rng));
        }
        const uint64_t t2 = rdtsc_fence();
        volatile bool eq2 = constant_time::are_equal(target_key, random_input);
        const uint64_t t3 = rdtsc_fence();
        (void)eq2;
        random_dist.add(static_cast<double>(t3 - t2));
    }

    const double t_val = compute_welch_t(fixed_dist, random_dist);
    std::cout << "[Dudect C++] t-статистика: " << t_val << " для " << iterations << " ітерацій\n";
    if (std::abs(t_val) > 4.5) {
        std::cout << "[УВАГА] Виявлено статистичний витік часу!\n";
    } else {
        std::cout << "[УСПІХ] Реалізація є криптографічно безпечною.\n";
    }
}

} // namespace crypto::testing
```
:::
