# 📋 Двійкові структури та заголовки таблиць ACPI

Під час завантаження ядра Linux підсистема ACPICA розбирає сирі бінарні блоки пам'яті, передані UEFI або Legacy BIOS. Кожна статична та динамічна таблиця ACPI складається з фіксованого заголовка та специфічного тіла структури. Для розробників системного програмного забезпечення, підсистеми ініціалізації та низькоуровневих драйверів розуміння точності вирівнювання (alignment), байтових зсувів (offsets) та сигнатур є фундаментальним. Цей матеріал містить вичерпний технічний довідник C/C++ структур для RSDP, SDT Header, FADT, MADT та Generic Address Structure (GAS).

Усі таблиці ACPI використовують прямий порядок байтів (Little Endian). Усі поля розміром у 16, 32 або 64 біти зберігаються безпосередньо у низькопорядовому форматі процесорів x86/ARM64. Якщо ядро працює на платформі з протилежним порядком байтів, підсистема ACPICA виконує автоматичну конверсію значень під час побудови дерева простору імен.

## 1. Root System Description Pointer (RSDP)

Структура RSDP є початковим якорем підсистеми ACPI у фізичній пам'яті комп'ютера. Вона не є системною таблицею в класичному розумінні, оскільки не має стандартного заголовка `ACPI_TABLE_HEADER`, а слугує лише вказівником на таблицю RSDT або XSDT.

### Сигнатура, вирівнювання та версійність

Структура RSDP завжди вирівнюється на межу 16 байтів (16-byte boundary). Перші 8 байтів містять суворо зафіксовану сигнатуру ASCII `"RSD PTR "` (з обов'язковим пробілом у 8-й позиції). 

У версії ACPI 1.0 структура мала фіксований розмір 20 байтів і підтримувала лише 32-бітну фізичну адресу таблиці RSDT. У специфікації ACPI 2.0 структуру було розширено до 36 байтів для додавання 64-бітного поля адреси XSDT, необхідного для систем з обсягом оперативної пам'яті понад 4 Гігабайти.

Таблиця RSDP містить два окремих поля контрольної суми:
1. **`checksum` (байт 9):** Контрольна сума перших 20 байтів структури (версія ACPI 1.0).
2. **`extended_checksum` (байт 32):** Контрольна сума всіх 36 байтів структури (версія ACPI 2.0+).

:::tabs
```c
/* C Definition (Linux Kernel uapi style) */
#include <stdint.h>

#pragma pack(push, 1)

struct rsdp_descriptor_v1 {
    char     signature[8];     /* "RSD PTR " */
    uint8_t  checksum;         /* Сума перших 20 байтів = 0 */
    char     oem_id[6];        /* Ідентифікатор виробника OEM */
    uint8_t  revision;         /* 0 = ACPI 1.0, 2 = ACPI 2.0+ */
    uint32_t rsdt_physical_address; /* 32-бітна адреса RSDT */
};

struct rsdp_descriptor_v2 {
    struct rsdp_descriptor_v1 v1;
    uint32_t length;           /* Загальний розмір структури (36 байтів) */
    uint64_t xsdt_physical_address; /* 64-бітна адреса XSDT */
    uint8_t  extended_checksum;/* Сума всіх 36 байтів = 0 */
    uint8_t  reserved[3];      /* Зарезервовані байти */
};

#pragma pack(pop)
```
```cpp
// C++ Idiomatic Definition (C++20 layout)
#include <cstdint>
#include <array>
#include <span>

#pragma pack(push, 1)

struct alignas(1) RsdpDescriptorV1 {
    std::array<char, 8> signature;     // "RSD PTR "
    std::uint8_t        checksum;      // Checksum of first 20 bytes
    std::array<char, 6> oem_id;        // OEM String
    std::uint8_t        revision;      // 0 for v1.0, 2 for v2.0+
    std::uint32_t       rsdt_address;  // 32-bit physical address
};

struct alignas(1) RsdpDescriptorV2 {
    RsdpDescriptorV1  v1;
    std::uint32_t     length;          // 36 bytes
    std::uint64_t     xsdt_address;    // 64-bit physical address
    std::uint8_t      extended_checksum; // Checksum of entire 36 bytes
    std::array<std::uint8_t, 3> reserved;
};

#pragma pack(pop)
```
:::

Поле `revision` визначає версію стандарту: значення `0` відповідає ACPI 1.0, а значення `2` відповідає специфікаціям ACPI від 2.0 до 6.5. Поле `oem_id` містить 6-символьний рядок у форматі ASCII із назвою розробника прошивки (наприклад, `"DELL  "`, `"INTEL "`, `"ALASKA"`).

## 2. Загальний заголовок системних таблиць (ACPI SDT Header)

Кожна системна таблиця ACPI (RSDT, XSDT, FADT, MADT, MCFG, DSDT, SSDT, SRAT, SLIT) починається зі стандартного 36-байтового заголовка `ACPI_TABLE_HEADER`. Цей заголовок гарантує уніфікований спосіб валідації та обходу таблиць під час первинного розбору.

### Деталізація полів заголовка

1. **`signature` (4 байти):** 4-символьний ASCII-ідентифікатор таблиці (наприклад, `"FACP"` для FADT, `"APIC"` для MADT, `"MCFG"` для PCI Express, `"DSDT"` для головної таблиці опису платформи).
2. **`length` (4 байти):** Повна довжина всієї таблиці у байтах, включаючи самі 36 байтів заголовка та вкладене тіло структури.
3. **`revision` (1 байт):** Ревізія специфікації даної конкретної таблиці. Дозволяє ядру підтримувати зворотну сумісність при появі нових полів у новіших ревізіях прошивки.
4. **`checksum` (1 байт):** Контрольна сума всієї таблиці. Обчислюється таким чином, щоб сума всіх байтів таблиці за модулем 256 дорівнювала нулю.
5. **`oem_id` (6 байтів):** Ідентифікатор виробника обладнання OEM.
6. **`oem_table_id` (8 байтів):** Ідентифікатор конкретної моделі материнської плати або версії BIOS, наданий виробником.
7. **`oem_revision` (4 байти):** Внутрішній номер версії ревізії таблиці від OEM-виробника.
8. **`asl_compiler_id` (4 байти):** Сигнатура компілятора, який згенерував цю таблицю (наприклад, `"INTL"` для Intel iASL Компілятора або `"MSFT"` для компілятора Microsoft).
9. **`asl_compiler_revision` (4 байти):** Номер версії компілятора ASL.

:::tabs
```c
/* C Definition */
#include <stdint.h>

#pragma pack(push, 1)

struct acpi_table_header {
    char     signature[4];     /* Наприклад "FACP", "APIC", "DSDT" */
    uint32_t length;           /* Довжина всієї таблиці включно із заголовком */
    uint8_t  revision;         /* Версія специфікації цієї таблиці */
    uint8_t  checksum;         /* Сума всіх байтів таблиці = 0 */
    char     oem_id[6];        /* OEM ID */
    char     oem_table_id[8];  /* Table ID виробника */
    uint32_t oem_revision;     /* Версія таблиці OEM */
    char     asl_compiler_id[4]; /* Сигнатура компілятора iASL */
    uint32_t asl_compiler_revision; /* Версія компілятора */
};

#pragma pack(pop)
```
```cpp
// C++ Idiomatic Definition
#include <cstdint>
#include <array>

#pragma pack(push, 1)

struct alignas(1) AcpiTableHeader {
    std::array<char, 4> signature;     // 4-char signature
    std::uint32_t       length;        // Total table size in bytes
    std::uint8_t        revision;      // Table revision
    std::uint8_t        checksum;      // Entire table checksum (sum % 256 == 0)
    std::array<char, 6> oem_id;        // OEM ID
    std::array<char, 8> oem_table_id;  // OEM Table ID
    std::uint32_t       oem_revision;  // OEM Revision number
    std::array<char, 4> asl_compiler_id; // Compiler ID (e.g. "INTL")
    std::uint32_t       asl_compiler_revision;
};

#pragma pack(pop)
```
:::

## 3. Generic Address Structure (GAS)

У версії ACPI 1.0 адреси регістрів у таблицях описувалися сирими 16-бітними номерами I/O портів x86. Для підтримки 64-бітних адрес пам'яті (MMIO), PCI Config Space та специфічних шин у специфікації ACPI 2.0 було представлено універсальну структуру адресації **GAS (Generic Address Structure)**.

### Анатомія структури GAS

Структура GAS має фіксований розмір 12 байтів та визначає тип простору, фізичну адресу та правила бітового доступу до регістра:

* **`space_id` (1 байт):** Визначає тип адресної системи:
  * `0`: SystemMemory (Фізична оперативна пам'ять / MMIO).
  * `1`: SystemIO (Простір портів вводу-виводу x86 I/O ports).
  * `2`: PCI_Config (Конфігураційний простір шини PCI).
  * `3`: EmbeddedControl (Регістри вбудованого мікроконтролера EC).
  * `4`: SMBus (Шина System Management Bus).
  * `5`: SystemCMOS (Пам'ять CMOS/RTC).
  * `6`: PciBarTarget (Базовий адресний регістр PCI BAR).
  * `7`: IPMI (Інтерфейс Intelligent Platform Management Interface).
  * `8`: GeneralPurposeIO (Лінії GPIO).
  * `9`: GenericSerialBus (Серійні шини I2C, SPI, UART).
* **`bit_width` (1 байт):** Розмір регістра у бітах (наприклад, 8, 16, 32 або 64 біти).
* **`bit_offset` (1 байт):** Бітовий зсув всередині вибраного цільового регістра.
* **`access_width` (1 байт):** Код атомного розміру доступу: `0` = Незначено, `1` = Byte access (8 біт), `2` = Word access (16 біт), `3` = DWord access (32 біти), `4` = QWord access (64 біти).
* **`address` (8 байтів):** 64-бітна фізична адреса або номер I/O порта/PCI адреса.

:::tabs
```c
/* C Definition */
#include <stdint.h>

#pragma pack(push, 1)

struct acpi_generic_address {
    uint8_t  space_id;    /* 0=SystemMemory, 1=SystemIO, 2=PCI_Config, 3=EC */
    uint8_t  bit_width;   /* Розмір регістра у бітах (8, 16, 32, 64) */
    uint8_t  bit_offset;  /* Зсув першого біта */
    uint8_t  access_width;/* Розмір доступу: 0=Undefined, 1=Byte, 2=Word, 3=DWord, 4=QWord */
    uint64_t address;     /* 64-бітна фізична адреса або I/O порт */
};

#pragma pack(pop)
```
```cpp
// C++ Idiomatic Definition
#include <cstdint>

#pragma pack(push, 1)

enum class AcpiAddressSpace : std::uint8_t {
    SystemMemory     = 0,
    SystemIO         = 1,
    PciConfig        = 2,
    EmbeddedControl  = 3,
    SmBus            = 4,
    SystemCmos       = 5,
    PciBarTarget     = 6,
    IPMI             = 7,
    GeneralPurposeIo = 8,
    GenericSerialBus = 9
};

struct alignas(1) AcpiGenericAddress {
    AcpiAddressSpace space_id;
    std::uint8_t     bit_width;
    std::uint8_t     bit_offset;
    std::uint8_t     access_width;
    std::uint64_t    address;
};

#pragma pack(pop)
```
:::

## 4. Fixed ACPI Description Table (FADT / FACP)

Таблиця FADT є фундаментальним центром статичної конфігурації. Вона передає ядру адреси фіксованих апаратних регістрів ACPI, вказівники на DSDT і FACS, а також архітектурні прапорці платформи.

### Важливі байтові зсуви у FADT

* `Offset 0x28 (40)`: 32-бітна адреса структури `FACS` (Firmware ACPI Control Structure), де зберігається вектор відновлення з режиму сну S3 (`Firmware_Waking_Vector`).
* `Offset 0x2C (44)`: 32-бітна фізична адреса головної динамічної таблиці `DSDT`.
* `Offset 0x30 (48)`: Порт `SMI_CMD`. Запис байта `ACPI_ENABLE` у цей порт змушує прошивку SMM перевести чіпсет з режимів APM/Legacy в режим ACPI.
* `Offset 0x38 (56)`: Порт `PM1a_EVT_BLK`. Блок регістрів статусу та увімкнення подій сну і таймера.
* `Offset 0x40 (64)`: Порт `PM1a_CNT_BLK`. Блок регістрів керування станами сну (вибір поля `SLP_TYPa` та запис біта `SLP_EN`).
* `Offset 0x4C (76)`: Порт `PM_TMR_BLK`. 24-бітний або 32-бітний апаратний таймер ACPI з частотою 3.579545 МГц.
* `Offset 0x56 (86)`: Порт `GPE0_BLK`. Базова адреса регістрів статусу та маскування загальних подій GPE.
* `Offset 0x8C (140)`: 64-бітна адреса `X_FACS`.
* `Offset 0x94 (148)`: 64-бітна фізична адреса `X_DSDT` (використовується у 64-бітних системах замість 32-бітного поля `DSDT`).
* `Offset 0x9C (156)`: Структура `RESET_REG` типу GAS. Описує порт або адреси регістра апаратного перезавантаження системи (Reset Register).
* `Offset 0xA8 (168)`: Значення байта `RESET_VALUE`, яке записується у `RESET_REG` для ініціювання хард-ресета комп'ютера.

### Архітектурні прапорці FADT Flags

Поле `flags` у FADT (Offset `0x70`) містить 32-бітну маску характеристик платформи:
* `Bit 0 (WBINVD)`: Якщо встановлено, ядро повинен виконувати інструкцію `WBINVD` перед входом у стан сну.
* `Bit 10 (DCK_CAP)`: Підтримка док-станції.
* `Bit 14 (RESET_REG_SUP)`: Підтримка регістра перезавантаження `RESET_REG`.
* `Bit 20 (HW_REDUCED_ACPI)`: Прапорець ACPI 5.0+, який означає, що платформа не має фіксованих регістрів ACPI (популярно в сучасних ARM64 та SoC системах).

## 5. Multiple APIC Description Table (MADT / APIC)

Таблиця MADT передає ядру повну апаратну карту топології контролерів переривань. Вона складається з основного заголовка та послідовності вкладених підтаблиць (Subtables).

Заголовок MADT описує 32-бітну фізичну адресу Local APIC для поточного CPU (`local_apic_address`) та прапорці `flags` (біт 0 вказує на наявність дуальних каскадних контролерів 8259 PIC).

### Ключові типи підтаблиць MADT

Кожна підтаблиця починається з заголовка із полів `type` (1 байт) та `length` (1 байт):

1. **Type 0 (Processor Local APIC):** Пов'язує ACPI Processor ID із фізичним Local APIC ID процесорного ядра. Містить прапор `flags` (біт 0 = Enabled).
2. **Type 1 (I/O APIC):** Описує контролер I/O APIC. Містить `io_apic_id`, фізичну адресу MMIO (`address`) та базовий системний номер переривання `global_system_interrupt_base` (GSI base).
3. **Type 2 (Interrupt Source Override):** Описує мапінг між класичними носіями IRQ ISA (0–15) та новими номерами GSI у системі APIC.

:::tabs
```c
/* C Subtable Header Definition */
#include <stdint.h>

#pragma pack(push, 1)

struct acpi_madt_subtable_header {
    uint8_t type;
    uint8_t length;
};

/* Type 0: Processor Local APIC */
struct acpi_madt_local_apic {
    struct acpi_madt_subtable_header header;
    uint8_t  processor_id; /* ACPI Processor ID */
    uint8_t  id;           /* Local APIC ID */
    uint32_t lapic_flags;  /* Bit 0 = Enabled, Bit 1 = Online Capable */
};

/* Type 1: I/O APIC */
struct acpi_madt_io_apic {
    struct acpi_madt_subtable_header header;
    uint8_t  id;           /* I/O APIC ID */
    uint8_t  reserved;
    uint32_t address;      /* Фізична адреса MMIO I/O APIC */
    uint32_t global_irq_base; /* Базовий номер GSI */
};

#pragma pack(pop)
```
```cpp
// C++ Subtable Definition
#include <cstdint>

#pragma pack(push, 1)

struct alignas(1) AcpiMadtSubtableHeader {
    std::uint8_t type;
    std::uint8_t length;
};

struct alignas(1) AcpiMadtLocalApic {
    AcpiMadtSubtableHeader header;
    std::uint8_t  processor_id;
    std::uint8_t  apic_id;
    std::uint32_t flags; // Bit 0: Enabled
};

struct alignas(1) AcpiMadtIoApic {
    AcpiMadtSubtableHeader header;
    std::uint8_t  io_apic_id;
    std::uint8_t  reserved;
    std::uint32_t io_apic_address;
    std::uint32_t global_system_interrupt_base;
};

#pragma pack(pop)
```
:::

## 6. Валідація та перевірка контрольної суми (Checksum)

Відповідно до специфікації ACPI, байтова сума всіх елементів валідної таблиці (включно із заголовком) за модулем 256 повинна дорівнювати нулю:

```
byte[0] + byte[1] + ... + byte[length - 1] ≡ 0  (mod 256)
```

Під час обходу виділеного діапазону пам'яті ядро послідовно підсумовує байти у 8-бітній змінній типу `uint8_t`. Завдяки переповненню беззнакового 8-бітного цілого числа підсумовування виконує операцію за модулем 256 автоматично без використання арифметичних операцій ділення. Якщо підсумковий результат відрізняється від нуля, ядро позначає таблицю як пошкоджену (corrupted) та відмовляється завантажувати з неї AML-код.
