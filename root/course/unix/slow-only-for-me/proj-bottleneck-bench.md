# ⚙️ Практикум: моделювання та діагностика вузьких місць продуктивності

Цей практикум надає повноцінну тестову лабораторію для відтворення, спостереження та локалізації чотирьох типових режимів деградації продуктивності в Linux. Програма `bottleneck_bench` дозволяє за запитом емулювати чисте обчислювальне навантаження на процесор (CPU-bound), шторм системних викликів (Kernel-bound), блокування спільних м'ютексів (Lock Contention) та синхронні дискові операції із зануренням у неперериваний сон (I/O-bound).

Головна цінність такої лабораторії — навчитися за лічені секунди розпізнавати характерні «відбитки» (signatures) кожного типу навантаження у стандартних утилітах операційної системи (`vmstat`, `pidstat`, `iostat`, `strace`, `perf`) та бачити, як системні виклики та стани ядра транслюються у показники затримок.

---

## 1. Архітектура тестового стенда

Програма приймає один із чотирьох аргументів командного рядка:
* `cpu`: запускає інтенсивний математичний розрахунок із хешуванням пам'яті (100% завантаження в `%usr`, стан `R`).
* `syscall`: виконує 2 000 000 небуферизованих 1-байтних системних викликів `write()` (85–95% завантаження в `%sys`).
* `lock`: створює 8 потоків, які агресивно конкурують за один короткоживучий м'ютекс (шторм системних викликів `futex` та сплеск `cswch/s`).
* `io`: виконує циклічні синхронні записи з примусовим прапорцем `O_SYNC` та викликом `fdatasync()` (стан процесу `D`, сплеск `%wa` та затримки `await`).

:::tabs
@tab C
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdint.h>
#include <time.h>
#include <errno.h>

#define THREAD_COUNT 8
#define LOCK_ITERATIONS 5000000
#define SYSCALL_ITERATIONS 2000000
#define IO_ITERATIONS 2000

/* Режим 1: Чисте обчислювальне навантаження (CPU-bound) */
void run_cpu_bound(void) {
    printf("[CPU-bound] Старт математичного циклу. Перевіряйте: perf top -p %d\n", getpid());
    volatile uint64_t hash = 0x123456789ABCDEF0ULL;
    while (1) {
        for (uint64_t i = 0; i < 100000000ULL; ++i) {
            hash ^= (i + 0x9e3779b9 + (hash << 6) + (hash >> 2));
        }
        /* Невелика пауза для перевірки сигналів переривання */
        usleep(1000);
    }
}

/* Режим 2: Шторм системних викликів (Kernel-bound) */
void run_syscall_bound(void) {
    printf("[Kernel-bound] Старт шторму викликів write(). Перевіряйте: strace -c -p %d\n", getpid());
    int fd = open("/dev/null", O_WRONLY);
    if (fd < 0) {
        perror("open /dev/null");
        return;
    }

    char byte = 'A';
    while (1) {
        for (size_t i = 0; i < SYSCALL_ITERATIONS; ++i) {
            if (write(fd, &byte, 1) != 1) {
                perror("write error");
                break;
            }
        }
        usleep(10000);
    }
    close(fd);
}

/* Режим 3: Конкуренція за блокування (Lock / Futex Contention) */
static pthread_mutex_t g_mutex = PTHREAD_MUTEX_INITIALIZER;
static volatile uint64_t g_shared_counter = 0;

void *lock_worker_thread(void *arg) {
    (void)arg;
    while (1) {
        for (size_t i = 0; i < 100000; ++i) {
            pthread_mutex_lock(&g_mutex);
            g_shared_counter++;
            pthread_mutex_unlock(&g_mutex);
        }
        usleep(1000);
    }
    return NULL;
}

void run_lock_contention(void) {
    printf("[Lock-bound] Старт 8 потоків із спільним м'ютексом. Перевіряйте: pidstat -w -p %d\n", getpid());
    pthread_t threads[THREAD_COUNT];
    for (int i = 0; i < THREAD_COUNT; ++i) {
        if (pthread_create(&threads[i], NULL, lock_worker_thread, NULL) != 0) {
            perror("pthread_create");
            return;
        }
    }
    for (int i = 0; i < THREAD_COUNT; ++i) {
        pthread_join(threads[i], NULL);
    }
}

/* Режим 4: Синхронний I/O (I/O-bound, стан D) */
void run_io_bound(void) {
    const char *test_file = "/tmp/bottleneck_sync.tmp";
    printf("[I/O-bound] Старт синхронного запису у %s. Перевіряйте: iostat -xz 1\n", test_file);
    
    int fd = open(test_file, O_WRONLY | O_CREAT | O_TRUNC | O_SYNC, 0644);
    if (fd < 0) {
        perror("open sync file");
        return;
    }

    char buffer[4096];
    memset(buffer, 'Z', sizeof(buffer));

    while (1) {
        for (size_t i = 0; i < IO_ITERATIONS; ++i) {
            if (write(fd, buffer, sizeof(buffer)) != (ssize_t)sizeof(buffer)) {
                perror("write sync");
                break;
            }
            fdatasync(fd);
        }
        lseek(fd, 0, SEEK_SET);
    }
    close(fd);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s [cpu|syscall|lock|io]\n", argv[0]);
        return 1;
    }

    printf("PID процесу: %d\n", getpid());

    if (strcmp(argv[1], "cpu") == 0) {
        run_cpu_bound();
    } else if (strcmp(argv[1], "syscall") == 0) {
        run_syscall_bound();
    } else if (strcmp(argv[1], "lock") == 0) {
        run_lock_contention();
    } else if (strcmp(argv[1], "io") == 0) {
        run_io_bound();
    } else {
        fprintf(stderr, "Невідомий режим: %s\n", argv[1]);
        return 1;
    }
    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <thread>
#include <mutex>
#include <chrono>
#include <span>
#include <memory>
#include <fcntl.h>
#include <unistd.h>
#include <system_error>
#include <cstring>

namespace {

constexpr size_t THREAD_COUNT = 8;
constexpr size_t SYSCALL_ITERATIONS = 2'000'000;
constexpr size_t IO_ITERATIONS = 2'000;

class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(const char* path, int flags, mode_t mode = 0644) {
        fd_ = ::open(path, flags, mode);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка відкриття дескриптора");
        }
    }
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }
    
    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;
    UniqueFd(UniqueFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
};

void run_cpu_bound() {
    std::cout << "[CPU-bound] Старт обчислень. PID: " << ::getpid() << '\n';
    volatile uint64_t hash = 0x123456789ABCDEF0ULL;
    while (true) {
        for (uint64_t i = 0; i < 100'000'000ULL; ++i) {
            hash ^= (i + 0x9e3779b9 + (hash << 6) + (hash >> 2));
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
}

void run_syscall_bound() {
    std::cout << "[Kernel-bound] Старт шторму системних викликів. PID: " << ::getpid() << '\n';
    UniqueFd null_dev("/dev/null", O_WRONLY);
    const char byte = 'A';
    while (true) {
        for (size_t i = 0; i < SYSCALL_ITERATIONS; ++i) {
            if (::write(null_dev.get(), &byte, 1) != 1) {
                throw std::system_error(errno, std::generic_category(), "Помилка запису у /dev/null");
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
}

void run_lock_contention() {
    std::cout << "[Lock-bound] Старт потоків із м'ютексом. PID: " << ::getpid() << '\n';
    std::mutex mtx;
    volatile uint64_t counter = 0;
    std::vector<std::jthread> workers;
    workers.reserve(THREAD_COUNT);

    for (size_t i = 0; i < THREAD_COUNT; ++i) {
        workers.emplace_back([&mtx, &counter]() {
            while (true) {
                for (size_t k = 0; k < 100'000; ++k) {
                    std::lock_guard<std::mutex> lock(mtx);
                    counter++;
                }
                std::this_thread::sleep_for(std::chrono::milliseconds(1));
            }
        });
    }
}

void run_io_bound() {
    const char* path = "/tmp/bottleneck_sync_cpp.tmp";
    std::cout << "[I/O-bound] Старт синхронного введення-виведення. PID: " << ::getpid() << '\n';
    UniqueFd sync_file(path, O_WRONLY | O_CREAT | O_TRUNC | O_SYNC, 0644);

    std::vector<char> buffer(4096, 'Z');
    while (true) {
        for (size_t i = 0; i < IO_ITERATIONS; ++i) {
            if (::write(sync_file.get(), buffer.data(), buffer.size()) != static_cast<ssize_t>(buffer.size())) {
                throw std::system_error(errno, std::generic_category(), "Помилка sync write");
            }
            ::fdatasync(sync_file.get());
        }
        ::lseek(sync_file.get(), 0, SEEK_SET);
    }
}

} // namespace

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " [cpu|syscall|lock|io]\n";
        return 1;
    }

    const std::string_view mode = argv[1];
    try {
        if (mode == "cpu") run_cpu_bound();
        else if (mode == "syscall") run_syscall_bound();
        else if (mode == "lock") run_lock_contention();
        else if (mode == "io") run_io_bound();
        else {
            std::cerr << "Невідомий режим: " << mode << '\n';
            return 1;
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

---

## 2. Покроковий практикум діагностики

### Збірка програми

```sh
# Збірка версії на C
gcc -O2 -fno-omit-frame-pointer -pthread bottleneck_bench.c -o bench_c

# Збірка версії на C++ (C++20)
g++ -O2 -std=c++20 -fno-omit-frame-pointer -pthread bottleneck_bench.cpp -o bench_cpp
```

Прапорець `-fno-omit-frame-pointer` є критично важливим: він змушує компілятор зберігати базовий покажчик стека в регістрі `RBP`. Це дозволяє утилітам `perf`, `bpftrace` та ядру Linux розмотувати стек викликів функцій із мінімальними накладними витратами без читання важких DWARF-таблиць.

---

### Дослід 1: Діагностика режиму CPU-bound

У цьому режимі програма виконує інтенсивний розрахунок псевдовипадкового хешу. Дані повністю поміщаються в регістри та кеш першого рівня L1.

Запускаємо обчислювальний режим у фоні:

```sh
./bench_cpp cpu &
# Нехай процес отримав PID 51200
```

1. **Знімаємо метрики розподілу процесора через `pidstat`:**
   ```sh
   pidstat -u 1 -p 51200
   ```
   *Аналіз виводу:*
   ```
   15:01:10   UID     PID    %usr %system  %guest   %wait    %CPU   CPU  Command
   15:01:11  1000   51200   99.80    0.20    0.00    0.00  100.00     2  bench_cpp
   ```
   Показник `%usr` становить майже 100%, системний час `sy` мінімальний. Процес обчислює виключно власний код у просторі користувача.

2. **Перевіряємо ефективність конвеєра через `perf stat`:**
   ```sh
   perf stat -p 51200 -- sleep 3
   ```
   *Аналіз апаратних лічильників:*
   ```
   Performance counter stats for process id '51200':
        9,451,204,112      cycles                    #    3.150 GHz
       20,320,089,450      instructions              #    2.15  insn per cycle
          124,512,900      branches                  #   41.504 M/sec
              142,100      branch-misses             #    0.11% of all branches
   ```
   Показник `insn per cycle` (IPC) становить `2.15`. Це означає, що процесор виконує понад 2 корисні інструкції за кожен такт, а конвеєр не простоює в очікуванні пам'яті.

3. **Локалізуємо гарячу функцію через `perf top`:**
   ```sh
   perf top -p 51200
   ```
   *Результат:* функція `run_cpu_bound` поглинає 99.2% усіх вибірок. Це класичний CPU-bound стан, який вимагає оптимізації алгоритму.

---

### Дослід 2: Діагностика шторму системних викликів (Kernel-bound)

У цьому режимі програма записує мільйони байтів у дескриптор `/dev/null` по одному байту за раз. Сама операція запису в `/dev/null` тривіальна, але накладні витрати на перетин межі привілеїв Ring 3 → Ring 0 поглинають майже всі такти процесора.

Запускаємо режим небуферизованих системних викликів:

```sh
./bench_cpp syscall &
# Нехай процес отримав PID 51280
```

1. **Перевіряємо `pidstat`:**
   ```sh
   pidstat -u 1 -p 51280
   ```
   *Аналіз виводу:*
   ```
   15:02:15   UID     PID    %usr %system  %guest   %wait    %CPU   CPU  Command
   15:02:16  1000   51280   11.20   88.80    0.00    0.00  100.00     0  bench_cpp
   ```
   Майже 90% часу процесора витрачається у просторі ядра (`%system`).

2. **Виконуємо агреговане трасування системних викликів через `strace -c`:**
   ```sh
   strace -c -p 51280
   # Через 3 секунди натискаємо Ctrl+C
   ```
   *Аналіз звіту:*
   ```
   % time     seconds  usecs/call     calls    errors syscall
   ------ ----------- ----------- --------- --------- ----------------
    99.12    2.825100           3    941700           write
     0.88    0.025000          25      1000           nanosleep
   ------ ----------- ----------- --------- --------- ----------------
   100.00    2.850100                942700           total
   ```
   Зафіксовано майже мільйон викликів `write()` за неповні три секунди. Кожен виклик триває всього 3 мікросекунди, але їхня колосальна кількість перевантажує ядро. Рішення: об'єднати дрібні операції у буфер розміром 64 КіБ.

---

### Дослід 3: Діагностика конфліктів блокувань (Futex Lock Contention)

У цьому режимі 8 паралельних потоків безперервно захоплюють і звільняють один спільний `pthread_mutex_t`. У бібліотеці `glibc` реалізація м'ютекса спершу намагається виконати атомарну інструкцію `atomic_compare_and_swap` у просторі користувача. Якщо замок зайнятий, потік змушений викликати системний виклик `futex(..., FUTEX_WAIT, ...)`.

Запускаємо режим конкуренції за блокування:

```sh
./bench_cpp lock &
# Нехай процес отримав PID 51340
```

1. **Знімаємо метрики перемикання контексту через `pidstat -w`:**
   ```sh
   pidstat -u -w 1 -p 51340
   ```
   *Аналіз виводу:*
   ```
   15:03:20   UID     PID    %usr %system   %CPU   cswch/s nvcswch/s  Command
   15:03:21  1000   51340   22.40   48.10  70.50  84210.00   1240.00  bench_cpp
   ```
   Добровільні перемикання контексту (`cswch/s`) підскочили до 84 тисяч за секунду! Потоки постійно блокуються, ядро переводить їх у чергу сну, а потім пробуджує при звільненні замка.

2. **Перевіряємо засинання потоків у ядрі через `/proc`:**
   ```sh
   cat /proc/51340/task/*/wchan
   ```
   *Результат:* більшість ниток постійно перебувають у стані `futex_wait_queue_me` або `futex_wait`.

3. **Локалізуємо системні виклики через `strace`:**
   ```sh
   strace -c -f -p 51340
   ```
   *Результат:* системний виклик `futex` займає понад 75% системного часу ядра. Рішення: зменшити гранулярність блокувань або використати роздільні черги для кожного потоку (Thread-local buffers).

---

### Дослід 4: Діагностика синхронного дискового зависання (I/O-bound)

У цьому режимі потік записує дані з прапорцем `O_SYNC` та викликає `fdatasync()`. Ядро блокує виконання процесу доти, доки контролер диска не завершить фізичний запис даних і не оновить журнал метаданих файлової системи.

Запускаємо режим синхронного скидання на диск:

```sh
./bench_cpp io &
# Нехай процес отримав PID 51410
```

1. **Перевіряємо стан процесу через `ps`:**
   ```sh
   ps -o pid,stat,wchan:24,cmd -p 51410
   ```
   *Аналіз виводу:*
   ```
     PID STAT WCHAN                    CMD
   51410 D    io_schedule              ./bench_cpp io
   ```
   Статус `D` (`TASK_UNINTERRUPTIBLE`) та канал очікування `io_schedule` свідчать про те, що процес заблокований на рівні дискового планувальника та чекає на переривання від накопичувача.

2. **Знімаємо статистику черги накопичувача через `iostat`:**
   ```sh
   iostat -xz 1
   ```
   *Аналіз виводу:*
   ```
   Device  r/s     w/s     rkB/s     wkB/s  r_await  w_await  aqu-sz  %util
   nvme0n1 0.00 2000.00     0.00   8000.00     0.00    18.40    3.60  99.20
   ```
   Показник `%util` досяг 99.2%, а час очікування `w_await` підскочив до 18.4 мс.

3. **Перевіряємо системний `vmstat 1`:**
   *Результат:* стовпчик `b` містить значення `1`, а `%wa` перевищує 45%.

---

## 3. Автоматизований зонд діагностики

Для швидкого збору діагностичного паспорта живого процесу використовують наступний скрипт на Bash (`probe.sh`), який агрегує інформацію з `/proc`, `pidstat` та `strace`:

```sh
#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Використання: $0 <PID> [тривалість_секунд]"
    exit 1
fi

PID="$1"
DURATION="${2:-3}"

if [[ ! -d "/proc/$PID" ]]; then
    echo "Помилка: процес з PID $PID не знайдено."
    exit 1
fi

CMD=$(cat "/proc/$PID/comm")
echo "=========================================================="
echo " ДІАГНОСТИЧНИЙ ЗОНД ПРОЦЕСУ: $CMD (PID: $PID)"
echo "=========================================================="

echo -e "\n[1] Розподіл CPU та перемикань контексту (pidstat):"
pidstat -u -w -r -p "$PID" 1 2

echo -e "\n[2] Поточний стан та функція очікування ядра (wchan):"
ps -o pid,tid,stat,wchan:24,comm -T -p "$PID"

echo -e "\n[3] Облік введення-виведення (/proc/$PID/io):"
cat "/proc/$PID/io"

echo -e "\n[4] Статистика затримки в черзі (/proc/$PID/schedstat):"
read -r CPU_TIME WAIT_TIME SLICES < "/proc/$PID/schedstat"
echo "  Час на CPU:       $((CPU_TIME / 1000000)) мс"
echo "  Очікування черги: $((WAIT_TIME / 1000000)) мс"
echo "  Квантів часу:     $SLICES"

echo -e "\n[5] Швидкий зріз системних викликів (strace $DURATION сек):"
strace -c -f -p "$PID" sleep "$DURATION" 2>&1 | tail -n 12

echo "=========================================================="
echo " Діагностику завершено."
```

Зонд дозволяє за кілька секунд отримати повну декомпозицію ресурсів і безпомилково віднести проблему до одного з кутів системного трикутника, виключаючи необхідність здогадок та сліпого тюнінгу.
