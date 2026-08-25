# 📋 Інтерфейси системних викликів та структур AF_XDP

Сокети AF_XDP (Address Family XDP, заголовок `<linux/if_xdp.h>`) надають прямий та високопродуктивний домен взаємодії між драйвером мережевої карти та простором користувача. Вони оперують сирими кадрами Ethernet і вимагають явного конфігурування буферів пам'яті UMEM та чотирьох кільцевих буферів (SPSC rings). Низькорівнева взаємодія виконується через стандартний системний виклик `socket()` та опції `setsockopt()`, тоді як вищорівнева бібліотека `libxdp` (або застаріла `libbpf`) надає зручні обгортки над цими структурами.

Цей довідник описує повну поверхню API сокетів AF_XDP, структуру системних викликів, опції конфігурування, формати дескрипторів та особливості роботи з низькорівневими буферами пам'яті.

## Створення сокета та константи сімейства

Сокет AF_XDP створюється у просторі користувача через виклик `socket()` із сімейством адрес `AF_XDP` (або `PF_XDP`). Системний виклик приймає тип сокета `SOCK_RAW` та протокол `0`. Повернений файловий дескриптор використовується для прив'язки до мережевого інтерфейсу, конфігурування буферів UMEM, опитування подій через `poll()`/`epoll()` або сповіщення ядра через `sendto()`.

Низькорівневий виклик створення сокета виглядає так:

:::tabs
```c
#include <sys/socket.h>
#include <linux/if_xdp.h>
#include <stdio.h>
#include <unistd.h>

int create_raw_xsk(void) {
    int xsk_fd = socket(AF_XDP, SOCK_RAW, 0);
    if (xsk_fd < 0) {
        perror("socket(AF_XDP) failed");
        return -1;
    }
    return xsk_fd;
}
```
```cpp
#include <sys/socket.h>
#include <linux/if_xdp.h>
#include <system_error>
#include <unistd.h>

class XskSocket {
    int fd_{-1};
public:
    XskSocket() {
        fd_ = ::socket(AF_XDP, SOCK_RAW, 0);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "socket(AF_XDP) failed");
        }
    }
    ~XskSocket() {
        if (fd_ >= 0) ::close(fd_);
    }
    XskSocket(const XskSocket&) = delete;
    XskSocket& operator=(const XskSocket&) = delete;
    XskSocket(XskSocket&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    XskSocket& operator=(XskSocket&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
};
```
:::

При створенні сокета ядро виділяє внутрішню структуру `struct xdp_sock` в системній пам'яті ядра. Однак у цей момент сокет ще не має прив'язаних буферів пам'яті і не здатний приймати чи передавати мережеві кадри. Після створення сокета його необхідно зареєструвати в підсистемі пам'яті UMEM та прив'язати до конкретної черги конкретного мережевого інтерфейсу.

## Реєстрація UMEM: struct xdp_umem_reg

Реєстрація пам'яті UMEM пов'язує виділений у просторі користувача буфер із сокетом AF_XDP за допомогою виклику `setsockopt(fd, SOL_XDP, XDP_UMEM_REG, &mr, sizeof(mr))`. У момент виконання цього виклику ядро перевіряє права процесу (`CAP_NET_ADMIN` або `CAP_BPF`), фіксує сторінки пам'яті у фізичній ОЗП (pinning) та формує внутрішню таблицю сторінок для DMA-адаптера мережевої карти.

Структура конфігурації `struct xdp_umem_reg` визначає геометрію пам'яті UMEM:

```c
struct xdp_umem_reg {
    __u64 addr;         /* Початкова віртуальна адреса буфера у userspace */
    __u64 len;          /* Загальний розмір UMEM у байтах (мусить бути кратним chunk_size) */
    __u32 chunk_size;   /* Розмір одного кадру (зазвичай 2048 або 4096) */
    __u32 headroom;     /* Зарезервоване місце на початку кожного кадру для метаданих */
    __u32 flags;        /* Прапорці налаштування UMEM (наприклад, XDP_UMEM_UNALIGNED_CHUNK_FLAG) */
};
```

### Поля структури `struct xdp_umem_reg`:

- `addr`: Початкова віртуальна адреса пам'яті, виділена у просторі користувача. Пам'ять повинна бути вирівняна на розмір сторінки ядра (`sysconf(_SC_PAGESIZE)` або `getpagesize()`, зазвичай 4096 байтів). Використання невирівняного буфера призведе до помилки `EINVAL`.
- `len`: Загальний розмір буфера UMEM у байтах. Повинен бути кратним розміру кадру `chunk_size`. Зазвичай виділяється масив розміром від кількох мегабайт до кількох гігабайт (наприклад, 4096 кадрів по 2048 байт = 8 МБ).
- `chunk_size`: Фіксований розмір одного кадру пам'яті у байтах. Стандартні значення — 2048 або 4096 байт. Розмір кадру визначає максимальний розмір пакета (MTU), який може бути прийнятий або відправлений без фрагментації.
- `headroom`: Кількість зарезервованих байтів на початку кожного кадру до початку пакетних даних. Використовується для того, щоб eBPF-програми або додаток могли вставляти власні заголовки (наприклад, тунельні заголовки VXLAN/GRE) без зміщення або перерозподілу пам'яті.
- `flags`: Бітова маска додаткових режимів UMEM. Основні прапорці:
  - `0`: Стандартний режим з вирівняними кадрами (Aligned chunks), де адреси кадрів кратні розміру `chunk_size`.
  - `XDP_UMEM_UNALIGNED_CHUNK_FLAG`: Режим невирівняних кадрів (Unaligned chunks), запроваджений у Linux 5.4, який дозволяє використовувати довільні адреси та розміри буферів.

Приклад ініціалізації та реєстрації UMEM у системі:

:::tabs
```c
#include <sys/socket.h>
#include <sys/mman.h>
#include <linux/if_xdp.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>

int setup_umem(int xsk_fd, void **buffer_out, size_t size) {
    void *buffer = NULL;
    if (posix_memalign(&buffer, getpagesize(), size) != 0) {
        perror("posix_memalign failed");
        return -1;
    }

    struct xdp_umem_reg mr = {
        .addr = (uintptr_t)buffer,
        .len = size,
        .chunk_size = 2048,
        .headroom = 0,
        .flags = 0
    };

    if (setsockopt(xsk_fd, SOL_XDP, XDP_UMEM_REG, &mr, sizeof(mr)) < 0) {
        perror("setsockopt(XDP_UMEM_REG) failed");
        free(buffer);
        return -1;
    }

    *buffer_out = buffer;
    return 0;
}
```
```cpp
#include <sys/socket.h>
#include <linux/if_xdp.h>
#include <unistd.h>
#include <cstdlib>
#include <system_error>
#include <memory>
#include <span>

class UmemArea {
    void* addr_{nullptr};
    size_t size_{0};
    uint32_t chunk_size_{2048};
public:
    UmemArea(int xsk_fd, size_t size, uint32_t chunk_size = 2048, uint32_t headroom = 0)
        : size_(size), chunk_size_(chunk_size) {
        if (posix_memalign(&addr_, getpagesize(), size_) != 0) {
            throw std::bad_alloc();
        }

        struct xdp_umem_reg mr{};
        mr.addr = reinterpret_cast<uint64_t>(addr_);
        mr.len = size_;
        mr.chunk_size = chunk_size_;
        mr.headroom = headroom;
        mr.flags = 0;

        if (::setsockopt(xsk_fd, SOL_XDP, XDP_UMEM_REG, &mr, sizeof(mr)) < 0) {
            ::free(addr_);
            throw std::system_error(errno, std::generic_category(), "setsockopt(XDP_UMEM_REG) failed");
        }
    }

    ~UmemArea() {
        if (addr_) ::free(addr_);
    }

    UmemArea(const UmemArea&) = delete;
    UmemArea& operator=(const UmemArea&) = delete;
    UmemArea(UmemArea&& o) noexcept : addr_(o.addr_), size_(o.size_), chunk_size_(o.chunk_size_) {
        o.addr_ = nullptr;
    }

    [[nodiscard]] void* data() const noexcept { return addr_; }
    [[nodiscard]] size_t size() const noexcept { return size_; }
    [[nodiscard]] uint32_t chunk_size() const noexcept { return chunk_size_; }

    [[nodiscard]] std::span<uint8_t> get_frame(uint64_t offset) const {
        return std::span<uint8_t>(static_cast<uint8_t*>(addr_) + offset, chunk_size_);
    }
};
```
:::

У разі недостатності ліміту блокування пам'яті (`RLIMIT_MEMLOCK`) системний виклик `setsockopt(XDP_UMEM_REG)` поверне помилку `EPERM` або `ENOMEM`. Для усунення цієї помилки необхідно збільшити ліміт пам'яті у файлі `/etc/security/limits.conf` або через `setrlimit(RLIMIT_MEMLOCK, ...)`.

## Налаштування кільцевих буферів (Rings)

Кільцеві буфери відображаються в пам'ять користувача за допомогою системного виклику `mmap()`. Розміри кілець повинні бути степенями двійки (наприклад, 1024, 2048, 4096).

Для виділення кілець використовуються такі опції `setsockopt`:
- `XDP_UMEM_FILL_RING`: розмір Fill Ring (для UMEM).
- `XDP_UMEM_COMPLETION_RING`: розмір Completion Ring (для UMEM).
- `XDP_RX_RING`: розмір RX Ring (для сокета).
- `XDP_TX_RING`: розмір TX Ring (для сокета).

Зсуви полів (offsets) усередині mmap-області запитуються через `getsockopt(fd, SOL_XDP, XDP_MMAP_OFFSETS, &off, &optlen)` у структуру `struct xdp_mmap_offsets`:

```c
struct xdp_ring_offset {
    __u64 producer;     /* Зсув до атомарного індексу виробника */
    __u64 consumer;     /* Зсув до атомарного індексу споживача */
    __u64 descriptors;  /* Зсув до масиву дескрипторів кадру */
    __u64 flags;        /* Зсув до прапорців стану кільця (наприклад, XDP_RING_NEED_WAKEUP) */
};

struct xdp_mmap_offsets {
    struct xdp_ring_offset rx;
    struct xdp_ring_offset tx;
    struct xdp_ring_offset fr; /* Fill Ring */
    struct xdp_ring_offset cr; /* Completion Ring */
};
```

Отримавши зсуви полів, додаток відображає кільцеві буфери через `mmap()`:
- `Fill Ring` та `Completion Ring` відображаються з відносною константою `XDP_UMEM_PGOFF`.
- `RX Ring` та `TX Ring` відображаються з відносною константою `XDP_PGOFF`.

Формат дескриптора пакета в RX та TX кільцях визначається структурою `struct xdp_desc`:

```c
struct xdp_desc {
    __u64 addr;     /* Зсув кадру в межах UMEM (байтове зміщення) */
    __u32 len;      /* Довжина пакетних даних у байтах */
    __u32 options;  /* Прапорці дескриптора (наприклад, XDP_PKT_CONTD для jumboframes) */
};
```

Поле `addr` містить зсув від початку UMEM плюс можливий зсув headroom. Поле `len` вказує точний розмір прийнятого або відправляємого пакета. Поле `options` використовується в нових ядрах для підтримки мульти-кадрових пакетів (Jumbo frames / SG XDP), де прапорець `XDP_PKT_CONTD` сигналізує про те, що пакет продовжується у наступному дескрипторі.

## Прив'язка сокета: struct sockaddr_xdp

Остаточним кроком ініціалізації є виклик `bind()`, який прив'язує сокет AF_XDP до конкретного мережевого інтерфейсу та його черги (Queue ID).

Структура прив'язки `struct sockaddr_xdp` передається у виклик `bind()`:

```c
struct sockaddr_xdp {
    __u16 sxdp_family;         /* AF_XDP */
    __u16 sxdp_flags;          /* Прапорці режиму роботи сокета */
    __u32 sxdp_ifindex;        /* Індекс мережевого інтерфейсу (if_nametoindex) */
    __u32 sxdp_queue_id;       /* Номер черги RX/TX мережевої карти (0..N-1) */
    __u32 sxdp_shared_umem_fd; /* FD сокета-власника UMEM (при XDP_SHARED_UMEM) */
};
```

### Детальний опис прапорців `sxdp_flags`:

| Прапорець | Детальний опис та призначення |
| :--- | :--- |
| `XDP_SHARED_UMEM` | Дозволяє декільком сокетам AF_XDP використовувати одну спільну область пам'яті UMEM. При цьому перший сокет створює UMEM, а наступні сокети передають його FD у полі `sxdp_shared_umem_fd`. |
| `XDP_COPY` | Примусово вмикає режим копіювання даних через `skb`. Використовується для тестування або коли драйвер NIC не підтримує родний Zero-Copy. |
| `XDP_ZEROCOPY` | Вимагає прямого доступ до DMA мережевої карти без копіювання ЦП. Якщо драйвер NIC не підтримує Zero-Copy, виклик `bind()` повертає помилку `EOPNOTSUPP`. |
| `XDP_USE_NEED_WAKEUP` | Вмикає механізм економії ЦП: ядро встановлює біт `XDP_RING_NEED_WAKEUP` у кільцях лише тоді, коли драйвер заснув і вимагає системного виклику `sendto()`/`poll()`. |

Приклад зв'язування сокета з чергою мережевої карти:

:::tabs
```c
#include <sys/socket.h>
#include <net/if.h>
#include <linux/if_xdp.h>
#include <stdio.h>
#include <string.h>

int bind_xsk(int xsk_fd, const char *ifname, uint32_t queue_id, uint16_t flags) {
    uint32_t ifindex = if_nametoindex(ifname);
    if (ifindex == 0) {
        perror("if_nametoindex failed");
        return -1;
    }

    struct sockaddr_xdp sxdp;
    memset(&sxdp, 0, sizeof(sxdp));
    sxdp.sxdp_family = AF_XDP;
    sxdp.sxdp_ifindex = ifindex;
    sxdp.sxdp_queue_id = queue_id;
    sxdp.sxdp_flags = flags;

    if (bind(xsk_fd, (struct sockaddr *)&sxdp, sizeof(sxdp)) < 0) {
        perror("bind(AF_XDP) failed");
        return -1;
    }

    return 0;
}
```
```cpp
#include <sys/socket.h>
#include <net/if.h>
#include <linux/if_xdp.h>
#include <system_error>
#include <string_view>
#include <cstring>

void bind_xsk_cpp(int xsk_fd, std::string_view ifname, uint32_t queue_id, uint16_t flags) {
    uint32_t ifindex = ::if_nametoindex(ifname.data());
    if (ifindex == 0) {
        throw std::system_error(errno, std::generic_category(), "if_nametoindex failed");
    }

    struct sockaddr_xdp sxdp{};
    sxdp.sxdp_family = AF_XDP;
    sxdp.sxdp_ifindex = ifindex;
    sxdp.sxdp_queue_id = queue_id;
    sxdp.sxdp_flags = flags;

    if (::bind(xsk_fd, reinterpret_cast<struct sockaddr*>(&sxdp), sizeof(sxdp)) < 0) {
        throw std::system_error(errno, std::generic_category(), "bind(AF_XDP) failed");
    }
}
```
:::

Коли виклик `bind()` виконується успішно, ядро створює прив'язку між сокетом та апаратною чергою NIC. З цього моменту eBPF-програма може перенаправляти кадри з цієї черги у даний сокет за допомогою карти `BPF_MAP_TYPE_XSKMAP`.

## Вищорівневі обгортки libxdp / libbpf

Для уникнення ручного обчислення зсувів `mmap()` та виконання низькорівневих бар'єрів пам'яті використовується бібліотека `libxdp` (або `libbpf`, заголовок `<xdp/xsk.h>`). Вона надає готові функції для створення та керування кільцевими буферами:

```c
/* Створення об'єкта UMEM */
int xsk_umem__create(struct xsk_umem **umem,
                     void *umem_area, uint64_t size,
                     struct xsk_ring_prod *fill,
                     struct xsk_ring_cons *comp,
                     const struct xsk_umem_config *config);

/* Створення та прив'язка сокета AF_XDP */
int xsk_socket__create(struct xsk_socket **xsk,
                       const char *ifname, uint32_t queue_id,
                       struct xsk_umem *umem,
                       struct xsk_ring_cons *rx,
                       struct xsk_ring_prod *tx,
                       const struct xsk_socket_config *config);
```

### Допоміжні inline-функції маніпулювання індексами:

- `xsk_ring_prod__reserve(prod, nb, &idx)`: зарезервувати `nb` позицій у кільці виробника (Fill або TX). Повертає початковий індекс `idx`.
- `xsk_ring_prod__submit(prod, nb)`: атомарно оновити індекс виробника, роблячи `nb` нових записів доступними для споживача.
- `xsk_ring_cons__peek(cons, nb, &idx)`: зчитати до `nb` доступних записів із кільця споживача (RX або Completion).
- `xsk_ring_cons__release(cons, nb)`: звільнити `nb` зчитаних записів у кільці споживача, просуваючи індекс споживання.
- `xsk_ring_prod__needs_wakeup(prod)`: перевірити, чи встановило ядро біт `XDP_RING_NEED_WAKEUP` для даного кільця.
