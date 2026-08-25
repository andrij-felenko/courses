# ⚙️ Міграція з вендорної IDE на CMake та GCC

Практичний перехід від закритого проєкту мікроконтролера у Keil MDK чи IAR Embedded Workbench до відкритої системи збірки на основі CMake та компілятора `arm-none-eabi-gcc` усуває потребу в комерційних ліцензіях і відкриває шлях до повної автоматизації в CI/CD. Головний виклик міграції полягає не стільки в компіляції файлів вихідного коду, скільки в адаптації вендорних розширень синтаксису, скриптів компонування, файлів запуску, реалізації системних заглушок стандартної бібліотеки та побудові ізольованого складального контейнера.

## 1. Архітектура відкритого проєкту

У вендорних середовищах дерево проєкту зберігається у монолітному XML-файлі (`.uvprojx` у Keil або `.ewp` в IAR), де змішані шляхи до сирців, конфігурація переривань, налаштування відладчика та стан вікон графічного інтерфейсу. При переході на CMake структура стає чіткою, модульною та повністю декларативною:

```
project-root/
├── CMakeLists.txt                  # Головний сценарій збірки цілей
├── cmake/
│   └── toolchain-arm-none-eabi.cmake # Опис крос-компілятора та прапорців цілі
├── core/
│   ├── inc/
│   │   └── compiler_port.h         # Уніфікація прагм та специфікаторів пам'яті
│   └── src/
│       ├── startup_stm32f407xx.c   # Векторна таблиця й Reset_Handler
│       ├── syscalls.c              # Заглушки newlib (_sbrk, _write, _read)
│       └── system_stm32f4xx.c      # Тактування й системна ініціалізація
├── drivers/
│   ├── cmsis/                      # Відкриті заголовки ARM CMSIS-Core
│   └── hal/                        # Периферійний шар (STM32 HAL / LL або власний)
├── linker/
│   └── STM32F407VGTx_FLASH.ld      # Скрипт лінкера GNU LD
└── Dockerfile                      # Відтворюване середовище збірки
```

У цій структурі кожен рівень чітко відокремлений:
- Каталог `cmake/` містить лише правила взаємодії з компілятором і не знає нічого про бізнес-логіку програми;
- Каталог `core/` містить код запуску процесора, векторну таблицю та системні виклики операційного середовища;
- Каталог `linker/` визначає фізичну карту пам'яті цільового кристала;
- Каталог `drivers/` ізолює низькорівневі виклики регістрів від верхніх рівнів застосунку.

## 2. Тулчейн-файл для крос-компіляції

Файл тулчейну повідомляє CMake, що збірка виконується не для хост-системи, а для цільового процесора Cortex-M. Він фіксує компілятор, компонувальник і базові апаратні прапорці архітектури:

```cmake
# cmake/toolchain-arm-none-eabi.cmake
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)

# Префікс інструментів GNU Arm Embedded Toolchain
set(TOOLCHAIN_PREFIX arm-none-eabi-)

set(CMAKE_C_COMPILER   ${TOOLCHAIN_PREFIX}gcc)
set(CMAKE_CXX_COMPILER ${TOOLCHAIN_PREFIX}g++)
set(CMAKE_ASM_COMPILER ${TOOLCHAIN_PREFIX}gcc)
set(CMAKE_OBJCOPY      ${TOOLCHAIN_PREFIX}objcopy CACHE INTERNAL "")
set(CMAKE_SIZE         ${TOOLCHAIN_PREFIX}size CACHE INTERNAL "")

# Запобігання тестовій лінковці під час конфігурації CMake (критично для bare-metal)
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

# Апаратні прапорці для ядра ARM Cortex-M4 з апаратним FPU
set(MCU_FLAGS "-mcpu=cortex-m4 -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb")

set(CMAKE_C_FLAGS_INIT   "${MCU_FLAGS} -fdata-sections -ffunction-sections -Wall -Wextra")
set(CMAKE_CXX_FLAGS_INIT "${MCU_FLAGS} -fdata-sections -ffunction-sections -fno-exceptions -fno-rtti -Wall -Wextra")
set(CMAKE_ASM_FLAGS_INIT "${MCU_FLAGS} -x assembler-with-cpp")

# Оптимізація розміру через вилучення невикористаних секцій та легку newlib-nano
set(CMAKE_EXE_LINKER_FLAGS_INIT "${MCU_FLAGS} -Wl,--gc-sections --specs=nano.specs --specs=nosys.specs")
```

Прапорці `-fdata-sections` та `-ffunction-sections` разом із ключем компонувальника `-Wl,--gc-sections` змушують компілятор розміщувати кожну функцію та глобальну змінну в окремій підсекції (наприклад, `.text.uart_init` або `.data.g_sensor_status`), а компонувальник — викидати невикористаний код. Це критично для мінімізації розміру бінарника прошивки в умовах обмеженої Flash-пам'яті мікроконтролера.

Параметр `--specs=nano.specs` підключає оптимізовану версію стандартної бібліотеки Newlib-Nano, що зменшує накладні витрати на базовий рантайм C/C++ у кілька разів. Специфікація `--specs=nosys.specs` надає дефолтні заглушки для невикористаних системних викликів POSIX, запобігаючи помилкам лінкера під час збірки без повноцінної ОС.

## 3. Головний CMakeLists.txt

Головний файл збірки описує виконувану ціль, додає шляхи до заголовків, скрипт компонування та генерує вихідні файли `.bin`, `.hex` і звіт про використання пам'яті:

```cmake
cmake_minimum_required(VERSION 3.22)

# Автоматичне підключення тулчейну, якщо не передано через CLI
if(NOT CMAKE_TOOLCHAIN_FILE)
    set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_SOURCE_DIR}/cmake/toolchain-arm-none-eabi.cmake")
endif()

project(firmware-portable C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(${PROJECT_NAME}.elf
    core/src/main.cpp
    core/src/startup_stm32f407xx.c
    core/src/syscalls.c
    core/src/system_stm32f4xx.c
    drivers/src/uart_driver.cpp
)

target_include_directories(${PROJECT_NAME}.elf PRIVATE
    core/inc
    drivers/inc
    drivers/cmsis/inc
)

# Передача скрипта компонувальника
set(LINKER_SCRIPT "${CMAKE_CURRENT_SOURCE_DIR}/linker/STM32F407VGTx_FLASH.ld")
target_link_options(${PROJECT_NAME}.elf PRIVATE
    -T${LINKER_SCRIPT}
    -Wl,-Map=${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}.map,--cref
)

# Генерація сирих бінарних файлів та виведення розміру секцій
add_custom_command(TARGET ${PROJECT_NAME}.elf POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O ihex ${PROJECT_NAME}.elf ${PROJECT_NAME}.hex
    COMMAND ${CMAKE_OBJCOPY} -O binary ${PROJECT_NAME}.elf ${PROJECT_NAME}.bin
    COMMAND ${CMAKE_SIZE} --format=berkeley ${PROJECT_NAME}.elf
    COMMENT "Generating raw binaries (.hex, .bin) and calculating memory footprint"
)
```

## 4. Адаптація скрипта компонування (Linker Script)

У середовищі Keil використовується формат scatter-файлів (`.sct`), а в IAR — файли конфігурації лінкера (`.icf`). Компонувальник GNU LD використовує власний синтаксис `.ld`.

Скрипт компонування вирішує три критичні задачі:
1. Описує фізичні регіони пам'яті (Flash і RAM), їхні початкові адреси (`ORIGIN`) та довжини (`LENGTH`);
2. Розподіляє вхідні об'єктні секції за адресами пам'яті (VMA — Virtual Memory Address) та визначає адресу завантаження у Flash (LMA — Load Memory Address);
3. Експортує системні символи меж секцій, які використовує стартап-код для ініціалізації оперативної пам'яті після апаратного скидання процесора.

Нижче наведено базовий скрипт компонувальника `linker/STM32F407VGTx_FLASH.ld`:

```ld
/* Точка входу в програму після скидання живлення */
ENTRY(Reset_Handler)

/* Визначення стеку: вершина оперативної пам'яті RAM */
_estack = ORIGIN(RAM) + LENGTH(RAM);

/* Мінімальні розміри для динамічної пам'яті (купи) та стеку */
_Min_Heap_Size = 0x200;  /* 512 байтів */
_Min_Stack_Size = 0x400; /* 1 КБ */

MEMORY
{
    FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 1024K
    RAM   (xrw) : ORIGIN = 0x20000000, LENGTH = 128K
    CCMRAM (rw) : ORIGIN = 0x10000000, LENGTH = 64K
}

SECTIONS
{
    /* Таблиця векторів переривань розміщується на самому початку Flash */
    .isr_vector :
    {
        . = ALIGN(4);
        KEEP(*(.isr_vector))
        . = ALIGN(4);
    } >FLASH

    /* Виконуваний код та константи */
    .text :
    {
        . = ALIGN(4);
        *(.text)
        *(.text*)
        *(.rodata)
        *(.rodata*)
        . = ALIGN(4);
        _etext = .;
    } >FLASH

    /* Символ початку завантаження секції ініціалізованих даних у Flash */
    _sidata = LOADADDR(.data);

    /* Ініціалізовані змінні: виконуються в RAM, завантажуються з Flash */
    .data :
    {
        . = ALIGN(4);
        _sdata = .;
        *(.data)
        *(.data*)
        *(.ramfunc)       /* Функції, що виконуються з оперативної пам'яті */
        *(.ramfunc*)
        . = ALIGN(4);
        _edata = .;
    } >RAM AT> FLASH

    /* Неініціалізовані дані (обнуляються стартапом) */
    .bss :
    {
        . = ALIGN(4);
        _sbss = .;
        __bss_start__ = _sbss;
        *(.bss)
        *(.bss*)
        *(COMMON)
        . = ALIGN(4);
        _ebss = .;
        __bss_end__ = _ebss;
    } >RAM

    /* Перевірка наявності вільного місця для стеку та купи */
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

Конструкція `>RAM AT> FLASH` визначає подвійну адресу секції `.data`: під час роботи мікроконтролера змінні розташовані в пам'яті `RAM` (VMA), але початкові значення зберігаються у енергонезалежній пам'яті `FLASH` (LMA). Символ `_sidata` зберігає точну адресу початку даних у Flash, звідки код стартапу копіює їх у пам'ять за адресою `_sdata`. Директива `KEEP(*(.isr_vector))` гарантує, що компонувальник не видалить векторну таблицю навіть за увімкненого прапорця `--gc-sections`.

## 5. Стартап-код та таблиця векторів переривань

У пропрієтарних IDE стартап зазвичай реалізовано на вендорному асемблері (діалект armasm у Keil або `iar-as` в IAR). Для відкритого тулчейну значно надійніше та прозоріше написати стартап безпосередньо мовою C/C++.

Стартап виконує чотири послідовні дії:
1. Оголошує таблицю векторів Cortex-M, де першим словом є адреса вершини стеку `_estack`, а другим — адреса функції `Reset_Handler`;
2. Копіює байти секції `.data` з Flash-пам'яті (`_sidata`) в оперативну пам'ять (`_sdata` .. `_edata`);
3. Заповнює нулями область пам'яті секції `.bss` (`_sbss` .. `_ebss`);
4. Викликає системну функцію ініціалізації тактування `SystemInit()`, функцію запуску конструкторів статичних C++ об'єктів `__libc_init_array()` та передає керування у функцію `main()`.

:::tabs
```c
/* core/src/startup_stm32f407xx.c */
#include <stdint.h>

/* Символи, експортовані скриптом компонування GNU LD */
extern uint32_t _estack;
extern uint32_t _sidata;
extern uint32_t _sdata;
extern uint32_t _edata;
extern uint32_t _sbss;
extern uint32_t _ebss;

extern void SystemInit(void);
extern void __libc_init_array(void);
extern int main(void);

void Reset_Handler(void);
void Default_Handler(void) {
    while (1) {}
}

/* Оголошення переривань як weak-аліасів до Default_Handler */
void NMI_Handler(void)        __attribute__((weak, alias("Default_Handler")));
void HardFault_Handler(void)  __attribute__((weak, alias("Default_Handler")));
void SysTick_Handler(void)    __attribute__((weak, alias("Default_Handler")));

/* Таблиця векторів переривань */
__attribute__((section(".isr_vector"), used))
void (* const g_pfnVectors[])(void) = {
    (void (*)(void))((uint32_t)&_estack), /* 0x00: Початкове значення SP */
    Reset_Handler,                         /* 0x04: Скидання (Reset) */
    NMI_Handler,                           /* 0x08: NMI */
    HardFault_Handler,                     /* 0x0C: Hard Fault */
    0, 0, 0, 0, 0, 0, 0,                   /* Зарезервовано */
    0, 0, 0,                               /* SVC, DebugMon, PendSV */
    SysTick_Handler,                       /* 0x3C: SysTick */
};

void Reset_Handler(void) {
    /* 1. Копіювання ініціалізованих даних з Flash у RAM */
    uint32_t *pSrc = &_sidata;
    uint32_t *pDst = &_sdata;
    while (pDst < &_edata) {
        *pDst++ = *pSrc++;
    }

    /* 2. Обнулення неініціалізованої пам'яті BSS */
    pDst = &_sbss;
    while (pDst < &_ebss) {
        *pDst++ = 0;
    }

    /* 3. Ініціалізація апаратної підсистеми тактування */
    SystemInit();

    /* 4. Виклик конструкторів глобальних C++ об'єктів */
    __libc_init_array();

    /* 5. Перехід до основної програми */
    main();

    /* Якщо main() завершився — зупиняємось у нескінченному циклі */
    while (1) {}
}
```
```cpp
// core/src/startup_stm32f407xx.cpp
#include <cstdint>
#include <span>

extern "C" {
    extern std::uint32_t _estack;
    extern std::uint32_t _sidata;
    extern std::uint32_t _sdata;
    extern std::uint32_t _edata;
    extern std::uint32_t _sbss;
    extern std::uint32_t _ebss;

    void SystemInit() noexcept;
    void __libc_init_array() noexcept;
    int main();

    void Reset_Handler() noexcept;
    void Default_Handler() noexcept {
        while (true) {}
    }

    void NMI_Handler() noexcept       [[gnu::weak, gnu::alias("Default_Handler")]];
    void HardFault_Handler() noexcept [[gnu::weak, gnu::alias("Default_Handler")]];
    void SysTick_Handler() noexcept   [[gnu::weak, gnu::alias("Default_Handler")]];

    using IsrVectorFn = void (*)(void);

    [[gnu::section(".isr_vector"), gnu::used]]
    const IsrVectorFn g_pfnVectors[] = {
        reinterpret_cast<IsrVectorFn>(&_estack),
        Reset_Handler,
        NMI_Handler,
        HardFault_Handler,
        nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr,
        nullptr, nullptr, nullptr,
        SysTick_Handler
    };
}

void Reset_Handler() noexcept {
    // 1. Копіювання секції .data
    const auto* src = &_sidata;
    auto* dst = &_sdata;
    while (dst < &_edata) {
        *dst++ = *src++;
    }

    // 2. Очищення секції .bss
    dst = &_sbss;
    while (dst < &_ebss) {
        *dst++ = 0;
    }

    // 3. Ініціалізація ядра та виклик конструкторів
    SystemInit();
    __libc_init_array();

    // 4. Головний цикл застосунку
    main();

    while (true) {}
}
```
:::

## 6. Системні виклики (Syscalls) та пам'ять Newlib

При переході на відкритий тулчейн компілятор використовує бібліотеку C `newlib` або `newlib-nano`. Функції динамічного виділення пам'яті (`malloc`, `free`, оператори `new`/`delete` у C++) та потокового виводу (`printf`) вимагають реалізації низькорівневих функцій операційного середовища.

У файлі `core/src/syscalls.c` реалізуються дві ключові функції:
1. `_sbrk` — керує збільшенням розміру купи (Heap), перевіряючи, щоб динамічна пам'ять не перекрила вершину стеку;
2. `_write` — перенаправляє символи виводу у фізичний периферійний інтерфейс (наприклад, UART або SWO).

:::tabs
```c
/* core/src/syscalls.c */
#include <sys/stat.h>
#include <errno.h>
#include <stdint.h>

#undef errno
extern int errno;

extern uint32_t _end;     /* Символ початку купи з лінкер-скрипта */
extern uint32_t _estack;  /* Вершина стеку */

void* _sbrk(ptrdiff_t incr) {
    static uint8_t *heap_end = NULL;
    uint8_t *prev_heap_end;

    if (heap_end == NULL) {
        heap_end = (uint8_t*)&_end;
    }

    prev_heap_end = heap_end;

    /* Запобігання зіткненню купи зі стеком (залишаємо запас під стек 1 КБ) */
    if (heap_end + incr > (uint8_t*)&_estack - 0x400) {
        errno = ENOMEM;
        return (void*)-1;
    }

    heap_end += incr;
    return (void*)prev_heap_end;
}

/* Перенаправлення виводу printf у низькорівневий UART драйвер */
extern void uart_send_char(char c);

int _write(int file, char *ptr, int len) {
    (void)file;
    for (int i = 0; i < len; ++i) {
        uart_send_char(ptr[i]);
    }
    return len;
}

int _read(int file, char *ptr, int len) {
    (void)file; (void)ptr; (void)len;
    return 0;
}

int _close(int file) { (void)file; return -1; }
int _fstat(int file, struct stat *st) { (void)file; st->st_mode = S_IFCHR; return 0; }
int _isatty(int file) { (void)file; return 1; }
int _lseek(int file, int ptr, int dir) { (void)file; (void)ptr; (void)dir; return 0; }
```
```cpp
// core/src/syscalls.cpp
#include <sys/stat.h>
#include <cerrno>
#include <cstdint>
#include <cstddef>
#include <span>

extern "C" {
    extern std::uint32_t _end;
    extern std::uint32_t _estack;

    void uart_send_char(char c) noexcept;

    void* _sbrk(std::ptrdiff_t incr) noexcept {
        static auto* heap_end = reinterpret_cast<std::uint8_t*>(&_end);
        auto* prev_heap_end = heap_end;

        const auto* stack_limit = reinterpret_cast<std::uint8_t*>(&_estack) - 0x400;
        if (heap_end + incr > stack_limit) {
            errno = ENOMEM;
            return reinterpret_cast<void*>(-1);
        }

        heap_end += incr;
        return reinterpret_cast<void*>(prev_heap_end);
    }

    int _write(int file, const char *ptr, int len) noexcept {
        (void)file;
        std::span<const char> buffer(ptr, static_cast<std::size_t>(len));
        for (char ch : buffer) {
            uart_send_char(ch);
        }
        return len;
    }

    int _read(int, char*, int) noexcept { return 0; }
    int _close(int) noexcept { return -1; }
    int _fstat(int, struct stat *st) noexcept { st->st_mode = S_IFCHR; return 0; }
    int _isatty(int) noexcept { return 1; }
    int _lseek(int, int, int) noexcept { return 0; }
}
```
:::

Якщо прошивка використовує операційну систему реального часу (RTOS, наприклад FreeRTOS), динамічне виділення пам'яті всередині стандартних функцій Newlib стає джерелом гонитви (*race condition*). У такому разі виділення пам'яті перенаправляють на потокобезпечні алокатори FreeRTOS (`pvPortMalloc` / `vPortFree`), або захищають системні виклики через реентерабельні структури `_reent` Newlib.

## 7. Абстракція розширень компіляторів

Головний бар'єр перенесення вихідного коду з Keil або IAR до GCC — це специфічні прагми та ключові слова розміщення у пам'яті (наприклад, виконання критичного коду з оперативної пам'яті RAM чи упакування мережевих структур). Щоб не редагувати код у десятках місць, створюється єдиний заголовок сумісності:

:::tabs
```c
/* core/inc/compiler_port.h */
#ifndef COMPILER_PORT_H
#define COMPILER_PORT_H

#include <stdint.h>
#include <stddef.h>

#if defined(__GNUC__) || defined(__clang__)
    /* GCC та Clang розширення */
    #define PORT_RAMFUNC        __attribute__((section(".ramfunc"), noinline))
    #define PORT_NORETURN       __attribute__((noreturn))
    #define PORT_ALIGNED(n)     __attribute__((aligned(n)))
    #define PORT_PACKED_STRUCT  struct __attribute__((packed))
    #define PORT_WEAK           __attribute__((weak))
    #define PORT_NAKED          __attribute__((naked))

    #define PORT_BARRIER()      __asm volatile("" ::: "memory")
    #define PORT_NOP()          __asm volatile("nop")

#elif defined(__ICCARM__)
    /* IAR Embedded Workbench розширення */
    #define PORT_RAMFUNC        __ramfunc
    #define PORT_NORETURN       __noreturn
    #define PORT_ALIGNED(n)     _Pragma(STRINGIFY(data_alignment=n))
    #define PORT_PACKED_STRUCT  __packed struct
    #define PORT_WEAK           __weak
    #define PORT_NAKED          __stackless

    #define PORT_BARRIER()      __asm volatile("" ::: "memory")
    #define PORT_NOP()          __no_operation()

#elif defined(__CC_ARM)
    /* Keil Arm Compiler 5 (ArmCC застарілий) */
    #define PORT_RAMFUNC        __attribute__((section("ram_functions")))
    #define PORT_NORETURN       __declspec(noreturn)
    #define PORT_ALIGNED(n)     __align(n)
    #define PORT_PACKED_STRUCT  __packed struct
    #define PORT_WEAK           __weak
    #define PORT_NAKED          __asm

    #define PORT_BARRIER()      __schedule_barrier()
    #define PORT_NOP()          __nop()
#else
    #error "Невідомий компілятор: додайте відповідні макроси розширень"
#endif

/* Приклад використання у C */
PORT_PACKED_STRUCT TelemetryFrame {
    uint32_t timestamp_ms;
    uint16_t voltage_mv;
    uint16_t current_ma;
    uint8_t  status_flags;
};

PORT_RAMFUNC void flash_critical_write_page(uint32_t page_addr, const uint8_t *data, size_t len);

#endif /* COMPILER_PORT_H */
```
```cpp
// core/inc/compiler_port.hpp
#ifndef COMPILER_PORT_HPP
#define COMPILER_PORT_HPP

#include <cstdint>
#include <cstddef>
#include <span>

#if defined(__GNUC__) || defined(__clang__)
    #define PORT_RAMFUNC        [[gnu::section(".ramfunc"), gnu::noinline]]
    #define PORT_NORETURN       [[noreturn]]
    #define PORT_ALIGNED(n)     alignas(n)
    #define PORT_PACKED_STRUCT  struct [[gnu::packed]]
    #define PORT_WEAK           [[gnu::weak]]

    inline void port_barrier() noexcept { asm volatile("" ::: "memory"); }
    inline void port_nop() noexcept     { asm volatile("nop"); }

#elif defined(__ICCARM__)
    #define PORT_RAMFUNC        __ramfunc
    #define PORT_NORETURN       [[noreturn]]
    #define PORT_ALIGNED(n)     alignas(n)
    #define PORT_PACKED_STRUCT  __packed struct
    #define PORT_WEAK           __weak

    inline void port_barrier() noexcept { asm volatile("" ::: "memory"); }
    inline void port_nop() noexcept     { __no_operation(); }
#else
    #error "Невідомий компілятор: додайте відповідні макроси розширень"
#endif

namespace core::portable {

PORT_PACKED_STRUCT TelemetryFrame {
    std::uint32_t timestamp_ms;
    std::uint16_t voltage_mv;
    std::uint16_t current_ma;
    std::uint8_t  status_flags;
};

PORT_RAMFUNC void flash_critical_write_page(std::uint32_t page_addr,
                                            std::span<const std::uint8_t> payload) noexcept;

} // namespace core::portable

#endif // COMPILER_PORT_HPP
```
:::

## 8. Докеризація складального середовища

Для повної ізоляції процесу збірки від операційної системи розробника та гарантії однакового результату створюється мінімальний `Dockerfile`:

```dockerfile
# Dockerfile
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Встановлення необхідних відкритих інструментів збірки
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    ninja-build \
    gcc-arm-none-eabi \
    libnewlib-arm-none-eabi \
    libstdc++-arm-none-eabi-newlib \
    python3 \
    git \
    clang-format \
    clang-tidy \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# За замовчуванням виконуємо конфігурацію та збірку через Ninja
CMD ["sh", "-c", "cmake -B build -G Ninja -DCMAKE_TOOLCHAIN_FILE=cmake/toolchain-arm-none-eabi.cmake && cmake --build build"]
```

Такий Docker-контейнер не потребує графічного інтерфейсу, монтується безпосередньо до робочої копії репозиторію та виконує детерміновану збірку на будь-якому сервері без потреби в ліцензійних серверах або донглах.

## 9. Запуск і перевірка збірки

Збірка виконується локально або всередині контейнера однаковими командами без використання графічного інтерфейсу:

```bash
# 1. Генерація файлів збірки Ninja
cmake -B build -G Ninja -DCMAKE_TOOLCHAIN_FILE=cmake/toolchain-arm-none-eabi.cmake -DCMAKE_BUILD_TYPE=Release

# 2. Компіляція та лінкування цілей
cmake --build build -j$(nproc)

# 3. Перевірка карти пам'яті через GNU size
arm-none-eabi-size -A -d build/firmware-portable.elf
```

Такий підхід повністю усуває залежність від комерційних IDE, перетворюючи складання мікроконтролерної прошивки на стандартний, версіонований і автоматизований інженерний процес, готовий до масштабування в сучасних хмарних конвеєрах неперервної інтеграції.
