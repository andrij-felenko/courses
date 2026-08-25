# ⚙️ Практична реалізація XDP-фільтра та Hairpin Router

Вставка демонструє практичну реалізацію високопродуктивного мережевого фільтра та маршрутизатора зворотного ходу (Hairpin Router) за допомогою eXpress Data Path (XDP). Наведено повний сирцевий код eBPF-програми мовою C, а також користувацьку програму управління (User Space Control Plane) мовами C та C++ у вкладках `:::tabs`.

---

## 1. Постановка задачі та архітектура рішення

При побудові сучасних високозавантажених мережевих вузлів часто виникає потреба обробляти різноманітні типи мережевого трафіку з мінімальними затримками (latency). Типовим прикладом є створення комбінованого сервісу, який повинен одночасно виконувати три завдання:

1. **Миттєво фільтрувати DDoS-атаки (Drop):** Відкидати небажаний або зловмисний трафік (наприклад, масовані UDP-флуди на певні сервісні порти) ще до того, как ядро виділить пам'ять під об'єкт `sk_buff`.
2. **Відповідати на діагностичні запити (Hairpin Bounce / TX):** Самостійно генерувати відповіді на перевірки доступності (ICMP Echo Request / ping) прямо з мережевої карти, повертаючи пакет назад у кабель з підміненими MAC та IP адресами без залучення мережевого стеку ядра.
3. **Пропускати легітимний трафік (Pass):** Усі інші пакети (наприклад, SSH, HTTP або BGP-трафік) прозоро передавати далі у стандартний стек ядра Linux для звичайної обробки сокетами додатків.

Для вирішення цього завдання ми напишемо два компоненти: eBPF-програму ядра (`xdp_prog.c`), яка завантажується безпосередньо у драйвер мережевої карти, та завантажувач у користувацькому просторі (User Space Control Plane), який контролює життєвий цикл eBPF-програми та прив'язує її до вибраного мережевого інтерфейсу.

---

## 2. Код eBPF-програми ядра (`xdp_prog.c`)

Нижче наведено сирцевий код eBPF-програми XDP. Зверніть увагу на використання допоміжних інлайнових функцій `swap_mac_addresses` та `swap_ip_addresses`, а також на обов'язкові перевірки меж (bounds checking) перед кожним зверненням до пам'яті пакету, які вимагаються верифікатором eBPF.

```c
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/icmp.h>
#include <linux/udp.h>
#include <linux/in.h>

/* Допоміжна функція для заміни місцями MAC-адрес у Ethernet-заголовку */
static __always_inline void swap_mac_addresses(struct ethhdr *eth) {
    unsigned char tmp[ETH_ALEN];
    __builtin_memcpy(tmp, eth->h_dest, ETH_ALEN);
    __builtin_memcpy(eth->h_dest, eth->h_source, ETH_ALEN);
    __builtin_memcpy(eth->h_source, tmp, ETH_ALEN);
}

/* Допоміжна функція для заміни місцями IP-адрес у IPv4-заголовку */
static __always_inline void swap_ip_addresses(struct iphdr *iph) {
    __be32 tmp = iph->saddr;
    iph->saddr = iph->daddr;
    iph->daddr = tmp;
}

SEC("xdp")
int xdp_router_filter(struct xdp_md *ctx) {
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;

    /* 1. Bounds check для Ethernet-заголовка */
    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end) {
        return XDP_PASS;
    }

    /* Перевіряємо, чи це IPv4 пакет */
    if (eth->h_proto != __builtin_htons(ETH_P_IP)) {
        return XDP_PASS;
    }

    /* 2. Bounds check для IP-заголовка */
    struct iphdr *iph = (void *)(eth + 1);
    if ((void *)(iph + 1) > data_end) {
        return XDP_PASS;
    }

    /* Перевірка випадків UDP трафіку */
    if (iph->protocol == IPPROTO_UDP) {
        struct udphdr *udph = (void *)iph + (iph->ihl * 4);
        if ((void *)(udph + 1) > data_end) {
            return XDP_PASS;
        }

        /* Якщо порт призначення 9999 — миттєво відкидаємо пакет (XDP_DROP) */
        if (udph->dest == __builtin_htons(9999)) {
            return XDP_DROP;
        }
    }

    /* Перевірка випадків ICMP Echo Request */
    if (iph->protocol == IPPROTO_ICMP) {
        struct icmphdr *icmph = (void *)iph + (iph->ihl * 4);
        if ((void *)(icmph + 1) > data_end) {
            return XDP_PASS;
        }

        /* Якщо це ICMP Echo Request (тип 8) */
        if (icmph->type == ICMP_ECHO) {
            /* Змінюємо тип на ICMP Echo Reply (тип 0) */
            icmph->type = ICMP_ECHOREPLY;
            
            /* Інкрементально оновлюємо контрольну суму ICMP (різниця типів 8 -> 0 дорівнює +0x0008) */
            icmph->checksum += 0x0008;

            /* Міняємо місцями джерело та призначення для MAC та IP */
            swap_mac_addresses(eth);
            swap_ip_addresses(iph);

            /* Відправляємо пакет назад через той самий мережевий адаптер (XDP_TX) */
            return XDP_TX;
        }
    }

    /* Усі інші пакети пропускаємо у стандартний стек ядра (XDP_PASS) */
    return XDP_PASS;
}

char _license[] SEC("license") = "GPL";
```

---

## 3. Детальний аналіз та крайові випадки обробки в eBPF

### 3.1. Генерація байткоду eBPF та верифікація меж

Коли компілятор Clang обробляє вирази вида `if ((void *)(eth + 1) > data_end)`, він генерує інструкції порівняння регістрів eBPF:

```assembly
; r1 містить вказівник ctx->data
; r2 містить вказівник ctx->data_end
r3 = r1
r3 += 14 ; Розмір struct ethhdr дорівнює 14 байт
if r3 > r2 goto +10 ; Перехід на відкидання або пропуск, якщо виходить за межі
```

Верифікатор ядра Linux під час завантаження простежує всі можливі гілки виконання (bounded execution paths). Якщо верифікатор виявить хоча б один шлях, на якому відбувається зчитування за адресою без попереднього порівняння `r3 > r2`, він відхилить програму з помилкою `invalid access to packet, off=14 size=1`.

### 3.2. Робота з динамічною довжиною IP-заголовка та опціями

У виразі `(void *)iph + (iph->ihl * 4)` використовується поле `ihl` (Internet Header Length) заголовка IPv4. Оскільки IPv4 заголовок може містити додаткові опції (Options), його довжина варіюється від 20 байт (`ihl = 5`) до 60 байт (`ihl = 15`).

Якщо зміщення обчислюється динамічно на основі значення з пакета, верифікатор ядра вимагає повторної перевірки меж `(void *)(udph + 1) > data_end`. Без цієї перевірки програма не пройде верифікацію, оскільки зловмисник може надіслати підроблений пакет із `ihl = 15`, де фактична довжина кадру менша за 60 байт.

### 3.3. Обчислення контрольної суми за RFC 1624

При зміні полів пакета (наприклад, типу ICMP з `ICMP_ECHO = 8` на `ICMP_ECHOREPLY = 0`) вимагається корекція контрольної суми (Checksum). Повне переобчислення контрольної суми за алгоритмом 16-бітного доповнення до одиниці (1's complement sum) вимагає проходу по всьому кадру.

Замість цього використовується формула інкрементального оновлення за RFC 1624:

```
HC' = ~(~HC + ~m + m')
```

Оскільки нове значення полів менше на 8 (`8 -> 0`), зворотнє значення контрольної суми збільшується на 8, що відповідає додаванню `0x0008` до поля `checksum`.

---

## 4. Користувацька програма управления (Control Plane)

Користувацька програма відповідає за відкриття зкомпільованого `.o` BPF-файла, завантаження байткоду в ядро за допомогою системного виклику `bpf()`, проведення перевірки верифікатором та прив'язку XDP-програми до вибраного мережевого інтерфейсу (наприклад, `eth0`).

Нижче наведено два ідіоматичних варіанти реалізації цієї програми: мовою C (з ручним управлінням ресурсами `libbpf`) та мовою C++20 (з використанням шаблону RAII для автоматичного відв'язування хука у деструкторі).

:::tabs
```c
/* C Implementation: Manual lifecycle management using libbpf C API */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <net/if.h>
#include <linux/if_link.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <interface> <path_to_bpf_obj>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *ifname = argv[1];
    const char *bpf_file = argv[2];

    /* Отримуємо числовий системний індекс мережевого інтерфейсу */
    unsigned int ifindex = if_nametoindex(ifname);
    if (ifindex == 0) {
        perror("Помилка if_nametoindex");
        return EXIT_FAILURE;
    }

    /* 1. Відкриваємо та завантажуємо BPF-об'єктний файл */
    struct bpf_object *obj = bpf_object__open_file(bpf_file, NULL);
    if (!obj) {
        fprintf(stderr, "Не вдалося відкрити BPF об'єкт %s\n", bpf_file);
        return EXIT_FAILURE;
    }

    if (bpf_object__load(obj)) {
        fprintf(stderr, "Не вдалося завантажити BPF програму в ядро (помилка верифікатора)\n");
        bpf_object__close(obj);
        return EXIT_FAILURE;
    }

    /* 2. Знаходимо програму у завантаженому об'єкті за її назвою у SEC() */
    struct bpf_program *prog = bpf_object__find_program_by_name(obj, "xdp_router_filter");
    if (!prog) {
        fprintf(stderr, "Не знайдено секцію xdp_router_filter у BPF об'єкті\n");
        bpf_object__close(obj);
        return EXIT_FAILURE;
    }

    int prog_fd = bpf_program__fd(prog);

    /* 3. Прив'язуємо XDP програму спочатку у Native режимі (XDP_FLAGS_DRV_MODE) */
    __u32 attach_flags = XDP_FLAGS_DRV_MODE;
    int err = bpf_xdp_attach(ifindex, prog_fd, attach_flags, NULL);
    if (err) {
        fprintf(stderr, "Native XDP не підтримується драйвером (код %d), пробуємо Generic mode...\n", err);
        attach_flags = XDP_FLAGS_SKB_MODE;
        err = bpf_xdp_attach(ifindex, prog_fd, attach_flags, NULL);
        if (err) {
            fprintf(stderr, "Помилка bpf_xdp_attach: %s\n", strerror(-err));
            bpf_object__close(obj);
            return EXIT_FAILURE;
        }
    }

    printf("XDP програму успішно завантажено на інтерфейс %s (ifindex %u)!\n", ifname, ifindex);
    printf("Натисніть Ctrl+C для вивантаження та завершення...\n");

    /* Тримаємо процес активним, поки працює XDP хук */
    while (1) {
        sleep(1);
    }

    /* Відв'язуємо програму та звільняємо ресурси при виході */
    bpf_xdp_detach(ifindex, attach_flags, NULL);
    bpf_object__close(obj);
    return EXIT_SUCCESS;
}
```
```cpp
// C++20 Implementation: RAII XdpLoader Wrapper
#include <iostream>
#include <string_view>
#include <system_error>
#include <memory>
#include <thread>
#include <chrono>
#include <net/if.h>
#include <linux/if_link.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

class XdpLoader {
public:
    XdpLoader(std::string_view ifname, std::string_view bpf_path) 
        : ifname_(ifname) {
        ifindex_ = if_nametoindex(ifname_.c_str());
        if (ifindex_ == 0) {
            throw std::system_error(errno, std::generic_category(), "Невідомий мережевий інтерфейс");
        }

        bpf_obj_ = bpf_object__open_file(bpf_path.data(), nullptr);
        if (!bpf_obj_) {
            throw std::runtime_error("Не вдалося відкрити BPF об'єктний файл");
        }

        if (bpf_object__load(bpf_obj_)) {
            bpf_object__close(bpf_obj_);
            throw std::runtime_error("Помилка завантаження BPF програми у ядро (помилка верифікатора)");
        }

        struct bpf_program* prog = bpf_object__find_program_by_name(bpf_obj_, "xdp_router_filter");
        if (!prog) {
            bpf_object__close(bpf_obj_);
            throw std::runtime_error("Секцію програми xdp_router_filter не знайдено");
        }

        int prog_fd = bpf_program__fd(prog);
        attach_flags_ = XDP_FLAGS_DRV_MODE;
        
        int err = bpf_xdp_attach(ifindex_, prog_fd, attach_flags_, nullptr);
        if (err) {
            std::cout << "Native XDP не підтримується драйвером, перехід на Generic mode...\n";
            attach_flags_ = XDP_FLAGS_SKB_MODE;
            err = bpf_xdp_attach(ifindex_, prog_fd, attach_flags_, nullptr);
            if (err) {
                bpf_object__close(bpf_obj_);
                throw std::system_error(-err, std::generic_category(), "Помилка прив'язки bpf_xdp_attach");
            }
        }
        attached_ = true;
    }

    ~XdpLoader() {
        if (attached_) {
            bpf_xdp_detach(ifindex_, attach_flags_, nullptr);
            std::cout << "\nXDP програму відв'язано від мережевого інтерфейсу " << ifname_ << std::endl;
        }
        if (bpf_obj_) {
            bpf_object__close(bpf_obj_);
        }
    }

    // Забороняємо копіювання об'єкта для гарантії єдиного володіння (RAII)
    XdpLoader(const XdpLoader&) = delete;
    XdpLoader& operator=(const XdpLoader&) = delete;

    // Дозволяємо переміщення володіння (Move semantics)
    XdpLoader(XdpLoader&& other) noexcept 
        : ifname_(std::move(other.ifname_)), ifindex_(other.ifindex_), 
          bpf_obj_(other.bpf_obj_), attach_flags_(other.attach_flags_), 
          attached_(other.attached_) {
        other.attached_ = false;
        other.bpf_obj_ = nullptr;
    }

private:
    std::string ifname_;
    unsigned int ifindex_{0};
    struct bpf_object* bpf_obj_{nullptr};
    uint32_t attach_flags_{0};
    bool attached_{false};
};

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <interface> <bpf_obj_file>\n";
        return 1;
    }

    try {
        XdpLoader loader(argv[1], argv[2]);
        std::cout << "XDP програму завантажено! Натисніть Ctrl+C для виходу...\n";
        
        while (true) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
```
:::

---

## 5. Порівняльний аналіз реалізацій C та C++

1. **Управління ресурсами:** У C-версії розробник повинен вручну стежити за кожною гілкою помилок і відв'язувати XDP-програму через `bpf_xdp_detach` та закривати BPF-об'єкт через `bpf_object__close`. У C++20 реалізації це робиться деструктором класу `XdpLoader` за принципом RAII (Resource Acquisition Is Initialization), що гарантує відсутність витоків ресурсів при виникненні винятків (`std::exception`).
2. **Передача рядків:** У C++ використано `std::string_view` для ефективної передачі шляхів без зайвого копіювання пам'яті.
3. **Обробка системних помилок:** Системні коди помилок POSIX конвертуються у стандартні винятки `std::system_error` з автоматичним декодуванням опису помилки.

---

## 6. Покрокова збірка, інспекція та тестування

Для компіляції eBPF коду потрібен компілятор Clang з підтримкою цільової архітектури BPF (`target bpf`), а для завантажувача — встановлена системна бібліотека `libbpf-dev`.

### Крок 1: Компільована збірка eBPF коду ядра

```bash
clang -O2 -target bpf -D__TARGET_ARCH_x86 -c xdp_prog.c -o xdp_prog.o
```

### Крок 2: Збірка користувацьких завантажувачів

```bash
# Збірка C-завантажувача:
gcc -O2 loader.c -o xdp_loader -lbpf

# Збірка C++20 завантажувача:
g++ -O2 -std=c++20 loader.cpp -o xdp_loader_cpp -lbpf
```

### Крок 3: Інспекція байткоду через bpftool

Перед завантаженням у ядро ви можете проінспектувати трансляцію C коду в інструкції eBPF:

```bash
bpftool prog dump xlated file xdp_prog.o
```

### Крок 4: Тестування та перевірка роботи

Запустіть завантажувач від імені привілейованого користувача `root`:

```bash
sudo ./xdp_loader_cpp eth0 xdp_prog.o
```

У сусідньому терміналі перевірте наявність хука XDP через утиліти ядра:

```bash
# Перевірка завантаженого хука на мережевому інтерфейсі
ip link show dev eth0
# Очікуваний вивід містить: prog/xdp id 42 mode native

# Перевірка фільтрації UDP порт 9999 (пакет має відкидатися без відповіді):
nc -u -v 192.168.1.100 9999

# Перевірка ICMP Echo (ping повинен повертатися через XDP_TX):
ping -c 4 192.168.1.100
```
