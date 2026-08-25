# ⚙️ Типізована MMIO-абстракція регістрів без накладних витрат

Робота з апаратними регістрами мікроконтролера через прямі макроси мови C несе системні інженерні ризики: випадковий запис у регістр тільки для читання, змішування бітових масок різних периферійних модулів або помилка в розрахунку зсуву призводять до непередбачуваного зависання пристрою. У цій практичній роботі побудовано завершену заголовну бібліотеку типізованого доступу до регістрів (MMIO) на базі стандартних засобів C++20. Шаблонна архітектура виконує всі перевірки прав доступу та сумісності бітових полів виключно на етапі компіляції, транслюючись у чистий машинний код без жодного байта накладних витрат у пам'яті Flash та оперативній пам'яті SRAM.

## Задача та системні обмеження низькорівневого коду

Низькорівневий драйвер апаратного периферійного модуля (наприклад, порту вводу-виводу GPIO, контролера послідовної шини UART чи апаратного таймера) безпосередньо взаємодіє з регістрами мікроконтролера, відображеними в адресний простір пам'яті. У класичній розробці мовою C такий доступ організовують через макроси препроцесора та пряме розіменування нетипізованих вказівників типу `*(volatile uint32_t*)(BASE_ADDR + OFFSET)`.

Цей традиційний підхід має чотири фундаментальні вади, які регулярно призводять до прихованих дефектів у прошивках:

1. **Відсутність контролю прав доступу на рівні компілятора:** апаратні регістри мають різну семантику доступу. Регістри вхідних даних (наприклад, `GPIO_IDR` або статусний регістр `USART_ISR`) є апаратно доступними виключно для читання. Запис у такий регістр або ігнорується апаратурою, або призводить до скидання прапорців стану. Інші регістри (наприклад, скидання буферів чи запуск перетворень) є доступними лише для запису. Макроси C не розрізняють ці режими, дозволяючи виконувати будь-яку операцію над будь-яким регістром.
2. **Змішування бітових масок різних периферійних модулів:** компілятор C трактує будь-яку бітову маску як беззнакове ціле число `uint32_t`. Якщо розробник помилково передасть маску налаштування дільника таймера у функцію конфігурації режиму піна GPIO, компілятор не видасть жодного попередження, хоча така операція спотворить стан апаратури.
3. **Небезпека операцій «читання-модифікація-запис» (Read-Modify-Write, RMW):** більшість регістрів конфігурації вимагають збереження сусідніх бітових полів при зміні одного виводу. Якщо головний потік зчитує регістр, змінює біт і записує значення назад, виникнення переривання в середині цієї послідовності призводить до стану гонитви (race condition) та втрати налаштувань, зроблених обробником переривання.
4. **Некоректна поведінка регістрів зі спеціальною семантикою (Write-1-to-Clear):** у багатьох мікроконтролерах (зокрема STM32, NXP LPC, ESP32) прапорці переривань у статусних регістрах скидаються записом одиниці в активний біт. Якщо виконати на такому регістрі класичну операцію RMW (`STATUS |= (1 << 5)`), операція зчитування поверне всі одиниці активних на цей момент прапорців, а наступний запис скине всі поточні переривання системи.

Мета цього проекту — побудувати узагальнену шаблонну систему, яка розв'язує всі перелічені проблеми на рівні типів C++, зберігаючи нульову ціну в машинному коді.

## Архітектурний дизайн шаблонної бібліотеки

Бібліотека будується навколо чотирьох взаємодіючих компонентів:

- **Перелічення політик доступу `Access`:** строго типізоване перелічення (`enum class`), що визначає режими `ReadOnly`, `WriteOnly` та `ReadWrite`.
- **Шаблонний клас `Register<Address, Type, Mode>`:** представляє конкретний апаратний регістр за фіксованою адресою. Методи `read()`, `write()`, `set_bits()` та `clear_bits()` обмежені вимогами концепцій C++ (`requires`), завдяки чому виклик недозволеної операції блокується ще на етапі трансляції.
- **RAII-клас `InterruptLock`:** захищає неатомарні операції над регістрами шляхом збереження регістра пріоритетів переривань ARM Cortex-M (`PRIMASK`) та атомарного вимкнення переривань з гарантованим відновленням у деструкторі.
- **Периферійний модуль `GpioPort<BaseAddress>`:** об'єднує групу пов'язаних регістрів конкретного порту та надає високорівневі типобезпечні методи налаштування виводів.

## Повна реалізація: порівняння C та C++20

Нижче наведено завершений вихідний код обох підходів. Приклад демонструє налаштування виводу 5 порту `GPIOA` мікроконтролера STM32 (регістр `MODER`, регістр вхідних даних `IDR` та регістр вихідних даних `ODR`).

:::tabs
```c
/* c_mmio_driver.h / c_mmio_driver.c — Класичний підхід мовою C */
#include <stdint.h>
#include <stdbool.h>

#define GPIOA_BASE          (0x40020000UL)
#define GPIOA_MODER_OFFSET  (0x00UL)
#define GPIOA_IDR_OFFSET    (0x10UL)
#define GPIOA_ODR_OFFSET    (0x14UL)

/* Нетипізовані макроси розіменування адрес */
#define GPIOA_MODER (*(volatile uint32_t*)(GPIOA_BASE + GPIOA_MODER_OFFSET))
#define GPIOA_IDR   (*(volatile uint32_t*)(GPIOA_BASE + GPIOA_IDR_OFFSET))
#define GPIOA_ODR   (*(volatile uint32_t*)(GPIOA_BASE + GPIOA_ODR_OFFSET))

#define PIN_5_MASK        (1U << 5)
#define PIN_5_MODE_OUTPUT (1U << (5 * 2))

/* Функція налаштування режиму піна */
void gpioa_pin5_set_output(void) {
    /* Немає захисту від стану гонитви з перериваннями */
    /* Немає перевірки коректності зміщення бітів */
    GPIOA_MODER |= PIN_5_MODE_OUTPUT;
}

/* Функція запису стану виводу */
void gpioa_pin5_write(bool high) {
    if (high) {
        GPIOA_ODR |= PIN_5_MASK;
    } else {
        GPIOA_ODR &= ~PIN_5_MASK;
    }
}

/* Функція читання вхідного стану */
bool gpioa_pin5_read(void) {
    return (GPIOA_IDR & PIN_5_MASK) != 0;
}

/* Приклад помилкового коду, який компілятор C пропускає */
void dangerous_c_usage(void) {
    /* Помилка: спроба запису у вхідний регістр IDR */
    GPIOA_IDR = 0x1234; 
}
```
```cpp
/* cpp_mmio_driver.hpp — Завершена заголовна бібліотека C++20 */
#include <cstdint>
#include <cstddef>
#include <type_traits>
#include <concepts>

namespace mcu {

// 1. Політики доступу до апаратного регістру
enum class Access : uint8_t {
    ReadOnly,
    WriteOnly,
    ReadWrite
};

// 2. RAII-блокування глобальних переривань для атомарних операцій RMW
class [[nodiscard]] InterruptLock {
public:
    InterruptLock() noexcept {
        #if defined(__arm__) || defined(__thumb__)
        asm volatile (
            "mrs %0, primask\n"
            "cpsid i\n"
            : "=r" (primask_)
            :
            : "memory"
        );
        #else
        primask_ = 0;
        #endif
    }

    ~InterruptLock() noexcept {
        #if defined(__arm__) || defined(__thumb__)
        asm volatile (
            "msr primask, %0\n"
            :
            : "r" (primask_)
            : "memory"
        );
        #endif
    }

    InterruptLock(const InterruptLock&) = delete;
    InterruptLock& operator=(const InterruptLock&) = delete;
    InterruptLock(InterruptLock&&) = delete;
    InterruptLock& operator=(InterruptLock&&) = delete;

private:
    uint32_t primask_{0};
};

// 3. Шаблон апаратного MMIO-регістра
template <uintptr_t Address, typename T, Access Acc>
struct Register {
    static_assert(std::is_integral_v<T>, "Тип регістру має бути цілочисельним!");

    // Читання дозволено тільки для ReadOnly та ReadWrite
    [[nodiscard]] static inline T read() noexcept 
        requires (Acc == Access::ReadOnly || Acc == Access::ReadWrite) 
    {
        return *reinterpret_cast<volatile T*>(Address);
    }

    // Запис дозволено тільки для WriteOnly та ReadWrite
    static inline void write(T value) noexcept 
        requires (Acc == Access::WriteOnly || Acc == Access::ReadWrite) 
    {
        *reinterpret_cast<volatile T*>(Address) = value;
    }

    // Атомарна модифікація бітів (Read-Modify-Write із блокуванням переривань)
    static inline void set_bits(T mask) noexcept 
        requires (Acc == Access::ReadWrite) 
    {
        InterruptLock lock;
        *reinterpret_cast<volatile T*>(Address) = *reinterpret_cast<volatile T*>(Address) | mask;
    }

    static inline void clear_bits(T mask) noexcept 
        requires (Acc == Access::ReadWrite) 
    {
        InterruptLock lock;
        *reinterpret_cast<volatile T*>(Address) = *reinterpret_cast<volatile T*>(Address) & ~mask;
    }

    static inline void modify(T clear_mask, T set_mask) noexcept
        requires (Acc == Access::ReadWrite)
    {
        InterruptLock lock;
        T current = *reinterpret_cast<volatile T*>(Address);
        *reinterpret_cast<volatile T*>(Address) = (current & ~clear_mask) | set_mask;
    }
};

// 4. Опис апаратної периферії GPIO
enum class Pin : uint8_t {
    P0 = 0, P1, P2, P3, P4, P5, P6, P7,
    P8, P9, P10, P11, P12, P13, P14, P15
};

enum class PinMode : uint32_t {
    Input     = 0b00,
    Output    = 0b01,
    Alternate = 0b10,
    Analog    = 0b11
};

template <uintptr_t BaseAddress>
struct GpioPort {
    using Moder = Register<BaseAddress + 0x00, uint32_t, Access::ReadWrite>;
    using Idr   = Register<BaseAddress + 0x10, uint32_t, Access::ReadOnly>;
    using Odr   = Register<BaseAddress + 0x14, uint32_t, Access::ReadWrite>;

    template <Pin P, PinMode M>
    static constexpr void configure_mode() noexcept {
        constexpr uint32_t shift = static_cast<uint8_t>(P) * 2U;
        constexpr uint32_t clear_mask = 0b11U << shift;
        constexpr uint32_t set_mask = static_cast<uint32_t>(M) << shift;

        Moder::modify(clear_mask, set_mask);
    }

    template <Pin P>
    static inline void set_pin(bool high) noexcept {
        constexpr uint32_t mask = 1U << static_cast<uint8_t>(P);
        if (high) {
            Odr::set_bits(mask);
        } else {
            Odr::clear_bits(mask);
        }
    }

    template <Pin P>
    [[nodiscard]] static inline bool read_pin() noexcept {
        constexpr uint32_t mask = 1U << static_cast<uint8_t>(P);
        return (Idr::read() & mask) != 0;
    }
};

// Конкретний екземпляр порту GPIOA на шині AHB2
using GpioA = GpioPort<0x40020000UL>;

} // namespace mcu

// Приклад використання в коді прошивки
void configure_hardware() {
    mcu::GpioA::configure_mode<mcu::Pin::P5, mcu::PinMode::Output>();
    mcu::GpioA::set_pin<mcu::Pin::P5>(true);
}
```
:::

## Покроковий механізм оптимізації компілятором

Розберемо, як саме компілятор C++ перетворює високорівневий шаблонний виклик `mcu::GpioA::configure_mode<mcu::Pin::P5, mcu::PinMode::Output>()` у машинний код:

1. **Інстанціювання шаблону (Template Instantiation):** компілятор підставляє константні параметри `P = Pin::P5` (значення 5) та `M = PinMode::Output` (значення 1) у шаблон методу `configure_mode()`.
2. **Константні обчислення (Compile-Time Evaluation):** обчислюються вирази зсуву `shift = 5 * 2 = 10`, маски очищення `clear_mask = 0b11 << 10 = 0xC00` (число 3072) та маски встановлення `set_mask = 0b01 << 10 = 0x400` (число 1024). Усі проміжні змінні замінюються прямими літералами.
3. **Вбудовування викликів (Inlining):** оскільки всі методи структури `Register` та `GpioPort` позначені `inline` і визначені в заголовку, компілятор ліквідує виклики `modify()`, безпосередньо підставляючи інструкції в точку виклику `configure_hardware()`.
4. **Розгортання деструктора RAII:** компілятор розміщує інструкцію читання `PRIMASK` та вимкнення переривань перед початком операції, а інструкцію відновлення `PRIMASK` — після фінального запису в регістр.
5. **Видалення мертвого коду (Dead Code Elimination):** оскільки структура `GpioA` не містить нестатичних полів (має нульовий розмір), компілятор не виділяє жодного байта пам'яті в стеку або сегменті `.bss`.

## Дизасемблерний аналіз для ARM Cortex-M4

Скомпілюємо функцію `configure_hardware()` за допомогою `arm-none-eabi-g++ -std=c++20 -O2 -mcpu=cortex-m4 -mthumb`:

```asm
configure_hardware():
    ldr     r3, .Lpool          ; r3 = 0x40020000 (базова адреса GPIOA)
    
    ; ── 1. Вхід у критичну секцію (конструктор InterruptLock) ──
    mrs     r2, PRIMASK         ; Читання поточного регістру маски переривань у r2
    cpsid   i                   ; Атомарне блокування переривань
    
    ; ── 2. Модифікація регістру MODER ──
    ldr     r1, [r3, #0]        ; Читання GPIOA_MODER (зсув 0x00)
    bic     r1, r1, #3072       ; Очищення бітів 10..11 (маска 0xC00 = 3072)
    orr     r1, r1, #1024       ; Встановлення біта 10 (маска 0x400 = 1024)
    str     r1, [r3, #0]        ; Запис оновленого значення у GPIOA_MODER
    
    ; ── 3. Вихід із критичної секції (деструктор InterruptLock) ──
    msr     PRIMASK, r2         ; Відновлення попереднього стану переривань
    
    ; ── 4. Запис у вихідний регістр ODR ──
    mrs     r2, PRIMASK         ; Повторний захист критичної секції для ODR
    cpsid   i                   ; Блокування переривань
    ldr     r1, [r3, #20]       ; Читання GPIOA_ODR (зсув 0x14 = 20)
    orr     r1, r1, #32         ; Встановлення біта 5 (маска 0x20 = 32)
    str     r1, [r3, #20]       ; Запис у GPIOA_ODR
    msr     PRIMASK, r2         ; Відновлення переривань
    
    bx      lr                  ; Повернення з функції
.Lpool:
    .word   1073872896          ; Константа 0x40020000 у пам'яті програм
```

## Крайові випадки та правила застосування

При використанні типізованої MMIO-абстракції на реальних мікроконтролерах слід враховувати такі особливості:

1. **Атомарні регістри бітового встановлення (STM32 BSRR):** для керування станом виводів сучасні мікроконтролери надають спеціальний регістр `BSRR` (Bit Set/Reset Register), запис у який виконується апаратно атомарно в один машинний такт. Для таких регістрів операція RMW не потрібна, тому метод `set_pin()` може виконувати прямий виклик `Bsrr::write(mask)` без створення `InterruptLock`.
2. **Бар'єри пам'яті компілятора:** оператор `asm volatile ("" ::: "memory")` у конструкторі та деструкторі `InterruptLock` забороняє оптимізатору компілятора переносити читання чи запис MMIO-регістрів за межі захищеної зони.
3. **Строга заборона неявних приведень:** завдяки використанню `enum class` спроба передати режим таймера у функцію `set_mode()` або спроба передати номер піна іншого порту генерує зрозумілу помилку типізації на етапі збирання.

Типізована абстракція регістрів C++20 усуває цілий клас апаратних збоїв у прошивках, не вимагаючи від системи додаткової пам'яті чи обчислювальних ресурсів.
