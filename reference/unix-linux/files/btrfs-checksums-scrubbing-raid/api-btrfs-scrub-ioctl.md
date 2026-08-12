# 🔌 Програмний інтерфейс ioctl підсистеми Btrfs Scrub

Підсистема фонового сканування та відновлення цілісності **Btrfs Scrubbing** надає програмний інтерфейс низького рівня на основі системних викликів `ioctl`. Це дозволяє утилітам системного моніторингу, демонам автоматизації (таким як `btrfsmaintenance` або `systemd` timers) та інструментам керування сховищами запускати перевірку блоків, скасовувати активні операції або отримувати розгорнуту статистику збоїв безпосередньо з ядра Linux.

Усі константи, прапорці керування та структурні типи даних підсистеми scrub оголошені у системному заголовочному файлі ядра `<linux/btrfs.h>`.

## Системні виклики ioctl та константи керування

Управління процедурою scrub здійснюється через три системні виклики `ioctl`, які виконуються над відкритою файловим дескриптором директорією монтування Btrfs:

| Команда ioctl | Аргумент (покажчик) | Опис та внутрішня логіка дії |
| :--- | :--- | :--- |
| `BTRFS_IOC_SCRUB` | `struct btrfs_ioctl_scrub_args*` | Ініціалізує фонове сканування для вказаного пристрою `devid`. За замовчуванням блокує викликаючий процес до повного обходу накопичувача, якщо не вказано додаткові прапорці. |
| `BTRFS_IOC_SCRUB_CANCEL` | `struct btrfs_ioctl_scrub_args*` | Перериває роботу фонового потоку scrub ядра для вказаного пристрою `devid`. |
| `BTRFS_IOC_SCRUB_PROGRESS` | `struct btrfs_ioctl_scrub_args*` | Запитує поточний стан лічильників просканованих байтів та виявлених помилок без зупинки процесу сканування. |

У разі спроби повторного запуску `BTRFS_IOC_SCRUB` для пристрою, де вже виконується сканування, ядро повертає код помилки `-EBUSY`. Якщо передано неіснуючий ідентифікатор пристрою `devid`, виклики `ioctl` повертають `-ENODEV`.

## Опис структур btrfs_ioctl_scrub_args та btrfs_scrub_progress

Основний обмін даними між користувацьким простором (userspace) та ядром виконується через структуру `btrfs_ioctl_scrub_args`:

:::tabs
```c
// Оголошення структур у системному заголовочному файлі <linux/btrfs.h>
struct btrfs_ioctl_scrub_args {
    __u64 devid;                // ID фізичного пристрою у масиві Btrfs (збігається з btrfs dev show)
    __u64 start;                // Початкова логічна дискова адреса для сканування (bytenr)
    __u64 end;                  // Кінцева логічна дискова адреса (або (u64)-1 для сканування всього диска)
    __u64 flags;                // Прапорці керування (BTRFS_SCRUB_READONLY)
    struct btrfs_scrub_progress progress; // Підсумкові та поточні лічильники цілісності
    __u64 unused[6 * 8 - 1];    // Резервні поля для сумісності з майбутніми версіями ядра
};
```
```cpp
// C++ аналог структури аргументів з ініціалізацією за замовчуванням
#include <cstdint>
#include <linux/btrfs.h>

namespace btrfs::api {

struct ScrubArgs {
    std::uint64_t devid{0};
    std::uint64_t start{0};
    std::uint64_t end{static_cast<std::uint64_t>(-1)};
    std::uint64_t flags{0};
    btrfs_scrub_progress progress{};
};

} // namespace btrfs::api
```
:::

Деталізована статистика сканування повертається у вкладеній структурі `btrfs_scrub_progress`:

:::tabs
```c
// Структура лічильників статистики scrub у ядрі Linux
struct btrfs_scrub_progress {
    __u64 data_extents_scrubbed;  // Кількість просканованих екстентів даних
    __u64 tree_extents_scrubbed;  // Кількість просканованих вузлів B-дерев метаданих
    __u64 data_bytes_scrubbed;    // Загальний обсяг просканованих байтів даних
    __u64 tree_bytes_scrubbed;    // Загальний обсяг просканованих байтів метаданих
    __u64 read_errors;            // Апаратні помилки зчитування з диска (I/O Errors)
    __u64 csum_errors;            // Помилки незбігу контрольних сум CRC32c / xxHash / SHA256
    __u64 verify_errors;          // Помилки валідації заголовків метаданих (bad generation/owner)
    __u64 uncorrectable_errors;   // Фатальні помилки, які не вдалося відновити з RAID-копій!
    __u64 corrected_errors;       // Успішно відновлені спотворення завдяки самоновленню з RAID-дзеркала
    __u64 last_physical;          // Останній фізичний сектор, оброблений на пристрої
    __u64 unverified_errors;      // Непідтверджені збої читання
};
```
```cpp
// C++ форматування підсумкової статистики scrub
#include <iostream>
#include <linux/btrfs.h>

inline void printScrubProgress(const btrfs_scrub_progress& p) {
    std::cout << "--- Статистика цілісності Btrfs Scrub ---\n"
              << "Проскановано даних: " << (p.data_bytes_scrubbed / (1024 * 1024)) << " МБ\n"
              << "Проскановано метаданих: " << (p.tree_bytes_scrubbed / (1024 * 1024)) << " МБ\n"
              << "Апаратних помилок читання: " << p.read_errors << "\n"
              << "Помилок хешу CRC32c: " << p.csum_errors << "\n"
              << "Виправлено з RAID: " << p.corrected_errors << "\n"
              << "НЕВІДНОВЛЮВАНИХ помилок: " << p.uncorrectable_errors << std::endl;
}
```
:::

### Помилки та інтерпретація лічильників

Поля структури `btrfs_scrub_progress` класифікують стан цілісності накопичувачів за кількома категоріями:

- `read_errors`: Апаратні помилки зчитування секторів з носія (Low-level Controller / Bad Sectors). Свідчать про фізичну зношеність пристрою.
- `csum_errors`: Випадки, коли сектор прочитано без апаратної помилки, але його CRC32c не збігається з хешем із `CSUM Tree` (Silent Bit Rot).
- `verify_errors`: Помилки логічної валідації заголовків B-дерев метаданих (наприклад, розбіжність генерації транзакції `generation` або незбіг `owner`).
- `corrected_errors`: Кількість пошкоджених секторів, які Btrfs успішно відновила під час сканування шляхом зчитування резервної копії з RAID1 / RAID10 / DUP та її запису поверх зіпсованого сектора.
- `uncorrectable_errors`: Кількість пошкоджень, які не вдалося відновити через відсутність валідного дзеркала або руйнування обох копій RAID.

## Внутрішній механізм обробки у ядрі Linux

При отриманні виклику `BTRFS_IOC_SCRUB` ядро спавнить фоновий потік `btrfs-scrub`. Цей потік виконує послідовну ітерацію за фізичними адресами накопичувача (`physical_offset`), вичитуючи безперервні страйпи.

Для запобігання деградації продуктивності основних користувацьких операцій ввода-виводу ядро знижує пріоритет фонових I/O-запитів scrub до рівня `IOPRIO_CLASS_IDLE`. Також операційна система відстежує ситуації ребалансування масиву (`btrfs balance`) або видалення диска (`btrfs device remove`): якщо під час роботи scrub на пристрої починається балансування, ядро атомарно призупиняє scrub і відновлює його після перерозподілу чанків.

Синхронізація між паралельними викликами `ioctl` забезпечується внутрішнім м'ютексом ядра `fs_info->scrub_lock`, що виключає гонку процесів під час запиту статистики `BTRFS_IOC_SCRUB_PROGRESS`.

## Прапорці керування та режим перевірки

Поле `flags` у структурі `btrfs_ioctl_scrub_args` регулює режим виконання:

- `BTRFS_SCRUB_READONLY`: Сканувати та виявляти незбіги хешів, але **не виконувати автоматичне самоновлення** (перезапис пошкодженого сектора з дзеркала). Режим використовується у діагностичних утилітах та перевірках аудиту цілісності.
- `0` (за замовчуванням): У разі виявлення помилки CRC32c ядро негайно зчитує валідний блок із дзеркала RAID1 та перезаписує пошкоджений сектор.

## Моніторинг у реальному часі та скасування

Для побудови інтерактивних індикаторів прогресу в утилітах демонів моніторингу рекомендується використовувати таку паттерн-схему:

1. Головний потік надсилає виклик `BTRFS_IOC_SCRUB` для пристрою у фоновому потоці.
2. Потік моніторингу з періодичністю у 1 секунду надсилає виклик `BTRFS_IOC_SCRUB_PROGRESS` для того самого `devid`.
3. Монітор обчислює різницю `data_bytes_scrubbed` між двома замірами й розраховує поточну швидкість у МБ/с та розрахований час завершення (ETA).
4. У разі отримання сигналу зупинки від системи (`SIGINT`, `SIGTERM`) daemon надсилає виклик `BTRFS_IOC_SCRUB_CANCEL`, що примушує ядро завершити I/O-цикл і повернути управління.

## Трасування та інтерфейс sysfs

Ядро надує псевдофайли у `sysfs` для динамічного обмеження пропускної здатності фонового сканування та перегляду трасування:

- `/sys/fs/btrfs/<UUID>/devinfo/<devid>/scrub_speed_max` — максимальна швидкість сканування у байтах на секунду (0 — без обмежень).
- `/sys/fs/btrfs/<UUID>/devinfo/<devid>/error_stats` — підсумкові лічильники помилок фізичного накопичувача.

Для системного моніторингу eBPF / `trace-cmd` ядро виставляє підсистему трасування:
- `btrfs:btrfs_scrub_start` — запуск процесу сканування;
- `btrfs:btrfs_scrub_read_error` — фіксація збою хешу або апаратної помилки `EIO`;
- `btrfs:btrfs_scrub_fixup_error` — успішне перезаписування зіпсованого сектора валідними даними.

## Програмні приклади запуску та перевірки Scrub: C та C++

Наведені нижче приклади демонструють відкриття точки монтування Btrfs, ініціалізацію процедури `scrub` через `ioctl` та виведення статистики відновлених і фатальних помилок.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <string.h>
#include <errno.h>
#include <linux/btrfs.h>

int main(int argc, char *argv[])
{
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <точка_монтування> <devid>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *mount_point = argv[1];
    uint64_t devid = strtoull(argv[2], NULL, 10);

    int fd = open(mount_point, O_RDONLY | O_DIRECTORY);
    if (fd < 0) {
        perror("Не вдалося відкрити точку монтування Btrfs");
        return EXIT_FAILURE;
    }

    struct btrfs_ioctl_scrub_args args;
    memset(&args, 0, sizeof(args));
    args.devid = devid;
    args.start = 0;
    args.end = (uint64_t)-1; // Весь простір диска
    args.flags = 0;          // 0 - дозволити автоматичне самоновлення (Self-Healing)

    printf("Запуск btrfs scrub для пристрою devid=%glu на %s...\n", devid, mount_point);

    if (ioctl(fd, BTRFS_IOC_SCRUB, &args) < 0) {
        fprintf(stderr, "Помилка ioctl BTRFS_IOC_SCRUB: %s\n", strerror(errno));
        close(fd);
        return EXIT_FAILURE;
    }

    printf("Scrub успішно завершено!\n");
    printf("Проскановано байтів даних: %glu MB\n", args.progress.data_bytes_scrubbed / (1024 * 1024));
    printf("Проскановано байтів метаданих: %glu MB\n", args.progress.tree_bytes_scrubbed / (1024 * 1024));
    printf("Помилок контрольних сум (CSUM): %glu\n", args.progress.csum_errors);
    printf("Успішно відновлено з RAID: %glu\n", args.progress.corrected_errors);
    printf("НЕВІДНОВЛЮВАНИХ помилок: %glu\n", args.progress.uncorrectable_errors);

    close(fd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <string>
#include <system_error>
#include <cstring>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/btrfs.h>

class BtrfsScrubController {
private:
    int fd_ = -1;

public:
    explicit BtrfsScrubController(const std::string& mount_point) {
        fd_ = ::open(mount_point.c_str(), O_RDONLY | O_DIRECTORY);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "Не вдалося відкрити точку монтування Btrfs: " + mount_point);
        }
    }

    ~BtrfsScrubController() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    // RAII керування дескриптором
    BtrfsScrubController(const BtrfsScrubController&) = delete;
    BtrfsScrubController& operator=(const BtrfsScrubController&) = delete;

    [[nodiscard]] btrfs_scrub_progress startScrub(std::uint64_t devid, bool read_only = false) {
        btrfs_ioctl_scrub_args args{};
        args.devid = devid;
        args.start = 0;
        args.end = static_cast<std::uint64_t>(-1);
        args.flags = read_only ? BTRFS_SCRUB_READONLY : 0;

        if (::ioctl(fd_, BTRFS_IOC_SCRUB, &args) < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "Помилка виконання ioctl BTRFS_IOC_SCRUB");
        }

        return args.progress;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <точка_монтування> <devid>\n";
        return EXIT_FAILURE;
    }

    try {
        std::string mount_point = argv[1];
        std::uint64_t devid = std::stoull(argv[2]);

        BtrfsScrubController controller(mount_point);
        std::cout << "Запуск Btrfs Scrub (C++ RAII) для devid=" << devid << "...\n";

        auto progress = controller.startScrub(devid);

        std::cout << "Scrub завершено успішно!\n"
                  << "Даних оброблено: " << (progress.data_bytes_scrubbed / (1024 * 1024)) << " МБ\n"
                  << "Метаданих оброблено: " << (progress.tree_bytes_scrubbed / (1024 * 1024)) << " МБ\n"
                  << "Виявлено помилок CRC32c: " << progress.csum_errors << "\n"
                  << "Виправлено з дзеркала RAID: " << progress.corrected_errors << "\n"
                  << "Невідновлюваних збоїв: " << progress.uncorrectable_errors << std::endl;

    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << std::endl;
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::
