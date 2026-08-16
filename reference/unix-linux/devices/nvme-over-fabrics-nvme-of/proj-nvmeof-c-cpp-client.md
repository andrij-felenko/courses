# ⚙️ Низькорівневе обслуговування NVMe-oF у просторі користувача: libnvme та ioctl

Для практичного управління мережевими блочними пристроями NVMe over Fabrics у системному програмуванні для Linux використовуються два рівні взаємодії: високорівнева бібліотека `libnvme` (яка лежить в основі стандартного системного інструменту `nvme-cli`) або пряме надсилання системних запитів `ioctl` та запис конфігураційних рядків у символьний пристрій керування ядра `/dev/nvme-fabrics`.

Програмне підключення до віддаленого дискового масиву вимагає послідовного виконання чотирьох системних завдань:
1. Відкриття контрольного символьного вузла керування `/dev/nvme-fabrics`.
2. Формування та запис спеціального тексту конфігурації підключення (опції `nqn`, `transport`, `traddr`, `trsvcid`) для створення віртуального адаптера.
3. Виявлення створеного ядром операційної системи блочного вузла у системі (наприклад, `/dev/nvme0n1`).
4. Виконання прямого читання чи запису секторів через виклики `NVME_IOCTL_SUBMIT_IO` з обов'язковим дотриманням вирівнювання буферів оперативноі пам'яті по межі сторінки (`4096 байтів`).

## Механічна архітектура пристрою `/dev/nvme-fabrics`

Символьний пристрій `/dev/nvme-fabrics` створюється ядерним модулем `nvme-fabrics.ko` під час завантаження підсистеми NVMe. Цей вузол не є фізичним накопичувачем — він слугує інтерфейсом розбору конфігураційного рядка у структуру параметрів `nvmf_ctrl_options`.

Коли програма у просторі користувача здійснює системний виклик `write()` у відкритий файловий дескриптор `/dev/nvme-fabrics`, ядро викликає внутрішню функцію `nvmf_dev_write()`. Вона зчитує текстовий рядок параметрів, розділених комами, виконує парсинг мережевих адрес та викликає транспортно-специфічний провайдер (`nvme_tcp_create_ctrl` для TCP або `nvme_rdma_create_ctrl` для RDMA). Якщо підключення до таргета проходить успішно, ядро створює новий контролер `/sys/class/nvme/nvmeX` та відповідний блочний пристрій `/dev/nvmeXn1`.

Процес парсингу рядка опцій ядерним провайдером висуває жорсткі вимоги до синтаксису. Ключові параметри конфігурації в рядку текстових опцій розділяються комами:
- `nqn`: Повний рядок NVMe Qualified Name цільової підсистеми.
- `transport`: Назва транспортного шару (`tcp`, `rdma`, `fc`).
- `traddr`: Мережева IP-адреса або ім'я вузла таргета (IPv4/IPv6).
- `trsvcid`: Номер мережевого порту (за замовчуванням `4420`).
- `hostnqn`: Опціональний рядок NQN ініціатора для авторизації на сервері.
- `nr_io_queues`: Кількість створюваних черг введення-виведення (за замовчуванням дорівнює кількості активних ядер CPU).
- `queue_size`: Глибина кожної черги подання SQ (наприклад, 128 або 512).

## Архітектурний приклад: Повний клієнт NVMe-oF (Discovery + Connect + Read)

Нижче наведено практичну реалізацію утиліти керування, яка виконує запит виявлення доступних підсистем (Discovery) та підключається до віддаленого NVMe-oF таргета по TCP.

:::tabs
```c
/* c — реалізація мовою C із використанням низькорівневих системних викликів ioctl */
#define _GNU_SOURCE   /* O_DIRECT у glibc відкривається лише з цим макросом */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <errno.h>
#include <stdint.h>
#include <linux/nvme_ioctl.h>

#define NVME_FABRICS_DEV "/dev/nvme-fabrics"
#define PAGE_SIZE 4096

/* Константи підсистеми Fabrics у ядрі Linux */
#define NVME_SC_SUCCESS 0x0

/* Прототип функції виконання прямого читання секторів з блокового пристрою */
static int read_nvme_block_c(const char *dev_path, uint64_t lba, void *buffer, size_t size) {
    int fd = open(dev_path, O_RDWR | O_DIRECT);
    if (fd < 0) {
        perror("Помилка відкриття блокового пристрою NVMe");
        return -1;
    }

    struct nvme_user_io io_cmd;
    memset(&io_cmd, 0, sizeof(io_cmd));
    io_cmd.opcode = 0x02; /* NVMe Read command */
    io_cmd.flags = 0;
    io_cmd.control = 0;
    io_cmd.metadata = 0;
    io_cmd.addr = (uint64_t)buffer;
    io_cmd.slba = lba;
    io_cmd.nblocks = (size / 512) - 1; /* 0-based count */

    int ret = ioctl(fd, NVME_IOCTL_SUBMIT_IO, &io_cmd);
    close(fd);

    if (ret < 0) {
        perror("Помилка виконання NVME_IOCTL_SUBMIT_IO");
        return -1;
    }

    return 0;
}

int main(int argc, char *argv[]) {
    printf("[C-Client] Ініціалізація підключення до NVMe-oF Target...\n");

    /* 1. Відкриття контрольного пристрою fabrics */
    int fabrics_fd = open(NVME_FABRICS_DEV, O_RDWR);
    if (fabrics_fd < 0) {
        perror("Не вдалося відкрити " NVME_FABRICS_DEV ". Перевірте модуль nvme-fabrics");
        return EXIT_FAILURE;
    }

    /* 2. Формування рядка параметрів для команди connect */
    char options[512];
    snprintf(options, sizeof(options),
             "nqn=nqn.2024-08.com.example:nvme.target1,transport=tcp,traddr=192.168.1.100,trsvcid=4420");

    printf("[C-Client] Відправка параметрів у /dev/nvme-fabrics: %s\n", options);

    ssize_t written = write(fabrics_fd, options, strlen(options));
    if (written < 0) {
        perror("Помилка запису у /dev/nvme-fabrics (Connect failed)");
        close(fabrics_fd);
        return EXIT_FAILURE;
    }

    close(fabrics_fd);
    printf("[C-Client] Успішно підключено віддалений контролер NVMe-oF.\n");

    /* 3. Виділення вирівняного буфера пам'яті під Direct IO */
    void *buf = NULL;
    if (posix_memalign(&buf, PAGE_SIZE, PAGE_SIZE) != 0) {
        perror("Помилка виділення вирівняної пам'яті posix_memalign");
        return EXIT_FAILURE;
    }

    /* 4. Читання першого сектора з пристрою /dev/nvme0n1 */
    const char *target_dev = "/dev/nvme0n1";
    if (read_nvme_block_c(target_dev, 0, buf, PAGE_SIZE) == 0) {
        printf("[C-Client] Успішно прочитано LBA 0 з %s. Сигнатура: 0x%02x%02x\n",
               target_dev, ((unsigned char *)buf)[0], ((unsigned char *)buf)[1]);
    }

    free(buf);
    return EXIT_SUCCESS;
}
```
```cpp
// cpp — ідіоматична реалізація мовою C++20 з використанням RAII, std::span та std::expected
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <expected>
#include <system_error>
#include <cstdlib>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>

namespace nvmeof {

// RAII обгортка для файлового дескриптора
class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd = -1) : fd_(fd) {}
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

// Делегат вирівняного виділення пам'яті для Direct I/O
struct PageAlignedDeleter {
    void operator()(void* ptr) const noexcept {
        ::free(ptr);
    }
};

template <typename T>
using PageAlignedBuffer = std::unique_ptr<T[], PageAlignedDeleter>;

template <typename T>
[[nodiscard]] PageAlignedBuffer<T> allocate_aligned_buffer(size_t count, size_t alignment = 4096) {
    void* ptr = nullptr;
    size_t total_bytes = count * sizeof(T);
    if (::posix_memalign(&ptr, alignment, total_bytes) != 0) {
        throw std::bad_alloc();
    }
    return PageAlignedBuffer<T>(static_cast<T*>(ptr));
}

// Клієнт управління NVMe-oF
class NvmeOfClient {
    static constexpr std::string_view FabricsDevice = "/dev/nvme-fabrics";
public:
    // Підключення до віддаленої підсистеми NVMe-oF
    [[nodiscard]] static std::expected<void, std::error_code> connect(
        std::string_view nqn,
        std::string_view traddr,
        std::string_view trsvcid = "4420",
        std::string_view transport = "tcp") 
    {
        UniqueFd fd(::open(FabricsDevice.data(), O_RDWR));
        if (!fd.valid()) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        std::string options = std::string("nqn=") + std::string(nqn) +
                              ",transport=" + std::string(transport) +
                              ",traddr=" + std::string(traddr) +
                              ",trsvcid=" + std::string(trsvcid);

        ssize_t ret = ::write(fd.get(), options.data(), options.size());
        if (ret < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return {};
    }

    // Виконання прямого читання логічних блоків LBA
    [[nodiscard]] static std::expected<void, std::error_code> read_lba(
        std::string_view dev_path,
        uint64_t lba,
        std::span<std::byte> buffer) 
    {
        UniqueFd fd(::open(dev_path.data(), O_RDWR | O_DIRECT));
        if (!fd.valid()) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        nvme_user_io io_cmd{};
        io_cmd.opcode = 0x02; // NVMe Read
        io_cmd.addr = reinterpret_cast<uint64_t>(buffer.data());
        io_cmd.slba = lba;
        io_cmd.nblocks = static_cast<uint16_t>((buffer.size() / 512) - 1);

        int ret = ::ioctl(fd.get(), NVME_IOCTL_SUBMIT_IO, &io_cmd);
        if (ret < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return {};
    }
};

} // namespace nvmeof

int main() {
    std::cout << "[C++20 Client] Підключення до віддаленої підсистеми NVMe-oF...\n";

    constexpr std::string_view target_nqn = "nqn.2024-08.com.example:nvme.target1";
    constexpr std::string_view target_ip = "192.168.1.100";

    auto conn_res = nvmeof::NvmeOfClient::connect(target_nqn, target_ip);
    if (!conn_res) {
        std::cerr << "Помилка підключення: " << conn_res.error().message() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << "[C++20 Client] Успішно підключено. Читання сектора...\n";

    constexpr size_t buffer_size = 4096;
    auto aligned_buf = nvmeof::allocate_aligned_buffer<std::byte>(buffer_size);
    std::span<std::byte> buf_span(aligned_buf.get(), buffer_size);

    auto read_res = nvmeof::NvmeOfClient::read_lba("/dev/nvme0n1", 0, buf_span);
    if (!read_res) {
        std::cerr << "Помилка читання LBA: " << read_res.error().message() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << "[C++20 Client] Блок успішно прочитано у RAII буфер!\n";
    return EXIT_SUCCESS;
}
```
:::

## Асинхронне введення-виведення через `io_uring` та команди passthrough

Сучасні високопродуктивні застосунки (наприклад, СУБД ScyllaDB або нові версії Ceph) відмовляються від синхронного виклику `ioctl(NVME_IOCTL_SUBMIT_IO)` на користь підсистеми **`io_uring`**. Починаючи з ядра Linux 5.19, `io_uring` підтримує асинхронні passthrough-команди NVMe через код операції `IORING_OP_URING_CMD` із `cmd_op = NVME_URING_CMD_IO`.

При використанні `io_uring` програма заповнює комірку черги submission queue entry (`struct io_uring_sqe`), виставляючи `opcode = IORING_OP_URING_CMD`, дескриптор символьного вузла `/dev/ng0n1` та потрібний `cmd_op`. Замість переходу у контекст ядра для кожного окремого запиту програма кладе десятки команд у кільцевий буфер у спільній пам'яті й робить один системний виклик `io_uring_enter()`.

Переваги асинхронної обробки через `io_uring` для NVMe-oF:
- **Batching:** десятки команд SQE подаються одним системним викликом `io_uring_enter()`, а вже драйвер `nvme-tcp` вирішує, скільки капсул укласти в одну відправку в сокет.
- **Passthrough:** команда NVMe доходить до контролера без трансляції у BIO й назад, тож застосунок може вживати власні опкоди та вендорські команди.
- **SQPOLL:** режим `IORING_SETUP_SQPOLL` садить окремий потік ядра опитувати кільце подання, тож у сталому режимі застосунок не робить жодного системного виклику — з бюджету запиту зникає вхід у ядро.

## Внутрішній маппінг черг `blk-mq` на мережеві сокети NVMe/TCP

Після того, як команда `write()` у пристрій `/dev/nvme-fabrics` завершується успішно, ядро Linux створює екземпляр контролера `struct nvme_tcp_ctrl`. Внутрішня підсистема багатовхідних черг блокового рівня `blk-mq` ініціалізує масив апаратних черг `struct blk_mq_hw_ctx`, прив'язаний до створених мережевих сокетів.

Для кожного процесорного ядра драйвер створює окрему чергу `struct nvme_tcp_queue` та відкриває сокет ядра `struct socket`. Коли застосунок виконує виклик `read_lba()`, блоковий рівень форматує об'єкт `struct request`, який передається у функцію `nvme_tcp_queue_rq()`.

Внутрішньо драйвер `nvme-tcp` перетворює запит ядра у структуру `struct nvme_tcp_request`:
1. Формується спільний 8-байтний заголовок PDU `CapsuleCmd` (`struct nvme_tcp_cmd_pdu`).
2. 64-байтна капсула SQE копіюється в тіло PDU — разом 72 байти, як і показує трасування нижче.
3. Готується масив `struct kvec` для системного виклику `kernel_sendmsg()`.
4. Мережевий стек надсилає кадри у сокет через підсистему `tcp_sendmsg()`.

У разі використання підсистеми **ktls (Kernel TLS)** або апаратних мережевих карт із підтримкою zero-copy надсилання сторінок даних `C2HData` / `H2CData` виконується безпосередньо зі сторінок пам'яті `struct page` через `skb_frag_t`, що дозволяє досягти нульового копіювання буферів оперативноі пам'яті.

## Підтримка Multipathing та станів ANA (Asymmetric Namespace Access)

При побудові високонадійних мереж зберігання даних клієнт NVMe-oF підключається до одного дискового тома через декілька незалежних мережевих адаптерів (Multipathing). Ядро Linux реалізує нативну підтримку мультипасингу NVMe (Native Multipathing), яка управляється специфікацією **ANA (Asymmetric Namespace Access)**.

Застосунок користувацького простору або системний демон моніторингу відстежує зміну станів ANA через прочитання файлів sysfs за шляхом `/sys/class/nvme-subsystem/nvme-subsysX/nvme0n1/ana_state`:
- **`optimized`:** Основний високошвидкісний шлях. Запити I/O направляються на цей контролер з мінімальною затримкою.
- **`non-optimized`:** Резервний шлях. Таргет здатний обробляти I/O, але трафік мандрує міжконтролерною шиною зберігання, що збільшує затримку.
- **`inaccessible`:** Шлях тимчасово недоступний (наприклад, під час планового перезавантаження мережевого комутатора).
- **`change`:** Підсистема перебуває у процесі перемикання станів (Failover Transition).

Обробка станів ANA на рівні користувацького коду дозволяє здійснювати динамічне перенаправлення трафіку на резервні IP-адреси таргета без зупинки обробки запитів у СУБД. Режим автоматичного перемикання каналів виключає виникнення тривалих пауз I/O та запобігає появі помилок `EIO` у застосунках.

## Налаштування шифрування kTLS для NVMe/TCP

У специфікації NVMe-oF 1.1 з'явилася нативна підтримка шифрування мережевого трафіку за допомогою протоколу TLS 1.3 (Transport Layer Security). Для уникнення деградації продуктивності ядро Linux реалізує підсистему **kTLS (In-Kernel TLS)**.

При використанні kTLS рукостискання TLS (Handshake) виконується бібліотекою OpenSSL у просторі користувача, після чого симетричні ключі шифрування AES-GCM передаються в ядро через `setsockopt(SOL_TLS, TLS_TX, ...)`. Мережевий модуль `nvme-tcp` надсилає PDU безпосередньо через шифрований сокет kTLS, а якщо карта вміє Inline TLS Offload, шифрування виконує вона сама «на льоту», не витрачаючи тактів процесора. Це дозволяє тримати конфіденційність трафіку без втрати пропускної здатності у мережах 100GbE.

## Використання вищого рівня: Бібліотека `libnvme` C API

У реальних виробничих проектах керування підключеннями часто виконують не через сирі `write()` у `/dev/nvme-fabrics`, а через офіційну C-бібліотеку `libnvme` (C library for NVMe administration).

Бібліотека надає об'єктно-орієнтоване C API для роботи з топологією:

```
struct nvme_root -> struct nvme_host -> struct nvme_subsystem -> struct nvme_ctrl
```

Типовий цикл виявлення та підключення через `libnvme`:

1. Створення кореневого контексту `struct nvme_root *r = nvme_create_root(stderr, DEFAULT_LOG_LEVEL)`.
2. Ініціалізація об'єкта хоста `struct nvme_host *h = nvme_default_host(r)`.
3. Створення контролера Discovery `struct nvme_ctrl *c = nvme_create_discovery_ctrl(r, h, "tcp", "192.168.1.100", "4420")`.
4. Отримання сторінок журналу `struct nvmf_discovery_log *log = nvme_get_discovery_log(c, &args)`.
5. Підключення до кожного поверненого NQN через `nvme_connect_node(h, entry->subnqn, entry->traddr, entry->trsvcid)`.

Перевага `libnvme` полягає в автоматичній обробці повернених помилок та таймаутів reconnect, а також нативній підтримці парсингу JSON-конфігурацій.

## Детальний розбір C-реалізації та роботи з `struct nvme_user_io`

У прикладі C-коду взаємодія з блочним пристроєм після підключення реалізована через системний виклик `ioctl()` із командою `NVME_IOCTL_SUBMIT_IO`. Розглянемо ключові кроки:

1. **Відкриття пристрою з прапорцем `O_DIRECT`:** Прапорець `O_DIRECT` вказує ядру операційної системи пропустити кеш сторінок (Page Cache) та виконувати введення-виведення безпосередньо між буфером програми користувача та мережевою картою чи контролером NVMe. Це виключає подвійне копіювання даних у пам'яті.
2. **Заповнення структури `struct nvme_user_io`:**
   - `opcode = 0x02`: Задає код операції нативного NVMe Read.
   - `addr`: 64-бітне число, що містить покажчик на виділений буфер у пам'яті програми користувача.
   - `slba`: Початковий адресований логічний блок (Starting LBA).
   - `nblocks`: Кількість блоків для передачі. Специфікація NVMe кодує це поле за виразом `Count - 1`. Тому для читання 8 секторів (4096 байтів при секторі 512 байтів) записується значення `7`.
3. **Виділення пам'яті через `posix_memalign()`:** Стандартна функція `malloc()` повертає буфер, вирівняний по межі 8 або 16 байтів. Для Direct IO ядро вимагає вирівнювання адреси буфера по межі сторінки (4096 байтів), інакше системний виклик `ioctl()` поверне відмову `EINVAL`.

## Детальний розбір C++20 реалізації та безпеки ресурсів (RAII)

C++20 версія клієнта переносить низькорівневу логіку у безпечну об'єктно-орієнтовану модель без використання сирих покажчиків і `goto`:

1. **Клас `UniqueFd` (RAII закриття файлів):** Забезпечує автоматичне закриття файлового дескриптора при виході з області видимості, у тому числі при виникненні виняткових ситуацій чи поверненні з функції з помилкою. Конструктор переміщення дозволяє безпечно передавати ownership дескриптора між функціями.
2. **Типізований алокатор `allocate_aligned_buffer()`:** Використовує `std::unique_ptr` із кастомним деструктором `PageAlignedDeleter`, який автоматично викликає `free()` при знищенні об'єкта. Це виключає витоки пам'яті при роботі з `posix_memalign()`.
3. **Використання `std::span` та `std::expected`:**
   - `std::span<std::byte>` передає розмір та покажчик на буфер як єдиний безпечний view, усуваючи ризик виходу за межі буфера.
   - `std::expected<void, std::error_code>` надає механізм обробки помилок без накладних витрат C++ винятків (Exception Handling overhead). Якщо системний виклик `write()` чи `ioctl()` повертає від'ємне значення, функція повертає об'єкт `std::unexpected` із системним кодом помилки `errno`.

## Оптимізація сокетів у користувацькому просторі

При побудові власних юзерспейс клієнтів (наприклад, у фреймворках SPDK — Storage Performance Development Kit) для сокета вимагається встановлення низькорівневих сокетних опцій через `setsockopt()`:

:::tabs
=== C
```c
int val = 1;
setsockopt(sock_fd, IPPROTO_TCP, TCP_NODELAY, &val, sizeof(val));
```
=== C++20
```cpp
int val = 1;
setsockopt(sock_fd, IPPROTO_TCP, TCP_NODELAY, &val, sizeof(val));
```
:::

Параметр `TCP_NODELAY` вимикає алгоритм Нагла (Nagle's Algorithm), який притримував би дрібні командні PDU до підтвердження попередніх; у парі з відкладеним ACK отримувача це давало б паузи аж до десятків мілісекунд. Крім того, опція `SO_BUSY_POLL` вмикає активне опитування мережевої карти без переходу в режим очікування переривання, що важливо для низькозатримкових баз даних.

## Збірка, запуск та тестування у системі Linux

Для збірки наведених прикладів у системі Linux із компіляторами GCC або Clang виконайте наступні команди:

```bash
# Збірка версії C
gcc -O2 -Wall -Wextra proj_client.c -o nvmeof_c_client

# Збірка версії C++20
g++ -O2 -std=c++20 -Wall -Wextra proj_client.cpp -o nvmeof_cpp_client
```

Перед запуском програми переконайтеся, що в ядрі завантажено необхідний транспортний модуль:

```bash
sudo modprobe nvme-tcp
```

Якщо запуск виконується у тестовому середовищі без реального мережевого таргета, можна підняти локальну підсистему `nvmet` на інтерфейсі `loopback` (`127.0.0.1`):

```bash
# Створення тестової підсистеми у ConfigFS
sudo mkdir /sys/kernel/config/nvmet/subsystems/nqn.2024-08.com.example:nvme.target1
echo 1 | sudo tee /sys/kernel/config/nvmet/subsystems/nqn.2024-08.com.example:nvme.target1/attr_allow_any_host

# Створення логічного порту TCP
sudo mkdir /sys/kernel/config/nvmet/ports/1
echo "tcp" | sudo tee /sys/kernel/config/nvmet/ports/1/addr_trtype
echo "127.0.0.1" | sudo tee /sys/kernel/config/nvmet/ports/1/addr_traddr
echo "4420" | sudo tee /sys/kernel/config/nvmet/ports/1/addr_trsvcid
echo "ipv4" | sudo tee /sys/kernel/config/nvmet/ports/1/addr_adrfam

# Зв'язування порту з підсистемою
sudo ln -s /sys/kernel/config/nvmet/subsystems/nqn.2024-08.com.example:nvme.target1 \
    /sys/kernel/config/nvmet/ports/1/subsystems/
```

Запуск бінарного файлу від імені суперкористувача `root` (необхідно для доступу до `/dev/nvme-fabrics`):

```bash
sudo ./nvmeof_cpp_client
```

## Відстеження стану підключених контролерів через sysfs та procfs

Операційна система Linux відображає всю внутрішню топологію активних підключень NVMe-oF у файловій системі sysfs за шляхом `/sys/class/nvme/`. Програма може інспектувати стан створених контролерів у реальному часі без надсилання мережевих пакетів:

- `/sys/class/nvme/nvme0/state`: Поточний стан контролера (`live` — підключено та готово до IO, `connecting` — у процесі встановлення з'єднання, `resetting` — у стані перезапуску, `deleting` — видаляється).
- `/sys/class/nvme/nvme0/transport`: Використовуваний тип транспорту (`tcp`, `rdma` або `fc`).
- `/sys/class/nvme/nvme0/address`: Текстова адреса таргета (наприклад, `traddr=192.168.1.100,trsvcid=4420`).
- `/sys/class/nvme/nvme0/subsysnqn`: NVMe Qualified Name цільової підсистеми.
- `/sys/class/nvme/nvme0/cntlid`: Числовий ідентифікатор контролера, виділений сервером.

Програмне зчитування цих файлів дозволяє побудувати власний моніторинг стану мережевих блочних пристроїв у просторі користувача.

## Простеження через ftrace та аналіз пакетів у Wireshark

Для глибокого відлагодження передачі PDU кадрів у ядрі Linux передбачено вбудовану підсистему спостереження `ftrace`. Усі події передачі команд та PDU логуються в підсистемі `nvme_tcp`:

```bash
# Увімкнення tracepoints для NVMe/TCP
echo 1 | sudo tee /sys/kernel/debug/tracing/events/nvme_tcp/enable

# Моніторинг подій обміну PDU у реальному часі
sudo cat /sys/kernel/debug/tracing/trace_pipe
```

Вивід трасування показує точний таймінг надсилання кадрів `nvme_tcp_send_cmd_pdu` та прийому відповіді `nvme_tcp_recv_pdu`:

```
nvme_tcp_send_cmd_pdu: nvme0: qid 1, tag 0x12, cmd opcode 0x2, plen 72
nvme_tcp_recv_pdu:     nvme0: qid 1, pdu type 0x7 (C2HData), plen 4128
nvme_tcp_recv_pdu:     nvme0: qid 1, pdu type 0x5 (CapsuleResp), status 0x0
```

Для аналізу мережевих кадрів у аналізаторі `Wireshark` використовується вбудований дисектор `nvme-tcp`. При захопленні трафіку на порту `4420` Wireshark розкодовує заголовки PDU, показує текстові значення NQN, параметри команд у PDU `CapsuleCmd` та стан контрольних сум `Data Digest CRC32c`.

## Пастки реалізації та системні підводні камені

При розробці системних додатків взаємодії з NVMe over Fabrics програмісти зіштовхуються з трьома поширеними помилками:

### 1. Помилка вирівнювання пам'яті (Direct I/O Boundary Violations)

При роботі через прапорець `O_DIRECT` у виклику `open()` ядерний блоковий рівень вимагає, щоб початкова адреса буфера у користувацькому просторі була суворо вирівняна по межі розміру фізичного сектора диска (512 або 4096 байтів). Використання стандартного `malloc()` або `std::vector::data()` без вирівнювання призводить до відмови системного виклику з помилкою `EINVAL` (Invalid Argument). Для виділення пам'яті слід використовувати `posix_memalign()` у C або `std::unique_ptr` із деструктором `free` над вирівняним вказівником у C++.

### 2. Конкуренція за символьний пристрій `/dev/nvme-fabrics`

Символьний пристрій `/dev/nvme-fabrics` є єдиною точкою входження для всіх процесів системи. Запис рядка конфігурації у `write()` є атомарним на рівні ядра, але якщо декілька паралельних процесів намагаються одночасно відкрити сокети підключення до однакового NQN без координації, ядро поверне помилку `EALREADY` або `EBUSY`.

### 3. Налаштування KATO (Keep Alive Timeout) та мережеві таймаути

При підключенні через `libnvme` або ручний запис у `/dev/nvme-fabrics` за замовчуванням `keep_alive_tmo` становить одиниці секунд. У нестабільних мережах із можливими короткочасними втратами пакетів це може призводити до фатального відключення блокового пристрою ядерним модулем `nvme-tcp`. При створенні високонадійних клієнтів рекомендується явно збільшувати значення `keep_alive_tmo` до 30–60 секунд та налаштовувати параметр `reconnect_delay`.
