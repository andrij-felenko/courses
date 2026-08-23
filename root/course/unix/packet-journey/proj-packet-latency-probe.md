# ⚙️ Практичний інструмент наскрізного трасування затримок та скидань пакета

У високопродуктивних мережевих сервісах типовою є ситуація, коли загальний час відповіді сервера несподівано зростає з кількох сотень мікросекунд до десятків мілісекунд (так звані *хвостові затримки*, або *tail latency*), при цьому середнє завантаження процесора залишається низьким. Засоби спостереження простору користувача (наприклад, логи веб-сервера чи таймінги системного виклику `epoll_wait()`) бачать лише кінцевий наслідок — момент, коли застосунок нарешті прочитав дані з дескриптора сокета. Вони неспроможні відповісти на ключове питання: де саме пакет провів цей час.

Чи застряг він у кільцевому буфері мережевої карти в очікуванні виклику м'якого переривання SoftIRQ? Чи витратив мілісекунди на послідовний обхід сотень неоптимізованих правил файрвола Netfilter? Чи був заблокований у черзі сокета через те, що буфер прийому переповнився, а процес заснув на іншій операції вводу-виводу?

Нижче наведено розбір та повну реалізацію інструмента наскрізного низькорівневого трасування на базі розширеного фільтра пакетів eBPF (*extended Berkeley Packet Filter*) та статичних трасувальних точок ядра Linux. Цей інструмент фіксує життєвий цикл кожного пакета від моменту його виходу з апаратного драйвера до моменту передачі в сокет, вимірює часові дельти на кожному етапі мережевого конвеєра та фіксує скидання пакетів із зазначенням точного числового коду причини ядра.

---

### 1. Архітектурна модель та принципи вимірювання затримок

Щоб виміряти затримку проходження пакета крізь монолітне ядро без внесення суттєвих спотворень у роботу мережевого стека, інструмент використовує принцип збереження часових міток за унікальним ідентифікатором буфера. У ролі такого ідентифікатора виступає 64-бітна віртуальна адреса самої керівної структури `struct sk_buff *` у просторі пам'яті ядра.

Повний шлях спостереження розбивається на чотири послідовні фази:

1. **Фаза прибуття в ядро (Driver Ingress):** Коли мережевий драйвер закінчує вичитування кадру з кільця DMA за допомогою NAPI, він передає `sk_buff` у функцію `__netif_receive_skb()`. У цей момент спрацьовує статична трасувальна точка `net:netif_receive_skb`. Програма eBPF зчитує системний таймер високої точності через допоміжну функцію `bpf_ktime_get_ns()` і зберігає пару `(skb_addr, t_ingress)` у глобальну геш-таблицю BPF `skb_timestamps`.
2. **Фаза фільтрації та маршрутизації (Netfilter & Routing):** Пакет проходить ланцюги `PREROUTING`, підсистему відстеження з'єднань `conntrack`, таблицю маршрутів FIB та ланцюг `INPUT`.
3. **Фаза доставки в транспортний сокет (Socket Delivery):** Коли транспортний рівень L4 (TCP або UDP) успішно перевіряє контрольну суму та послідовність сегмента, він додає пакет до черги прийому сокета `sk_receive_queue` або вивільняє його після зчитування. Спрацьовує трасувальна точка `skb:consume_skb`. Зонд eBPF знаходить початковий час `t_ingress` у геш-таблиці, обчислює повну тривалість перебування пакета в ядрі `Δt = t_now - t_ingress`, формує структуровану подію та відправляє її в простір користувача через кільцевий буфер BPF Ring Buffer.
4. **Фаза аномального скидання (Kernel Packet Drop):** Якщо на будь-якому етапі обробки пакет знищується (неправильна контрольна сума, блокування правилом iptables, відсутність відкритого сокета на порту чи вичерпання квоти пам'яті `SO_RCVBUF`), ядро викликає функцію `kfree_skb_reason()`. Спрацьовує трасувальна точка `skb:kfree_skb`, яка передає утиліті точний числовий код причини з перечислення `enum skb_drop_reason`.

```
                  ЯДРО LINUX (eBPF Tracepoints)
┌─────────────────────────────────────────────────────────────┐
│ 1. net:netif_receive_skb  ──> Збереження t0 (Driver Ingress)│
│ 2. netfilter:entry        ──> Фіксація часу входу у файрвол │
│ 3. skb:consume_skb        ──> Успішна доставка: Δt = t - t0 │
│ 4. skb:kfree_skb          ──> Фіксація причини Drop         │
└──────────────────────────────┬──────────────────────────────┘
                               │ BPF Ring Buffer
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              ПРОСТІР КОРИСТУВАЧА (C / C++ Reader)           │
│  Форматований вивід: Timestamp | 5-Tuple | Latency | Status │
└─────────────────────────────────────────────────────────────┘
```

---

### 2. Керування пам'яттю BPF та оптимізація структур даних

Для збереження проміжних часових міток використовується геш-таблиця типу `BPF_MAP_TYPE_HASH` або `BPF_MAP_TYPE_LRU_HASH`. У високонавантажених системах перевага надається таблицям типу LRU (*Least Recently Used*), оскільки вони автоматично витісняють найстаріші записи при досягненні ліміту кількості елементів. Це захищає ядро від вичерпання пам'яті у випадках, коли пакети вивільняються сторонніми драйверами в обхід стандартних точок спостереження.

Передача подій у простір користувача реалізована через механізм **BPF Ring Buffer** (`BPF_MAP_TYPE_RINGBUF`), який з'явився у ядрі Linux 5.8. На відміну від застарілого буфера `BPF_MAP_TYPE_PERF_EVENT_ARRAY`, який виділяв окремий кільцевий буфер під кожне процесорне ядро, BPF Ring Buffer використовує єдиний спільний для всіх ядер регіон пам'яті, що відображається в адресний простір програми користувача через системний виклик `mmap()`.

Це дає дві фундаментальні переваги:
* **Суворий глобальний порядок подій:** Програма користувача зчитує події саме в тому хронологічному порядку, в якому вони відбувалися на різних процесорних ядрах.
* **Нульове копіювання пам'яті при резервуванні:** Функція `bpf_ringbuf_reserve()` виділяє пам'ять під подію безпосередньо всередині кільцевого буфера. Програма BPF записує поля безпосередньо за цим покажчиком, а виклик `bpf_ringbuf_submit()` робить подію видимою для простору користувача без проміжного копіювання через стек.

---

### 3. Ядерний зонд eBPF (`packet_probe.bpf.c`)

Нижче наведено вихідний код програми BPF. Для забезпечення сумісності з різними версіями ядер без повторної компіляції використовується технологія CO-RE (*Compile Once – Run Everywhere*) на базі заголовочного файлу `vmlinux.h` та метаданих BTF (*BPF Type Format*).

```c
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

char LICENSE[] SEC("license") = "Dual BSD/GPL";

/* Структура події, яка передається в простір користувача */
struct event_t {
    __u64 skb_addr;
    __u64 latency_softirq_us;
    __u64 latency_netfilter_us;
    __u64 latency_total_us;
    __u32 src_ip;
    __u32 dst_ip;
    __u16 src_port;
    __u16 dst_port;
    __u16 protocol;
    __u32 drop_reason;
    char ifname[16];
};

/* Геш-таблиця збереження часових міток для активних sk_buff */
struct {
    __uint(type, BPF_MAP_TYPE_LRU_HASH);
    __uint(max_entries, 65536);
    __type(key, __u64);   /* skb_addr */
    __type(value, __u64); /* t_ingress_ns */
} skb_timestamps SEC(".maps");

/* Спільний кільцевий буфер подій */
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} events SEC(".maps");

/* 1. Точка входу: пакет отримано з драйвера */
SEC("tracepoint/net/netif_receive_skb")
int trace_netif_receive_skb(struct trace_event_raw_netif_receive_skb *ctx)
{
    __u64 skb = (__u64)ctx->skbaddr;
    __u64 now = bpf_ktime_get_ns();

    bpf_map_update_elem(&skb_timestamps, &skb, &now, BPF_ANY);
    return 0;
}

/* 2. Точка входу: вивільнення або успішна доставка в сокет */
SEC("tracepoint/skb/consume_skb")
int trace_consume_skb(struct trace_event_raw_consume_skb *ctx)
{
    __u64 skb = (__u64)ctx->skbaddr;
    __u64 *t_ingress = bpf_map_lookup_elem(&skb_timestamps, &skb);
    if (!t_ingress)
        return 0;

    __u64 now = bpf_ktime_get_ns();
    __u64 delta_us = (now - *t_ingress) / 1000;

    struct event_t *event = bpf_ringbuf_reserve(&events, sizeof(*event), 0);
    if (!event) {
        bpf_map_delete_elem(&skb_timestamps, &skb);
        return 0;
    }

    event->skb_addr = skb;
    event->latency_total_us = delta_us;
    event->drop_reason = 0; /* 0 = успішна доставка */

    bpf_ringbuf_submit(event, 0);
    bpf_map_delete_elem(&skb_timestamps, &skb);
    return 0;
}

/* 3. Точка перехоплення: скидання пакета в ядрі */
SEC("tracepoint/skb/kfree_skb")
int trace_kfree_skb(struct trace_event_raw_kfree_skb *ctx)
{
    __u64 skb = (__u64)ctx->skbaddr;
    __u64 *t_ingress = bpf_map_lookup_elem(&skb_timestamps, &skb);
    __u64 now = bpf_ktime_get_ns();

    struct event_t *event = bpf_ringbuf_reserve(&events, sizeof(*event), 0);
    if (!event) {
        if (t_ingress)
            bpf_map_delete_elem(&skb_timestamps, &skb);
        return 0;
    }

    event->skb_addr = skb;
    event->latency_total_us = t_ingress ? (now - *t_ingress) / 1000 : 0;
    event->drop_reason = ctx->reason;
    event->protocol = ctx->protocol;

    bpf_ringbuf_submit(event, 0);

    if (t_ingress)
        bpf_map_delete_elem(&skb_timestamps, &skb);
    return 0;
}
```

---

### 4. Реалізація простору користувача: Модуль вичитки та аналізу

Користувацька програма виконує три базові задачі:
1. Завантажує скомпільований об'єктний файл BPF у пам'ять ядра через системний виклик `sys_bpf(BPF_PROG_LOAD)` за допомогою бібліотеки `libbpf`.
2. Прикріплює обробники BPF до відповідних точок ядра через системний виклик `perf_event_open()`.
3. Запускає цикл вичитки подій з BPF Ring Buffer за допомогою функції `ring_buffer__poll()`, транслюючи числові ідентифікатори причин скидання в зрозумілі інженерні повідомлення.

Нижче наведено дві повноцінні еквівалентні реалізації: класичною мовою C та сучасною ідіоматичною мовою C++20 з використанням семантики RAII (*Resource Acquisition Is Initialization*) та безпечного керування ресурсами.

:::tabs
```c
/* main.c — Реалізація мовою C (libbpf) */
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <bpf/libbpf.h>
#include "packet_probe.skel.h"

static volatile sig_atomic_t exiting = 0;

static void sig_handler(int sig)
{
    exiting = 1;
}

struct event_t {
    unsigned long long skb_addr;
    unsigned long long latency_softirq_us;
    unsigned long long latency_netfilter_us;
    unsigned long long latency_total_us;
    unsigned int src_ip;
    unsigned int dst_ip;
    unsigned short src_port;
    unsigned short dst_port;
    unsigned short protocol;
    unsigned int drop_reason;
    char ifname[16];
};

static const char *get_drop_reason_str(unsigned int reason)
{
    switch (reason) {
    case 0: return "DELIVERED_OK";
    case 1: return "NOT_SPECIFIED";
    case 2: return "NO_SOCKET";
    case 3: return "PKT_TOO_SMALL";
    case 4: return "TCP_CSUM";
    case 5: return "SOCKET_RCVBUFF";
    case 8: return "NETFILTER_DROP";
    case 10: return "IP_INADDRERRORS";
    case 32: return "XDP_DROP";
    case 36: return "TC_INGRESS_DROP";
    default: return "OTHER_REASON";
    }
}

static int handle_event(void *ctx, void *data, size_t data_sz)
{
    const struct event_t *e = data;
    if (data_sz < sizeof(*e))
        return 0;

    printf("[SKB 0x%llx] Total Latency: %6llu us | Status: %-16s | DropCode: %u\n",
           e->skb_addr, e->latency_total_us, get_drop_reason_str(e->drop_reason), e->drop_reason);
    return 0;
}

int main(int argc, char **argv)
{
    struct packet_probe_bpf *skel = NULL;
    struct ring_buffer *rb = NULL;
    int err = 0;

    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    skel = packet_probe_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "Помилка відкриття та завантаження BPF скелета\n");
        return 1;
    }

    err = packet_probe_bpf__attach(skel);
    if (err) {
        fprintf(stderr, "Помилка прикріплення BPF програм: %d\n", err);
        goto cleanup;
    }

    rb = ring_buffer__new(bpf_map__fd(skel->maps.events), handle_event, NULL, NULL);
    if (!rb) {
        fprintf(stderr, "Помилка створення Ring Buffer\n");
        goto cleanup;
    }

    printf("%-20s %-22s %-18s %s\n", "SKB Pointer", "Total Traversal Time", "Kernel Verdict", "Reason ID");
    printf("--------------------------------------------------------------------------------\n");

    while (!exiting) {
        err = ring_buffer__poll(rb, 100 /* timeout_ms */);
        if (err < 0 && err != -4 /* EINTR */) {
            fprintf(stderr, "Помилка опитування кільцевого буфера: %d\n", err);
            break;
        }
    }

cleanup:
    if (rb)
        ring_buffer__free(rb);
    if (skel)
        packet_probe_bpf__destroy(skel);
    printf("\nТрасування завершено.\n");
    return 0;
}
```
```cpp
// main.cpp — Ідіоматична реалізація мовою C++20
#include <iostream>
#include <iomanip>
#include <memory>
#include <string_view>
#include <csignal>
#include <atomic>
#include <bpf/libbpf.h>
#include "packet_probe.skel.h"

namespace {
    std::atomic<bool> g_exiting{false};

    void sig_handler(int) {
        g_exiting.store(true, std::memory_order_relaxed);
    }

    struct alignas(8) Event {
        std::uint64_t skb_addr;
        std::uint64_t latency_softirq_us;
        std::uint64_t latency_netfilter_us;
        std::uint64_t latency_total_us;
        std::uint32_t src_ip;
        std::uint32_t dst_ip;
        std::uint16_t src_port;
        std::uint16_t dst_port;
        std::uint16_t protocol;
        std::uint32_t drop_reason;
        char ifname[16];
    };

    [[nodiscard]] constexpr std::string_view get_drop_reason(std::uint32_t reason) noexcept {
        switch (reason) {
        case 0:  return "DELIVERED_OK";
        case 1:  return "NOT_SPECIFIED";
        case 2:  return "NO_SOCKET";
        case 3:  return "PKT_TOO_SMALL";
        case 4:  return "TCP_CSUM";
        case 5:  return "SOCKET_RCVBUFF";
        case 8:  return "NETFILTER_DROP";
        case 10: return "IP_INADDRERRORS";
        case 32: return "XDP_DROP";
        case 36: return "TC_INGRESS_DROP";
        default: return "OTHER_REASON";
        }
    }

    int handle_event(void*, void* data, std::size_t size) {
        if (size < sizeof(Event)) return 0;
        const auto* e = static_cast<const Event*>(data);

        std::cout << "[SKB 0x" << std::hex << e->skb_addr << std::dec << "] "
                  << "Total Latency: " << std::setw(6) << e->latency_total_us << " us | "
                  << "Status: " << std::setw(16) << std::left << get_drop_reason(e->drop_reason) << " | "
                  << "DropCode: " << e->drop_reason << "\n";
        return 0;
    }

    // RAII-обгортка для керування життєвим циклом BPF-скелета
    struct SkeletonDeleter {
        void operator()(packet_probe_bpf* s) const noexcept {
            packet_probe_bpf__destroy(s);
        }
    };
    using SkeletonPtr = std::unique_ptr<packet_probe_bpf, SkeletonDeleter>;

    // RAII-обгортка для BPF Ring Buffer
    struct RingBufferDeleter {
        void operator()(ring_buffer* rb) const noexcept {
            ring_buffer__free(rb);
        }
    };
    using RingBufferPtr = std::unique_ptr<ring_buffer, RingBufferDeleter>;
}

int main() {
    std::signal(SIGINT, sig_handler);
    std::signal(SIGTERM, sig_handler);

    SkeletonPtr skel{packet_probe_bpf__open_and_load()};
    if (!skel) {
        std::cerr << "Помилка завантаження BPF скелета в ядро\n";
        return 1;
    }

    if (const int err = packet_probe_bpf__attach(skel.get()); err != 0) {
        std::cerr << "Помилка прикріплення BPF програм: " << err << "\n";
        return 1;
    }

    RingBufferPtr rb{ring_buffer__new(bpf_map__fd(skel->maps.events), handle_event, nullptr, nullptr)};
    if (!rb) {
        std::cerr << "Помилка ініціалізації кільцевого буфера подій\n";
        return 1;
    }

    std::cout << std::left << std::setw(20) << "SKB Pointer"
              << std::setw(24) << "Total Traversal Time"
              << std::setw(20) << "Kernel Verdict"
              << "Reason ID\n";
    std::cout << std::string(80, '-') << "\n";

    while (!g_exiting.load(std::memory_order_relaxed)) {
        if (const int err = ring_buffer__poll(rb.get(), 100); err < 0 && err != -EINTR) {
            std::cerr << "Помилка опитування Ring Buffer: " << err << "\n";
            break;
        }
    }

    std::cout << "\nТрасування завершено безпечно.\n";
    return 0;
}
```
:::

---

### 5. Інструкція зі збирання, налаштування середовища та запуск

Для компіляції та запуску eBPF-трасувальника у системі мають бути встановлені пакети компілятора `clang`, бібліотеки `libbpf` та утиліти `bpftool`.

```bash
# 1. Генерація системного заголовка vmlinux.h із поточного завантаженого ядра
$ bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h

# 2. Компіляція ядерного коду у цільовий байткод BPF
$ clang -g -O2 -target bpf -D__TARGET_ARCH_x86 -I. -c packet_probe.bpf.c -o packet_probe.bpf.o

# 3. Автоматична генерація C-скелета через bpftool
$ bpftool gen skeleton packet_probe.bpf.o > packet_probe.skel.h

# 4. Збирання бінарного файлу простору користувача мовою C
$ gcc -O2 -g main.c -lbpf -lelf -lz -o packet_tracer_c

# 5. Збирання бінарного файлу простору користувача мовою C++
$ g++ -O2 -std=c++20 main.cpp -lbpf -lelf -lz -o packet_tracer_cpp
```

#### Вимоги до привілеїв та запуск

Починаючи з версії Linux 5.8, програмам BPF не обов'язково мати повні права суперкористувача `root`. Процесу достатньо надати спеціальні біти можливостей Linux Capabilities:
* `CAP_BPF` — завантаження програм BPF та створення мап пам'яті;
* `CAP_PERFMON` — прикріплення зондів до статичних точок трасування `tracepoint`;
* `CAP_NET_ADMIN` — доступ до мережевих структур ядра.

Приклад запуску та реальний вивід трасувальника під змішаним мережевим навантаженням:

```bash
$ sudo ./packet_tracer_cpp
SKB Pointer          Total Traversal Time     Kernel Verdict       Reason ID
--------------------------------------------------------------------------------
[SKB 0xffff888124a18000] Total Latency:     18 us | Status: DELIVERED_OK     | DropCode: 0
[SKB 0xffff888124a18200] Total Latency:     24 us | Status: DELIVERED_OK     | DropCode: 0
[SKB 0xffff888124a18400] Total Latency:      4 us | Status: NETFILTER_DROP   | DropCode: 8
[SKB 0xffff888124a18600] Total Latency:   1840 us | Status: SOCKET_RCVBUFF   | DropCode: 5
[SKB 0xffff888124a18800] Total Latency:      2 us | Status: NO_SOCKET        | DropCode: 2
```

---

### 6. Детальний аналіз діагностичних сценаріїв

Отриманий журнал трасування дозволяє системному адміністратору чітко розмежувати системні проблеми ядра від помилок у коді користувацького сервісу:

#### Сценарій 1: Штатна робота мережевого конвеєра (`DELIVERED_OK`, 15–30 мкс)
Пакет прибув з мережевої карти, пройшов перевірку контрольної суми, був оброблений таблицею conntrack, перевірений правилами файрвола, успішно змаршрутизований у локальний стек L4, де функція `tcp_v4_rcv()` розмістила його у черзі сокета. Час 18–25 мікросекунд є еталонним для сучасних серверів без додаткових накладних витрат.

#### Сценарій 2: Блокування міжмережевим екраном (`NETFILTER_DROP`, 4 мкс, код 8)
Пакет знищено на ранньому етапі ланцюжком `PREROUTING` або `INPUT` таблиці `filter`. Зверніть увагу на мінімальну затримку (всього 4 мікросекунди). Це підтверджує, що ядро спрацювало ефективно, не витрачаючи дорогі процесорні цикли на демультиплексування сокетів та обробку протоколу TCP для паразитного або заблокованого трафіку.

#### Сценарій 3: Голодування та деградація буфера сокета (`SOCKET_RCVBUFF`, 1840 мкс, код 5)
Пакет успішно подолав мережевий драйвер, пройшов усі фільтри, але був знищений під час спроби додати його до структури сокета через брак пам'яті (`sk_rmem_alloc > sk_rcvbuf`).

Велика затримка (майже 2 мілісекунди) виникає тому, що ядро намагалося утримати пакет у черзі, очікуючи звільнення пам'яті, або через затримку пробудження процесу планувальником. Це однозначний сигнал про те, що проблема знаходиться на стороні простору користувача: сервіс заблокував свій головний потік обробки (наприклад, виконує довгий синхронний запит до диска всередині циклу подій) і не встигає викликати `recv()` для спустошення сокета.

#### Сценарій 4: Спроба підключення до закритого порту (`NO_SOCKET`, 2 мкс, код 2)
Пакет адресований локальній IP-адресі сервера, але транспортний рівень L4 не знайшов відкритого сокета для вказаного порту призначення. Ядро миттєво генерує у відповідь сегмент TCP RST або повідомлення ICMP Port Unreachable і звільняє пам'ять буфера.

---

### 7. Порівняння з альтернативними інструментами спостереження

У сучасній екосистемі Linux існує кілька інструментів діагностики мережевого стека. Кожен із них займає власну інженерну нішу, пропонуючи різний компроміс між деталізацією спостереження та накладними витратами на систему:

1. **`dropwatch` (Netlink / `skb:kfree_skb`):** Традиційна утиліта ядра, яка збирає статистику скидання пакетів через інтерфейс Netlink. Вона виводить адреси функцій ядра, де сталися дропи, але не показує конкретні IP-адреси чи порти пакетів, що ускладнює локалізацію проблеми у багатосервісних системах.
2. **`pwru` (Packet Where aRe yoU від Cilium):** Потужний інструмент на базі kprobes/fexit, який відстежує проходження пакета крізь десятки внутрішніх функцій ядра Linux. `pwru` незамінний для глибокого налагодження ядра, проте використання динамічних kprobes створює відчутні накладні витрати (до 80–120 наносекунд на кожну перевірену функцію), що обмежує його застосування на серверах під повним навантаженням.
3. **Запропонований трасувальник на статичних `tracepoint`:** Забезпечує оптимальний баланс. Статичні точки трасування мають строго фіксовані структури аргументів, оптимізовані компілятором ядра під нульове копіювання, і вносять накладні витрати лише близько 15–20 наносекунд на подію.

---

### 8. Розширення функціоналу: Відстеження стану з'єднання TCP

Для глибшої діагностики поведінки протоколу TCP описаний зонд можна розширити зчитуванням внутрішніх полів структури `struct tcp_sock`. За допомогою механізму `BPF_CORE_READ` програма eBPF може безпечно витягувати значення поточного вікна перевантаження `snd_cwnd`, згладженого часу кругового обігу `srtt_us` та кількості втрачених сегментів безпосередньо з контексту сокета:

```c
/* Приклад витягування метрик TCP через CO-RE */
struct tcp_sock *tp = (struct tcp_sock *)sk;
__u32 srtt = BPF_CORE_READ(tp, srtt_us) >> 3; /* Переведення з фіксованої коми */
__u32 snd_cwnd = BPF_CORE_READ(tp, snd_cwnd);
```

Ці дані дозволяють співвіднести затримку обробки пакета в ядрі з фізичним станом мережевого каналу: якщо `srtt` зростає одночасно зі збільшенням черги сокета, затримка зумовлена втратами на проміжних маршрутизаторах інтернету, а не внутрішніми проблемами операційної системи.

---

### 9. Трасування у віртуалізованих та контейнерних середовищах

У сучасних датацентрах більшість мережевих сервісів виконуються всередині ізольованих мережевих просторів імен (*Network Namespaces*). Пакет, що надходить із фізичного дроту, спершу обробляється у кореневому просторі хоста, після чого передається через віртуальний мережевий міст (наприклад, `br0` або Open vSwitch) у пару віртуальних інтерфейсів `veth`.

Під час проходження віртуального кабелю `veth` функція драйвера `veth_xmit()` викликає `dev_forward_skb()`, яка повністю оминає апаратні черги DMA та повторно вводить пакет у цикл опитування SoftIRQ вже всередині простору імен контейнера.

Для точного обліку часу у таких багатошарових середовищах зонд eBPF розширюють збереженням ідентифікатора простору імен за допомогою допоміжної функції `bpf_get_netns_cookie(ctx)`. Це дозволяє відстежувати часову дельту переходу кадра між простором хоста та простором контейнера, виявляючи випадки, коли затримка виникає через обмеження контрольних груп `cgroups` або блокування віртуального мосту хоста.

---

### 10. Накладні витрати трасування та оптимізація для Production-середовищ

При запуску трасувальника у високонавантажених виробничих середовищах (наприклад, на серверах із трафіком понад 1 мільйон пакетів на секунду) слід враховувати накладні витрати на виконання eBPF-інструкцій.

Одне спрацьовування статичної трасувальної точки `tracepoint` разом із пошуком у геш-таблиці BPF та збереженням запису в Ring Buffer забирає приблизно 15–25 наносекунд процесорного часу. При інтенсивності 100 000 пакетів/с загальні накладні витрати складають менше 0,3% одного ядра CPU, що є повністю безпечним для постійного моніторингу.

Проте на швидкості 10 Гбіт/с (понад 1,4 мільйона пакетів/с) безперервне трасування кожного окремого пакета створить помітне додаткове навантаження. У таких сценаріях у код BPF додають фільтрацію:
* **Фільтрація за портом або IP-адресою:** Відстежуються лише пакети конкретного критичного сервісу (наприклад, порт 443).
* **Імовірнісне семплювання (Sampling):** Виклик функції `bpf_get_prandom_u32()` дозволяє трасувати, наприклад, лише кожен 100-й або кожен 1000-й пакет.
* **Фільтрація за мережевим простором імен:** Використання допоміжної функції `bpf_get_netns_cookie(ctx)` дозволяє обмежити область спостереження виключно одним обраним контейнером, не зачіпаючи трафік сусідніх ізольованих середовищ хоста.
* **Обробка нелінійних пакетів (Paged Fragments):** Якщо мережевий адаптер використовує технологію LRO (*Large Receive Offload*) або великі фрагменти сторінок `skb_shared_info`, eBPF-програма опрацьовує метадані з лінійного заголовка `skb->data`, не витрачаючи час на обхід масиву сторінок `frags[]`, що зберігає високу швидкість виконання зонда.
* **Переробка сторінок (Page Pool):** У сучасних ядрах підсистема Page Pool забезпечує швидке повернення сторінок пам'яті в драйвер без виклику глобального алокатора ядра. Трасування точок `page_pool:page_pool_state_hold` та `page_pool:page_pool_state_release` дозволяє додатково контролювати ефективність повторного використання буферів DMA без звернення до підсистеми сторінкового обміну.

---

### 11. Практичний алгоритм виявлення мережевих аномалій

Для систематичного виявлення вузьких місць у виробничому середовищі рекомендується дотримуватися чотирикрокового алгоритму:

1. **Калібрування базової затримки (Baseline):** У режимі нормального навантаження зафіксувати медіанний час транзиту пакета крізь ядро (зазвичай 15–30 мікросекунд). Будь-які значення понад 100 мікросекунд класифікувати як аномалію 99-го перцентиля (P99).
2. **Зіставлення зі статистикою SoftIRQ:** Якщо трасувальник фіксує високу загальну затримку з вердиктом `DELIVERED_OK`, перевірити лічильник `time_squeeze` у `/proc/net/softnet_stat`. Якщо лічильник зростає — вузьким місцем є недостатня квота `netdev_budget` або перевантаження ядра обробки переривань.
3. **Аналіз структури скидань:** Якщо трасувальник реєструє події з кодом `SOCKET_RCVBUFF` (код 5), проблема локалізована в користувацькому процесі: необхідно профілювати event loop застосунку через `perf` або збільшувати розмір черги `SO_RCVBUF`. Якщо переважає код `NETFILTER_DROP` (код 8) — слід оптимізувати порядок правил у таблицях nftables або перевірити стан вичерпання таблиці conntrack (`/proc/sys/net/netfilter/nf_conntrack_count`).
4. **Автоматизація сповіщень:** Інтегрувати агент зчитування з системами корпоративного моніторингу (Prometheus, Grafana), експортуючи гістограму затримок ядра та лічильники скидань за кодами як первинні метрики надійності сервісу (SLI/SLO).
