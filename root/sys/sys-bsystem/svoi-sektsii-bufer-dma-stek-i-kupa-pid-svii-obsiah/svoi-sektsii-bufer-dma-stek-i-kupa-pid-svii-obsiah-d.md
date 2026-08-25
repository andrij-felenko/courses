# Свої секції, буфер DMA, стек і купа під свій обсяг

<preknowlist>
- [Тулчейн](root:sys-bsystem/toolchain) — компілятор, асемблер, компонувальник і послідовність етапів збірки бінарного образу.
- [Map-файл](root:sys-bsystem/map-fail) — карта символів, секцій і розподілу адрес пам'яті компонувальником.
- [Прямий доступ до пам'яті (DMA)](root:hw-arch/dma) — апаратна передача блоків даних між периферією та RAM без участі процесора.
- [Когерентність кеша і DMA](root:hw-arch/cache-coherency-dma) — розсинхронізація даних між кешем ядра та фізичною оперативною пам'яттю.
- [Матриця шин](root:hw-arch/bus-matrix) — топологія багатошинних з'єднань між процесорними ядрами, контролерами DMA та різними банками RAM.
</preknowlist>

Коли типовий шаблон проєкту під мікроконтролер архітектури ARM Cortex-M або RISC-V компілюється зі стандартним скриптом компонувальника (*linker script*), пам'ять виглядає однорідною і простою: єдиний блок постійної пам'яті Flash та єдиний суцільний масив оперативної пам'яті RAM. Проте в реальних сучасних мікроконтролерах — таких як сімейства STM32H7, STM32F7 чи NXP i.MX RT — апаратна організація пам'яті є суворо гетерогенною. Фізичний кристал містить декілька незалежних доменів пам'яті: надшвидку пам'ять інструкцій ITCM (*Instruction Tightly-Coupled Memory*), пам'ять даних ядра DTCM (*Data Tightly-Coupled Memory*), загальну системну оперативну пам'ять AXI SRAM та окремі банки SRAM периферійних доменів D2 і D3.

Щойно у прошивці з'являється високонавантажена периферія — наприклад, контролер Ethernet, SD-карта на шині SDMMC через DMA, або графічний дисплей — наївна модель однорідної пам'яті призводить до важких апаратних збоїв. Якщо буфер приймання Ethernet розміром 1536 байтів випадково опиниться у пам'яті DTCM, апаратний блок DMA викличе BusFault або зависне, оскільки матриця системних шин фізично не з'єднує DMA-мастер мережевого контролера з приватною шиною ядра. Якщо на ядрі Cortex-M7 увімкнути кеш даних (*D-Cache*) і не вирівняти буфер передавання на розмір рядка кешу в 32 байти, інвалідація кешу після отримання пакета непомітно знищить змінні операційної системи, що випадково опинилися в тому ж рядку. А якщо динамічна купа (*heap*) безконтрольно росте назустріч низхідному стеку (*stack*), вони зіткнуться всередині оперативної пам'яті, руйнуючи покажчики повернення з функцій.

Усі ці проблеми вирішуються на рівні компонування прошивки. Скрипт компонувальника (файл із розширенням `.ld` у тулчейні GNU) формує фізичну топологію прошивки, призначає змінні та функції у цільові банки пам'яті, гарантує строге вирівнювання структур під вимоги кеш-пам'яті та встановлює апаратні й програмні бар'єри між стеком і купою.

![Розкладка пам'яті мікроконтролера](/root/sys/sys-bsystem/svoi-sektsii-bufer-dma-stek-i-kupa-pid-svii-obsiah/img/linker-memory-map.svg)

*Фізична топологія пам'яті: відповідність адрес завантаження (LMA) у постійній пам'яті Flash та адрес виконання (VMA) у незалежних доменах оперативної пам'яті DTCM, RAM_D1 та RAM_D2.*

## Анатомія скрипта компонувальника: блоки MEMORY та SECTIONS

Компонувальник GNU `ld` формує остаточний двійковий образ ELF (*Executable and Linkable Format*) з множини вхідних об'єктних файлів (`.o`), створених компілятором та асемблером. Кожен об'єктний файл містить власні секції коду, констант і даних. Робота компонувальника полягає у тому, щоб зібрати однотипні секції докупи, виділити для них неперервні діапазони фізичних адрес та розрахувати абсолютні значення всіх покажчиків і символів.

Цей процес керується двома фундаментальними блоками скрипта компонувальника: директивою `MEMORY` та директивою `SECTIONS`.

### Директива MEMORY: опис фізичного простору чипа

Блок `MEMORY` декларує фізично наявні в мікроконтролері банки пам'яті, вказуючи для кожного з них базову адресу (`ORIGIN`), граничну довжину (`LENGTH`) та список прав доступу:
- `r` — пам'ять доступна для читання (*read*);
- `w` — пам'ять доступна для запису (*write*);
- `x` — пам'ять містить виконуваний машинний код (*execute*).

Типова конфігурація для високопродуктивного мікроконтролера з багатодоменною шинною матрицею визначає незалежні регіони:

```ld
MEMORY
{
  ITCM_RAM (rwx) : ORIGIN = 0x00000000, LENGTH = 64K
  FLASH    (rx)  : ORIGIN = 0x08000000, LENGTH = 1024K
  DTCM_RAM (rwx) : ORIGIN = 0x20000000, LENGTH = 128K
  RAM_D1   (rwx) : ORIGIN = 0x24000000, LENGTH = 512K
  RAM_D2   (rwx) : ORIGIN = 0x30000000, LENGTH = 288K
  RAM_D3   (rwx) : ORIGIN = 0x38000000, LENGTH = 64K
}
```

У цій конфігурації кожен регіон має суворе апаратне призначення. Регіон `FLASH` зберігає незмінний двійковий код і константи. Регіон `ITCM_RAM` з'єднаний з ядром через шину I-TCM і забезпечує вибірку інструкцій із нульовою затримкою тактування. Регіон `DTCM_RAM` є найшвидшою оперативною пам'яттю для стека ядра та критичних обчислювальних структур. Регіони `RAM_D1` та `RAM_D2` розміщені на загальній системній шині AXI/AHB і доступні як ядру, так і автономним контролерам DMA.

### Директива SECTIONS та концепція VMA проти LMA

Блок `SECTIONS` описує правила розміщення вхідних секцій з об'єктних файлів у вихідні блоки пам'яті. На цьому етапі виникає принципове розмежування між двома типами адрес:

1. **VMA** (*Virtual / Execution Memory Address*) — адреса виконання. Це фізична адреса комірки пам'яті, за якою секція розташовується під час роботи прошивки і до якої процесор звертається за допомогою інструкцій завантаження (`LDR`), запису (`STR`) та переходів (`BL`).
2. **LMA** (*Load Memory Address*) — адреса завантаження. Це адреса у двійковому образі енергонезалежної пам'яті Flash, за якою початковий вміст секції зберігається до старту процесора.

Для незмінного машинного коду (`.text`), таблиці векторів переривань (`.isr_vector`) та константних даних (`.rodata`) адреси VMA та LMA ідентичні: вони зберігаються у Flash і виконуються безпосередньо з Flash (механізм XIP — *eXecute In Place*). У скрипті для них вказується однозначне призначення `> FLASH`.

Для глобальних змінних з ненульовими початковими значеннями (`.data`) виникає роздвоєння: початкові байти змінних повинні надійно зберігатися у Flash при вимкненому живленні, але під час виконання програми процесор повинен мати змогу читати і змінювати їх у швидкій оперативній пам'яті. Тому для секції `.data` адреса VMA належить оперативній пам'яті (`DTCM_RAM`), а адреса LMA — постійній пам'яті `FLASH`. У синтаксисі GNU `ld` це записується за допомогою оператора `AT>`:

```ld
SECTIONS
{
  /* Таблиця векторів переривань розміщується на початку Flash */
  .isr_vector :
  {
    . = ALIGN(4);
    KEEP(*(.isr_vector))
    . = ALIGN(4);
  } > FLASH

  /* Машинний код програми */
  .text :
  {
    . = ALIGN(4);
    *(.text)
    *(.text*)
    *(.glue_7)
    *(.glue_7t)
    *(.eh_frame)
    KEEP(*(.init))
    KEEP(*(.fini))
    . = ALIGN(4);
    _etext = .;
  } > FLASH

  /* Таблиці виклику конструкторів глобальних об'єктів C++ */
  .init_array :
  {
    . = ALIGN(4);
    PROVIDE_HIDDEN (__init_array_start = .);
    KEEP (*(SORT(.init_array.*)))
    KEEP (*(.init_array*))
    PROVIDE_HIDDEN (__init_array_end = .);
    . = ALIGN(4);
  } > FLASH

  /* Незмінні константи: рядкові літерали, lookup-таблиці */
  .rodata :
  {
    . = ALIGN(4);
    *(.rodata)
    *(.rodata*)
    . = ALIGN(4);
  } > FLASH

  /* Збереження адреси початку LMA-образу секції .data у Flash */
  _sidata = LOADADDR(.data);

  /* Секція ініціалізованих змінних: VMA в RAM, LMA у FLASH */
  .data :
  {
    . = ALIGN(4);
    _sdata = .;
    *(.data)
    *(.data*)
    . = ALIGN(4);
    _edata = .;
  } > DTCM_RAM AT> FLASH

  /* Секція неініціалізованих змінних: тільки VMA в RAM (обнуляється стартапом) */
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
  } > DTCM_RAM
}
```

У наведеному фрагменті застосовано кілька ключових інструментів компонувальника:
- Символ крапки `.` позначає поточний лічильник адреси (*location counter*). Призначення виразу лічильнику зсуває адресу наступного об'єкта.
- Функція `ALIGN(4)` вирівнює лічильник адреси вгору до найближчого числа, кратного 4 байтам, запобігаючи генерації нерозпізнаних апаратних помилок вирівнювання (*Alignment Faults*) при 32-бітних зверненнях.
- Функція `LOADADDR(.data)` повертає фізичну адресу LMA у пам'яті Flash, де компонувальник розмістив початкові байти ініціалізації для змінних секції `.data`.
- Директива `KEEP()` забороняє компонувальнику видаляти секцію під час роботи оптимізації прапорцем `--gc-sections` (видалення мертвого коду). Без `KEEP()` таблиця векторів переривань була б видалена, оскільки на неї немає прямих посилань із прикладного коду.
- Директива `PROVIDE_HIDDEN()` експортує глобальний символ для стартап-коду середовища C++, але обмежує його видимість межами поточного двійкового модуля.

### Стартап-ініціалізація пам'яті перед main()

Мікроконтролер не має вбудованої операційної системи, яка завантажувала б образи програм у пам'ять. Коли сигнал апаратного скидання Reset знімається, ядро зчитує з нульового зміщення Flash початкову вершину стека та адресу функції `Reset_Handler`.

До моменту виклику першої інструкції прикладного коду або конструктора C++ стартап-код зобов'язаний самостійно виконати дві низькорівневі операції:
1. Скопіювати байти секції `.data` з Flash (починаючи з адреси `_sidata`) у фізичну RAM (від `_sdata` до `_edata`).
2. Заповнити нульовими байтами весь діапазон пам'яті секції `.bss` (від `_sbss` до `_ebss`).
3. Для програм на C++ — викликати функцію ініціалізації середовища `__libc_init_array()`, яка по черзі виконує покажчики на конструктори глобальних і статичних об'єктів із секції `.init_array`.

:::tabs
```c
#include <stdint.h>

extern uint32_t _sidata; /* Початок образу .data у Flash (LMA) */
extern uint32_t _sdata;  /* Початок .data в RAM (VMA) */
extern uint32_t _edata;  /* Кінець .data в RAM (VMA) */
extern uint32_t _sbss;   /* Початок .bss в RAM (VMA) */
extern uint32_t _ebss;   /* Кінець .bss в RAM (VMA) */

extern void SystemInit(void);
extern void __libc_init_array(void);
extern int main(void);

void Reset_Handler(void) {
    uint32_t *src = &_sidata;
    uint32_t *dst = &_sdata;

    /* Копіювання початкових значень .data з Flash у RAM */
    while (dst < &_edata) {
        *dst++ = *src++;
    }

    /* Обнулення секції .bss */
    dst = &_sbss;
    while (dst < &_ebss) {
        *dst++ = 0U;
    }

    /* Ініціалізація тактування та базових шин */
    SystemInit();

    /* Виклик глобальних конструкторів середовища C/C++ */
    __libc_init_array();

    /* Перехід до основної логіки */
    main();

    /* Нескінченна пастка на випадок виходу з main */
    while (1) {
    }
}
```
```cpp
#include <cstdint>
#include <algorithm>
#include <span>

extern "C" {
    extern std::uint32_t _sidata;
    extern std::uint32_t _sdata;
    extern std::uint32_t _edata;
    extern std::uint32_t _sbss;
    extern std::uint32_t _ebss;

    void SystemInit() noexcept;
    void __libc_init_array() noexcept;
    int main();
}

namespace {

inline void copy_initialized_data() noexcept {
    const auto* src = &_sidata;
    auto* dst = &_sdata;
    const std::size_t count = static_cast<std::size_t>(&_edata - &_sdata);
    std::copy_n(src, count, dst);
}

inline void zero_uninitialized_bss() noexcept {
    auto* dst = &_sbss;
    const std::size_t count = static_cast<std::size_t>(&_ebss - &_sbss);
    std::fill_n(dst, count, 0U);
}

} // namespace

extern "C" void Reset_Handler() noexcept {
    copy_initialized_data();
    zero_uninitialized_bss();

    SystemInit();
    __libc_init_array();

    main();

    while (true) {
        // Пастка на випадок повернення
    }
}
```
:::

Якщо стартап-код буде скомпільовано без точної відповідності символам компонувальника або якщо розміри секцій не будуть кратними розміру слова (4 байти), цикл копіювання пошкодить перші змінні в пам'яті ще до того, як процесор виконає перший рядок функції `main()`.

> 🔧 **Навіщо це.** Розділення LMA та VMA дозволяє мікроконтролеру зберігати весь стан змінних у компактному енергонезалежному Flash-образі, а під час завантаження розгортати його у швидкісній оперативній пам'яті. Розуміння цієї моделі дозволяє переносити критичні функції у швидку пам'ять або ізолювати специфічні буфери для периферійних контролерів.

## Створення кастомних секцій для периферії, швидкого коду та енергонезалежних даних

Стандартні секції `.text`, `.rodata`, `.data` та `.bss` закривають потреби типових обчислень. Проте реальна вбудована система вимагає спеціалізованого розміщення даних у пам'яті:
- **Буфери дескрипторів DMA:** контролери Ethernet, SDMMC чи USB вимагають, щоб буфери лежали в доменах оперативної пам'яті, підключених до загальної матриці шин (наприклад, `RAM_D2` за адресою `0x30000000`), оскільки ядровий домен `DTCM` апаратно ізольований від периферійного DMA.
- **Швидкісні функції в RAM (*RAM Code*):** математичні алгоритми цифрової фільтрації або обробники високовольтних інверторів повинні виконуватися з пам'яті `ITCM_RAM` без тактів очікування (*zero wait-states*), тоді як Flash на високих частотах вимагає від 3 до 7 тактів затримки на кожну вибірку.
- **Енергонезалежні змінні (*No-Init RAM* / *Backup SRAM*):** дані журналу аварій або змінні обміну з завантажувачем (*bootloader*) не повинні затиратися нулями під час «теплого» перезавантаження мікроконтролера по Reset.

### Оголошення та властивості кастомних секцій у скрипті

Для створення нової секції вказується її ім'я, правила вирівнювання, цільовий банк пам'яті та спосіб завантаження:

```ld
SECTIONS
{
  /* 1. Секція для буферів DMA у домені RAM_D2 */
  .dma_buffer (NOLOAD) :
  {
    . = ALIGN(32);
    _sdma_buffer = .;
    *(.dma_buffer)
    *(.dma_buffer*)
    . = ALIGN(32);
    _edma_buffer = .;
  } > RAM_D2

  /* 2. Секція коду для виконання з надшвидкої пам'яті ITCM */
  _siram_code = LOADADDR(.ram_code);
  .ram_code :
  {
    . = ALIGN(4);
    _sram_code = .;
    *(.ram_code)
    *(.ram_code*)
    . = ALIGN(4);
    _eram_code = .;
  } > ITCM_RAM AT> FLASH

  /* 3. Секція змінних, що зберігають стан при перезавантаженні (No-Init) */
  .noinit (NOLOAD) :
  {
    . = ALIGN(4);
    *(.noinit)
    *(.noinit*)
    . = ALIGN(4);
  } > DTCM_RAM
}
```

Директива `(NOLOAD)` має вирішальне значення. Вона повідомляє компонувальнику, що секція описує пам'ять, початковий образ якої **не потрібно записувати у вихідний двійковий файл** (`.bin` або `.hex`). Без прапорця `(NOLOAD)` оголошення буфера DMA розміром 64 КБ призвело б до роздування бінарного образу прошивки на 64 КБ порожніх нулів, які програматор змушений був би довго прошивати у Flash.

Для розміщення змінних або функцій у кастомних секціях у вихідному коді застосовують атрибути компілятора GCC / Clang:

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

#define ETH_RX_BUFFER_SIZE 1536
#define ETH_RX_BUF_COUNT   4

/* Розміщення буферів у виділеній секції .dma_buffer з вирівнюванням на 32 байти */
__attribute__((section(".dma_buffer"), aligned(32)))
static uint8_t eth_rx_buffers[ETH_RX_BUF_COUNT][ETH_RX_BUFFER_SIZE];

/* Дескриптор кільцевого буфера DMA */
typedef struct {
    volatile uint32_t status;
    volatile uint32_t control;
    volatile uint32_t buffer_addr;
    volatile uint32_t next_desc;
} DmaDescriptor_t;

__attribute__((section(".dma_buffer"), aligned(32)))
static DmaDescriptor_t dma_rx_ring[ETH_RX_BUF_COUNT];

/* Змінна, що зберігає код перезавантаження між рестартами ядра */
__attribute__((section(".noinit")))
static uint32_t reset_reason_magic;

/* Функція, що виконується з надшвидкої пам'яті ITCM */
__attribute__((section(".ram_code"), noinline))
float Fast_Inverse_Sqrt(float x) {
    float xhalf = 0.5f * x;
    union { float f; uint32_t i; } conv = { .f = x };
    conv.i = 0x5f3759df - (conv.i >> 1);
    conv.f *= (1.5f - (xhalf * conv.f * conv.f));
    return conv.f;
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <bit>

namespace drivers {

inline constexpr std::size_t eth_rx_buffer_size = 1536;
inline constexpr std::size_t eth_rx_buf_count = 4;

struct alignas(32) DmaDescriptor {
    volatile std::uint32_t status{0};
    volatile std::uint32_t control{0};
    volatile std::uint32_t buffer_addr{0};
    volatile std::uint32_t next_desc{0};
};

// Буфери DMA у спеціалізованому домені RAM_D2
alignas(32) [[gnu::section(".dma_buffer")]]
static std::array<std::array<std::uint8_t, eth_rx_buffer_size>, eth_rx_buf_count> eth_rx_buffers;

alignas(32) [[gnu::section(".dma_buffer")]]
static std::array<DmaDescriptor, eth_rx_buf_count> dma_rx_ring;

// Змінна без ініціалізації для передачі стану через Reset
[[gnu::section(".noinit")]]
static std::uint32_t reset_reason_magic;

// Швидка математична функція в ITCM RAM
[[gnu::section(".ram_code"), gnu::noinline]]
float fast_inverse_sqrt(float x) noexcept {
    const float xhalf = 0.5f * x;
    std::uint32_t i = std::bit_cast<std::uint32_t>(x);
    i = 0x5f3759dfU - (i >> 1);
    float result = std::bit_cast<float>(i);
    result *= (1.5f - (xhalf * result * result));
    return result;
}

} // namespace drivers
```
:::

Для секції `.ram_code` стартап-код доповнюється ще одним циклом копіювання, який переносить байти машинного коду з адреси `_siram_code` у Flash за адресою `_sram_code` у пам'ять `ITCM_RAM` перед стартом `main()`.

## Вирівнювання та кеш-когерентність: небезпека False Sharing

Високопродуктивні процесорні ядра архітектур Cortex-M7 та Cortex-M55 оснащені дворівневим апаратним кешем даних (*L1 D-Cache*). Кеш-пам'ять оперує не поодинокими байтами чи 32-бітними словами, а дискретними блоками фіксованої довжини — **рядками кешу** (*cache lines*), розмір яких на ядрах Cortex-M7 становить рівно 32 байти.

Коли процесор виконує запис у пам'ять, D-Cache (якщо він налаштований у типовому режимі відкладеного запису — *Write-Back*) оновлює лише внутрішній рядок кешу, помічаючи його прапорцем модифікації (*dirty*). Фізична комірка у мікросхемі RAM залишається зі старим значенням до моменту витіснення або примусового скидання рядка.

Водночас периферійні контролери прямого доступу до пам'яті (DMA) взаємодіють з оперативною пам'яттю безпосередньо через системну шину, повністю оминаючи процесорний кеш. Це породжує дві взаємні проблеми когерентності даних:

1. **Передавання через DMA (TX):** Процесор сформував пакет у пам'яті, але свіжі байти залишилися у швидкому кеші ядра. Контролер DMA вичитує з фізичної RAM застарілі дані. Щоб уникнути цього, перед стартом DMA-транзакції процесор зобов'язаний виконати операцію скидання кешу (*Clean* / *Flush*): функція `SCB_CleanDCache_by_Addr()`.
2. **Приймання через DMA (RX):** Контролер DMA записав щойно прийнятий пакет у фізичну RAM. Якщо процесор звернеться до буфера, кеш ядра може повернути старі байти, які випадково опинилися в кеші раніше. Щоб уникнути цього, після завершення DMA-транзакції процесор зобов'язаний виконати операцію інвалідації кешу (*Invalidate*): функція `SCB_InvalidateDCache_by_Addr()`.

![Когерентність D-Cache і DMA](/root/sys/sys-bsystem/svoi-sektsii-bufer-dma-stek-i-kupa-pid-svii-obsiah/img/dma-cache-alignment.svg)

*Проблема хибного спільного використання (False Sharing): якщо буфер DMA не вирівняний на 32 байти або його довжина не кратна розміру рядка кешу, інвалідація та скидання кешу пошкоджують сусідні змінні ядра.*

### Механізм апаратної катастрофи: False Sharing

Найбільш підступний дефект виникає тоді, коли буфер DMA не вирівняний на межу 32 байтів або його розмір не кратний 32 байтам.

Розглянемо практичний випадок: буфер приймання DMA `dma_rx_buf[64]` розташований за адресою `0x20000004`, а за адресою `0x20000000` компілятор випадково поклав системний прапорець операційної системи `uint32_t os_task_flags`. Обидві змінні ділять спільний 32-байтний рядок кешу (діапазон адрес від `0x20000000` до `0x2000001F`).

Послідовність руйнування даних розгортається наступним чином:
1. Процесор оновлює стан операційної системи: `os_task_flags |= TASK_READY`. Рядок кешу `0x20000000..0x2000001F` стає «брудним» (*dirty*).
2. Зовнішній контролер DMA приймає мережевий пакет і записує байти у фізичну RAM за адресою `0x20000004..0x20000043`.
3. Обробник переривання DMA викликає функцію інвалідації: `SCB_InvalidateDCache_by_Addr(0x20000004, 64)`.
4. Оскільки апаратна інвалідація оперує тільки повними рядками кешу, процесор викидає весь перший рядок `0x20000000..0x2000001F`. Модифіковане значення `os_task_flags` безслідно знищується, і операційна система пропускає подію перемикання задачі!
5. Зворотний сценарій: якби процесор викликав `SCB_CleanDCache` над сусідньою змінною, кеш ядра примусово виштовхнув би свої застарілі байти `0x20000004..0x2000001F` у RAM, затерши початок щойно прийнятого мережевого кадру!

Цей ефект називається **хибним спільним доступом** (*false sharing*).

### Захист на рівні скрипта компонування та MPU

Щоб повністю унеможливити False Sharing, діє непорушний інженерний стандарт: **кожен буфер або масив дескрипторів DMA повинен починатися з адреси, строго кратної 32 байтам (`ALIGN(32)`), і мати розмір, доповнений до цілого числа, кратного 32 байтам**.

Якщо постійне ручне керування кешем через `SCB_CleanDCache` та `SCB_InvalidateDCache` створює накладні витрати часу або підвищує ризик людської помилки, застосовують апаратний модуль захисту пам'яті (*MPU — Memory Protection Unit*).

Через MPU весь домен пам'яті `RAM_D2` (адреса `0x30000000`) конфігурується як звичайна некешована пам'ять (*Normal Non-Cacheable*):

:::tabs
```c
#include <stdint.h>

/* Регістри блоку MPU для архітектури ARMv7-M (Cortex-M7) */
#define MPU_TYPE_REG  (*(volatile uint32_t*)0xE000ED90)
#define MPU_CTRL_REG  (*(volatile uint32_t*)0xE000ED94)
#define MPU_RNR_REG   (*(volatile uint32_t*)0xE000ED98)
#define MPU_RBAR_REG  (*(volatile uint32_t*)0xE000ED9C)
#define MPU_RASR_REG  (*(volatile uint32_t*)0xE000EDA0)

void MPU_Configure_NonCacheable_D2(void) {
    /* Тимчасове вимкнення MPU */
    MPU_CTRL_REG = 0;

    /* Вибір слота регіону MPU № 0 */
    MPU_RNR_REG = 0;
    
    /* Базова адреса регіону: 0x30000000 (RAM_D2) */
    MPU_RBAR_REG = 0x30000000;

    /*
     * Налаштування бітів RASR (Region Attribute and Size Register):
     * XN = 1 (заборона виконання коду в буферах даних)
     * AP = 011 (повний доступ ядра на читання та запис)
     * TEX = 001, C = 0, B = 0 (Normal Non-Cacheable, Non-Shareable)
     * SIZE = 0x12 (розмір 2^(18+1) = 512 КБ, що покриває 288 КБ RAM_D2)
     * ENABLE = 1
     */
    MPU_RASR_REG = (1UL << 28) | (3UL << 24) | (1UL << 19) | (18UL << 1) | 1UL;

    /* Увімкнення MPU з збереженням фонової карти адрес (PRIVDEFENA) */
    MPU_CTRL_REG = (1UL << 2) | (1UL << 0);

    /* Бар'єри пам'яті для синхронізації конфігурації */
    __builtin_arm_dsb(15);
    __builtin_arm_isb(15);
}
```
```cpp
#include <cstdint>

namespace mpu {

struct HardwareMpu {
    volatile std::uint32_t type;
    volatile std::uint32_t ctrl;
    volatile std::uint32_t rnr;
    volatile std::uint32_t rbar;
    volatile std::uint32_t rasr;
};

inline auto& hardware_mpu = *reinterpret_cast<HardwareMpu*>(0xE000ED90);

void setup_non_cacheable_d2_region() noexcept {
    hardware_mpu.ctrl = 0; // Вимкнути MPU перед модифікацією

    hardware_mpu.rnr = 0;             // Регіон № 0
    hardware_mpu.rbar = 0x30000000U;  // Базова адреса RAM_D2

    // XN=1, AP=RW (3), Non-cacheable (TEX=1, C=0, B=0), Size=512KB (18), Enable=1
    constexpr std::uint32_t rasr_config = 
        (1U << 28) | (3U << 24) | (1U << 19) | (18U << 1) | 1U;
    hardware_mpu.rasr = rasr_config;

    // Увімкнути MPU з бітом PRIVDEFENA (фонова адресація для решти Flash/RAM)
    hardware_mpu.ctrl = (1U << 2) | (1U << 0);

    asm volatile("dsb 0xf\nisb 0xf" ::: "memory");
}

} // namespace mpu
```
:::

Після активації цього регіону MPU процесорні звернення до секції `.dma_buffer` проходять повз D-Cache, гарантуючи повну апаратну когерентність між ядром та DMA без додаткових інструкцій скидання.

## Організація оперативної пам'яті: стек, купа та ключові символи компонувальника

Основна оперативна пам'ять мікроконтролера (наприклад, банк `DTCM_RAM` або `RAM_D1`) ділиться між чотирма сутностями:
1. **Секція `.data`** — розміщується з молодших адрес оперативної пам'яті.
2. **Секція `.bss`** — розміщується безпосередньо за `.data`.
3. **Купа (Heap)** — простір динамічної пам'яті для викликів `malloc()`, `calloc()` та оператора C++ `new`. Вона починається відразу за межею `.bss` (символ `_ebss` або `end`) і зростає у бік старших адрес.
4. **Стек (Stack)** — пам'ять під локальні змінні, кадри функцій та контексти збереження регістрів при виклику переривань. На архітектурах ARM Cortex-M та RISC-V реалізовано низхідний стек (*Full Descending Stack*): покажчик вершини стека (*Stack Pointer — SP*) ініціалізується найвищою адресою банку пам'яті (`_estack`) і при кожному виклику функції рухається вниз — назустріч купі.

![Організація оперативної пам'яті та захист _sbrk](/root/sys/sys-bsystem/svoi-sektsii-bufer-dma-stek-i-kupa-pid-svii-obsiah/img/stack-heap-layout.svg)

*Зустрічний рух купи та стека в оперативній пам'яті: межі `_Min_Heap_Size`, `_Min_Stack_Size`, захисний бар'єр та перевірка вільних адрес.*

### Конфігурація розмірів та статична валідація пам'яті

Розміри гарантованого запасу під купу та стек задаються змінними на початку скрипта компонувальника:

```ld
/* Мінімальний гарантований обсяг під купу та стек */
_Min_Heap_Size = 0x800;   /* 2 КБ під динамічну пам'ять */
_Min_Stack_Size = 0x1000; /* 4 КБ під стек ядра та переривань */

/* Вершина стека — найвища адреса регіону DTCM_RAM */
_estack = ORIGIN(DTCM_RAM) + LENGTH(DTCM_RAM);
```

Щоб компонувальник ще під час збірки перевірив, чи фізично помістяться всі статичні дані разом із запитаним обсягом стека й купи у фізичний кристал, у кінець блоку `SECTIONS` додають секцію статичної верифікації:

```ld
SECTIONS
{
  /* ... попередні секції (.text, .rodata, .data, .bss) ... */

  ._user_heap_stack :
  {
    . = ALIGN(8);
    PROVIDE(end = .);
    PROVIDE(_end = .);
    . = . + _Min_Heap_Size;
    . = . + _Min_Stack_Size;
    . = ALIGN(8);
  } > DTCM_RAM

  /* Якщо сумарний обсяг перевищує фізичну пам'ять — зупинити збірку */
  ASSERT(. <= ORIGIN(DTCM_RAM) + LENGTH(DTCM_RAM), 
         "ПОМИЛКА: Недостатньо пам'яті DTCM_RAM для розміщення статичних даних, купи та стека!")
}
```

Директива `ASSERT` перетворює небезпечну плаваючу помилку під час виконання на жорстку помилку компонування. Якщо після додавання нових глобальних масивів пам'ять буде вичерпана, компіляція зупиниться з точним повідомленням про дефіцит байтів.

## Захист від фатального зіткнення стека й купи: системний виклик `_sbrk()`

Динамічне виділення пам'яті через стандартні бібліотеки C/C++ (`newlib`, `newlib-nano`) спирається на низькорівневий системний виклик `_sbrk(ptrdiff_t incr)`. Його призначення — зсувати поточну верхню межу виділеного пулу купи (*break pointer*) на `incr` байтів вгору.

У багатьох застарілих прикладах `_sbrk` реалізовано без жодної перевірки меж:

:::tabs
```c
/* НАЇВНА І НЕБЕЗПЕЧНА РЕАЛІЗАЦІЯ — НЕ ВИКОРИСТОВУВАТИ */
void* _sbrk_unsafe(ptrdiff_t incr) {
    extern char end; /* Символ кінця .bss зі скрипта компонувальника */
    static char *heap_end = NULL;
    char *prev_heap_end;

    if (heap_end == NULL) {
        heap_end = &end;
    }
    prev_heap_end = heap_end;
    heap_end += incr;
    return (void*)prev_heap_end;
}
```
```cpp
// НАЇВНА І НЕБЕЗПЕЧНА РЕАЛІЗАЦІЯ — НЕ ВИКОРИСТОВУВАТИ
extern "C" {
    extern char end;

    void* _sbrk_unsafe_cpp(std::ptrdiff_t incr) noexcept {
        static char* heap_end = &end;
        char* prev_heap_end = heap_end;
        heap_end += incr;
        return prev_heap_end;
    }
}
```
:::

Така реалізація є джерелом фатальних збоїв. Коли купа переповнюється, `heap_end` перетинає межу активного стека. Наступний виклик `malloc` повертає адресу всередині стекових кадрів, і запис у виділений буфер затирає локальні змінні та адреси повернення функцій у стеку, викликаючи невідтворюваний HardFault.

### Надійна реалізація `_sbrk` з подвійним бар'єром захисту

Надійна реалізація зобов'язана одночасно перевіряти два критерії безпеки:
1. **Динамічний бар'єр:** Нова межа купи `heap_end + incr` не повинна перевищувати поточне значення апаратного покажчика стека `SP` (зчитується з регістру `MSP` через інструкцію `MRS`).
2. **Гарантований статичний бар'єр:** Нова межа купи не повинна заходити у зарезервований простір під стек `_estack - _Min_Stack_Size`, навіть якщо в поточну мить стек не заглиблений (оскільки переривання з високим пріоритетом може виникнути будь-якої миті).

Якщо пам'ять вичерпана, функція встановлює код помилки `errno = ENOMEM` і повертає значення `(void*)-1`:

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <errno.h>

#undef errno
extern int errno;

/* Символи зі скрипта компонувальника */
extern uint8_t end;
extern uint8_t _estack;
extern uint32_t _Min_Stack_Size;

/* Читання поточного значення апаратного покажчика стека (MSP) */
static inline uint32_t read_current_msp(void) {
    uint32_t result;
    __asm volatile("mrs %0, msp" : "=r"(result));
    return result;
}

void* _sbrk(ptrdiff_t incr) {
    static uint8_t *heap_end = NULL;
    uint8_t *prev_heap_end;

    if (heap_end == NULL) {
        heap_end = &end;
    }

    prev_heap_end = heap_end;
    uint8_t *next_heap_end = heap_end + incr;

    /* Зчитування поточного динамічного стека */
    uint32_t current_sp = read_current_msp();

    /* Розрахунок статичної межі безпеки під стек */
    uint8_t *stack_boundary = (uint8_t*)(&_estack) - (uint32_t)(&_Min_Stack_Size);

    /* 
     * Перевірка двох умов:
     * 1. Чи не наздогнала купа поточний активний стек SP
     * 2. Чи не зайшла купа в гарантований резерв стека переривань
     */
    if ((next_heap_end > (uint8_t*)current_sp) || (next_heap_end > stack_boundary)) {
        errno = ENOMEM;
        return (void*)-1;
    }

    heap_end = next_heap_end;
    return (void*)prev_heap_end;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <cerrno>

extern "C" {
    extern std::uint8_t end;
    extern std::uint8_t _estack;
    extern std::uint32_t _Min_Stack_Size;

    void* _sbrk(std::ptrdiff_t incr) noexcept;
}

namespace sys {

[[nodiscard]] inline std::uintptr_t read_current_msp() noexcept {
    std::uintptr_t sp_value;
    asm volatile("mrs %0, msp" : "=r"(sp_value));
    return sp_value;
}

class CollisionSafeHeap {
public:
    static void* allocate(std::ptrdiff_t incr) noexcept {
        static std::uint8_t* heap_end = &end;

        auto* prev_heap_end = heap_end;
        auto* next_heap_end = heap_end + incr;

        const auto active_sp = read_current_msp();
        const auto* stack_boundary = &_estack - reinterpret_cast<std::uintptr_t>(&_Min_Stack_Size);

        // Перевірка обох бар'єрів
        if ((next_heap_end > reinterpret_cast<const std::uint8_t*>(active_sp)) || 
            (next_heap_end > stack_boundary)) {
            errno = ENOMEM;
            return reinterpret_cast<void*>(-1);
        }

        heap_end = next_heap_end;
        return prev_heap_end;
    }
};

} // namespace sys

extern "C" void* _sbrk(std::ptrdiff_t incr) noexcept {
    return sys::CollisionSafeHeap::allocate(incr);
}
```
:::

### Патерни детермінованого виділення пам'яті в C++

У вбудованих системах реального часу стандартний `malloc` і глобальний `new` несуть критичний ризик **фрагментації пам'яті**: після тривалої роботи системи купа розбивається на дрібні ізольовані фрагменти, і виділення навіть невеликого неперервного буфера зазнає невдачі.

У сучасному C++17 для уникнення фрагментації застосовують поліморфні ресурси пам'яті (*PMR — Polymorphic Memory Resources*). Буфер виділяється всередині спеціалізованої секції пам'яті (наприклад, у `RAM_D2`), а контейнери `std::pmr::vector` працюють виключно всередині локального монотонного алокатора:

:::tabs
```c
#include <stdint.h>
#include <stddef.h>

/* Фіксований статичний пул блоків у кастомній секції */
#define BLOCK_SIZE_BYTES  64
#define TOTAL_BLOCKS_NUM  32

__attribute__((section(".dma_buffer"), aligned(4)))
static uint8_t block_memory_pool[TOTAL_BLOCKS_NUM][BLOCK_SIZE_BYTES];
static uint32_t block_allocation_mask = 0;

void* FixedPool_Allocate(void) {
    for (uint32_t i = 0; i < TOTAL_BLOCKS_NUM; ++i) {
        if (!(block_allocation_mask & (1UL << i))) {
            block_allocation_mask |= (1UL << i);
            return (void*)&block_memory_pool[i][0];
        }
    }
    return NULL; /* Пам'ять у пулі вичерпана */
}

void FixedPool_Free(void *ptr) {
    if (ptr == NULL) return;
    ptrdiff_t offset = (uint8_t*)ptr - &block_memory_pool[0][0];
    uint32_t index = (uint32_t)(offset / BLOCK_SIZE_BYTES);
    if (index < TOTAL_BLOCKS_NUM) {
        block_allocation_mask &= ~(1UL << index);
    }
}
```
```cpp
#include <cstdint>
#include <array>
#include <memory_resource>
#include <vector>

namespace memory {

// Фіксований буфер у спеціалізованому домені RAM_D2
alignas(32) [[gnu::section(".dma_buffer")]]
static std::array<std::byte, 16384> telemetry_dma_pool;

void process_sensor_packet() {
    // Монотонний алокатор, що працює виключно всередині масиву telemetry_dma_pool
    std::pmr::monotonic_buffer_resource pool_resource(
        telemetry_dma_pool.data(),
        telemetry_dma_pool.size(),
        std::pmr::null_memory_resource() // Заборона звернення до глобальної купи
    );

    // Вектор гарантовано розміщується у виділеному домені RAM_D2
    std::pmr::vector<std::uint32_t> packet_data(&pool_resource);
    packet_data.reserve(512);

    for (std::uint32_t i = 0; i < 256; ++i) {
        packet_data.push_back(i * 15U);
    }

    // При виході з функції вся пам'ять звільняється миттєвим скиданням покажчика
}

} // namespace memory
```
:::

## Контрольний інженерний чекліст валідації компонування

Перед фінальним випуском прошивки та під час діагностики складних збоїв пам'яті перевіряють наступний контрольний список:

1. **Аналіз Map-файлу:** Згенерувати файл карти (`-Wl,-Map=output.map`) і перевірити секцію `Linker script and memory map`. Переконатися, що всі структури з атрибутом `__attribute__((section(".dma_buffer")))` потрапили саме у вихідну секцію `.dma_buffer`, а не звалилися у загальний `.bss` через друкарську помилку в імені атрибута.
2. **Звірка з таблицею Bus Matrix:** Порівняти адреси буферів DMA з апаратною таблицею матриці шин у даташиті мікроконтролера. Якщо буфер Ethernet чи SDMMC опинився за адресою `0x20000000` (DTCM), зв'язок апаратно заблоковано на рівні кремнію.
3. **Перевірка вирівнювання кешу:** Переконатися, що для кожного буфера DMA виконано дві умови: адреса початку кратна 32 байтам (`addr % 32 == 0`), а розмір також ділиться на 32 без залишку (`size % 32 == 0`).
4. **Статичний бар'єр у скрипті:** Перевірити наявність директиви `ASSERT` у файлі `.ld` для перевірки `_ebss + _Min_Heap_Size + _Min_Stack_Size <= ORIGIN(RAM) + LENGTH(RAM)`.
5. **Водяні знаки стека (Stack Watermarking):** Під час стартапу заповнити всю область стека від `_ebss + _Min_Heap_Size` до `_estack` магічним байтом `0xA5`. Після стрес-тестування системи перевірити, яка кількість байтів `0xA5` залишилася незмінною знизу стека — це дає точну реальну оцінку глибини стека під час переривань.
