# ⚙️ Практичний обробник пакетів на AF_XDP та eBPF

Цей проєкт демонструє повну реалізацію високошвідкісного обробника кадрів (Echo-сервера на рівні L2/L3), який комбінує ядрову програму eBPF XDP для перенаправлення трафіку та користувацький додаток на AF_XDP для зчитування і повернення кадрів без копіювання (Zero-Copy).

Архітектура обробника складається з двох ключових частин:

1. **Компонент ядра (eBPF XDP):** завантажується на рівні драйвера мережевої карти. Програма перехоплює кожен надхідний Ethernet-кадр до того, як для нього буде виділено структуру `sk_buff`. Вона перевіряє номер RX-черги кадру і шукає відповідний файловий дескриптор сокета в карті `BPF_MAP_TYPE_XSKMAP`. Якщо сокет підключено, вона перенаправляє пакет через `bpf_redirect_map()`.
2. **Компонент простору користувача (C / C++):** виділяє сторінково-вирівняний буфер UMEM, створює сокет AF_XDP, конфігурує чотири кільцеві буфери (Fill, RX, TX, Completion), реєструє сокет у карті XSKMAP та запускає нескінченний цикл обробки кадрів.

## 1. Програма eBPF XDP (Ядро Linux)

Програма eBPF завантажується на мережевий інтерфейс і перехоплює кадри на рівні драйвера. Вона шукає відповідну чергу в карті `BPF_MAP_TYPE_XSKMAP` і повертає `XDP_REDIRECT`.

Нижче наведено повний вихідний код програми ядра `xdp_redirect_kern.c`:

```c
// xdp_redirect_kern.c
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <linux/if_ether.h>
#include <linux/ip.h>

struct {
    __uint(type, BPF_MAP_TYPE_XSKMAP);
    __uint(max_entries, 64);
    __type(key, int);
    __type(value, int);
} xsks_map SEC(".maps");

SEC("xdp")
int xdp_redirect_xsk(struct xdp_md *ctx) {
    int rx_queue_index = ctx->rx_queue_index;

    // Перевіряємо, чи є підключений сокет AF_XDP для цієї черги
    if (bpf_map_lookup_elem(&xsks_map, &rx_queue_index)) {
        return bpf_redirect_map(&xsks_map, rx_queue_index, 0);
    }

    // Якщо сокет відсутній, передаємо пакет стандартному стеку ядра
    return XDP_PASS;
}

char _license[] SEC("license") = "GPL";
```

### Пояснення роботи eBPF програми:
- `ctx->rx_queue_index`: поле структури `struct xdp_md`, яке містить апаратний номер черги RX мережевої карти, з якої надійшов даний пакет.
- `BPF_MAP_TYPE_XSKMAP`: спеціальна BPF-карта, масив якої індексується номерами черг, а значеннями є файлові дескриптори сокетів AF_XDP.
- `bpf_redirect_map(&xsks_map, rx_queue_index, 0)`: ядра функція, яка виконує швидкий редирект кадру в сокет AF_XDP. Якщо у Fill Ring сокета є вільний кадр UMEM, ядро копіює/DMA-шить пакет туди і повертає `XDP_REDIRECT`. Якщо у Fill Ring немає кадрів, пакет буде відкинуто.
- `XDP_PASS`: якщо для даної черги сокет AF_XDP не зареєстровано, програма повертає `XDP_PASS`, що спрямовує пакет до стандартного мережевого стеку Linux (`sk_buff` / IP / TCP stack).

## 2. Додаток простору користувача (User Space Control Plane & Loop)

Додаток виділяє UMEM, налаштовує кільця Fill, Completion, RX та TX, ініціалізує сокет AF_XDP, заповнює карту XSKMAP та запускає цикл обробки пакетів.

Обробка пакетів у просторі користувача відбувається за такими кроками:

1. **Ініціалізація пам'яті UMEM:** виділяється масив пам'яті розміром `NUM_FRAMES * FRAME_SIZE` за допомогою `posix_memalign()`. Початкова адреса має бути вирівняна на розмір сторінки пам'яті (4096 байтів). Це вирівнювання є обов'язковим для коректного виконання реєстрації UMEM у ядрі.
2. **Первинне поповнення Fill Ring:** перед початком роботи додаток мусить заповнити принаймні половину Fill Ring адресами вільних кадрів UMEM. Без цього драйвер мережевої карти не матиме буферів для прийому перших пакетів і буде змушений їх відкидати.
3. **Пакетний цикл (Batching Loop):**
   - Додаток викликає `xsk_ring_cons__peek(&rx, BATCH_SIZE, &rx_idx)` для перевірки наявності нових прийнятих дескрипторів у RX-кільці.
   - Для кожного прийнятого кадру додаток отримує його адресовий зсув `addr` у межах UMEM та довжину пакета `len`.
   - За допомогою `xsk_umem__get_data(buffer, addr)` додаток отримує безпосередній вказівник на Ethernet-кадр у пам'яті ОЗП.
   - Додаток виконує обробку (у наведеному прикладі — L2 Swap: переставлення місцями Destination MAC та Source MAC адрес).
   - Додаток резервує місця у TX-кільці за допомогою `xsk_ring_prod__reserve(&tx, rcvd, &tx_idx)` і передає туди оброблені дескриптори кадрів.
   - Додаток сповіщає ядро викликом `xsk_ring_prod__submit(&tx, rcvd)`. Якщо увімкнено прапорець `XDP_USE_NEED_WAKEUP`, додаток перевіряє `xsk_ring_prod__needs_wakeup()` і за потреби викликає `xsk_socket__wakeup()`.
   - Звільнені кадри з Completion Ring повертаються у Fill Ring для повторного вжитку під нові прийоми.

Нижче наведено повні ідіоматичні реалізації компонента простору користувача мовами C та C++:

:::tabs
```c
// xsk_app.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <poll.h>
#include <sys/mman.h>
#include <net/if.h>
#include <linux/if_xdp.h>
#include <xdp/xsk.h>

#define NUM_FRAMES 4096
#define FRAME_SIZE 2048
#define BATCH_SIZE 64

static volatile int global_running = 1;

static void sig_handler(int sig) {
    (void)sig;
    global_running = 0;
}

struct xsk_app {
    struct xsk_umem *umem;
    struct xsk_ring_prod fill;
    struct xsk_ring_cons comp;
    struct xsk_ring_cons rx;
    struct xsk_ring_prod tx;
    struct xsk_socket *xsk;
    void *buffer;
};

static int init_xsk_app(struct xsk_app *app, const char *ifname, uint32_t queue_id) {
    size_t umem_size = NUM_FRAMES * FRAME_SIZE;
    if (posix_memalign(&app->buffer, getpagesize(), umem_size) != 0) {
        perror("posix_memalign failed");
        return -1;
    }

    struct xsk_umem_config umem_cfg = {
        .fill_size = NUM_FRAMES,
        .comp_size = NUM_FRAMES,
        .frame_size = FRAME_SIZE,
        .frame_headroom = XSK_UMEM__DEFAULT_FRAME_HEADROOM,
        .flags = 0
    };

    if (xsk_umem__create(&app->umem, app->buffer, umem_size,
                         &app->fill, &app->comp, &umem_cfg) < 0) {
        perror("xsk_umem__create failed");
        free(app->buffer);
        return -1;
    }

    struct xsk_socket_config xsk_cfg = {
        .rx_size = NUM_FRAMES,
        .tx_size = NUM_FRAMES,
        .libbpf_flags = XSK_LIBBPF_FLAGS__INHIBIT_PROG_LOAD,
        .xdp_flags = XDP_FLAGS_UPDATE_IF_NOEXIST,
        .bind_flags = XDP_ZEROCOPY | XDP_USE_NEED_WAKEUP
    };

    if (xsk_socket__create(&app->xsk, ifname, queue_id,
                           app->umem, &app->rx, &app->tx, &xsk_cfg) < 0) {
        // Якщо Zero-Copy не підтримується, спробуємо XDP_COPY
        xsk_cfg.bind_flags = XDP_COPY | XDP_USE_NEED_WAKEUP;
        if (xsk_socket__create(&app->xsk, ifname, queue_id,
                               app->umem, &app->rx, &app->tx, &xsk_cfg) < 0) {
            perror("xsk_socket__create failed");
            xsk_umem__delete(app->umem);
            free(app->buffer);
            return -1;
        }
    }

    // Первинне поповнення Fill Ring вільними адресами
    uint32_t idx = 0;
    if (xsk_ring_prod__reserve(&app->fill, NUM_FRAMES / 2, &idx) == NUM_FRAMES / 2) {
        for (int i = 0; i < NUM_FRAMES / 2; i++) {
            *xsk_ring_prod__fill_addr(&app->fill, idx + i) = i * FRAME_SIZE;
        }
        xsk_ring_prod__submit(&app->fill, NUM_FRAMES / 2);
    }

    return 0;
}

static void process_packets(struct xsk_app *app) {
    uint32_t rx_idx = 0, tx_idx = 0, comp_idx = 0, fill_idx = 0;
    
    uint32_t rcvd = xsk_ring_cons__peek(&app->rx, BATCH_SIZE, &rx_idx);
    if (!rcvd) {
        if (xsk_ring_prod__needs_wakeup(&app->fill)) {
            struct pollfd fds = { .fd = xsk_socket__fd(app->xsk), .events = POLLIN };
            poll(&fds, 1, 10);
        }
        return;
    }

    // Резервуємо місця в TX кільці для ехо-відповіді
    uint32_t tx_reserved = xsk_ring_prod__reserve(&app->tx, rcvd, &tx_idx);
    while (tx_reserved < rcvd) {
        if (xsk_ring_prod__needs_wakeup(&app->tx)) {
            xsk_socket__wakeup(app->xsk, XDP_WAKEUP_TX);
        }
        tx_reserved = xsk_ring_prod__reserve(&app->tx, rcvd, &tx_idx);
    }

    for (uint32_t i = 0; i < rcvd; i++) {
        const struct xdp_desc *desc = xsk_ring_cons__rx_desc(&app->rx, rx_idx + i);
        uint64_t addr = desc->addr;
        uint32_t len = desc->len;

        // Отримуємо вказівник на кадр
        uint8_t *pkt = (uint8_t *)xsk_umem__get_data(app->buffer, addr);

        // Переставляємо MAC-адреси місцями (L2 Swap Echo)
        uint8_t tmp_mac[6];
        memcpy(tmp_mac, pkt, 6);
        memcpy(pkt, pkt + 6, 6);
        memcpy(pkt + 6, tmp_mac, 6);

        // Вміщуємо в TX кільце
        struct xdp_desc *tx_desc = xsk_ring_prod__tx_desc(&app->tx, tx_idx + i);
        tx_desc->addr = addr;
        tx_desc->len = len;
    }

    xsk_ring_cons__release(&app->rx, rcvd);
    xsk_ring_prod__submit(&app->tx, rcvd);

    // Звільнення повернених кадрів з Completion Ring
    uint32_t completed = xsk_ring_cons__peek(&app->comp, BATCH_SIZE, &comp_idx);
    if (completed > 0) {
        uint32_t fill_res = xsk_ring_prod__reserve(&app->fill, completed, &fill_idx);
        if (fill_res == completed) {
            for (uint32_t i = 0; i < completed; i++) {
                uint64_t freed_addr = *xsk_ring_cons__comp_addr(&app->comp, comp_idx + i);
                *xsk_ring_prod__fill_addr(&app->fill, fill_idx + i) = freed_addr;
            }
            xsk_ring_prod__submit(&app->fill, completed);
        }
        xsk_ring_cons__release(&app->comp, completed);
    }
}

int main(int argc, char **argv) {
    if (argc < 3) {
        printf("Usage: %s <ifname> <queue_id>\n", argv[0]);
        return 1;
    }

    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    struct xsk_app app;
    memset(&app, 0, sizeof(app));

    if (init_xsk_app(&app, argv[1], atoi(argv[2])) < 0) {
        return 1;
    }

    printf("AF_XDP Echo Server running on %s queue %s...\n", argv[1], argv[2]);

    while (global_running) {
        process_packets(&app);
    }

    printf("Shutting down...\n");
    xsk_socket__delete(app.xsk);
    xsk_umem__delete(app.umem);
    free(app.buffer);

    return 0;
}
```
```cpp
// xsk_app.cpp
#include <iostream>
#include <memory>
#include <vector>
#include <system_error>
#include <csignal>
#include <cstring>
#include <unistd.h>
#include <poll.h>
#include <sys/mman.h>
#include <net/if.h>
#include <linux/if_xdp.h>
#include <xdp/xsk.h>
#include <span>

static volatile std::sig_atomic_t g_running = 1;

static void handle_signal(int) {
    g_running = 0;
}

class AfXdpEchoEngine {
    static constexpr size_t kNumFrames = 4096;
    static constexpr size_t kFrameSize = 2048;
    static constexpr size_t kBatchSize = 64;

    void* buffer_{nullptr};
    size_t buffer_size_{kNumFrames * kFrameSize};
    
    struct xsk_umem* umem_{nullptr};
    struct xsk_ring_prod fill_{};
    struct xsk_ring_cons comp_{};
    struct xsk_ring_cons rx_{};
    struct xsk_ring_prod tx_{};
    struct xsk_socket* xsk_{nullptr};

public:
    AfXdpEchoEngine(std::string_view ifname, uint32_t queue_id) {
        if (posix_memalign(&buffer_, getpagesize(), buffer_size_) != 0) {
            throw std::bad_alloc();
        }

        struct xsk_umem_config umem_cfg{};
        umem_cfg.fill_size = kNumFrames;
        umem_cfg.comp_size = kNumFrames;
        umem_cfg.frame_size = kFrameSize;
        umem_cfg.frame_headroom = XSK_UMEM__DEFAULT_FRAME_HEADROOM;
        umem_cfg.flags = 0;

        if (xsk_umem__create(&umem_, buffer_, buffer_size_, &fill_, &comp_, &umem_cfg) < 0) {
            ::free(buffer_);
            throw std::system_error(errno, std::generic_category(), "xsk_umem__create failed");
        }

        struct xsk_socket_config xsk_cfg{};
        xsk_cfg.rx_size = kNumFrames;
        xsk_cfg.tx_size = kNumFrames;
        xsk_cfg.libbpf_flags = XSK_LIBBPF_FLAGS__INHIBIT_PROG_LOAD;
        xsk_cfg.xdp_flags = XDP_FLAGS_UPDATE_IF_NOEXIST;
        xsk_cfg.bind_flags = XDP_ZEROCOPY | XDP_USE_NEED_WAKEUP;

        if (xsk_socket__create(&xsk_, ifname.data(), queue_id, umem_, &rx_, &tx_, &xsk_cfg) < 0) {
            xsk_cfg.bind_flags = XDP_COPY | XDP_USE_NEED_WAKEUP;
            if (xsk_socket__create(&xsk_, ifname.data(), queue_id, umem_, &rx_, &tx_, &xsk_cfg) < 0) {
                xsk_umem__delete(umem_);
                ::free(buffer_);
                throw std::system_error(errno, std::generic_category(), "xsk_socket__create failed");
            }
        }

        // Поповнюємо Fill Ring початковими кадрами
        uint32_t idx = 0;
        if (xsk_ring_prod__reserve(&fill_, kNumFrames / 2, &idx) == kNumFrames / 2) {
            for (size_t i = 0; i < kNumFrames / 2; ++i) {
                *xsk_ring_prod__fill_addr(&fill_, idx + i) = i * kFrameSize;
            }
            xsk_ring_prod__submit(&fill_, kNumFrames / 2);
        }
    }

    ~AfXdpEchoEngine() {
        if (xsk_) xsk_socket__delete(xsk_);
        if (umem_) xsk_umem__delete(umem_);
        if (buffer_) ::free(buffer_);
    }

    AfXdpEchoEngine(const AfXdpEchoEngine&) = delete;
    AfXdpEchoEngine& operator=(const AfXdpEchoEngine&) = delete;

    void process_single_batch() {
        uint32_t rx_idx = 0, tx_idx = 0, comp_idx = 0, fill_idx = 0;

        uint32_t rcvd = xsk_ring_cons__peek(&rx_, kBatchSize, &rx_idx);
        if (!rcvd) {
            if (xsk_ring_prod__needs_wakeup(&fill_)) {
                struct pollfd pfd{.fd = xsk_socket__fd(xsk_), .events = POLLIN, .revents = 0};
                ::poll(&pfd, 1, 10);
            }
            return;
        }

        uint32_t tx_reserved = xsk_ring_prod__reserve(&tx_, rcvd, &tx_idx);
        while (tx_reserved < rcvd) {
            if (xsk_ring_prod__needs_wakeup(&tx_)) {
                xsk_socket__wakeup(xsk_, XDP_WAKEUP_TX);
            }
            tx_reserved = xsk_ring_prod__reserve(&tx_, rcvd, &tx_idx);
        }

        for (uint32_t i = 0; i < rcvd; ++i) {
            const struct xdp_desc* desc = xsk_ring_cons__rx_desc(&rx_, rx_idx + i);
            uint64_t addr = desc->addr;
            uint32_t len = desc->len;

            auto frame_data = std::span<uint8_t>(
                static_cast<uint8_t*>(xsk_umem__get_data(buffer_, addr)), len
            );

            if (frame_data.size() >= 12) {
                // L2 MAC Swap
                std::swap_ranges(frame_data.begin(), frame_data.begin() + 6, frame_data.begin() + 6);
            }

            struct xdp_desc* tx_desc = xsk_ring_prod__tx_desc(&tx_, tx_idx + i);
            tx_desc->addr = addr;
            tx_desc->len = len;
        }

        xsk_ring_cons__release(&rx_, rcvd);
        xsk_ring_prod__submit(&tx_, rcvd);

        // Повернення оброблених кадрів з Completion Ring у Fill Ring
        uint32_t completed = xsk_ring_cons__peek(&comp_, kBatchSize, &comp_idx);
        if (completed > 0) {
            if (xsk_ring_prod__reserve(&fill_, completed, &fill_idx) == completed) {
                for (uint32_t i = 0; i < completed; ++i) {
                    uint64_t freed_addr = *xsk_ring_cons__comp_addr(&comp_, comp_idx + i);
                    *xsk_ring_prod__fill_addr(&fill_, fill_idx + i) = freed_addr;
                }
                xsk_ring_prod__submit(&fill_, completed);
            }
            xsk_ring_cons__release(&comp_, completed);
        }
    }

    void run() {
        while (g_running) {
            process_single_batch();
        }
    }
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <ifname> <queue_id>\n";
        return 1;
    }

    std::signal(SIGINT, handle_signal);
    std::signal(SIGTERM, handle_signal);

    try {
        AfXdpEchoEngine engine(argv[1], std::stoul(argv[2]));
        std::cout << "C++ AF_XDP Engine running on " << argv[1] << "...\n";
        engine.run();
    } catch (const std::exception& ex) {
        std::cerr << "Fatal error: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
```
:::

## 3. Розбір проблемних ситуацій та діагностика помилок

Під час експлуатації додатка AF_XDP у промисловому середовищі можуть виникати такі типові проблеми:

1. **Голодування Fill Ring (Fill Ring Starvation):**
   Якщо користувацький додаток затримує обробку кадрів і не повертає адреси у Fill Ring, драйвер мережевої карти вичерпує вільні DMA-буфери. У цьому разі нові надхідні кадри відкидаються мережевою картою, а в лічильниках `ethtool -S` або `/sys/class/net/<ifname>/statistics/rx_dropped` зростає значення помилок. Для вирішення слід збільшити розмір кілець (`NUM_FRAMES`) або оптимізувати процес обробки у користувацькому циклі.

2. **Витікання кадрів UMEM (Buffer Leak):**
   Якщо дескриптор кадру витягнуто з RX-кільця, але не відправлено у TX-кільце і не повернуто у Fill-кільце, цей кадр втрачається для системи до перезапуску додатка. Усі прийняті адреси кадрів мають суворо відстежуватися та повертатися у Fill Ring.

3. **Спад продуктивності через некоректну прив'язку CPU:**
   Якщо потік додатка виконується на одному ядрі CPU, а переривання NAPI мережевої карти обробляються на іншому ядрі, між ними виникає суттєва затримка через передачу міжпроцесорних переривань (IPI) та скидання кешів L1/L2. Для запобігання цьому обов'язково налаштовується примусова прив'язка потоків та IRQ (`/proc/irq/<num>/smp_affinity`).

## 4. Компіляція, прив'язка та налаштування продуктивності

Для успішної збірки додатка необхідна наявність системних бібліотек `libxdp` та `libbpf` разом з відповідними заголовочними файлами розвитку (`libxdp-devel` / `libbpf-devel`).

Команди збірки компонента ядра та додатка простору користувача:

```bash
# 1. Компіляція eBPF програми у байткод BPF
clang -O2 -g -target bpf -c xdp_redirect_kern.c -o xdp_redirect_kern.o

# 2. Завантаження eBPF програми на мережевий інтерфейс eth0
bpftool prog load xdp_redirect_kern.o /sys/fs/bpf/xdp_redirect_app type xdp
bpftool net attach xdp id $(bpftool prog show pinned /sys/fs/bpf/xdp_redirect_app | awk '{print $1}' | tr -d ':') dev eth0

# 3. Компіляція додатка простору користувача (C)
gcc -O3 xsk_app.c -o xsk_app -lxdp -lbpf

# 4. Компіляція додатка простору користувача (C++)
g++ -O3 -std=c++20 xsk_app.cpp -o xsk_app_cpp -lxdp -lbpf
```

### Оптимізація та налаштування системного середовища:

Для досягнення максимальної продуктивності обробника у режимі Zero-Copy (понад 10–14 Mpps на ядро) необхідно виконати кілька оптимізацій операційної системи:

1. **Прив'язка потоку до ядра CPU (CPU Affinity):**
   Потік обробки AF_XDP мусить виконуватися на тому самому ядрі ЦП, яке обробляє переривання NAPI даної черги мережевої карти. Це усуває перемикання контексту та інвалідацію L1/L2 кешів процесора:
   ```bash
   taskset -c 2 ./xsk_app eth0 0
   ```
2. **Збільшення глибини дескрипторних кілець мережевої карти:**
   За допомогою `ethtool` слід збільшити розміри апаратних кілець RX/TX до максимуму (наприклад, 4096):
   ```bash
   ethtool -G eth0 rx 4096 tx 4096
   ```
3. **Налаштування керування RSS (Receive Side Scaling):**
   Для багатопотокової обробки слід налаштувати таблицю індирекції RSS так, щоб окремі мережеві потоки рівномірно розподілялися між чергами NIC:
   ```bash
   ethtool -X eth0 equal 4
   ```
