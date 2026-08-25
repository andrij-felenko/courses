# ⚙️ Реалізація динамічних значень: NaN-boxing та теговані покажчики на C та C++

У класичних інтерпретаторах (як-от CPython) кожне динамічне значення є повноцінним об'єктом у купі. Навіть для зберігання звичайного числа `42` виділяється структура `PyObject` розміром 24–32 байти (8 байтів лічильника посилань, 8 байтів покажчика на тип, 8 байтів значення). При виконанні мільйонів операцій це призводить до катастрофічного навантаження на диспетчер пам'яті (malloc/free) та постійних промахів кешу процесора L1/L2.

Щоб усунути ці витрати, сучасні високопродуктивні віртуальні машини (JavaScriptCore у WebKit, SpiderMonkey у Firefox, LuaJIT) використовують техніку **NaN-boxing** (або *NaN-tagging*). Цей підхід упаковує будь-яке динамічне значення (дійсне число, 32-бітне ціле, булевий прапорець, значення `null` або 48-бітний покажчик на купу) у єдине 64-бітне машинне слово (8 байтів) без жодних додаткових алокацій у динамічній пам'яті.

## Анатомія стандарту IEEE 754 та резервні біти

Стандарт чисел з плаваючою комою подвійної точності (IEEE 754 `double`) займає 64 біти:
- 1 біт знака (`s`);
- 11 бітів експоненти (`e`);
- 52 біти мантиси (`m`).

```
64-бітний формат IEEE 754 Double:
 1 біт    11 бітів                        52 біти
┌───┬───────────┬────────────────────────────────────────────────────────┐
│ s │ eeeeeeeee │ mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm │
└───┴───────────┴────────────────────────────────────────────────────────┘
```

Значення вважається **NaN** (Not a Number — «не число»), якщо всі 11 бітів експоненти встановлені в `1` (`0x7FF`), а мантиса не дорівнює нулю. Стандарт розрізняє два види NaN:
1. **Сигнальний NaN (Signaling NaN, SNaN):** старший біт мантиси дорівнює `0` (при ненульових інших бітах). Використання SNaN в арифметичних інструкціях процесора викликає апаратне переривання FPU (Invalid Operation Exception).
2. **Тихий NaN (Quiet NaN, QNaN):** старший біт мантиси дорівнює `1` (маска `0x7FF8_0000_0000_0000`). Такі значення вільно проходять крізь обчислення FPU без виклику винятків, сигналізуючи про невизначений результат (як-от `0.0 / 0.0` або `sqrt(-1.0)`).

Решта 51 біт мантиси у Quiet NaN процесором взагалі не використовуються і є вільним корисним навантаженням (англ. *payload*). 

На сучасних 64-бітних архітектурах x86-64 та ARM64 віртуальний адресний простір обмежений 48 бітами при 4-рівневій трансляції сторінок (PML4) або 57 бітами при 5-рівневій (PML5). У просторі користувача канонічні віртуальні адреси завжди лежать у нижньому діапазоні від `0x0000_0000_0000_0000` до `0x0000_7FFF_FFFF_FFFF`. Це означає, що 16 старших бітів будь-якого вказівника на об'єкт у купі гарантовано дорівнюють нулю, і адреса повністю вміщується у молодші 48 бітів.

Це відкриває можливість закодувати всю систему динамічних типів у межах одного 64-бітного слова:
1. Якщо бітова комбінація не містить префікса Quiet NaN — це справжній `double`, який процесор обробляє стандартними інструкціями FPU/SSE/AVX без жодних додаткових дій.
2. Якщо значення містить маску Quiet NaN — старші 16 бітів визначають тег типу (покажчик на купу, 32-бітне ціле число, булевий тип, null або undefined), а молодші 48 бітів містять корисні дані.

```
Структура значення при NaN-Boxing:
1. Звичайний double (будь-яке дійсне число):
   [ s | eeeeeeeee (≠ 0x7FF) | mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm ]

2. Закодований тип (Quiet NaN префікс):
   [ 1 | 11111111111 | 1 | Tag (3 біти) | Payload / Pointer (48 бітів)   ]
   └───────────────┬─┘   └──────┬─────┘   └──────────────┬───────────────┘
     0x7FF8 (QNaN)         Тип даних        Адреса в RAM або Int32
```

## Крайові випадки: канонізація дійсних NaN та адреси пам'яті

При практичній реалізації NaN-boxing виникають два критичні крайові випадки, про які повинен пам'ятати розробник віртуальної машини:

1. **Колізія зі справжніми обчислювальними NaN:** Якщо користувацька програма виконує операцію `0.0 / 0.0`, апаратний блок FPU поверне апаратний Quiet NaN. Якщо випадково біти його мантиси співпадуть із нашим службовим тегом (наприклад, `TAG_INT` чи `TAG_POINTER`), віртуальна машина помилково інтерпретує дійсне число як об'єктний покажчик, що призведе до падіння процесу (Segmentation Fault).  
   *Рішення:* Під час створення значення з дійсного числа (`val_from_double`) виконується **канонізація NaN** (англ. *NaN canonicalization*): якщо вхідне число є `isnan(x)`, його бітове представлення примусово замінюється на єдиний стандартний канонічний Quiet NaN, який не перетинається з діапазоном службових тегів.
2. **Розширення покажчиків та ARM64 Top-Byte-Ignore (TBI):** На деяких платформах ARM64 увімкнено апаратну функцію TBI, яка дозволяє ядру ігнорувати старші 8 бітів покажчика. При передачі адреси з `NanBoxedValue` до системних викликів або сторонніх бібліотек C (FFI) необхідно гарантувати коректне очищення маски тегу перед розіменуванням пам'яті.

## Практична реалізація: пакування, розпакування та диспетчеризація

Нижче наведено повноцінну реалізацію системи динамічних значень на мовах C та C++ з підтримкою дійсних чисел, цілих чисел, булевих прапорців, null та об'єктних покажчиків.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

/* Базова маска Quiet NaN для 64-бітного слова */
#define QNAN_MASK     ((uint64_t)0x7FF8000000000000ULL)
#define TAG_MASK      ((uint64_t)0x0007000000000000ULL)
#define PAYLOAD_MASK  ((uint64_t)0x0000FFFFFFFFFFFFULL)

/* Теги для типів, що зберігаються всередині NaN */
#define TAG_POINTER   ((uint64_t)0x0001000000000000ULL)
#define TAG_INT       ((uint64_t)0x0002000000000000ULL)
#define TAG_BOOL      ((uint64_t)0x0003000000000000ULL)
#define TAG_NULL      ((uint64_t)0x0004000000000000ULL)

/* Канонічний NaN для представлення дійсного Not-a-Number */
#define CANONICAL_NAN ((uint64_t)0x7FF8000000000000ULL)

typedef uint64_t DynValue;

/* Конструктори значень */
static inline DynValue val_from_double(double num) {
    if (isnan(num)) {
        return CANONICAL_NAN;
    }
    DynValue v;
    memcpy(&v, &num, sizeof(double));
    return v;
}

static inline DynValue val_from_int(int32_t num) {
    return QNAN_MASK | TAG_INT | ((uint64_t)(uint32_t)num);
}

static inline DynValue val_from_bool(bool b) {
    return QNAN_MASK | TAG_BOOL | (b ? 1ULL : 0ULL);
}

static inline DynValue val_from_ptr(void *ptr) {
    return QNAN_MASK | TAG_POINTER | (((uint64_t)ptr) & PAYLOAD_MASK);
}

static inline DynValue val_null(void) {
    return QNAN_MASK | TAG_NULL;
}

/* Предикати перевірки типів */
static inline bool val_is_double(DynValue v) {
    return (v & QNAN_MASK) != QNAN_MASK;
}

static inline bool val_is_int(DynValue v) {
    return (v & (QNAN_MASK | TAG_MASK)) == (QNAN_MASK | TAG_INT);
}

static inline bool val_is_bool(DynValue v) {
    return (v & (QNAN_MASK | TAG_MASK)) == (QNAN_MASK | TAG_BOOL);
}

static inline bool val_is_ptr(DynValue v) {
    return (v & (QNAN_MASK | TAG_MASK)) == (QNAN_MASK | TAG_POINTER);
}

static inline bool val_is_null(DynValue v) {
    return (v & (QNAN_MASK | TAG_MASK)) == (QNAN_MASK | TAG_NULL);
}

/* Розпакування значень */
static inline double val_as_double(DynValue v) {
    double d;
    memcpy(&d, &v, sizeof(double));
    return d;
}

static inline int32_t val_as_int(DynValue v) {
    return (int32_t)(uint32_t)(v & 0xFFFFFFFFULL);
}

static inline bool val_as_bool(DynValue v) {
    return (v & 1ULL) != 0;
}

static inline void* val_as_ptr(DynValue v) {
    return (void*)(uintptr_t)(v & PAYLOAD_MASK);
}

/* Динамічна операція додавання з перевіркою тегів під час виконання */
DynValue dynamic_add(DynValue a, DynValue b, bool *type_error) {
    *type_error = false;

    /* Швидкий шлях: обидва операнди є цілими числами */
    if (val_is_int(a) && val_is_int(b)) {
        return val_from_int(val_as_int(a) + val_as_int(b));
    }

    /* Додавання дійсних чисел (з автоконверсією int -> double) */
    if ((val_is_double(a) || val_is_int(a)) && (val_is_double(b) || val_is_int(b))) {
        double da = val_is_double(a) ? val_as_double(a) : (double)val_as_int(a);
        double db = val_is_double(b) ? val_as_double(b) : (double)val_as_int(b);
        return val_from_double(da + db);
    }

    /* Помилка типізації під час виконання */
    *type_error = true;
    return val_null();
}

int main(void) {
    DynValue v1 = val_from_int(40);
    DynValue v2 = val_from_int(2);
    DynValue v3 = val_from_double(3.14159);
    DynValue v_str_dummy = val_from_ptr((void*)0x7FFF0010);

    bool err = false;
    DynValue res_int = dynamic_add(v1, v2, &err);
    if (!err) {
        printf("Int + Int = %d\n", val_as_int(res_int));
    }

    DynValue res_mixed = dynamic_add(v1, v3, &err);
    if (!err) {
        printf("Int + Double = %f\n", val_as_double(res_mixed));
    }

    DynValue res_invalid = dynamic_add(v1, v_str_dummy, &err);
    if (err) {
        printf("TypeError: несумісні типи операндів під час виконання!\n");
    }

    printf("Розмір DynValue у пам'яті: %zu байтів\n", sizeof(DynValue));
    return 0;
}
```
```cpp
#include <iostream>
#include <cstdint>
#include <bit>
#include <cmath>
#include <string>
#include <string_view>
#include <memory>
#include <expected>
#include <optional>
#include <variant>

enum class TypeKind : uint8_t {
    Double,
    Int32,
    Bool,
    Pointer,
    Null
};

class NanBoxedValue {
private:
    static constexpr uint64_t QNAN_MASK     = 0x7FF8'0000'0000'0000ULL;
    static constexpr uint64_t TAG_MASK      = 0x0007'0000'0000'0000ULL;
    static constexpr uint64_t PAYLOAD_MASK  = 0x0000'FFFF'FFFF'FFFFULL;

    static constexpr uint64_t TAG_POINTER   = 0x0001'0000'0000'0000ULL;
    static constexpr uint64_t TAG_INT       = 0x0002'0000'0000'0000ULL;
    static constexpr uint64_t TAG_BOOL      = 0x0003'0000'0000'0000ULL;
    static constexpr uint64_t TAG_NULL      = 0x0004'0000'0000'0000ULL;
    static constexpr uint64_t CANONICAL_NAN = 0x7FF8'0000'0000'0000ULL;

    uint64_t raw_bits_{QNAN_MASK | TAG_NULL};

    explicit constexpr NanBoxedValue(uint64_t raw) noexcept : raw_bits_(raw) {}

public:
    constexpr NanBoxedValue() noexcept = default;

    static NanBoxedValue from_double(double v) noexcept {
        if (std::isnan(v)) {
            return NanBoxedValue(CANONICAL_NAN);
        }
        return NanBoxedValue(std::bit_cast<uint64_t>(v));
    }

    static constexpr NanBoxedValue from_int(int32_t v) noexcept {
        return NanBoxedValue(QNAN_MASK | TAG_INT | static_cast<uint64_t>(static_cast<uint32_t>(v)));
    }

    static constexpr NanBoxedValue from_bool(bool b) noexcept {
        return NanBoxedValue(QNAN_MASK | TAG_BOOL | (b ? 1ULL : 0ULL));
    }

    static NanBoxedValue from_ptr(const void* ptr) noexcept {
        auto addr = reinterpret_cast<uintptr_t>(ptr);
        return NanBoxedValue(QNAN_MASK | TAG_POINTER | (addr & PAYLOAD_MASK));
    }

    static constexpr NanBoxedValue make_null() noexcept {
        return NanBoxedValue(QNAN_MASK | TAG_NULL);
    }

    [[nodiscard]] constexpr TypeKind kind() const noexcept {
        if ((raw_bits_ & QNAN_MASK) != QNAN_MASK) return TypeKind::Double;
        switch (raw_bits_ & (QNAN_MASK | TAG_MASK)) {
            case QNAN_MASK | TAG_INT:     return TypeKind::Int32;
            case QNAN_MASK | TAG_BOOL:    return TypeKind::Bool;
            case QNAN_MASK | TAG_POINTER: return TypeKind::Pointer;
            default:                      return TypeKind::Null;
        }
    }

    [[nodiscard]] constexpr bool is_double() const noexcept { return kind() == TypeKind::Double; }
    [[nodiscard]] constexpr bool is_int() const noexcept    { return kind() == TypeKind::Int32; }
    [[nodiscard]] constexpr bool is_bool() const noexcept   { return kind() == TypeKind::Bool; }
    [[nodiscard]] constexpr bool is_ptr() const noexcept    { return kind() == TypeKind::Pointer; }
    [[nodiscard]] constexpr bool is_null() const noexcept   { return kind() == TypeKind::Null; }

    [[nodiscard]] double as_double() const noexcept {
        return std::bit_cast<double>(raw_bits_);
    }

    [[nodiscard]] constexpr int32_t as_int() const noexcept {
        return static_cast<int32_t>(static_cast<uint32_t>(raw_bits_ & 0xFFFF'FFFFULL));
    }

    [[nodiscard]] constexpr bool as_bool() const noexcept {
        return (raw_bits_ & 1ULL) != 0;
    }

    [[nodiscard]] void* as_ptr() const noexcept {
        return reinterpret_cast<void*>(static_cast<uintptr_t>(raw_bits_ & PAYLOAD_MASK));
    }
};

/* Динамічна арифметика з ідіоматичним std::expected для обробки помилок */
struct TypeError {
    std::string message;
};

std::expected<NanBoxedValue, TypeError> add_dynamic(NanBoxedValue a, NanBoxedValue b) {
    if (a.is_int() && b.is_int()) {
        return NanBoxedValue::from_int(a.as_int() + b.as_int());
    }

    if ((a.is_double() || a.is_int()) && (b.is_double() || b.is_int())) {
        double da = a.is_double() ? a.as_double() : static_cast<double>(a.as_int());
        double db = b.is_double() ? b.as_double() : static_cast<double>(b.as_int());
        return NanBoxedValue::from_double(da + db);
    }

    return std::unexpected(TypeError{"TypeError: неможливо виконати операцію над несумісними типами"});
}

int main() {
    auto v1 = NanBoxedValue::from_int(40);
    auto v2 = NanBoxedValue::from_int(2);
    auto v3 = NanBoxedValue::from_double(3.14159);
    auto v_null = NanBoxedValue::make_null();

    if (auto res = add_dynamic(v1, v2); res) {
        std::cout << "Int + Int = " << res->as_int() << '\n';
    }

    if (auto res = add_dynamic(v1, v3); res) {
        std::cout << "Int + Double = " << res->as_double() << '\n';
    }

    if (auto res = add_dynamic(v1, v_null); !res) {
        std::cout << res.error().message << '\n';
    }

    std::cout << "Розмір NanBoxedValue: " << sizeof(NanBoxedValue) << " байтів\n";
    std::cout << "Розмір std::variant<double, int, bool, void*>: " 
              << sizeof(std::variant<double, int32_t, bool, void*>) << " байтів\n";
    return 0;
}
```
:::

## Взаємодія з JIT-компіляторами та спекулятивне розпакування

Сучасні JIT-компілятори (як-от TurboFan у V8 або FTL у JavaScriptCore) використовують представлення NaN-boxing для **спекулятивного розпакування** (англ. *speculative unboxing*).

Коли профайлер віртуальної машини фіксує, що функція в циклі оперує виключно цілими числами або дійсними числами, JIT-компілятор генерує спеціалізований машинний код:
1. На вході в цикл виконується єдина перевірка форми та тегів аргументів (англ. *type guard*).
2. Тіло циклу компілюється в прямі інструкції процесора без жодних тегів (`ADDSD`, `MULSD`, `ADD EAX, EDX`), зберігаючи чисті значення у регістрах SSE/AVX.
3. Якщо на черговій ітерації виникає невідповідність типу (наприклад, у масив чисел потрапив рядок), спрацьовує перехід на **деоптимізацію (Deoptimization Bailout)**: JIT скидає скомпільований блок, запаковує поточні регістри назад у `NanBoxedValue` і повертає керування інтерпретатору.

## Порівняння продуктивності: `NanBoxedValue` проти `std::variant`

У стандартній бібліотеці C++ для збереження закритого набору динамічних типів використовується шаблон `std::variant`. Проте через вимоги стандарту щодо роздільного збереження дискримінанта типу та вирівнювання полів розмір `std::variant<double, int, bool, void*>` на 64-бітній системі складає **16 байтів** (8 байтів під найбільше значення + 8 байтів під дискримінант індексу з вирівнюванням).

Порівняння архітектурних характеристик двох підходів:

| Властивість | NaN-Boxing (`NanBoxedValue`) | `std::variant<...>` |
| :--- | :--- | :--- |
| **Розмір структури** | **8 байтів** (1 машинне слово) | **16 байтів** (2 машинних слова) |
| **Елементів у лінії кешу L1 (64B)** | **8 значень** (максимальна щільність) | **4 значення** (50% простір на вирівнювання) |
| **Передача через регістри ABI** | 1 регістр (`%rdi` або `%xmm0`) | 2 регістри або через стек |
| **Швидкість читання `double`** | **0 тактів** (пряме читання без розпакування) | 2–4 такти (перевірка дискримінанта + зсув) |
| **Підтримка типів** | Числа, bool, null, 48-бітні покажчики | Довільні структури C++ з конструкторами |

NaN-boxing демонструє, як низькорівневе знання формату процесорних інструкцій та архітектури віртуальної пам'яті дозволяє реалізувати динамічну типізацію з мінімальними накладними витратами, наближаючись до швидкодії статично скомпільованого коду.
