# 📜 Публічний ioctl-інтерфейс F2FS: керування прибиранням, шпильками й атомарним записом

Файлова система F2FS (Flash-Friendly File System) надає спеціалізований системний інтерфейс викликів `ioctl()`, який дозволяє прикладним програмам та системним демонам напряму керувати фоновими механізмами лог-структурованого тому. У той час як класичний POSIX-інтерфейс приховує деталі розкладки за абстракціями `read()` та `write()`, системний код на кшталт СУБД (SQLite), сервісів Android (vold, installd), утиліт обслуговування накопичувачів та менеджерів swap-файлів вимагає прямого впливу на прибирач сегментів, вирівнювання екстентів та атомарність транзакцій. Цей довідник описує контракти системних викликів `<linux/f2fs_fs.h>`, структуру аргументів, коди помилок, інтеграцію зі СУБД, керування стисненням, розбір через `tracefs` та ідіоматичні приклади виклику з C і C++.

## Карта ioctl-команд та їхнє призначення

Операції `ioctl()` в F2FS розбиваються на п'ять функціональних груп: керування прибиранням сміття, транзакційні атомарні записи, прикріплення блоків (pinning), стиснення та керування дефрагментацією і пристроями.

| Системна команда ioctl | Аргумент (тип / структура) | Привілеї | Основне призначення |
| :--- | :--- | :--- | :--- |
| `F2FS_IOC_GARBAGE_COLLECT` | `__u32 *sync` (0 або 1) | `CAP_SYS_ADMIN` | Примусовий запуск прибирача сегментів (фоновий або синхронний режим) |
| `F2FS_IOC_WRITE_CHECKPOINT` | `NULL` (без аргументу) | `CAP_SYS_ADMIN` | Миттєве скидання контрольної ділянки (checkpoint) на носій |
| `F2FS_IOC_GET_PIN_FILE` | `__u32 *pin` (0 або 1) | Права читання | Перевірка, чи прикріплено блоки файлу до фізичних секцій |
| `F2FS_IOC_SET_PIN_FILE` | `__u32 *pin` (0 або 1) | `CAP_SYS_ADMIN` / Власник | Заборона прибиральнику переміщувати блоки файлу (для swap/loop) |
| `F2FS_IOC_START_ATOMIC_WRITE` | `NULL` | Власник файлу | Початок транзакційної сесії запису без підготовки WAL-файлу |
| `F2FS_IOC_COMMIT_ATOMIC_WRITE` | `NULL` | Власник файлу | Фіксація всіх накопичених атомарних змін у базі даних |
| `F2FS_IOC_ABORT_ATOMIC_WRITE` | `NULL` | Власник файлу | Скасування накопичених атомарних змін та відкат сторінок |
| `F2FS_IOC_MOVE_RANGE` | `struct f2fs_move_range *` | Власник файлу | Пряме переміщення фізичних екстентів між двома файлами |
| `F2FS_IOC_DEFRAGMENT` | `struct f2fs_defragment *` | `CAP_SYS_ADMIN` | Ущільнення та дефрагментація екстентів у вказаному діапазоні |
| `F2FS_IOC_COMPRESS_FILE` | `NULL` | Власник файлу | Примусове стиснення вже записаного нестисненого файлу |
| `F2FS_IOC_DECOMPRESS_FILE` | `NULL` | Власник файлу | Примусове розпакування всіх кластерів стиснутого файлу |
| `F2FS_IOC_RELEASE_COMPRESS_BLOCKS` | `__u64 *count` | Власник файлу | Звільнення зекономлених блоків стиснутого файлу в систему |
| `F2FS_IOC_RESERVE_COMPRESS_BLOCKS` | `__u64 *count` | Власник файлу | Резервування фізичних блоків під майбутній розпакований запис |
| `F2FS_IOC_SEC_TRIM_FILE` | `struct f2fs_sectrim_range *` | `CAP_SYS_ADMIN` | Безпечне гарантоване стирання (secure erase) фізичних блоків |
| `F2FS_IOC_FLUSH_DEVICE` | `struct f2fs_flush_device *` | `CAP_SYS_ADMIN` | Перенесення живих сегментів із конкретного блокового пристрою |
| `F2FS_IOC_GET_FEATURES` | `__u32 *features` | Усі користувачі | Отримання бітової карти активних можливостей суперблока |

## Детальний розбір системних команд

### 1. Керування прибиранням та контрольною ділянкою

Лог-структурована система підтримує продуктивність лише тоді, коли вільні сегменти готуються заздалегідь. За замовчуванням прибирач F2FS працює у фоні під час простою накопичувача, однак утиліти обслуговування можуть просити ядро очистити носій перед виконанням інтенсивних записів.

Команда `F2FS_IOC_GARBAGE_COLLECT` приймає вказівник на 32-бітне ціле число:
- `sync = 0`: запускає один прохід фонового прибирача. Ядро оцінює сегменти за політикою вигоди на одиницю витрат (Cost-Benefit) — `(1 − u) · вік ÷ (1 + u)` — і бере той, у якого це відношення найбільше.
- `sync = 1`: запускає примусовий синхронний прохід. Ядро вибирає найпорожніший брудний сегмент (Greedy Policy), імітуючи примусовий режим очікування, і блокує викликаючий потік до завершення фізичного перенесення всіх живих блоків у нову голову лога.

Виклик `F2FS_IOC_WRITE_CHECKPOINT` примусово синхронізує внутрішні таблиці метаданих ядра (Node Address Table — NAT, Segment Info Table — SIT) і записує оновлену контрольно-облікову ділянку (Checkpoint Region) у дві копії на початку тому. Це гарантує точки відновлення без необхідності виконання повного `sync()` для всього дискового масиву.

### 2. Прикріплення файлів (Pinned Files)

Коли прибирач F2FS вибирає сегмент-жертву, він читає його живі блоки й дописує їх у голову лога за новішими фізичними адресами. Для більшості файлів це прозоро, бо карта блоків оновлюється в NAT/inode. Проте для файлів підкачки (swap files) та образів дисків (loop devices) переміщення блоків є неприпустимим, оскільки ядро Linux звертається до swap-файла через прямі фізичні зсуви блокового пристрою (`bmap`), оминаючи VFS.

Щоб захистити такі файли, F2FS підтримує атрибут **pinning** через `F2FS_IOC_SET_PIN_FILE`. Для прикріпленого файлу ядро гарантує, що прибирач не переносить його фізичних блоків.

Вимоги та послідовність кроків для успішного прикріплення swap-файла:
1. Створення порожнього файла. Прикріплення діє на блоки, які ядро виділить після нього, тому порядок такий: спершу файл, потім `ioctl`, і аж тоді місце.
2. Виклик `ioctl(fd, F2FS_IOC_SET_PIN_FILE, &pin_flag)`. З цього моменту ядро виділяє блоки цього файла в окремій ділянці й не дає прибирачеві їх переносити.
3. Розширення до повного фіксованого розміру через `fallocate(fd, 0, 0, swap_size)`, а тоді `fsync(fd)`; `truncate()` або почергове дописування `write()` не годяться, бо лишають розрізані екстенти.
4. Перевірка статусу прикріплення через `F2FS_IOC_GET_PIN_FILE`.
5. Передача файла системному виклику `swapon(path, 0)` або підключення як loop-пристрою через `ioctl(loop_fd, LOOP_SET_FD, fd)`.

Спроба прикріпити стиснений (compression) файл поверне `EINVAL`. Якщо прибирач F2FS під час фонового обходу виявляє сегмент із прикріпленими блоками, він залишає їх на місці й переносить лише сусідні звичайні блоки.

### 3. Атомарні записи для СУБД (Atomic Writes)

Традиційні бази даних (наприклад, SQLite чи InnoDB) для захисту від перерваного запису вимушені писати дані двічі: спершу в журнал передзапису (WAL — Write-Ahead Log), а потім у файл бази даних. У лог-структурованій файловій системі до цього подвійного запису додається ще й оновлення метаданих у лозі.

F2FS пропонує власний механізм **атомарного запису**:
1. Застосунок викликає `F2FS_IOC_START_ATOMIC_WRITE`. З цього моменту всі зміни сторінок у файлі перехоплюються F2FS.
2. Застосунок пише нові блоки безпосередньо у файл бази даних через звичайний `write()`. F2FS виділяє для них нові фізичні блоки в лозі, але **не оновлює** офіційну карту блоків inode та NAT.
3. Якщо транзакція успішна, застосунок викликає `F2FS_IOC_COMMIT_ATOMIC_WRITE`. F2FS атомарно перемикає покажчики блоків і записує контрольний вузол.
4. Якщо стався збій живлення або застосунок викликав `F2FS_IOC_ABORT_ATOMIC_WRITE`, F2FS просто скидає тимчасові незафіксовані блоки в лозі, залишаючи стару версію бази недоторканою.

### 4. Керування прозорим стисненням файлів

F2FS підтримує прозоре стиснення кластерів (за замовчуванням алгоритми LZ4, ZSTD чи LZO). Стиснення відбувається кластерами по 4–256 сторінок: розмір задає монтувальний параметр `compress_log_size` (кластер = 4 КіБ · 2ⁿ, за замовчуванням і мінімум n = 2, максимум n = 8), а для окремого файлу його читає й міняє `F2FS_IOC_SET_COMPRESS_OPTION`. Оскільки стиснутий кластер займає менше блоків, ніж сирий файл, F2FS повертає вільне місце в систему через команду `F2FS_IOC_RELEASE_COMPRESS_BLOCKS`.

Коли застосунок хоче стиснути вручну файл, що вже лежить на диску, він викликає `F2FS_IOC_COMPRESS_FILE`. Навпаки, команда `F2FS_IOC_DECOMPRESS_FILE` розпаковує всі кластери й відновлює стандартне нестиснуте представлення. Для підготовки до прямого запису в стиснутий файл команда `F2FS_IOC_RESERVE_COMPRESS_BLOCKS` гарантує наявність незайнятих фізичних блоків, запобігаючи помилкам `ENOSPC` під час декомпресії. Запит `F2FS_IOC_GET_COMPRESS_BLOCKS` повертає точну кількість фізичних блоків, які наразі збережені завдяки стисненню.

### 5. Дефрагментація, переміщення діапазонів та безпечне стирання

З часом активний допис у різні файли створює фрагментацію екстентів. Команда `F2FS_IOC_DEFRAGMENT` збирає розкидані блоки файлу в один послідовний сегмент. Для криптографічного чи безпечного фізичного вилучення даних на рівні флеш-комірок `F2FS_IOC_SEC_TRIM_FILE` виконує апаратне обнулення блоків із використанням прапорців `F2FS_TRIM_FILE_DISCARD` та `F2FS_TRIM_FILE_ZEROOUT`.

Нижче наведено контракти структур з ядрового заголовка `<linux/f2fs_fs.h>` у порівнянні з ідіоматичними C++20 обгортками:

:::tabs
```c
/* Цитата з ядрового заголовка <linux/f2fs_fs.h> */
struct f2fs_defragment {
    __u64 start;    /* початковий зсув у файлі (у байтах) */
    __u64 len;      /* довжина ділянки для дефрагментації */
};

struct f2fs_move_range {
    __u32 dst_fd;   /* дескриптор цільового файла */
    __u64 pos_in;   /* початковий зсув у джерелі */
    __u64 pos_out;  /* початковий зсув у цілі */
    __u64 len;      /* довжина діапазону для переміщення */
};

struct f2fs_sectrim_range {
    __u64 start;    /* початковий байт */
    __u64 len;      /* довжина для обнулення */
    __u64 flags;    /* прапорці безпечного стирання */
};

struct f2fs_flush_device {
    __u32 dev_num;  /* номер фізичного накопичувача в масиві */
    __u32 segments; /* кількість вимиваних сегментів */
};
```

```cpp
// Ідіоматичні C++20 обгортки над ядровими структурами <linux/f2fs_fs.h>
#include <cstdint>
#include <linux/f2fs_fs.h>

namespace f2fs {

struct DefragRange {
    std::uint64_t start{0}; // початковий зсув у байтах
    std::uint64_t len{0};   // довжина ділянки
    
    [[nodiscard]] ::f2fs_defragment to_native() const noexcept {
        return ::f2fs_defragment{.start = start, .len = len};
    }
};

struct MoveRange {
    int target_fd{-1};
    std::uint64_t src_offset{0};
    std::uint64_t dst_offset{0};
    std::uint64_t length{0};

    [[nodiscard]] ::f2fs_move_range to_native() const noexcept {
        return ::f2fs_move_range{
            .dst_fd = static_cast<std::uint32_t>(target_fd),
            .pos_in = src_offset,
            .pos_out = dst_offset,
            .len = length
        };
    }
};

struct SecureTrimRange {
    std::uint64_t start{0};
    std::uint64_t len{0};
    std::uint64_t flags{0};

    [[nodiscard]] ::f2fs_sectrim_range to_native() const noexcept {
        return ::f2fs_sectrim_range{.start = start, .len = len, .flags = flags};
    }
};

struct FlushDeviceConfig {
    std::uint32_t device_index{0};
    std::uint32_t segments_count{0};

    [[nodiscard]] ::f2fs_flush_device to_native() const noexcept {
        return ::f2fs_flush_device{.dev_num = device_index, .segments = segments_count};
    }
};

} // namespace f2fs
```
:::

### 6. Керування багатодисковими масивами (`F2FS_IOC_FLUSH_DEVICE`)

Сучасна F2FS підтримує роботу поверх кількох фізичних блокових пристроїв у рамках одного логічного тому (наприклад, швидкісний NVMe SSD для гарячих блоків метаданих та повільніший SATA SSD / ZNS для даних). У разі необхідності гарячої заміни або вилучення одного з дискових накопичувачів виконується виклик `F2FS_IOC_FLUSH_DEVICE`.

Приймаючи структуру `struct f2fs_flush_device`, ядро знаходить усі живі сегменти на вказаному пристрої `dev_num` та примусово мігрує їх у вільні сегменти інших пристроїв масиву. Поле `segments` обмежує, скільки сегментів пристрою ядро перенесе за один виклик.

### 7. Запит можливостей суперблока (`F2FS_IOC_GET_FEATURES`)

Команда `F2FS_IOC_GET_FEATURES` повертає бітову маску розширень, що були активовані під час форматування тома за допомогою `mkfs.f2fs`. Системний код перевіряє такі ключові прапорці:

- `F2FS_FEATURE_ENCRYPT` (`0x0001`): підтримка нативного шифрування файлів (fscrypt).
- `F2FS_FEATURE_BLKZONED` (`0x0002`): підтримка зонованих блокових пристроїв (ZNS SSD / SMR HDD).
- `F2FS_FEATURE_ATOMIC_WRITE` (`0x0004`): підтримка транзакційного атомарного запису для СУБД.
- `F2FS_FEATURE_VERITY` (`0x0400`): підтримка дерев Меркла для перевірки цілісності читань (fs-verity).
- `F2FS_FEATURE_COMPRESSION` (`0x2000`): підтримка прозорого стиснення кластерів LZ4/ZSTD.

## Інтеграція зі СУБД: SQLite поверх атомарного запису

Готового модуля в апстрімі SQLite для цього немає. Атомарний запис F2FS від початку робили саме під SQLite на Android, і схема виглядає так: шар VFS перевіряє через `F2FS_IOC_GET_FEATURES` прапорець `F2FS_FEATURE_ATOMIC_WRITE` і, знайшовши його, перемикає транзакційний двигун:

1. **Замість створення `.db-journal` або `.db-wal`** файлів, SQLite перед виконанням `BEGIN TRANSACTION` надсилає `ioctl(fd, F2FS_IOC_START_ATOMIC_WRITE)`.
2. Усі сторінки B-дерева модифікуються в оперативній пам'яті та скидаються у файл бази даних звичайним `write()`.
3. При виконанні `COMMIT` SQLite надсилає `ioctl(fd, F2FS_IOC_COMMIT_ATOMIC_WRITE)` і викликає `fsync()`.
4. Результат: швидкість транзакцій помітно зростає, а навантаження на комірки флеш-пам'яті (TBW) падає, бо зникає другий запис тих самих даних, властивий WAL-журналюванню.

## Простеження та діагностика через sysfs та tracepoints

Стан F2FS видно у файловій системі `sysfs`, а перебіг самих операцій — через точки трасування в `tracefs`:

- `/sys/fs/f2fs/<device>/gc_mode`: відображає поточний режим прибирача (`GC_NORMAL`, `GC_IDLE_CB`, `GC_URGENT_HIGH`).
- `/sys/fs/f2fs/<device>/dirty_segments`: кількість брудних сегментів, що очікують на прибирання.
- `/sys/fs/f2fs/<device>/unusable`: кількість блоків, якими не можна скористатися, поки не записано контрольну ділянку.
- `/sys/fs/f2fs/<device>/compr_written_block`: лічильник стиснутих записаних блоків.

Діагностика викликів у реальному часі здійснюється через ftrace:

```sh
# Увімкнення точок трасування прибирача F2FS
# echo 1 > /sys/kernel/tracing/events/f2fs/f2fs_gc_begin/enable
# echo 1 > /sys/kernel/tracing/events/f2fs/f2fs_gc_end/enable
# cat /sys/kernel/tracing/trace_pipe
```

## Приклади використання: C та C++

Нижче наведено робочі приклади роботи з ioctl F2FS для перевірки стану прикріплення, запусків GC та атомарної транзакції СУБД.

:::tabs
```c
/* f2fs_ops.c — керування прибиранням та атомарним записом F2FS на C.
 * Збірка: cc -O2 -o f2fs_ops f2fs_ops.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <linux/f2fs_fs.h>

/* Перевірка підтримки ioctl F2FS та стану прикріплення файлу */
int check_file_pin_status(int fd) {
    uint32_t pin_state = 0;
    if (ioctl(fd, F2FS_IOC_GET_PIN_FILE, &pin_state) < 0) {
        if (errno == ENOTTY || errno == EOPNOTSUPP) {
            fprintf(stderr, "Файлова система не підтримує ioctl F2FS\n");
        } else {
            perror("F2FS_IOC_GET_PIN_FILE failed");
        }
        return -1;
    }
    printf("Стан прикріплення (pin): %s\n", pin_state ? "прикріплено" : "вільний");
    return pin_state;
}

/* Запуск атомарної транзакції запису в базу даних */
int execute_atomic_transaction(int fd, const char *data, size_t len) {
    /* 1. Початок атомарної транзакції */
    if (ioctl(fd, F2FS_IOC_START_ATOMIC_WRITE) < 0) {
        perror("F2FS_IOC_START_ATOMIC_WRITE failed");
        return -1;
    }

    /* 2. Запис даних у файл (іде в нові сегменти лога) */
    ssize_t written = write(fd, data, len);
    if (written < 0 || (size_t)written != len) {
        perror("Запис не вдався, скасовуємо транзакцію");
        /* Відкат транзакції при помилці */
        ioctl(fd, F2FS_IOC_ABORT_ATOMIC_WRITE);
        return -1;
    }

    /* 3. Фіксація транзакції (атомарне оновлення покажчиків метаданих) */
    if (ioctl(fd, F2FS_IOC_COMMIT_ATOMIC_WRITE) < 0) {
        perror("F2FS_IOC_COMMIT_ATOMIC_WRITE failed");
        ioctl(fd, F2FS_IOC_ABORT_ATOMIC_WRITE);
        return -1;
    }

    printf("Атомарну транзакцію успішно зафіксовано (%zd байтів)\n", written);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_файла_на_f2fs>\n", argv[0]);
        return 1;
    }

    int fd = open(argv[1], O_RDWR | O_CREAT, 0644);
    if (fd < 0) {
        perror("open failed");
        return 1;
    }

    /* Перевіряємо статус */
    check_file_pin_status(fd);

    /* Демонстрація атомарного запису */
    const char *payload = "TRANSACTION_DATA_BLOCK_HEADER_F2FS_ATOMIC";
    execute_atomic_transaction(fd, payload, strlen(payload));

    /* Спроба запустити прибирача у фоновому режимі (потрібен CAP_SYS_ADMIN) */
    uint32_t sync_gc = 0; /* 0 — фоновий прохід, 1 — синхронний */
    if (ioctl(fd, F2FS_IOC_GARBAGE_COLLECT, &sync_gc) == 0) {
        printf("Фоновий прибирач F2FS успішно активовано\n");
    } else {
        printf("F2FS_IOC_GARBAGE_COLLECT повернув: %s (потрібні привілеї CAP_SYS_ADMIN)\n",
               strerror(errno));
    }

    close(fd);
    return 0;
}
```

```cpp
// f2fs_ops.cpp — RAII-обгортка та ідіоматичне керування F2FS ioctl у C++20.
// Збірка: g++ -std=c++20 -O2 -o f2fs_ops_cpp f2fs_ops.cpp
#include <iostream>
#include <string_view>
#include <system_error>
#include <utility>
#include <cstdint>
#include <cerrno>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/f2fs_fs.h>

namespace f2fs {

// RAII обгортка для безпечного керування файловим дескриптором F2FS
class FileDescriptor {
    int fd_{-1};
public:
    explicit FileDescriptor(int fd) noexcept : fd_(fd) {}
    ~FileDescriptor() {
        if (fd_ >= 0) ::close(fd_);
    }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_(std::exchange(other.fd_, -1)) {}
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = std::exchange(other.fd_, -1);
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

// RAII транзакція атомарного запису в F2FS
class AtomicTransaction {
    int fd_{-1};
    bool committed_{false};
public:
    explicit AtomicTransaction(int fd) : fd_(fd) {
        if (::ioctl(fd_, F2FS_IOC_START_ATOMIC_WRITE) < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "F2FS_IOC_START_ATOMIC_WRITE failed");
        }
    }

    ~AtomicTransaction() {
        if (fd_ >= 0 && !committed_) {
            // Скасувати транзакцію в деструкторі при винятку або помилці
            ::ioctl(fd_, F2FS_IOC_ABORT_ATOMIC_WRITE);
        }
    }

    void commit() {
        if (committed_) return;
        if (::ioctl(fd_, F2FS_IOC_COMMIT_ATOMIC_WRITE) < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "F2FS_IOC_COMMIT_ATOMIC_WRITE failed");
        }
        committed_ = true;
    }

    AtomicTransaction(const AtomicTransaction&) = delete;
    AtomicTransaction& operator=(const AtomicTransaction&) = delete;
};

// Допоміжні функції керування F2FS
[[nodiscard]] bool get_pin_status(int fd) {
    uint32_t pin = 0;
    if (::ioctl(fd, F2FS_IOC_GET_PIN_FILE, &pin) < 0) {
        throw std::system_error(errno, std::generic_category(), 
                               "F2FS_IOC_GET_PIN_FILE failed");
    }
    return pin != 0;
}

void trigger_garbage_collection(int fd, bool sync) {
    uint32_t sync_val = sync ? 1 : 0;
    if (::ioctl(fd, F2FS_IOC_GARBAGE_COLLECT, &sync_val) < 0) {
        throw std::system_error(errno, std::generic_category(), 
                               "F2FS_IOC_GARBAGE_COLLECT failed");
    }
}

} // namespace f2fs

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях_до_файла>\n";
        return 1;
    }

    try {
        int raw_fd = ::open(argv[1], O_RDWR | O_CREAT, 0644);
        if (raw_fd < 0) {
            throw std::system_error(errno, std::generic_category(), "open failed");
        }
        f2fs::FileDescriptor file{raw_fd};

        bool is_pinned = f2fs::get_pin_status(file.get());
        std::cout << "Стан прикріплення: " << (is_pinned ? "pinned" : "unpinned") << '\n';

        // Виконання безпечної RAII транзакції
        {
            f2fs::AtomicTransaction tx{file.get()};
            std::string_view payload = "CPP20_ATOMIC_TRANSACTION_PAYLOAD";
            ssize_t res = ::write(file.get(), payload.data(), payload.size());
            if (res < 0 || static_cast<size_t>(res) != payload.size()) {
                throw std::system_error(errno, std::generic_category(), "write failed");
            }
            tx.commit();
            std::cout << "Атомарний запис зафіксовано в C++!\n";
        }

    } catch (const std::exception& ex) {
        std::cerr << "Помилка F2FS: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
```
:::

## Крайові випадки та пастки діагностики

1. **Помилка `ENOTTY` або `EOPNOTSUPP`**:
   Свідчить про те, що цільовий файл лежить не на томі F2FS (а на ext4, xfs чи btrfs) або ядро зібране без підтримки F2FS.
2. **Помилка `EPERM` / `EACCES` при спробі GC**:
   Команди `F2FS_IOC_GARBAGE_COLLECT` і `F2FS_IOC_WRITE_CHECKPOINT` вимагають `CAP_SYS_ADMIN`: без нього виклик повертає `-1` і `errno = EPERM`. Для `F2FS_IOC_SET_PIN_FILE` досить бути власником файлу — чужому файлові ядро відмовить із `EACCES`.
3. **Взаємодія Pinned Files із дефрагментацією**:
   Прикріплений файл ядро не дає перебудувати: `F2FS_IOC_DEFRAGMENT` на ньому відмовляє, а зміна розміру через `truncate()` руйнує саму гарантію суцільності екстентів. Перед такими діями файл слід відкріпити (`pin = 0`).
4. **Атомарний запис і `fsync()`**:
   Атомарний запис гарантує лише цілісність метаданих усередині F2FS. Щоб переконатися, що зафіксовані атомарні блоки фізично записані на комірки флеш-пам'яті, після `F2FS_IOC_COMMIT_ATOMIC_WRITE` все одно необхідно викликати стандартний POSIX `fsync(fd)`.
