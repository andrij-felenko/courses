# ⚙️ Практикум: аналіз таблиць, декомпіляція ASL та оверрайд DSDT у Linux

У реальних умовах розробки та усунення багів у прошивках материнських плат системним інженерам часто доводиться зчитувати сирі бінарні таблиці ACPI з пам'яті, декомпілювати їх у людські вихідні файли ASL, вносити виправлення в AML-код та перевизначати DSDT/SSDT під час завантаження ядра Linux. Цей практичний посібник містить покроковий інструктаж з аналізу ACPI в Linux, детальний опис механізму створення CPIO-архіву табличного оверрайду для initramfs, опрацювання розширень DSDT/SSDT, розбір ключових системних інваріантів, а також готові утиліти мовами C та C++ для читання й валідації сирих таблиць безпосередньо з системних інтерфейсів sysfs.

Необхідність у перевизначенні таблиць ACPI виникає тоді, коли виробник материнської плати випускає BIOS із багами у коді DSDT: наприклад, коли метод `_STA` пристрою контролера I2C помилково вимикає сенсорний тачпад, якщо операційна система не повідомляє про себе як специфічна версія Windows, або коли у термальних зонах прописано неправильні критичні пороги температур.

## 1. Схема отримання та мульти-табличної декомпіляції ACPI (iasl)

Усі статичні та динамічні таблиці, які ядро Linux прочитало під час старту з UEFI або BIOS, доступні у віртуальній файловій системі sysfs за шляхом `/sys/firmware/acpi/tables/`. Кожен файл у цьому каталозі названо відповідно до 4-символьної сигнатури ACPI (наприклад, `FADT`, `MADT`, `MCFG`, `DSDT`). Динамічні таблиці SSDT відображаються як `SSDT1`, `SSDT2` тощо.

### 1.1. Збереження бінарних дампів з пам'яті

Для отримання сирих таблиць використовується утиліта `acpidump` з офіційного пакету `acpica-tools` або пряме копіювання з системного каталогу sysfs. Утиліта `acpidump` зчитує всі системні таблиці безпосередньо з фізичних адрес RAM та зберігає їх в єдиному текстовому hex-дампі. Далі утиліта `acpixtract` розбирає цей дамп на окремі бінарні `.dat` файли.

```bash
# Варіант 1: Через acpidump та acpixtract
sudo acpidump > acpidump.dat
acpixtract -a acpidump.dat

# Варіант 2: Прямо з інтерфейсу sysfs
cp /sys/firmware/acpi/tables/DSDT dsdt.dat
cp /sys/firmware/acpi/tables/FADT fadt.dat
cp /sys/firmware/acpi/tables/SSDT* .
```

### 1.2. Внутрішня структура бінарного AML та опкоди ACPICA

Бінарний вміст DSDT та SSDT є байт-кодом AML (ACPI Machine Language), який виконується віртуальною машиною ACPICA всередині ядра. AML є стековою мовою з префіксною нотацією, де кожен оператор починається з байта опкоду (`Opcode`).

Оператори бувають трьох основних типів:
1. **Оператори даних та оголошень:** Оголошують об'єкти у просторі імен (`NameOp` `0x08`, `DeviceOp` `0x5B 0x82`, `MethodOp` `0x5B 0x14`, `ScopeOp` `0x10`).
2. **Оператори обчислень та керування:** Виконують арифметичні дії та розгалуження (`AddOp` `0x72`, `IfOp` `0xA0`, `ElseOp` `0xA1`, `ReturnOp` `0xA4`).
3. **Оператори контейнерів та пакетів:** Визначають блоки даних із вказанням розміру пакета (`PkgLength`).

Кожен змістовний блок AML починається з визначення `PkgLength` (кодування довжини пакета). Довжина пакета може займати від 1 до 4 байтів:
- Якщо старші 2 біти першого байта дорівнюють `00`, довжина пакета вміщується в 1 байт (значення від 0 до 63 байтів).
- Якщо старші біти дорівнюють `01`, `10` або `11`, довжина обчислюється з урахуванням наступних 1, 2 або 3 байтів відповідно.

Імена об'єктів у AML завжди пакуються у 4-байтні фіксовані ідентифікатори `NameSeg` (наприклад, `PCI0`, `_SB_`, `TMR_`). Якщо ім'я коротше 4 символів, воно доповнюється символами підкреслення `_` до 4 байтів.

### 1.3. Декомпіляція AML за допомогою iasl та розв'язання зовнішніх посилань (External)

Компілятор iASL від Intel (Intel ACPI Source Language Compiler/Decompiler) вміє працювати у зворотному напрямку. Він зчитує стековий байт-код AML і реконструює високорівневий синтаксичний код мовою ASL.

Якщо виконувати ізольовану декомпіляцію одного лише файла DSDT:

```bash
iasl -d dsdt.dat
```

інженер практично завжди зіткнеться з помилками видачі `UnknownObj` або неописом зовнішніх методів. Це відбувається тому, що сучасні прошивки виносять ініціалізацію відеокарт, контролерів USB-C та термальних зон окремо в додаткові таблиці SSDT. Коли DSDT викликає метод, визначений у `SSDT1`, самостійний розбір DSDT не знає кількості аргументів цього методу і не може правильно розібрати байт-код.

Щоб розв'язати цю проблему, iASL підтримує мульти-табличну декомпіляцію з прапорцем `-e`. Інженер має передати всі наявні бінарні таблиці SSDT як джерела зовнішніх символів:

```bash
iasl -e ssdt1.dat ssdt2.dat ssdt3.dat -d dsdt.dat
```

Під час запуску з прапорцем `-e` компілятор iASL виконує два проходи:
1. **Перший прохід (Symbol Scanning):** Зчитує всі надані таблиці SSDT, аналізує оголошення `Scope`, `Device`, `Method` та будує глобальну символьну таблицю простору імен ACPI з інформацією про тип кожного об'єкта та кількість параметрів усіх методів.
2. **Другий прохід (Decompilation):** Декомпілює цільовий файл `dsdt.dat`. Знайшовши виклик зовнішнього методу з `SSDT`, iASL звіряється зі зібраною символьною таблицею, генерує коректний макрос `External (\_SB.PCI0.GFX0.DD01, MethodObj)` у початку ASL-файлу та правильно декомпілює передачу аргументів.

При виявленні синтаксичних некоректностей прошивки або незакритих блоків `Scope` під час декомпіляції, iASL видає попередження та створює комбіновані макроси. Інженер повинен вручну перевірити створені директиви `External` і переконатися, що типи оголошених об'єктів (`DeviceObj`, `MethodObj`, `IntObj`, `FieldUnitObj`) відповідають реальним типам джерела.

### 1.4. Анатомія та відновлення вихідного ASL-файлу

Текстовий файл `dsdt.dsl` починається із макроса `DefinitionBlock`, який визначає назву вихідного AML-файлу, сигнатуру таблиці, ревізію та OEM-ідентифікатори:

```asl
/* Приклад фрагмента dsdt.dsl */
DefinitionBlock ("DSDT.aml", "DSDT", 2, "INTEL ", "OEMDSDT ", 0x00000001)
{
    Scope (\_SB)
    {
        Device (PCI0)
        {
            Name (_HID, EisaId ("PNP0A08"))  /* PCI Express Root Bridge */
            Method (_STA, 0, NotSerialized)
            {
                Return (0x0F)  /* Device present, enabled, functioning */
            }

            Device (I2C1)
            {
                Name (_ADR, 0x00150001)
                Method (_STA, 0, NotSerialized)
                {
                    /* Виправлений метод _STA для тачпада */
                    Return (0x0F)
                }
            }
        }
    }
}
```

У цьому фрагменті оголошується область системної шини `\_SB` та пристрій `PCI0` з ідентифікатором `PNP0A08`. Метод `_STA` повертає значення `0x0F`, що інформує ядро про повну готовність пристрою до роботи.

## 2. Створення initrd CPIO оверрайду та фази завантаження ядра Linux

Після внесення виправлень у файл `dsdt.dsl` (наприклад, виправлення методу `_STA` або переписання термальних зон), файл повторно компілюється у бінарний байт-код AML:

```bash
iasl -tc dsdt.dsl
```

Параметр `-tc` вмикає строгий режим перевірки синтаксису і генерує скомпільований бінарний файл `dsdt.aml`, а також заголовковий файл C з hex-масивом. Якщо у коді є синтаксичні помилки або некоректні типи даних, iASL зупинить процес із вказанням конкретного рядка коду.

### 2.1. Формат CPIO header newc та магічне число 070701

Ядро Linux містить підсистему `ACPI Table Override`, яка дозволяє підмінити DSDT та SSDT прошивки материнської плати до того, як ядро почне будувати дерево простору імен ACPICA.

Для цього використовується механізм підкладки першого CPIO-архіву до складу initramfs. Цей архів повинен мати формат `newc` (SVR4 portable format without CRC).

Заголовок кожного файла у форматі `newc` складається з 110 байтів ASCII-тексту. Найперші 6 байтів заголовка містять магічний ASCII-рядок `"070701"`. Далі у заголовку слідують текстові hex-поля розміром 8 байтів кожне:
- `c_ino`: номер inode;
- `c_mode`: права доступу та тип файла;
- `c_uid` / `c_gid`: ідентифікатори власника;
- `c_nlink`: кількість лінків;
- `c_mtime`: час модифікації;
- `c_filesize`: розмір вмісту файла у байтах (8 hex-символів);
- `c_namesize`: довжина імені шляху файла у байтах (включаючи terminating null);
- `c_chksum`: checksum (у `newc` дорівнює 0).

Після 110 байтів заголовка розміщується назва шляху файла, яка вирівнюється нульовими байтами до кратності 4 байтам. Далі розміщується бінарне тіло файла, яке також вирівнюється до 4 байтів.

### 2.2. Ієрархія шляхів оверрайду у проданному архіві

Специфікація ядра Linux вимагає, щоб бінарні таблиці ACPI для оверрайду знаходилися у CPIO-архіві за суворо визначеними шляхами:
- `kernel/x86/microcode/ACPI/DSDT.aml` — для підміни головної таблиці DSDT;
- `kernel/x86/microcode/ACPI/SSDT1.aml`, `kernel/x86/microcode/ACPI/SSDT2.aml` — для додавання або підміни додаткових таблиць SSDT.

Створення архіву виконується за допомогою стандартних утиліт командного рядка:

```bash
# 1. Створення каталогу згідно зі специфікацією ядра
mkdir -p kernel/x86/microcode/ACPI

# 2. Копіювання згенерованого AML файлу з ім'ям DSDT.aml
cp dsdt.aml kernel/x86/microcode/ACPI/DSDT.aml

# 3. Упаковка в несжиманий CPIO архів формату newc
find kernel | cpio -H newc -o > acpi_override.cpio
```

### 2.3. Чому архів вимагається суворо несжиманим (Uncompressed CPIO)

Головна вимога до `acpi_override.cpio` полягає в тому, що цей архів **не можна стискати** за допомогою `gzip`, `bzip2`, `lz4` чи `zstd`.

Технічна причина полягає у фазі завантаження ядра. Підсистема оверрайду ACPI виконується у функції `acpi_table_upgrade()`, яка викликається під час ранньої ініціалізації архітектури `setup_arch()`. На цьому етапі ядро ще не ініціалізувало віртуальну пам'яті у повному обсязі, не створило підсистему сторінкового розподільника (page allocator) та не завантажило алгоритми декомпресії initrd.

Ядро зчитує початковий фізичний адрес initramfs, переданий завантажувачем GRUB2 чи systemd-boot, і сканує перші байти пам'яті на наявність магічного ряду `"070701"`. Якщо заголовок CPIO знайдено у сирому вигляді, ядро негайно витягує вміст `DSDT.aml` у зарезервований блок пам'яті (memblock). Якщо ж архів стиснуто, ядро не бачить магічних байтів `"070701"`, пропускає перевірку і вважає, що initrd містить лише звичайну файлову систему, яка буде розпакована пізніше — але для ACPI це буде занадто пізно, бо ACPICA вже побудує дерево простору імен із таблиць BIOS.

### 2.4. Внутрішній механізм ядра acpi_table_upgrade()

Внутрішня робота підсистеми `acpi_table_upgrade()` відбувається за наступним алгоритмом:

1. **Сканування заголовка CPIO:** Ядро проходить по файлах раннього CPIO-архіву і шукає записи у префіксі `kernel/x86/microcode/ACPI/`.
2. **Перевірка заголовка ACPI:** Знайшовши файл `DSDT.aml`, ядро вичитує перші 36 байтів, валідує сигнатуру `"DSDT"` та перевіряє 8-бітну контрольну суму бінарного AML-блоку.
3. **Аллокація memblock:** Ядро виділяє суцільний фізичний блок пам'яті через `memblock_alloc()`, копіює туди AML-дані та вирівнює адрес.
4. **Заміна у таблиці ACPICA:** Ядро реєструє виділений блок у глобальному масиві `acpi_gbl_hardware_tables`. Коли ACPICA згодом запитує фізичну адресу DSDT з таблиці FADT, підсистема повертає адресу з memblock замість адреси з прошивки UEFI/BIOS.

### 2.5. Конфігурація завантажувача та діагностика

Отриманий файл `acpi_override.cpio` додається першим елементом у рядку ініціалізації initrd завантажувача GRUB2 або systemd-boot.

```text
# Фрагмент конфігурації /boot/grub/grub.cfg
menuentry 'Linux with ACPI Override' {
    linux   /vmlinuz-6.8.0-generic root=/dev/sda2 ro quiet
    initrd  /acpi_override.cpio /initrd.img-6.8.0-generic
}
```

Зверніть увагу: у рядку `initrd` файл `acpi_override.cpio` вказується **перед** основним стиснутим образом `initrd.img-6.8.0-generic`. Завантажувач розміщує ці два файли один за одним у єдиному безперервному буфері RAM. Ядро спочатку вичитує несжиману частину ACPI, а після закінчення CPIO-архіву знаходить заголовок gzip/zstd і передає решту даних підсистемі `populate_rootfs()`.

Перевірити успішність заміни можна за допомогою системного журналу `dmesg`:

```bash
sudo dmesg | grep -i acpi | grep -i override
# Очікуваний вивід: ACPI: Table [DSDT] replaced by host OS
```

Якщо під час завантаження виникають помилки виконання AML-коду, можна увімкнути динамічне трасування віртуальної машини ACPICA через параметри ядра:

```text
acpi.debug_layer=0xFFFFFFFF acpi.debug_level=0x2
```

Це змушує інтерпретатор друкувати кожен крок виконання опкодів у системний журнал `dmesg`.

## 3. Опрацювання розширень DSDT/SSDT та стратегії патчингу

Підсистема ACPI оперує однією головною таблицею опису системи DSDT та багатьма додатковими таблицями SSDT.

### 3.1. DSDT проти SSDT: відмінності та призначення

- **DSDT (Differentiated System Description Table):** Обов'язкова монолітна таблиця, адреса якої прописана у таблиці FADT. Вона містить базове дерево пристроїв материнської плати (`\_SB`), контролери системних шин (PCI, I2C, SPI), шини шинних мостів та системні ресурси.
- **SSDT (Secondary System Description Table):** Допоміжні таблиці, які доповнюють простір імен. Адреси статичних SSDT прописані у підтаблицях XSDT/RSDT. SSDT використовуються для відокремлення коду дискретних відеокарт (NVIDIA Optimus / AMD Enduro), регуляторів живлення процесорних ядер (P-states, C-states), контролерів Thunderbolt/USB4 та зовнішніх доків.

### 3.2. Динамічне завантаження SSDT через Load та LoadTable

ACPI дозволяє завантажувати SSDT не лише під час старту, але й динамічно під час виконання AML-коду. У мові ASL для цього передбачені опкоди `Load` та `LoadTable`.

Наприклад, коли користувач підключає зовнішню графічну карту Thunderbolt, AML-код контролера PCIe може викликати:

```asl
LoadTable ("SSDT", "OEMID ", "GPU_TAB", "\\_SB.PCI0.RP05", 0, 0)
```

Оператор `LoadTable` знаходить у пам'яті відповідну SSDT-таблицю за сигнатурою, OEM ID та OEM Table ID, вичитує її AML байт-код і монтує нові пристрої у вказану область простору імен (`\_SB.PCI0.RP05`).

### 3.3. Модифікація простору імен через Scope та правила унікальності об'єктів

Кожна SSDT-таблиця оперує вказівниками на простір імен. За допомогою конструкції `Scope (\_SB.PCI0)` додаткова таблиця може «вмикатися» в існуючий вузол DSDT і додавати нові пристрої чи методи.

Проте ACPICA накладає суворі правила унікальності об'єктів:
1. **Унікальність імен у межах Scope:** Усі об'єкти в одному вузлі `Scope` повинні мати унікальні 4-символьні імена `NameSeg`. Якщо SSDT спробує оголосити пристрій `Device (TPAD)`, який вже існує в DSDT під тим самим шляхом, ACPICA припинить завантаження SSDT з помилкою `AE_ALREADY_EXISTS`.
2. **Директива External:** Якщо SSDT звертається до об'єкта чи методу, оголошеного в DSDT, цей об'єкт обов'язково повинен бути задекларований через `External (\_SB.PCI0.I2C1.TPAD, DeviceObj)`.

### 3.4. DSDT Override проти Custom SSDT Override

При виправленні багів у прошивках у інженера є два шляхи:

1. **DSDT Override (Повна заміна DSDT):** Декомпільовується весь DSDT, правиться баг і заміна завантажується через initrd.
   - *Перевага:* Дозволяє змінити будь-який рядок вихідного коду DSDT.
   - *Недолік:* Нестійкість до оновлень BIOS. Якщо користувач оновлює прошивку материнської плати, його виправлений DSDT від старої версії BIOS буде перекривати новий DSDT виробника, втрачаючи виправлення безпеки чи підтримку нових процесорів.
2. **Custom SSDT Override (Ін'єкція виправляючої SSDT):** Замість заміни всієї DSDT створюється маленька автономна таблиця SSDT (наприклад `SSDT-FIX.aml`). У ній через `Scope` підключаються необхідні вузли, а через оголошення нових методів або перекриття об'єктів виправляється поведінка.
   - *Перевага:* Модульність та безпека. Оригінальний DSDT залишається недоторканим і оновлюється разом із BIOS, а кастомна SSDT додає лише необхідний патч.

## 4. Архітектурні інваріанти парсингу та валідації AML / ACPI

Під час створення парсерів або інструментів модифікації AML необхідно дотримуватися п'яти фундаментальних системних інваріантів:

### 4.1. Інваріант заголовка ACPI та збереження DefinitionBlock

Кожна таблиця ACPI (як статична, так і динамічна) починається з фіксованого 36-байтного заголовка `acpi_table_header`.

Структура заголовка повинна задовольняти такі вимоги:
- Перші 4 байти містять ASCII-сигнатуру (`DSDT`, `SSDT`, `FADT`, `MADT`).
- Поле `length` (починаючи з офсету 4) містить повну довжину таблиці у байтах, включаючи самі 36 байтів заголовка.
- Поле `revision` визначає версію специфікації ACPI (для ACPI 2.0+ значення дорівнює `2`).
- Усі зміщення полів у пам'яті повинні бути вирівняні без пружків пакування компілятора (`#pragma pack(push, 1)` або `alignas(1)`).

### 4.2. Інваріант 8-бітної контрольної суми (Checksum)

Сума всіх байтів таблиці ACPI по модулю 256 повинна бути суворо дорівнює `0x00`:

`Сума (від i = 0 до Length - 1) Byte[i] mod 256 = 0`

Якщо після редагування AML-коду або заголовка сума байтів не дорівнює 0, ядро Linux визнає таблицю пошкодженою (`Invalid ACPI checksum`) і відмовиться її завантажувати. При ручному формуванні або компіляції через iASL поле `checksum` розраховується як доповнення до нуля від суми всіх інших байтів.

### 4.3. Інваріант відповідності розміру Length

Значення поля `Length` у заголовку ACPI має суворо відповідати фактичному розміру бінарного масиву чи файла на диску. Якщо файл на диску має розмір 4096 байтів, а поле `Length` містить `0x0800` (2048 байтів), парсер ACPICA зчитає лише першу половину файла, що призведе до зрізання опкоду `DefinitionBlock` та фатальної помилки парсингу `AE_AML_BAD_TLV`.

### 4.4. Інваріанти завантаження у простір імен ACPICA (AcpiLoadTable)

При виклику внутрішньої функції `AcpiLoadTable()` у ядрі діють наступні інваріанти:
- Кожен створений об'єкт реєструється як вузол `ACPI_NAMESPACE_NODE` у глобальному графі.
- Операції додавання вузлів виконуються під захистом системного м'ютекса `AcpiGbl_NamespaceMutex`.
- Усі посилання на зовнішні об'єкти повинні розв'язуватися у момент завершення обходу таблиці; якщо символ залишається неописаним, об'єкт маркується як неактивний.

## 5. Програмний читач та розшинений аналізатор ACPI (C / C++)

Нижче наведено реалізацію утиліти мовами C та C++, яка відкриває бінарні файли системних таблиць безпосередньо з віртуальної файлової системи sysfs (наприклад, `/sys/firmware/acpi/tables/FADT` або `/sys/firmware/acpi/tables/DSDT`), перевіряє розмір заголовка, розбирає поля структури, розраховує 8-бітну контрольну суму та сканує базові опкоди AML.

Усі приклади мовою C++ написані з дотриманням стандарту C++20, з використанням RAII, `std::span`, `std::string_view` та безапеляційно без витоків ресурсів. Приклад мовою C використовує ідіоматичний підхід C із явним керуванням пам'яттю, паковкою структур та вичерпною обробкою помилок.

:::tabs
```c
/* C Implementation: ACPI Table Inspector & AML Header Parser */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#pragma pack(push, 1)
struct acpi_table_header {
    char     signature[4];
    uint32_t length;
    uint8_t  revision;
    uint8_t  checksum;
    char     oem_id[6];
    char     oem_table_id[8];
    uint32_t oem_revision;
    char     asl_compiler_id[4];
    uint32_t asl_compiler_revision;
};
#pragma pack(pop)

/* Валідація 8-бітної контрольної суми */
int validate_acpi_checksum(const uint8_t *buffer, size_t length) {
    if (!buffer || length == 0) return 0;
    uint8_t sum = 0;
    for (size_t i = 0; i < length; ++i) {
        sum += buffer[i];
    }
    return (sum == 0);
}

/* Простий аналіз AML PkgLength (довжини пакета) */
size_t parse_aml_pkg_length(const uint8_t *aml_data, size_t max_len, size_t *bytes_read) {
    if (max_len < 1) return 0;
    uint8_t lead = aml_data[0];
    uint8_t byte_count = (lead >> 6) & 0x03;

    if (byte_count == 0) {
        if (bytes_read) *bytes_read = 1;
        return (lead & 0x3F);
    }

    if (max_len < (size_t)(byte_count + 1)) return 0;
    size_t length = (lead & 0x0F);
    for (uint8_t i = 0; i < byte_count; ++i) {
        length |= ((size_t)aml_data[1 + i]) << (4 + i * 8);
    }
    if (bytes_read) *bytes_read = byte_count + 1;
    return length;
}

int process_acpi_table_file(const char *filepath) {
    FILE *f = fopen(filepath, "rb");
    if (!f) {
        perror("Failed to open ACPI table file");
        return 1;
    }

    struct acpi_table_header hdr;
    if (fread(&hdr, 1, sizeof(hdr), f) != sizeof(hdr)) {
        fprintf(stderr, "Failed to read ACPI header\n");
        fclose(f);
        return 1;
    }

    if (hdr.length < sizeof(struct acpi_table_header)) {
        fprintf(stderr, "Invalid header length field: %u\n", hdr.length);
        fclose(f);
        return 1;
    }

    uint8_t *full_table = (uint8_t *)malloc(hdr.length);
    if (!full_table) {
        fprintf(stderr, "Memory allocation failure for %u bytes\n", hdr.length);
        fclose(f);
        return 1;
    }

    fseek(f, 0, SEEK_SET);
    size_t read_bytes = fread(full_table, 1, hdr.length, f);
    fclose(f);

    if (read_bytes != hdr.length) {
        fprintf(stderr, "Read mismatch: expected %u, got %zu\n", hdr.length, read_bytes);
        free(full_table);
        return 1;
    }

    int valid_sum = validate_acpi_checksum(full_table, hdr.length);

    printf("=== ACPI Table Metadata ===\n");
    printf("Signature:       %.4s\n", hdr.signature);
    printf("Table Length:    %u bytes\n", hdr.length);
    printf("Revision:        %u\n", hdr.revision);
    printf("OEM ID:          %.6s\n", hdr.oem_id);
    printf("OEM Table ID:    %.8s\n", hdr.oem_table_id);
    printf("ASL Compiler ID: %.4s\n", hdr.asl_compiler_id);
    printf("Checksum Status: %s\n", valid_sum ? "VALID (0x00)" : "INVALID");

    /* Якщо це DSDT або SSDT, показуємо інформацію про AML payload */
    if (memcmp(hdr.signature, "DSDT", 4) == 0 || memcmp(hdr.signature, "SSDT", 4) == 0) {
        size_t payload_offset = sizeof(struct acpi_table_header);
        if (hdr.length > payload_offset) {
            size_t aml_len = hdr.length - payload_offset;
            printf("AML Payload Size: %zu bytes\n", aml_len);
            
            size_t pkg_bytes_read = 0;
            size_t root_pkg_len = parse_aml_pkg_length(full_table + payload_offset, aml_len, &pkg_bytes_read);
            printf("Root AML PkgLength: %zu bytes (encoded in %zu header bytes)\n", root_pkg_len, pkg_bytes_read);
        }
    }

    free(full_table);
    return valid_sum ? 0 : 2;
}

int main(int argc, char **argv) {
    const char *path = (argc > 1) ? argv[1] : "/sys/firmware/acpi/tables/FADT";
    return process_acpi_table_file(path);
}
```
```cpp
// C++ Implementation: Modern RAII ACPI Table Inspector & AML Parser (C++20)
#include <iostream>
#include <fstream>
#include <vector>
#include <array>
#include <string_view>
#include <span>
#include <numeric>
#include <cstdint>
#include <memory>

#pragma pack(push, 1)
struct alignas(1) AcpiTableHeader {
    std::array<char, 4> signature;
    std::uint32_t       length;
    std::uint8_t        revision;
    std::uint8_t        checksum;
    std::array<char, 6> oem_id;
    std::array<char, 8> oem_table_id;
    std::uint32_t       oem_revision;
    std::array<char, 4> asl_compiler_id;
    std::uint32_t       asl_compiler_revision;
};
#pragma pack(pop)

class AcpiTableParser {
public:
    static bool validateChecksum(std::span<const std::uint8_t> data) noexcept {
        if (data.empty()) return false;
        const std::uint8_t sum = std::accumulate(
            data.begin(), data.end(), static_cast<std::uint8_t>(0)
        );
        return sum == 0;
    }

    static std::pair<std::size_t, std::size_t> parseAmlPkgLength(std::span<const std::uint8_t> amlData) noexcept {
        if (amlData.empty()) return {0, 0};
        const std::uint8_t lead = amlData[0];
        const std::uint8_t byteCount = (lead >> 6) & 0x03;

        if (byteCount == 0) {
            return {static_cast<std::size_t>(lead & 0x3F), 1};
        }

        if (amlData.size() < static_cast<std::size_t>(byteCount + 1)) {
            return {0, 0};
        }

        std::size_t length = (lead & 0x0F);
        for (std::uint8_t i = 0; i < byteCount; ++i) {
            length |= (static_cast<std::size_t>(amlData[1 + i]) << (4 + i * 8));
        }
        return {length, static_cast<std::size_t>(byteCount + 1)};
    }

    static bool inspectTable(std::string_view path) {
        std::ifstream file(path.data(), std::ios::binary | std::ios::ate);
        if (!file.is_open()) {
            std::cerr << "Error: Cannot open ACPI table file: " << path << '\n';
            return false;
        }

        const auto fileSize = static_cast<std::size_t>(file.tellg());
        file.seekg(0, std::ios::beg);

        if (fileSize < sizeof(AcpiTableHeader)) {
            std::cerr << "Error: File size (" << fileSize << " bytes) is smaller than ACPI header\n";
            return false;
        }

        std::vector<std::uint8_t> buffer(fileSize);
        if (!file.read(reinterpret_cast<char*>(buffer.data()), fileSize)) {
            std::cerr << "Error: Failed to read binary table data\n";
            return false;
        }

        const auto* hdr = reinterpret_cast<const AcpiTableHeader*>(buffer.data());
        const std::string_view sig(hdr->signature.data(), 4);
        const std::string_view oem(hdr->oem_id.data(), 6);
        const std::string_view oemTable(hdr->oem_table_id.data(), 8);
        const std::string_view compiler(hdr->asl_compiler_id.data(), 4);

        const bool isChecksumValid = validateChecksum(buffer);

        std::cout << "========================================\n";
        std::cout << "   Modern C++20 ACPI Table Inspector    \n";
        std::cout << "========================================\n";
        std::cout << "Signature:         " << sig << '\n';
        std::cout << "Header Length:     " << hdr->length << " bytes\n";
        std::cout << "File Raw Size:     " << fileSize << " bytes\n";
        std::cout << "Revision:          " << static_cast<int>(hdr->revision) << '\n';
        std::cout << "OEM ID:            " << oem << '\n';
        std::cout << "OEM Table ID:      " << oemTable << '\n';
        std::cout << "ASL Compiler:      " << compiler << '\n';
        std::cout << "Checksum Status:   " << (isChecksumValid ? "VALID (0x00)" : "INVALID") << '\n';

        if (sig == "DSDT" || sig == "SSDT") {
            const std::span<const std::uint8_t> fullSpan(buffer);
            if (fullSpan.size() > sizeof(AcpiTableHeader)) {
                const auto amlPayload = fullSpan.subspan(sizeof(AcpiTableHeader));
                std::cout << "AML Bytecode Size: " << amlPayload.size() << " bytes\n";

                const auto [pkgLen, bytesRead] = parseAmlPkgLength(amlPayload);
                std::cout << "Root AML PkgLength: " << pkgLen << " bytes (header bytes: " << bytesRead << ")\n";
            }
        }

        return isChecksumValid;
    }
};

int main(int argc, char** argv) {
    const std::string_view path = (argc > 1) ? argv[1] : "/sys/firmware/acpi/tables/FADT";
    return AcpiTableParser::inspectTable(path) ? 0 : 1;
}
```
:::
