# 📋 Програмні інтерфейси та примітиви константного часу

Стандартні криптографічні інтерфейси та низькорівневі примітиви константного часу усувають часові витоки на рівні операційних систем, мов програмування та системних бібліотек. Програмний захист секретних ключів, паролів та автентифікаційних тегів вимагає детермінованого часу виконання машинного коду: сигнатури функцій захищеного порівняння буферів, безгалузевого умовного вибору та низькорівневих компіляторних бар'єрів гарантують однакову кількість процесорних тактів та ідентичний профіль звернень до пам'яті незалежно від оброблюваних значень.

## Стандартні функції константного порівняння пам'яті

Класична функція `memcmp(const void *s1, const void *s2, size_t n)` зі стандартної бібліотеки C (`<string.h>`) суворо заборонена до використання у криптографічному коді, оскільки її машинна реалізація оптимізована під максимальну швидкість і негайно перериває виконання на першому незбіжному байті. Для безпечної обробки паролів, ключів, підписів, токенів та HMAC використовуються спеціалізовані стандартизовані API:

### 1. `CRYPTO_memcmp` (OpenSSL та LibreSSL)

Бібліотека OpenSSL надає функцію `CRYPTO_memcmp` для захищеного порівняння криптографічних блоків фіксованої довжини.

:::tabs
```c
#include <openssl/crypto.h>

/* Сигнатура та приклад виклику в C */
int verify_token(const uint8_t *user_buf, const uint8_t *secret_buf, size_t len) {
    if (CRYPTO_memcmp(user_buf, secret_buf, len) == 0) {
        return 1; /* Збіг: доступ дозволено */
    }
    return 0; /* Розбіжність */
}
```
```cpp
#include <openssl/crypto.h>
#include <span>
#include <cstdint>

/* Безпечна C++ обгортка для spans */
[[nodiscard]] bool verify_token(std::span<const uint8_t> user_buf, std::span<const uint8_t> secret_buf) noexcept {
    if (user_buf.size() != secret_buf.size()) {
        return false;
    }
    return CRYPTO_memcmp(user_buf.data(), secret_buf.data(), user_buf.size()) == 0;
}
```
:::

- **Параметри:**
  - `a`: Вказівник на перший блок пам'яті;
  - `b`: Вказівник на другий блок пам'яті;
  - `len`: Кількість байтів для повного порівняння.
- **Значення, що повертаються:**
  - `0`: Блоки пам'яті повністю ідентичні за всіма `len` байтами;
  - Ненульове значення (`!= 0`): Виявлено розбіжність хоча б в одному біті.
- **Внутрішній механізм:** Функція гарантовано виконує прохід по всьому масиву довжиною `len` байтів без розгалужень, акумулюючи побітову різницю `XOR` у машинному регістрі за допомогою інструкцій `OR`. Час виконання лінійно залежить виключно від довжини `len` і не залежить від позиції першого неспівпадіння.
- **Вимоги до вирівнювання:** Функція коректно обробляє як вирівняні, так і невирівняні покажчики, проте для оптимізації завантаження на 64-бітних архітектурах рекомендується вирівнювати буфери за межею 8 або 16 байтів.

### 2. `sodium_memcmp` (libsodium)

Криптографічна бібліотека libsodium реалізує власний захищений порівнювач пам'яті з розширеними гарантіями захисту від компіляторних оптимізацій.

:::tabs
```c
#include <sodium.h>

/* Сигнатура та виклик у C */
int check_auth_tag(const unsigned char *tag1, const unsigned char *tag2, size_t len) {
    return (sodium_memcmp(tag1, tag2, len) == 0);
}
```
```cpp
#include <sodium.h>
#include <span>
#include <cstdint>

/* C++ обгортка з перевіркою розмірів */
[[nodiscard]] bool check_auth_tag(std::span<const uint8_t> tag1, std::span<const uint8_t> tag2) noexcept {
    if (tag1.size() != tag2.size()) {
        return false;
    }
    return sodium_memcmp(tag1.data(), tag2.data(), tag1.size()) == 0;
}
```
:::

- **Параметри:** Вказівники на порівнювані масиви та розмір `len`.
- **Значення, що повертаються:**
  - `0`: Вміст пам'яті повністю збігається;
  - `-1`: Виявлено розбіжність.
- **Особливості:** Реалізація містить вбудовані компіляторні бар'єри пам'яті `volatile`, що унеможливлює видалення циклу акумуляції навіть при екстремальних рівнях оптимізації (Link-Time Optimization, LTO) та виключає витік інформації через векторні регістри AVX/SSE.

### 3. `timingsafe_bcmp` (BSD-системи та macOS)

Системний виклик `timingsafe_bcmp` доступний безпосередньо у стандартній бібліотеці C сучасних операційних систем (OpenBSD 4.9+, FreeBSD 12.0+, macOS 10.12.1+, NetBSD 8.0+).

:::tabs
```c
#include <string.h>

/* Сигнатура та системний виклик у BSD C */
int bsd_safe_compare(const void *b1, const void *b2, size_t len) {
    return (timingsafe_bcmp(b1, b2, len) == 0);
}
```
```cpp
#include <string.h>
#include <span>
#include <cstddef>

/* C++ інтерфейс для системного виклику */
[[nodiscard]] bool bsd_safe_compare(std::span<const std::byte> b1, std::span<const std::byte> b2) noexcept {
    if (b1.size() != b2.size()) {
        return false;
    }
    return timingsafe_bcmp(b1.data(), b2.data(), b1.size_bytes()) == 0;
}
```
:::

- **Семантика повернення:** Повертає `0` у разі повної ідентичності буферів, або ненульове число при розбіжності. На відміну від застарілої функції `bcmp`, гарантує постійний час виконання на рівні ядра операційної системи.

### Чому `memcmp_s` зі стандарту C11 Annex K не захищає від таймінг-атак

У додатку Annex K стандарту C11 було впроваджено функцію `memcmp_s(const void *s1, rsize_t s1max, const void *s2, rsize_t n, int *diff)`. Поширена інженерна помилка полягає у припущенні, що функції з суфіксом `_s` (Bounds-Checking Interfaces) забезпечують криптографічну безпеку.

Насправді стандарт C11 специфікує функцію `memcmp_s` виключно для захисту від переповнення буфера (Buffer Overflow) шляхом валідації граничних розмірів `s1max` та `n`. Її внутрішня реалізація використовує той самий достроковий вихід `early-exit`, що й стандартна `memcmp()`. Використання `memcmp_s` у криптографічному контексті є вразливим.

---

## Бібліотека власних примітивів константного часу (C / C++)

Для створення складних криптографічних протоколів (наприклад, операцій на еліптичних кривих Ed25519 або решіткових постквантових схем Kyber та Dilithium) необхідні булеві операції, операції умовного копіювання та умовного обміну, які принципово не створюють інструкцій умовного переходу (`JMP`, `JZ`, `B.EQ`).

Нижче наведено повну бібліотеку базових примітивів:

:::tabs
```c
#include <stdint.h>
#include <stddef.h>

/* Перетворення булевого прапорця (0 або 1) на бітову маску (0x00..0 або 0xFF..F) */
static inline uint32_t ct_bool_to_mask32(uint32_t bit) {
    return (uint32_t)(-(int32_t)(bit & 1));
}

/* Перевірка на нуль: повертає маску 0xFFFFFFFF якщо val == 0, інакше 0x00000000 */
static inline uint32_t ct_is_zero_mask32(uint32_t val) {
    uint64_t v = val;
    return (uint32_t)(~((v | (0 - v)) >> 31) & 1) ? 0xFFFFFFFFU : 0x00000000U;
}

/* Безгалузевий мультиплексор: якщо mask == 0xFFFFFFFF, повертає a, якщо 0, повертає b */
static inline uint32_t ct_select32(uint32_t mask, uint32_t a, uint32_t b) {
    return (a & mask) | (b & ~mask);
}

/* Умовне копіювання буфера: якщо flag == 1, копіює src в dst, інакше dst не змінюється */
static inline void ct_conditional_copy(uint8_t flag, uint8_t *dst, const uint8_t *src, size_t len) {
    uint8_t mask = (uint8_t)(-(int8_t)(flag & 1));
    for (size_t i = 0; i < len; ++i) {
        dst[i] ^= mask & (src[i] ^ dst[i]);
    }
    /* Компіляторний бар'єр пам'яті */
    __asm__ __volatile__("" : "+m"(*dst) : : "memory");
}

/* Умовний обмін двох буферів (Conditional Swap) за константний час */
static inline void ct_conditional_swap(uint8_t flag, uint8_t *a, uint8_t *b, size_t len) {
    uint8_t mask = (uint8_t)(-(int8_t)(flag & 1));
    for (size_t i = 0; i < len; ++i) {
        uint8_t delta = mask & (a[i] ^ b[i]);
        a[i] ^= delta;
        b[i] ^= delta;
    }
    __asm__ __volatile__("" : "+m"(*a), "+m"(*b) : : "memory");
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>
#include <type_traits>

namespace ct {

// Перетворення прапорця 0/1 у суцільну маску
template <std::unsigned_integral T>
[[nodiscard]] constexpr T to_mask(T bit) noexcept {
    using SignedT = std::make_signed_t<T>;
    return static_cast<T>(-static_cast<SignedT>(bit & 1));
}

// Безгалузевий вибір між двома значеннями
template <std::unsigned_integral T>
[[nodiscard]] constexpr T select(T mask, T a, T b) noexcept {
    return (a & mask) | (b & ~mask);
}

// Умовне копіювання за константний час
template <typename T>
void conditional_copy(bool flag, std::span<T> dst, std::span<const T> src) noexcept {
    if (dst.size() != src.size()) return;

    const uint8_t mask = static_cast<uint8_t>(-static_cast<int8_t>(flag ? 1 : 0));
    auto* dst_bytes = reinterpret_cast<uint8_t*>(dst.data());
    const auto* src_bytes = reinterpret_cast<const uint8_t*>(src.data());
    const size_t total_bytes = dst.size_bytes();

    for (size_t i = 0; i < total_bytes; ++i) {
        dst_bytes[i] ^= mask & (src_bytes[i] ^ dst_bytes[i]);
    }

    asm volatile("" : : "r"(dst_bytes) : "memory");
}

// Умовний обмін пам'яті двох діапазонів
template <typename T>
void conditional_swap(bool flag, std::span<T> a, std::span<T> b) noexcept {
    if (a.size() != b.size()) return;

    const uint8_t mask = static_cast<uint8_t>(-static_cast<int8_t>(flag ? 1 : 0));
    auto* a_bytes = reinterpret_cast<uint8_t*>(a.data());
    auto* b_bytes = reinterpret_cast<uint8_t*>(b.data());
    const size_t total_bytes = a.size_bytes();

    for (size_t i = 0; i < total_bytes; ++i) {
        const uint8_t delta = mask & (a_bytes[i] ^ b_bytes[i]);
        a_bytes[i] ^= delta;
        b_bytes[i] ^= delta;
    }

    asm volatile("" : : "r"(a_bytes), "r"(b_bytes) : "memory");
}

} // namespace ct
```
:::

## Крайові випадки та правила безпечної інтеграції

Під час інтеграції примітивів константного часу в промислові криптографічні бібліотеки необхідно суворо дотримуватися таких інженерних правил:

1. **Обробка буферів нульової довжини (`len == 0`):**
   Функції порівняння при виклику з `len = 0` повинні негайно повертати `0` (вважати рівними) без розіменування вказівників. При цьому довжина буферів `len` сама по собі повинна бути публічною (відкритою) інформацією. Якщо довжина секрету (наприклад, довжина пароля) є конфіденційною, необхідно попередньо доповнити пароль вирівнюванням до фіксованої максимальної довжини.
2. **Перекриття областей пам'яті (Memory Overlap):**
   Примітиви `ct_conditional_copy` та `ct_conditional_swap` вимагають неперетинних буферів (`restrict` у C або унікальні spans у C++). Спроба умовного копіювання в частково перекриті області пам'яті може призвести до спотворення даних.
3. **Заборона оптимізацій часу компонування (LTO):**
   При увімкненому міжпроцедурному аналізі (Interprocedural Optimization, IPO/LTO) компілятор може простежити значення змінних між різними файлами `.c` / `.cpp` і виявити, що прапорець `flag` у конкретному місці виклику завжди дорівнює `0` або `1`, що призведе до видалення безгалузевого коду. Використання асемблерних бар'єрів пам'яті всередині кожного примітиву є обов'язковою гарантією збереження константного часу в релізних бінарних збірках.

---

## Низькорівневі компіляторні бар'єри та апаратні інструкції

### Компіляторні бар'єри оптимізації (Optimization Barriers)

Компілятори GCC та Clang мають потужні оптимізаційні проходи (Loop Idiom Recognition, Dead Code Elimination), які здатні розпізнати побітові акумулятори і згорнути їх у векторні інструкції з раннім перериванням. Для блокування таких оптимізацій застосовуються порожні асемблерні конструкції:

:::tabs
```c
/* Блокування перевпорядкування та видалення змінної у C */
#define HIDE_VALUE(var) __asm__ __volatile__("" : "+r"(var) : : "memory")

/* Блокування оптимізації масивів у пам'яті */
#define MEMORY_BARRIER() __asm__ __volatile__("" : : : "memory")
```
```cpp
#include <concepts>

namespace ct {

// Шаблонна функція приховування значення від компілятора у C++
template <typename T>
inline void hide_value(T& var) noexcept {
    asm volatile("" : "+r"(var) : : "memory");
}

// Повний бар'єр пам'яті
inline void memory_barrier() noexcept {
    asm volatile("" : : "memory");
}

} // namespace ct
```
:::

### Апаратні прапорці детермінованого часу (Hardware DIT Modes)

Сучасні процесорні архітектури мають вбудовані апаратні механізми відключення асинхронних оптимізацій для чутливих регістрів:

1. **ARMv8.4-A Data Independent Timing (PSTATE.DIT):**
   - Вмикається записом у системний регістр: `MSR DIT, #1`.
   - Гарантує, що інструкції множення, ділення та бітових операцій виконуються за фіксовану кількість тактів незалежно від значень операндів.
2. **Intel Data Operand Independent Timing Mode (DOITM):**
   - Вмикається через біт `DOITM` у моделезалежному регістрі `IA32_MCU_OPT_CTRL` (MSR `0x123`).
   - Відключає оптимізації швидкого ділення та раннього виходу на нулях у процесорах архітектури Tiger Lake та новіших.
