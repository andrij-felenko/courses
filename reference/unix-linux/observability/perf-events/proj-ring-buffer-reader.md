# ⚙️ Зчитування кільцевого буфера perf_event_open

Цей практичний приклад показує, як відкрити подію саплінгу апаратних циклів процесора через системний виклик `perf_event_open()`, налаштувати кільцевий буфер розділюваної пам'яті через `mmap()` та асинхронно зчитувати вибірки користувацьким кодом на мовах C та C++.

## 1. Архітектурна задача та механіка розділюваної пам'яті

Коли вибіркове профілювання запускається на високій частоті (наприклад, 1000 вибірок на секунду на кожне ядро), ядро Linux не може робити контекстні перемикання або викликати системний виклик `read()` на кожен NMI-сигнал. Здійснення тисяч системних викликів на секунду призвело б до падіння продуктивності самої системи та спотворення результатів вимірювання.

Для розв'язання цієї проблеми в користувацькому просторі виділяється розділювана пам'яті через виклик `mmap()` безпосередньо на дескрипторі події `fd`. Розмір цієї пам'яті обов'язково повинен дорівнювати $1 + 2^N$ системним сторінкам пам'яті (де $1$ сторінка — це заголовок управління, а $2^N$ сторінок — кільцевий масив даних):

1. **Сторінка управління (Page 0)**: Структура `struct perf_event_mmap_page`, розташована за адресою початку відображення. У ній ядро оновлює курсор `data_head`, а користувацька програма оновлює курсор `data_tail`.
2. **Кільцевий буфер даних ($2^N$ сторінок)**: Пам'ять, яка починається віддразу за першою сторінкою (зсув `data_offset = 4096`). У цю зону ядро по колу записує двійкові блоки подій `PERF_RECORD_SAMPLE`.

### Бар'єри пам'яті та синхронізація без локів

Оскільки ядро записує нові вибірки в контексті переривань NMI (Non-Maskable Interrupt), застосування м'ютексів або звичайних локів (spinlock) у середовищі ядра неможливе. Синхронізація між ядром та користувацькою програмою базується на двох 64-бітних курсорах:

- `data_head`: Вказує на абсолютне зміщення в байтах від початку буфера даних, куди ядро запише наступний запис. Це значення монотонно зростає і ніколи не скидається у нуль при оговтуванні кільцевого масиву.
- `data_tail`: Вказує на абсолютне зміщення у байтах, до якого користувацький процес вже прочитав і вилучив вибірки.

Оскільки процесор може перевпорядковувати операції читання та запису в пам'яті (out-of-order execution), при зчитуванні `data_head` обов'язково застосовується бар'єр пам'яті із семантикою `acquire` (`atomic_load_explicit(..., memory_order_acquire)` у C/C++). Це гарантує, що інструкції читання тіла вибірки не будуть виконані процесором до того, як прочитано оновлене значення `data_head`.

Після завершення розбору вибірок користувацька програма записує оновлене значення `data_tail` із семантикою `release` (`atomic_store_explicit(..., memory_order_release)`), повідомляючи ядру про звільнення простору для нових вибірок.

---

## 2. Покроковий розбір конфігурації системного виклику

Перед проведенням відображення пам'яті `mmap()` програма повинна правильно заповнити структуру `struct perf_event_attr`:

1. **Встановлення типу події (`type = PERF_TYPE_HARDWARE`)**: Вказує ядру, що моніторинг здійснюватиметься за допомогою апаратного лічильника PMU.
2. **Конфігурація події (`config = PERF_COUNT_HW_CPU_CYCLES`)**: Обирає вимірювання загальної кількості тактових імпульсів CPU.
3. **Період вибірки (`sample_period = 100000`)**: Задає генерацію переривання NMI кожні 100 000 тактових імпульсів процесора.
4. **Маска полів вибірки (`sample_type`)**:
   - `PERF_SAMPLE_IP`: Додає віртуальну адресу інструкції `RIP`.
   - `PERF_SAMPLE_TID`: Додає ідентифікатор процесу PID та потоку TID.
   - `PERF_SAMPLE_TIME`: Додає наносекундний часовий штамп ядра.
5. **Фільтри середовища (`exclude_kernel = 1`, `exclude_hv = 1`)**: Обмежує моніторинг виключно кодом користувацького простору (ring 3), ігноруючи інструкції ядра та гіпервізора.

---

## 3. Реалізація у коді (C та C++)

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <stdatomic.h>
#include <linux/perf_event.h>

static long perf_event_open(struct perf_event_attr *hw_event, pid_t pid,
                             int cpu, int group_fd, unsigned long flags) {
    return syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);
}

int main(void) {
    struct perf_event_attr pe;
    memset(&pe, 0, sizeof(struct perf_event_attr));
    pe.type = PERF_TYPE_HARDWARE;
    pe.size = sizeof(struct perf_event_attr);
    pe.config = PERF_COUNT_HW_CPU_CYCLES;
    pe.sample_period = 100000; // Самплінг кожні 100 000 циклів CPU
    pe.sample_type = PERF_SAMPLE_IP | PERF_SAMPLE_TID | PERF_SAMPLE_TIME;
    pe.disabled = 1;
    pe.exclude_kernel = 1;
    pe.exclude_hv = 1;

    int fd = (int)perf_event_open(&pe, 0, -1, -1, 0);
    if (fd == -1) {
        perror("perf_event_open failed");
        return EXIT_FAILURE;
    }

    // Виділяємо 1 сторінку управління + 8 сторінок даних (1 + 8 * 4096 байтів)
    const size_t page_size = (size_t)sysconf(_SC_PAGESIZE);
    const size_t data_pages = 8;
    const size_t mmap_size = page_size * (1 + data_pages);

    void *base = mmap(NULL, mmap_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (base == MAP_FAILED) {
        perror("mmap failed");
        close(fd);
        return EXIT_FAILURE;
    }

    struct perf_event_mmap_page *hdr = (struct perf_event_mmap_page *)base;
    char *data_boundary = (char *)base + page_size;
    size_t data_size = page_size * data_pages;

    // Вмикаємо лічильник
    ioctl(fd, PERF_EVENT_IOC_RESET, 0);
    ioctl(fd, PERF_EVENT_IOC_ENABLE, 0);

    // Імітація обчислювального навантаження
    volatile unsigned long long dummy = 0;
    for (unsigned long long i = 0; i < 50000000ULL; ++i) {
        dummy += i;
    }

    // Вимикаємо моніторинг
    ioctl(fd, PERF_EVENT_IOC_DISABLE, 0);

    // Зчитуємо записи з кільцевого буфера
    uint64_t head = atomic_load_explicit((_Atomic uint64_t *)&hdr->data_head, memory_order_acquire);
    uint64_t tail = hdr->data_tail;

    printf("Зчитано data_head = %lu, data_tail = %lu\n", head, tail);

    size_t samples_count = 0;
    while (tail < head) {
        uint64_t offset = tail % data_size;
        struct perf_event_header *phead = (struct perf_event_header *)(data_boundary + offset);

        if (phead->size == 0) {
            break; // Захист від пошкоджених даних
        }

        if (phead->type == PERF_RECORD_SAMPLE) {
            struct {
                uint64_t ip;
                uint32_t pid, tid;
                uint64_t time;
            } *sample = (void *)((char *)phead + sizeof(struct perf_event_header));

            samples_count++;
            if (samples_count <= 5) {
                printf("  [Вибірка #%zu] RIP = 0x%lx, PID = %u, TID = %u, Time = %lu ns\n",
                       samples_count, sample->ip, sample->pid, sample->tid, sample->time);
            }
        }

        tail += phead->size;
    }

    // Оновлюємо курсор tail для ядра
    atomic_store_explicit((_Atomic uint64_t *)&hdr->data_tail, tail, memory_order_release);
    printf("Усього вибірок оброблено: %zu\n", samples_count);

    munmap(base, mmap_size);
    close(fd);
    return EXIT_SUCCESS;
}
```

```cpp
#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <expected>
#include <system_error>
#include <atomic>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <linux/perf_event.h>

namespace sys {

class ScopedFd {
    int fd_{-1};
public:
    explicit ScopedFd(int fd) : fd_(fd) {}
    ~ScopedFd() { if (fd_ != -1) ::close(fd_); }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ != -1; }
};

struct SampleRecord {
    std::uint64_t ip;
    std::uint32_t pid;
    std::uint32_t tid;
    std::uint64_t time;
};

class PerfRingBuffer {
    ScopedFd fd_;
    void* mmap_base_{MAP_FAILED};
    std::size_t mmap_size_{0};
    std::size_t page_size_{0};
    std::size_t data_size_{0};

    static long perf_event_open_sys(struct perf_event_attr* attr, pid_t pid,
                                   int cpu, int group_fd, unsigned long flags) {
        return ::syscall(__NR_perf_event_open, attr, pid, cpu, group_fd, flags);
    }

public:
    static std::expected<PerfRingBuffer, std::error_code> create(std::uint64_t sample_period, std::size_t data_pages = 8) {
        struct perf_event_attr pe{};
        pe.type = PERF_TYPE_HARDWARE;
        pe.size = sizeof(struct perf_event_attr);
        pe.config = PERF_COUNT_HW_CPU_CYCLES;
        pe.sample_period = sample_period;
        pe.sample_type = PERF_SAMPLE_IP | PERF_SAMPLE_TID | PERF_SAMPLE_TIME;
        pe.disabled = 1;
        pe.exclude_kernel = 1;
        pe.exclude_hv = 1;

        int raw_fd = static_cast<int>(perf_event_open_sys(&pe, 0, -1, -1, 0));
        if (raw_fd == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        ScopedFd fd(raw_fd);
        std::size_t psize = static_cast<std::size_t>(::sysconf(_SC_PAGESIZE));
        std::size_t total_size = psize * (1 + data_pages);

        void* base = ::mmap(nullptr, total_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd.get(), 0);
        if (base == MAP_FAILED) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return PerfRingBuffer(std::move(fd), base, total_size, psize, psize * data_pages);
    }

    PerfRingBuffer(ScopedFd fd, void* base, std::size_t total_size, std::size_t psize, std::size_t dsize)
        : fd_(std::move(fd)), mmap_base_(base), mmap_size_(total_size), page_size_(psize), data_size_(dsize) {}

    ~PerfRingBuffer() {
        if (mmap_base_ != MAP_FAILED) {
            ::munmap(mmap_base_, mmap_size_);
        }
    }

    PerfRingBuffer(const PerfRingBuffer&) = delete;
    PerfRingBuffer& operator=(const PerfRingBuffer&) = delete;
    PerfRingBuffer(PerfRingBuffer&&) noexcept = default;

    void start() {
        ::ioctl(fd_.get(), PERF_EVENT_IOC_RESET, 0);
        ::ioctl(fd_.get(), PERF_EVENT_IOC_ENABLE, 0);
    }

    void stop() {
        ::ioctl(fd_.get(), PERF_EVENT_IOC_DISABLE, 0);
    }

    [[nodiscard]] std::vector<SampleRecord> consume_samples() {
        std::vector<SampleRecord> records;
        auto* hdr = static_cast<struct perf_event_mmap_page*>(mmap_base_);
        auto* data_boundary = static_cast<const char*>(mmap_base_) + page_size_;

        std::uint64_t head = std::atomic_load_explicit(
            reinterpret_cast<const std::atomic<std::uint64_t>*>(&hdr->data_head),
            std::memory_order_acquire
        );
        std::uint64_t tail = hdr->data_tail;

        while (tail < head) {
            std::uint64_t offset = tail % data_size_;
            auto* phead = reinterpret_cast<const struct perf_event_header*>(data_boundary + offset);

            if (phead->size == 0) break;

            if (phead->type == PERF_RECORD_SAMPLE) {
                struct RawSample {
                    std::uint64_t ip;
                    std::uint32_t pid;
                    std::uint32_t tid;
                    std::uint64_t time;
                };
                const auto* raw = reinterpret_cast<const RawSample*>(
                    reinterpret_cast<const char*>(phead) + sizeof(struct perf_event_header)
                );
                records.push_back(SampleRecord{raw->ip, raw->pid, raw->tid, raw->time});
            }
            tail += phead->size;
        }

        std::atomic_store_explicit(
            reinterpret_cast<std::atomic<std::uint64_t>*>(&hdr->data_tail),
            tail, std::memory_order_release
        );
        return records;
    }
};

} // namespace sys

int main() {
    auto profiler_res = sys::PerfRingBuffer::create(100'000);
    if (!profiler_res) {
        std::cerr << "Помилка ініціалізації perf: " << profiler_res.error().message() << '\n';
        return 1;
    }

    auto profiler = std::move(*profiler_res);
    profiler.start();

    volatile std::uint64_t dummy{0};
    for (std::uint64_t i = 0; i < 50'000'000ULL; ++i) {
        dummy += i;
    }

    profiler.stop();

    auto samples = profiler.consume_samples();
    std::cout << "Отримано вибірок у C++: " << samples.size() << '\n';

    for (std::size_t i = 0; i < std::min<std::size_t>(5, samples.size()); ++i) {
        const auto& s = samples[i];
        std::cout << "  [Вибірка #" << (i + 1) << "] IP = 0x" << std::hex << s.ip
                  << std::dec << ", PID = " << s.pid << ", Time = " << s.time << " ns\n";
    }

    return 0;
}
```
:::

---

## 4. Детальний аналіз та крайові випадки реалізації

Під час виділення та зчитування кільцевого буфера perf у реальних висувних системах слід враховувати такі важливі інженерні аспекти:

### 4.1. Вимога до ступеня двійки для кількості сторінок даних

Кількість сторінок даних у виклику `mmap()` обов'язково повинна дорівнювати ступеню двійки ($2^N$, тобто 1, 2, 4, 8, 16, 32... сторінок). Це необхідно тому, що операція обчислення почного зміщення у масиві здійснюється через остачу від ділення `tail % data_size`. 

Якщо розробник спробує виділити 3 або 5 сторінок, виклик `mmap()` поверне помилку `EINVAL`.

### 4.2. Обробка подій переповнення та переповнення кільцевого буфера

Якщо користувацький процес зчитує дані з буфера повільніше, ніж ядро генерує NMI-вибірки, виникає ситуація переповнення буфера. У цьому випадку ядро не переписує непрочитані вибірки, а відкидає нові події та записує спеціальну структуру `PERF_RECORD_LOST`:

:::tabs
```c
struct perf_record_lost {
    struct perf_event_header header;
    uint64_t id;    /* Ідентифікатор події */
    uint64_t lost;  /* Кількість пропущених вибірок */
};
```
```cpp
struct PerfRecordLost {
    struct perf_event_header header;
    std::uint64_t id;    // Ідентифікатор події
    std::uint64_t lost;  // Кількість пропущених вибірок
};
```
:::

При розборі циклу `while (tail < head)` програма повинна перевіряти `phead->type == PERF_RECORD_LOST` і коригувати лічильник статистичної похибки.

### 4.3. Обробка огортання (Wrap-around) записів у кільцевому буфері

Оскільки елементи `struct perf_event_header` мають змінну довжину `size` (наприклад, 32, 48 або 128 байтів), запис події може потрапити на саму межу буфера даних (`offset + size > data_size`).

Ядро Linux гарантує, що сторінки пам'яті кільцевого буфера прозоро відображаються у віртуальний простір двічі поспіль (за допомогою зацикленого `mmap` через `remap_file_pages` або суміжні сторінки VMA). Це дозволяє користувацькому коду зчитувати зміщені структури за прямими вказівниками `phead` без необхідності сичного склеювання байтів між кінцем та початком буфера.

### 4.4. Порівняння підходів C та C++

1. **Керування ресурсами**: Реалізація мовою C вимагає ручного відстеження викликів `close(fd)` та `munmap()` при кожному виході з функції або обробці помилок. Реалізація C++ використовує ідіому RAII (`ScopedFd` та клас `PerfRingBuffer`), гарантуючи звільнення файлового дескриптора й пам'яті при виході з области видимості.
2. **Обробка помилок**: У C повертається `-1` з оновленням глобальної змінної `errno`. У C++20 застосовується сучасний контейнер `std::expected<PerfRingBuffer, std::error_code>`, що явно вимагає перевірки результату створення об'єкта без використання винятків.
3. **Безпека типів**: Користувацький C++ клас приховує сирі вказівники на `void*` та структурні операції з арифметикою вказівників всередині приватого методу `consume_samples()`, повертаючи типізований вектор `std::vector<SampleRecord>`.
