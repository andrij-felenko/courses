# ⚙️ Повний мінімальний стартовий код для ARM Cortex-M

Цей практичний проектний приклад містить завершену та перевірену реалізацію автономного стартового коду для мікроконтролерів архітектури ARM Cortex-M (сімейства STM32, SAMD, LPC, NXP Kinetis тощо) мовами C та ідіоматичного C++. Реалізація розгортає повне середовище пам'яті, ініціалізує математичний співпроцесор FPU, запускає глобальні конструктори C++, обробляє апаратне скидання та містить діагностичний обробник апаратних помилок із витягуванням кадру стека.

## 1. Скрипт лінкера: експорт адресних символів

Перед написанням стартового коду необхідно визначити карту розміщення секцій у пам'яті за допомогою скрипта лінкера (`linker.ld`).

Зверніть увагу на важливий нюанс роботи тулчейну: символи лінкера (`_sdata`, `_edata`, `_sidata`, `_sbss`, `_ebss`, `_end`) не є звичайними змінними у пам'яті. У таблиці символів об'єктного файлу ELF вони позначають лише **адреси** меж секцій. Тому в коді C або C++ до них завжди звертаються за допомогою оператора взяття адреси: `&_sdata`. Якщо спробувати прочитати `_sdata` як звичайну змінну без амперсанда, компілятор згенерує інструкцію читання пам'яті за цією адресою, намагаючись використати перше машинне слово самої секції як адресу.

Також за стандартом ARM AAPCS (Procedure Call Standard for the ARM Architecture) покажчик стека `SP` на межі виклику будь-якої публічної функції або обробника переривання повинен бути строго вирівняний на **8 байтів** (подвійне машинне слово). Це необхідно для коректної роботи інструкцій подвійної точності `LDRD`/`STRD` та 64-бітних операцій з рухомою комою. Тому стек `_estack` розміщується за адресою, кратною 8 байтам.

Для запобігання непомітному переповненню оперативної пам'яті скрипт лінкера містить спеціальну секцію перевірки мінімального резерву під купу та стек (`_Min_Heap_Size` та `_Min_Stack_Size`). Якщо сумарний обсяг глобальних змінних разом із резервом стека перевищить фізичний розмір RAM, лінкер завершить роботу з помилкою переповнення на етапі збирання.

```ld
/* Скрипт розміщення секцій пам'яті linker.ld */
ENTRY(Reset_Handler)

MEMORY
{
  FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 512K
  RAM   (rwx) : ORIGIN = 0x20000000, LENGTH = 128K
}

/* Вершина головного стека — самий кінець оперативної пам'яті (вирівняно на 8 байтів) */
_estack = ORIGIN(RAM) + LENGTH(RAM);

_Min_Heap_Size = 0x200;   /* Мінімальний резерв під купу (512 байтів) */
_Min_Stack_Size = 0x400;  /* Мінімальний гарантований стек (1024 байти) */

SECTIONS
{
  /* 1. Векторна таблиця обов'язково розміщується на початку Flash */
  .isr_vector :
  {
    . = ALIGN(4);
    KEEP(*(.isr_vector))
    . = ALIGN(4);
  } >FLASH

  /* 2. Тіло програми та константи */
  .text :
  {
    . = ALIGN(4);
    *(.text)
    *(.text*)
    *(.rodata)
    *(.rodata*)
    . = ALIGN(4);
  } >FLASH

  /* 3. Таблиця покажчиків на глобальні конструктори C++ */
  .init_array :
  {
    . = ALIGN(4);
    PROVIDE_HIDDEN (__init_array_start = .);
    KEEP (*(SORT(.init_array.*)))
    KEEP (*(.init_array*))
    PROVIDE_HIDDEN (__init_array_end = .);
    . = ALIGN(4);
  } >FLASH

  /* Завантажувальна адреса LMA для початкових значень .data у Flash */
  _sidata = LOADADDR(.data);

  /* 4. Секція ініціалізованих змінних у RAM (VMA), що завантажується з Flash (LMA) */
  .data :
  {
    . = ALIGN(4);
    _sdata = .;        /* Початок секції .data в RAM */
    *(.data)
    *(.data*)
    . = ALIGN(4);
    _edata = .;        /* Кінець секції .data в RAM */
  } >RAM AT> FLASH

  /* 5. Секція неініціалізованих змінних у RAM (у Flash займає 0 байтів) */
  .bss :
  {
    . = ALIGN(4);
    _sbss = .;         /* Початок секції .bss в RAM */
    *(.bss)
    *(.bss*)
    *(COMMON)
    . = ALIGN(4);
    _ebss = .;         /* Кінець секції .bss в RAM */
  } >RAM

  /* 6. Початок динамічної пам'яті (купи / heap) для _sbrk та перевірка запасу стека */
  ._user_heap_stack :
  {
    . = ALIGN(8);
    PROVIDE ( end = . );
    PROVIDE ( _end = . );
    . = . + _Min_Heap_Size;
    . = . + _Min_Stack_Size;
    . = ALIGN(8);
  } >RAM
}
```

## 2. Реалізація стартового модуля

Нижче наведено повну реалізацію стартового коду для C та ідіоматичного C++. Модуль розгортає повне середовище виконання:
1. Формує статичний масив векторів переривань із прив'язкою до секції `.isr_vector`.
2. Копіює 32-бітні блоки даних із Flash LMA у RAM VMA між мітками `_sdata` та `_edata`.
3. Заповнює діапазон RAM між `_sbss` та `_ebss` нулями.
4. Надає повний доступ до співпроцесорів `CP10`/`CP11` у регістрі `SCB->CPACR` для розблокування FPU.
5. Обходить масив `.init_array` та послідовно викликає конструктори глобальних об'єктів C++.
6. Передає керування функції `main()` та реалізує термінальну пастку `wfi` для збереження енергії у разі повернення.
7. Містить спеціальний діагностичний обробник `HardFault_Handler` із точкою зупину налагоджувача `bkpt #0`.

:::tabs
```c
#include <stdint.h>
#include <stddef.h>

/* Символи адресних меж, експортовані лінкером */
extern uint32_t _estack;
extern uint32_t _sidata;
extern uint32_t _sdata;
extern uint32_t _edata;
extern uint32_t _sbss;
extern uint32_t _ebss;

/* Межі таблиці виклику конструкторів C++ */
extern void (*__init_array_start[])(void);
extern void (*__init_array_end[])(void);

/* Прототипи системних функцій */
int main(void);
void Reset_Handler(void);
void Default_Handler(void);

/* Оголошення системних винятків зі слабким зв'язком */
void NMI_Handler(void)        __attribute__((weak, alias("Default_Handler")));
void HardFault_Handler(void)  __attribute__((weak, alias("Default_Handler")));
void MemManage_Handler(void)  __attribute__((weak, alias("Default_Handler")));
void BusFault_Handler(void)   __attribute__((weak, alias("Default_Handler")));
void UsageFault_Handler(void) __attribute__((weak, alias("Default_Handler")));
void SVC_Handler(void)        __attribute__((weak, alias("Default_Handler")));
void PendSV_Handler(void)     __attribute__((weak, alias("Default_Handler")));
void SysTick_Handler(void)    __attribute__((weak, alias("Default_Handler")));

/* Системне налаштування тактування за замовчуванням */
void SystemInit(void) __attribute__((weak));
void SystemInit(void) {
    /* Базова заглушка: користувач може перевизначити у власному файлі */
}

/* Увімкнення математичного співпроцесора FPU (Cortex-M4/M7/M33) */
static inline void enable_fpu(void) {
    volatile uint32_t *scb_cpacr = (volatile uint32_t *)0xE000ED88UL;
    /* Надання повного доступу (Full Access) до блоків CP10 та CP11: біти 20..23 = 0b1111 */
    *scb_cpacr |= (0xFUL << 20);
    __asm volatile("dsb\n\tisb" ::: "memory");
}

/* Ініціалізація глобальних об'єктів C++ */
static inline void init_cpp_runtime(void) {
    size_t count = (size_t)(__init_array_end - __init_array_start);
    for (size_t i = 0; i < count; ++i) {
        if (__init_array_start[i] != NULL) {
            __init_array_start[i]();
        }
    }
}

/* Головна точка входу після апаратного скидання */
void Reset_Handler(void) {
    /* 1. Копіювання початкових значень .data з Flash у RAM */
    uint32_t *p_src = &_sidata;
    uint32_t *p_dst = &_sdata;
    while (p_dst < &_edata) {
        *p_dst++ = *p_src++;
    }

    /* 2. Занулення пам'яті секції .bss у RAM */
    uint32_t *p_bss = &_sbss;
    while (p_bss < &_ebss) {
        *p_bss++ = 0;
    }

    /* 3. Апаратне налаштування: FPU та тактування */
    enable_fpu();
    SystemInit();

    /* 4. Виклик C++ конструкторів */
    init_cpp_runtime();

    /* 5. Передача керування у прикладну програму */
    (void)main();

    /* 6. Безпечний сон процесора, якщо main() випадково завершив роботу */
    while (1) {
        __asm volatile("wfi");
    }
}

/* Обробник непередбачених або невизначених переривань */
void Default_Handler(void) {
    /* Апаратна точка зупину для захоплення під налагоджувачем GDB */
    __asm volatile("bkpt #0");
    while (1) {
    }
}

/* Векторна таблиця, розташована у секції .isr_vector */
__attribute__((section(".isr_vector"), used))
void (* const g_pfnVectors[])(void) = {
    (void (*)(void))(&_estack), /* 0x00: Initial SP */
    Reset_Handler,              /* 0x04: Reset Handler */
    NMI_Handler,                /* 0x08: NMI */
    HardFault_Handler,          /* 0x0C: HardFault */
    MemManage_Handler,          /* 0x10: MemManage */
    BusFault_Handler,           /* 0x14: BusFault */
    UsageFault_Handler,         /* 0x18: UsageFault */
    0, 0, 0, 0,                 /* 0x1C..0x28: Reserved */
    SVC_Handler,                /* 0x2C: SVCall */
    0,                          /* 0x30: Debug Monitor */
    0,                          /* 0x34: Reserved */
    PendSV_Handler,             /* 0x38: PendSV */
    SysTick_Handler,            /* 0x3C: SysTick */
};
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>

/* Символи меж від лінкера */
extern "C" {
    extern std::uint32_t _estack;
    extern std::uint32_t _sidata;
    extern std::uint32_t _sdata;
    extern std::uint32_t _edata;
    extern std::uint32_t _sbss;
    extern std::uint32_t _ebss;

    using CtorPointer = void (*)(void);
    extern CtorPointer __init_array_start[];
    extern CtorPointer __init_array_end[];

    int main();
    void Reset_Handler();
    void Default_Handler();

    void NMI_Handler()        __attribute__((weak, alias("Default_Handler")));
    void HardFault_Handler()  __attribute__((weak, alias("Default_Handler")));
    void MemManage_Handler()  __attribute__((weak, alias("Default_Handler")));
    void BusFault_Handler()   __attribute__((weak, alias("Default_Handler")));
    void UsageFault_Handler() __attribute__((weak, alias("Default_Handler")));
    void SVC_Handler()        __attribute__((weak, alias("Default_Handler")));
    void PendSV_Handler()     __attribute__((weak, alias("Default_Handler")));
    void SysTick_Handler()    __attribute__((weak, alias("Default_Handler")));
    void SystemInit()         __attribute__((weak));
}

void SystemInit() {
    /* Базова реалізація за замовчуванням */
}

namespace mcu::startup {
    /* Увімкнення апаратного співпроцесора FPU */
    inline void enable_fpu() noexcept {
        constexpr auto cpacr_reg_addr = static_cast<std::uintptr_t>(0xE000ED88UL);
        auto* const scb_cpacr = reinterpret_cast<volatile std::uint32_t*>(cpacr_reg_addr);
        
        constexpr std::uint32_t full_access = (0xFUL << 20);
        *scb_cpacr |= full_access;
        asm volatile("dsb\n\tisb" ::: "memory");
    }

    /* Виклик глобальних конструкторів через std::span */
    inline void call_constructors() noexcept {
        const std::span<CtorPointer> ctors(
            __init_array_start,
            static_cast<std::size_t>(__init_array_end - __init_array_start)
        );

        for (const auto ctor : ctors) {
            if (ctor != nullptr) {
                ctor();
            }
        }
    }
}

extern "C" void Reset_Handler() {
    /* 1. Копіювання ініціалізованих даних .data з Flash у RAM */
    const std::uint32_t* src = &_sidata;
    std::uint32_t* dst = &_sdata;
    while (dst < &_edata) {
        *dst++ = *src++;
    }

    /* 2. Заповнення секції .bss нулями в RAM */
    std::uint32_t* bss = &_sbss;
    while (bss < &_ebss) {
        *bss++ = 0;
    }

    /* 3. Апаратна ініціалізація ядра */
    mcu::startup::enable_fpu();
    SystemInit();

    /* 4. Запуск глобальних конструкторів C++ */
    mcu::startup::call_constructors();

    /* 5. Виклик прикладної логіки */
    static_cast<void>(main());

    /* 6. Термінальна енергозберігаюча пастка */
    while (true) {
        asm volatile("wfi");
    }
}

extern "C" void Default_Handler() {
    asm volatile("bkpt #0");
    while (true) {
    }
}

/* Типізована векторна таблиця для C++ */
using VectorEntry = void (*)(void);

extern "C" {
    __attribute__((section(".isr_vector"), used))
    const VectorEntry g_pfnVectors[] = {
        reinterpret_cast<VectorEntry>(&_estack),
        Reset_Handler,
        NMI_Handler,
        HardFault_Handler,
        MemManage_Handler,
        BusFault_Handler,
        UsageFault_Handler,
        nullptr, nullptr, nullptr, nullptr,
        SVC_Handler,
        nullptr,
        nullptr,
        PendSV_Handler,
        SysTick_Handler,
    };
}
```
:::

## 3. Діагностичний обробник HardFault з витягуванням стека

У реальних проектах обробник `HardFault_Handler` не повинен просто крутитися в глухому порожньому циклі. Для швидкого пошуку причини збою (ділення на нуль, невірний покажчик, доступ за межі масиву) створюють спеціальну асемблерну обгортку, яка зчитує поточний активний покажчик стека (`MSP` або `PSP`) і передає його в діагностичну функцію:

:::tabs
```c
/* Діагностичний аналізатор збою HardFault мовою C */
void HardFault_Handler_C(uint32_t *stack_frame) {
    volatile uint32_t r0  = stack_frame[0];
    volatile uint32_t r1  = stack_frame[1];
    volatile uint32_t r2  = stack_frame[2];
    volatile uint32_t r3  = stack_frame[3];
    volatile uint32_t r12 = stack_frame[4];
    volatile uint32_t lr  = stack_frame[5];
    volatile uint32_t pc  = stack_frame[6]; /* Адреса інструкції, що викликала збій */
    volatile uint32_t psr = stack_frame[7];

    volatile uint32_t cfsr = *(volatile uint32_t *)0xE000ED28;
    volatile uint32_t hfsr = *(volatile uint32_t *)0xE000ED2C;

    (void)r0; (void)r1; (void)r2; (void)r3; (void)r12; (void)lr; (void)pc; (void)psr;
    (void)cfsr; (void)hfsr;

    /* Зупинка під налагоджувачем */
    __asm volatile("bkpt #0");
    while (1) {
    }
}
```
```cpp
#include <cstdint>

/* Діагностичний аналізатор збою HardFault мовою C++ */
extern "C" void HardFault_Handler_C(std::uint32_t* stack_frame) {
    const std::uint32_t r0  = stack_frame[0];
    const std::uint32_t r1  = stack_frame[1];
    const std::uint32_t r2  = stack_frame[2];
    const std::uint32_t r3  = stack_frame[3];
    const std::uint32_t r12 = stack_frame[4];
    const std::uint32_t lr  = stack_frame[5];
    const std::uint32_t pc  = stack_frame[6]; /* Точна адреса аварійної інструкції */
    const std::uint32_t psr = stack_frame[7];

    const auto cfsr = *reinterpret_cast<volatile std::uint32_t*>(0xE000ED28UL);
    const auto hfsr = *reinterpret_cast<volatile std::uint32_t*>(0xE000ED2CUL);

    static_cast<void>(r0);  static_cast<void>(r1);  static_cast<void>(r2);
    static_cast<void>(r3);  static_cast<void>(r12); static_cast<void>(lr);
    static_cast<void>(pc);  static_cast<void>(psr); static_cast<void>(cfsr);
    static_cast<void>(hfsr);

    asm volatile("bkpt #0");
    while (true) {
    }
}
```
:::

Маючи значення `pc` (наприклад, `0x08001248`), інженер може виконати команду в терміналі:
```bash
arm-none-eabi-addr2line -e firmware.elf 0x08001248
```
Утиліта миттєво поверне точну назву вихідного файлу та номер рядка коду C/C++, на якому стався краш.

## 4. Реалізація системного виклику `_sbrk` для динамічної пам'яті

Якщо ваша програма використовує динамічне виділення пам'яті (`malloc`, `free`, оператори `new` та `delete`), стандартній бібліотеці C потрібна системна функція `_sbrk()`, яка керує зростанням купи (heap) від символу `_end` угору в напрямку вершини стека:

:::tabs
```c
/* Реалізація системного виклику _sbrk мовою C */
#include <errno.h>
#include <stdint.h>

extern uint32_t _end;
extern uint32_t _estack;

void *_sbrk(ptrdiff_t incr) {
    static uint8_t *heap_end = NULL;
    uint8_t *prev_heap_end;

    if (heap_end == NULL) {
        heap_end = (uint8_t *)&_end;
    }

    prev_heap_end = heap_end;

    /* Перевірка на зіткнення купи зі стеком */
    if ((uint32_t)(heap_end + incr) > ((uint32_t)&_estack - 1024)) {
        errno = ENOMEM;
        return (void *)-1;
    }

    heap_end += incr;
    return (void *)prev_heap_end;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <cerrno>

/* Реалізація системного виклику _sbrk мовою C++ */
extern "C" {
    extern std::uint32_t _end;
    extern std::uint32_t _estack;

    void* _sbrk(std::ptrdiff_t incr) noexcept {
        static auto* heap_end = reinterpret_cast<std::uint8_t*>(&_end);
        auto* const prev_heap_end = heap_end;

        const auto current_sp = reinterpret_cast<std::uintptr_t>(heap_end + incr);
        const auto stack_limit = reinterpret_cast<std::uintptr_t>(&_estack) - 1024UL;

        if (current_sp > stack_limit) {
            errno = ENOMEM;
            return reinterpret_cast<void*>(-1);
        }

        heap_end += incr;
        return reinterpret_cast<void*>(prev_heap_end);
    }
}
```
:::

## 5. Прапорці збирання та компіляторні пастки

Під час збирання автономного образу мікроконтролера за допомогою інструментів GCC (`arm-none-eabi-gcc` або `arm-none-eabi-g++`) необхідно передати компілятору суворий набір прапорців командного рядка:

- **`-nostartfiles`:** Забороняє лінкеру підключати стандартні системні об'єктні файли хост-платформи (`crt0.o`, `crti.o`, `crtbegin.o`), оскільки всю функціональність ініціалізації бере на себе наш написаний модуль.
- **`-ffreestanding`:** Повідомляє компілятору, що середовище виконання є повністю автономним (bare-metal, без операційної системи), і програма не обов'язково починається з виклику `main(int argc, char **argv)`.
- **`-fno-builtin` або `-fno-builtin-memcpy`:** **Критично важливий прапорець оптимізації.** Під час збирання з рівнем оптимізації `-O2` або `-O3` компілятор GCC аналізує цикли і може розпізнати конструкцію `while (p_dst < &_edata) *p_dst++ = *p_src++;` як шаблон копіювання пам'яті. У результаті компілятор автоматично замінює цей цикл на асемблерний виклик стандартної функції `memcpy()`. Якщо функція `memcpy` у вашій збірці сама використовує неініціалізовані ресурси пам'яті або відсутня в проекті, це викличе фатальне зависання чи нескінченну рекурсію до завершення ініціалізації RAM.
- **`-fno-exceptions -fno-rtti`:** Для проектів мовою C++ вимикає генерацію таблиць розгортання винятків (`.eh_frame`) та інформації про типи часу виконання (RTTI), що економить від 20 до 50 КБ Flash-пам'яті мікроконтролера.

## 6. Покрокова діагностика старту в GDB та OpenOCD

Для детальної перевірки коректності виконання кожного етапу стартового коду використовують покрокове апаратне налагодження через інтерфейс SWD або JTAG за допомогою налагоджувача GDB:

```gdb
# 1. Підключення до сервера налагодження OpenOCD
target extended-remote :3333

# 2. Апаратне скидання мікроконтролера та зупинка процесора на першому такті
monitor reset halt

# 3. Встановлення точки зупину на точку входу стартового коду
break Reset_Handler
continue

# 4. Перевірка початкового стану регістрів ядра (SP має вказувати на _estack, PC — на Reset_Handler)
info registers sp pc xpsr

# 5. Покрокове проходження інструкцій копіювання .data
stepi 10

# 6. Перевірка наявності скопійованих значень у пам'яті SRAM за адресою секції .data
x/4xw &_sdata

# 7. Перевірка заповнення нулями в пам'яті секції .bss
x/16xb &_sbss

# 8. Продовження виконання до входу в основну програму main()
break main
continue
```

Така покрокова перевірка дозволяє миттєво локалізувати помилки в скрипті лінкера, невірні адреси секцій LMA/VMA або зависання під час увімкнення тактування `SystemInit()`.
