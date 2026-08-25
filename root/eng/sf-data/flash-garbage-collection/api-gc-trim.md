# 📋 Інтерфейс керування збиранням сміття: TRIM, Discard та sysfs-інтерфейси

Ця вставка містить системну довідку щодо програмних та апаратних інтерфейсів, які дозволяють операційній системі та прикладним програмам взаємодіяти із збирачем сміття у Flash-накопичувачах. Розглянуто системний виклик Linux `ioctl(FITRIM)`, параметри підсистеми блокових пристроїв sysfs, а також структури команд вищого рівня ATA TRIM, NVMe Dataset Management Deallocate та eMMC ERASE/TRIM.

---

## 1. Програмний інтерфейс Linux: `ioctl(FITRIM)`

На рівні операційної системи Linux основним засобом явного виклику збирання сміття є системний виклик `ioctl` із прапором `FITRIM` (декларований у системному заголовку `<linux/fs.h>`). Виклик надсилається до файлового дескриптора змонтованої файлової системи й примушує її виявити всі невикористані блоки та відправити відповідні команди TRIM/Deallocate на накопичувач.

### Структура даних `struct fstrim_range`

:::tabs
```c
struct fstrim_range {
    uint64_t start;   /* Початковий логічний зсув у байтах */
    uint64_t len;     /* Довжина діапазону для очищення у байтах */
    uint64_t minlen;  /* Мінімальний розмір вільного фрагмента у байтах */
};
```
```cpp
// Декларація структури із заголовку <linux/fs.h> у C++
struct fstrim_range {
    uint64_t start;   // Початковий логічний зсув у байтах
    uint64_t len;     // Довжина діапазону для очищення у байтах
    uint64_t minlen;  // Мінімальний розмір вільного фрагмента у байтах
};
```
:::

#### Детальний опис полів структури `fstrim_range`:
- `start`: початковий байтовий зсув від початку файлової системи, з якого починається сканування вільних блоків. Для очищення всієї файлової системи передають `0`.
- `len`: обсяг діапазону сканування у байтах. Значення `UINT64_MAX` (або `(uint64_t)-1`) означає сканування до самого кінця місткості файлової системи. Після завершення виклику ядро перезаписує це поле фактичною кількістю байтів, які були підтверджені накопичувачем як очищені.
- `minlen`: мінімальний розмір неперервного відрізка вільних блоків у байтах, який варто надсилати у TRIM. Повідомлення накопичувача про дрібні фрагменти (наприклад, 4 КБ) створює надмірний накладний час на автобусі PCIe або SATA. Значення `minlen = 1048576` (1 МБ) наказує файловій системі ігнорувати дрібні дірки й надсилати тільки великі неперервні масиви, що ідеально відповідає розмірам стиральних блоків (*eraseblocks*) контролера FTL.

### Права доступу та сумісність
Для виконання виклику `ioctl(FITRIM)` процес мусить мати привілеї суперкористувача (привілей `CAP_SYS_ADMIN`). Виклик підтримується основними файловими системами Linux: `ext4`, `xfs`, `btrfs`, `f2fs` та `vfat`.

---

## 2. Приклади використання `FITRIM` мовами C та C++

Нижче наведено повні реалізації системних утиліт мовами C та C++17 для виконання примусової очистки файлової системи.

:::tabs
```c
/* fstrim_example.c — Виклики FITRIM системним API у C */
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/fs.h>
#include <errno.h>
#include <string.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <точка_монтування>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *mount_point = argv[1];
    int fd = open(mount_point, O_RDONLY | O_DIRECTORY);
    if (fd < 0) {
        perror("Помилка відкриття точки монтування");
        return EXIT_FAILURE;
    }

    struct fstrim_range range;
    memset(&range, 0, sizeof(range));
    range.start = 0;
    range.len = (uint64_t)-1; /* До кінця диска */
    range.minlen = 1024 * 1024; /* Мінімальний блок: 1 МБ */

    printf("Надсилання FITRIM для %s (minlen = %llu байтів)...\n", 
           mount_point, (unsigned long long)range.minlen);

    if (ioctl(fd, FITRIM, &range) < 0) {
        perror("Помилка виконання ioctl(FITRIM)");
        close(fd);
        return EXIT_FAILURE;
    }

    printf("Успішно! Звільнено накопичувачем: %llu байтів (%.2f МБ)\n",
           (unsigned long long)range.len,
           (double)range.len / (1024.0 * 1024.0));

    close(fd);
    return EXIT_SUCCESS;
}
```
```cpp
// fstrim_example.cpp — Ідіоматичний виклик FITRIM у C++17
#include <iostream>
#include <filesystem>
#include <system_error>
#include <string_view>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/fs.h>

class FileDescriptor {
public:
    explicit FileDescriptor(const std::filesystem::path& path) {
        fd_ = ::open(path.c_str(), O_RDONLY | O_DIRECTORY);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити каталог");
        }
    }

    ~FileDescriptor() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    [[nodiscard]] int get() const noexcept { return fd_; }

private:
    int fd_{-1};
};

uint64_t execute_fstrim(const std::filesystem::path& mount_point, uint64_t minlen_bytes = 1048576) {
    FileDescriptor fd(mount_point);

    fstrim_range range{};
    range.start = 0;
    range.len = static_cast<uint64_t>(-1);
    range.minlen = minlen_bytes;

    if (::ioctl(fd.get(), FITRIM, &range) < 0) {
        throw std::system_error(errno, std::generic_category(), "Помилка виконання ioctl(FITRIM)");
    }

    return range.len;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <точка_монтування>\n";
        return EXIT_FAILURE;
    }

    try {
        std::filesystem::path mount_point = argv[1];
        std::cout << "Виконання TRIM для: " << mount_point << "...\n";
        
        uint64_t trimmed_bytes = execute_fstrim(mount_point);
        
        std::cout << "Успішно! FTL підтвердив очищення: " << trimmed_bytes << " байтів ("
                  << static_cast<double>(trimmed_bytes) / (1024.0 * 1024.0) << " МБ)\n";
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

---

## 3. Детальний аналіз реалізації програмних викликів

Розберемо кроки виконання коду:
1. **Відкриття точки монтування**: функція `open()` відкриває каталог монтування (наприклад, `/mnt/data`) із прапорцем `O_DIRECTORY`. Це важливо, бо `ioctl(FITRIM)` працює лише над дескрипторами змонтованої файлової системи, а не сирими дескрипторами диска (`/dev/sda`).
2. **Ініціалізація діапазону**: заповнення структури `fstrim_range` із вказуванням `minlen = 1024 * 1024`. Якщо встановити `minlen = 0`, файлова система надсилатиме TRIM навіть на поодинокі вільні сектори по 4 КБ, що призведе до сплеску затримок на шині.
3. **Обробка результату**: системний виклик `ioctl` модифікує значення `range.len` на місці, записуючи туди кількість реально відправлених байтів.

---

## 4. Ядерний рівень Linux: функція `blkdev_issue_discard()`

Всередині ядра Linux, при написанні файлових систем або системних драйверів, відправка команд Discard здійснюється безпосередньо через блоковий шар (*block layer*) за допомогою функції `blkdev_issue_discard()`, що оголошена в кодовій базі ядра у `<linux/bio.h>`:

:::tabs
```c
int blkdev_issue_discard(struct block_device *bdev, 
                         sector_t sector, 
                         sector_t nr_sects,
                         gfp_t gfp_mask, 
                         unsigned long flags);
```
```cpp
// Сигнатура функції ядра для виклику в C++
int blkdev_issue_discard(struct block_device *bdev, 
                         sector_t sector, 
                         sector_t nr_sects,
                         gfp_t gfp_mask, 
                         unsigned long flags);
```
:::

### Параметри внутрішньоядерного API:
- `bdev`: вказівник на структуру блокового пристрою ядра.
- `sector`: початковий сектор диска (у 512-байтових блоках).
- `nr_sects`: кількість секторів для знецінення.
- `gfp_mask`: маска виділення пам'яті ядра (наприклад, `GFP_KERNEL` або `GFP_NOFS`).
- `flags`: додаткові прапорці керування синхронністю операції.

Драйвер файлової системи вираховує межі вільних екстентів (*extents*) і викликає `blkdev_issue_discard()`. Блоковий шар ядра розбиває запит на окремі пакети `struct bio` із прапором `REQ_OP_DISCARD` і передає їх у чергу команд конкретного контролера носія.

---

## 5. Інтерфейси керування дисковим шаром Linux: `/sys/block/sdX/queue/`

Ядро Linux експортує параметри підтримки TRIM/Discard через псевдо-файлову систему sysfs. Ці параметри доступні за шляхом `/sys/block/<device>/queue/`.

| Файл у sysfs | Опис і значення |
| :--- | :--- |
| `discard_granularity` | Мінімальний квант вирівнювання застарілих сторінок у байтах (зазвичай 4096 або 512 000). |
| `discard_max_bytes` | Максимальний обсяг даних, який може бути передано в одній апаратній команді TRIM. |
| `discard_max_hw_bytes` | Апаратна верхня межа контролера накопичувача. |
| `discard_zeroes_data` | Прапор (`1` або `0`): чи гарантує контролер читання нулів із за-TRIM-ованих LBA. |
| `discard_max_discard_segments` | Максимальна кількість незв'язаних діапазонів LBA в одном пакеті команди. |

### Пояснення функціоналу вирівнювання (Discard Granularity)
Значення `discard_granularity` показує внутрішній розмір фізичного блоку FTL. Якщо файлова система надсилає запит на TRIM для діапазону LBA, який не вирівняний по цій межі, ядро відтинає невирівняні краї, щоб запобігти випадковому знеціненню сусідніх чинних даних у тому самому eraseblock.

### Опитування параметрів Discard через CLI

```bash
# Перевірка підтримки TRIM диском /dev/sda (значення > 0 означає підтримку)
cat /sys/block/sda/queue/discard_max_bytes

# Отримання гранулярності стирання
cat /sys/block/sda/queue/discard_granularity
```

---

## 6. Протокольний шар: апаратні команди TRIM, Deallocate та eMMC ERASE

Коли виклик `FITRIM` проходить крізь файлову систему й драйвер блокового пристрою, ядро формує конкретну пакетовану команду залежно від типу інтерфейсу носія.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          ІЄРАРХІЯ ВИКЛИКІВ TRIM                         │
├─────────────────────────────────────────────────────────────────────────┤
│ Програма користувача:       fstrim_example / fstrim / ioctl(FITRIM)     │
│                                           │                             │
│ Файлова система:            ext4 / xfs / btrfs (звільнення extents)     │
│                                           │                             │
│ Блоковий шар Linux:         blkdev_issue_discard()                      │
│                                           │                             │
│ Драйвер шини:               nvme.ko                     ahci.ko         │
│                                           │                        │    │
│ Фізична команда шини:   NVMe Deallocate             ATA DATA SET MGMT   │
│                         (Command Opcode 0x09)       (Feature 0x06 TRIM) │
└─────────────────────────────────────────────────────────────────────────┘
```

### ATA Data Set Management (SATA TRIM)
В інтерфейсі ATA команда TRIM реалізована як підфункція команди `DATA SET MANAGEMENT` (командний код `0x06`).
- Оперує кадрами розміром 512 байтів (один сектор кадру може описати до 64 діапазонів LBA).
- Кожен діапазон описується 64-бітним полем:
  - 48 бітів: початковий LBA.
  - 16 бітів: кількість секторів у діапазоні (до 65 535 секторів).

### NVMe Dataset Management (Deallocate)
В інтерфейсі NVM Express операція TRIM реалізована через команду `Dataset Management` (Opcode `0x09`) із встановленим атрибутом `AD` (*Attribute Deallocate*, біт 2).

#### Структура описувача діапазону NVMe (NVMe Range Descriptor):

:::tabs
```c
struct nvme_dsm_range {
    uint32_t attributes;     /* Додаткові прапори контексту (Hot/Cold) */
    uint32_t length;         /* Довжина діапазону в блоках LBA */
    uint64_t slba;           /* Початковий LBA (Starting LBA) */
};
```
```cpp
// Описувач діапазону NVMe у C++
struct nvme_dsm_range {
    uint32_t attributes;     // Додаткові прапори контексту (Hot/Cold)
    uint32_t length;         // Довжина діапазону в блоках LBA
    uint64_t slba;           // Початковий LBA (Starting LBA)
};
```
:::

Одна команда NVMe Dataset Management може передавати масив із 256 таких структур у паці даних, дозволяючи операційній системі одночасно повідомити FTL про сотні видалених фрагментів файлів за одну операцію доступу до контролера.

### eMMC / SD Card TRIM та ERASE (JEDEC eMMC Standard)
У вбудованих сховищах eMMC (стандарт JEDEC JESD84-B51) операції інформування FTL реалізовано через послідовність команд шини SD/MMC:
- `CMD35 (ERASE_GROUP_START)` — встановлення початкового блоку.
- `CMD36 (ERASE_GROUP_END)` — встановлення кінцевого блоку.
- `CMD38 (ERASE)` з аргументом `0x00000001` (TRIM) або `0x00000000` (Erase).

Параметризований виклик `CMD38` дозволяє eMMC контролеру відрізнити негайне апаратне стирання від відкладеної позначки для збирача сміття.

---

## 7. Криміналістичні та безпекові наслідки TRIM

Виконання команди TRIM змінює поведінку читання фізичних секторів:
- **Deterministic Read Zero after TRIM (RZAT)**: контролер підтверджує, що будь-яке читання LBA після TRIM повертатиме суто логічні нулі (`0x00`).
- **Deterministic Read after TRIM (DRAT)**: контролер гарантує читання сталого значення після TRIM (може бути не нуль, а `0xFF`).
- **Non-deterministic Read**: контролер повертає сміття або старі дані до моменту реального стирання блоку.

З погляду цифрової криміналістики (*Digital Forensics*), задіяний TRIM унеможливлює традиційне відновлення видалених файлів (*file carving*): після відправки TRIM індекси L2P миттєво обнуляються, і спроба прочитати за-TRIM-овані сектори повертає нулі, навіть якщо фізичні комірки NAND ще не були біологічно стерті високовольтним імпульсом.
