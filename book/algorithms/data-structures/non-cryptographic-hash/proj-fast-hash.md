# ⚙️ Практична реалізація надшвидкої некриптографічної хеш-функції

Код реалізації некриптографічної хеш-функції має забезпечувати максимальну пропускну здатність на процесорах різної архітектури (x86-64, ARM64), правильно обробляти невирівняне читання пам'яті (unaligned memory access) та не порушувати правило суворого псевдонімування типів в мові C/C++ (strict aliasing rule).

У цьому практичному проекті розбирається повна реалізація 64-бітного некриптографічного хешу на основі принципів алгоритмів MurmurHash3 та Wyhash. Алгоритм зчитує вхідні дані 64-бітними блоками (SWAR — SIMD Within A Register), накопичує стан через множення на магічні первинні константи з високою бітовою щільністю та виконує фіналізацію через двосторонній бітовий міксер.

## Проблема невирівняного читання та Strict Aliasing

При розробці високоефективного хешу виникає спокуса розкласти байтовий масив на цілочисельні 64-бітні слова за допомогою прямого приведення типів вказівників:

:::tabs
```c
/* НЕПРАВИЛЬНО у C: Порушення strict aliasing та ризик BUS_ERROR! */
const uint64_t *words = (const uint64_t *)data;
uint64_t block = words[i];
```
```cpp
// НЕПРАВИЛЬНО у C++: Порушення strict aliasing та undefined behavior!
const auto* words = reinterpret_cast<const std::uint64_t*>(data);
std::uint64_t block = words[i];
```
:::

Такий підхід містить дві фундаментальні проблеми низькорівневої інженерії. По-перше, у мовах C та C++ розіменування вказівника типу `uint64_t*`, що вказує на масив `uint8_t`, порушує правило суворого псевдонімування типів (strict aliasing rule). Оптимізувальний компілятор має право припустити, що ці вказівники не можуть посилатися на ту саму ділянку пам'яті, і викинути потрібні інструкції завантаження регістрів, згенерувавши прихований дефект у машиному коді.

По-друге, на деяких архітектурах (наприклад, ARMv7, SPARC або окремих мікроконтролерах) спроба прочитати 64-бітне слово з адреси, не кратної 8 байтам, викликає апаратне виключення вирівнювання (`BUS_ERROR`) або системний перерив ядра.

Професійний спосіб прочитати 64-бітний блок без неокресленої поведінки (UB) та без втрати продуктивності — використання системної функції `memcpy` або меташаблону `std::bit_cast`. Сучасні оптимізувальний компілятори (GCC, Clang, MSVC) розпізнають `memcpy` фіксованого розміру 8 байтів і повністю викреслюють виклик функції, замінюючи його на єдину скалярну інструкцію `MOV` (x86-64) або `LDR` (ARM64).

## Повний вихідний код реалізації

Нижче наведено паралельну реалізацію мовами C (чистий C99/C11) та C++ (сучасний C++20 із підтримкою `std::span` та `std::string_view`).

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <string.h>

/* Магічні константи з високою бітовою щільністю (prime constants) */
static const uint64_t C1 = 0x87c37b91114253d5ULL;
static const uint64_t C2 = 0x4cf5ad432745937fULL;
static const uint64_t FINAL_M1 = 0xff51afd7565a1a5dULL;
static const uint64_t FINAL_M2 = 0xc4ceb9fe1a85ec53ULL;

/* Циклічний зсув бітів ліворуч */
static inline uint64_t rotl64(uint64_t x, int8_t r) {
    return (x << r) | (x >> (64 - r));
}

/* Безпечне зчитування 64-бітного слова незалежно від вирівнювання */
static inline uint64_t load64(const uint8_t *p) {
    uint64_t v;
    memcpy(&v, p, sizeof(v));
    return v;
}

/* Фіналізатор (Avalanche Mixer fmix64) */
static inline uint64_t fmix64(uint64_t k) {
    k ^= k >> 33;
    k *= FINAL_M1;
    k ^= k >> 33;
    k *= FINAL_M2;
    k ^= k >> 33;
    return k;
}

/* Головна функція обчислення 64-бітного хешу */
uint64_t fast_hash64(const void *key, size_t len, uint64_t seed) {
    const uint8_t *data = (const uint8_t *)key;
    const size_t nblocks = len / 8;
    
    uint64_t h1 = seed ^ (len * C1);

    /* 1. Основний цикл обробки 64-бітних блоків */
    for (size_t i = 0; i < nblocks; i++) {
        uint64_t k1 = load64(data + i * 8);

        k1 *= C1;
        k1 = rotl64(k1, 31);
        k1 *= C2;

        h1 ^= k1;
        h1 = rotl64(h1, 27);
        h1 = h1 * 5 + 0x52dce729;
    }

    /* 2. Обробка хвоста (залишок 0..7 байтів) */
    const uint8_t *tail = data + nblocks * 8;
    uint64_t k2 = 0;

    switch (len & 7) {
    case 7: k2 ^= (uint64_t)tail[6] << 48; /* fallthrough */
    case 6: k2 ^= (uint64_t)tail[5] << 40; /* fallthrough */
    case 5: k2 ^= (uint64_t)tail[4] << 32; /* fallthrough */
    case 4: k2 ^= (uint64_t)tail[3] << 24; /* fallthrough */
    case 3: k2 ^= (uint64_t)tail[2] << 16; /* fallthrough */
    case 2: k2 ^= (uint64_t)tail[1] << 8;  /* fallthrough */
    case 1: k2 ^= (uint64_t)tail[0];
            k2 *= C1;
            k2 = rotl64(k2, 31);
            k2 *= C2;
            h1 ^= k2;
    };

    /* 3. Фінальна дифузія */
    h1 ^= len;
    return fmix64(h1);
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <string_view>
#include <span>
#include <bit>

namespace fast_hash {

constexpr std::uint64_t C1 = 0x87c37b91114253d5ULL;
constexpr std::uint64_t C2 = 0x4cf5ad432745937fULL;
constexpr std::uint64_t FINAL_M1 = 0xff51afd7565a1a5dULL;
constexpr std::uint64_t FINAL_M2 = 0xc4ceb9fe1a85ec53ULL;

[[nodiscard]] constexpr std::uint64_t rotl64(std::uint64_t x, std::int8_t r) noexcept {
    return (x << r) | (x >> (64 - r));
}

[[nodiscard]] inline std::uint64_t load64(const std::uint8_t* p) noexcept {
    std::uint64_t v;
    std::memcpy(&v, p, sizeof(v));
    return v;
}

[[nodiscard]] inline std::uint64_t fmix64(std::uint64_t k) noexcept {
    k ^= k >> 33;
    k *= FINAL_M1;
    k ^= k >> 33;
    k *= FINAL_M2;
    k ^= k >> 33;
    return k;
}

// Ідіоматичний С++20 інтерфейс через std::span
[[nodiscard]] std::uint64_t hash64(std::span<const std::uint8_t> data, std::uint64_t seed = 0) noexcept {
    const std::size_t len = data.size();
    const std::size_t nblocks = len / 8;
    const std::uint8_t* ptr = data.data();
    
    std::uint64_t h1 = seed ^ (len * C1);

    for (std::size_t i = 0; i < nblocks; ++i) {
        std::uint64_t k1 = load64(ptr + i * 8);

        k1 *= C1;
        k1 = rotl64(k1, 31);
        k1 *= C2;

        h1 ^= k1;
        h1 = rotl64(h1, 27);
        h1 = h1 * 5 + 0x52dce729;
    }

    const std::uint8_t* tail = ptr + nblocks * 8;
    std::uint64_t k2 = 0;

    switch (len & 7) {
    case 7: k2 ^= static_cast<std::uint64_t>(tail[6]) << 48; [[fallthrough]];
    case 6: k2 ^= static_cast<std::uint64_t>(tail[5]) << 40; [[fallthrough]];
    case 5: k2 ^= static_cast<std::uint64_t>(tail[4]) << 32; [[fallthrough]];
    case 4: k2 ^= static_cast<std::uint64_t>(tail[3]) << 24; [[fallthrough]];
    case 3: k2 ^= static_cast<std::uint64_t>(tail[2]) << 16; [[fallthrough]];
    case 2: k2 ^= static_cast<std::uint64_t>(tail[1]) << 8;  [[fallthrough]];
    case 1: k2 ^= static_cast<std::uint64_t>(tail[0]);
            k2 *= C1;
            k2 = rotl64(k2, 31);
            k2 *= C2;
            h1 ^= k2;
    }

    h1 ^= len;
    return fmix64(h1);
}

// Перевантаження для роботи із std::string_view
[[nodiscard]] inline std::uint64_t hash64(std::string_view str, std::uint64_t seed = 0) noexcept {
    return hash64(std::span<const std::uint8_t>(reinterpret_cast<const std::uint8_t*>(str.data()), str.size()), seed);
}

} // namespace fast_hash
```
:::

## Покроковий аналіз роботи реалізації

1. **Ініціалізація змінної стану (`h1`):** Змінна `h1` ініціалізується початковим значенням `seed`, до якого домішується добуток довжини масиву `len` на первинну константу `C1`. Це гарантує, що навіть до початку обробки блоків стан відображає розмір вхідних даних.
2. **Скалярний цикл SWAR:** Цикл обробляє вхідний масив суцільними 64-бітними словами (`len / 8`). Кожне прочитане число `k1` множиться на непарну константу `C1`, проходить циклічний бітовий зсув на 31 біт ліворуч (`rotl64(k1, 31)`), множиться на другу константу `C2` і додається до акумулятора `h1`. Після цього стан `h1` ротується на 27 бітів і множиться на 5 плюс аддитивний доданок `0x52dce729` для руйнування лінійності.
3. **Обробка хвоста (`switch` з `fallthrough`):** Конструкція `switch (len & 7)` обробляє залишок від 1 до 7 байтів. Каскадна відсутність оператора `break` (з атрибутом `[[fallthrough]]` у C++17) дозволяє упакувати всі байти хвоста у 64-бітне ціле число за один прохід switch без використання внутрішнього циклу.
4. **Фіналізатор `fmix64`:** Після домішування довжини масиву стан пропускається крізь 3 раунди зсувів праворуч на 33 біти та множень на високоефективні константи `FINAL_M1` та `FINAL_M2`. Це розсіює останні бітові кореляції, досягаючи строгого критерію лавини.

## Розгортання циклу та паралелізм на рівні інструкцій (ILP)

Представлений алгоритм використовує один акумулятор `h1`. Кожна наступна ітерація циклу залежить від результату попередньої (`h1` бере участь у розрахунку наступного кроку). Спіраль залежностей за даними (data dependency chain) обмежує швидкодію скалярного конвеєра CPU.

Для досягнення швидкості понад 15–20 Гбайт/с на довгих буферах застосовують розгортання циклу на **4 паралельні акумулятори** (`h1, h2, h3, h4`):

:::tabs
```c
/* Обробка блоків по 32 байти у C */
for (size_t i = 0; i < nblocks_by_32; i++) {
    uint64_t k1 = load64(data + i * 32 + 0);
    uint64_t k2 = load64(data + i * 32 + 8);
    uint64_t k3 = load64(data + i * 32 + 16);
    uint64_t k4 = load64(data + i * 32 + 24);

    h1 = mix_step(h1, k1);
    h2 = mix_step(h2, k2);
    h3 = mix_step(h3, k3);
    h4 = mix_step(h4, k4);
}
uint64_t h = h1 ^ h2 ^ h3 ^ h4;
```
```cpp
// Обробка блоків по 32 байти у C++
for (std::size_t i = 0; i < nblocks_by_32; ++i) {
    std::uint64_t k1 = load64(ptr + i * 32 + 0);
    std::uint64_t k2 = load64(ptr + i * 32 + 8);
    std::uint64_t k3 = load64(ptr + i * 32 + 16);
    std::uint64_t k4 = load64(ptr + i * 32 + 24);

    h1 = mix_step(h1, k1);
    h2 = mix_step(h2, k2);
    h3 = mix_step(h3, k3);
    h4 = mix_step(h4, k4);
}
std::uint64_t h = h1 ^ h2 ^ h3 ^ h4;
```
:::

Оскільки обчислення `h1`, `h2`, `h3` та `h4` є повністю незалежними, суперскалярний процесор виконує інструкції множення та зсуву паралельно на різних арифмометрах (ALU), подвоюючи пропускну здатність алгоритму без використання векторних регістрів.

## Апаратно-прискорені векторами реалізації (SIMD & AES-NI)

Сучасні системні бібліотеки (xxHash, aHash, MeowHash) виходять за межі скалярних операцій ЦПУ, використовуючи два класи апаратних розширень:

1. **Векторні інструкції (AVX2 / AVX-512 / ARM NEON):** Векторний блок обробляє 256 або 512 бітів вхідного масиву за одну інструкцію. Інструкція `VPMADDWD` обчислює множення 16-бітних цілих чисел із накопиченням 32-бітних результатів, паралельно змішуючи 16 паралельних елементів вектора. Це усуває вузькі місця скалярного множника CPU та піднімає пропускну здатність до 25–30 Гбайт/с.
2. **Апаратні раунди шифрування (AES-NI / ARMv8 Crypto):** Векторні інструкції `AESENC` та `AESENCLAST` виконують один раунд шифрування AES (операції SubBytes, ShiftRows, MixColumns, AddRoundKey) за 1 такт CPU у векторних регістрах `xmm`/`ymm`. Алгоритми на кшталт aHash чи MeowHash використовують апаратні раунди AES не для криптографії, а як надпотужний бітовий міксер з ідеальним лавинним ефектом та пропускною здатністю понад 30 Гбайт/с.

## Тестування продуктивності та надійність

При інтеграції реалізації у реальні системні бібліотеки розробник повинен провести тестування за допомогою трьох обов'язкових методик:

1. **Санітарне випробування на детермінованість (Sanity Check):** Перевірка обчислення хешу від фіксованої послідовності (наприклад, 256 байтів від 0x00 до 0xFF) та порівняння результату із контрольною сумою. Це гарантує, що алгоритм згенеровано однаковий код на x86-64, ARM64 та RISC-V.
2. **Профілювання промахів кешу (Cache Miss Profiling):** Перевірка роботи з гарячим кешем (L1 Cache) та холодними буферами в оперативній пам'яті (DRAM). Для коротких ключів (8 байтів) латентність обчислення має становити від 8 до 14 тактів CPU.
3. **Обробка межевих значень (Edge Cases):** Перевірка передачі порожнього бувера (`len = 0`), вказівника на кінець сторінки пам'яті (`page boundary alignment`) та максимального значення довжини `len = SIZE_MAX`.
