# ⚙️ Практичний тулчейн для ARM Cortex-M та проєкт прошивки

Цей практичний посібник містить повну, готову до виробничого використання конфігурацію крос-збірки мікроконтролерної прошивки для ядра ARM Cortex-M4 (STM32F4) за допомогою CMake та GNU Arm Embedded Toolchain (`arm-none-eabi-gcc`). Його відкривають, коли потрібно створити надійний каркас проєкту для мікроконтролера без операційної системи (bare-metal), усунути помилки тестування компілятора на стадії конфігурації, налаштувати скрипт лінкера й забезпечити паралельну підтримку мов C та сучасного C++.

---

## 1. Файл тулчейна: arm-none-eabi.cmake

Файл тулчейна повідомляє CMake про відсутність операційної системи (`Generic`), встановлює цільовий процесор, вказує шляхи до виконуваних файлів тулчейна та вимикає спроби лінкування тестових бінарників під час ініціалізації компілятора.

Головним завданням цього сценарію є переведення внутрішнього стану CMake у режим крос-компіляції ще до того, як рушій збірки почне перевіряти компілятор. Для мікроконтролерів без операційної системи обов'язково встановлюється режим `STATIC_LIBRARY` для команди `try_compile`: це змушує CMake тестувати компілятор створенням об'єктного файлу та архіву `.a`, повністю виключаючи виклик лінкера.

У сценарії передбачено гнучкий механізм виявлення бінарних утиліт: якщо встановлено змінну оточення `ARM_TOOLCHAIN_PATH`, шляхи будуються від неї, інакше CMake виконує стандартний пошук у системній змінній `PATH`.

```cmake
# cmake/arm-none-eabi.cmake
cmake_minimum_required(VERSION 3.20)

# 1. Декларація цільової платформи без операційної системи
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)

# 2. Обхід помилки лінкування під час перевірки компілятора в project()
# Замість створення повноцінного ELF CMake перевірятиме компілятор через архіватор .a
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

# 3. Виявлення префікса цільового тулчейна
set(TOOLCHAIN_TRIPLE "arm-none-eabi")

# Підтримка пошуку в системному PATH або за фіксованим префіксом змінної середовища
if(DEFINED ENV{ARM_TOOLCHAIN_PATH})
    set(TOOLCHAIN_BIN_DIR "$ENV{ARM_TOOLCHAIN_PATH}/bin/")
else()
    set(TOOLCHAIN_BIN_DIR "")
endif()

# 4. Призначення компіляторів та бінарних утиліт
set(CMAKE_C_COMPILER   "${TOOLCHAIN_BIN_DIR}${TOOLCHAIN_TRIPLE}-gcc")
set(CMAKE_CXX_COMPILER "${TOOLCHAIN_BIN_DIR}${TOOLCHAIN_TRIPLE}-g++")
set(CMAKE_ASM_COMPILER "${TOOLCHAIN_BIN_DIR}${TOOLCHAIN_TRIPLE}-gcc")

set(CMAKE_AR       "${TOOLCHAIN_BIN_DIR}${TOOLCHAIN_TRIPLE}-ar"      CACHE FILEPATH "Archiver")
set(CMAKE_RANLIB   "${TOOLCHAIN_BIN_DIR}${TOOLCHAIN_TRIPLE}-ranlib"  CACHE FILEPATH "Ranlib")
set(CMAKE_OBJCOPY  "${TOOLCHAIN_BIN_DIR}${TOOLCHAIN_TRIPLE}-objcopy" CACHE FILEPATH "Objcopy")
set(CMAKE_OBJDUMP  "${TOOLCHAIN_BIN_DIR}${TOOLCHAIN_TRIPLE}-objdump" CACHE FILEPATH "Objdump")
set(CMAKE_SIZE     "${TOOLCHAIN_BIN_DIR}${TOOLCHAIN_TRIPLE}-size"    CACHE FILEPATH "Size utility")

# 5. Ізоляція пошукових шляхів: інструменти шукаємо на хості, бібліотеки хоста блокуємо
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
```

---

## 2. Скрипт лінкера: linker.ld

Для компонування виконуваного ELF-файла мікроконтролеру потрібна точна карта пам'яті. У скрипті лінкера задаються фізичні адреси Flash-пам'яті (де зберігається двійковий образ прошивки) та оперативної пам'яті SRAM (де розміщуються змінні, стек і динамічна пам'ять).

Зверніть увагу на секцію `.data`: вона має адресу завантаження (LMA, англ. *Load Memory Address*) у Flash-пам'яті (`AT> FLASH`) та віртуальну адресу виконання (VMA, англ. *Virtual Memory Address*) у RAM. Під час старту мікроконтролера код ініціалізації повинен скопіювати початкові значення змінних із Flash у RAM за символами `_sidata`, `_sdata` та `_edata`.

Крім того, для підтримки глобальних об'єктів у C++ скрипт лінкера містить секцію `.init_array`, де компілятор зберігає покажчики на конструктори глобальних об'єктів, які мають бути викликані перед входом у головну функцію програми.

```ld
/* linker.ld — карта пам'яті для мікроконтролера STM32F401 (Flash: 512KB, RAM: 96KB) */
ENTRY(Reset_Handler)

MEMORY
{
    FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 512K
    RAM   (rwx) : ORIGIN = 0x20000000, LENGTH = 96K
}

_estack = ORIGIN(RAM) + LENGTH(RAM);

SECTIONS
{
    /* Таблиця векторів переривань розміщується на самому початку Flash */
    .isr_vector :
    {
        . = ALIGN(4);
        KEEP(*(.isr_vector))
        . = ALIGN(4);
    } > FLASH

    /* Машинний код програми та константні дані */
    .text :
    {
        . = ALIGN(4);
        *(.text)
        *(.text*)
        *(.rodata)
        *(.rodata*)
        . = ALIGN(4);
        _etext = .;
    } > FLASH

    /* Таблиця виклику статичних конструкторів C++ */
    .init_array :
    {
        . = ALIGN(4);
        PROVIDE_HIDDEN (__init_array_start = .);
        KEEP (*(SORT(.init_array.*)))
        KEEP (*(.init_array*))
        PROVIDE_HIDDEN (__init_array_end = .);
        . = ALIGN(4);
    } > FLASH

    _sidata = LOADADDR(.data);

    /* Ініціалізовані глобальні змінні (копіюються з Flash у RAM під час старту) */
    .data :
    {
        . = ALIGN(4);
        _sdata = .;
        *(.data)
        *(.data*)
        . = ALIGN(4);
        _edata = .;
    } > RAM AT> FLASH

    /* Неініціалізовані змінні (очищаються нулями під час старту) */
    .bss :
    {
        . = ALIGN(4);
        _sbss = .;
        *(.bss)
        *(.bss*)
        *(COMMON)
        . = ALIGN(4);
        _ebss = .;
    } > RAM
}
```

---

## 3. Опис збірки: CMakeLists.txt

Файл опису збірки `CMakeLists.txt` інкапсулює апаратні прапорці процесора в інтерфейсній цілі `cortex_m4_flags`. Такий підхід гарантує, що прапорці архітектури (`-mcpu=cortex-m4`, `-mthumb`, `-mfpu=fpv4-sp-d16`, `-mfloat-abi=hard`) транзитивно передаються як на етап компіляції вихідних файлів, так і на етап фінального компонування лінкером.

Прапорець `-mfloat-abi=hard` вказує компілятору генерувати апаратні інструкції FPU для чисел із рухомою комою та передавати аргументи функцій типу `float` безпосередньо через регістри `s0-s15`, а не емулювати їх програмно через загальні регістри `r0-r3`.

Крім того, застосовуються прапорці `-ffunction-sections` та `-fdata-sections` разом із опцією лінкера `-Wl,--gc-sections`. Це вмикає агресивне видалення невикористаного мертвого коду (англ. *Dead Code Elimination*), що суттєво зменшує кінцевий розмір прошивки у Flash-пам'яті.

```cmake
cmake_minimum_required(VERSION 3.20)
project(stm32_firmware C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 1. Інтерфейсна ціль для прапорців архітектури Cortex-M4 з апаратним FPU
add_library(cortex_m4_flags INTERFACE)
target_compile_options(cortex_m4_flags INTERFACE
    -mcpu=cortex-m4
    -mthumb
    -mfpu=fpv4-sp-d16
    -mfloat-abi=hard
    -ffunction-sections
    -fdata-sections
    -Wall
    -Wextra
)

target_link_options(cortex_m4_flags INTERFACE
    -mcpu=cortex-m4
    -mthumb
    -mfpu=fpv4-sp-d16
    -mfloat-abi=hard
    -T${CMAKE_CURRENT_SOURCE_DIR}/linker.ld
    -Wl,--gc-sections
    --specs=nano.specs
    --specs=nosys.specs
    -Wl,-Map=${CMAKE_CURRENT_BINARY_DIR}/firmware.map
)

# 2. Виконуваний файл прошивки
add_executable(firmware.elf
    startup.c
    main.cpp
)

target_link_libraries(firmware.elf PRIVATE cortex_m4_flags)

# 3. Генерація файлів образів пам'яті для програматора (.hex та .bin)
add_custom_command(TARGET firmware.elf POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:firmware.elf> ${CMAKE_CURRENT_BINARY_DIR}/firmware.hex
    COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:firmware.elf> ${CMAKE_CURRENT_BINARY_DIR}/firmware.bin
    COMMAND ${CMAKE_SIZE} $<TARGET_FILE:firmware.elf>
    COMMENT "Створення бінарних файлів .hex і .bin та вивід розміру секцій:"
)
```

---

## 4. Вихідний код: ініціалізація та головний цикл

Стартап-код виконує базове апаратне налаштування після скидання: налаштовує вказівник стека, копіює секцію ініціалізованих змінних `.data` з енергонезалежної Flash-пам'яті в RAM, заповнює нулями секцію неініціалізованих змінних `.bss`, викликає конструктори статичних об'єктів C++ і передає керування функції `main_app()`.

Таблиця векторів переривань розміщується в окремій іменованій секції `.isr_vector`. Скрипт лінкера за допомогою директиви `KEEP(*(.isr_vector))` гарантує, що оптимізатор лінкера не видалить цю таблицю як невикористану.

### Код ініціалізації мікроконтролера (startup)

:::tabs
```c
/* startup.c — мінімальний стартап-код мовою C */
#include <stdint.h>

extern uint32_t _estack;
extern uint32_t _sidata, _sdata, _edata, _sbss, _ebss;

void Reset_Handler(void);
void Default_Handler(void) { while (1); }

__attribute__((section(".isr_vector")))
void (* const g_pfnVectors[])(void) = {
    (void (*)(void))(&_estack),
    Reset_Handler,
    Default_Handler, /* NMI */
    Default_Handler  /* HardFault */
};

extern void main_app(void);

void Reset_Handler(void) {
    uint32_t *src = &_sidata;
    uint32_t *dst = &_sdata;
    while (dst < &_edata) {
        *dst++ = *src++;
    }
    dst = &_sbss;
    while (dst < &_ebss) {
        *dst++ = 0;
    }
    main_app();
    while (1);
}
```
```cpp
// startup.cpp — строго типізований стартап-код мовою C++ з викликом конструкторів
#include <cstdint>

extern "C" {
    extern std::uint32_t _estack;
    extern std::uint32_t _sidata, _sdata, _edata, _sbss, _ebss;
    extern void (*__init_array_start[])() noexcept;
    extern void (*__init_array_end[])() noexcept;
    void Reset_Handler() noexcept;
    void main_app() noexcept;
}

namespace {
[[noreturn]] void default_handler() noexcept {
    while (true) {}
}
}

using InterruptVector = void (*)() noexcept;

extern "C" [[gnu::section(".isr_vector")]]
const InterruptVector g_pfnVectors[] = {
    reinterpret_cast<InterruptVector>(&_estack),
    Reset_Handler,
    default_handler, // NMI
    default_handler  // HardFault
};

extern "C" void Reset_Handler() noexcept {
    // 1. Копіювання ініціалізованих змінних у RAM
    const auto *src = &_sidata;
    auto *dst = &_sdata;
    while (dst < &_edata) {
        *dst++ = *src++;
    }

    // 2. Очищення секції неініціалізованих змінних у RAM
    dst = &_sbss;
    while (dst < &_ebss) {
        *dst++ = 0;
    }

    // 3. Виклик конструкторів глобальних і статичних об'єктів C++
    for (auto **ctor = __init_array_start; ctor < __init_array_end; ++ctor) {
        if (*ctor != nullptr) {
            (*ctor)();
        }
    }

    // 4. Запуск головної логіки програми
    main_app();
    while (true) {}
}
```
:::

### Головна логіка: керування апаратними регістрами

У наведених нижче вкладках продемонстровано керування апаратними регістрами порту введення-виведення (миготіння світлодіодом на піні PC13): у C — через традиційні макроси розіменування числових адрес, у C++ — через безпечні шаблонні обгортки з типізацією операцій читання/запису та compile-time гарантією адресації.

:::tabs
```c
/* main.c — процедурний підхід із макросами розіменування адрес */
#include <stdint.h>

#define RCC_AHB1ENR  (*(volatile uint32_t *)0x40023830)
#define GPIOC_MODER  (*(volatile uint32_t *)0x40020800)
#define GPIOC_ODR    (*(volatile uint32_t *)0x40020814)

static void delay_cycles(volatile uint32_t count) {
    while (count--) {
        __asm__ volatile("nop");
    }
}

void main_app(void) {
    /* Увімкнення тактування порту GPIOC (біт 2) */
    RCC_AHB1ENR |= (1U << 2);

    /* Налаштування піна PC13 на вихід */
    GPIOC_MODER &= ~(3U << (13 * 2));
    GPIOC_MODER |= (1U << (13 * 2));

    while (1) {
        GPIOC_ODR ^= (1U << 13);
        delay_cycles(500000);
    }
}
```
```cpp
// main.cpp — типізована робота з регістрами мікроконтролера через шаблони
#include <cstdint>

namespace mcu {

template <std::uintptr_t Addr>
struct Register {
    static void write(std::uint32_t val) noexcept {
        *reinterpret_cast<volatile std::uint32_t *>(Addr) = val;
    }

    [[nodiscard]] static std::uint32_t read() noexcept {
        return *reinterpret_cast<volatile std::uint32_t *>(Addr);
    }

    static void set_bits(std::uint32_t mask) noexcept {
        write(read() | mask);
    }

    static void clear_bits(std::uint32_t mask) noexcept {
        write(read() & ~mask);
    }
};

using RccAhb1Enr = Register<0x40023830>;
using GpiocModer = Register<0x40020800>;
using GpiocOdr   = Register<0x40020814>;

inline void delay(volatile std::uint32_t count) noexcept {
    while (count--) {
        asm volatile("nop");
    }
}

} // namespace mcu

extern "C" void main_app() noexcept {
    // Увімкнення тактування GPIOC (біт 2)
    mcu::RccAhb1Enr::set_bits(1U << 2);

    // Налаштування PC13 (режим виходу 0b01)
    mcu::GpiocModer::clear_bits(3U << (13 * 2));
    mcu::GpiocModer::set_bits(1U << (13 * 2));

    while (true) {
        mcu::GpiocOdr::write(mcu::GpiocOdr::read() ^ (1U << 13));
        mcu::delay(500000);
    }
}
```
:::

---

## 5. Специфікації Newlib та системні заглушки

У мікроконтролерній розробці критичну роль відіграють опції Newlib, що передаються лінкеру:

1. **`--specs=nano.specs`**: Підключає оптимізовану за розміром версію стандартної бібліотеки Newlib Nano. У ній видалено громіздку підтримку 64-розрядних чисел із плаваючою комою у функціях форматування `printf`/`scanf`, що заощаджує від 20 до 50 кілобайтів Flash-пам'яті.
2. **`--specs=nosys.specs`**: Підключає заглушки для низькорівневих викликів бібліотеки C (таких як `_write`, `_read`, `_sbrk`, `_exit`). Без цього прапорця або власної реалізації системних заглушок лінкер повідомить про невизначені посилання на системні виклики під час спроби використання будь-яких стандартних функцій або операторів динамічної пам'яті (`malloc`, `new`).

---

## 6. Запуск конфігурації, збірки та верифікації

Для виконання збірки прошивки передайте файл тулчейна командному рядку CMake або використайте генератор Ninja:

```bash
# 1. Генерація системи збірки із зазначенням файлу тулчейна
cmake -B build -S . --toolchain cmake/arm-none-eabi.cmake -G Ninja

# 2. Компіляція бінарних файлів та генерація образів .hex/.bin
cmake --build build

# 3. Перевірка розміру секцій скомпільованого двійкового файлу
# arm-none-eabi-size build/firmware.elf
# text    data     bss     dec     hex filename
#  584       0       0     584     248 firmware.elf
```

Утиліта `arm-none-eabi-size` демонструє розподіл пам'яті: секція `text` містить машинний код і таблицю векторів у Flash-пам'яті, тоді як змінні секцій `data` та `bss` займають оперативну пам'ять SRAM. Отримані файли `firmware.hex` та `firmware.bin` готові для завантаження в мікроконтролер через апаратний програматор ST-Link, J-Link або завантажувач DFU.

### Аналіз карти компонування (Map-файл)

Завдяки прапорцю `-Wl,-Map=${CMAKE_CURRENT_BINARY_DIR}/firmware.map`, лінкер формує текстовий файл звіту про розміщення символів у пам'яті. Відкривши цей файл, розробник може точно простежити:
- Які саме функції та об'єктні файли потрапили у фінальний ELF, а які було відкинуто оптимізатором `--gc-sections`.
- Точні адреси розташування кожної глобальної змінної у Flash та RAM.
- Залишковий вільний обсяг Flash-пам'яті мікроконтролера та межу стека (`_estack`).
