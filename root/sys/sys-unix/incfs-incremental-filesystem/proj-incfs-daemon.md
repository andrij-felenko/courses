# ⚙️ Демон керування та заповнення блоків IncFS

Практична взаємодія з інкрементальною файловою системою IncFS вимагає створення користувацького фонового сервісу (демона), який відкриває службові файли керування, відстежує запити читання від інших процесів та динамічно заповнює відсутні блоки даних. Нижче наведено детальний аналіз архітектури, тестового середовища, оптимізації продуктивності та завершену реалізацію мінімального демона заповнення блоків IncFS мовами C та C++.

## Архітектура та функціональна схема демона

Демон заповнення блоків виконує роль проміжної ланки між підсистемою ядра Linux IncFS та віддаленим джерелом даних (мережевий CDN-сервер або інструмент розробника `adb` через кабель USB).

Демон виконує чотири послідовні кроки для забезпечення прозорого підкачування сторінок даних:

1. **Ініціалізація та відкриття файлу подій:** Сервіс відкриває службовий файл `.pending_reads` у корені змонтованої точки IncFS у режимі читання `O_RDONLY`.
2. **Очікування запитів через системний виклик `poll()`:** Потік очікує появи подій `EPOLLIN` від ядра Linux без марнотратного завантаження процесора.
3. **Зчитування списку відсутніх блоків:** Читає масив структур `incfs_pending_read_info`, що містять UUID файлу та індекс відсутнього блоку.
4. **Генерація та заповнення блоку через `ioctl`:** Створює або завантажує з мережі буфер розміром 4096 байт і викликає команду `INCFS_IOC_FILL_BLOCKS`.

```
                  +--------------------------+
                  |  Відкриття .pending_reads|
                  +--------------------------+
                               |
                               v
                  +--------------------------+
                  |   poll() — очікування    | <------+
                  +--------------------------+        |
                               | (Є подія)            |
                               v                      |
                  +--------------------------+        |
                  |  read() запиту з ядра    |        |
                  +--------------------------+        |
                               |                      |
                               v                      |
                  +--------------------------+        |
                  | INCFS_IOC_FILL_BLOCKS    | -------+
                  +--------------------------+
```

---

## Покроковий розбір життєвого циклу заповнення

Перш ніж розглядати код, детально простежимо потік виконання операцій, підготовку середовища та механізми оптимізації:

### 1. Монтування тестувального каталогу IncFS
Перед запуском демона у тестовому середовищі Linux створюється точка монтування через команду `mount`:
```bash
# Створення базового та цільового каталогів
mkdir -p /tmp/incfs_backing /tmp/incfs_mount

# Монтування файлової системи IncFS
mount -t incfs /tmp/incfs_backing /tmp/incfs_mount
```

### 2. Отримання дескрипторів та розмежування доступу
Демон відкриває два критичні файлові дескриптори:
- Дескриптор на псевдофайл `/tmp/incfs_mount/.pending_reads` для зчитування сповіщень ядра про відсутні блоки.
- Дескриптор самого каталогу `/tmp/incfs_mount` (із прапором `O_DIRECTORY`) — через нього демон відкриває потрібний файл за його File ID у підкаталозі `.index`. Саму команду `INCFS_IOC_FILL_BLOCKS` подають уже на дескриптор цього файлу: структура заповнення не містить File ID, тож файл визначає саме дескриптор.

### 3. Групове заповнення блоків (Batching)
Для оптимізації продуктивності та зменшення кількості системних викликів команда `INCFS_IOC_FILL_BLOCKS` дозволяє передати масив блоків одним викликом. Усі блоки такого масиву належать тому самому файлу — тому, чий дескриптор передано в `ioctl`. Поле `count` у структурі `incfs_fill_blocks` може вказувати на масив із 16, 32 або 64 блоків, які завантажено з мережі в одному пакеті. Це знижує накладні витрати на переключення контексту ядра при високошвидкісному потоковому завантаженні.

### 4. Багатопотоковість та неблокуюче введення-виведення
У реальних виробничих умовах (Android `IncrementalService`) один потік очікування подій розподіляє запити по пулу робочих потоків (*worker thread pool*). Це дозволяє паралельно завантажувати десятки блоків через незалежні HTTP-з'єднання. Для забезпечення найвищої швидкості файлові дескриптори відкриваються із прапорцем `O_NONBLOCK`.

### 5. Обробка таймаутів та системних помилок
Якщо додаток заблокувався на зчитуванні, демон має відреагувати до того, як вичерпається системний таймаут `read_timeout_ms` (за замовчуванням 10 секунд). Тому цикл подій використовує таймаут 5000 мс у виклику `poll()`. У разі збою мережі демон може повторити спробу завантаження блоку до трьох разів.

---

## Реалізація демона: C та C++

:::tabs
```c
/* incfs_daemon.c — Реалізація демона заповнення IncFS мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <stdint.h>
#include <errno.h>

/* Визначення базових структур IncFS */
#define INCFS_IOCTL_BASE 0x67

struct incfs_pending_read_info {
    uint64_t file_id_low;
    uint64_t file_id_high;
    uint32_t timestamp_us;
    uint32_t block_index;
};

struct incfs_fill_block {
    uint32_t block_index;
    uint32_t data_len;
    uint64_t data;
    uint8_t  compression;
    uint8_t  flags;
    uint16_t reserved;
};

struct incfs_fill_blocks {
    uint64_t count;
    uint64_t fill_blocks;
};

#define INCFS_IOC_FILL_BLOCKS _IOW(INCFS_IOCTL_BASE, 2, struct incfs_fill_blocks)

#define BLOCK_SIZE 4096

static int fill_single_block(int incfs_file_fd, uint32_t block_idx) {
    uint8_t buffer[BLOCK_SIZE];
    /* Заповнюємо тестовий блок 4KB впізнаваним паттерном 'A' */
    memset(buffer, 'A', BLOCK_SIZE);

    struct incfs_fill_block fb = {
        .block_index = block_idx,
        .data_len = BLOCK_SIZE,
        .data = (uint64_t)(uintptr_t)buffer,
        .compression = 0,
        .flags = 0,
        .reserved = 0
    };

    struct incfs_fill_blocks fbs = {
        .count = 1,
        .fill_blocks = (uint64_t)(uintptr_t)&fb
    };

    if (ioctl(incfs_file_fd, INCFS_IOC_FILL_BLOCKS, &fbs) < 0) {
        perror("ioctl INCFS_IOC_FILL_BLOCKS failed");
        return -errno;
    }

    printf("[IncFS Daemon C] Блок %u успішно заповнено (4096 байт)\n", block_idx);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_кореню_incfs>\n", argv[0]);
        return EXIT_FAILURE;
    }

    char pending_path[512];
    snprintf(pending_path, sizeof(pending_path), "%s/.pending_reads", argv[1]);

    int pending_fd = open(pending_path, O_RDONLY);
    if (pending_fd < 0) {
        perror("Не вдалося відкрити .pending_reads");
        return EXIT_FAILURE;
    }

    int dir_fd = open(argv[1], O_RDONLY | O_DIRECTORY);
    if (dir_fd < 0) {
        perror("Не вдалося відкрити дескриптор каталогу IncFS");
        close(pending_fd);
        return EXIT_FAILURE;
    }

    printf("[IncFS Daemon C] Демон запущено. Очікування подій на %s...\n", pending_path);

    struct pollfd pfd = {
        .fd = pending_fd,
        .events = POLLIN
    };

    while (1) {
        int ret = poll(&pfd, 1, 5000); /* Таймаут 5 секунд */
        if (ret < 0) {
            perror("Помилка poll()");
            break;
        } else if (ret == 0) {
            printf("[IncFS Daemon C] Таймаут poll(). Запитів немає...\n");
            continue;
        }

        if (pfd.revents & POLLIN) {
            struct incfs_pending_read_info req;
            ssize_t bytes_read = read(pending_fd, &req, sizeof(req));
            if (bytes_read == sizeof(req)) {
                printf("[IncFS Daemon C] Отримано запит: FileID=%llx%llx, Block=%u\n",
                       (unsigned long long)req.file_id_high,
                       (unsigned long long)req.file_id_low,
                       req.block_index);

                char id_path[64];
                snprintf(id_path, sizeof(id_path), ".index/%016llx%016llx",
                         (unsigned long long)req.file_id_high,
                         (unsigned long long)req.file_id_low);

                int file_fd = openat(dir_fd, id_path, O_RDWR | O_CLOEXEC);
                if (file_fd < 0) {
                    perror("Не вдалося відкрити файл за File ID");
                    continue;
                }

                fill_single_block(file_fd, req.block_index);
                close(file_fd);
            }
        }
    }

    close(dir_fd);
    close(pending_fd);
    return EXIT_SUCCESS;
}
```
```cpp
// incfs_daemon.cpp — Ідіоматична реалізація демона IncFS мовою C++20 (RAII, span, expected)
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <memory>
#include <expected>
#include <format>
#include <system_error>
#include <filesystem>
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <sys/ioctl.h>
#include <cstdint>

namespace fs = std::filesystem;

// RAII-обгортка для автоматичного закриття файлового дескриптора POSIX
class UniqueFd {
    int fd_{-1};
public:
    constexpr UniqueFd() noexcept = default;
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
    
    int release() noexcept {
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

constexpr uint32_t kBlockSize = 4096;
constexpr uint8_t kIncfsIoctlBase = 0x67;

struct alignas(8) PendingReadInfo {
    uint64_t file_id_low;
    uint64_t file_id_high;
    uint32_t timestamp_us;
    uint32_t block_index;
};

struct IncfsFillBlock {
    uint32_t block_index;
    uint32_t data_len;
    uint64_t data;
    uint8_t  compression{0};
    uint8_t  flags{0};
    uint16_t reserved{0};
};

struct IncfsFillBlocks {
    uint64_t count;
    uint64_t fill_blocks;
};

#define INCFS_IOC_FILL_BLOCKS _IOW(kIncfsIoctlBase, 2, IncfsFillBlocks)

class IncfsDaemon {
    UniqueFd pending_fd_;
    UniqueFd dir_fd_;

public:
    static std::expected<IncfsDaemon, std::error_code> create(const fs::path& incfs_root) {
        const auto pending_path = incfs_root / ".pending_reads";
        
        int pfd = ::open(pending_path.c_str(), O_RDONLY | O_CLOEXEC);
        if (pfd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        int dfd = ::open(incfs_root.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC);
        if (dfd < 0) {
            ::close(pfd);
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return IncfsDaemon(UniqueFd(pfd), UniqueFd(dfd));
    }

    std::expected<void, std::error_code> fill_block(const PendingReadInfo& req, std::span<const uint8_t> data) {
        // Заповнення подають на дескриптор самого файлу: IncfsFillBlock не містить File ID.
        // Тому файл відкриваємо за його ідентифікатором у каталозі .index.
        const auto id_path = std::format(".index/{:016x}{:016x}", req.file_id_high, req.file_id_low);
        UniqueFd file_fd{::openat(dir_fd_.get(), id_path.c_str(), O_RDWR | O_CLOEXEC)};
        if (!file_fd.valid()) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        const uint32_t block_index = req.block_index;
        IncfsFillBlock fb{
            .block_index = block_index,
            .data_len = static_cast<uint32_t>(data.size()),
            .data = reinterpret_cast<uint64_t>(data.data())
        };

        IncfsFillBlocks fbs{
            .count = 1,
            .fill_blocks = reinterpret_cast<uint64_t>(&fb)
        };

        if (::ioctl(file_fd.get(), INCFS_IOC_FILL_BLOCKS, &fbs) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        std::cout << "[IncFS Daemon C++] Успішно заповнено блок " << block_index 
                  << " (" << data.size() << " байт)\n";
        return {};
    }

    void run_event_loop() {
        std::cout << "[IncFS Daemon C++] Цикл подій запущено...\n";
        
        std::vector<uint8_t> dummy_payload(kBlockSize, 'B');
        pollfd pfd{.fd = pending_fd_.get(), .events = POLLIN, .revents = 0};

        while (true) {
            int ret = ::poll(&pfd, 1, 5000); // 5 сек таймаут
            if (ret < 0) {
                if (errno == EINTR) continue;
                std::cerr << "[IncFS Daemon C++] Помилка poll(): " 
                          << std::generic_category().message(errno) << '\n';
                break;
            } else if (ret == 0) {
                std::cout << "[IncFS Daemon C++] Таймаут очікування подій...\n";
                continue;
            }

            if (pfd.revents & POLLIN) {
                PendingReadInfo req{};
                ssize_t nread = ::read(pending_fd_.get(), &req, sizeof(req));
                if (nread == sizeof(req)) {
                    std::cout << "[IncFS Daemon C++] Запит блоку: Index=" << req.block_index 
                              << ", Timestamp=" << req.timestamp_us << "us\n";

                    if (auto res = fill_block(req, dummy_payload); !res) {
                        std::cerr << "[IncFS Daemon C++] Не вдалося заповнити блок: " 
                                  << res.error().message() << '\n';
                    }
                }
            }
        }
    }

private:
    IncfsDaemon(UniqueFd pfd, UniqueFd dfd) 
        : pending_fd_(std::move(pfd)), dir_fd_(std::move(dfd)) {}
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях_до_кореню_incfs>\n";
        return EXIT_FAILURE;
    }

    auto daemon_res = IncfsDaemon::create(argv[1]);
    if (!daemon_res) {
        std::cerr << "Не вдалося ініціалізувати демон: " 
                  << daemon_res.error().message() << '\n';
        return EXIT_FAILURE;
    }

    daemon_res->run_event_loop();
    return EXIT_SUCCESS;
}
```
:::

---

## Типові пастки та підводні камені

При реалізації виробничих сервісів заповнення блоків IncFS виникає кілька критичних інженерних пасток:

### 1. Взаємне блокування (Deadlock) демона
Якщо потік виконання самого демона спробує відкрити або прочитати інкрементальний файл, який сам же й обслуговує, до заповнення відсутнього блоку, потік демона заблокується у ядрі. Це і є взаємне блокування: демон чекає сам на себе. 

Для уникнення цього демон відкриває файл лише за його File ID у каталозі `.index` і ніколи не читає його вміст: усе, що він робить із цим дескриптором, — це `ioctl` заповнення, який ніде не чекає на відсутні блоки.

### 2. Розміри блоків і межа файлу
Команда `INCFS_IOC_FILL_BLOCKS` приймає блоки рівно по 4096 байтів. Виняток лише один — останній блок файлу: він може бути коротшим, і в `data_len` слід передати його справжню довжину. Некоректний `data_len` або індекс блоку поза межами файлу дають `EINVAL`.

### 3. Багатопоточність та конкурентний доступ
Якщо кілька потоків прикладного додатку одночасно читають різні блоки того самого файлу, ядро Linux генерує кілька подій у `.pending_reads`. Демон повинен обробляти події у паралельних робочих потоках (*thread pool*), щоб уникнути затримок читання для користувача.

### 4. Обробка помилок мережевого з'єднання
При втраті мережевого зв'язку демон повинен коректно обробляти ситуацію неможливості доставлення блоку. Спеціального «блоку помилки» в IncFS немає. Якщо блок доставити не вдалося, демон просто не заповнює його, і читача звільняє таймаут `read_timeout_ms`: `read()` завершиться помилкою `ETIME`, а звернення через `mmap` дістане `SIGBUS`. Підсовувати замість даних сміття не можна — воно або не пройде перевірку за деревом Меркла, або потрапить у гру як пошкоджений ресурс.

### 5. Методика тестування та верифікації через strace
Для аналізу взаємодії демона з ядром та перевірки часу реакції застосовується інструмент `strace`:
```bash
# Простеження викликів poll та ioctl у демоні IncFS
strace -e poll,read,ioctl ./incfs_daemon /tmp/incfs_mount

# Створення запиту читання відсутнього блоку з іншого термінала
dd if=/tmp/incfs_mount/test_file.apk of=/dev/null bs=4096 count=1 skip=5
```
Під час виконання команди `dd` у виводі `strace` чітко видно момент виходу з `poll()`, читання 24 байт структури `incfs_pending_read_info` з `.pending_reads` та успішне виконання `ioctl(..., INCFS_IOC_FILL_BLOCKS)`.
