# Практичний проєкт: XDP-маршрутизатор на базі CPUMAP та DEVMAP

У цьому практичному проєкті розглядається повна реалізація високопродуктивного L2/L3 XDP-маршрутизатора. Система приймає кадри на вхідному мережевому інтерфейсі, модифікує MAC-адреси заголовка Ethernet (L2 rewrite), розподіляє трафік між ядрами ЦП за допомогою `BPF_MAP_TYPE_CPUMAP` та перенаправляє пакети у вихідний мережевий порт за допомогою `BPF_MAP_TYPE_DEVMAP`.

Головна мета проєкту — продемонструвати на практиці побудову монолітного високопродуктивного маршрутизатора, який обходить стандартний L3-стек Linux для прискореної переадресації кадра, але зберігає можливість розпаралелювання обробки складного трафіку між ядрами процесора.

Проєкт складається з двох ключових компонентів:
1. **eBPF-програма ядра (`xdp_router_kern.c`):** Завантажується у драйвер мережевої карти, виконує аналіз заголовків пакетів, редагує MAC-адреси та викликає `bpf_redirect_map()`.
2. **Програма управління простору користувача (`loader`):** Створює BPF-карти, конфігурує цільові CPU та вихідні мережеві пристрої, завантажує eBPF-байткод у ядро та прив'язує його до мережевого інтерфейсу за допомогою бібліотеки `libbpf`.

---

## 1. Архітектурний розбір eBPF-програми ядра (`xdp_router_kern.c`)

Програма ядра виконується безпосередньо у драйвері мережевої карти для кожного вхідного кадра `struct xdp_md`.

У програмі оголошуються дві BPF-карти:
- `cpu_map` типу `BPF_MAP_TYPE_CPUMAP` для перенаправлення парних IP-адрес на ядро ЦП 1.
- `tx_dev_map` типу `BPF_MAP_TYPE_DEVMAP` для прямого виводу непарних IP-адрес на мережевий порт з `ifindex = 2`.

Кожен вхідний кадр проходить строгу перевірку меж пам'яті (bounds checking) для задоволення вимог BPF Verifier. Програма спочатку перевіряє розмір Ethernet-заголовка, перевіряє поле `h_proto` на відповідність IPv4 (`ETH_P_IP`), після чого аналізує IPv4-заголовок. 

Для непарних IP-адрес виконується L2 rewrite — заміна вихідної та цільової MAC-адрес у спині Ethernet-кадра — після чого викликається `bpf_redirect_map()`. Заміна MAC-адрес виконується безпосередньо в бафері кадра за допомогою вбудованої функції `__builtin_memcpy()`, що гарантує високу інлайн-оптимізацію компілятором LLVM/Clang.

Перевірка меж пам'яті видається невід'ємною частиною коду BPF. Оскільки статичний аналізатор ядра (BPF Verifier) перевіряє кожну інструкцію на потенційний вихід за межі виділеної сторінки, будь-яке звернення до полів `eth->h_proto` чи `iph->saddr` без попередньої перевірки умов `(void*)(hdr + 1) > data_end` призведе до відхилення завантаження програми верифікатором ядра із помилкою `invalid access to packet memory`.

Для конвертації мережевого порядкового байтів (Big-Endian) у хостовий порядок байтів (Host Endianness) використовуються макроси `bpf_htons()` та `bpf_ntohl()`, які гарантують коректне обчислення IP-адрес та портів на архітектурах x86_64 та ARM64.

Крім того, при використанні `bpf_redirect_map()` для `tx_dev_map` у якості третього аргументу передається прапор `XDP_ABORTED`. Це означає, що якщо цільовий мережевий пристрій з `ifindex = 2` видалений з системи або його драйвер тимчасово вимкнено, ядро не буде передавати пакет у стандартний мережевий стек, а моментально відкине його зі згенерованою подією трасування `xdp_redirect_err`.

```c
#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/in.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_endian.h>

/* BPF-карта CPUMAP для розпаралелювання обробки між ядрами */
struct {
    __uint(type, BPF_MAP_TYPE_CPUMAP);
    __uint(max_entries, 64);
    __type(key, __u32);   /* cpu_id */
    __type(value, struct bpf_cpumap_val);
} cpu_map SEC(".maps");

/* BPF-карта DEVMAP для прямого виводу кадра в TX-інтерфейс */
struct {
    __uint(type, BPF_MAP_TYPE_DEVMAP);
    __uint(max_entries, 256);
    __type(key, __u32);   /* ifindex */
    __type(value, struct bpf_devmap_val);
} tx_dev_map SEC(".maps");

/* Допоміжна функція L2 rewrite (заміна MAC-адрес) */
static __always_inline int rewrite_mac(struct xdp_md *ctx, unsigned char *src_mac, unsigned char *dst_mac)
{
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;
    struct ethhdr *eth = data;

    if ((void *)(eth + 1) > data_end)
        return -1;

    __builtin_memcpy(eth->h_dest, dst_mac, ETH_ALEN);
    __builtin_memcpy(eth->h_source, src_mac, ETH_ALEN);
    return 0;
}

SEC("xdp")
int xdp_router_entry(struct xdp_md *ctx)
{
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;
    struct ethhdr *eth = data;

    /* Перевірка меж пам'яті для BPF Verifier */
    if ((void *)(eth + 1) > data_end)
        return XDP_PASS;

    /* Працюємо лише з IP-пакетами */
    if (eth->h_proto != bpf_htons(ETH_P_IP))
        return XDP_PASS;

    struct iphdr *iph = (void *)(eth + 1);
    if ((void *)(iph + 1) > data_end)
        return XDP_PASS;

    /* Простий приклад балансування: парні IP на CPU 1, непарні на DEVMAP port 2 */
    __u32 src_ip = bpf_ntohl(iph->saddr);
    
    if (src_ip % 2 == 0) {
        /* Скеровуємо на CPU 1 через CPUMAP */
        __u32 target_cpu = 1;
        return bpf_redirect_map(&cpu_map, target_cpu, XDP_PASS);
    } else {
        /* L2 rewrite та пряме перенаправлення на eth1 (ifindex = 2) */
        unsigned char next_hop_mac[6] = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55};
        unsigned char src_port_mac[6] = {0x00, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE};

        if (rewrite_mac(ctx, src_port_mac, next_hop_mac) < 0)
            return XDP_DROP;

        __u32 target_ifindex = 2;
        return bpf_redirect_map(&tx_dev_map, target_ifindex, XDP_ABORTED);
    }
}

char _license[] SEC("license") = "GPL";
```

---

## 2. Програма простору користувача (Userspace Loader)

Програма простору користувача відповідає за підготовку середовища: вона перетворює назви мережевих пристроїв (наприклад, `eth0`, `eth1`) у системні індекси `ifindex` за допомогою системного виклику `if_nametoindex()`, завантажує компільований BPF-об'єкт `xdp_router_kern.o` у ядро Linux via `libbpf`, знаходить BPF-карти за їхніми іменами та записує конфігураційні структури `bpf_cpumap_val` та `bpf_devmap_val`.

Після налаштування карт завантажувач прив'язує BPF-програму `xdp_router_entry` до вхідного мережевого порту за допомогою функції `bpf_xdp_attach()`.

Нижче наведено імплементації завантажувача мовами C та C++.

У версії на C++ реалізовано шаблони безпечного управління ресурсами RAII за допомогою `std::unique_ptr` із власним видалячем `BpfObjectDeleter`, який гарантує автоматичне відкріплення XDP-програми та закриття файлових дескрипторів при виході з зони видимості чи при виникненні винятків. 

Класичне C-програмування з `libbpf` вимагає ручного виклику `bpf_object__close()` та відкріплення XDP-програми через `bpf_xdp_detach()` у кожній гілці обробки помилок. C++ імплементація вирішує цю проблему за допомогою паттерна RAII: деструктор `XdpRouterManager` автоматично перевіряє факт прикріплення програми та безпечно відкріплює її від мережевого інтерфейсу при виході з обгортки. Крім того, завантажувач C++ використовує типи стандартної бібліотеки C++20, такі як `std::string_view` для уникнення зайвого виділення пам'яті під рядкові аргументи та `std::chrono` для організації точно вимірюваних циклів очікування.

Використання `std::runtime_error` у C++ версії забезпечує вичерпну передачу контексту помилок наверх по стеку викликів без ризику витоку системних дескрипторів BPF.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <net/if.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

int main(int argc, char **argv)
{
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <rx_ifname> <tx_ifname>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *rx_ifname = argv[1];
    const char *tx_ifname = argv[2];

    unsigned int rx_ifindex = if_nametoindex(rx_ifname);
    unsigned int tx_ifindex = if_nametoindex(tx_ifname);

    if (!rx_ifindex || !tx_ifindex) {
        perror("Не вдалося отримати ifindex для мережевих інтерфейсів");
        return EXIT_FAILURE;
    }

    /* Відкриття та завантаження BPF-об'єкта */
    struct bpf_object *obj = bpf_object__open_file("xdp_router_kern.o", NULL);
    if (!obj) {
        fprintf(stderr, "Помилка відкриття файлу bpf об'єкта\n");
        return EXIT_FAILURE;
    }

    if (bpf_object__load(obj)) {
        fprintf(stderr, "Помилка завантаження eBPF-програми у ядро\n");
        bpf_object__close(obj);
        return EXIT_FAILURE;
    }

    /* Отримання дескрипторів карт */
    int cpu_map_fd = bpf_object__find_map_fd_by_name(obj, "cpu_map");
    int dev_map_fd = bpf_object__find_map_fd_by_name(obj, "tx_dev_map");

    if (cpu_map_fd < 0 || dev_map_fd < 0) {
        fprintf(stderr, "Помилка знаходження BPF-карт\n");
        bpf_object__close(obj);
        return EXIT_FAILURE;
    }

    /* Конфігурація CPUMAP: налаштовуємо CPU ID 1 із розміром черги 2048 */
    struct bpf_cpumap_val cpu_val = {
        .qsize = 2048,
        .bpf_prog = {.fd = 0}
    };
    __u32 cpu_key = 1;
    if (bpf_map_update_elem(cpu_map_fd, &cpu_key, &cpu_val, BPF_ANY) < 0) {
        perror("Помилка оновлення елемента CPUMAP");
        bpf_object__close(obj);
        return EXIT_FAILURE;
    }

    /* Конфігурація DEVMAP: додаємо tx_ifindex у карту */
    struct bpf_devmap_val dev_val = {
        .ifindex = tx_ifindex,
        .bpf_prog = {.fd = 0}
    };
    __u32 dev_key = tx_ifindex;
    if (bpf_map_update_elem(dev_map_fd, &dev_key, &dev_val, BPF_ANY) < 0) {
        perror("Помилка оновлення елемента DEVMAP");
        bpf_object__close(obj);
        return EXIT_FAILURE;
    }

    /* Пошук XDP-програми та прив'язка до RX-інтерфейсу */
    struct bpf_program *prog = bpf_object__find_program_by_name(obj, "xdp_router_entry");
    int prog_fd = bpf_program__fd(prog);

    DECLARE_LIBBPF_OPTS(bpf_xdp_attach_opts, opts);
    if (bpf_xdp_attach(rx_ifindex, prog_fd, XDP_FLAGS_UPDATE_IF_NOEXIST, &opts) < 0) {
        perror("Помилка прикріплення XDP програми до інтерфейсу");
        bpf_object__close(obj);
        return EXIT_FAILURE;
    }

    printf("XDP-маршрутизатор успішно запущено на %s -> %s\n", rx_ifname, tx_ifname);
    printf("Натисніть Ctrl+C для зупинки...\n");

    while (1) {
        sleep(1);
    }

    /* Відкріплення XDP програми */
    bpf_xdp_detach(rx_ifindex, 0, &opts);
    bpf_object__close(obj);
    return EXIT_SUCCESS;
}
```

@tab C++
```cpp
#include <iostream>
#include <memory>
#include <string_view>
#include <stdexcept>
#include <chrono>
#include <thread>
#include <net/if.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

// RAII обгортка для bpf_object
struct BpfObjectDeleter {
    void operator()(bpf_object* obj) const noexcept {
        if (obj) {
            bpf_object__close(obj);
        }
    }
};

using BpfObjectPtr = std::unique_ptr<bpf_object, BpfObjectDeleter>;

class XdpRouterManager {
public:
    XdpRouterManager(std::string_view rx_ifname, std::string_view tx_ifname)
        : rx_ifname_(rx_ifname), tx_ifname_(tx_ifname) {
        
        rx_ifindex_ = if_nametoindex(rx_ifname_.data());
        tx_ifindex_ = if_nametoindex(tx_ifname_.data());

        if (rx_ifindex_ == 0 || tx_ifindex_ == 0) {
            throw std::runtime_error("Не вдалося знайти системний індекс мережевого інтерфейсу");
        }
    }

    void load_and_attach(std::string_view bpf_obj_path) {
        bpf_obj_.reset(bpf_object__open_file(bpf_obj_path.data(), nullptr));
        if (!bpf_obj_) {
            throw std::runtime_error("Неможливо відкрити файл BPF об'єкта");
        }

        if (bpf_object__load(bpf_obj_.get()) != 0) {
            throw std::runtime_error("Помилка завантаження eBPF програмою у ядро");
        }

        configure_maps();
        attach_xdp();
    }

    ~XdpRouterManager() {
        if (attached_ && rx_ifindex_ != 0) {
            DECLARE_LIBBPF_OPTS(bpf_xdp_attach_opts, opts);
            bpf_xdp_detach(rx_ifindex_, 0, &opts);
            std::cout << "[RAII] XDP програму відкріплено від інтерфейсу.\n";
        }
    }

private:
    void configure_maps() {
        int cpu_map_fd = bpf_object__find_map_fd_by_name(bpf_obj_.get(), "cpu_map");
        int dev_map_fd = bpf_object__find_map_fd_by_name(bpf_obj_.get(), "tx_dev_map");

        if (cpu_map_fd < 0 || dev_map_fd < 0) {
            throw std::runtime_error("Не знайдено необхідних карт CPUMAP чи DEVMAP");
        }

        // Конфігурація CPUMAP (цільовий CPU 1, qsize 2048)
        struct bpf_cpumap_val cpu_val{};
        cpu_val.qsize = 2048;
        cpu_val.bpf_prog.fd = 0;
        uint32_t cpu_key = 1;

        if (bpf_map_update_elem(cpu_map_fd, &cpu_key, &cpu_val, BPF_ANY) < 0) {
            throw std::runtime_error("Помилка ініціалізації елемента CPUMAP");
        }

        // Конфігурація DEVMAP (вихідний ifindex)
        struct bpf_devmap_val dev_val{};
        dev_val.ifindex = tx_ifindex_;
        dev_val.bpf_prog.fd = 0;
        uint32_t dev_key = tx_ifindex_;

        if (bpf_map_update_elem(dev_map_fd, &dev_key, &dev_val, BPF_ANY) < 0) {
            throw std::runtime_error("Помилка ініціалізації елемента DEVMAP");
        }
    }

    void attach_xdp() {
        bpf_program* prog = bpf_object__find_program_by_name(bpf_obj_.get(), "xdp_router_entry");
        if (!prog) {
            throw std::runtime_error("Не знайдено XDP-функцію xdp_router_entry у BPF-об'єкті");
        }

        int prog_fd = bpf_program__fd(prog);
        DECLARE_LIBBPF_OPTS(bpf_xdp_attach_opts, opts);

        if (bpf_xdp_attach(rx_ifindex_, prog_fd, XDP_FLAGS_UPDATE_IF_NOEXIST, &opts) < 0) {
            throw std::runtime_error("Помилка прив'язки XDP програми до вхідного мережевого порту");
        }

        attached_ = true;
        std::cout << "Успішно запущено XDP-маршрутизатор [C++] (" << rx_ifname_ << " -> " << tx_ifname_ << ")\n";
    }

    std::string rx_ifname_;
    std::string tx_ifname_;
    unsigned int rx_ifindex_{0};
    unsigned int tx_ifindex_{0};
    BpfObjectPtr bpf_obj_{nullptr};
    bool attached_{false};
};

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <rx_ifname> <tx_ifname>\n";
        return EXIT_FAILURE;
    }

    try {
        XdpRouterManager router(argv[1], argv[2]);
        router.load_and_attach("xdp_router_kern.o");

        std::cout << "Маршрутизатор працює. Натисніть Ctrl+C для завершення...\n";
        while (true) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

---

## 3. Збірка, тестування та перевірка результатів

Для компіляції eBPF-програми та користувацьких завантажувачів потрібні утиліти `clang`, `llvm` та системні заголовки `libbpf`:

```bash
# 1. Компіляція eBPF програмою під цільову архітектуру bpf
clang -O2 -g -target bpf -c xdp_router_kern.c -o xdp_router_kern.o

# 2. Компіляція C завантажувача
gcc -O2 loader.c -o loader_c -lbpf

# 3. Компіляція C++ завантажувача
g++ -O2 -std=c++20 loader.cpp -o loader_cpp -lbpf

# 4. Створення віртуальної мережевої тестової пари veth
sudo ip link add veth0 type veth peer name veth1
sudo ip link set dev veth0 up
sudo ip link set dev veth1 up

# 5. Запуск маршрутизатора між veth0 та veth1
sudo ./loader_cpp veth0 veth1
```

Після успішного запуску програма переходить у цикл очікування. У цей момент ви можете генерувати тестовий трафік (наприклад, за допомогою `ping` або `iperf3`) та відстежувати передачу пакетів через `bpftool map dump` та перевіряти лічильники перенаправлених кадрів через `ethtool -S veth1 | grep xdp_xmit`.

При виконанні тестування у віртуальному середовищі з пристроями `veth` рекомендується переконатися, що прапорець Generic XDP не використовується примусово, оскільки сучасне ядро Linux повністю підтримує метод `ndo_xdp_xmit` для пар `veth`.

При виникненні помилок типу `EOPNOTSUPP` переконайтеся, що віртуальний або фізичний драйвер підтримує `Native XDP` та метод `ndo_xdp_xmit`. Для віртуальних інтерфейсів `veth` підтримка `ndo_xdp_xmit` присутня у сучасних версіях ядра Linux. Якщо ви тестуєте програму на фізичній мережевій карті, перевірте версію ядра та наявність підтримки XDP redirection у драйвері адаптера.
