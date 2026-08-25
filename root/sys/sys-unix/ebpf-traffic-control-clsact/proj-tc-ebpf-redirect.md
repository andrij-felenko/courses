# ⚙️ Практичний проект: перенаправлення трафіку за допомогою eBPF TC clsact

У цьому проекті реалізовано повну практичну систему програмованого аналізу, модифікації та високошвидкісного перенаправлення мережевого трафіку в ядрі Linux на основі підсистеми Traffic Control (tc) та дисципліни черги `clsact`. Проект демонструє реальну архітектуру мережевих датапатів, які використовуються у сучасних хмарних плагінах Kubernetes (CNI), таких як Cilium чи Calico eBPF data path, для з'єднання віртуальних інтерфейсів `veth` контейнерів з фізичними мережевими картами хоста.

Система складається з двох автономних частин:
1. **eBPF-програми ядра (`tc_redirect_kern.c`):** Компілюється у байт-код BPF для архітектури 64-бітних регістрів. Програма прикріплюється до точки підключення `ingress` віртуального інтерфейсу `veth0`, виконує послідовне розпарсування заголовків канального (Ethernet L2), мережевого (IPv4 L3) та транспортного (TCP L4) рівнів. Вона здійснює сувору перевірку меж пам'яті для верифікатора BPF Verifier і за допомогою допоміжної функції `bpf_redirect()` перенаправляє всі пакети з TCP-портом призначення 8080 безпосередньо у вихідний інтерфейс `veth1`, повністю минаючи стек L3-маршрутизації та Netfilter.
2. **Користувацького завантажувача (Userspace Loader):** Керує повним життєвим циклом програми eBPF у ядрі: ініціалізує qdisc `clsact`, оновлює таблиці BPF Maps індексами пристроїв, завантажує байт-код через системний виклик `bpf()` та виконує прив'язку до хука за допомогою бібліотеки `libbpf`. Для забезпечення сумісності з різними стилями розробки надано дві ідіоматичні реалізації завантажувача — процедурною мовою C та об'єктно-орієнтованою мовою C++ з використанням шаблону RAII.

## 1. Архітектура та покроковий розбір програми ядра (`tc_redirect_kern.c`)

Код програми ядра розроблено з дотриманням усіх вимог безпеки BPF Verifier. Будь-яке роздереферення вказівника на дані пакета передується явним порівнянням із кінцевим зсувом лінійного буфера `data_end`.

```c
#include <linux/bpf.h>
#include <linux/pkt_cls.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <arpa/inet.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_endian.h>

#define TARGET_PORT 8080

// Конфігураційна карта BPF типу ARRAY для збереження індексу цільового інтерфейсу
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 1);
    __type(key, __u32);
    __type(value, __u32);
} config_map SEC(".maps");

SEC("classifier")
int tc_redirect_func(struct __sk_buff *skb) {
    // Зчитуємо межі лінійного буфера пакета з контексту skb
    void *data = (void *)(long)skb->data;
    void *data_end = (void *)(long)skb->data_end;

    // Крок 1: Перевірка меж та розпарсування Ethernet заголовка (L2)
    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end) {
        return TC_ACT_OK; // Буфер надто малий — передаємо пакет далі
    }

    // Перевіряємо протокол L2: обробляємо лише кадри IPv4 (EtherType 0x0800)
    if (eth->h_proto != bpf_htons(ETH_P_IP)) {
        return TC_ACT_OK;
    }

    // Крок 2: Перевірка меж та розпарсування IP заголовка (L3)
    struct iphdr *ip = (void *)(eth + 1);
    if ((void *)(ip + 1) > data_end) {
        return TC_ACT_OK;
    }

    // Перевіряємо протокол L3: відфільтровуємо лише TCP-трафік (IPPROTO_TCP = 6)
    if (ip->protocol != IPPROTO_TCP) {
        return TC_ACT_OK;
    }

    // Крок 3: Перевірка меж та розпарсування TCP заголовка (L4)
    struct tcphdr *tcp = (void *)(ip + 1);
    if ((void *)(tcp + 1) > data_end) {
        return TC_ACT_OK;
    }

    // Крок 4: Аналіз порту призначення та прийняття рішення про перенаправлення
    if (tcp->dest == bpf_htons(TARGET_PORT)) {
        __u32 key = 0;
        __u32 *ifindex_ptr = bpf_map_lookup_elem(&config_map, &key);
        
        if (ifindex_ptr && *ifindex_ptr > 0) {
            // Перенаправляємо пакет на цільовий ifindex у режимі egress (flags = 0)
            return bpf_redirect(*ifindex_ptr, 0);
        }
    }

    // Усі інші пакети пропускаємо для стандартної обробки ядром
    return TC_ACT_OK;
}

char _license[] SEC("license") = "GPL";
```

### Детальний механізм роботи коду ядра:
1. **Зчитування контексту `skb`:** Програма отримує вказівник на `struct __sk_buff`. Зчитування полів `skb->data` та `skb->data_end` повертає 32-бітні значення зсувів у пам'яті. У 64-бітній архітектурі вони зводяться до вказівників через `(void *)(long)skb->data`.
2. **Перевірка меж (Bounds Check):** Вираз `(void *)(eth + 1) > data_end` вираховує математичний зсув `data + sizeof(struct ethhdr)` (14 байтів). Якщо цей зсув перевищує `data_end`, верифікатор BPF гарантує, що програма припинить обробку та поверне `TC_ACT_OK`. Без цієї перевірки завантаження коду в ядро буде заблоковане верифікатором із помилкою `invalid access to packet`.
3. **Конвертація порядку байтів (`bpf_htons`):** Поля мережевих заголовків (`eth->h_proto`, `tcp->dest`) зберігаються у форматі Big-Endian (Network Byte Order). Оскільки процесори x86_64 використовують Little-Endian, макрос `bpf_htons()` міняє байти місцями для коректного порівняння констант.
4. **Взаємодія з BPF Map:** Таблиця `config_map` типу `BPF_MAP_TYPE_ARRAY` зберігає системний індекс цільового мережевого інтерфейсу (`ifindex`), записаний користувацьким завантажувачем. Функція `bpf_map_lookup_elem()` повертає вказівник на значення. Перевірка `ifindex_ptr && *ifindex_ptr > 0` захищає від дереференсування нулевого вказівника (Null Pointer Dereference).
5. **Виконання `bpf_redirect()`:** Функція `bpf_redirect(ifindex, 0)` записує цільовий індекс пристрою та напрямок (egress = 0) у приховані метадані `skb` і повертає системний код `TC_ACT_REDIRECT`. При отриманні цього коду функція `__netif_receive_skb_core()` перехоплює пакет і відправляє його безпосередньо у функцію передачі драйвера `dev_queue_xmit(target_if)`, обходячи Netfilter та routing lookup.

## 2. Користувацькі завантажувачі (Userspace Loaders)

Завантажувачі користувацького простору відповідають за завантаження компільованого об'єктного файла `tc_redirect_kern.o` у ядро через системний виклик `bpf()`, ініціалізацію qdisc `clsact` та прикріплення програми до `ingress` хука за допомогою високорівневого API `libbpf`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <net/if.h>
#include <errno.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <src_ifname> <target_ifname>\n", argv[0]);
        return 1;
    }

    const char *src_if = argv[1];
    const char *target_if = argv[2];

    // Перетворюємо текстові назви інтерфейсів у системні числові індекси (ifindex)
    unsigned int src_ifindex = if_nametoindex(src_if);
    unsigned int target_ifindex = if_nametoindex(target_if);

    if (!src_ifindex || !target_ifindex) {
        perror("Помилка if_nametoindex (інтерфейс не знайдено у системі)");
        return 1;
    }

    // 1. Відкриваємо ELF об'єктний файл програми eBPF
    struct bpf_object *obj = bpf_object__open_file("tc_redirect_kern.o", NULL);
    if (libbpf_get_error(obj)) {
        fprintf(stderr, "Не вдалося відкрити BPF ELF об'єктний файл\n");
        return 1;
    }

    // 2. Завантажуємо байт-код у ядро (проходження перевіряльника BPF Verifier)
    if (bpf_object__load(obj)) {
        fprintf(stderr, "Помилка BPF Verifier при завантаженні програми у ядро\n");
        bpf_object__close(obj);
        return 1;
    }

    struct bpf_program *prog = bpf_object__find_program_by_name(obj, "tc_redirect_func");
    int prog_fd = bpf_program__fd(prog);

    // 3. Оновлюємо конфігураційну карту BPF Map індексом цільового пристрою
    struct bpf_map *map = bpf_object__find_map_by_name(obj, "config_map");
    int map_fd = bpf_map__fd(map);
    __u32 key = 0;
    if (bpf_map_update_elem(map_fd, &key, &target_ifindex, BPF_ANY) < 0) {
        perror("Помилка bpf_map_update_elem при записі у BPF карту");
        bpf_object__close(obj);
        return 1;
    }

    // 4. Налаштовуємо хук clsact та опції прикріплення Direct-Action
    DECLARE_LIBBPF_OPTS(bpf_tc_hook, hook,
        .sz = sizeof(struct bpf_tc_hook),
        .ifindex = src_ifindex,
        .attach_point = BPF_TC_INGRESS
    );

    DECLARE_LIBBPF_OPTS(bpf_tc_opts, opts,
        .sz = sizeof(struct bpf_tc_opts),
        .prog_fd = prog_fd
    );

    // Створюємо дисципліну черги clsact (операція є ідемпотентною)
    int err = bpf_tc_hook_create(&hook);
    if (err && err != -EEXIST) {
        fprintf(stderr, "Не вдалося створити clsact qdisc: %s\n", strerror(-err));
        bpf_object__close(obj);
        return 1;
    }

    // Прикріплюємо BPF програму до ingress хука у режимі direct-action
    err = bpf_tc_attach(&hook, &opts);
    if (err) {
        fprintf(stderr, "Не вдалося прикріпити TC BPF програму: %s\n", strerror(-err));
        bpf_object__close(obj);
        return 1;
    }

    printf("Успішно прикріплено eBPF TC програму до %s (ingress) -> redirect %s\n", src_if, target_if);
    printf("Натисніть Enter для відкріплення програми та завершення...\n");
    getchar();

    // 5. Очищення ресурсів: відкріплюємо фільтр та видаляємо об'єкт з пам'яті
    opts.prog_fd = 0;
    opts.prog_id = 0;
    bpf_tc_detach(&hook, &opts);
    bpf_object__close(obj);
    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <stdexcept>
#include <memory>
#include <system_error>
#include <net/if.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

// RAII клас для керування життєвим циклом eBPF TC clsact програми
class BpfTcManager {
public:
    BpfTcManager(std::string_view src_if, std::string_view target_if) {
        src_ifindex_ = if_nametoindex(src_if.data());
        target_ifindex_ = if_nametoindex(target_if.data());

        if (src_ifindex_ == 0 || target_ifindex_ == 0) {
            throw std::system_error(errno, std::generic_category(), "Невідомий мережевий інтерфейс у системі");
        }

        // 1. Відкриваємо BPF ELF об'єктний файл
        obj_ = bpf_object__open_file("tc_redirect_kern.o", nullptr);
        if (libbpf_get_error(obj_)) {
            throw std::runtime_error("Не вдалося відкрити eBPF ELF об'єктний файл");
        }

        // 2. Завантажуємо байт-код у ядро (проходження BPF Verifier)
        if (bpf_object__load(obj_)) {
            bpf_object__close(obj_);
            throw std::runtime_error("Помилка BPF Verifier при завантаженні eBPF у ядро");
        }

        setup_map();
        attach_tc();
    }

    ~BpfTcManager() noexcept {
        // Гарантоване відкріплення BPF фільтра при руйнуванні об'єкта або винятку
        if (attached_) {
            opts_.prog_fd = 0;
            opts_.prog_id = 0;
            bpf_tc_detach(&hook_, &opts_);
        }
        if (obj_) {
            bpf_object__close(obj_);
        }
    }

    // Забороняємо копіювання об'єкта (строгий RAII ресурс)
    BpfTcManager(const BpfTcManager&) = delete;
    BpfTcManager& operator=(const BpfTcManager&) = delete;

private:
    void setup_map() {
        auto* map = bpf_object__find_map_by_name(obj_, "config_map");
        int map_fd = bpf_map__fd(map);
        std::uint32_t key = 0;
        std::uint32_t val = target_ifindex_;

        if (bpf_map_update_elem(map_fd, &key, &val, BPF_ANY) < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося оновити конфігураційну BPF карту");
        }
    }

    void attach_tc() {
        auto* prog = bpf_object__find_program_by_name(obj_, "tc_redirect_func");
        int prog_fd = bpf_program__fd(prog);

        hook_.sz = sizeof(struct bpf_tc_hook);
        hook_.ifindex = src_ifindex_;
        hook_.attach_point = BPF_TC_INGRESS;

        opts_.sz = sizeof(struct bpf_tc_opts);
        opts_.prog_fd = prog_fd;

        // Створюємо qdisc clsact (операція є ідемпотентною)
        int err = bpf_tc_hook_create(&hook_);
        if (err && err != -EEXIST) {
            throw std::system_error(-err, std::generic_category(), "Не вдалося створити clsact qdisc");
        }

        // Прикріплюємо фільтр direct-action
        err = bpf_tc_attach(&hook_, &opts_);
        if (err) {
            throw std::system_error(-err, std::generic_category(), "Не вдалося прикріпити TC BPF filter");
        }
        attached_ = true;
    }

    unsigned int src_ifindex_{0};
    unsigned int target_ifindex_{0};
    struct bpf_object* obj_{nullptr};
    struct bpf_tc_hook hook_{};
    struct bpf_tc_opts opts_{};
    bool attached_{false};
};

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <src_ifname> <target_ifname>\n";
        return 1;
    }

    try {
        BpfTcManager manager(argv[1], argv[2]);
        std::cout << "eBPF TC clsact прикріплено у режимі RAII. Натисніть Enter для виходу...\n";
        std::cin.get();
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
```
:::

## 3. Оцінка переваг C++ RAII реалізації над C

У той час як процедурний C-завантажувач вимагає ручного відстеження всіх гілок помилок та викликів `goto cleanup`, C++ реалізація на основі патерну RAII (Resource Acquisition Is Initialization) надає фундаментальні переваги для продакшен-систем:

1. **Гарантія вивільнення ресурсів:** Якщо під час оновлення карт BPF чи прикріплення фільтра виникає помилка, деструктор `~BpfTcManager()` автоматично відкріплює програму через `bpf_tc_detach()` та закриває об'єкт через `bpf_object__close()`. Це виключає витоки файлових дескрипторів та "завислі" BPF-фільтри в ядрі.
2. **Типобезпечна обробка помилок:** Використання `std::system_error` та `std::runtime_error` дозволяє передавати виклики вище по стеку викликів без громіздких від'ємних кодів повернення.
3. **Безпека копіювання:** Явне видалення конструктора копіювання `delete` запобігає ситуаціям подвійного закриття одного й того самого дескриптора `bpf_object` під час передачі об'єкта в інші функції.

## 4. Оптимізація продуктивності: `bpf_redirect_peer()` для контейнерних мереж

У реальних хмарних середовищах Kubernetes пакети передаються між мережевим простором імен хоста (default netns) та мережевими просторами контейнерів (pod netns) через віртуальні pairs `veth`.

Якщо використати стандартну функцію `bpf_redirect(target_ifindex, 0)`, ядро відправляє пакет на вихідний шлях (egress) інтерфейсу `veth0`. Звідти пакет потрапляє у функцію `dev_forward_skb()`, яка вимушена виконати перевірку сокетного буфера, скинути кешовані вказівники та повторно виділити метадані для переходу в інший netns.

Для усунення цих накладних витрат ядро Linux пропонує спеціалізований хепер **`bpf_redirect_peer()`**:

```c
// Використання bpf_redirect_peer для прямого переходу в netns контейнера
SEC("classifier")
int tc_fast_redirect(struct __sk_buff *skb) {
    // ... розпарсування заголовків ...
    
    // Передає пакет безпосередньо на ingress хук парного veth пристрою в іншому netns
    return bpf_redirect_peer(target_ifindex, 0);
}
```

Виклик `bpf_redirect_peer()` усуває подвійне переключення контексту між просторами імен, уникає повторного розпарасування заголовків і зменшує затримку перенаправлення пакетів між контейнерами на 30–40%.

## 5. Крайові випадки: фрагментовані (paged) та клоновані кадри

Під час обробки високошвидкісного трафіку eBPF програма може зіткнутися з кадрами великого розміру (Jumbo Frames > 1500 байтів) або пакетами, згенерованими технологіями розвантаження GRO (Generic Receive Offload) та TSO (TCP Segmentation Offload).

У таких випадках частина даних пакета зберігається у нелінійних сторінках `skb_shinfo(skb)->frags`. Якщо TCP-заголовок виходить за межі лінійного буфера `data_end`, вираз `(tcp + 1) > data_end` поверне `true`, і базовий код пропустить пакет без перенаправлення.

Для вирішення цієї проблеми програма повинна викликати хепер `bpf_skb_pull_data()`:

```c
// Примусове підтягування перших 54 байтів (Eth + IP + TCP) у лінійний буфер
if ((void *)(tcp + 1) > data_end) {
    if (bpf_skb_pull_data(skb, sizeof(struct ethhdr) + sizeof(struct iphdr) + sizeof(struct tcphdr)) < 0) {
        return TC_ACT_OK;
    }
    // Після виклику bpf_skb_pull_data обов'язково оновлюємо вказівники!
    data = (void *)(long)skb->data;
    data_end = (void *)(long)skb->data_end;
}
```

Хепер `bpf_skb_pull_data()` підтягує вказану кількість байтів із пагінованих сторінок у лінійну область `skb->data`. Оскільки адреса лінійного буфера в пам'яті може змінитися, програма зобов'язана заново ініціалізувати вказівники `data` та `data_end` після виклику `bpf_skb_pull_data()`.

## 6. Збірка, розгортання та діагностика

Для збірки проекту потрібні компілятори Clang (для коду ядра BPF) та GCC/G++ разом із бібліотеками `libbpf` та `libelf`.

### Покрокові команди компіляції:

```bash
# 1. Компіляція програми ядра у байт-код BPF (архітектура -target bpf)
clang -O2 -g -target bpf -c tc_redirect_kern.c -o tc_redirect_kern.o

# 2. Збірка C-завантажувача
gcc -O2 tc_loader.c -lbpf -lelf -o tc_loader_c

# 3. Збірка C++ завантажувача (стандарт C++20)
g++ -O2 -std=c++20 tc_loader.cpp -lbpf -lelf -o tc_loader_cpp
```

### Налаштування тестового середовища та запуск:

Для безпечного тестування створюється пара віртуальних мережевих інтерфейсів `veth0` та `veth1`:

```bash
# 1. Створення віртуальної пари інтерфейсів
sudo ip link add veth0 type veth peer name veth1
sudo ip link set veth0 up
sudo ip link set veth1 up

# 2. Запуск C++ завантажувача
sudo ./tc_loader_cpp veth0 veth1
```

### Методи інспекції та діагностики в ядрі:

Після запуску завантажувача можна перевірити стан підсистеми TC через стандартні утиліти:

```bash
# Перевірка наявності qdisc clsact на veth0
tc qdisc show dev veth0

# Перевірка прикріпленого BPF фільтра та його ID
tc filter show dev veth0 ingress

# Інспекція всіх завантажених BPF програм у системі через bpftool
sudo bpftool net show
sudo bpftool prog show type sched_cls

# Перегляд логів bpf_trace_printk (якщо додано налагоджувальний вивід)
sudo cat /sys/kernel/debug/tracing/trace_pipe
```

Вивід команди `tc filter show` підтверджує створення BPF класифікатора з ідентифікатором завантаженої програми `id`, прапорцем `direct-action` та тегом секції `classifier`, що гарантує виконання обробки пакетів на швидкості ядра Linux.
