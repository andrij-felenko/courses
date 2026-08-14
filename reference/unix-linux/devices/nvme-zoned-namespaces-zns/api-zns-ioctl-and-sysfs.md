# 📋 Інтерфейс системних викликів, ioctl та sysfs для NVMe ZNS

Ця довідкова вставка містить точні специфікації структур даних, атрибутів sysfs, викликів ioctl та командних кодів підсистеми NVMe ZNS у ядрі Linux, необхідних для низкорівневого управління зонованими накопичувачами з користувацького простору (userspace).

## Атрибути псевдофайлової системи sysfs для ZNS

Підсистема блочних пристроїв ядра Linux експортує геометрію та апаратні обмеження ZNS-простору імен через псевдофайлову систему `sysfs` за шляхом `/sys/block/nvmeXnY/queue/`. Ці файли надають системним адміністорам та високонавантаженим застосункам змогу зчитувати параметри диска без виконання системних викликів ioctl з правами суперкористувача.

Кожен із цих атрибутів відображає фундаментальні обмеження драйвера та контролера пристрою:

| Атрибут sysfs | Тип даних | Опис та можливі значення |
| :--- | :--- | :--- |
| `zoned` | string | Режим зонування пристрою. Значення `host-managed` вказує на суворий ZNS або Host-Managed SMR. Значення `none` означає звичайний блоковий пристрій. |
| `chunk_sectors` | integer | Розмір зони у 512-байтових секторах (Zone Size). Наприклад, значення `262144` відповідає зоні розміром 128 МБ. |
| `zone_append_max_bytes` | integer | Максимальний розмір однієї апаратної операції `Zone Append` у байтах (обмеження ZASL). Звичайно від 4 КБ до 128 КБ. |
| `nr_zones` | integer | Загальна кількість зон у просторі імен NVMe. |
| `max_open_zones` | integer | Максимальна кількість одночасно відкритих зон (ліміт MOR). Значення `0` означає відсутність апаратного обмеження. |
| `max_active_zones` | integer | Максимальна кількість активних зон (ліміт MAR, сума відкритих та закритих зон з WP > ZSLBA). `0` = неограничено. |

Отримати значення атрибутів у консолі можна за допомогою стандартних команд читання:

```bash
cat /sys/block/nvme0n1/queue/zoned
cat /sys/block/nvme0n1/queue/zone_append_max_bytes
cat /sys/block/nvme0n1/queue/chunk_sectors
cat /sys/block/nvme0n1/queue/max_open_zones
cat /sys/block/nvme0n1/queue/max_active_zones
```

Системні бібліотеки (наприклад, `libnvme` або `libblkio`) зчитують ці атрибути під час ініціалізації дескриптора пристрою, щоб налаштувати правильний розмір буферів та уникнути надсилання команд запису, що перевищують межу `zone_append_max_bytes`. Якщо застосунок спробує сформувати запит дозапису розміром 256 КБ при значенні `zone_append_max_bytes = 131072` (128 КБ), шар ядра Linux поверне системну помилку `EINVAL` ще до надсилання команди вSubmission Queue пристрою.

При створенні високопродуктивних систем збереження даних на основі NVMe ZNS вивчення вмісту sysfs є першим обов'язковим кроком автоматизованого конфігурування. Кожен параметр експортується драйвером ядра `nvme` під час виконання функції `nvme_update_zone_info()`. Якщо значення атрибута `zoned` відрізняється від `host-managed`, спроба виконання будь-яких специфічних зональних викликів ioctl чи команд `Zone Append` поверне помилку `ENOTTY` (Inappropriate ioctl for device).

Зверніть увагу, що атрибут `chunk_sectors` вказує саме на двійковий логічний розмір зони (Zone Size) у секторах по 512 байт, а не на фактичну корисну ємність (Zone Capacity). Корисна ємність зони може бути меншою за `chunk_sectors` через межі апаратних блоків стирання NAND Flash. Фактичне значення `Zone Capacity` можна дізнатися лише шляхом виконання системного виклику `BLKREPORTZONE` чи зчитування звіту зон через нативну команду NVMe ZNS.

Параметри `max_open_zones` та `max_active_zones` визначають фундаментальні ліміти буферизації контролера SSD. Якщо програма намагається відкрити нову зону при досягненні `max_open_zones`, ядро або пристрій відхилить запит. Розумні драйвери керування зонами автоматично закривають застарілі зони при наближенні до цієї межі. Значення `0` у цих файлах означає, що пристрій не має жорстких апаратних обмежень на кількість відкритих чи активних зон.

Крім того, підсистема `sysfs` дає змогу моніторити динамічний стан черги пристрою через атрибути `nr_requests` та `scheduler`. У більшості випадків для пристроїв ZNS використовується планувальник `none` чи `mq-deadline`, щоб запобігти зайвим перевішуванням та затримкам при передачі команд у нижній шар `blk-mq`.

У системах керування збереженням даних на основі контейнерів (Docker, Kubernetes/CSI) ці каталоги та файли `sysfs` можуть монтуватися у режим readonly всередину контейнера, даючи змогу мікросервісам моніторити параметри дискової підсистеми без потреби надання підвищених привілеїв суперкористувача (CAP_SYS_ADMIN).

Крім того, системний інспектор може зчитувати інформацію про апаратні черги I/O через атрибут `/sys/block/nvmeXnY/mq/`, де для кожної hardware queue (hctx) експортуються лічильники оброблених команд та кількість переривань CPU. Також доступні метрики лічильників тайм-аутів та помилок ретраїв.

Ці sysfs параметри дають змогу створювати автоматизовані скрипти моніторингу Prometheus/Grafana для завчасного попередження про наближення до апаратних лімітів MAR та MOR. Завдяки прозорості атрибутів sysfs адміністрування зонованих накопичувачів у дата-центрах стає детермінованим і надійним.

## Універсальні виклики ioctl ядра Linux (`<linux/blkzoned.h>`)

Ядро Linux забезпечує уніфікований шар Zoned Block Device (ZBD), який дозволяє виконувати базові операції над будь-яким зонованим пристроєм (NVMe ZNS або SMR HDD) через класичні виклики `ioctl()`. Це дозволяє писати крос-платформений код управління зонами, який не залежить від того, чи підключено накопичувач через NVMe PCIe, чи через SAS SMR.

### Основні макроси та константи ioctl

Константи викликів визначено в заголовочному файлі `<linux/blkzoned.h>`:

:::tabs
```c
#include <linux/blkzoned.h>

#define BLKREPORTZONE  _IOWR(0x12, 130, struct blk_zone_report)
#define BLKRESETZONE   _IOW(0x12, 131, struct blk_zone_range)
#define BLKGETZONESZ   _IOR(0x12, 132, __u32)
#define BLKGETNRZONES  _IOR(0x12, 133, __u32)
#define BLKOPENZONE    _IOW(0x12, 134, struct blk_zone_range)
#define BLKCLOSEZONE   _IOW(0x12, 135, struct blk_zone_range)
#define BLKFINISHZONE  _IOW(0x12, 136, struct blk_zone_range)
```
```cpp
#include <linux/blkzoned.h>
#include <sys/ioctl.h>

// У C++ використовують ті самі системні макроси ZBD із <linux/blkzoned.h>
constexpr auto kReportZone = BLKREPORTZONE;
constexpr auto kResetZone  = BLKRESETZONE;
constexpr auto kGetZoneSz  = BLKGETZONESZ;
constexpr auto kGetNrZones = BLKGETNRZONES;
```
:::

Детальний механізм роботи цих системних викликів полягає у наступному:

- `BLKRESETZONE`: Приймає вказувач на структуру `struct blk_zone_range`. Драйвер ядра перетворює діапазон секторів у початковий LBA зони (SLBA) та формує апаратну команду `Zone Management Send` з кодом дії Reset (`0x04`). Ця операція миттєво стирає фізичний блок флеш-пам'яті NAND і повертає вказівник запису (Write Pointer) на початок зони.
- `BLKREPORTZONE`: Використовується для зчитування масиву описувачів зон. Застосунок виділяє буфер пам'яті, де розміщується структура `struct blk_zone_report` з динамічним масивом `zones[]`. У полі `sector` вказується початковий сектор для запиту, а в полі `nr_zones` — максимальна кількість секторів для зчитування. Ядро заповнює цей масив актуальними даними про значення Write Pointer та стан кожної зони.
- `BLKOPENZONE`, `BLKCLOSEZONE`, `BLKFINISHZONE`: Надсилають відповідні апаратні команди `Zone Management Send` (з кодами дій Open `0x03`, Close `0x01`, Finish `0x02`), що дозволяє застосунку явно керувати внутрішніми ресурсами контролера SSD (моральні ліміти MOR та MAR).

### Структури даних Linux ZBD

Для виконання дій над конкретним діапазоном секторів використовується структура `struct blk_zone_range`. Поле `sector` вказує на початковий сектор зони у 512-байтових одиницях, а `nr_sectors` вказує кількість секторів, охоплених операцією (наприклад, для скидання кількох зон поспіль):

:::tabs
```c
struct blk_zone_range {
    __u64 sector;       /* Початковий сектор зони (512-байтові одиниці) */
    __u64 nr_sectors;   /* Сумарна кількість секторів у діапазоні */
};
```
```cpp
// У C++20 структура виклику ініціалізується через 지정ний ініціалізатор (designated initializers)
struct blk_zone_range range{
    .sector = 0,
    .nr_sectors = 262144
};
```
:::

Для запиту інформації про стан зон (Zone Report) використовується структура `struct blk_zone_report`, яка містить заголовок запиту та гнучкий масив описувачів зон:

:::tabs
```c
struct blk_zone_report {
    __u64 sector;       /* Початковий сектор для запиту звіту */
    __u32 nr_zones;     /* Вхід: розмір масиву zones[]; Вихід: повернута кількість */
    __u8  flags;        /* Прапорці звіту (наприклад, BLK_ZONE_REP_CAPACITY) */
    __u8  pad[7];       /* Резервні байти вирівнювання */
    struct blk_zone zones[0]; /* Гнучкий масив описувачів зон */
};
```
```cpp
// Динамічний розмір буфера звіту зон у C++
std::size_t rep_size = sizeof(struct blk_zone_report) + n_zones * sizeof(struct blk_zone);
auto rep_buf = std::make_unique<std::byte[]>(rep_size);
auto* report = reinterpret_cast<struct blk_zone_report*>(rep_buf.get());
```
:::

При виділенні пам'яті під `struct blk_zone_report` застосунок мусить враховувати розмір заголовка та кількість елементів:

:::tabs
```c
size_t rep_size = sizeof(struct blk_zone_report) + n_zones * sizeof(struct blk_zone);
struct blk_zone_report *rep = (struct blk_zone_report *)malloc(rep_size);
```
```cpp
std::size_t rep_size = sizeof(struct blk_zone_report) + n_zones * sizeof(struct blk_zone);
auto rep = std::unique_ptr<struct blk_zone_report, decltype(&std::free)>(
    static_cast<struct blk_zone_report*>(std::malloc(rep_size)), &std::free
);
```
:::

Кожен елемент масиву `struct blk_zone` містить детальні апаратні атрибути окремої зони:

:::tabs
```c
struct blk_zone {
    __u64 start;        /* Початковий сектор зони (ZSLBA) */
    __u64 len;          /* Фізичний розмір зони у секторах (Zone Size) */
    __u64 wp;           /* Поточна позиція вказівника запису (Write Pointer) */
    __u8  type;         /* Тип зони: 0x01 = CONVENTIONAL, 0x02 = SEQ_WRITE_REQ */
    __u8  cond;         /* Стан зони (Zone Condition) */
    __u8  non_seq;      /* Прапорець непослідовного запису (0 для ZNS) */
    __u8  reset;        /* Потрібне скидання зони */
    __u8  pad[4];       /* Вирівнювання структури до 64 байт */
    __u64 capacity;     /* Доступна корисна ємність зони (Zone Capacity) */
    __u8  reserved[24]; /* Резерв ядра для майбутніх розширень */
};
```
```cpp
// У C++ безпечна перевірка стану зони здійснюється через enum class
enum class ZoneCondition : std::uint8_t {
    Empty      = BLK_ZONE_COND_EMPTY,
    ImpOpen    = BLK_ZONE_COND_IMP_OPEN,
    ExpOpen    = BLK_ZONE_COND_EXP_OPEN,
    Closed     = BLK_ZONE_COND_CLOSED,
    Full       = BLK_ZONE_COND_FULL,
    ReadOnly   = BLK_ZONE_COND_READONLY,
    Offline    = BLK_ZONE_COND_OFFLINE
};
```
:::

Таблиця можливих значень поля `cond` (Zone Condition):

| Код стану `cond` | Константа C | Опис стану зони |
| :--- | :--- | :--- |
| `0x00` | `BLK_ZONE_COND_NOT_WP` | Звичайна зона довільного доступу (Conventional). |
| `0x01` | `BLK_ZONE_COND_EMPTY` | Порожня зона (`Empty`), WP == start. |
| `0x02` | `BLK_ZONE_COND_IMP_OPEN` | Неявно відкрита пристроєм (`Implicit Open`). |
| `0x03` | `BLK_ZONE_COND_EXP_OPEN` | Явно відкрита хостом (`Explicit Open`). |
| `0x04` | `BLK_ZONE_COND_CLOSED` | Закрита зона (`Closed`). |
| `0x0d` | `BLK_ZONE_COND_READONLY` | Зона у режимі лише читання (`Read Only`). |
| `0x0e` | `BLK_ZONE_COND_FULL` | Заповнена зона (`Full`), WP == start + capacity. |
| `0x0f` | `BLK_ZONE_COND_OFFLINE` | Зона виведена з експлуатації (`Offline`). |

Для правильної обробки відповідей від системного виклику `BLKREPORTZONE` код користувацького простору повинен перевіряти повернуте значення у полі `rep->nr_zones`. Якщо вказана кількість секторів диска охоплює більше зон, ніж розмір виділеного масиву, ядро заповнить лише перші `nr_zones` елементів, і для зчитання решти зон знадобиться повторний виклик зі зміщеним початковим сектором.

Потрібно також зважати на те, що поле `wp` (Write Pointer) повертається у 512-байтових секторах. Якщо зона перебуває у стані `Full`, значення `wp` завжди дорівнює `start + capacity`. Спроба обчислити розмір залишкового вільного місця у зоні виконується за формулою: `free_sectors = (cond == BLK_ZONE_COND_FULL) ? 0 : (start + capacity - wp)`.

## Виклики ioctl для управління зонами в C та C++

Для виконання скидання зони або запиту звіту про зони з програмного коду використовується системний виклик `ioctl()`. Нижче наведено порівняльний приклад виконання операції `BLKRESETZONE` мовами C та ідіоматичною C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/blkzoned.h>

int reset_single_zone(int fd, uint64_t zone_start_sector, uint64_t zone_size_sectors) {
    struct blk_zone_range range;
    range.sector = zone_start_sector;
    range.nr_sectors = zone_size_sectors;

    if (ioctl(fd, BLKRESETZONE, &range) < 0) {
        perror("BLKRESETZONE failed");
        return -1;
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <system_error>
#include <expected>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/blkzoned.h>

std::expected<void, std::error_code> reset_single_zone(int fd, std::uint64_t zone_start_sector, std::uint64_t zone_size_sectors) noexcept {
    struct blk_zone_range range{
        .sector = zone_start_sector,
        .nr_sectors = zone_size_sectors
    };

    if (::ioctl(fd, BLKRESETZONE, &range) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
```
:::

У C++ версії використовується сучасний тип `std::expected<void, std::error_code>` (доступний у C++23 чи через системні бібліотеки), що повністю виключає використання винятків на гарячому шляху виконання I/O операцій та надає зручний інтерфейс перевірки помилок через об'єкт `std::error_code`.

## Специфічні нативні команди NVMe ZNS (`<linux/nvme_ioctl.h>`)

Для виконання прямих апаратних команд NVMe уминувши універсальний шар Linux ZBD використовуються системні виклики `NVME_IOCTL_IO_CMD` або `NVME_IOCTL_ADMIN_CMD`. Це необхідно при розробці низькорівневих драйверів у користувацькому просторі (наприклад, у фреймворку SPDK або високопродуктивних плагінах баз даних).

### Коди команд (Opcode) специфікації NVMe ZNS

:::tabs
```c
#define nvme_zns_cmd_mgmt_send   0x79  /* Zone Management Send */
#define nvme_zns_cmd_mgmt_recv   0x7a  /* Zone Management Receive */
#define nvme_zns_cmd_append      0x7d  /* Zone Append */
```
```cpp
namespace nvme::zns {
constexpr std::uint8_t kCmdMgmtSend = 0x79;
constexpr std::uint8_t kCmdMgmtRecv = 0x7a;
constexpr std::uint8_t kCmdAppend   = 0x7d;
}
```
:::

### Дії команди Zone Management Send (поле ZSA - Zone Action)

При використанні opcode `0x79` (Zone Management Send) хост передає конкретний код дії в покроковому полі `dw13` команди:

| Код ZSA | Назва дії | Поведінка контролера ZNS |
| :--- | :--- | :--- |
| `0x01` | Close Zone | Переводить відкриту зону у стан `Closed`. |
| `0x02` | Finish Zone | Переводить зону у стан `Full` (WP зсувається на кінець ємності). |
| `0x03` | Open Zone | Переводить порожню або закриту зону у стан `Explicit Open`. |
| `0x04` | Reset Zone | Стирає зону, переводить у стан `Empty`, ставить WP = ZSLBA. |
| `0x05` | Offline Zone | Переводить зону у стан `Offline` (при апаратних тестах). |

### Структура апаратної команди Zone Append

При надсиланні команди `0x7d` (Zone Append) через `struct nvme_passthru_cmd`:

- `cdw10`: Початковий LBA зони (SLBA, нижчі 32 біти адреси ZSLBA).
- `cdw11`: Початковий LBA зони (SLBA, вищі 32 біти адреси ZSLBA).
- `cdw12`: Кількість логічних блоків (NLB, 0-based: `0` відповідає 1 блоку).
- `result`: Контролер SSD повертає фактично виділений LBA у вихідному 64-бітному полі результату CQE.

Нижче наведено приклад надсилання нативної команди `Zone Append` мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>

uint64_t submit_nvme_append_c(int fd, uint32_t nsid, uint64_t zslba, void *buf, size_t len) {
    uint32_t nlb = len / 512;
    struct nvme_passthru_cmd cmd;
    memset(&cmd, 0, sizeof(cmd));

    cmd.opcode      = 0x7d; /* Zone Append */
    cmd.nsid        = nsid;
    cmd.addr        = (uint64_t)(uintptr_t)buf;
    cmd.data_len    = len;
    cmd.cdw10       = (uint32_t)(zslba & 0xFFFFFFFF);
    cmd.cdw11       = (uint32_t)(zslba >> 32);
    cmd.cdw12       = nlb - 1; /* 0-based NLB */
    cmd.timeout_ms  = 1000;

    if (ioctl(fd, NVME_IOCTL_IO_CMD, &cmd) < 0) {
        perror("NVME_IOCTL_IO_CMD append failed");
        return (uint64_t)-1;
    }
    return cmd.result;
}
```
```cpp
#include <iostream>
#include <span>
#include <expected>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>

std::expected<std::uint64_t, std::error_code> submit_nvme_append_cpp(
    int fd, 
    std::uint32_t nsid, 
    std::uint64_t zslba, 
    std::span<const std::byte> buffer
) noexcept {
    uint32_t nlb = static_cast<uint32_t>(buffer.size() / 512);
    struct nvme_passthru_cmd cmd{};

    cmd.opcode      = 0x7d; // Zone Append
    cmd.nsid        = nsid;
    cmd.addr        = reinterpret_cast<std::uint64_t>(buffer.data());
    cmd.data_len    = static_cast<std::uint32_t>(buffer.size());
    cmd.cdw10       = static_cast<std::uint32_t>(zslba & 0xFFFFFFFF);
    cmd.cdw11       = static_cast<std::uint32_t>(zslba >> 32);
    cmd.cdw12       = nlb - 1; // 0-based NLB
    cmd.timeout_ms  = 1000;

    if (::ioctl(fd, NVME_IOCTL_IO_CMD, &cmd) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return cmd.result;
}
```
:::

Зауважте, що при використанні команди `Zone Append` у структурі `struct nvme_passthru_cmd` значення `cdw10` та `cdw11` приймають початковий адресований сектор всієї зони (ZSLBA), а не точну текучу позицію Write Pointer. Самостійний розрахунок Write Pointer на боці хоста не потрібен — контролер SSD виконає цей розрахунок атомарно.

## Специфічні коди помилок (Device Status Codes) контролера ZNS

При виконанні прямих викликів `NVME_IOCTL_IO_CMD` контролер NVMe може повертати спеціалізовані коди апаратного статусу (Status Field у CQE), які експортуються у системних журналах ядра та структурі команди:

| Код статусу | Назва помилки | Фізична причина виникнення |
| :--- | :--- | :--- |
| `0x0288` | Unaligned Write | Спроба виконати стандартний `WRITE` за адресою LBA, яка не збігається з поточним значенням Write Pointer (`LBA != WP`). |
| `0x0289` | Zone Boundary Error | Спроба записати дані, розмір яких виходить за межі корисної ємності зони (`WP + NLB > Zone Capacity`). |
| `0x028a` | Zone Is Full | Спроба запису у зону, яка перебуває у стані `Full`. |
| `0x028b` | Zone Is Read Only | Спроба запису або скидання зони, яка перейшла у стан `Read Only` через апаратний знос NAND. |
| `0x028c` | Zone Is Offline | Спроба будь-якої операції із зоною у стані `Offline` (фізична відмова кристала). |
| `0x028d` | Zone Invalid Write Pointer | Спроба надсилання команди дозапису `Zone Append` у зону, де Write Pointer є недійсним. |
| `0x028e` | Invalid Zone Action | Надсилання непідтримуваного коду дії ZSA у команді `Zone Management Send`. |
| `0x028f` | Zone Resources Exceeded | Перевищення апаратних лімітів MOR (відкриті зони) або MAR (активні зони) при спробі відкрити нову зону. |

Відстеження та правильне декодування цих апаратних кодів статусу є фундаментальною умовою створення стійких до помилок серверних застосунків. Наприклад, при отриманні коду `0x028f` (Zone Resources Exceeded) високонавантажена база даних не повинна аварійно завершувати роботу: вона має відправити команду `Zone Management Send` з дією `Close` для неактивної зони, звільнити ресурси контролера SSD, після чого повторити невдалу операцію запису.

Слід пам'ятати, що коди помилок NVMe витягуються з поля `cmd.result` або `errno` залежно від того, чи відхилено команду драйвером ядра, чи самим контролером накопичувача. Використання цих уніфікованих викликів та нативних команд NVMe забезпечує максимальну гнучкість при розробці низькорівневих систем зберігання даних у ядрі Linux та користувацькому просторі.
