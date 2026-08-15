# ⚙️ Читання й скидання покажчика запису зони через ioctl

Цей практичний проєкт демонструє низькорівневу взаємодію із зонованими блочними накопичувачами ZNS у системі Linux. У ньому наведено реалізацію утиліти, яка через системні виклики `ioctl` зчитує поточний стан покажчика запису (Write Pointer) апаратної зони та виконує її скидання за допомогою команди `BLKRESETZONE`.

Програму реалізовано у двох варіантах — мовою C з класичним управлінням ресурсами та мовою C++ з використанням ідіоми RAII (*Resource Acquisition Is Initialization*), системних винятків `std::system_error` та безпечних контейнерів `std::vector`.

---

## Принцип роботи та розбір системних викликів

Робота із зонованим пристроєм на рівні низькорівневих системних викликів базується на отриманні файлового дескриптора блочного пристрою `/dev/nvmeXnY` та надсиланні специфічних команд керування через виклик `ioctl(fd, request, structure)`.

### 1. Зчитування стану зони (BLKREPORTZONE)
Щоб дізнатися поточну позицію покажчика запису, програма повинна виділити буфер пам'яті під структуру `struct blk_zone_report`. Особливість цієї структури полягає в тому, що вона містить гнучкий масив (`flexible array member`) структур `struct blk_zone` наприкінці.
Виділений розмір буфера в байтах обчислюється наступним чином:
```
Розмір буфера = sizeof(struct blk_zone_report) + N × sizeof(struct blk_zone)
```
Де `N` — кількість зон, стан яких необхідно прочитати (у нашому прикладі `N = 1`).

Перед викликом `ioctl` програма ініціалізує поле `sector` початковим сектором зони (наприклад, `0`) та поле `nr_zones` значенням `1`. Після повернення з ядра поле `nr_zones` містить кількість реально повернутих записів, а у масиві `zones[0]` зберігаються параметри зони:
- `start`: початковий сектор зони в адресному просторі LBA.
- `len`: довжина зони в секторах.
- `wp`: поточна абсолютна позиція покажчика запису (Write Pointer).
- `cond`: апаратний стан зони (0x1 = EMPTY, 0x2 = IMPLICIT OPEN, 0x3 = EXPLICIT OPEN, 0x4 = CLOSED, 0xE = FULL).

### 2. Скидання покажчика запису (BLKRESETZONE)
Команда `BLKRESETZONE` приймає аргументом вказівник на структуру `struct blk_zone_range`, яка містить два поля:
- `sector`: початковий сектор зони, покажчик якої слід скинути.
- `nr_sectors`: довжина ділянки в секторах (повинна точно відповідати розміру зони або бути кратною йому).

Коли ядро отримує цей `ioctl`, воно формує блоковий запит `REQ_OP_ZONE_RESET` і надсилає його в чергу команд контролера NVMe ZNS. Контролер виконує апаратне стирання відповідного блоку NAND-флеш, переводить стан зони в `EMPTY` і повертає покажчик `wp` у значення `start`.

---

## Двомовна реалізація утиліти управління ZNS

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/blkzoned.h>

// Функція запиту стану зони ZNS накопичувача через ioctl(BLKREPORTZONE)
static int print_zone_report(int fd, unsigned long long start_sector) {
    // Обчислюємо розмір буфера з урахуванням одного елемента гнучкого масиву
    size_t rep_size = sizeof(struct blk_zone_report) + sizeof(struct blk_zone);
    struct blk_zone_report *rep = (struct blk_zone_report *)malloc(rep_size);
    if (!rep) {
        perror("Помилка виділення пам'яті під звіт зон");
        return -1;
    }

    memset(rep, 0, rep_size);
    rep->sector = start_sector;
    rep->nr_zones = 1;

    // Виконуємо системний виклик ioctl до ядра Linux
    if (ioctl(fd, BLKREPORTZONE, rep) < 0) {
        perror("Помилка виконання виклику BLKREPORTZONE");
        free(rep);
        return -1;
    }

    if (rep->nr_zones > 0) {
        struct blk_zone *z = &rep->zones[0];
        printf("Зона від сектора %llu: довжина=%llu, WP=%llu, стан=0x%x\n",
               (unsigned long long)z->start,
               (unsigned long long)z->len,
               (unsigned long long)z->wp,
               (unsigned int)z->cond);
    } else {
        printf("Зону за сектором %llu не знайдено на пристрої\n", start_sector);
    }

    free(rep);
    return 0;
}

// Функція скидання покажчика запису зони через ioctl(BLKRESETZONE)
static int reset_zone(int fd, unsigned long long start_sector, unsigned long long sector_count) {
    struct blk_zone_range range;
    range.sector = start_sector;
    range.nr_sectors = sector_count;

    if (ioctl(fd, BLKRESETZONE, &range) < 0) {
        perror("Помилка виконання виклику BLKRESETZONE");
        return -1;
    }

    printf("Успішно скинуто покажчик запису зони від сектора %llu (%llu секторів)\n",
           start_sector, sector_count);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s /dev/nvmeXnY\n", argv[0]);
        return 1;
    }

    // Відкриваємо блочний пристрій у режимі читання та запису (O_RDWR)
    int fd = open(argv[1], O_RDWR);
    if (fd < 0) {
        perror("Не вдалося відкрити зонований пристрій");
        return 1;
    }

    printf("=== Стан зони ДО скидання ===\n");
    if (print_zone_report(fd, 0) < 0) {
        close(fd);
        return 1;
    }

    printf("\nНадсилання команди BLKRESETZONE...\n");
    if (reset_zone(fd, 0, 524288) == 0) {
        printf("\n=== Стан зони ПІСЛЯ скидання ===\n");
        print_zone_report(fd, 0);
    }

    close(fd);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <stdexcept>
#include <system_error>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/blkzoned.h>

// RAII обгортка для безпечного управління файловим дескриптором ZNS пристрою
class ZnsDevice {
    int fd_{-1};

public:
    explicit ZnsDevice(const char* path) {
        fd_ = ::open(path, O_RDWR);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити ZNS пристрій");
        }
    }

    ~ZnsDevice() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    // Забороняємо копіювання файлового дескриптора (Rule of Five)
    ZnsDevice(const ZnsDevice&) = delete;
    ZnsDevice& operator=(const ZnsDevice&) = delete;

    // Дозволяємо переміщення (Move semantics)
    ZnsDevice(ZnsDevice&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    ZnsDevice& operator=(ZnsDevice&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }

    // Безпечне отримання звіту про стан зони з виділенням векторного буфера
    [[nodiscard]] blk_zone get_zone_info(std::uint64_t start_sector) const {
        std::size_t rep_size = sizeof(blk_zone_report) + sizeof(blk_zone);
        std::vector<std::uint8_t> buffer(rep_size, 0);

        auto* rep = reinterpret_cast<blk_zone_report*>(buffer.data());
        rep->sector = start_sector;
        rep->nr_zones = 1;

        if (::ioctl(fd_, BLKREPORTZONE, rep) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка ioctl(BLKREPORTZONE)");
        }

        if (rep->nr_zones == 0) {
            throw std::runtime_error("Зону за вказаним сектором не знайдено");
        }

        return rep->zones[0];
    }

    // Виконання апаратного скидання зони (BLKRESETZONE)
    void reset_zone(std::uint64_t start_sector, std::uint64_t sector_count) {
        blk_zone_range range{};
        range.sector = start_sector;
        range.nr_sectors = sector_count;

        if (::ioctl(fd_, BLKRESETZONE, &range) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка ioctl(BLKRESETZONE)");
        }
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " /dev/nvmeXnY\n";
        return 1;
    }

    try {
        ZnsDevice dev(argv[1]);

        std::cout << "=== Стан зони ДО скидання ===\n";
        auto z1 = dev.get_zone_info(0);
        std::cout << "Зона від сектора " << z1.start
                  << ": довжина=" << z1.len
                  << ", WP=" << z1.wp
                  << ", стан=0x" << std::hex << static_cast<unsigned int>(z1.cond) << std::dec << "\n";

        std::cout << "\nНадсилання команди BLKRESETZONE...\n";
        dev.reset_zone(0, 524288);

        std::cout << "\n=== Стан зони ПІСЛЯ скидання ===\n";
        auto z2 = dev.get_zone_info(0);
        std::cout << "Зона від сектора " << z2.start
                  << ": довжина=" << z2.len
                  << ", WP=" << z2.wp << "\n";

    } catch (const std::exception& ex) {
        std::cerr << "Виняток системи: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
```
:::

---

## Простеження операцій у ядрі через ftrace та bpftrace

Для того щоб пересвідчитися, що ядро Linux дійсно надсилає апаратні команди `Zone Reset` або `Zone Append` у накопичувач ZNS, розробники можуть використовувати підсистему простеження ядра (ftrace) або інструмент `bpftrace`.

### Інспекція подій блочного шару через tracepoints
Підсистема `block` ядра Linux містить спеціальні точки простеження (tracepoints) під операції Zone Management:

```bash
# Увімкнення простеження подій Zone Management у ftrace
echo 1 > /sys/kernel/tracing/events/block/block_bio_queue/enable
echo 1 > /sys/kernel/tracing/events/nvme/nvme_setup_cmd/enable

# Перегляд журналу простеження в реальному часі
grep -Ei "zone_reset|zone_append| ZR | ZA " /sys/kernel/tracing/trace_pipe
```

Типовий рядок виводу під час виконання команди `BLKRESETZONE`:
```text
  kworker/u16:3-1240 [002] .... 14205.123456: block_bio_queue: 259,1 ZR 524288 + 524288 [f2fs_gc_kthread]
  kworker/u16:3-1240 [002] .... 14205.123510: nvme_setup_cmd: nvme0n1, qid 2, cmdid 42, zone_reset, slba 524288
```
Двобуквений код `ZR` у полі `rwbs` виводу `block_bio_queue` вказує на `REQ_OP_ZONE_RESET`: усі зонні операції ядро позначає літерою `Z` і другою літерою дії — `ZA` (append), `ZF` (finish), `ZO` (open), `ZC` (close).

### Вимірювання часу формування NVMe-команди через bpftrace
Драйвер NVMe перетворює кожен `bio` на команду в функції `nvme_setup_cmd()` — саме там запит на скидання зони чи на `Zone Append` дістає свій код операції. Час, проведений у цій функції, показує вартість формування команди перед постановкою в чергу пристрою:

```bash
bpftrace -e 'kprobe:nvme_setup_cmd { @t[tid] = nsecs; }
             kretprobe:nvme_setup_cmd /@t[tid]/ { @ns = hist(nsecs - @t[tid]); delete(@t[tid]); }'
```
Ключем тут служить `tid`, а не аргумент функції: у `kretprobe` аргументи вже недоступні, доступне лише `retval`. Гістограма `@ns` покаже розподіл часу підготовки команди в наносекундах; сплески в ній означають затримку ще до того, як запит потрапив у чергу PCIe.

---

## Порівняльний аналіз та підводні камені реалізації

Під час розробки системного коду для зонованих пристроїв необхідно враховувати кілька важливих аспектів:

### 1. Управління ресурсами: C проти C++
- У варіанті мовою **C** буфер під `struct blk_zone_report` виділяється вручну через `malloc()` і вимагає явного виклику `free()` у кожній гілці обробки помилок. Помилка у зв'язці `open/close` або пропущений `free()` перед поворотом з функції викличуть витік ресурсів ядра або пам'яті.
- У варіанті мовою **C++** деструктор класу `ZnsDevice` гарантує закриття файлового дескриптора при виході з області видимості (зокрема під час викидання винятків). Виділення буфера через `std::vector<std::uint8_t>` усуває необхідність ручного виклику `free()`, задовольняючи концепції динамічної безпеки пам'яті RAII.

### 2. Прапорці відкриття пристрою
Для виконання запиту `BLKREPORTZONE` достатньо відкрити дескриптор у режимі тільки для читання (`O_RDONLY`). Однак для надсилання команди `BLKRESETZONE` або для запису через `Zone Append` пристрій **обов'язково повинен відкриватися в режимі читання та запису (`O_RDWR`)**, інакше ядро поверне помилку доступу `EBADF` (*Bad file descriptor*).

### 3. Вирівнювання параметрів секторів
Аргумент `sector` у структурі `struct blk_zone_range` **мусить точно відповідати початковому сектору зони** (`start`). Спроба надіслати `BLKRESETZONE` із сектором у середині зони викличе помилку `EINVAL` (*Invalid argument*). Крім того, значення `nr_sectors` має бути кратним розміру зони `chunk_sectors`.

### 4. Поведінка на незонованих пристроях
Якщо запустити наведений код на звичайному накопичувачі NVMe SSD або розділі SATA HDD, виклики `ioctl(BLKREPORTZONE)` та `ioctl(BLKRESETZONE)` завершаться з помилкою `ENOTTY` (*Inappropriate ioctl for device*) або `ENOTSUP` (*Operation not supported*), оскільки драйвер блочного шару перевіряє значення параметра `/sys/block/<dev>/queue/zoned` перед відправкою команди в апаратуру.
