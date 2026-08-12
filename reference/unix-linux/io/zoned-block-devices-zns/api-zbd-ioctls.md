# 📋 Системні ioctl-виклики та структури ZBD у Linux

Операційна система Linux надає низькорівневий двонаправлений інтерфейс викликів `ioctl()` та псевдо-ФС `sysfs` для опитування топології зон, моніторингу станів та управління вказівниками запису (Write Pointer) зонованих блокових пристроїв.

Прямий виклик `ioctl()` застосовується розробниками системного програмного забезпечення (баз даних, високопродуктивних двигунів сховищ, файлових систем), коли необхідний безпосередній контроль над апаратними зонами в оминанні традиційних стандартних шарів VFS.

---

## 1. Конфігурація та простеження через sysfs

Перш ніж надсилати команди до пристрою, процес користувацького простору повинен перевірити підтримку зонового режиму в підсистемі `block`. Інформація експортується через псевдо-файлову систему `sysfs` за шляхом `/sys/block/<dev>/queue/`:

### Основні параметри зонованого черги в sysfs

- `/sys/block/<dev>/queue/zoned`: Показує модель управління зонами пристрою.
  - `none`: Звичайний пристрій довільного доступу (не є ZBD).
  - `host-aware`: Пристрій Host-Aware (підтримує довільний запис, але надає звіт про зони).
  - `host-managed`: Суворий пристрій Host-Managed (вимагає послідовного запису за WP).
- `/sys/block/<dev>/queue/nr_zones`: Загальна кількість зон на пристрої (зокрема Conventional та SWR).
- `/sys/block/<dev>/queue/chunk_sectors`: Фізичний розмір зони (`Zone Size`), виражений у 512-байтових секторах. Згідно зі специфікацією NVMe ZNS, цей параметр обов'язково є ступенем двійки, що спрощує апаратну та системну адресацію зон у драйвері за допомогою швидкодіяльної побітової операції двійкового зсуву `LBA >> shift` замість коштовного ділення.
- `/sys/block/<dev>/queue/max_open_zones`: Максимальна кількість зон, які можуть одночасно перебувати у стані `Explicitly Open` або `Implicitly Open`. Значення `0` означає відсутність апаратного ліміту.
- `/sys/block/<dev>/queue/max_active_zones`: Максимальна кількість зон у станах, відмінних від `Empty` та `Full` (активні зони, що споживають ресурси SRAM контролера).
- `/sys/block/<dev>/queue/zone_append_max_bytes`: Максимальний обсяг даних (у байтах), який пристрій спроможний прийняти в рамках єдиної атомарної команди `Zone Append`.

Приклад перевірки параметрів у командному рядку:

```bash
$ cat /sys/block/nvme1n2/queue/zoned
host-managed
$ cat /sys/block/nvme1n2/queue/chunk_sectors
524288 # 524288 * 512 = 268435456 байтів (256 МБ)
$ cat /sys/block/nvme1n2/queue/max_open_zones
14
```

---

## 2. Заголовок та командні коди ioctl

Взаємодія з пристроєм через системний виклик `ioctl(fd, cmd, arg)` базується на константах, оголошених у системному заголовку `<linux/blkzoned.h>`.

:::tabs
```c
#include <linux/blkzoned.h>
#include <sys/ioctl.h>

// Основні управляючі командні коди ioctl підсистеми ZBD:
// BLKREPORTZONES — заповнення масиву описувачів зон для вказаного діапазону LBA
// BLKRESETZONE   — апаратне скидання вказівника запису (Write Pointer) у 0
// BLKOPENZONE    — явний перехід зони в стан Explicitly Opened
// BLKCLOSEZONE   — явний перехід зони в стан Closed (звільнення ресурсів кешу)
// BLKFINISHZONE  — дострокове переведення частково записаної зони у стан Full
// BLKGETZONESZ   — швидке отримання розміру зони в 512-байтових секторах
// BLKGETNRZONES  — швидке отримання загальної кількості зон пристрою
```
```cpp
#include <linux/blkzoned.h>
#include <sys/ioctl.h>
#include <cstdint>

// Основні управляючі командні коди ioctl підсистеми ZBD (C++ UAPI):
// BLKREPORTZONES — заповнення масиву описувачів зон для вказаного діапазону LBA
// BLKRESETZONE   — апаратне скидання вказівника запису (Write Pointer) у 0
// BLKOPENZONE    — явний перехід зони в стан Explicitly Opened
// BLKCLOSEZONE   — явний перехід зони в стан Closed (звільнення ресурсів кешу)
// BLKFINISHZONE  — дострокове переведення частково записаної зони у стан Full
// BLKGETZONESZ   — швидке отримання розміру зони в 512-байтових секторах
// BLKGETNRZONES  — швидке отримання загальної кількості зон пристрою
```
:::

Виклики `BLKGETZONESZ` та `BLKGETNRZONES` є найшвидшим способом дізнатися про параметри пристрою без зчитування інформації з `sysfs`. Вони приймають вказівник на змінну типу `unsigned int` або `uint32_t` і повертають значення безпосередньо з кешу ядра.

---

## 3. Структури опитування та звіту про зони

Для отримання топології зон додаток виділяє пам'ять під структуру `struct blk_zone_report`, за якою безпосередньо слідує буфер для масиву елементів `struct blk_zone`.

:::tabs
```c
struct blk_zone_report {
    __u64 sector;       // Початковий сектор (LBA), з якого починати звіт
    __u32 nr_zones;     // Вхід: розмір масиву; Вихід: кількість повернутих зон
    __u32 flags;        // Прапорці фільтрації звіту (наприклад, 0)
    struct blk_zone zones[0]; // Гнучкий масив результатів звіту
};

struct blk_zone {
    __u64 start;        // Початковий сектор зони (у 512-байтових одиницях)
    __u64 len;          // Загальний фізичний розмір зони у секторах (Zone Size)
    __u64 wp;           // Поточна позиція вказівника запису Write Pointer (сектор)
    __u8  type;         // Тип зони (Conventional або SeqWrite)
    __u8  cond;         // Поточний стан зони (Empty, Open, Full тощо)
    __u8  non_seq;      // Прапорець непослідовного запису (для Host-Aware)
    __u8  reset;        // Прапорець вимоги скидання зони
    __u8  resv[4];      // Резервні байти для вирівнювання
    __u64 capacity;     // Дійсний обсяг доступних для запису секторів (Zone Capacity)
    __u8  reserved[24]; // Падінг структури до 64 байтів
};
```
```cpp
// У C++ вирівнювання та масив зон обробляються через динамічний буфер або std::vector
struct blk_zone_report {
    std::uint64_t sector;   // Початковий сектор (LBA), з якого починати звіт
    std::uint32_t nr_zones; // Вхід: розмір масиву; Вихід: повернуто зон
    std::uint32_t flags;    // Прапорці фільтрації звіту
    struct blk_zone zones[0]; // Динамічний контент зон
};

struct blk_zone {
    std::uint64_t start;    // Початковий сектор зони (у 512-байтових одиницях)
    std::uint64_t len;      // Фізичний розмір зони у секторах (Zone Size)
    std::uint64_t wp;       // Поточна позиція вказівника запису Write Pointer
    std::uint8_t  type;     // Тип зони (Conventional або SeqWrite)
    std::uint8_t  cond;     // Поточний стан зони (Empty, Open, Full тощо)
    std::uint8_t  non_seq;  // Прапорець непослідовного запису
    std::uint8_t  reset;    // Прапорець вимоги скидання зони
    std::uint8_t  resv[4];  // Резервні байти вирівнювання
    std::uint64_t capacity; // Дійсна ємність зони у секторах (Zone Capacity)
    std::uint8_t  reserved[24]; // Фіксований падінг структури
};
```
:::

### Деталізація типів та станів зон у масиві дій

Поле `type` описує правила доступу до зони згідно зі специфікацією UAPI ядра Linux `<linux/blkzoned.h>`:
- `BLK_ZONE_TYPE_CONVENTIONAL` (`0x01`): Довільний запис у будь-який сектор без обмежень WP (апаратно забезпечується CMR-доріжками на SMR або FTL-зонами на ZNS SSD).
- `BLK_ZONE_TYPE_SEQWRITE_REQ` (`0x02`): Сувора вимога послідовного запису за вказівником `wp`.

Поле `cond` (Zone Condition) відображає поточний стан зони в кінцевому автоматі пристрою:
- `BLK_ZONE_COND_EMPTY` (`0x00`): Зона порожня. `wp == start`.
- `BLK_ZONE_COND_IMP_OPEN` (`0x01`): Неявно відкрита контролером при отриманні запису.
- `BLK_ZONE_COND_EXP_OPEN` (`0x02`): Явно відкрита хостом командою `BLKOPENZONE`.
- `BLK_ZONE_COND_CLOSED` (`0x03`): Закрита хостом (`BLKCLOSEZONE`) або витіснена контролером.
- `BLK_ZONE_COND_FULL` (`0x04`): Зона заповнена повністю. `wp == start + capacity`.
- `BLK_ZONE_COND_READONLY` (`0x0d`): Зона доступна лише для читання через фізичні помилки або знос.
- `BLK_ZONE_COND_OFFLINE` (`0x0e`): Зона повністю виведена з експлуатації (апаратно пошкоджена).

---

## 4. Алгоритм пагінації при ітерації по зонах (`BLKREPORTZONES`)

Приватний пристрій може містити десятки тисяч зон. Запит інформації про всі зони в рамках одного системного виклику вимагав би виділення десятків мегабайтів безперервної пам'яті ядра.

Для запобігання переповненню розробники застосовують пагінований цикл ітерації:

1. Додаток виділяє буфер під `struct blk_zone_report` + N елементів `struct blk_zone` (наприклад, 1024 зони).
2. Початковий сектор `rep->sector` встановлюється в 0.
3. Викликається `ioctl(fd, BLKREPORTZONES, rep)`.
4. Обробляється `rep->nr_zones` повернутих елементів.
5. Для наступної ітерації `rep->sector` встановлюється у значення `start + len` останньої повернутої зони.
6. Цикл повторюється, доки `rep->nr_zones` не дорівнюватиме 0.

---

## 5. Операції змінення стану зон: `struct blk_zone_range`

Для виконання дій над зонами (скидання WP, відкриття, закриття, фіналізація) використовується структура `struct blk_zone_range`.

:::tabs
```c
struct blk_zone_range {
    __u64 sector;       // Початковий сектор зони (LBA)
    __u64 nr_sectors;   // Сумарна кількість секторів у діапазоні для виконання дії
};
```
```cpp
struct blk_zone_range {
    std::uint64_t sector;     // Початковий сектор зони (LBA)
    std::uint64_t nr_sectors; // Сумарна кількість секторів для зміни стану
};
```
:::

### Опис операцій керування діапазоном

1. **`BLKRESETZONE`**: Приймає `struct blk_zone_range`. Очищає зони у вказаному діапазоні. Пристрій атомарно скидає вказівник запису на початок зони (`wp = start`) та переводить її в стан `Empty`. На ZNS SSD це викликає фізичне стирання блоків флеш-пам'яті (`Erase Block`). Якщо вказати `nr_sectors`, що охоплює весь диск, пристрій виконає загальне скидання всіх зон.
2. **`BLKOPENZONE`**: Переводить зони в стан `Explicitly Opened`. Гарантує, що пристрій виділив апаратні ресурси контролера і подальші операції запису не зазнають невдачі через вичерпання активних зон.
3. **`BLKCLOSEZONE`**: Звільняє апаратні ресурси відкритих зон, переводячи їх у стан `Closed`.
4. **`BLKFINISHZONE`**: Переводить частково записану зону в стан `Full`. Вказівник `wp` примусово встановлюється на `start + capacity`. Використовується, коли додаток більше не планує дописувати дані в дану зону і хоче звільнити ліміт `max_open_zones`.

---

## 6. Коди помилок системних викликів ioctl та крайові випадки

При порушенні контракту ZBD системний виклик `ioctl()` повертає `-1` та встановлює змінну `errno` у відповідне значення. Розробник системного ПЗ мусить обробляти наступні ситуації:

| Значення `errno` | Причина виникнення помилки | Спосіб обробки у системному ПЗ |
| :--- | :--- | :--- |
| `EINVAL` | Некоректний початковий сектор LBA (не вирівняний на початок зони) або некоректні розміри діапазону `nr_sectors`. | Перевірити, що `sector % chunk_sectors == 0`. |
| `EIO` | Апаратна помилка пристрою (Unaligned Write, запис у Full зону, фізичний збій медиа). | Прочитати звіт зони (`BLKREPORTZONES`), перевірити стан `cond`. |
| `EOPNOTSUPP` | Ядро або базовий блоковий пристрій не підтримують зонові ioctl (наприклад, звичайний SATA SSD). | Перевірити `/sys/block/<dev>/queue/zoned`. |
| `EBUSY` | Досягнуто апаратного ліміту відкритих зон (`max_open_zones` / `max_active_zones`), пристрій відхилив відкриття нової зони. | Закрити застарілі зони викликом `BLKCLOSEZONE` або `BLKFINISHZONE`. |
| `ENOSPC` | Спроба запису за межі ємності зони (`Zone Capacity`). | Перевірити `wp + len <= start + capacity`. |

---

## 7. Бібліотека вищого рівня `libzbd`

Для спрощення розробки користувацьких додатків проєкт Linux Management Utilities надає користувацьку бібліотеку `libzbd` (`libzbd-dev`). Вона обгортає прямі виклики `ioctl()` у високорівневі C-функції:

:::tabs
```c
#include <libzbd/zbd.h>

// Основні функції бібліотеки libzbd:
// zbd_open() — відкриття блокового пристрою ZBD
// zbd_get_info() — зчитування загальних параметрів (розмір зони, кількість зон)
// zbd_report_zones() — повернення динамічного масиву секторів
// zbd_reset_zones() — скидання вказаного діапазону зон
// zbd_finish_zones() — примусова фіналізація зон
```
```cpp
#include <libzbd/zbd.h>
#include <memory>
#include <system_error>

// C++ Обгортка для роботи з libzbd
class ZbdDevice {
private:
    int m_fd{-1};
    struct zbd_info m_info{};

public:
    explicit ZbdDevice(const char* filename) {
        m_fd = zbd_open(filename, O_RDWR, &m_info);
        if (m_fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити ZBD пристрій через libzbd");
        }
    }

    ~ZbdDevice() {
        if (m_fd >= 0) zbd_close(m_fd);
    }

    [[nodiscard]] uint32_t zone_size() const noexcept { return m_info.zone_size; }
    [[nodiscard]] uint32_t nr_zones() const noexcept { return m_info.nr_zones; }
};
```
:::

Використання `libzbd` рекомендується для складних проектів (таких як ZenFS для RocksDB), оскільки вона автоматично обробляє відмінності між версіями ядер Linux та надає сумісність із різними типами інтерфейсів (SCSI ZBC, ATA ZAC та NVMe ZNS).

---

## 8. Приклад прямого використання ioctl у C та C++

Нижче наведено фрагменти коду для виконання виклику `BLKRESETZONE` безпосередньо над файловим дескриптором пристрою.

:::tabs
```c
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/blkzoned.h>

int reset_single_zone(int dev_fd, uint64_t zone_start_sector, uint64_t zone_size_sectors) {
    struct blk_zone_range range;
    range.sector = zone_start_sector;
    range.nr_sectors = zone_size_sectors;

    if (ioctl(dev_fd, BLKRESETZONE, &range) < 0) {
        perror("Помилка виконання ioctl(BLKRESETZONE)");
        return -1;
    }

    printf("Зону за сектором %lh успішно скинуто в Empty\n", zone_start_sector);
    return 0;
}
```
```cpp
#include <iostream>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/blkzoned.h>

void reset_single_zone_cpp(int dev_fd, std::uint64_t zone_start_sector, std::uint64_t zone_size_sectors) {
    struct blk_zone_range range{};
    range.sector = zone_start_sector;
    range.nr_sectors = zone_size_sectors;

    if (::ioctl(dev_fd, BLKRESETZONE, &range) < 0) {
        throw std::system_error(errno, std::generic_category(), "Помилка виконання ioctl BLKRESETZONE");
    }

    std::cout << "Зону за сектором " << zone_start_sector << " успішно скинуто у C++\n";
}
```
:::
