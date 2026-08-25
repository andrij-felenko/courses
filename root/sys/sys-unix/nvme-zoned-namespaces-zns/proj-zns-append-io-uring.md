# ⚙️ Паралельний дозапис у зони ZNS через io_uring та passthrough ioctl

Ця практична вставка демонструє розробку високонавантаженого програмного забезпечення для паралельного дозапису в зони NVMe ZNS з використанням низькорівневих системних викликів `ioctl` та асинхронного механізму `io_uring` passthrough у мовах C та C++.

## Завдання

У сучасних хмарних базах даних та сховищах об'єктів (наприклад, RocksDB з плагіном ZenFS чи Ceph) ключовою вимогою є максимальна утилізація пропускної здатності дискової підсистеми при паралельній обробці тисяч клієнтських запитів. При використанні традиційних блочних пристроїв це досягається паралельним записом з багатьох потоків CPU через окремі черги I/O.

Однак при переході на зоновані накопичувачі NVMe ZNS виникає бар'єр: зона вимагає суворо послідовного запису (Sequential Write Required, SWR). Якщо кілька потоків намагатимуться писати у одну зону через звичайний виклик `WRITE`, хост буде змушений використовувати глобальні синхронізаційні блокування (spinlock/mutex) для послідовного вибору LBA, що зруйнує паралелізм.

Метою цього проєкту є створення практичної утиліти, яка:
1. Приймає блоковий пристрій ZNS (наприклад, `/dev/nvme0n1`).
2. Виконує апаратне скидання зони (`Zone Reset`) для повернення у початковий стан `Empty`.
3. Запускає декілька паралельних робочих потоків, кожен з яких надсилає дані в одну й ту саму відкриту зону **без жодних блокувань (lock-free)** за допомогою атомарної команди `Zone Append`.
4. Виводитиме фактично виділені контролером SSD адреси LBA для кожного виділеного блоку.

## Ідея та архітектура рішення

При використанні звичайних викликів `write()` чи команди `NVME_NVM_CMD_WRITE` програма повинна самостійно вираховувати `LBA = Write Pointer` і серіалізувати виклики між потоками у користувацькому просторі.

Замість цього ми застосовуємо атомарний механізм `Zone Append` (opcode `0x7d`):

1. **Ініціалізація та скидання зони:** Головний потік відкриває файловий дескриптор пристрою з прапорцем `O_DIRECT`, щоб обійти системний кеш сторінок ядра Linux. Після цього надсилається виклик `ioctl(BLKRESETZONE)`, який переводить зональний вказівник запису (Write Pointer) на початковий сектор зони (ZSLBA = 0).
2. **Паралельне заповнення Submission Queues:** Робочі потоки не узгоджують між собою адреси LBA. Кожен потік заповнює свій буфер даних і надсилає апаратну команду `Zone Append`, вказуючи лише ZSLBA (початок зони).
3. **Атомарна серіалізація в контролері SSD:** Контролер NVMe SSD приймає команди з усіх черг паралельно, атомарно виділяє поточне значення Write Pointer під кожен запит, записує дані у флеш-пам'ять і повертає фактично виділений LBA у вихідному повідомивши CQE (Completion Queue Entry).

```
+-------------------------------------------------------------------+
|                        Головний потік (Main)                      |
|                Open /dev/nvme0n1 (O_DIRECT)                       |
|                ioctl(BLKRESETZONE) -> ZSLBA = 0                   |
+-------------------------------------------------------------------+
                                  │
          ┌───────────────────────┴───────────────────────┐
          ▼                                               ▼
+-------------------+                           +-------------------+
|  Робочий потік 0  |                           |  Робочий потік 1  |
|  Buffer A (4 KB)  |                           |  Buffer B (4 KB)  |
+-------------------+                           +-------------------+
          │                                               │
          │ Zone Append (ZSLBA=0)                         │ Zone Append (ZSLBA=0)
          ▼                                               ▼
+-------------------------------------------------------------------+
|                     Драйвер NVMe / blk-mq                         |
|                 Паралельні Submission Queues                      |
+-------------------------------------------------------------------+
                                  │
                                  ▼
+-------------------------------------------------------------------+
|                      Контролер SSD ZNS                            |
| 1. Атомарний інкремент WP: Write Pointer 0 -> LBA 0 (Потік 0)    |
| 2. Атомарний інкремент WP: Write Pointer 8 -> LBA 8 (Потік 1)    |
| 3. Повернення виділених LBA у повідомленнях CQE                    |
+-------------------------------------------------------------------+
```

Детальний аналіз функціонування цієї архітектури показує, що відсутність блокувань у користувацькому просторі усуває проблему контеншну (mutex contention) між ядрами CPU. Усі потоки можуть одночасно записувати командні словники у свої локальні Submission Queues підсистеми `blk-mq`. Контролер NVMe SSD бере на себе функцію атомарного арбітра: він обробляє команди I/O в порядку їх фізичного надходження у мікроконтролер диска та атомарно просуває Write Pointer зони.

Це дозволяє досягати максимальної швидкості запису, обмеженої лише пропускною здатністю шини PCIe та апаратною швидкістю запису сторінок NAND Flash.

## Особливості проектування безблокових структур даних

Оскільки при використанні команди `Zone Append` контролер SSD самостійно виділяє LBA за поточним значенням Write Pointer, порядок фактичного розміщення блоків у зоні залежить від того, яка саме команда надходить першою у мікроконтролер диска. Це означає, що програма користувацького простору повинна підтримувати індексні структури даних (наприклад, Sparse Index чи відображення ідентифікатора блоку на виділений LBA).

Кожен робочий потік отримує виділений LBA у полі `cmd.result` від виклику `ioctl` чи в полі `cqe->res64` при використанні `io_uring`. Після цього потік записує пару `(Block_ID -> Allocated_LBA)` у логічний індекс файлу. Оскільки записи виконуються у різні комірки індексу, потоки не конфліктують між собою під час оновлення метаданих.

У високомасштабованих системах (таких як плагін ZenFS для RocksDB) цей підхід дозволяє позбутися міжпроцесних locks на рівні виділення LBA. База даних просто виділяє незмінну область у пам'яті під SSTable-файл і розпаралелює його запис між багатьма робочими потоками ядра.

Кожен потік заповнює свій фрагмент пам'яті і надсилає його в зоноване сховище. Після завершення всіх викликів `Zone Append` головний потік записує підсумковий масив вказувальників у заголовок файлу або таблицю метаданих.

## Фрагментація та вирівнювання блоків (Block Padding & Alignment)

У практичних серверних базах даних розмір структури даних не завжди є кратним фізичному сектору (512 або 4096 байт). При використанні ZNS дозаписи повинні суворо вирівнюватися на розмір сектора носія.

Для обходу цієї проблеми застосовується вирівнювання з падінгом (Block Padding):
- Якщо корисний розмір запису становить, наприклад, 3500 байт, програма додає нульові байти (zero-padding) до межі 4096 байт перед надсиланням команди `Zone Append`.
- Заголовок кожного блоку містить точне значення корисної довжини (Payload Length), що дозволяє читачеві ігнорувати заповнювальні байти при зчитуванні.
- Для передачі великих неперервних файлів у декількох зонах використовується виділення слотів (Slab Allocation), де розмір кожної порції дозапису вибирається рівним точній кратній величині ZASL (наприклад, 64 КБ).

## Реалізація коду

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>
#include <linux/blkzoned.h>
#include <pthread.h>
#include <errno.h>

#define SECTOR_SIZE 512
#define NUM_THREADS 4
#define WRITES_PER_THREAD 8
#define BLOCK_SIZE 4096

typedef struct {
    int fd;
    uint64_t zslba;
    int thread_id;
} thread_arg_t;

/* Виконання апаратної команди Zone Append через ioctl */
static uint64_t zns_zone_append(int fd, uint32_t nsid, uint64_t zslba, void *buffer, size_t len) {
    uint32_t nlb = len / SECTOR_SIZE;
    struct nvme_passthru_cmd cmd;
    memset(&cmd, 0, sizeof(cmd));

    cmd.opcode      = 0x7d; /* nvme_zns_cmd_append */
    cmd.nsid        = nsid;
    cmd.addr        = (uint64_t)(uintptr_t)buffer;
    cmd.data_len    = len;
    cmd.cdw10       = (uint32_t)(zslba & 0xFFFFFFFF);
    cmd.cdw11       = (uint32_t)(zslba >> 32);
    cmd.cdw12       = nlb - 1; /* 0-based NLB */
    cmd.timeout_ms  = 2000;

    if (ioctl(fd, NVME_IOCTL_IO_CMD, &cmd) < 0) {
        perror("ioctl(NVME_IOCTL_IO_CMD - Zone Append) failed");
        return (uint64_t)-1;
    }

    /* cmd.result містить виділений LBA у 64-бітному результаті CQE */
    return cmd.result;
}

/* Робоча функція паралельного потоку (без локів!) */
static void *worker_thread(void *arg) {
    thread_arg_t *targ = (thread_arg_t *)arg;
    void *buffer = NULL;

    /* Потрібне вирівнювання пам'яті для Direct I/O */
    if (posix_memalign(&buffer, 4096, BLOCK_SIZE) != 0) {
        perror("posix_memalign failed");
        pthread_exit(NULL);
    }

    memset(buffer, 0xAA + targ->thread_id, BLOCK_SIZE);

    for (int i = 0; i < WRITES_PER_THREAD; i++) {
        uint64_t allocated_lba = zns_zone_append(targ->fd, 1, targ->zslba, buffer, BLOCK_SIZE);
        if (allocated_lba == (uint64_t)-1) {
            fprintf(stderr, "[Thread %d] Append failed at iteration %d\n", targ->thread_id, i);
            break;
        }
        printf("[Thread %d] Appended block %d -> Allocated LBA: 0x%lx\n",
               targ->thread_id, i, allocated_lba);
    }

    free(buffer);
    pthread_exit(NULL);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s /dev/nvmeXnY\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *devpath = argv[1];
    int fd = open(devpath, O_RDWR | O_DIRECT);
    if (fd < 0) {
        perror("Failed to open device");
        return EXIT_FAILURE;
    }

    /* 1. Скидання першої зони (ZSLBA = 0) */
    struct blk_zone_range range = {
        .sector = 0,
        .nr_sectors = 262144 /* 128 MB у 512B секторах */
    };

    printf("Resetting zone at sector 0...\n");
    if (ioctl(fd, BLKRESETZONE, &range) < 0) {
        perror("ioctl(BLKRESETZONE) failed");
        close(fd);
        return EXIT_FAILURE;
    }
    printf("Zone reset successful.\n");

    /* 2. Запуск паралельних потоків дозапису */
    pthread_t threads[NUM_THREADS];
    thread_arg_t args[NUM_THREADS];

    for (int i = 0; i < NUM_THREADS; i++) {
        args[i].fd = fd;
        args[i].zslba = 0; /* Вказуємо початковий LBA зони */
        args[i].thread_id = i;
        if (pthread_create(&threads[i], NULL, worker_thread, &args[i]) != 0) {
            perror("pthread_create failed");
        }
    }

    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    close(fd);
    printf("All parallel lockless appends completed successfully.\n");
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <thread>
#include <span>
#include <memory>
#include <expected>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>
#include <linux/blkzoned.h>

namespace zns {

constexpr std::size_t kSectorSize = 512;
constexpr std::size_t kBlockSize = 4096;

// RAII обгортка для файлового дескриптора пристрою
class DeviceHandle {
public:
    explicit DeviceHandle(const char* path) {
        fd_ = ::open(path, O_RDWR | O_DIRECT);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to open ZNS device");
        }
    }

    ~DeviceHandle() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    DeviceHandle(const DeviceHandle&) = delete;
    DeviceHandle& operator=(const DeviceHandle&) = delete;
    DeviceHandle(DeviceHandle&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    DeviceHandle& operator=(DeviceHandle&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }

private:
    int fd_{-1};
};

// Вирівняна пам'ять для Direct I/O (RAII)
class AlignedBuffer {
public:
    explicit AlignedBuffer(std::size_t size, std::size_t alignment = 4096) : size_(size) {
        void* ptr = nullptr;
        if (::posix_memalign(&ptr, alignment, size) != 0) {
            throw std::bad_alloc();
        }
        data_.reset(static_cast<std::byte*>(ptr));
    }

    [[nodiscard]] std::span<std::byte> span() noexcept { return {data_.get(), size_}; }
    [[nodiscard]] std::span<const std::byte> span() const noexcept { return {data_.get(), size_}; }
    [[nodiscard]] void* data() noexcept { return data_.get(); }

private:
    struct FreeDeleter {
        void operator()(void* p) const { std::free(p); }
    };
    std::unique_ptr<std::byte[], FreeDeleter> data_;
    std::size_t size_;
};

// Виконання Zone Reset
std::expected<void, std::error_code> reset_zone(const DeviceHandle& dev, std::uint64_t start_sector, std::uint64_t nr_sectors) {
    struct blk_zone_range range{
        .sector = start_sector,
        .nr_sectors = nr_sectors
    };
    if (::ioctl(dev.get(), BLKRESETZONE, &range) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

// Атомарна команда Zone Append
std::expected<std::uint64_t, std::error_code> zone_append(
    const DeviceHandle& dev, 
    std::uint32_t nsid, 
    std::uint64_t zslba, 
    std::span<const std::byte> buffer
) {
    uint32_t nlb = static_cast<uint32_t>(buffer.size() / kSectorSize);
    struct nvme_passthru_cmd cmd{};

    cmd.opcode      = 0x7d; // nvme_zns_cmd_append
    cmd.nsid        = nsid;
    cmd.addr        = reinterpret_cast<std::uint64_t>(buffer.data());
    cmd.data_len    = static_cast<std::uint32_t>(buffer.size());
    cmd.cdw10       = static_cast<std::uint32_t>(zslba & 0xFFFFFFFF);
    cmd.cdw11       = static_cast<std::uint32_t>(zslba >> 32);
    cmd.cdw12       = nlb - 1;
    cmd.timeout_ms  = 2000;

    if (::ioctl(dev.get(), NVME_IOCTL_IO_CMD, &cmd) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return cmd.result; // Выділений LBA з CQE
}

} // namespace zns

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " /dev/nvmeXnY\n";
        return EXIT_FAILURE;
    }

    try {
        zns::DeviceHandle dev(argv[1]);

        std::cout << "Resetting zone at sector 0...\n";
        if (auto res = zns::reset_zone(dev, 0, 262144); !res) {
            std::cerr << "Zone reset failed: " << res.error().message() << "\n";
            return EXIT_FAILURE;
        }
        std::cout << "Zone reset successful.\n";

        constexpr int kNumThreads = 4;
        constexpr int kWritesPerThread = 8;
        std::vector<std::thread> workers;
        workers.reserve(kNumThreads);

        for (int tid = 0; tid < kNumThreads; ++tid) {
            workers.emplace_back([&dev, tid]() {
                zns::AlignedBuffer buf(zns::kBlockSize);
                std::memset(buf.data(), 0xBB + tid, zns::kBlockSize);

                for (int i = 0; i < kWritesPerThread; ++i) {
                    auto res = zns::zone_append(dev, 1, 0, buf.span());
                    if (!res) {
                        std::cerr << "[Thread " << tid << "] Append failed: " << res.error().message() << "\n";
                        break;
                    }
                    std::cout << "[Thread " << tid << "] Appended block " << i 
                              << " -> Allocated LBA: 0x" << std::hex << *res << std::dec << "\n";
                }
            });
        }

        for (auto& t : workers) {
            t.join();
        }

        std::cout << "All C++ lockless appends completed successfully.\n";

    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

## Покроковий аналіз виконання коду

1. **Відкриття файлового дескриптора з `O_DIRECT`:**
   Команди `passthrough ioctl` вимагають прямого DMA-передавання між буфером у пам'яті користувацького простору та картою NVMe PCIe. Відкриття файлу з прапорцем `O_DIRECT` інформує ядро Linux про те, що запити не повинні копіюватися у системний кеш сторінок (Page Cache). Це запевняє, що виклик не зазнає подвійного буферизаційного копіювання і вирушить напряму в контролер диска.
2. **Апаратне скидання зони (`BLKRESETZONE`):**
   Перед запуском потоків утиліта надсилає команду `BLKRESETZONE`, яка переводить першу зону (починаючи з сектора 0) у стан `Empty`. Це скидає внутрішній вказівник запису (Write Pointer) на значення 0 та запевняє, що початковий стан зони готовий приймати нові дозаписи.
3. **Паралельне створення потоків (`pthread_create` / `std::thread`):**
   Кожен потік виділяє власну ділянку пам'яті `AlignedBuffer`, вирівняну на 4096 байт через `posix_memalign()`. Це гарантує, що фізична адреса бувера збігається з межею сторінки пам'яті, унеможливлюючи помилки складання сторінок ядра (DMA boundary faults).
4. **Надсилання та обробка `Zone Append`:**
   Кожен потік формує структуру `struct nvme_passthru_cmd`, де заповнює opcode `0x7d` (Zone Append), вказує `cdw10` та `cdw11` (ZSLBA = 0) та обчислює `cdw12 = nlb - 1`. Після успішного завершення `ioctl` потік витягує виділену адресу LBA з поля `cmd.result`.

Конструкція `std::span<const std::byte>` у мові C++ забезпечує безпечну передачу незмінних буферів без ризику втрати розміру чи неявного перетворення типів вказавників (`void*`), що є стандартом сучасного високоефективного C++ коду.

## Аналіз асинхронного `io_uring_cmd` passthrough

У наведеному вище прикладі використано синхронний системний виклик `ioctl(NVME_IOCTL_IO_CMD)`. Для кожного запиту запису потік здійснює перехід у режим ядра (context switch). При швидкостях у мільйони IOPS цей перехід перетворюється на головний деструктивний чинник продуктивності CPU.

У високпродуктивних системах (наприклад, у фреймворках SPDK та io_uring) виклики `ioctl` замінюються на **`io_uring` passthrough** (код операції `IORING_OP_URIS_CMD` з описувачем `NVME_URING_CMD_IO`).

При використанні `io_uring`:
- Програма підготує структуру `struct io_uring_sqe` у кільцевому буфері користувацького простору.
- Поле `sqe->cmd_op` встановлюється в `NVME_URING_CMD_IO`.
- Потоки надсилають сотні команд `Zone Append` одним системним викликом `io_uring_enter()`.
- Результат (виділений LBA) зчитується з буфера завершення `struct io_uring_cqe->res64` без жодного синхронного блокування потоків.

Використання `io_uring` passthrough зменшує накладні витрати на системні виклики майже до нуля, дозволяючи одному ядру CPU обробляти понад 1.5 мільйона операцій `Zone Append` на секунду.

Для налаштування асинхронного пастру програма створює екземпляр кільця через `io_uring_queue_init()`, а потім заповнює апаратні поля NVMe команди прямо у буфері SQE без виконання переходу в режим ядра на кожну операцію.

## Порівняння продуктивності: Synchronous `ioctl` vs Asynchronous `io_uring`

При роботі із зонованими накопичувачами вибір механізму подання команд безпосередньо впливає на затримку (latency) та кількість операцій на секунду (IOPS).

| Показник | Synchronous `ioctl` | Asynchronous `io_uring_cmd` |
| :--- | :--- | :--- |
| Переключення контексту (Context Switch) | Високе (на кожну команду I/O) | Амортизоване (один виклик на батч) |
| Витрати CPU на 100k IOPS | ~35–45% одного ядра CPU | ~4–8% одного ядра CPU |
| Підтримка Polling Mode | Відсутня (переривання) | Підтримується (`IORING_SETUP_SQPOLL`) |
| Складність програмування | Низька (прості виклики C API) | Середня (управління кільцевими буферами) |

Для серверних баз даних реального часу (RocksDB / ZenFS) застосування `io_uring` passthrough є єдино можливим шляхом досягнення межі продуктивності фізичної шини PCIe Gen4/Gen5.

## Бар'єри пам'яті та апаратна узгодженість (Memory Barriers & Coherency)

При передачі буферів користувацького простору у контролер NVMe через прямий доступ до пам'яті (DMA), процесорний кеш (L1/L2/L3) мусить бути узгоджений із фізичною оперативною пам'яттю (DRAM). Підсистема шини PCIe використовує механізм Bus Snooping для контролю кеш-ліній.

У системному програмуванні на C та C++ при заповненні вирівняних буферів перед надсиланням `Zone Append` слід переконатися, що всі операції запису в пам'ять завершилися до того, як адреса буфера передається в регістри DMA контролера NVMe. У C++20 для цього використовується апаратний бар'єр пам'яті `std::atomic_thread_fence(std::memory_order_release)`, або виклики `sfence` для x86-64 архітектури, щоб запобігти спекулятивному переупорядкуванню інструкцій процесором.

## Оптимізація прив'язки потоків (NUMA & Core Pinning)

Для забезпечення максимальної швидкості передачі даних команд `Zone Append` у багатьохпроцесорних серверах критичноважливо зважати на архітектуру NUMA (Non-Uniform Memory Access). Кожен контролер NVMe PCIe підключений до конкретного PCIe-кореня (PCIe Root Complex) і відповідного сокета CPU.

При розробці високоефективного коду робочі потоки прив'язуються до ядер CPU, які знаходяться на тому самому NUMA-вузлі, що й NVMe контролер, за допомогою виклику `pthread_setaffinity_np()`. Буфери пам'яті виділяються за допомогою функцій `numa_alloc_onnode()`. Це запобігає передачі I/O даних через міжпроцесорний шинний міст (AMD Infinity Fabric чи Intel UPI), що зменшує затримку дозапису на 15–25%.

## Обробка переривань та корректне завершення (Graceful Shutdown)

При аварійному завершенні застосунку або отриманні сигналів переривання (`SIGINT`, `SIGTERM`) незавершені операції `Zone Append` можуть залишити зони у стані `Explicit Open`.

Для забезпечення стійкості утиліта повинна реєструвати обробники сигналів:
- При отриманні `SIGINT` обробник прапором зупиняє формування нових I/O викликів.
- Робочі потоки дочікуються завершення поточних команд в Submission Queue.
- Головний потік надсилає команду `Zone Management Send` з кодом дій `Zone Close` (для збереження позиції WP) чи `Zone Finish` (для фіксації заповнення зони).
- Файловий дескриптор закривається, звільняючи ресурси ядра.

## Часті пастки та крайові випадки (Traps)

1. **Вирівнювання пам'яті для Direct I/O (`O_DIRECT`):**
   При відкритті файлу з прапорцем `O_DIRECT` ядро Linux вимагає, щоб адрес буфера даних у пам'яті був вирівняний на межу фізичного сектора або сторінки (4096 байт). Використання звичайного `malloc()` або локального масиву на стеку призведе до помилки `EFAULT` або `EINVAL` під час виконання `ioctl`. У мові C використовується `posix_memalign()`, а в C++ — вирівняний алокатор або `std::aligned_alloc()`.

2. **Перевищення ліміту ZASL (Zone Append Size Limit):**
   Специфікація ZNS обмежує максимальний розмір одного запиту `Zone Append`. Якщо спробувати надіслати буфер 1 МБ за одну команду, накопичувач відхилить її з апаратною помилкою контролера. Перед запуском масового запису програма повинна прочитати значення `/sys/block/nvmeXnY/queue/zone_append_max_bytes` і розбити великі I/O запити на шматки, що не перевищують ZASL.

3. **Неправильний розрахунок NLB (Number of Logical Blocks):**
   У специфікації NVMe значення в полях команд (наприклад, `cdw12` для `Zone Append`) є **0-based**. Це означає, що для запису 1 блоку (512 байт) необхідно передавати `cdw12 = 0`. Спроба передати `cdw12 = 1` призведе до того, що пристрій спробує прочитати з буфера 1024 байти, що викличе вихід за межі пам'яті.

4. **Переповнення відкритих зон (MOR Exceeded):**
   Якщо програма надсилає `Zone Append` у порожню зону, контролер ZNS автоматично переводить цю зону у стан `Implicit Open`. Якщо кількість таких неявно відкритих зон перевищить апаратне значення `max_open_zones`, накопичувач поверне помилку `0x028f` (Zone Resources Exceeded). Щоб уникнути цього, програма повинна явно завершувати зони (`Zone Finish`) при досягненні кінця їх ємності.

5. **Недостатній час очікування (Timeout handling):**
   Операція `Zone Reset` або великі батчі `Zone Append` можуть замагати більше часу при високому навантаженні на носій. Значення `timeout_ms` у структурі `struct nvme_passthru_cmd` слід встановлювати не менше ніж 2000 мс, щоб уникнути передчасного переривання команди драйвером ядра.

6. **Поведінка при досягненні Zone Capacity:**
   Коли Write Pointer наближається до межі `Zone Capacity`, черговий `Zone Append` може не вміститися у залишок вільного місця. У цьому випадку пристрій відхилить команду з кодом помилки `Zone Boundary Error` (`0x0289`). Програма має відстежувати залишок вільного місця або обробляти цей код статусу, переходячи до дозапису у наступну вільну зону.
