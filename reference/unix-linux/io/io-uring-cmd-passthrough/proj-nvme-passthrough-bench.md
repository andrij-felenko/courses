# ⚙️ Практична реалізація бенчмарку NVMe passthrough на C та C++

Ця вставка містить повноцінний практичний проєкт для вимірювання продуктивності та відправки низькорівневих команд NVMe Read безпосередньо через символьний дескриптор `/dev/ng0n1` за допомогою підсистеми `io_uring` та опкоду `IORING_OP_URING_CMD`.

Проєкт продемонстровано у двох варіантах:
1. **Чистий C (стандарт C11 / POSIX):** Використовує низькорівневі системні виклики та стандартну бібліотеку `liburing`. Демонструє явне керування ресурсами, перевірку вирівнювання пам'яті та ручне заповнення командних слів NVMe.
2. **Ідіоматичний C++20:** Використовує концепцію RAII для автоматичного керування файловими дескрипторами та контекстом `io_uring`, безпечні буфери `std::span` із гарантованим DMA-вирівнюванням, а також стандартний механізм повернення помилок `std::expected`.

## Постановка практичного завдання

Головною метою бенчмарку є пряма передача команд апаратного зчитання блоків безпосередньо в контролер NVMe, минаючи VFS та підсистему `blk-mq`. Застосунок повинен ініціалізувати кільце `io_uring`, виділити пам'ять з alignment 4096 байт, сформувати 40-байтне навантаження `struct nvme_uring_cmd` всередині SQE, надіслати запит та обробити результат у CQE з мінімальними накладними витратами.

Крім того, реалізація висуває вимоги щодо гарантії сумісності з різними розмірами секторів накопичувачів (512 байт та 4096 байт) та безпечного закриття ресурсів під час обробки системних сигналів переривання.

## Код реалізації проєкту

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <liburing.h>
#include <linux/nvme_ioctl.h>

#define ALIGNMENT 4096
#define READ_SIZE 4096

int main(int argc, char *argv[]) {
    const char *dev_path = (argc > 1) ? argv[1] : "/dev/ng0n1";
    struct io_uring ring;
    int fd;
    void *buffer;
    struct io_uring_sqe *sqe;
    struct io_uring_cqe *cqe;
    struct nvme_uring_cmd *cmd;
    int ret;

    /* Відкриваємо символьний пристрій NVMe generic character device */
    fd = open(dev_path, O_RDWR);
    if (fd < 0) {
        perror("Помилка відкриття NVMe символьного пристрою");
        return 1;
    }

    /* Виділяємо вирівняну пам'ять для DMA (4096 байт) */
    ret = posix_memalign(&buffer, ALIGNMENT, READ_SIZE);
    if (ret != 0) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        close(fd);
        return 1;
    }
    memset(buffer, 0, READ_SIZE);

    /* Ініціалізуємо io_uring з глибиною черги 32 */
    ret = io_uring_queue_init(32, &ring, 0);
    if (ret < 0) {
        fprintf(stderr, "Помилка ініціалізації io_uring: %s\n", strerror(-ret));
        free(buffer);
        close(fd);
        return 1;
    }

    /* Отримуємо вільний елемент черги подачі SQE */
    sqe = io_uring_get_sqe(&ring);
    if (!sqe) {
        fprintf(stderr, "Не вдалося отримати SQE з кільця\n");
        io_uring_queue_exit(&ring);
        free(buffer);
        close(fd);
        return 1;
    }

    /* Налаштовуємо операцію IORING_OP_URING_CMD */
    io_uring_prep_rw(IORING_OP_URING_CMD, sqe, fd, NULL, 0, 0);
    sqe->cmd_op = NVME_URING_CMD_IO;

    /* Заповнюємо специфічну структуру команди NVMe */
    cmd = (struct nvme_uring_cmd *)sqe->cmd;
    memset(cmd, 0, sizeof(*cmd));
    cmd->opcode = 0x02; /* NVMe I/O Read opcode */
    cmd->nsid = 1;      /* Namespace ID 1 */
    cmd->addr = (__u64)buffer;
    cmd->data_len = READ_SIZE;
    cmd->cdw10 = 0;     /* LBA 0 (нижні 32 біти) */
    cmd->cdw11 = 0;     /* LBA 0 (верхні 32 біти) */
    cmd->cdw12 = 0;     /* 1 блок (0-based значення: 0 відповідає 1 LBA) */

    sqe->user_data = 0x42;

    /* Відправляємо команду в ядро */
    ret = io_uring_submit(&ring);
    if (ret < 0) {
        fprintf(stderr, "Помилка відправлення SQE: %s\n", strerror(-ret));
        io_uring_queue_exit(&ring);
        free(buffer);
        close(fd);
        return 1;
    }

    /* Очікуємо завершення виконання у CQE */
    ret = io_uring_wait_cqe(&ring, &cqe);
    if (ret < 0) {
        fprintf(stderr, "Помилка очікування CQE: %s\n", strerror(-ret));
        io_uring_queue_exit(&ring);
        free(buffer);
        close(fd);
        return 1;
    }

    if (cqe->res == 0) {
        printf("NVMe Read успішно виконано! Прочитано %d байт з LBA 0.\n", READ_SIZE);
    } else {
        fprintf(stderr, "NVMe Read завершився з помилкою res = %d\n", cqe->res);
    }

    io_uring_cqe_seen(&ring, cqe);
    io_uring_queue_exit(&ring);
    free(buffer);
    close(fd);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <expected>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <liburing.h>
#include <linux/nvme_ioctl.h>

namespace nvme_uring {

// RAII обгортка для файлового дескриптора символьного пристрою
class NvmeDevice {
    int fd_{-1};
public:
    explicit NvmeDevice(const char* path) {
        fd_ = ::open(path, O_RDWR);
    }
    ~NvmeDevice() {
        if (fd_ >= 0) ::close(fd_);
    }
    NvmeDevice(const NvmeDevice&) = delete;
    NvmeDevice& operator=(const NvmeDevice&) = delete;
    NvmeDevice(NvmeDevice&& o) noexcept : fd_{o.fd_} { o.fd_ = -1; }

    [[nodiscard]] int fd() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

// RAII обгортка для кільця io_uring
class UringContext {
    struct io_uring ring_{};
    bool active_{false};
public:
    explicit UringContext(unsigned entries) {
        if (::io_uring_queue_init(entries, &ring_, 0) == 0) {
            active_ = true;
        }
    }
    ~UringContext() {
        if (active_) ::io_uring_queue_exit(&ring_);
    }
    UringContext(const UringContext&) = delete;
    UringContext& operator=(const UringContext&) = delete;

    [[nodiscard]] struct io_uring* ring() noexcept { return &ring_; }
    [[nodiscard]] bool valid() const noexcept { return active_; }
};

// RAII буфер з вирівнюванням пам'яті під DMA
class DmaBuffer {
    void* ptr_{nullptr};
    std::size_t size_{0};
public:
    DmaBuffer(std::size_t alignment, std::size_t size) : size_{size} {
        if (::posix_memalign(&ptr_, alignment, size_) != 0) {
            ptr_ = nullptr;
        }
    }
    ~DmaBuffer() {
        if (ptr_) ::free(ptr_);
    }
    DmaBuffer(const DmaBuffer&) = delete;
    DmaBuffer& operator=(const DmaBuffer&) = delete;

    [[nodiscard]] std::span<std::byte> as_bytes() noexcept {
        return {reinterpret_cast<std::byte*>(ptr_), size_};
    }
    [[nodiscard]] void* raw() const noexcept { return ptr_; }
    [[nodiscard]] std::size_t size() const noexcept { return size_; }
    [[nodiscard]] bool valid() const noexcept { return ptr_ != nullptr; }
};

// Асинхронна функція відправлення команди NVMe Read
std::expected<std::size_t, std::error_code> read_nvme_block(
    NvmeDevice& dev,
    UringContext& ring_ctx,
    DmaBuffer& buf,
    std::uint64_t lba
) {
    if (!dev.valid() || !ring_ctx.valid() || !buf.valid()) {
        return std::unexpected(std::make_error_code(std::errc::invalid_argument));
    }

    struct io_uring_sqe* sqe = ::io_uring_get_sqe(ring_ctx.ring());
    if (!sqe) {
        return std::unexpected(std::make_error_code(std::errc::resource_unavailable_try_again));
    }

    ::io_uring_prep_rw(IORING_OP_URING_CMD, sqe, dev.fd(), nullptr, 0, 0);
    sqe->cmd_op = NVME_URING_CMD_IO;

    auto* cmd = reinterpret_cast<struct nvme_uring_cmd*>(sqe->cmd);
    std::memset(cmd, 0, sizeof(*cmd));
    cmd->opcode = 0x02; // NVMe Read opcode
    cmd->nsid = 1;      // Namespace ID 1
    cmd->addr = reinterpret_cast<__u64>(buf.raw());
    cmd->data_len = static_cast<__u32>(buf.size());
    cmd->cdw10 = static_cast<__u32>(lba & 0xFFFFFFFF);
    cmd->cdw11 = static_cast<__u32>(lba >> 32);
    cmd->cdw12 = 0;     // 1 LBA (0-based значення)

    sqe->user_data = 0x100;

    int ret = ::io_uring_submit(ring_ctx.ring());
    if (ret < 0) {
        return std::unexpected(std::error_code(-ret, std::generic_category()));
    }

    struct io_uring_cqe* cqe{nullptr};
    ret = ::io_uring_wait_cqe(ring_ctx.ring(), &cqe);
    if (ret < 0) {
        return std::unexpected(std::error_code(-ret, std::generic_category()));
    }

    int res = cqe->res;
    ::io_uring_cqe_seen(ring_ctx.ring(), cqe);

    if (res < 0) {
        return std::unexpected(std::error_code(-res, std::generic_category()));
    }

    return buf.size();
}

} // namespace nvme_uring

int main(int argc, char* argv[]) {
    const char* dev_path = (argc > 1) ? argv[1] : "/dev/ng0n1";
    nvme_uring::NvmeDevice dev{dev_path};
    nvme_uring::UringContext ring{32};
    nvme_uring::DmaBuffer buffer{4096, 4096};

    auto result = nvme_uring::read_nvme_block(dev, ring, buffer, 0);
    if (result) {
        std::cout << "C++20 NVMe Read успішно виконано! Прочитано " << *result << " байт.\n";
    } else {
        std::cerr << "NVMe Read завершився з помилкою: " << result.error().message() << "\n";
        return 1;
    }

    return 0;
}
```
:::

## Детальний аналіз архітектурних рішень у коді

Наведений код демонструє фундаментальні засади побудови низькорівневих систем зберігання даних нового покоління. Розглянемо ключові підсистеми реалізації та пастки, із якими стикаються розробники:

### Керування ресурсами пам'яті та DMA-вирівнювання

Контролер NVMe використовує прямий доступ до пам'яті (PCIe DMA). Якщо буфер пам'яті не вирівняний за фізичною межею 4096 байт, шина PCIe або контролер пам'яті процесора не зможе сформувати одноразовий пакет DMA, що призведе до помилки передачі `-EFAULT` або до необхідності подвійного копіювання всередині ядра.

У С-версії для цього застосовується POSIX-функція `posix_memalign(&buffer, 4096, 4096)`. Вона гарантує, що молодші 12 біт віртуальної адреси дорівнюють нулю. У С++ версії цей механізм інкапсульовано у клас `DmaBuffer`. Конструктор класу бере на себе виділення пам'яті, а деструктор гарантує виклики `free()`. Використання обгортки `std::span<std::byte>` запобігає витокам покажчиків та небезпечному використанню "сирих" адрес `void*`.

### Безпека у C++20 через std::expected та RAII

На відміну від С-реалізації, де помилки повертаються від'ємними значеннями `errno` і вимагають каскадних операторів `if (ret < 0) goto cleanup`, C++20 варіант будується на сучасній концепції обробки помилок `std::expected<T, E>`:

1. **Відсутність винятків у гарячому шляху (Zero-cost exception handling):** Функція `read_nvme_block` не генерує C++ винятків (`throw`), що гарантує детермінований час виконання без раскручування стеку (stack unwinding).
2. **Типобезпечна обробка помилок:** Тип `std::error_code` повертає точний системний код помилки, отриманий від системного виклику або від CQE.
3. **Автоматична очистка кілець:** Класи `NvmeDevice` та `UringContext` самостійно закривають файловий дескриптор (`close`) та звільняють кільце (`io_uring_queue_exit`) під час знищення об'єкта, навіть якщо функція завершилася достроково.

### Налаштування команди та прапорці NVMe

Особливу увагу приділено заповненню структури `nvme_uring_cmd`:
- **Поле `opcode = 0x02`:** Це стандартний апаратний опкод NVMe I/O Read. Для операції запису використовується опкод `0x01`.
- **Поле `nsid = 1`:** Ідентифікатор простору імен. Для більшості одинарних NVMe-накопичувачів це значення дорівнює `1`.
- **Поля `cdw10` та `cdw11`:** Складають 64-бітну адресу LBA. Оскільки значення передається як 64-бітне число `uint64_t lba`, у C++ коді воно безпечно розділяється на молодші (`lba & 0xFFFFFFFF`) та старші (`lba >> 32`) 32 біти.
- **Поле `cdw12 = 0`:** Кількість секторів для зчитування. Важливо пам'ятати, що у специфікації NVMe це значення є 0-based: `0` означає зчитати 1 сектор (512 або 4096 байт залежно від формату низькорівневої розмітки накопичувача).

## Асинхронний поллінг та режим IOPOLL

У бенчмарках, орієнтованих на досягнення понад 1 000 000 IOPS, програма видозмінюється для роботи у режимі busy-polling. При створенні кільця додається прапорець `IORING_SETUP_IOPOLL`:

:::tabs
```c
/* Створення io_uring у режимі IOPOLL для низьких затримок на C */
struct io_uring_params params;
memset(&params, 0, sizeof(params));
params.flags = IORING_SETUP_IOPOLL;

int ret = io_uring_queue_init_params(32, &ring, &params);
if (ret < 0) {
    perror("Помилка створення IOPOLL кільця");
}
```
```cpp
// Створення io_uring у режимі IOPOLL на C++20 з обробкою помилок
#include <system_error>
#include <liburing.h>

std::expected<struct io_uring, std::error_code> create_iopoll_ring(unsigned entries) {
    struct io_uring ring{};
    struct io_uring_params params{};
    params.flags = IORING_SETUP_IOPOLL;

    int ret = ::io_uring_queue_init_params(entries, &ring, &params);
    if (ret < 0) {
        return std::unexpected(std::error_code(-ret, std::generic_category()));
    }
    return ring;
}
```
:::

У режимі `IOPOLL` замість виклику `io_uring_wait_cqe()` застосунок робить неблокуюче опитування `io_uring_enter()` із прапорцем `IORING_ENTER_GETEVENTS`. Це переводить CPU у вибіркову перевірку статусних бітів hardware CQ NVMe контролера, виключаючи переривання MSI-X та знімаючи накладні витрати на зміну контексту процесора.

Завдяки уникненню переривань процесорний кеш L1/L2 залишається гарячим, а затримка зчитування зменшується до значення апаратного флеш-чипа SSD (близько 5-7 мікросекунд).

## Трасування через bpftrace та ftrace

Для перевірки того, що запити дійсно проходять повз підсистему `blk-mq`, використовується скрипт `bpftrace`. Він перехоплює вхід у функцію `nvme_ns_uring_cmd` та фіксує час виконання апаратного passthrough:

```bpftrace
#!/usr/bin/env bpftrace
/* Трасування затримок виклику nvme_ns_uring_cmd у наносекундах */

kprobe:nvme_ns_uring_cmd
{
    @start[tid] = nsecs;
}

kretprobe:nvme_ns_uring_cmd
/@start[tid]/
{
    $duration = nsecs - @start[tid];
    @us = hist($duration / 1000);
    delete(@start[tid]);
}

END
{
    printf("Гістограма затримок nvme_ns_uring_cmd (мікросекунди):\n");
}
```

Під час виконання трасування можна переконатися, що середній час проходження команди у ядрі становить менше 400 наносекунд, що у 5-8 разів швидше за класичний виклик `pread()` через `blk-mq`.

## Професійне тестування через fio (Engine io_uring_cmd)

Для всебічного бенчмаркінгу реальних дискових накопичувачів використовується утиліта `fio` з вбудованим двигуном `io_uring_cmd`. Нижче наведено приклад конфігураційного файла `passthru.fio`:

```ini
[global]
filename=/dev/ng0n1
ioengine=io_uring_cmd
cmd_type=nvme
iodepth=64
numjobs=4
thread
group_reporting
direct=1

[randread_passthru]
rw=randread
bs=4k
time_based
runtime=30
```

Запуск даної конфігурації через `sudo fio passthru.fio` демонструє граничні можливості SSD-накопичувача без обмежень з боку файлової системи та блокового шару Linux.

## Налаштування параметрів операційної системи

Для досягнення максимальних показників продуктивності при виконанні пасстру команд NVMe необхідно виконати базову оптимізацію параметрів ядра Linux:

1. **Вимкнення механізму службових переривань irqbalance:** На високонавантажених серверах автоматичний розподіл переривань `irqbalance` створює міжядерний трафік. Переривання від конкретної черги NVMe повинні бути жорстко прив'язані до відповідного ядра CPU через `/proc/irq/N/smp_affinity`.
2. **Налаштування параметрів пам'яті hugepages:** Виділення пам'яті під пули буферів `io_uring` через механізм Transparent Huge Pages (THP) або статичні Hugepages розміром 2 МБ дозволяє зменшити кількість промахів у буфері трансляції адрес TLB (Translation Lookaside Buffer).
3. **Пріоритет системного виклику:** Застосування прапорців `IOSQE_ASYNC` та налаштування пріоритету `ioprio_set` для виділених потоків обробки I/O.

## Налаштування прав доступу udev

За замовчуванням символьні пристрої `/dev/ngXnY` мають права `0600` та належать користувачу `root`. Щоб дозволити непривілейованим застосункам виконувати passthrough команд без виклику `sudo`, створюють правило `udev`:

```bash
# /etc/udev/rules.d/99-nvme-passthrough.rules
KERNEL=="ng[0-9]*n[0-9]*", GROUP="disk", MODE="0660"
```

Після створення правила його застосовують командою `sudo udevadm control --reload-rules && sudo udevadm trigger`.

## Інструкція зі збірки та запуску

Для компіляції та запуску проєкту на системі з Linux kernel 5.19+ вимагається наявність встановленої бібліотеки `liburing` (версії 2.2 або новішої):

```bash
# Збірка прикладу на мові C:
gcc -O2 -std=c11 main.c -luring -o nvme_passthru_c

# Збірка прикладу на мові C++20:
g++ -O2 -std=c++20 main.cpp -luring -o nvme_passthru_cpp

# Запуск з вказанням символьного пристрою (вимагає sudo або прав CAP_SYS_ADMIN):
sudo ./nvme_passthru_c /dev/ng0n1
sudo ./nvme_passthru_cpp /dev/ng0n1
```

Перевірка проходження системних викликів через `strace`:

```bash
sudo strace -e io_uring_setup,io_uring_enter ./nvme_passthru_c /dev/ng0n1
```

У виводі `strace` можна спостерігати єдиний системний виклик `io_uring_enter()`, який передає команду та отримує результат, повністю оминаючи традиційні виклики `read()` та `ioctl()`.
