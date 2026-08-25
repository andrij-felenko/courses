# ⚙️ Практикум: емуляція витоку дискового простору та відновлення на льоту

Практичне дослідження аномалій дискового простору потребує надійного й повністю контрольованого стенду: процесу, який створює великий файл, утримує його відкритим, видаляє запис із каталогу через системний виклик `unlink()` і продовжує виконувати запис нових порцій даних. У цей момент системні утиліти `df` та `du` починають демонструвати протилежні картини реальності. Інженер повинен уміти зафіксувати розбіжність через системні виклики `statvfs()` та `fstatat()`, локалізувати дескриптор у псевдофайловій системі `/proc/[pid]/fd/` та вивільнити заблоковані дискові блоки на льоту через операцію зрізання (`ftruncate`), не перериваючи роботу основного сервісу.

## Архітектура дослідницької утиліти

Утиліта проєкту складається з двох тісно пов'язаних логічних компонентів, що моделюють повний життєвий цикл виробничого інциденту:

1. **Генератор аномального витоку (`leak_producer`):** створює новий файл у вказаному каталозі, виділяє в ньому реальні фізичні блоки (наприклад, 64 МіБ або 1 ГіБ через системні функції `posix_fallocate` або прямий буферизований `write`), відкриває дескриптор на запис, вилучає запис із каталогу за допомогою `unlink()` і переходить у режим фонового утримання ресурсу.
2. **Аналізатор і рятувальник простору (`space_rescuer`):** зчитує сукупні показники `statvfs()` для відповідної точки VFS, підраховує видимий розмір каталогу через рекурсивний обхід дерева функцією `ftw()` або `std::filesystem::recursive_directory_iterator`, фіксує числову розбіжність між метриками, після чого знаходить відкритий дескриптор у `/proc` і виконує операцію `ftruncate(fd, 0)` або `fallocate(FALLOC_FL_PUNCH_HOLE)` безпосередньо через магічний псевдошлях `/proc/[pid]/fd/[fd]`.

```
ПРОЦЕС-ГЕНЕРАТОР (PID 4102)                ПРОЦЕС-РЯТУВАЛЬНИК
┌────────────────────────────┐             ┌────────────────────────────┐
│ 1. open("leak.dat", O_CREAT│             │ 1. statvfs("/tmp/test")    │
│ 2. fallocate(64 МБ)        │             │    -> f_bfree зменшено!    │
│ 3. unlink("leak.dat")      │             │ 2. nftw("/tmp/test")       │
│    i_nlink = 0             │             │    -> du бачить 0 байтів!  │
│    i_count = 1             │             │ 3. open("/proc/4102/fd/3") │
│ 4. Фоновий цикл            │<── ftruncate(fd, 0) ─────────────────────┤
└────────────────────────────┘             │ 4. statvfs("/tmp/test")    │
                                           │    -> f_bfree ВІДНОВЛЕНО!  │
                                           └────────────────────────────┘
```

## Реалізація стенду двома мовами

Нижче наведено повний вихідний код експерименту мовами C та C++. Обидві програми виконують повний цикл: ініціалізацію робочого каталогу, генерацію блоків, вилучення імені файлу через `unlink()`, порівняння метрик VFS і розміру каталогу, інспекцію структури `/proc/self/fd` та оперативне вивільнення блоків без закриття дескриптора.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <dirent.h>
#include <errno.h>
#include <ftw.h>

#define TARGET_DIR "/tmp/disk_test_leak"
#define FILE_NAME "/tmp/disk_test_leak/phantom.bin"
#define ALLOC_SIZE (64 * 1024 * 1024) /* 64 МіБ */

static off_t g_dir_apparent_size = 0;

static int count_file_size(const char *fpath, const struct stat *sb, int typeflag) {
    if (typeflag == FTW_F) {
        g_dir_apparent_size += sb->st_blocks * 512;
    }
    return 0;
}

static off_t measure_directory_usage(const char *dir_path) {
    g_dir_apparent_size = 0;
    if (ftw(dir_path, count_file_size, 16) != 0) {
        perror("Помилка обходу дерева ftw");
        return -1;
    }
    return g_dir_apparent_size;
}

static void print_vfs_status(const char *path, const char *phase_label) {
    struct statvfs st;
    if (statvfs(path, &st) != 0) {
        perror("statvfs error");
        return;
    }

    unsigned long long total_bytes = (unsigned long long)st.f_blocks * st.f_frsize;
    unsigned long long free_bytes = (unsigned long long)st.f_bfree * st.f_frsize;
    unsigned long long avail_bytes = (unsigned long long)st.f_bavail * st.f_frsize;
    off_t du_bytes = measure_directory_usage(path);

    printf("\n[%s]\n", phase_label);
    printf("  Точка VFS:          %s\n", path);
    printf("  Загалом (VFS):      %10llu KiB (%llu MiB)\n", total_bytes / 1024, total_bytes / (1024 * 1024));
    printf("  Вільно (f_bfree):   %10llu KiB (%llu MiB)\n", free_bytes / 1024, free_bytes / (1024 * 1024));
    printf("  Доступно (f_bavail): %8llu KiB (%llu MiB)\n", avail_bytes / 1024, avail_bytes / (1024 * 1024));
    printf("  Каталог (du / ftw): %8lld KiB (%lld MiB)\n", (long long)du_bytes / 1024, (long long)du_bytes / (1024 * 1024));
}

int main(void) {
    mkdir(TARGET_DIR, 0755);

    print_vfs_status(TARGET_DIR, "ЕТАП 1: Початковий стан чистого каталогу");

    int fd = open(FILE_NAME, O_CREAT | O_RDWR | O_TRUNC, 0644);
    if (fd < 0) {
        perror("Не вдалося створити файл");
        return 1;
    }

    /* Виділяємо 64 МіБ реальних блоків на диску */
    if (posix_fallocate(fd, 0, ALLOC_SIZE) != 0) {
        /* Резервний варіант: послідовний запис буфера */
        char buffer[4096];
        memset(buffer, 0xAA, sizeof(buffer));
        for (size_t i = 0; i < ALLOC_SIZE / sizeof(buffer); ++i) {
            if (write(fd, buffer, sizeof(buffer)) != (ssize_t)sizeof(buffer)) {
                perror("write failed");
                close(fd);
                return 1;
            }
        }
    }
    fsync(fd);

    print_vfs_status(TARGET_DIR, "ЕТАП 2: Файл 64 MiB створено й записано на диск");

    /* Вилучаємо запис із каталогу: i_nlink падає до 0 */
    if (unlink(FILE_NAME) != 0) {
        perror("unlink failed");
        close(fd);
        return 1;
    }

    print_vfs_status(TARGET_DIR, "ЕТАП 3: Файл видалено через unlink(), але fd залишається ВІДКРИТИМ");

    printf("\n--> Спроба перевірити /proc/self/fd:\n");
    char fd_path[64];
    char link_target[256];
    snprintf(fd_path, sizeof(fd_path), "/proc/self/fd/%d", fd);
    ssize_t len = readlink(fd_path, link_target, sizeof(link_target) - 1);
    if (len > 0) {
        link_target[len] = '\0';
        printf("  Дескриптор %s вказує на: %s\n", fd_path, link_target);
    }

    printf("\n--> Відновлення місця на льоту: ftruncate(fd, 0)...\n");
    if (ftruncate(fd, 0) != 0) {
        perror("ftruncate failed");
    }

    print_vfs_status(TARGET_DIR, "ЕТАП 4: Дескриптор обнулено (блоки повернуто в суперблок)");

    close(fd);
    rmdir(TARGET_DIR);
    printf("\nТест успішно завершено. Ресурси коректно вивільнено.\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <filesystem>
#include <fstream>
#include <vector>
#include <string>
#include <system_error>
#include <memory>
#include <span>
#include <cstdint>
#include <unistd.h>
#include <fcntl.h>
#include <sys/statvfs.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

class FileDescriptor {
public:
    explicit FileDescriptor(int fd) noexcept : fd_(fd) {}
    ~FileDescriptor() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

private:
    int fd_{-1};
};

struct VfsMetrics {
    std::uint64_t total_kib{0};
    std::uint64_t free_kib{0};
    std::uint64_t avail_kib{0};
    std::uint64_t du_kib{0};
};

class DiskInspector {
public:
    static std::uint64_t calculate_directory_usage(const fs::path& root_path) {
        std::uint64_t total_bytes = 0;
        std::error_code ec;
        if (!fs::exists(root_path, ec)) return 0;

        for (const auto& entry : fs::recursive_directory_iterator(root_path, fs::directory_options::skip_permission_denied, ec)) {
            if (entry.is_regular_file(ec)) {
                struct stat st{};
                if (::lstat(entry.path().c_str(), &st) == 0) {
                    total_bytes += static_cast<std::uint64_t>(st.st_blocks) * 512;
                }
            }
        }
        return total_bytes;
    }

    static VfsMetrics inspect(const fs::path& target_path) {
        struct statvfs st{};
        if (::statvfs(target_path.c_str(), &st) != 0) {
            throw std::system_error(errno, std::generic_category(), "statvfs failed");
        }

        const auto block_size = static_cast<std::uint64_t>(st.f_frsize);
        VfsMetrics metrics;
        metrics.total_kib = (st.f_blocks * block_size) / 1024;
        metrics.free_kib = (st.f_bfree * block_size) / 1024;
        metrics.avail_kib = (st.f_bavail * block_size) / 1024;
        metrics.du_kib = calculate_directory_usage(target_path) / 1024;
        return metrics;
    }

    static void print_status(const fs::path& target_path, std::string_view phase_label) {
        const auto m = inspect(target_path);
        std::cout << "\n[" << phase_label << "]\n"
                  << "  Точка VFS:          " << target_path << "\n"
                  << "  Загалом (VFS):      " << m.total_kib << " KiB (" << m.total_kib / 1024 << " MiB)\n"
                  << "  Вільно (f_bfree):   " << m.free_kib << " KiB (" << m.free_kib / 1024 << " MiB)\n"
                  << "  Доступно (f_bavail): " << m.avail_kib << " KiB (" << m.avail_kib / 1024 << " MiB)\n"
                  << "  Каталог (du/stat):  " << m.du_kib << " KiB (" << m.du_kib / 1024 << " MiB)\n";
    }
};

int main() {
    const fs::path test_dir = "/tmp/disk_test_cpp_leak";
    const fs::path test_file = test_dir / "phantom_cpp.bin";
    constexpr std::size_t alloc_bytes = 64 * 1024 * 1024; // 64 MiB

    std::error_code ec;
    fs::create_directories(test_dir, ec);

    DiskInspector::print_status(test_dir, "ЕТАП 1: Чистий каталог");

    FileDescriptor fd(::open(test_file.c_str(), O_CREAT | O_RDWR | O_TRUNC, 0644));
    if (!fd.valid()) {
        std::cerr << "Помилка відкриття файлу: " << std::generic_category().message(errno) << "\n";
        return 1;
    }

    if (::posix_fallocate(fd.get(), 0, alloc_bytes) != 0) {
        std::vector<char> buffer(4096, '\xBB');
        for (std::size_t i = 0; i < alloc_bytes / buffer.size(); ++i) {
            if (::write(fd.get(), buffer.data(), buffer.size()) != static_cast<ssize_t>(buffer.size())) {
                std::cerr << "Write error\n";
                return 1;
            }
        }
    }
    ::fsync(fd.get());

    DiskInspector::print_status(test_dir, "ЕТАП 2: Файл 64 MiB створено й зафіксовано на диску");

    if (::unlink(test_file.c_str()) != 0) {
        std::cerr << "Unlink error: " << std::generic_category().message(errno) << "\n";
        return 1;
    }

    DiskInspector::print_status(test_dir, "ЕТАП 3: Файл видалено з каталогу (unlink), але дескриптор відкрито");

    const fs::path proc_fd = fs::path("/proc/self/fd") / std::to_string(fd.get());
    if (fs::exists(proc_fd, ec)) {
        const auto target = fs::read_symlink(proc_fd, ec);
        std::cout << "\n--> Інспекція /proc/self/fd:\n"
                  << "  Дескриптор " << proc_fd << " посилається на: " << target << "\n";
    }

    std::cout << "\n--> Вивільнення блоків на льоту через ::ftruncate(fd, 0)...\n";
    if (::ftruncate(fd.get(), 0) != 0) {
        std::cerr << "ftruncate failed: " << std::generic_category().message(errno) << "\n";
    }

    DiskInspector::print_status(test_dir, "ЕТАП 4: Розмір скинуто до 0 (блоки звільнено)");

    fs::remove_all(test_dir, ec);
    std::cout << "\nТестування успішно завершено.\n";
    return 0;
}
```
:::

## Покроковий аналіз внутрішніх станів ядра

Під час послідовного проходження чотирьох етапів програми спостерігаються точні зміни структур ядра:

1. **Етап 1 (Вихідний стан):** Значення `f_bfree` у структурі суперблока максимальне. Утиліта рекурсивного сканування каталогу повертає рівно 0 KiB зайнятого простору, оскільки каталог не містить жодного файлу.
2. **Етап 2 (Виділення блоків):** Виклик `posix_fallocate()` виділяє 16 384 фізичні блоки розміром по 4096 байтів. Лічильник вільних блоків суперблока `f_bfree` зменшується рівно на 65 536 KiB. Функція обходу каталогу підтверджує ті самі 65 536 KiB зайнятого простору на основі поля `st_blocks × 512`. На цьому етапі глобальний облік VFS і сканування каталогу перебувають у повній згоді.
3. **Етап 3 (Фаза розриву зв'язку):** Системний виклик `unlink()` видаляє запис `dirent` із каталогу `/tmp/disk_test_leak`. Лічильник `i_nlink` відповідного інода падає до 0. Функція обходу каталогу більше не знаходить жодного запису й рапортує 0 KiB зайнятого місця. Проте запит `statvfs()` продовжує показувати ті самі 64 МіБ як зайняті! Дискові блоки утримуються драйвером файлової системи, тому що структура `struct inode` має активний лічильник `i_count = 1` від відкритого дескриптора в таблиці процесу. Символьне посилання `/proc/self/fd/[fd]` вказує на назву з міткою `(deleted)`.
4. **Етап 4 (Оперативне відновлення):** Виклик `ftruncate(fd, 0)` надсилає команду драйверу файлової системи на скорочення логічної довжини файлу до нуля. Драйвер звільняє екстенти блоків, позначає їх нулями в бітовій карті розподілу та повертає в лічильник `f_bfree` суперблока. Показник вільного простору миттєво повертається до початкового значення, хоча дескриптор процесу залишається відкритим і цілком придатним для подальшої роботи.

## Сценарій автоматизованого тестування через bash

Для швидкої демонстрації ефекту на реальному сервері без компіляції C++ коду можна скористатися простим сценарієм командного інтерпретатора bash:

```bash
#!/usr/bin/env bash
set -euo pipefail

TEST_DIR="/tmp/bash_disk_experiment"
mkdir -p "$TEST_DIR"

echo "=== 1. Початковий стан ==="
df -h "$TEST_DIR"
du -sh "$TEST_DIR"

# Запускаємо фоновий процес, який створює файл і утримує його відкритим
python3 -c "
import time, os
f = open('$TEST_DIR/leak.log', 'w')
f.write('X' * (64 * 1024 * 1024))
f.flush()
print('Файл створено. Очікування...')
while True:
    time.sleep(1)
" &
PY_PID=$!
sleep 2

echo "=== 2. Файл створено ==="
df -h "$TEST_DIR"
du -sh "$TEST_DIR"

# Видаляємо файл із каталогу
rm -f "$TEST_DIR/leak.log"

echo "=== 3. Файл видалено через rm, але процес працює ==="
df -h "$TEST_DIR"
du -sh "$TEST_DIR"

echo "=== 4. Пошук через lsof ==="
lsof +L1 "$TEST_DIR" || true

echo "=== 5. Звільнення місця через /proc ==="
# Знаходимо дескриптор процесу python
FD=$(ls -l /proc/$PY_PID/fd | grep 'leak.log' | awk '{print $9}')
echo "Обнулення /proc/$PY_PID/fd/$FD..."
: > "/proc/$PY_PID/fd/$FD"

echo "=== 6. Стан після обнулення ==="
df -h "$TEST_DIR"
du -sh "$TEST_DIR"

# Завершуємо процес
kill -9 "$PY_PID"
rm -rf "$TEST_DIR"
```

## Практичні аспекти та підводні камені

1. **Особливості зміщення `f_pos` та прапорець `O_APPEND`:** Якщо процес відкрив файл без прапорця `O_APPEND`, внутрішнє зміщення позиції читання-запису `f_pos` після виклику `ftruncate(fd, 0)` залишається на старій позиції (наприклад, 64 МіБ). Будь-який наступний системний виклик `write()` створить розріджений файл (*sparse file*), утворивши діру між нульовим байтом і поточною позицією. Якщо ж файл відкрито з прапорцем `O_APPEND`, ядро автоматично зміщує `f_pos` на поточний фізичний кінець файлу (який після `ftruncate` стає рівним 0), і запис продовжується з самого початку файлу без утворення розріджених дірок.
2. **Права доступу та безпека в `/proc`:** Для виконання команди обнулення `> /proc/[pid]/fd/[fd]` інженер повинен мати привілеї користувача, від імені якого працює цільовий процес, або права адміністратора `root` (адміністративні спроможності `CAP_DAC_OVERRIDE` та `CAP_SYS_PTRACE`).
3. **Файлові системи зі знімками (Btrfs, ZFS):** На сучасних CoW-системах вивільнення блоків через `ftruncate` може не призвести до негайного зростання `f_bfree`, якщо ці самі блоки зафіксовані в активному миттєвому знімку (*snapshot*). У такому разі вільні блоки повертаються в суперблок лише після повного видалення знімка.
4. **Інспекція через `debugfs`:** На файлових системах ext4 інженер із правами root може дослідити стан інода без імені напряму на сирому блоковому пристрої за допомогою інтерактивної утиліти `debugfs -R 'stat <номер_інода>' /dev/sdX`. Утиліта покаже поле `Links: 0`, але виведе повне дерево екстентів та номери фізичних дискових блоків, які продовжують залишатися виділеними доти, доки процес не закриє дескриптор.
