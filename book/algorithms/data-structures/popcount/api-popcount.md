# 📋 Довідник інтерфейсів, інтринсиків та апаратних інструкцій бітових операцій

Цей довідник містить вичерпну технічну специфікацію апаратних інструкцій сучасних мікропроцесорних архітектур, низькорівневих компіляторних інтринсиків, інтерфейсів стандартних бібліотек та системних контрактів для обчислення ваги Гемінга (кількості встановлених бітів, popcount), парності бітового слова (parity), а також фундаментальних примітивів позиціонування ранг і вибірка (rank і select).

---

## 1. Апаратні інструкції процесорних архітектур та векторних розширень

Операція підрахунку одиничних розрядів пройшла шлях від спеціалізованого вузла суперкомп'ютерів до базової інструкції процесорних архітектур загального призначення та векторних SIMD-блоків.

### Базові скалярні інструкції архітектури x86 та x86-64

В архітектурі x86-64 операція реалізована інструкцією `POPCNT`, що входить до набору SSE4.2 (на процесорах Intel, починаючи з мікроархітектури Nehalem) та набору Advanced Bit Manipulation (ABM на процесорах AMD, починаючи з K10).

- **Кодування опкоду:** `F3 0F B8 /r` (для 16-, 32- та 64-бітних регістрів і операндів у пам'яті).
- **Підтримувані операнди:** регістри загального призначення `r16`, `r32`, `r64` або комірки оперативної пам'яті `m16`, `m32`, `m64`.
- **Вплив на регістр прапорців (EFLAGS):**
  - Прапорець нуля `ZF` (Zero Flag) встановлюється в `1`, якщо вхідний операнд дорівнює нулю (`src == 0`), і скидається в `0`, якщо у слові є бодай один встановлений біт;
  - Прапорці `CF`, `PF`, `AF`, `SF`, `OF` безумовно скидаються в `0`.
- **Латентність та пропускна здатність:** на сучасних мікроархітектурах Intel Core (Golden Cove, Raptor Cove) та AMD Zen (Zen 3, Zen 4, Zen 5) латентність становить строго 1 машинний такт, а пропускна здатність складає 1–2 інструкції за такт завдяки наявності кількох паралельних конвеєрних портів виконання (виконується в конвеєрному порту 1 на Intel або портах ALU 0/1 на AMD). На старіших архітектурах Sandy Bridge, Ivy Bridge та Haswell латентність становила 3 такти.
- **Мікроархітектурна особливість Haswell / Broadwell (хибна залежність за даними):** через апаратну помилку асинхронного декодера вихідний регістр помилково маркувався як залежний від свого попереднього значення (так звана false dependency). Якщо в циклі значення накопичувалося в один регістр або кілька інструкцій `POPCNT` записували в той самий регістр без проміжного читання, процесор марно очікував завершення попередньої операції. Для усунення затримки конвеєра компілятори GCC і Clang перед інструкцією `POPCNT` вставляють примусове обнулення цільового регістра інструкцією `XOR dst, dst` або `LZCNT`.
- **Апаратна схема обчислення всередині АЛП:** на рівні кремнію скалярний блок `POPCNT` містить дерево суматорів без поширення переносу (Wallace Tree або Carry-Save Tree), яке перетворює 64 окремі біти на 7-бітне двійкове число за один такт синхросигналу без використання циклічних зсувів.

### Векторні розширення x86: AVX-512 VPOPCNTDQ та BITALG

Для масової паралельної обробки бітових масивів компанія Intel представила векторні розширення:

1. **AVX-512 VPOPCNTDQ (Vector Population Count Doubleword and Quadword):**
   - `VPOPCNTD`: паралельний підрахунок одиниць у кожному 32-бітному елементі 512-бітного регістра ZMM (16 незалежних лічильників одночасно) або 256-бітного YMM (8 елементів);
   - `VPOPCNTQ`: паралельний підрахунок одиниць у кожному 64-бітному елементі ZMM (8 лічильників) або YMM (4 елементи);
   - **Маскування виконання (Opmask `k1..k7`):** дозволяє вибірково оновлювати окремі елементи регістра з нульовим маскуванням (`{z}`) або збереженням попередніх значень;
   - **Латентність:** 3 такти, пропускна здатність — 1 інструкція за такт на процесорах Intel Ice Lake, Tiger Lake, Sapphire Rapids, Granite Rapids та AMD Zen 4 / Zen 5.
   - **Енергоспоживання та частотне масштабування:** на відміну від важких інструкцій плаваючої коми AVX-512 FMA, цілочисельні інструкції `VPOPCNTDQ` належать до легкого класу ліцензій (License 0 / License 1) і не викликають зниження базової тактової частоти ядер процесора.

2. **AVX-512 BITALG (Bit Algorithms Extension):**
   - `VPOPCNTB`: побайтовий підрахунок одиниць для 64 окремих байтів у регістрі ZMM;
   - `VPOPCNTW`: підрахунок одиниць для 32 окремих 16-бітних слів у регістрі ZMM;
   - `VPSHUFBITQMB`: бітове позиційне переставляння за маскою, що дозволяє виконувати довільні бітові перестановки та стиснення на рівні окремих бітів.

### Емуляція векторного підрахунку на AVX2 (підхід PSHUFB)

На процесорах, які підтримують лише AVX2 без спеціалізованої інструкції `VPOPCNT`, паралельний підрахунок виконується векторним табличним перетворенням за алгоритмом Войцеха Мули (Wojciech Muła):
1. 256-бітний вектор розбивається на 4-бітні напівбайти (нібли) за допомогою побітового маскування `AND 0x0F` та логічного зсуву праворуч `SRL 4`;
2. Векторна інструкція табличної підстановки байтів `_mm256_shuffle_epi8` (`VPSHUFB`) використовує заздалегідь підготовлену константну 128-бітну або 256-бітну таблицю ваги Гемінга для чисел від 0 до 15;
3. Отримані побайтові суми додаються горизонтально за допомогою інструкції підсумовування абсолютних різниць `_mm256_sad_epu8` (`VPSADBW`), яка згортає по 8 байтів у 64-бітну суму за 1 машинний такт;
4. Цей підхід забезпечує обробку зі швидкістю понад 20 ГБ/с на пам'яті в кеші L1, значно випереджаючи наївний скалярний перебір.

### Архітектура ARM: Advanced SIMD (NEON), SVE та SVE2

- **ARMv8-A NEON:** скалярної інструкції `POPCNT` для регістрів загального призначення в базовому наборі AArch64 не передбачено. Замість цього використовується векторний блок NEON:
  - `CNT Vd.8B, Vn.8B` / `CNT Vd.16B, Vn.16B`: обчислює вагу Гемінга для кожного байта 64- або 128-бітного векторного регістра за табличним або матричним принципом;
  - `ADDV B0, Vn.8B` / `UADDLV H0, Vn.16B`: виконує горизонтальне векторне додавання байтових лічильників в один підсумковий скалярний регістр;
  - Латентність зв'язки `CNT` + `ADDV` на ядрах Cortex-A78, Cortex-X2 та Neoverse-N2 становить 5–6 тактів.
- **ARM SVE / SVE2 (Scalable Vector Extension):**
  - `CNT Zdn.B, Zdn.B`: векторний побайтовий підрахунок для векторів довжиною від 128 до 2048 бітів без прив'язки до фіксованої довжини регістра (Vector-Length Agnostic, VLA);
  - `CNTP Xd, Pg, Pn.B`: апаратний підрахунок кількості активних бітів (істинних предикатів) усередині предикатного регістра. Виконується безпосередньо в скалярний регістр `Xd` за 1–2 такти;
  - `CNTB`, `CNTH`, `CNTW`, `CNTD`: повертає кількість відповідних елементів (байтів, півслів, слів, подвійних слів) у поточному апаратному векторному регістрі, що дозволяє автоматично організовувати цикл обробки довільних масивів без фіксованого кроку.

### Архітектури RISC-V, WebAssembly та графічні процесори NVIDIA CUDA

- **RISC-V Zbb (Basic Bit-Manipulation Extension):**
  - `cpop rd, rs`: підрахунок одиниць у цілому регістрі (32 біти для RV32, 64 біти для RV64);
  - `cpopw rd, rs`: підрахунок одиниць у молодших 32 бітах регістра для 64-бітної архітектури RV64;
  - Латентність інструкції на процесорних ядрах SiFive Performance P550 та XiangShan становить 1 такт.
- **WebAssembly (Wasm MVP & SIMD128):**
  - `i32.popcnt`, `i64.popcnt`: базові скалярні стекові операції для віртуальної машини WebAssembly;
  - `i8x16.popcnt`: операція розширення Fixed-Width SIMD, що обчислює вагу для 16 окремих байтів у 128-бітному векторі.
- **NVIDIA GPU (PTX ISA):**
  - `popc.b32 rd, rs`, `popc.b64 rd, rs`: апаратні інструкції потокового мультипроцесора (Streaming Multiprocessor);
  - `__popc()`, `__popcll()`: вбудовані інтринсики середовища CUDA C/C++;
  - `__ballot_sync()` у поєднанні з `__popc()`: фундаментальний прийом варп-синхронізації для визначення кількості активних ниток варпа (warp reduction), які задовольнили умову гілкування або досягли цільової точки виконання.

---

## 2. Специфікація компіляторних інтринсиків C та C++

### Компілятори GCC та Clang

Компілятори сімейства GCC і Clang надають вбудовані функції з префіксом `__builtin_`. За наявності відповідних цільових прапорців оптимізації компілятор транслює виклик безпосередньо в машинну інструкцію; у разі компіляції під застарілу архітектуру підставляється вбудований безрозгалужений SWAR-алгоритм.

```c
/* Сигнатури вбудованих функцій GCC та Clang */
int __builtin_popcount(unsigned int x);
int __builtin_popcountl(unsigned long x);
int __builtin_popcountll(unsigned long long x);

/* Пов'язані бітові операції */
int __builtin_parity(unsigned int x);
int __builtin_parityl(unsigned long x);
int __builtin_parityll(unsigned long long x);

int __builtin_clz(unsigned int x);      /* Count leading zeros: невизначена поведінка для x = 0 */
int __builtin_ctz(unsigned int x);      /* Count trailing zeros: невизначена поведінка для x = 0 */
int __builtin_ffs(int x);               /* Find first set: повертає індекс 1..32, або 0 для нуля */
```

#### Контракт та інваріанти GCC / Clang
- **Область визначення:** аргумент повинен бути беззнаковим цілим числом відповідного типу. Передача знакового від'ємного числа призводить до його неявного приведення до беззнакового типу відповідно до правил перетворення мови C (залишок за модулем `2ⁿ`).
- **Діапазон результату:** ціле число типу `int` у діапазоні від `0` до `sizeof(type) * 8`.
- **Поведінка для нуля:** на відміну від `__builtin_clz` та `__builtin_ctz`, для яких нульовий аргумент є суворою невизначеною поведінкою (Undefined Behavior), функція `__builtin_popcount(0)` гарантовано і детерміновано повертає `0`.
#### Розпізнавання шаблонів компіляторами (Idiom Recognition)
Сучасні оптимізуючі компілятори (LLVM Clang від версії 10, GCC від версії 9) оснащені модулями розпізнавання канонічних шаблонів бітових циклів. Якщо розробник записує класичний цикл Вегнера-Кернігана або наївний побітовий перебір:
```c
int count = 0;
while (x != 0) {
    x &= (x - 1);
    count++;
}
```
за наявності прапорця оптимізації `-O2` або `-O3` компілятор автоматично згортає весь цикл у єдину інструкцію `POPCNT` або відповідний інтринсик. Це усуває всі умовні переходи та непередбачувані затримки конвеєра. Проте для гарантованої швидкодії на будь-якому рівні оптимізації та запобігання деградації в налагоджувальних збірках (Debug) рекомендується завжди викликати явні інтринсики або стандартний `std::popcount`.

#### Безпека перетворення типів та поведінка зі знаковими числами
- **Знакові цілі числа:** операція побітового підрахунку одиниць визначена строго над двійковим бітовим представленням. Передача від'ємного числа у компіляторні інтринсики мови C призводить до його приведення до беззнакового еквівалента того самого розміру за модулем `2ⁿ`. Наприклад, для 32-бітного числа `-1` (двійковий запис `0xFFFFFFFF`) результат складе рівно `32`.
- **Розширення розрядності (Zero Extension vs Sign Extension):** під час передачі 8- або 16-бітних беззнакових типів (`uint8_t`, `uint16_t`) у 32-бітний інтринсик `__builtin_popcount` значення неявно розширюється нулями у старших розрядах (Zero Extension), що гарантує збереження правильної кількості одиниць. Якщо ж значення передається як знаковий `int8_t`, компілятор виконає знакове розширення (Sign Extension), заповнюючи старші 24 розряди одиницями для від'ємних чисел, що призведе до несподіваного завищення результату.

### Компілятор Microsoft Visual C++ (MSVC)

У компіляторі MSVC бітові інтринсики доступні через заголовок `<intrin.h>`.

```c
#include <intrin.h>

/* Скалярні інтринсики MSVC для архітектур x86 / x64 / ARM / ARM64 */
unsigned int __popcnt(unsigned int value);
unsigned short __popcnt16(unsigned short value);
unsigned __int64 __popcnt64(unsigned __int64 value);

/* Векторні інтринсики SSE4.2 */
unsigned int _mm_popcnt_u32(unsigned int a);
unsigned __int64 _mm_popcnt_u64(unsigned __int64 a);
```

#### Особливості розрядності MSVC на платформі Windows
В операційній системі Windows використовується модель даних LLP64, де тип `unsigned long` завжди має розмір 32 біти (на відміну від моделі LP64 в Unix/Linux, де `unsigned long` є 64-бітним). Тому для 64-бітних обчислень у MSVC необхідно обов'язково використовувати `__popcnt64` або `_mm_popcnt_u64` з типами `uint64_t` або `unsigned __int64`. Для активації інструкцій потрібен прапорець компіляції `/O2` та `/arch:AVX2` або `/arch:AVX512`.

---

## 3. Стандартна бібліотека C++20 (`<bit>`)

Починаючи зі стандарту C++20, операції побітового аналізу отримали уніфіковану платформонезалежну специфікацію в заголовку `<bit>`.

```cpp
#include <bit>

namespace std {
    template <typename T>
    [[nodiscard]] constexpr int popcount(T x) noexcept;

    template <typename T>
    [[nodiscard]] constexpr bool has_single_bit(T x) noexcept;

    template <typename T>
    [[nodiscard]] constexpr T bit_ceil(T x);

    template <typename T>
    [[nodiscard]] constexpr T bit_floor(T x) noexcept;

    template <typename T>
    [[nodiscard]] constexpr int bit_width(T x) noexcept;

    template <typename T>
    [[nodiscard]] constexpr int countl_zero(T x) noexcept;

    template <typename T>
    [[nodiscard]] constexpr int countr_zero(T x) noexcept;

    template <typename T>
    [[nodiscard]] constexpr int countl_one(T x) noexcept;

    template <typename T>
    [[nodiscard]] constexpr int countr_one(T x) noexcept;
}
```

### Специфікація контракту `std::popcount`

1. **Концепти та обмеження типів:**
   Функція обмежена концептом `std::unsigned_integral`. Тип `T` зобов'язаний бути одним зі стандартних беззнакових типів:
   - `unsigned char`, `unsigned short`, `unsigned int`, `unsigned long`, `unsigned long long`;
   - стандартні псевдоніми фіксованої ширини: `uint8_t`, `uint16_t`, `uint32_t`, `uint64_t`, `uintptr_t`, `size_t`.
2. **Заборона знакових типів:**
   Передача знакового цілого числа (`int`, `int64_t`) або типу з рухомою комою викликає помилку компіляції на етапі перевірки концепту. Таке рішення прийнято комітетом ISO C++, оскільки бітове представлення від'ємних чисел і знаковий розряд призводять до неоднозначностей і прихованих дефектів. Для обробки знакового значення його слід явно перетворити на беззнаковий аналог:
   ```cpp
   int x = -42;
   int ones = std::popcount(static_cast<std::make_unsigned_t<int>>(x));
   ```
3. **Обчислюваність на етапі компіляції (`constexpr`):**
   Функція `std::popcount` є повноцінно `constexpr`. Компілятор здатний згортати обчислення ваги Гемінга константних виразів під час трансляції програми без виконання інструкцій під час роботи.
4. **Гарантія безпеки винятків (`noexcept`):**
   Функція не виділяє пам'ять, не звертається до системних викликів і гарантовано не викидає жодних винятків (`noexcept(true)`).
5. **Атрибут `[[nodiscard]]`:**
   Компілятор видає попередження, якщо результат обчислення функції ігнорується, захищаючи розробника від випадкового виклику без збереження значення.

---

## 4. Специфікація примітивів позиціонування Rank та Select

Лаконічні структури даних (succinct data structures) будуються на двох взаємно обернених операціях над бітовими послідовностями: рангу (`rank`) та вибірці (`select`).

### Операція `rank`

Операція `rank1(B, i)` повертає кількість одиничних бітів у префіксі бітового масиву `B` від нульової позиції до індексу `i` включно:
`rank1(B, i) = popcount(B[0..i])`.

- **Математичний інваріант:** `0 <= rank1(B, i) <= i + 1`.
- **Монотонність:** для будь-яких `i1 <= i2` виконується `rank1(B, i1) <= rank1(B, i2)`.
- **Дуальна операція для нулів:** кількість нульових розрядів на тому самому префіксі обчислюється без окремого індексу за формулою:
  `rank0(B, i) = (i + 1) - rank1(B, i)`.

### Операція `select`

Операція `select1(B, k)` повертає позицію (індекс) `k`-ї одиниці у бітовому масиві `B` (де `k >= 1`):
`select1(B, k) = i`, таке що `rank1(B, i) = k` та `B[i] = 1`.

- **Контракт обробки помилок:**
  - Якщо `k == 0` (некоректний порядковий номер): функція повертає статус помилки або сигнальне значення `(size_t)-1`;
  - Якщо `k > popcount(B)` (у масиві менше одиниць, ніж запитано): функція повертає ознаку відсутності результату (`(size_t)-1` у C або `std::nullopt` у C++);
  - Якщо `k <= popcount(B)`: повертається коректний індекс у межах `[0..N-1]`.
- **Апаратне прискорення `select64` інструкцією `PDEP`:**
  На процесорах із підтримкою набору інструкцій BMI2 (Bit Manipulation Instruction Set 2) вибірка `k`-ї одиниці в межах одного 64-бітного слова виконується за сталий час за допомогою паралельного розкидання бітів:
  ```c
  #include <immintrin.h>

  /* Знаходження позиції k-ї одиниці (1 <= k <= popcount(x)) у 64-бітному слові */
  static inline uint32_t select64_bmi2(uint64_t x, unsigned int k) {
      uint64_t mask = 1ULL << (k - 1);
      uint64_t deposited = _pdep_u64(mask, x);
      return (uint32_t)_tzcnt_u64(deposited);
  }
  ```

---

## 5. Підтримка в екосистемах інших мов програмування

### Мова Rust (`core::primitive` / `std::primitive`)

У мові Rust операції побітового аналізу є методами примітивних цілочисельних типів `u8`, `u16`, `u32`, `u64`, `u128`, `usize`:

```rust
// Сигнатури базових методів
pub const fn count_ones(self) -> u32;
pub const fn count_zeros(self) -> u32;
pub const fn leading_zeros(self) -> u32;
pub const fn trailing_zeros(self) -> u32;

// Приклад використання в середовищі no_std
let mask: u64 = 0b1011_0000_1111;
let weight: u32 = mask.count_ones(); // Повертає 8
let parity: bool = (weight % 2) != 0;
```
- **Особливості:** методи доступні у режимі `#![no_std]` і є повноцінними константними функціями (`const fn`). За наявності прапорця `-C target-cpu=native` компілятор `rustc` (на базі LLVM) генерує безпосередню інструкцію `POPCNT` або `CNT`.

### Мова Go (`math/bits`)

Стандартний пакет `math/bits` містить оптимізовані функції з прямою асемблерною підтримкою:

```go
package bits

func OnesCount(x uint) int
func OnesCount32(x uint32) int
func OnesCount64(x uint64) int
func RotateLeft64(x uint64, k int) uint64
func ReverseBytes64(x uint64) uint64
```
- **JIT/AOT-трансляція:** компілятор Go розпізнає виклики функцій пакета `math/bits` як апаратні інтринсики і транслює їх у машинні інструкції цільової архітектури без накладних витрат на виклик процедури.

### Платформа Java (`java.lang.Integer`, `java.lang.Long`)

У віртуальній машині Java методи реалізовані як статичні методи класів-обгорток:

```java
public static int bitCount(int i);
public static int bitCount(long i);
public static int numberOfLeadingZeros(long i);
public static int numberOfTrailingZeros(long i);
```
- **Анотація `@IntrinsicCandidate`:** починаючи з Java 9, JIT-компілятори C1 і C2 анотують `bitCount` як цільовий інтринсик і замінюють його машинною командою `POPCNT` під час формування нативного коду.

### Платформа .NET / C# (`System.Numerics.BitOperations`)

У сучасному середовищі .NET (версії .NET Core 3.1, .NET 6, 7, 8, 9) операції зібрані у статичному класі `BitOperations`:

```csharp
using System.Numerics;

public static int PopCount(uint value);
public static int PopCount(ulong value);
public static int PopCount(nuint value);
public static bool IsPow2(ulong value);
```
- **Апаратне прискорення:** JIT-компілятор RyuJIT автоматично інлайнить ці виклики в інструкції `POPCNT` або векторні еквіваленти для ARM64.

---

## 6. Еталонна реалізація портативної бібліотеки бітових операцій

Нижче наведено промислову переносиму реалізацію модулів бітових операцій мовами C та C++20, що включає інваріанти, виявлення можливостей архітектури та перевірку кодів помилок.

:::tabs
```c
/* bit_ops.h — Переносима бібліотека бітових операцій мовою C */
#ifndef BIT_OPS_H
#define BIT_OPS_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#if defined(_MSC_VER)
#  include <intrin.h>
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* Статусні коди операцій вибірки та пошуку */
typedef enum {
    BIT_SUCCESS = 0,
    BIT_ERR_OUT_OF_RANGE = 1,
    BIT_ERR_NOT_FOUND = 2,
    BIT_ERR_INVALID_ARGUMENT = 3
} bit_status_t;

/* Обчислення ваги Гемінга (popcount) для 32-бітного слова */
static inline uint32_t bit_popcount32(uint32_t x) {
#if defined(__GNUC__) || defined(__clang__)
    return (uint32_t)__builtin_popcount(x);
#elif defined(_MSC_VER)
    return __popcnt(x);
#else
    /* Портативний безрозгалужений SWAR-алгоритм */
    x = x - ((x >> 1) & 0x55555555U);
    x = (x & 0x33333333U) + ((x >> 2) & 0x33333333U);
    x = (x + (x >> 4)) & 0x0F0F0F0FU;
    return (x * 0x01010101U) >> 24;
#endif
}

/* Обчислення ваги Гемінга (popcount) для 64-бітного слова */
static inline uint32_t bit_popcount64(uint64_t x) {
#if defined(__GNUC__) || defined(__clang__)
    return (uint32_t)__builtin_popcountll(x);
#elif defined(_MSC_VER) && defined(_M_X64)
    return (uint32_t)__popcnt64(x);
#elif defined(_MSC_VER)
    return __popcnt((uint32_t)x) + __popcnt((uint32_t)(x >> 32));
#else
    /* Портативний SWAR для 64-бітних слів */
    x = x - ((x >> 1) & 0x5555555555555555ULL);
    x = (x & 0x3333333333333333ULL) + ((x >> 2) & 0x3333333333333333ULL);
    x = (x + (x >> 4)) & 0x0F0F0F0F0F0F0F0FULL;
    return (uint32_t)((x * 0x0101010101010101ULL) >> 56);
#endif
}

/* Обчислення парності (1, якщо кількість одиниць непарна, 0 — якщо парна) */
static inline uint32_t bit_parity64(uint64_t x) {
#if defined(__GNUC__) || defined(__clang__)
    return (uint32_t)__builtin_parityll(x);
#else
    x ^= x >> 32;
    x ^= x >> 16;
    x ^= x >> 8;
    x ^= x >> 4;
    x ^= x >> 2;
    x ^= x >> 1;
    return (uint32_t)(x & 1ULL);
#endif
}

/* Обчислення рангу одиниць у 64-бітному слові на префіксі [0..bit_idx] */
static inline bit_status_t bit_rank64(uint64_t word, uint32_t bit_idx, uint32_t* out_rank) {
    if (!out_rank) return BIT_ERR_INVALID_ARGUMENT;
    if (bit_idx >= 64) {
        *out_rank = 0;
        return BIT_ERR_OUT_OF_RANGE;
    }
    uint64_t mask = (bit_idx == 63) ? ~0ULL : ((1ULL << (bit_idx + 1)) - 1ULL);
    *out_rank = bit_popcount64(word & mask);
    return BIT_SUCCESS;
}

/* Пошук позиції k-ї одиниці (1 <= k <= 64) у 64-бітному слові */
static inline bit_status_t bit_select64(uint64_t word, uint32_t k, uint32_t* out_pos) {
    if (!out_pos || k == 0 || k > 64) return BIT_ERR_INVALID_ARGUMENT;
    uint32_t total = bit_popcount64(word);
    if (k > total) {
        *out_pos = 0xFFFFFFFFU;
        return BIT_ERR_NOT_FOUND;
    }

    /* Двійковий пошук позиції k-ї одиниці за допомогою popcount */
    uint32_t low = 0, high = 63, result = 63;
    while (low <= high) {
        uint32_t mid = low + (high - low) / 2;
        uint64_t mask = (mid == 63) ? ~0ULL : ((1ULL << (mid + 1)) - 1ULL);
        if (bit_popcount64(word & mask) >= k) {
            result = mid;
            if (mid == 0) break;
            high = mid - 1;
        } else {
            low = mid + 1;
        }
    }
    *out_pos = result;
    return BIT_SUCCESS;
}

#ifdef __cplusplus
}
#endif

#endif /* BIT_OPS_H */
```
```cpp
/* bit_ops.hpp — Ідіоматична бібліотека бітових операцій мовою C++20 */
#pragma once

#include <bit>
#include <concepts>
#include <cstdint>
#include <cstddef>
#include <optional>
#include <expected>
#include <string_view>

namespace bitops {

enum class BitError {
    OutOfRange,
    NotFound,
    InvalidArgument
};

/* Концепт для суворо беззнакових цілих типів */
template <typename T>
concept UnsignedWord = std::unsigned_integral<T>;

/* Обчислення ваги Гемінга (кількості одиниць) для довільного беззнакового типу */
template <UnsignedWord T>
[[nodiscard]] constexpr int popcount(T value) noexcept {
    return std::popcount(value);
}

/* Обчислення парності (true — непарна кількість одиниць, false — парна) */
template <UnsignedWord T>
[[nodiscard]] constexpr bool parity(T value) noexcept {
    return (std::popcount(value) & 1) != 0;
}

/* Обчислення рангу одиниць у слові на діапазоні розрядів [0..bit_idx] */
template <UnsignedWord T>
[[nodiscard]] constexpr std::expected<size_t, BitError> rank1(T word, size_t bit_idx) noexcept {
    constexpr size_t total_bits = sizeof(T) * 8;
    if (bit_idx >= total_bits) {
        return std::unexpected(BitError::OutOfRange);
    }
    const T mask = (bit_idx == total_bits - 1) 
        ? static_cast<T>(~static_cast<T>(0)) 
        : static_cast<T>((static_cast<T>(1) << (bit_idx + 1)) - static_cast<T>(1));
    return static_cast<size_t>(std::popcount(static_cast<T>(word & mask)));
}

/* Дуальний ранг нулів */
template <UnsignedWord T>
[[nodiscard]] constexpr std::expected<size_t, BitError> rank0(T word, size_t bit_idx) noexcept {
    auto r1 = rank1(word, bit_idx);
    if (!r1) return std::unexpected(r1.error());
    return (bit_idx + 1) - *r1;
}

/* Пошук позиції k-ї одиниці (1-індексація для k) */
template <UnsignedWord T>
[[nodiscard]] constexpr std::expected<size_t, BitError> select1(T word, size_t k) noexcept {
    constexpr size_t total_bits = sizeof(T) * 8;
    if (k == 0 || k > total_bits) {
        return std::unexpected(BitError::InvalidArgument);
    }
    if (static_cast<size_t>(std::popcount(word)) < k) {
        return std::unexpected(BitError::NotFound);
    }

    size_t low = 0;
    size_t high = total_bits - 1;
    size_t result = total_bits - 1;

    while (low <= high) {
        size_t mid = low + (high - low) / 2;
        const T mask = (mid == total_bits - 1)
            ? static_cast<T>(~static_cast<T>(0))
            : static_cast<T>((static_cast<T>(1) << (mid + 1)) - static_cast<T>(1));

        if (static_cast<size_t>(std::popcount(static_cast<T>(word & mask))) >= k) {
            result = mid;
            if (mid == 0) break;
            high = mid - 1;
        } else {
            low = mid + 1;
        }
    }
    return result;
}

} // namespace bitops
```
:::

---

## 7. Зведена таблиця сумісності, діагностики та прапорців компіляції

| Платформа / Мова | Скалярна інструкція | Векторний аналог | Прапорці оптимізації | Підтримка constexpr | Гарантія нульового аргументу |
|---|---|---|---|---|---|
| **C++20 (`<bit>`)** | `POPCNT` | `VPOPCNTDQ` / `CNT` | `-O2 -march=native` | Так (`constexpr`) | Детерміновано `0` |
| **C (GCC / Clang)** | `__builtin_popcountll` | Автовекторизація | `-O3 -mpopcnt -mbitalg` | Так (розширення GNU) | Детерміновано `0` |
| **C (MSVC x64)** | `__popcnt64` | `_mm512_popcnt_epi64` | `/O2 /arch:AVX2` | Ні (runtime intrinsic) | Детерміновано `0` |
| **Rust (`core`)** | `u64::count_ones` | `std::simd` | `-C target-cpu=native` | Так (`const fn`) | Детерміновано `0` |
| **Go (`math/bits`)** | `bits.OnesCount64` | Вбудований асемблер | За замовчуванням у go build | Ні (компіляторний інтринсик) | Детерміновано `0` |
| **Java 21+** | `Long.bitCount` | Vector API (`IntVector`) | HotSpot JIT (C2 Compiler) | Так (JIT intrinsic) | Детерміновано `0` |
| **.NET 8/9 C#** | `BitOperations.PopCount` | `Vector256.Count` | RyuJIT Release | Так (JIT intrinsic) | Детерміновано `0` |
| **CUDA PTX** | `popc.b64` | SIMD Video instructions | `nvcc -O3 -arch=sm_80` | Так (device constexpr) | Детерміновано `0` |

