# ⚙️ Практична реалізація reflink-клонування та управління знімками Btrfs

Цей практичний проєкт показує, як розробляти системні утиліти для програмної взаємодії з підсистемою Btrfs у Linux користувацькому просторі (userspace). Тут наведено повний вихідний код мовами C та C++, який автоматизує процес створення субтомів, створення атомарних Read-Only знімків та швидкого клонування великих файлів за допомогою Copy-on-Write ioctls.

## Постановка задачі та сценарій використання

У багатьох інфраструктурних задачах (наприклад, при розгортанні тестових середовищ для баз даних або створенні ізольованих контейнерів) виникає потреба швидко скопіювати еталонне середовище без значних витрат часу та дискового простору. Класичне копіювання файлів через системні виклики `read(2)` та `write(2)` для файлу розміром 100 ГБ займає десятки секунд та виснажує ресурс SSD-накопичувача. 

Використання нативних можливостей Btrfs дозволяє виконати цю задачу, не копіюючи жодного байта даних: ядро лише додає посилання на вже наявні екстенти (Extent Sharing). Ціна операції залежить від кількості екстентів файлу, а не від його обсягу, тож замість десятків секунд читання-запису лишаються мілісекунди роботи з метаданими.

Програма реалізує завершений цикл маніпуляції об'єктами Btrfs:
1. **Перевірка та відкриття директорії:** Відкриває файловий дескриптор батьківської точки монтування Btrfs через `open(2)` з прапорцем `O_DIRECTORY`.
2. **Створення субтому (`BTRFS_IOC_SUBVOL_CREATE`):** Створює новий робочий субтом `subvol_demo` як окреме B-дерево в системному корінному дереві `ROOT_TREE`.
3. **Reflink-клонування файлу (`FICLONE`):** Створює файл `cloned.bin` всередині субтому, який використовує спільні дискові екстенти з джерельним файлом `source.bin`, не витрачаючи додаткового простору на диску.
4. **Створення Read-Only знімка (`BTRFS_IOC_SNAP_CREATE_V2`):** Виконує атомарне створення знімка `subvol_demo_snap` із встановленням прапорця `BTRFS_SUBVOL_RDONLY`.

## Порівняльна таблиця парадигм реалізації (C vs C++)

| Аспект реалізації | Реалізація мовою C | Реалізація мовою C++20 |
| :--- | :--- | :--- |
| **Управління ресурсами** | Ручний виклик `close(fd)` у кожній гілці помилок | Автоматичний деструктор RAII класу `FileDescriptor` |
| **Обробка помилок** | Перевірка коду повернення `-1` та виклик `perror()` | Винятки `std::system_error` із кодом `errno` |
| **Робота з шляхами** | Статичні масиви `char[1024]` та `snprintf()` | Безпечний клас `std::filesystem::path` |
| **Передавання рядків** | Вказівники `const char*` з гарантією `\0` | Легковаговий `std::string_view` без копіювання |

## Вихідний код реалізації

:::tabs
```c
// c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <linux/btrfs.h>
#include <linux/fs.h>

// Помічник для створення нового порожнього субтому
int create_subvolume(const char *parent_dir, const char *subvol_name) {
    int dir_fd = open(parent_dir, O_RDONLY | O_DIRECTORY);
    if (dir_fd < 0) {
        perror("[ERR] Не вдалося відкрити батьківську директорію");
        return -1;
    }

    struct btrfs_ioctl_vol_args args;
    memset(&args, 0, sizeof(args));
    strncpy(args.name, subvol_name, BTRFS_PATH_NAME_MAX);
    args.name[BTRFS_PATH_NAME_MAX] = '\0';

    if (ioctl(dir_fd, BTRFS_IOC_SUBVOL_CREATE, &args) < 0) {
        perror("[ERR] Помилка ioctl(BTRFS_IOC_SUBVOL_CREATE)");
        close(dir_fd);
        return -1;
    }

    close(dir_fd);
    printf("[+] Субтом '%s' успішно створено в '%s'\n", subvol_name, parent_dir);
    return 0;
}

// Помічник для створення знімка лише для читання (Read-Only Snapshot)
int create_readonly_snapshot(const char *src_subvol, const char *parent_dir, const char *snap_name) {
    int src_fd = open(src_subvol, O_RDONLY | O_DIRECTORY);
    if (src_fd < 0) {
        perror("[ERR] Не вдалося відкрити джерельний субтом");
        return -1;
    }

    int parent_fd = open(parent_dir, O_RDONLY | O_DIRECTORY);
    if (parent_fd < 0) {
        perror("[ERR] Не вдалося відкрити батьківську директорію для знімка");
        close(src_fd);
        return -1;
    }

    struct btrfs_ioctl_vol_args_v2 args2;
    memset(&args2, 0, sizeof(args2));
    args2.fd = src_fd;
    args2.flags = BTRFS_SUBVOL_RDONLY;
    strncpy(args2.name, snap_name, BTRFS_SUBVOL_NAME_MAX);
    args2.name[BTRFS_SUBVOL_NAME_MAX] = '\0';

    if (ioctl(parent_fd, BTRFS_IOC_SNAP_CREATE_V2, &args2) < 0) {
        perror("[ERR] Помилка ioctl(BTRFS_IOC_SNAP_CREATE_V2)");
        close(parent_fd);
        close(src_fd);
        return -1;
    }

    close(parent_fd);
    close(src_fd);
    printf("[+] Read-Only знімок '%s' успішно створено\n", snap_name);
    return 0;
}

// Помічник для клонування файлу через VFS FICLONE (reflink)
int reflink_clone_file(const char *src_path, const char *dst_path) {
    int src_fd = open(src_path, O_RDONLY);
    if (src_fd < 0) {
        perror("[ERR] Не вдалося відкрити джерельний файл");
        return -1;
    }

    int dst_fd = open(dst_path, O_WRONLY | O_CREAT | O_EXCL, 0644);
    if (dst_fd < 0) {
        perror("[ERR] Не вдалося створити цільовий файл");
        close(src_fd);
        return -1;
    }

    if (ioctl(dst_fd, FICLONE, src_fd) < 0) {
        perror("[ERR] Помилка ioctl(FICLONE) — не Btrfs або між пристроями");
        close(src_fd);
        close(dst_fd);
        unlink(dst_path);
        return -1;
    }

    close(src_fd);
    close(dst_fd);
    printf("[+] Файл '%s' успішно клоновано через FICLONE у '%s'\n", src_path, dst_path);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <точка_монтування_btrfs>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *mnt = argv[1];
    char subvol_path[1024];
    snprintf(subvol_path, sizeof(subvol_path), "%s/subvol_demo", mnt);

    if (create_subvolume(mnt, "subvol_demo") != 0) {
        return EXIT_FAILURE;
    }

    char src_file[1024], dst_file[1024];
    snprintf(src_file, sizeof(src_file), "%s/source.bin", mnt);
    snprintf(dst_file, sizeof(dst_file), "%s/cloned.bin", subvol_path);

    // Запис вихідного тестового файлу
    int tmp_fd = open(src_file, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (tmp_fd >= 0) {
        const char *data = "Btrfs CoW Reflink Payload Data\n";
        write(tmp_fd, data, strlen(data));
        close(tmp_fd);
    }

    reflink_clone_file(src_file, dst_file);
    create_readonly_snapshot(subvol_path, mnt, "subvol_demo_snap");

    return EXIT_SUCCESS;
}
```
```cpp
// cpp
#include <iostream>
#include <string>
#include <string_view>
#include <system_error>
#include <memory>
#include <filesystem>
#include <algorithm>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/btrfs.h>
#include <linux/fs.h>

namespace fs = std::filesystem;

// Ідіоматична RAII-обгортка для безпечного управління файловими дескрипторами
class FileDescriptor {
    int fd_{-1};
public:
    explicit FileDescriptor(int fd) : fd_(fd) {}
    ~FileDescriptor() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& rhs) noexcept : fd_(rhs.fd_) {
        rhs.fd_ = -1;
    }

    FileDescriptor& operator=(FileDescriptor&& rhs) noexcept {
        if (this != &rhs) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = rhs.fd_;
            rhs.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

class BtrfsManager {
public:
    static void create_subvolume(const fs::path& parent_dir, std::string_view subvol_name) {
        FileDescriptor dir_fd(::open(parent_dir.c_str(), O_RDONLY | O_DIRECTORY));
        if (!dir_fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити батьківську директорію");
        }

        struct btrfs_ioctl_vol_args args{};
        const size_t copy_len = std::min(subvol_name.size(), static_cast<size_t>(BTRFS_PATH_NAME_MAX));
        std::copy_n(subvol_name.begin(), copy_len, args.name);
        args.name[copy_len] = '\0';

        if (::ioctl(dir_fd.get(), BTRFS_IOC_SUBVOL_CREATE, &args) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка ioctl(BTRFS_IOC_SUBVOL_CREATE)");
        }

        std::cout << "[+] Субтом '" << subvol_name << "' успішно створено в '" << parent_dir.string() << "'\n";
    }

    static void create_readonly_snapshot(const fs::path& src_subvol, const fs::path& parent_dir, std::string_view snap_name) {
        FileDescriptor src_fd(::open(src_subvol.c_str(), O_RDONLY | O_DIRECTORY));
        if (!src_fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити джерельний субтом");
        }

        FileDescriptor parent_fd(::open(parent_dir.c_str(), O_RDONLY | O_DIRECTORY));
        if (!parent_fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити батьківську директорію");
        }

        struct btrfs_ioctl_vol_args_v2 args2{};
        args2.fd = src_fd.get();
        args2.flags = BTRFS_SUBVOL_RDONLY;
        const size_t copy_len = std::min(snap_name.size(), static_cast<size_t>(BTRFS_SUBVOL_NAME_MAX));
        std::copy_n(snap_name.begin(), copy_len, args2.name);
        args2.name[copy_len] = '\0';

        if (::ioctl(parent_fd.get(), BTRFS_IOC_SNAP_CREATE_V2, &args2) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка ioctl(BTRFS_IOC_SNAP_CREATE_V2)");
        }

        std::cout << "[+] Read-Only знімок '" << snap_name << "' успішно створено\n";
    }

    static void reflink_clone_file(const fs::path& src_path, const fs::path& dst_path) {
        FileDescriptor src_fd(::open(src_path.c_str(), O_RDONLY));
        if (!src_fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити джерельний файл");
        }

        FileDescriptor dst_fd(::open(dst_path.c_str(), O_WRONLY | O_CREAT | O_EXCL, 0644));
        if (!dst_fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося створити цільовий файл");
        }

        if (::ioctl(dst_fd.get(), FICLONE, src_fd.get()) < 0) {
            fs::remove(dst_path);
            throw std::system_error(errno, std::generic_category(), "Помилка ioctl(FICLONE)");
        }

        std::cout << "[+] Файл '" << src_path.string() << "' клоновано через FICLONE у '" << dst_path.string() << "'\n";
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <точка_монтування_btrfs>\n";
        return EXIT_FAILURE;
    }

    try {
        const fs::path mnt = argv[1];
        const fs::path subvol_path = mnt / "subvol_demo";

        BtrfsManager::create_subvolume(mnt, "subvol_demo");

        const fs::path src_file = mnt / "source.bin";
        const fs::path dst_file = subvol_path / "cloned.bin";

        {
            FileDescriptor tmp_fd(::open(src_file.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0644));
            if (tmp_fd.valid()) {
                const std::string payload = "Btrfs CoW Reflink Payload Data\n";
                ::write(tmp_fd.get(), payload.data(), payload.size());
            }
        }

        BtrfsManager::reflink_clone_file(src_file, dst_file);
        BtrfsManager::create_readonly_snapshot(subvol_path, mnt, "subvol_demo_snap");

    } catch (const std::exception& ex) {
        std::cerr << "[ERR] Помилка виконання: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

## Кроки збірки, запуску та верифікації результатів

Для успішної збірки проєкту в системі мають бути встановлені компілятор C/C++ та базові заголовкові файли ядра Linux (пакет `linux-headers` у Debian/Ubuntu або `kernel-headers` у Fedora/Arch Linux).

### Компіляція вихідного коду:

```bash
# Збірка версії мовою C
gcc -O2 -Wall btrfs_demo.c -o btrfs_demo_c

# Збірка версії мовою C++ (потрібна підтримка C++20)
g++ -O2 -Wall -std=c++20 btrfs_demo.cpp -o btrfs_demo_cpp
```

### Виконання та перевірка в системі:

Створення субтому та знімка привілеїв не потребує — досить права запису в батьківський каталог. Права суперкористувача (`sudo`) чи мандат `CAP_SYS_ADMIN` знадобляться для видалення субтому (якщо том не змонтовано з опцією `user_subvol_rm_allowed`) та для зміни дефолтного субтому; нижче `sudo` вжито тому, що тестовий том зазвичай належить root:

```bash
# Запуск утиліти над монтованим Btrfs-розділом
sudo ./btrfs_demo_cpp /mnt/btrfs_pool

# Перевірка списку створених субтомів через системну утиліту btrfs-progs
sudo btrfs subvolume list /mnt/btrfs_pool
```

Очікуваний вивід команди `btrfs subvolume list`:
```text
ID 256 gen 42 top level 5 path subvol_demo
ID 257 gen 42 top level 5 path subvol_demo_snap
```

Зверніть увагу, що `subvol_demo_snap` має той самий номер генерації (`gen 42`) на момент створення і прапорець `ro` (Read-Only), який блокує будь-які подальші модифікації файлів усередині цього знімка.

## Детальний аналіз інженерних рішень та пасток

### 1. Передача дескрипторів між викликами ioctl

У функції `create_readonly_snapshot` ключовим моментом є коректне заповнення поля `args2.fd`. Воно повинно вказувати на *вже відкритий файловий дескриптор джерельного субтому*, а не на батьківський каталог. Сама ж команда `ioctl` викликається над файловим дескриптором *батьківської директорії*, у якій буде розміщено новий знімок. Порушення цього правила призведе до повернення помилки `EBADF` або `EINVAL`.

### 2. Безпека типів та RAII у C++

У реалізації на C++ використовується власний клас `FileDescriptor`. Він гарантує дотримання принципу RAII (Resource Acquisition Is Initialization): файловий дескриптор закривається деструктором навіть тоді, коли виклик `ioctl` піднімає виняток `std::system_error`. Копіювальні конструктор і оператор присвоєння заблоковано (`= delete`), що запобігає випадковому подвійному закриттю дескриптора (`double close`).

### 3. Діагностика помилки `EXDEV` при клонуванні

Системний виклик `FICLONE` є атомарною операцією на рівні B-дерева файлової системи. Спроба виконати reflink-клонування між файлами, що знаходяться на різних пристроях або різних файлових системах (наприклад, з Ext4 у Btrfs або між двома окремими пулами Btrfs), завжди завершиться з помилкою `EXDEV` (Invalid cross-device link). Виробниче програмне забезпечення має перехоплювати код `EXDEV` та виконувати звичайне фолбек-копіювання через `copy_file_range(2)` або послідовні виклики `read(2)` / `write(2)`.

### 4. Інспектування файлових екстентів через `filefrag`

Для верифікації того, що клонований файл дійсно ділить фізичні дискові блоки з джерелом без дублювання простору, можна використати системну утиліту `filefrag`:

```bash
# Перевірка фізичних дискових блоків вихідного та клонованого файлу
sudo filefrag -v /mnt/btrfs_pool/source.bin
sudo filefrag -v /mnt/btrfs_pool/subvol_demo/cloned.bin
```

Колонка `physical` у виводі `filefrag` для обох файлів вказуватиме на один і той самий діапазон фізичних секторів диска. Це наочно підтверджує, що reflink-клонування через `FICLONE` створило лише нові метадані в B-дереві субтому, зберігши вільний дисковий простір накопичувача.

### 5. Динамічна зміна дефолтного субтому для завантаження системи

Крім створення та клонування, розробники інфраструктурних утиліт автоматичного відновлення систем (таких як `Snapper` або `Timeshift`) використовують виклик `BTRFS_IOC_DEFAULT_SUBVOL` для переключення субтому, який монтується за замовчуванням:

```c
// Програмне переключення замовчувального субтому за його numeric ID
__u64 default_subvol_id = 257; // ID знімка для відкоту системи
if (ioctl(mnt_fd, BTRFS_IOC_DEFAULT_SUBVOL, &default_subvol_id) < 0) {
    perror("[ERR] Не вдалося змінити default subvolume ID");
}
```

Коли завантажувач Linux (GRUB або systemd-boot) передає ядру параметр `root=/dev/sda1` без вказання опції `subvol=`, ядро Linux автоматично монтує той субтом, чий ID записано у полі замовчування суперблоку через `BTRFS_IOC_DEFAULT_SUBVOL`. Це дозволяє реалізувати атомарний відкіт всієї ОС на попередній знімок шляхом виконання єдиного виклику `ioctl`.

Крім того, після виконання викликів `ioctl` для створення субтому та знімка, операційна система може зажадати виклику `sync(2)` або `fsync(2)`, якщо утиліта повинна гарантувати фізичний запис нових метаданих на дисковий накопичувач перед завершенням свого виконання. За замовчуванням Btrfs фіксує нові транзакції метаданих кожні 30 секунд, тож без явного `sync(2)`/`fsync(2)` новий субтом якийсь час живе лише в пам'яті. Прапор `BTRFS_SUBVOL_CREATE_ASYNC`, який колись дозволяв повернути керування ще до фіксації транзакції, вилучено з ядра 5.7 — від нього ioctl із цим бітом повертає `EOPNOTSUPP`.
