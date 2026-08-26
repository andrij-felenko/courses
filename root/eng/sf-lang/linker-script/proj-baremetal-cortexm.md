# ⚙️ Практика розробки: Bare-Metal стартап і Linker Script для ARM Cortex-M

Програмування мікроконтролерів без операційної системи (bare-metal) вимагає повного контролю над тим, як скомпільовані інструкції та змінні розміщуються у фізичній пам'яті кремнієвого чипа. Цей практичний проєкт демонструє створення повнофункціонального образу прошивки для ядра ARM Cortex-M4 (мікроконтролер лінійки STM32F4): від написання скрипта компонувача з підтримкою Flash, SRAM і швидкої CCMRAM до реалізації стартового коду (startup) мовами C та C++, з детальним аналізом карти пам'яті (`.map`).

---

## 1. Архітектурні вимоги та карта пам'яті чипа

Цільовий мікроконтролер містить три фізично відокремлені банки пам'яті з власними шинними інтерфейсами:

1. **Flash (ROM)** — `0x08000000..0x0807FFFF` (512 КБ): енергонезалежна пам'ять програм, підключена через шини I-Code (інструкції) та D-Code (літерали). Підтримує пряме виконання коду безпосередньо з кремнію (XIP — eXecute In Place);
2. **SRAM1 (Головна RAM)** — `0x20000000..0x2001FFFF` (128 КБ): загальна пам'ять для змінних `.data`, `.bss`, динамічної купи (Heap) та головного стека процесора (MSP);
3. **CCMRAM (Core Coupled Memory RAM)** — `0x10000000..0x1000FFFF` (64 КБ): надшвидка оперативна пам'ять, підключена безпосередньо до шини D-Bus процесорного ядра Cortex-M4. Вона працює без затримок (нуль тактів очікування), проте не має доступу до контролера прямого доступу до пам'яті (DMA). Через це CCMRAM ідеально підходить для критичних векторів переривань, таблиць математичних функцій цифрової обробки сигналів (DSP) або стеків окремих задач RTOS.

---

## 2. Робочий Linker Script: `stm32f4.ld`

Скрипт компонувача описує фізичні банки пам'яті, експортує межові символи для стартового коду та контролює статичний бюджет стека й купи через директиви `ASSERT`.

```ld
/* Точка входу для GDB та апаратного завантажувача */
ENTRY(Reset_Handler)

/* Визначення розмірів системного стека та купи */
_Min_Heap_Size  = 0x400;  /* 1 КБ мінімальної купи */
_Min_Stack_Size = 0x800;  /* 2 КБ мінімального стека */

/* 1. Декларація фізичних банків пам'яті */
MEMORY
{
  FLASH   (rx)  : ORIGIN = 0x08000000, LENGTH = 512K
  RAM     (xrw) : ORIGIN = 0x20000000, LENGTH = 128K
  CCMRAM  (rw)  : ORIGIN = 0x10000000, LENGTH = 64K
}

/* Обчислення верхівки стека: кінець головного банку SRAM */
_estack = ORIGIN(RAM) + LENGTH(RAM);

/* 2. Розподіл секцій по адресах виконання (VMA) та завантаження (LMA) */
SECTIONS
{
  /* Таблиця векторів переривань: строго на початку Flash (0x08000000) */
  .isr_vector :
  {
    . = ALIGN(4);
    KEEP(*(.isr_vector))
    . = ALIGN(4);
  } >FLASH

  /* Машинний код програми */
  .text :
  {
    . = ALIGN(4);
    *(.text)
    *(.text*)
    *(.glue_7)         /* Клейовий код ARM-Thumb */
    *(.glue_7t)
    *(.eh_frame)

    KEEP (*(.init))
    KEEP (*(.fini))

    . = ALIGN(4);
    _etext = .;        /* Кінець коду */
  } >FLASH

  /* Константи та рядкові літерали */
  .rodata :
  {
    . = ALIGN(4);
    *(.rodata)
    *(.rodata*)
    . = ALIGN(4);
  } >FLASH

  /* Таблиці конструкторів для глобальних об'єктів C++ */
  .init_array :
  {
    . = ALIGN(4);
    PROVIDE_HIDDEN (__init_array_start = .);
    KEEP (*(SORT_BY_INIT_PRIORITY(.init_array.*) SORT_BY_INIT_PRIORITY(.ctors.*)))
    KEEP (*(.init_array* .ctors*))
    PROVIDE_HIDDEN (__init_array_end = .);
    . = ALIGN(4);
  } >FLASH

  /* Адреса завантаження секції .data у Flash (LMA) */
  _sidata = LOADADDR(.data);

  /* Ініціалізовані глобальні та статичні змінні (VMA в RAM, LMA у Flash) */
  .data :
  {
    . = ALIGN(4);
    _sdata = .;        /* Початок .data у RAM */
    *(.data)
    *(.data*)
    . = ALIGN(4);
    _edata = .;        /* Кінець .data у RAM */
  } >RAM AT> FLASH

  /* Спеціальна секція для розміщення критичних буферів у CCMRAM */
  .ccmram :
  {
    . = ALIGN(4);
    _sccmram = .;
    *(.ccmram)
    *(.ccmram*)
    . = ALIGN(4);
    _eccmram = .;
  } >CCMRAM AT> FLASH
  _siccmram = LOADADDR(.ccmram);

  /* Неініціалізовані змінні, які стартовий код заповнює нулями */
  .bss :
  {
    . = ALIGN(4);
    _sbss = .;         /* Початок .bss у RAM */
    __bss_start__ = _sbss;
    *(.bss)
    *(.bss*)
    *(COMMON)
    . = ALIGN(4);
    _ebss = .;         /* Кінець .bss у RAM */
    __bss_end__ = _ebss;
  } >RAM

  /* Резервування пам'яті для динамічної купи та стека з перевіркою переповнення */
  ._user_heap_stack :
  {
    . = ALIGN(8);
    PROVIDE ( end = . );
    PROVIDE ( _end = . );
    . = . + _Min_Heap_Size;
    . = . + _Min_Stack_Size;
    . = ALIGN(8);
  } >RAM

  /* Перевірка лімітів пам'яті під час компонування */
  ASSERT(_ebss + _Min_Heap_Size + _Min_Stack_Size <= ORIGIN(RAM) + LENGTH(RAM),
         "Критична помилка: Секції .data + .bss + Heap + Stack перевищують обсяг SRAM!")

  /* Видалення непотрібних метаданих компілятора */
  /DISCARD/ :
  {
    *(.comment)
    *(.note*)
  }
}
```

### Покроковий розбір структури скрипта

1. **Директива `ENTRY(Reset_Handler)`** повідомляє налагоджувачу та аналізаторам двійкових файлів, що першою виконуваною функцією програми є обробник скидання `Reset_Handler`.
2. **Блок `MEMORY`** резервує точні простори фізичних адрес. Якщо обсяг скомпільованого коду чи констант перевищить 512 КБ, лінкер зупинить збірку з повідомленням `region 'FLASH' overflowed by N bytes`.
3. **Вершина стека `_estack`** розраховується як `0x20000000 + 128K = 0x20020000`. Оскільки стек Cortex-M є спадним (full descending), покажчик стека починає рух від самої верхньої межі SRAM вниз до молодших адрес.
4. **Директива `KEEP(*(.isr_vector))`** гарантує збереження масиву векторів переривань. За увімкненого прапорця лінкера `--gc-sections` (видалення невикористовуваного коду) компонувальник видалив би таблицю векторів, оскільки жодна функція у C-коді явно не викликає масив `g_pfnVectors`.
5. **Розділення VMA та LMA у секції `.data`**: вираз `>RAM AT> FLASH` наказує лінкеру генерувати інструкції звернення до змінних за адресами в діапазоні RAM `0x20000000`, але розмістити самі початкові байти змінних у Flash-пам'яті відразу після коду `.text`. Функція `_sidata = LOADADDR(.data);` експортує фізичну адресу початку цих даних у Flash.
6. **Директива `ASSERT`** гарантує статичний контроль пам'яті: якщо сума кінцевої адреси секції `.bss` (`_ebss`) та мінімально необхідних розмірів купи й стека виходить за межі 128 КБ оперативної пам'яті, збірка аварійно переривається.

---

## 3. Таблиця векторів та стартовий код (Startup)

Стартовий код виконує початкову ініціалізацію чипа до передачі керування у функцію `main()`:
1. Завантажує змінні `.data` зі збереженого у Flash образу (`_sidata`) у робочу пам'ять RAM (`_sdata.._edata`);
2. Обнуляє область пам'яті `.bss` (`_sbss.._ebss`);
3. Копіює швидкі функції або буфери у `CCMRAM` (якщо вони присутні);
4. Викликає конструктори глобальних об'єктів C++ через `__libc_init_array()`;
5. Передає керування у `main()`.

:::tabs
```c
/* startup.c — Стартова ініціалізація мікроконтролера мовою C */
#include <stdint.h>

/* Символи, визначені у скрипті компонувача stm32f4.ld */
extern uint32_t _estack;
extern uint32_t _sidata;
extern uint32_t _sdata;
extern uint32_t _edata;
extern uint32_t _sbss;
extern uint32_t _ebss;
extern uint32_t _siccmram;
extern uint32_t _sccmram;
extern uint32_t _eccmram;

/* Прототипи функцій */
void Reset_Handler(void);
void Default_Handler(void);
extern void __libc_init_array(void);
extern int main(void);

/* Оголошення слабких обробників винятків Cortex-M */
void NMI_Handler(void)        __attribute__((weak, alias("Default_Handler")));
void HardFault_Handler(void)  __attribute__((weak, alias("Default_Handler")));
void MemManage_Handler(void)  __attribute__((weak, alias("Default_Handler")));
void BusFault_Handler(void)   __attribute__((weak, alias("Default_Handler")));
void UsageFault_Handler(void) __attribute__((weak, alias("Default_Handler")));
void SysTick_Handler(void)    __attribute__((weak, alias("Default_Handler")));

/* Таблиця векторів переривань, що примусово розміщується у .isr_vector */
__attribute__((section(".isr_vector"), used))
const uint32_t* const g_pfnVectors[] = {
    (const uint32_t*)&_estack,          /* 0x0000: Початковий Main Stack Pointer */
    (const uint32_t*)Reset_Handler,     /* 0x0004: Вектор скидання процесора */
    (const uint32_t*)NMI_Handler,       /* 0x0008: Немасковане переривання */
    (const uint32_t*)HardFault_Handler, /* 0x000C: Апаратна помилка */
    (const uint32_t*)MemManage_Handler, /* 0x0010: Помилка MPU */
    (const uint32_t*)BusFault_Handler,  /* 0x0014: Помилка шини */
    (const uint32_t*)UsageFault_Handler,/* 0x0018: Помилка інструкції */
    0, 0, 0, 0,                         /* Зарезервовано ARM */
    0, 0, 0,
    (const uint32_t*)SysTick_Handler    /* 0x003C: Системний таймер */
};

void Reset_Handler(void) {
    /* 1. Копіювання секції .data з Flash у SRAM */
    uint32_t *p_src = &_sidata;
    uint32_t *p_dst = &_sdata;
    while (p_dst < &_edata) {
        *p_dst++ = *p_src++;
    }

    /* 2. Занулення секції .bss в SRAM */
    p_dst = &_sbss;
    while (p_dst < &_ebss) {
        *p_dst++ = 0;
    }

    /* 3. Копіювання секції .ccmram з Flash у CCMRAM (за потреби) */
    p_src = &_siccmram;
    p_dst = &_sccmram;
    while (p_dst < &_eccmram) {
        *p_dst++ = *p_src++;
    }

    /* 4. Виклик конструкторів глобальних об'єктів C++ */
    __libc_init_array();

    /* 5. Запуск головної програми */
    main();

    /* Якщо main() повернув значення — нескінченний цикл */
    while (1) {}
}

void Default_Handler(void) {
    while (1) {}
}
```
```cpp
// startup.cpp — Ідіоматична стартова ініціалізація мовою C++20
#include <cstdint>
#include <span>
#include <algorithm>

// Експорт лінкерних символів через масиви без розміру
extern "C" {
    extern std::uint32_t _estack[];
    extern std::uint32_t _sidata[];
    extern std::uint32_t _sdata[];
    extern std::uint32_t _edata[];
    extern std::uint32_t _sbss[];
    extern std::uint32_t _ebss[];
    extern std::uint32_t _siccmram[];
    extern std::uint32_t _sccmram[];
    extern std::uint32_t _eccmram[];

    void Reset_Handler() noexcept;
    void Default_Handler() noexcept;
    void __libc_init_array() noexcept;
    int main();
}

// Псевдоніми обробників переривань
extern "C" {
    void NMI_Handler() __attribute__((weak, alias("Default_Handler")));
    void HardFault_Handler() __attribute__((weak, alias("Default_Handler")));
    void SysTick_Handler() __attribute__((weak, alias("Default_Handler")));
}

// Типобезпечна таблиця векторів переривань
using VectorHandler = void (*)();

struct VectorTable {
    const void* initial_sp;
    VectorHandler reset;
    VectorHandler nmi;
    VectorHandler hard_fault;
    VectorHandler reserved[4];
    VectorHandler sv_call;
    VectorHandler reserved_debug;
    VectorHandler reserved2;
    VectorHandler pend_sv;
    VectorHandler sys_tick;
};

__attribute__((section(".isr_vector"), used))
const VectorTable g_vector_table = {
    .initial_sp = _estack,
    .reset = Reset_Handler,
    .nmi = NMI_Handler,
    .hard_fault = HardFault_Handler,
    .reserved = {nullptr, nullptr, nullptr, nullptr},
    .sv_call = nullptr,
    .reserved_debug = nullptr,
    .reserved2 = nullptr,
    .pend_sv = nullptr,
    .sys_tick = SysTick_Handler
};

void Reset_Handler() noexcept {
    // 1. Копіювання секції .data за допомогою std::copy
    const auto data_size = reinterpret_cast<std::uintptr_t>(_edata) - reinterpret_cast<std::uintptr_t>(_sdata);
    const std::span<const std::uint32_t> data_flash{_sidata, data_size / sizeof(std::uint32_t)};
    const std::span<std::uint32_t> data_ram{_sdata, data_size / sizeof(std::uint32_t)};
    std::copy(data_flash.begin(), data_flash.end(), data_ram.begin());

    // 2. Обнулення секції .bss за допомогою std::fill
    const auto bss_size = reinterpret_cast<std::uintptr_t>(_ebss) - reinterpret_cast<std::uintptr_t>(_sbss);
    const std::span<std::uint32_t> bss_ram{_sbss, bss_size / sizeof(std::uint32_t)};
    std::fill(bss_ram.begin(), bss_ram.end(), 0U);

    // 3. Ініціалізація CCMRAM
    const auto ccm_size = reinterpret_cast<std::uintptr_t>(_eccmram) - reinterpret_cast<std::uintptr_t>(_sccmram);
    if (ccm_size > 0) {
        const std::span<const std::uint32_t> ccm_flash{_siccmram, ccm_size / sizeof(std::uint32_t)};
        const std::span<std::uint32_t> ccm_ram{_sccmram, ccm_size / sizeof(std::uint32_t)};
        std::copy(ccm_flash.begin(), ccm_flash.end(), ccm_ram.begin());
    }

    // 4. Виклик конструкторів статичних і глобальних об'єктів
    __libc_init_array();

    // 5. Виклик main()
    main();

    while (true) {
        asm volatile("wfi");
    }
}

void Default_Handler() noexcept {
    while (true) {
        asm volatile("wfi");
    }
}
```
:::

---

## 4. Збірка прошивки та аналіз карти пам'яті (`.map`)

Для компіляції та створення карти пам'яті використовується утиліта `arm-none-eabi-gcc` з ключами генерації звіту компонування:

```bash
# Компіляція сирцевих файлів у позиційно-незалежні об'єктні файли
arm-none-eabi-gcc -c -mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16 \
    -O2 -ffunction-sections -fdata-sections -Wall startup.c -o startup.o

arm-none-eabi-gcc -c -mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16 \
    -O2 -ffunction-sections -fdata-sections -Wall main.c -o main.o

# Компонування з використанням stm32f4.ld та генерацією firmware.map
arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16 \
    -Tstm32f4.ld -Wl,-Map=firmware.map,--cref,--gc-sections \
    -nostartfiles -o firmware.elf startup.o main.o
```

### Розбір фрагмента звіту `firmware.map`

Файл `.map` є головним документом верифікації компонування. У ньому відображено точний розподіл байтів:

```text
Memory Configuration

Name             Origin             Length             Attributes
FLASH            0x0000000008000000 0x0000000000080000 xr
RAM              0x0000000020000000 0x0000000000020000 xrw
CCMRAM           0x0000000010000000 0x0000000000010000 rw
*default*        0x0000000000000000 0xffffffffffffffff

Linker script and memory map

.isr_vector     0x0000000008000000       0x40
                0x0000000008000000                _isr_vector_start = .
 *(.isr_vector)
 .isr_vector    0x0000000008000000       0x40 startup.o
                0x0000000008000000                g_pfnVectors

.text           0x0000000008000040      0x3b0
 *(.text*)
 .text.Reset_Handler
                0x0000000008000040       0x4c startup.o
                0x0000000008000040                Reset_Handler
 .text.main     0x000000000800008c       0x58 main.o
                0x000000000800008c                main
                0x00000000080003f0                _etext = .

.data           0x0000000020000000       0x18 load address 0x00000000080003f0
                0x0000000020000000                _sdata = .
 .data.sensor_calib
                0x0000000020000000       0x10 main.o
                0x0000000020000000                sensor_calib
                0x0000000020000018                _edata = .
                0x00000000080003f0                _sidata = LOADADDR (.data)

.bss            0x0000000020000018      0x100
                0x0000000020000018                _sbss = .
 .bss.rx_buffer
                0x0000000020000018      0x100 main.o
                0x0000000020000018                rx_buffer
                0x0000000020000118                _ebss = .
```

Аналіз звіту карти пам'яті підтверджує такі ключові інваріанти архітектури:
1. **Зв'язок VMA та LMA для `.data`**: Секція `.data` має адресу виконання (VMA) `0x20000000`, але її фізична адреса завантаження (LMA) у Flash — `0x080003f0` (одразу після завершення секції коду `.text`). Це означає, що при прошиванні чипа початкові значення змінних ляжуть у Flash за адресою `0x080003f0`, а під час виконання стартовий код перенесе їх у RAM на `0x20000000`.
2. **Розрахунок вершини стека**: Стартовий покажчик стека `_estack` розраховано як `0x20000000 + 128K = 0x20020000`. При апаратному скиданні ядро автоматично зчитає це 32-бітне значення з нульової комірки Flash (`0x08000000`) і встановить його у регістр MSP.
3. **Ефективність оптимізатора**: Ключ `--gc-sections` видалив усі невикористані допоміжні функції з об'єктних файлів, але зберіг критично важливу секцію `.isr_vector` завдяки прямому використанню макроса `KEEP()`.

---

## 5. Інспекція символів та заголовків утилітами GNU Binutils

Для швидкої діагностики зібраного двійкового файлу `firmware.elf` використовуються утиліти бінарного аналізу.

### Перевірка заголовків секцій через `readelf`

Команда `arm-none-eabi-readelf -S firmware.elf` виводить таблицю всіх секцій ELF, їхні типи, розміри та прапорці:

```text
Section Headers:
  [Nr] Name              Type            Addr     Off    Size   ES Flg Lk Inf Al
  [ 1] .isr_vector       PROGBITS        08000000 010000 000040 00  AX  0   0  4
  [ 2] .text             PROGBITS        08000040 010040 0003b0 00  AX  0   0  4
  [ 3] .rodata           PROGBITS        080003f0 0103f0 000080 00   A  0   0  4
  [ 4] .data             PROGBITS        20000000 020000 000018 00  WA  0   0  4
  [ 5] .bss              NOBITS          20000018 020018 000100 00  WA  0   0  4
  [ 6] ._user_heap_stack NOBITS          20000118 020018 000c00 00  WA  0   0  8
```

Прапорці `Flg` вказують на режим обробки сегментів пам'яті:
* `A` (Alloc) — пам'ять під секцію повинна бути виділена під час завантаження;
* `X` (Execute) — секція містить виконуваний машинний код;
* `W` (Write) — секція доступна для запису під час виконання.

Секція `.bss` має тип `NOBITS` (не містить бітів у самому ELF-файлі на диску), оскільки на Flash її дані не зберігаються, а створюються динамічно в оперативній пам'яті під час виконання стартового коду.

### Сортування та аналіз символів через `nm`

Команда `arm-none-eabi-nm -n -S firmware.elf` виводить усі символи прошивки, відсортовані за зростанням числових адрес:

```text
08000000 00000040 D g_pfnVectors
08000040 0000004c T Reset_Handler
0800008c 00000058 T main
080003f0          A _sidata
20000000          A _sdata
20000000 00000010 D sensor_calib
20000018          A _edata
20000018          A _sbss
20000018 00000100 B rx_buffer
20000118          A _ebss
20020000          A _estack
```

Символи типу `A` (Absolute) — це маркери, визначені у скрипті компонувача (`_sdata`, `_edata`, `_sbss`, `_ebss`, `_estack`). Вони не мають фізичного розміру і слугують числовими орієнтирами для стартового коду процесора.

---

## 6. Типові пастки та крайові випадки розробки

Під час практичної розробки скриптів компонування та стартового коду для архітектури ARM Cortex-M розробники найчастіше стикаються з трьома критичними помилками:

1. **Невирівняні адреси копіювання `.data`**: Якщо секція `.data` або `.bss` закінчується за непарною адресою (наприклад, `0x20000013`), а цикл копіювання в `Reset_Handler` працює з 32-бітними словами (`uint32_t*`), то останнє звернення вийде за межі масиву або викличе апаратну помилку шини (Bus Fault / Usage Fault) через некратне вирівнювання покажчика. Завжди ставте `. = ALIGN(4);` як перед початком, так і після завершення кожної секції у скрипті компонувача.
2. **Видалення таблиці векторів оптимізатором**: Якщо у вихідному описі секції `.isr_vector` пропустити директиву `KEEP()`, то при використанні прапорця `-Wl,--gc-sections` компонувальник видалить весь масив векторів, оскільки жодна функція у C-програмі явно не викликає `g_pfnVectors`. У результаті процесор після скидання зчитає нульові значення і зависне у нескінченному циклі скидання.
3. **Приховане зіткнення стека й купи**: Якщо розмір глобальних масивів `.bss` зростає, динамічна купа починає перетинатися з областю стека. Використання жорстких перевірок `ASSERT` у скрипті гарантує, що компонувальник завчасно повідомить про переповнення пам'яті ще на етапі збірки, запобігаючи непередбачуваним збоям у роботі мікроконтролера в польових умовах.
