# 📋 Інтерфейс користувача dma-buf heaps: структура та системний виклик

Ця вставка надає технічний довідник системних викликів, структур даних, бітових масок, прапорців та специфікацій файлових дескрипторів, які використовуються у просторі користувача для виділення неперервної або розділюваної оперативної пам'яті через фреймворк dma-buf heaps.

## Заголовкові файли та вузли пристроїв простору користувача

Для взаємодії з фреймворком dma-buf heaps програма простору користувача мусить підключити системний заголовковий файл ядра Linux:

```c
#include <linux/dma-heap.h>
```

Фреймворк експортує кожну доступну купу пам'яті як окремий символьний пристрій (character device) у системному каталозі `/dev/dma_heap/`. Кожен такий вузол створюється підсистемою ядра під час ініціалізації відповідного драйвера купи та отримує власні старший і молодший номери пристрою (major/minor numbers).

У стандартній конфігурації сучасного ядра Linux у системі присутні наступні вузли пристроїв:
- `/dev/dma_heap/system` — системна купа (System Heap). Виділяє фізично розривні сторінки оперативної пам'яті за допомогою стандартного розподільника сторінок ядра (buddy allocator). Використовується для пристроїв, обладнаних IOMMU.
- `/dev/dma_heap/system-uncached` — системна купа без кешування CPU. Сторінки мапуються з атрибутами `uncached` або `write-combine`, що усуває потребу в ручному скиданні кешів CPU, але знижує швидкість прямого читання процесором.
- `/dev/dma_heap/linux,cma` або `/dev/dma_heap/cma` — купа підсистеми CMA (Contiguous Memory Allocator). Виділяє фізично неперервні блоки пам'яті з зарезервованого регіону RAM для пристроїв без IOMMU.
- `/dev/dma_heap/<vendor>-cma` або `/dev/dma_heap/<vendor>-secure` — специфічні купи розробників SoC (NXP, Rockchip, Qualcomm) для роботи зі статичною SRAM пам'яттю чи ізольованими анклавами TrustZone / TEE.

## Структура `dma_heap_allocation_data`

Виділення пам'яті виконується єдиним системним викликом `ioctl(DMA_HEAP_IOC_ALLOC)` з передачею вказівника на структуру `struct dma_heap_allocation_data`:

```c
struct dma_heap_allocation_data {
    __u64 len;        /* Бажаний розмір буфера в байтах */
    __u32 fd;         /* Повернений файловий дескриптор dma-buf */
    __u32 fd_flags;   /* Прапорці відкриття файлового дескриптора */
    __u64 heap_flags; /* Специфічні прапорці купи */
};
```

### Деталізація полів та механізмів ядра

1. **`len` (`__u64`):**
   Задає обсяг пам'яті в байтах, який необхідно виділити. Ядро автоматично округлює значення `len` вгору до найближчого кратного розміру системної сторінки (`PAGE_SIZE`, що на архітектурах x86_64 та ARM64 зазвичай становить 4096 байт). Якщо простір користувача передає значення `len = 0`, системний виклик негайно завершується з поверненням помилки `-EINVAL`.

2. **`fd` (`__u32`):**
   Вихідне поле. У разі успішного виділення пам'яті ядро створює новий анонімний файл `dma-buf` і записує його файловий дескриптор у це поле. Отриманий дескриптор є повноцінним файловим дескриптором POSIX, підтримує дублювання через системний виклик `dup()`, передачу іншим процесам через `sendmsg()` з підсистемою SCM_RIGHTS у сокетах Unix domain, а також відображення у віртуальний адресний простір через системний виклик `mmap()`.

3. **`fd_flags` (`__u32`):**
   Задає бітові прапорці для створюваного файлового дескриптора. Допустимі комбінації включають:
   - `O_CLOEXEC` — встановлює прапорець `close-on-exec`, що запобігає випадковому витоку відкритих дескрипторів буферів пам'яті при виконанні системного виклику `execve()` у дочірніх процесах.
   - `O_RDWR` — відкриває дескриптор для читання та запису процесом простору користувача.
   - `O_RDONLY` або `O_WRONLY` — обмежує режими доступу до буфера з боку простору користувача при використанні виклику `mmap()`.

4. **`heap_flags` (`__u64`):**
   Зарезервоване бітове поле для передачі додаткових прапорців конкретному розподільнику купи. У стандартній реалізації ядра Linux для куп `system` та `cma` це поле повинно дорівнювати `0`. Якщо простір користувача передає біти, які не підтримуються драйвером купи, ядро негайно повертає помилку `-EINVAL`.

## Системний виклик `DMA_HEAP_IOC_ALLOC`

Системний виклик кодується стандартним макросом `_IOWR`:

```c
#define DMA_HEAP_IOC_MAGIC 'H'
#define DMA_HEAP_IOC_ALLOC _IOWR(DMA_HEAP_IOC_MAGIC, 0x0, struct dma_heap_allocation_data)
```

### Коди помилок та обробка виняткових ситуацій

У разі успішного виконання виклик повертає `0`. При виникненні збою виклик повертає `-1`, а системна змінна `errno` встановлюється в одне з наступних значень:

- `EINVAL`: неокруглений або нульовий розмір `len`, встановлені непідтримувані біти в `heap_flags`, або передано некоректні `fd_flags`.
- `ENOMEM`: ядру не вистачило оперативної пам'яті для виділення сторінок або пул CMA надто фрагментований для виділення суцільного неперервного блоку.
- `ENOTTY`: виклик `ioctl` виконано на дескрипторі файлу, який не належить підсистемі dma-buf heaps.
- `EACCES` / `EPERM`: процес не має достатніх прав доступу на читання або запис для відкриття вузла пристрою в `/dev/dma_heap/`.
- `EFAULT`: вказівник на структуру `dma_heap_allocation_data` посилається на недопустиму область віртуальної пам'яті процесу.

## Відображення буфера у простір користувача через `mmap()`

Для прямого процесорного читання або запису даних у буфер `dma-buf` програма може відобразити файловий дескриптор у свій віртуальний адресний простір:

```c
void *ptr = mmap(NULL, buffer_len, PROT_READ | PROT_WRITE, MAP_SHARED, dmabuf_fd, 0);
if (ptr == MAP_FAILED) {
    perror("mmap dma-buf failed");
}
```

Параметр `offset` при виклику `mmap()` для `dma-buf` обов'язково повинен дорівнювати `0`.

## Синхронізація кешу через `DMA_BUF_IOCTL_SYNC`

Якщо простір користувача звертається до даних у виділеному буфері через відображення `mmap()`, для збереження когерентності між CPU та DMA-контролерами апаратури необхідно виконувати виклик `ioctl(DMA_BUF_IOCTL_SYNC)` з відповідною структурою `struct dma_buf_sync`:

```c
#include <linux/dma-buf.h>

struct dma_buf_sync sync = {
    .flags = DMA_BUF_SYNC_START | DMA_BUF_SYNC_RW
};
ioctl(dma_buf_fd, DMA_BUF_IOCTL_SYNC, &sync);

/* читання або запис даних у mmap-вказівник */

sync.flags = DMA_BUF_SYNC_END | DMA_BUF_SYNC_RW;
ioctl(dma_buf_fd, DMA_BUF_IOCTL_SYNC, &sync);
```

### Специфікація прапорців `dma_buf_sync`

- `DMA_BUF_SYNC_READ`: інвалідація кеш-рядків CPU перед зчитуванням даних, записаних апаратним DMA-контролером.
- `DMA_BUF_SYNC_WRITE`: примусове скидання брудних кеш-рядків CPU (clean/flush) у RAM після модифікації даних процесором.
- `DMA_BUF_SYNC_RW`: комбінація `DMA_BUF_SYNC_READ | DMA_BUF_SYNC_WRITE`.
- `DMA_BUF_SYNC_START`: початок критичної секції процесорного доступу.
- `DMA_BUF_SYNC_END`: завершення критичної секції процесорного доступу.

## Передача файлового дескриптора через UNIX сокети (Inter-Process Communication)

Файловий дескриптор `dma-buf` можна передавати між незалежними процесами у системі без копіювання самого вмісту пам'яті. Для цього застосовується механізм `SCM_RIGHTS` UNIX domain сокетів:

```c
struct msghdr msg = {0};
struct cmsghdr *cmsg;
char buf[CMSG_SPACE(sizeof(int))];

msg.msg_control = buf;
msg.msg_controllen = sizeof(buf);

cmsg = CMSG_FIRSTHDR(&msg);
cmsg->cmsg_level = SOL_SOCKET;
cmsg->cmsg_type = SCM_RIGHTS;
cmsg->cmsg_len = CMSG_LEN(sizeof(int));

*((int *) CMSG_DATA(cmsg)) = dmabuf_fd;

sendmsg(socket_fd, &msg, 0);
```

Приймаючий процес отримує власний файловий дескриптор у своїй таблиці відкритих файлів, який посилається на той самий об'єкт `dma-buf` у ядрі.

## Приклад виклику API у просторі користувача

Нижче наведено робочий приклад виділення буфера пам'яті через інтерфейс dma-buf heaps мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/dma-heap.h>
#include <errno.h>

int allocate_dma_buffer(const char *heap_path, size_t size) {
    int heap_fd = open(heap_path, O_RDONLY | O_CLOEXEC);
    if (heap_fd < 0) {
        perror("open dma_heap device failed");
        return -1;
    }

    struct dma_heap_allocation_data alloc_data = {
        .len = size,
        .fd = 0,
        .fd_flags = O_RDWR | O_CLOEXEC,
        .heap_flags = 0
    };

    if (ioctl(heap_fd, DMA_HEAP_IOC_ALLOC, &alloc_data) < 0) {
        perror("DMA_HEAP_IOC_ALLOC ioctl failed");
        close(heap_fd);
        return -1;
    }

    close(heap_fd);
    return alloc_data.fd;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <expected>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/dma-heap.h>

class UniqueFd {
    int fd_ = -1;
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

std::expected<UniqueFd, std::error_code> allocate_dma_buffer(std::string_view heap_path, std::size_t size) {
    UniqueFd heap_fd(::open(heap_path.data(), O_RDONLY | O_CLOEXEC));
    if (!heap_fd.valid()) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    dma_heap_allocation_data alloc_data{};
    alloc_data.len = size;
    alloc_data.fd_flags = O_RDWR | O_CLOEXEC;
    alloc_data.heap_flags = 0;

    if (::ioctl(heap_fd.get(), DMA_HEAP_IOC_ALLOC, &alloc_data) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return UniqueFd(static_cast<int>(alloc_data.fd));
}
```
:::
