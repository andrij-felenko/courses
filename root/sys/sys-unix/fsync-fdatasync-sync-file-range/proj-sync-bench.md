# ⚙️ Вимірювання продуктивності скидання кешу та реалізація надійного накопичення

Для розуміння ціни гарантій довговічності у високонавантажених системах критично порівняти затримку та пропускну здатність операцій `fsync()`, `fdatasync()`, `sync_file_range()` та прапорця `O_DSYNC`. Нижче наведено практичні реалізації тесту на мовах C та C++, які вимірюють затримки скидання кешу на реальному файлі та демонструють безпечну конвеєризацію запису.

## 1. Контракт та відмінності реалізацій

Практичний тест виконує серію циклічних записів блоками по 4 КіБ і порівнює чотири стратегії синхронізації:
1. `fsync(fd)` після кожного запису (повний захист даних і метаданих).
2. `fdatasync(fd)` після кожного запису (захист даних та розміру файла).
3. `sync_file_range()` після кожного запису (асинхронна конвеєризація сторінок без дискового `FLUSH`).
4. `open(..., O_DSYNC)` з безпосереднім записом через `write()`.

У коді мовою C++ використовуються класичні принципи RAII (Resource Acquisition Is Initialization) для безпечного закриття файлових дескрипторів при виникненні винятків чи передчасному виході, а також хронометрія високої точності через `std::chrono::high_resolution_clock`.

## 2. Реалізація бенчмарка

:::tabs
```c
/* bench_sync.c — Вимірювання затримок системних викликів скидання кешу в C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>
#include <errno.h>

#define BLOCK_SIZE 4096
#define ITERATIONS 1000

static double get_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static int run_test_fsync(const char *filename) {
    int fd = open(filename, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) return -1;

    char buffer[BLOCK_SIZE];
    memset(buffer, 'A', BLOCK_SIZE);

    double start = get_time_sec();
    for (int i = 0; i < ITERATIONS; i++) {
        if (write(fd, buffer, BLOCK_SIZE) != BLOCK_SIZE) {
            close(fd);
            return -1;
        }
        if (fsync(fd) < 0) {
            close(fd);
            return -1;
        }
    }
    double elapsed = get_time_sec() - start;

    close(fd);
    printf("  [fsync]      %d ітерацій: %.4f с (%.2f ops/sec, %.3f мс/op)\n",
           ITERATIONS, elapsed, ITERATIONS / elapsed, (elapsed / ITERATIONS) * 1000.0);
    return 0;
}

static int run_test_fdatasync(const char *filename) {
    int fd = open(filename, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) return -1;

    char buffer[BLOCK_SIZE];
    memset(buffer, 'B', BLOCK_SIZE);

    double start = get_time_sec();
    for (int i = 0; i < ITERATIONS; i++) {
        if (write(fd, buffer, BLOCK_SIZE) != BLOCK_SIZE) {
            close(fd);
            return -1;
        }
        if (fdatasync(fd) < 0) {
            close(fd);
            return -1;
        }
    }
    double elapsed = get_time_sec() - start;

    close(fd);
    printf("  [fdatasync]  %d ітерацій: %.4f с (%.2f ops/sec, %.3f мс/op)\n",
           ITERATIONS, elapsed, ITERATIONS / elapsed, (elapsed / ITERATIONS) * 1000.0);
    return 0;
}

static int run_test_sync_range(const char *filename) {
    int fd = open(filename, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) return -1;

    char buffer[BLOCK_SIZE];
    memset(buffer, 'C', BLOCK_SIZE);

    double start = get_time_sec();
    off64_t offset = 0;
    for (int i = 0; i < ITERATIONS; i++) {
        if (write(fd, buffer, BLOCK_SIZE) != BLOCK_SIZE) {
            close(fd);
            return -1;
        }
        if (sync_file_range(fd, offset, BLOCK_SIZE,
                            SYNC_FILE_RANGE_WAIT_BEFORE |
                            SYNC_FILE_RANGE_WRITE |
                            SYNC_FILE_RANGE_WAIT_AFTER) < 0) {
            close(fd);
            return -1;
        }
        offset += BLOCK_SIZE;
    }
    double elapsed = get_time_sec() - start;

    close(fd);
    printf("  [sync_range] %d ітерацій: %.4f с (%.2f ops/sec, %.3f мс/op) [УВАГА: НЕ захищає від знеструмлення!]\n",
           ITERATIONS, elapsed, ITERATIONS / elapsed, (elapsed / ITERATIONS) * 1000.0);
    return 0;
}

static int run_test_odsync(const char *filename) {
    int fd = open(filename, O_WRONLY | O_CREAT | O_TRUNC | O_DSYNC, 0644);
    if (fd < 0) return -1;

    char buffer[BLOCK_SIZE];
    memset(buffer, 'D', BLOCK_SIZE);

    double start = get_time_sec();
    for (int i = 0; i < ITERATIONS; i++) {
        if (write(fd, buffer, BLOCK_SIZE) != BLOCK_SIZE) {
            close(fd);
            return -1;
        }
    }
    double elapsed = get_time_sec() - start;

    close(fd);
    printf("  [O_DSYNC]    %d ітерацій: %.4f с (%.2f ops/sec, %.3f мс/op)\n",
           ITERATIONS, elapsed, ITERATIONS / elapsed, (elapsed / ITERATIONS) * 1000.0);
    return 0;
}

int main(void) {
    printf("=== Бенчмарк скидання кешу (C) ===\n");
    const char *testfile = "sync_bench.tmp";

    if (run_test_fsync(testfile) < 0) perror("fsync failed");
    if (run_test_fdatasync(testfile) < 0) perror("fdatasync failed");
    if (run_test_sync_range(testfile) < 0) perror("sync_file_range failed");
    if (run_test_odsync(testfile) < 0) perror("O_DSYNC failed");

    unlink(testfile);
    return 0;
}
```
```cpp
// bench_sync.cpp — Вимірювання затримок системних викликів скидання кешу в C++20
#include <iostream>
#include <vector>
#include <chrono>
#include <string_view>
#include <memory>
#include <system_error>
#include <span>
#include <cstdint>
#include <unistd.h>
#include <fcntl.h>

namespace storage {

class FileDescriptor {
    int fd_ = -1;

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
};

class SyncBenchmark {
    static constexpr std::size_t BlockSize = 4096;
    static constexpr std::size_t Iterations = 1000;

    static FileDescriptor open_file(std::string_view path, int flags) {
        int fd = ::open(path.data(), flags, 0644);
        if (fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити файл");
        }
        return FileDescriptor{fd};
    }

public:
    static void test_fsync(std::string_view path) {
        auto file = open_file(path, O_WRONLY | O_CREAT | O_TRUNC);
        std::vector<std::uint8_t> buffer(BlockSize, 'A');

        auto start = std::chrono::high_resolution_clock::now();
        for (std::size_t i = 0; i < Iterations; ++i) {
            if (::write(file.get(), buffer.data(), buffer.size()) != static_cast<ssize_t>(buffer.size())) {
                throw std::system_error(errno, std::generic_category(), "Запис не вдався");
            }
            if (::fsync(file.get()) < 0) {
                throw std::system_error(errno, std::generic_category(), "fsync не вдався");
            }
        }
        auto elapsed = std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - start).count();
        report("fsync", elapsed);
    }

    static void test_fdatasync(std::string_view path) {
        auto file = open_file(path, O_WRONLY | O_CREAT | O_TRUNC);
        std::vector<std::uint8_t> buffer(BlockSize, 'B');

        auto start = std::chrono::high_resolution_clock::now();
        for (std::size_t i = 0; i < Iterations; ++i) {
            if (::write(file.get(), buffer.data(), buffer.size()) != static_cast<ssize_t>(buffer.size())) {
                throw std::system_error(errno, std::generic_category(), "Запис не вдався");
            }
            if (::fdatasync(file.get()) < 0) {
                throw std::system_error(errno, std::generic_category(), "fdatasync не вдався");
            }
        }
        auto elapsed = std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - start).count();
        report("fdatasync", elapsed);
    }

    static void test_sync_file_range(std::string_view path) {
        auto file = open_file(path, O_WRONLY | O_CREAT | O_TRUNC);
        std::vector<std::uint8_t> buffer(BlockSize, 'C');

        auto start = std::chrono::high_resolution_clock::now();
        off64_t offset = 0;
        for (std::size_t i = 0; i < Iterations; ++i) {
            if (::write(file.get(), buffer.data(), buffer.size()) != static_cast<ssize_t>(buffer.size())) {
                throw std::system_error(errno, std::generic_category(), "Запис не вдався");
            }
            if (::sync_file_range(file.get(), offset, BlockSize,
                                  SYNC_FILE_RANGE_WAIT_BEFORE |
                                  SYNC_FILE_RANGE_WRITE |
                                  SYNC_FILE_RANGE_WAIT_AFTER) < 0) {
                throw std::system_error(errno, std::generic_category(), "sync_file_range не вдався");
            }
            offset += BlockSize;
        }
        auto elapsed = std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - start).count();
        report("sync_file_range", elapsed);
    }

    static void test_odsync(std::string_view path) {
        auto file = open_file(path, O_WRONLY | O_CREAT | O_TRUNC | O_DSYNC);
        std::vector<std::uint8_t> buffer(BlockSize, 'D');

        auto start = std::chrono::high_resolution_clock::now();
        for (std::size_t i = 0; i < Iterations; ++i) {
            if (::write(file.get(), buffer.data(), buffer.size()) != static_cast<ssize_t>(buffer.size())) {
                throw std::system_error(errno, std::generic_category(), "Запис не вдався");
            }
        }
        auto elapsed = std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - start).count();
        report("O_DSYNC", elapsed);
    }

private:
    static void report(std::string_view name, double seconds) {
        double ops = Iterations / seconds;
        double ms_per_op = (seconds / Iterations) * 1000.0;
        std::cout << "  [" << name << "] " << Iterations << " ітерацій: "
                  << seconds << " с (" << ops << " ops/sec, " << ms_per_op << " мс/op)\n";
    }
};

} // namespace storage

int main() {
    std::cout << "=== Бенчмарк скидання кешу (C++20) ===\n";
    constexpr std::string_view testfile = "sync_bench_cpp.tmp";

    try {
        storage::SyncBenchmark::test_fsync(testfile);
        storage::SyncBenchmark::test_fdatasync(testfile);
        storage::SyncBenchmark::test_sync_file_range(testfile);
        storage::SyncBenchmark::test_odsync(testfile);
    } catch (const std::exception& ex) {
        std::cerr << "Помилка тестування: " << ex.what() << '\n';
        ::unlink(testfile.data());
        return 1;
    }

    ::unlink(testfile.data());
    return 0;
}
```
:::

## 3. Детальний аналіз механіки виконання та порівняльний розбір

Для точного оцінювання роботи кожного з чотирьох методів розглянемо внутрішню механіку ядра Linux, яка запускається під час виконання даної тестової програми.

### Механіка Тесту 1: `fsync(fd)`
У кожній ітерації циклу програма здійснює запис 4 КіБ даних через `write()`, після чого викликає `fsync(fd)`. Ядро під час виклику `fsync()` виконує наступні кроки:
1. Пошук сторінки у `radix-tree`/`xarray` дескриптора файлу.
2. Зміна стану сторінки з dirty на writeback та передача `bio` запиту до блокового шару.
3. Формування транзакції метаданих у журналі файлової системи (наприклад, ext4 JBD2) для збереження нового значення часу модифікації `st_mtime` та збільшення розміру файла `st_size`.
4. Видача команди `REQ_PREFLUSH` накопичувачу, що змушує дисковий контролер зачекати на фізичний запис даних з DRAM у Flash-осередки.
5. Завершення виклику після отримання апаратного переривання від диска.

### Механіка Тесту 2: `fdatasync(fd)`
У цьому тесті операція `write()` виконується в межах новоствореного файла. Оскільки розширення файла модифікує розмір `st_size`, перші ітерації `fdatasync()` також оновлюють метадані. Проте якщо файл заздалегідь розширено (або у випадку перезапису існуючих блоків), `fdatasync()` пропускає етап створення журнальної транзакції для `st_mtime`. Це позбавляє дискову підсистему потреби записувати додаткові блоки журналу — і виграш тим більший, чим дорожча журнальна транзакція конкретної файлової системи.

### Механіка Тесту 3: `sync_file_range(...)`
У даній стратегії програма використовує прапорці `SYNC_FILE_RANGE_WAIT_BEFORE | SYNC_FILE_RANGE_WRITE | SYNC_FILE_RANGE_WAIT_AFTER`. 
- Виклик чекає, поки брудні сторінки ядра будуть передані дисковому контролеру через DMA, але **не надсилає** команду `FLUSH`.
- Затримка виконання виклику виявляється у 5–10 разів нижчою (близько 0.02–0.05 мс проти 0.2–0.5 мс для `fsync` на NVMe SSD).
- Проте цей тест наочно демонструє відсутність справжнього захисту від знеструмлення: байти осідають у волатильному DRAM-кеші накопичувача.

### Механіка Тесту 4: `open(..., O_DSYNC)`
При відкритті файла з прапорцем `O_DSYNC` кожен `write()` наприкінці сам проходить шлях `fdatasync()` (`generic_write_sync()` → `vfs_fsync_range()`). Там, де накопичувач підтримує Force Unit Access, блоковий шар може позначити сам запис ознакою `REQ_FUA` замість окремої команди `FLUSH`.
- Перевага: відсутній додатковий перехід між користувацьким простором та ядром (user-to-kernel context switch) для виклику `fdatasync()`.
- Недолік: унеможливлюється групування (batching) кількох послідовних записів в один дисковий транш.

## 4. Вплив апаратури: Серверні накопичувачі з PLP (Power Loss Protection)

Результати вимірювання затримок дискових систем можуть суттєво відрізнятися залежно від того, де саме виконується тестова програма:

1. **Споживацькі NVMe/SATA SSD (Consumer-grade SSDs)**:
   Такі накопичувачі мають волатильний DRAM-кеш і не володіють резервними конденсаторами. При отриманні дискової команди `FLUSH` (згенерованої системними викликами `fsync` або `fdatasync`) контролер диска призупиняє прийом нових запитів і виштовхує весь вміст DRAM у NAND Flash. Це дає високі затримки (від 0.3 до 2.0 мс на виклик).

2. **Корпоративні серверні SSD з підтримкою PLP (Enterprise SSDs with Power Loss Protection)**:
   Серверні SSD оснащено масивом іоністорів (суперконденсаторів), які надають достатньо енергії для автоматичного скидання DRAM-кешу у Flash при несподіваному вимкненні електроживлення. Контролер такого диска вважає свій DRAM-буфер **енергонезалежним** і відповідає успіхом на команду `FLUSH` майже миттєво. Затримка `fsync()` на таких дисках знижується до 20–40 мікросекунд, що наближає продуктивність `fsync` до `sync_file_range`.

3. **Віртуальні машини та режими кешування гіпервізора (KVM / QEMU / VMware)**:
   При запуску бенчмарка у середовищі віртуалізації поведінка регулюється параметром дискового кешу гіпервізора:
   - `cache=writethrough` або `cache=directsync`: гіпервізор чекає на справжній дисковий `FLUSH` хоста. Результати відображають реальну продуктивність носія.
   - `cache=unsafe`: гіпервізор ігнорує дискові команди `FLUSH`, перетворюючи всі `fsync` у швидкі операції в RAM хоста. Вимірювати надійність у цьому режимі немає сенсу.

## 5. Профілювання за допомогою системних утиліт

Для підтвердження різниці у дискових викликах під час запуску бенчмарка рекомендується використовувати утиліти `strace` та `blktrace`:

```bash
# Підрахунок кількості системних викликів та часу виконання
strace -c ./bench_sync

# Моніторинг команд FLUSH/FUA на рівні блокового пристрою
sudo blktrace -d /dev/nvme0n1 -o - | blkparse -i - | grep -E "FLUSH|FUA"
```

При запуску на `tmpfs` (RAM-диск) усі чотири методи повертають миттєвий успіх (під 1 000 000 ops/sec), оскільки `tmpfs` взагалі не має блокового пристрою й не реалізує дискові команди `FLUSH`. Для вимірювання справжніх гарантій довговічності тестування обов'язково має проводитися на фізичних SSD/NVMe носіях із журнальними файловими системами (ext4, xfs).
