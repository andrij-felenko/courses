# ⚙️ Програмний NAPT-транслятор із таблицею сесій та оновленням контрольних сум

Під час побудови програмних маршрутизаторів, віртуальних мережевих шлюзів у хмарних середовищах, вбудованих прошивок для IoT-пристроїв, а також користувацьких мережевих драйверів (на базі фреймворків DPDK, VPP, eBPF/XDP або системних віртуальних інтерфейсів TUN/TAP) розробники стикаються з необхідністю реалізувати високопродуктивний рушій трансляції мережевих адрес і портів (NAPT).

Головна вимога до системного транслятора — обробка мережевих пакетів на швидкості фізичного каналу (англ. *line rate*) з мінімальною затримкою передачі. Це вимагає строгої інженерної оптимізації трьох базових підсистем:
1. **Збереження стану сесій (англ. *stateful connection tracking*)**: двонаправлена таблиця з'єднань із константною складністю пошуку `O(1)` для вихідного (LAN → WAN) та вхідного зворотного (WAN → LAN) трафіку.
2. **Динамічний розподіл пулу ефемерних портів**: швидке виділення вільних портів у діапазоні `1024..65535`, запобігання колізіям між незалежними внутрішніми клієнтами та своєчасна утилізація закритих сесій.
3. **Інкрементна корекція контрольних сум за RFC 1624**: математичне оновлення 16-бітних полів `checksum` у заголовках IPv4, TCP та UDP без перечитування байтів корисного навантаження.

---

### 1. Архітектура структур даних та життєвий цикл з'єднання

В основі моделі лежить 5-компонентний кортеж (англ. *5-tuple*), що однозначно ідентифікує двонаправлений потік даних на мережевому та транспортному рівнях:
- IP-адреса джерела (`src_ip`, 32 біти);
- IP-адреса призначення (`dst_ip`, 32 біти);
- Порт джерела (`src_port`, 16 бітів);
- Порт призначення (`dst_port`, 16 бітів);
- Числовий код протоколу (`protocol`, 8 бітів: `6` для TCP, `17` для UDP, `1` для ICMP).

Для забезпечення симетричної маршрутизації кожен сеанс зв'язку описується парою дзеркальних кортежів у структурі сесії `NatSession`:
1. **Прямий кортеж (ORIGINAL)**: реєструє потік від внутрішнього хоста локальної мережі до зовнішнього сервера. За цим ключем шукаються всі наступні вихідні пакети клієнта для швидкої заміни `src_ip` на публічну адресу шлюзу `wan_ip` та `src_port` на виділений `nat_port`.
2. **Зворотний кортеж (REPLY)**: реєструє очікувану відповідь від зовнішнього сервера. Коли сервер надсилає зворотний пакет на публічну адресу `wan_ip:nat_port`, транслятор виконує пошук у таблиці за кортежем `(remote_ip, remote_port, wan_ip, nat_port, proto)` і миттєво підміняє адресу та порт призначення на внутрішні координати комп'ютера в LAN.

```
                    ┌─────────────────────────┐
                    │      NAT Hash Table     │
                    ├─────────────────────────┤
   LAN ➔ WAN        │  ORIGINAL Tuple:        │        WAN ➔ LAN
(192.168.1.50:51234 ➔   192.168.1.50:51234    │   (93.184.216.34:80 ➔
 93.184.216.34:80)  │  ⇄ 93.184.216.34:80     │    203.0.113.5:40001)
                    ├─────────────────────────┤
                    │  REPLY Tuple:           │
                    │   93.184.216.34:80      │
                    │  ⇄ 203.0.113.5:40001    │
                    └─────────────────────────┘
```

---

### 2. Керування пулом портів та інкрементний перерахунок

Діапазон ефемерних портів охоплює значення від 1024 до 65535 (загалом 64 512 унікальних номерів). Для відстеження зайнятості використовується бітовий масив `port_allocated` або компактний вектор булевих прапорців.

Щоб мінімізувати накладні витрати на пошук вільного порту за умов високого навантаження (коли відкриваються тисячі з'єднань за секунду), алгоритм реалізує циклічний показник сканування `next_port_scan`. Пошук починається з позиції, наступної за останнім виділеним портом, що рівномірно розподіляє навантаження за номерами та запобігає передчасному перевикористанню одного й того самого порту для сесій, які щойно завершилися.

Інкрементна корекція контрольних сум базується на рівнянні 3 зі стандарту **RFC 1624**:

```
~C' = ~C + ~m + m'
C'  = ~(~C')
```

Функція `csum_update_u16` інвертує стару контрольну суму, додає побітову інверсію старого значення `~old_val`, додає нове 16-бітне значення `new_val`, виконує циклічне перенесення розряду (end-around carry) через зсув `sum >> 16` та повертає інвертований 16-бітний результат. Для 32-бітних IP-адрес функція `csum_update_u32` послідовно викликає 16-бітне оновлення для старшої та молодшої половин адреси.

---

### 3. Повна реалізація транслятора: C та C++

У наведеному нижче коді реалізовано повноцінний рушій обробки сирих мережевих пакетів. Код містить обробку як вихідного трафіку (SNAT для напрямку LAN → WAN), так і вхідного трафіку (зворотний DNAT для відповідей WAN → LAN), перевірку довжини заголовків, захист від пошкоджених пакетів та корекцію контрольних сум.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define NAT_PORT_START 1024
#define NAT_PORT_END   65535
#define HASH_BUCKETS   4096
#define TCP_TIMEOUT_SEC 300
#define UDP_TIMEOUT_SEC 60

typedef struct {
    uint32_t src_ip;
    uint32_t dst_ip;
    uint16_t src_port;
    uint16_t dst_port;
    uint8_t  proto;
} FlowTuple;

typedef struct NatEntry {
    FlowTuple original;      /* Прямий кортеж (LAN -> WAN) */
    FlowTuple reply;         /* Зворотний кортеж (WAN -> LAN) */
    uint16_t  assigned_port; /* Виділений WAN порт трансляції */
    time_t    last_seen;     /* Час останньої активності */
    struct NatEntry* next_orig;
    struct NatEntry* next_reply;
} NatEntry;

typedef struct {
    uint32_t wan_ip;
    NatEntry* orig_buckets[HASH_BUCKETS];
    NatEntry* reply_buckets[HASH_BUCKETS];
    bool port_allocated[NAT_PORT_END - NAT_PORT_START + 1];
    uint16_t next_port_scan;
} NatEngine;

/* Інкрементний перерахунок контрольної суми за RFC 1624 */
static inline uint16_t csum_update_u16(uint16_t old_csum, uint16_t old_val, uint16_t new_val) {
    uint32_t sum = (uint32_t)(~old_csum & 0xFFFF) + (uint32_t)(~old_val & 0xFFFF) + (uint32_t)new_val;
    while (sum >> 16) {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }
    return (uint16_t)(~sum & 0xFFFF);
}

static inline uint16_t csum_update_u32(uint16_t old_csum, uint32_t old_val, uint32_t new_val) {
    uint16_t old_hi = (uint16_t)(old_val >> 16);
    uint16_t old_lo = (uint16_t)(old_val & 0xFFFF);
    uint16_t new_hi = (uint16_t)(new_val >> 16);
    uint16_t new_lo = (uint16_t)(new_val & 0xFFFF);

    uint16_t c = csum_update_u16(old_csum, old_hi, new_hi);
    return csum_update_u16(c, old_lo, new_lo);
}

/* Хешування 5-компонентного кортежу */
static uint32_t hash_tuple(const FlowTuple* t) {
    uint32_t h = t->src_ip ^ t->dst_ip ^ ((uint32_t)t->src_port << 16 | t->dst_port) ^ t->proto;
    h ^= (h >> 16);
    return h % HASH_BUCKETS;
}

static bool tuple_equal(const FlowTuple* a, const FlowTuple* b) {
    return a->src_ip == b->src_ip && a->dst_ip == b->dst_ip &&
           a->src_port == b->src_port && a->dst_port == b->dst_port &&
           a->proto == b->proto;
}

/* Ініціалізація рушія NAT */
void nat_init(NatEngine* nat, uint32_t wan_ip) {
    nat->wan_ip = wan_ip;
    memset(nat->orig_buckets, 0, sizeof(nat->orig_buckets));
    memset(nat->reply_buckets, 0, sizeof(nat->reply_buckets));
    memset(nat->port_allocated, 0, sizeof(nat->port_allocated));
    nat->next_port_scan = 0;
}

/* Виділення ефемерного порту */
static int32_t allocate_port(NatEngine* nat) {
    uint16_t total = NAT_PORT_END - NAT_PORT_START + 1;
    for (uint16_t i = 0; i < total; ++i) {
        uint16_t idx = (nat->next_port_scan + i) % total;
        if (!nat->port_allocated[idx]) {
            nat->port_allocated[idx] = true;
            nat->next_port_scan = (idx + 1) % total;
            return NAT_PORT_START + idx;
        }
    }
    return -1; /* Пул портів вичерпано */
}

/* Обробка вихідного пакета LAN -> WAN (SNAT) */
bool nat_process_outbound(NatEngine* nat, uint8_t* pkt, uint32_t len, NatEntry* entry_pool, uint32_t* pool_idx, uint32_t max_entries) {
    if (len < 20) return false;
    uint8_t ihl = (pkt[0] & 0x0F) * 4;
    if (len < ihl + 8) return false;

    uint8_t proto = pkt[9];
    if (proto != 6 && proto != 17) return false;

    uint32_t src_ip = *(uint32_t*)&pkt[12];
    uint32_t dst_ip = *(uint32_t*)&pkt[16];
    uint16_t* src_port_ptr = (uint16_t*)&pkt[ihl];
    uint16_t* dst_port_ptr = (uint16_t*)&pkt[ihl + 2];
    uint16_t src_port = *src_port_ptr;
    uint16_t dst_port = *dst_port_ptr;

    FlowTuple key = { src_ip, dst_ip, src_port, dst_port, proto };
    uint32_t h = hash_tuple(&key);
    NatEntry* entry = nat->orig_buckets[h];

    while (entry) {
        if (tuple_equal(&entry->original, &key)) break;
        entry = entry->next_orig;
    }

    if (!entry) {
        if (*pool_idx >= max_entries) return false;
        int32_t port = allocate_port(nat);
        if (port < 0) return false;

        entry = &entry_pool[(*pool_idx)++];
        entry->original = key;
        entry->assigned_port = (uint16_t)port;
        entry->last_seen = time(NULL);

        /* Зворотний кортеж: WAN відповідь */
        entry->reply.src_ip = dst_ip;
        entry->reply.dst_ip = nat->wan_ip;
        entry->reply.src_port = dst_port;
        entry->reply.dst_port = (uint16_t)port;
        entry->reply.proto = proto;

        entry->next_orig = nat->orig_buckets[h];
        nat->orig_buckets[h] = entry;

        uint32_t rh = hash_tuple(&entry->reply);
        entry->next_reply = nat->reply_buckets[rh];
        nat->reply_buckets[rh] = entry;
    } else {
        entry->last_seen = time(NULL);
    }

    /* Модифікація IP-заголовка */
    uint16_t* ip_csum = (uint16_t*)&pkt[10];
    *ip_csum = csum_update_u32(*ip_csum, src_ip, nat->wan_ip);
    *(uint32_t*)&pkt[12] = nat->wan_ip;

    /* Модифікація L4-заголовка */
    uint16_t new_port = entry->assigned_port;
    if (proto == 6) { /* TCP */
        uint16_t* tcp_csum = (uint16_t*)&pkt[ihl + 16];
        uint16_t c = csum_update_u32(*tcp_csum, src_ip, nat->wan_ip);
        *tcp_csum = csum_update_u16(c, src_port, new_port);
    } else if (proto == 17) { /* UDP */
        uint16_t* udp_csum = (uint16_t*)&pkt[ihl + 6];
        if (*udp_csum != 0x0000) {
            uint16_t c = csum_update_u32(*udp_csum, src_ip, nat->wan_ip);
            c = csum_update_u16(c, src_port, new_port);
            *udp_csum = (c == 0x0000) ? 0xFFFF : c;
        }
    }
    *src_port_ptr = new_port;
    return true;
}

/* Обробка вхідного пакета WAN -> LAN (зворотний DNAT) */
bool nat_process_inbound(NatEngine* nat, uint8_t* pkt, uint32_t len) {
    if (len < 20) return false;
    uint8_t ihl = (pkt[0] & 0x0F) * 4;
    if (len < ihl + 8) return false;

    uint8_t proto = pkt[9];
    if (proto != 6 && proto != 17) return false;

    uint32_t src_ip = *(uint32_t*)&pkt[12];
    uint32_t dst_ip = *(uint32_t*)&pkt[16];
    uint16_t* src_port_ptr = (uint16_t*)&pkt[ihl];
    uint16_t* dst_port_ptr = (uint16_t*)&pkt[ihl + 2];
    uint16_t src_port = *src_port_ptr;
    uint16_t dst_port = *dst_port_ptr;

    FlowTuple key = { src_ip, dst_ip, src_port, dst_port, proto };
    uint32_t h = hash_tuple(&key);
    NatEntry* entry = nat->reply_buckets[h];

    while (entry) {
        if (tuple_equal(&entry->reply, &key)) break;
        entry = entry->next_reply;
    }

    if (!entry) {
        return false; /* Невідоме вхідне з'єднання: відкидаємо пакет */
    }

    entry->last_seen = time(NULL);
    uint32_t lan_ip = entry->original.src_ip;
    uint16_t lan_port = entry->original.src_port;

    /* Модифікація IP: Destination IP -> LAN IP */
    uint16_t* ip_csum = (uint16_t*)&pkt[10];
    *ip_csum = csum_update_u32(*ip_csum, dst_ip, lan_ip);
    *(uint32_t*)&pkt[16] = lan_ip;

    /* Модифікація L4: Destination Port -> LAN Port */
    if (proto == 6) {
        uint16_t* tcp_csum = (uint16_t*)&pkt[ihl + 16];
        uint16_t c = csum_update_u32(*tcp_csum, dst_ip, lan_ip);
        *tcp_csum = csum_update_u16(c, dst_port, lan_port);
    } else if (proto == 17) {
        uint16_t* udp_csum = (uint16_t*)&pkt[ihl + 6];
        if (*udp_csum != 0x0000) {
            uint16_t c = csum_update_u32(*udp_csum, dst_ip, lan_ip);
            c = csum_update_u16(c, dst_port, lan_port);
            *udp_csum = (c == 0x0000) ? 0xFFFF : c;
        }
    }
    *dst_port_ptr = lan_port;
    return true;
}
```
```cpp
#include <cstdint>
#include <chrono>
#include <vector>
#include <unordered_map>
#include <optional>
#include <span>
#include <memory>

class NatEngine {
public:
    static constexpr uint16_t PortStart = 1024;
    static constexpr uint16_t PortEnd = 65535;

    struct Endpoint {
        uint32_t ip{0};
        uint16_t port{0};

        bool operator==(const Endpoint&) const = default;
    };

    struct FlowTuple {
        Endpoint src;
        Endpoint dst;
        uint8_t  proto{0};

        bool operator==(const FlowTuple&) const = default;
    };

    struct TupleHash {
        std::size_t operator()(const FlowTuple& t) const noexcept {
            std::size_t h1 = (static_cast<std::size_t>(t.src.ip) << 16) ^ t.src.port;
            std::size_t h2 = (static_cast<std::size_t>(t.dst.ip) << 16) ^ t.dst.port;
            return h1 ^ (h2 << 1) ^ (static_cast<std::size_t>(t.proto) << 24);
        }
    };

    struct NatSession {
        FlowTuple original;
        FlowTuple reply;
        uint16_t  assigned_port{0};
        std::chrono::steady_clock::time_point last_seen;
    };

    explicit NatEngine(uint32_t wan_ip)
        : wan_ip_(wan_ip), port_allocated_(PortEnd - PortStart + 1, false) {}

    // Обробка вихідного пакета LAN -> WAN (SNAT)
    bool process_outbound(std::span<uint8_t> packet) {
        if (packet.size() < 20) return false;
        uint8_t ihl = (packet[0] & 0x0F) * 4;
        if (packet.size() < static_cast<std::size_t>(ihl + 8)) return false;

        uint8_t proto = packet[9];
        if (proto != 6 && proto != 17) return false;

        uint32_t src_ip = read_u32(&packet[12]);
        uint32_t dst_ip = read_u32(&packet[16]);
        uint16_t src_port = read_u16(&packet[ihl]);
        uint16_t dst_port = read_u16(&packet[ihl + 2]);

        FlowTuple orig_tuple{ {src_ip, src_port}, {dst_ip, dst_port}, proto };

        auto it = forward_table_.find(orig_tuple);
        if (it == forward_table_.end()) {
            auto port_opt = allocate_port();
            if (!port_opt) return false;

            uint16_t nat_port = *port_opt;
            FlowTuple reply_tuple{ {dst_ip, dst_port}, {wan_ip_, nat_port}, proto };

            NatSession session{
                .original = orig_tuple,
                .reply = reply_tuple,
                .assigned_port = nat_port,
                .last_seen = std::chrono::steady_clock::now()
            };

            auto [ins_it, _] = forward_table_.emplace(orig_tuple, session);
            reverse_table_.emplace(reply_tuple, orig_tuple);
            it = ins_it;
        } else {
            it->second.last_seen = std::chrono::steady_clock::now();
        }

        uint16_t assigned_port = it->second.assigned_port;

        // 1. Модифікація IP-заголовка
        uint16_t ip_csum = read_u16(&packet[10]);
        ip_csum = csum_update_u32(ip_csum, src_ip, wan_ip_);
        write_u16(&packet[10], ip_csum);
        write_u32(&packet[12], wan_ip_);

        // 2. Модифікація L4-заголовка
        if (proto == 6) { // TCP
            uint16_t tcp_csum = read_u16(&packet[ihl + 16]);
            uint16_t c = csum_update_u32(tcp_csum, src_ip, wan_ip_);
            c = csum_update_u16(c, src_port, assigned_port);
            write_u16(&packet[ihl + 16], c);
        } else if (proto == 17) { // UDP
            uint16_t udp_csum = read_u16(&packet[ihl + 6]);
            if (udp_csum != 0x0000) {
                uint16_t c = csum_update_u32(udp_csum, src_ip, wan_ip_);
                c = csum_update_u16(c, src_port, assigned_port);
                write_u16(&packet[ihl + 6], (c == 0x0000) ? 0xFFFF : c);
            }
        }
        write_u16(&packet[ihl], assigned_port);
        return true;
    }

    // Обробка вхідного пакета WAN -> LAN (зворотний DNAT)
    bool process_inbound(std::span<uint8_t> packet) {
        if (packet.size() < 20) return false;
        uint8_t ihl = (packet[0] & 0x0F) * 4;
        if (packet.size() < static_cast<std::size_t>(ihl + 8)) return false;

        uint8_t proto = packet[9];
        if (proto != 6 && proto != 17) return false;

        uint32_t src_ip = read_u32(&packet[12]);
        uint32_t dst_ip = read_u32(&packet[16]);
        uint16_t src_port = read_u16(&packet[ihl]);
        uint16_t dst_port = read_u16(&packet[ihl + 2]);

        FlowTuple reply_key{ {src_ip, src_port}, {dst_ip, dst_port}, proto };

        auto rev_it = reverse_table_.find(reply_key);
        if (rev_it == reverse_table_.end()) {
            return false; // Невідома сесія
        }

        auto fwd_it = forward_table_.find(rev_it->second);
        if (fwd_it == forward_table_.end()) {
            return false;
        }

        fwd_it->second.last_seen = std::chrono::steady_clock::now();
        uint32_t lan_ip = fwd_it->second.original.src.ip;
        uint16_t lan_port = fwd_it->second.original.src.port;

        // 1. Модифікація IP-заголовка: dst_ip -> lan_ip
        uint16_t ip_csum = read_u16(&packet[10]);
        ip_csum = csum_update_u32(ip_csum, dst_ip, lan_ip);
        write_u16(&packet[10], ip_csum);
        write_u32(&packet[16], lan_ip);

        // 2. Модифікація L4-заголовка: dst_port -> lan_port
        if (proto == 6) {
            uint16_t tcp_csum = read_u16(&packet[ihl + 16]);
            uint16_t c = csum_update_u32(tcp_csum, dst_ip, lan_ip);
            *reinterpret_cast<uint16_t*>(&packet[ihl + 16]) = csum_update_u16(c, dst_port, lan_port);
        } else if (proto == 17) {
            uint16_t udp_csum = read_u16(&packet[ihl + 6]);
            if (udp_csum != 0x0000) {
                uint16_t c = csum_update_u32(udp_csum, dst_ip, lan_ip);
                c = csum_update_u16(c, dst_port, lan_port);
                write_u16(&packet[ihl + 6], (c == 0x0000) ? 0xFFFF : c);
            }
        }
        write_u16(&packet[ihl + 2], lan_port);
        return true;
    }

    // Очищення застарілих сесій за тайм-аутом
    void prune_stale_sessions(std::chrono::seconds timeout) {
        auto now = std::chrono::steady_clock::now();
        for (auto it = forward_table_.begin(); it != forward_table_.end(); ) {
            if (now - it->second.last_seen > timeout) {
                uint16_t port = it->second.assigned_port;
                if (port >= PortStart && port <= PortEnd) {
                    port_allocated_[port - PortStart] = false;
                }
                reverse_table_.erase(it->second.reply);
                it = forward_table_.erase(it);
            } else {
                ++it;
            }
        }
    }

private:
    uint32_t wan_ip_;
    std::unordered_map<FlowTuple, NatSession, TupleHash> forward_table_;
    std::unordered_map<FlowTuple, FlowTuple, TupleHash>  reverse_table_;
    std::vector<bool> port_allocated_;
    uint16_t next_port_scan_{0};

    static constexpr uint16_t csum_update_u16(uint16_t old_csum, uint16_t old_val, uint16_t new_val) noexcept {
        uint32_t sum = static_cast<uint32_t>(~old_csum & 0xFFFF) +
                       static_cast<uint32_t>(~old_val & 0xFFFF) +
                       static_cast<uint32_t>(new_val);
        while (sum >> 16) {
            sum = (sum & 0xFFFF) + (sum >> 16);
        }
        return static_cast<uint16_t>(~sum & 0xFFFF);
    }

    static constexpr uint16_t csum_update_u32(uint16_t old_csum, uint32_t old_val, uint32_t new_val) noexcept {
        uint16_t c = csum_update_u16(old_csum, static_cast<uint16_t>(old_val >> 16), static_cast<uint16_t>(new_val >> 16));
        return csum_update_u16(c, static_cast<uint16_t>(old_val & 0xFFFF), static_cast<uint16_t>(new_val & 0xFFFF));
    }

    std::optional<uint16_t> allocate_port() {
        const uint16_t total = PortEnd - PortStart + 1;
        for (uint16_t i = 0; i < total; ++i) {
            uint16_t idx = (next_port_scan_ + i) % total;
            if (!port_allocated_[idx]) {
                port_allocated_[idx] = true;
                next_port_scan_ = (idx + 1) % total;
                return PortStart + idx;
            }
        }
        return std::nullopt;
    }

    static uint16_t read_u16(const uint8_t* p) noexcept {
        return (static_cast<uint16_t>(p[0]) << 8) | p[1];
    }
    static void write_u16(uint8_t* p, uint16_t v) noexcept {
        p[0] = static_cast<uint8_t>(v >> 8);
        p[1] = static_cast<uint8_t>(v & 0xFF);
    }
    static uint32_t read_u32(const uint8_t* p) noexcept {
        return (static_cast<uint32_t>(p[0]) << 24) | (static_cast<uint32_t>(p[1]) << 16) |
               (static_cast<uint32_t>(p[2]) << 8) | p[3];
    }
    static void write_u32(uint8_t* p, uint32_t v) noexcept {
        p[0] = static_cast<uint8_t>(v >> 24);
        p[1] = static_cast<uint8_t>(v >> 16);
        p[2] = static_cast<uint8_t>(v >> 8);
        p[3] = static_cast<uint8_t>(v & 0xFF);
    }
};
```
:::

---

### 4. Покроковий розбір коду та робота з сирими байтами

У наведеній реалізації обидві мовні версії дотримуються єдиної послідовності обробки кожного вхідного кадру:

1. **Валідація мінімального розміру**: перший рядок функції `packet.size() < 20` гарантує, що буфер містить щонайменше базовий заголовок IPv4 без опцій.
2. **Вилучення IHL (Internet Header Length)**: байт `packet[0] & 0x0F` містить довжину IP-заголовка у 32-бітних словах. Множення на 4 дає точне зміщення байтів, з якого починається заголовок транспортного рівня L4 (TCP або UDP).
3. **Фільтрація протоколу**: перевірка байта `packet[9]` (`IPPROTO_TCP = 6`, `IPPROTO_UDP = 17`). Усі інші протоколи (наприклад, GRE, ESP, OSPF) або вимагають специфічної логіки трансляції, або відкидаються.
4. **Вичитування полів із урахуванням порядку байтів**: функції `read_u16` та `read_u32` зчитують байти у мережевому порядку (Big-Endian). У мові C це виконується через пряме розіменування приведення типів `uint32_t*`, а у C++ — через безпечні бітові зсуви над `std::span<uint8_t>`, що унеможливлює помилки порушення вирівнювання пам'яті (англ. *unaligned memory access*).
5. **Двохешовий пошук**: при виявленні нового потоку створюються два симетричні записи у `forward_table_` та `reverse_table_`. Це дозволяє обробляти як вихідні запити, так і вхідні відповіді без сканування масивів за час `O(1)`.

---

### 5. Детальний аналіз пасток реалізації та граничних станів

#### Пастка 1. Вичерпання пулу портів (Port Exhaustion)
Діапазон ефемерних портів `1024..65535` надає 64 512 унікальних номерів на одну публічну IPv4-адресу. Якщо за NAT працює велика корпоративна мережа або кластер мікросервісів, які відкривають тисячі короткоживучих HTTP-запитів без повторного використання з'єднань (HTTP keep-alive), пул портів швидко вичерпується.

Для запобігання відмовам у реальних шлюзах застосовують три механізми:
1. **Портовий мапінг, залежний від адреси призначення (Address-Dependent Mapping)**: один і той самий зовнішній порт `40001` може бути одночасно призначений клієнту `192.168.1.50` (який з'єднується з сервером `93.184.216.34:80`) та клієнту `192.168.1.51` (який з'єднується з іншим сервером `198.51.100.20:443`). У такому разі ключ зворотного пошуку включає не лише `wan_ip:nat_port`, а й `remote_ip:remote_port`, що збільшує ефективну місткість пулу сесій у сотні разів.
2. **Багатоадресний пул (NAT Pool / M:N)**: транслятор має список із кількох публічних IPv4-адрес і циклічно перемикається між ними при заповненні портів поточної адреси.
3. **Агресивне скидання напіввідкритих сесій (SYN-flood mitigation)**: сесії в стані очікування відповіді (SYN_SENT) очищаються за тайм-аутом 10–20 секунд замість стандартних 300 секунд.

#### Пастка 2. Фрагментація IP-дейтаграм
Коли розмір вихідного IP-пакета перевищує MTU мережевого інтерфейсу (наприклад, 1500 байтів для стандартного Ethernet), протокол IP розбиває дейтаграму на декілька фрагментів:
- **Перший фрагмент (`Fragment Offset == 0`, прапорець `MF = 1`)**: містить заголовок IP та заголовок транспортного рівня L4 з номерами портів TCP або UDP. Транслятор зчитує порти, створює запис у таблиці сесій і модифікує заголовок.
- **Наступні фрагменти (`Fragment Offset > 0`)**: **не містять заголовка транспортного рівня L4**! У них присутні лише IP-заголовок та 16-бітне поле ідентифікатора дейтаграми `ip->id`.

Якщо транслятор не підтримує повної збірки дейтаграм (англ. *IP reassembly*), він не знає, якому порту належить другий фрагмент, і не може переписати IP-адресу. 

Для вирішення цієї проблеми мережеві рушії використовують **таблицю стану фрагментів (англ. *fragment tracking table*)**:
1. При отриманні першого фрагмента транслятор запам'ятовує трійку `(src_ip, ip->id, proto)` разом із виділеним зовнішнім портом та новим `ip->id`.
2. При отриманні наступних фрагментів транслятор шукає їх за ідентифікатором дейтаграми `ip->id`, підміняє IP-адресу та інкрементно коригує контрольну суму IP-заголовка без спроби прочитати відсутній транспортний заголовок.

#### Пастка 3. Заворот трафіку всередину (Hairpinning / NAT Loopback)
Коли клієнт усередині локальної мережі `192.168.1.50` намагається отримати доступ до вебсервера `192.168.1.10`, розташованого в тій самій локальній мережі, звертаючись за його публічною доменною назвою (що резолвиться у зовнішню адресу роутера `203.0.113.5:8080`), виникає ситуація так званої «шпильки» (англ. *hairpinning*):
1. Якщо роутер застосує лише **DNAT** (перепише адресу призначення `203.0.113.5` на внутрішню `192.168.1.10`), пакет прийде до локального сервера з адресою джерела `192.168.1.50`.
2. Сервер побачить, що клієнт знаходиться в його ж власній підмережі `192.168.1.0/24`, і надішле відповідь клієнту **напряму через локальний комутатор L2 в обхід роутера**.
3. Клієнт `192.168.1.50` отримає відповідь із джерела `192.168.1.10`, тоді як він відкривав сокет до `203.0.113.5`. Стек TCP клієнта негайно скине це з'єднання пакетом `RST`, оскільки сокет очікував відповідь від іншої IP-адреси.

Для коректної роботи Hairpinning маршрутизатор зобов'язаний застосувати **подвійну трансляцію (Double NAT)**:
- **DNAT**: переписати адресу призначення `203.0.113.5 ➔ 192.168.1.10`;
- **SNAT**: одночасно переписати адресу джерела `192.168.1.50 ➔ 192.168.1.1` (LAN-адресу самого роутера).

У цьому випадку сервер відповість роутеру, а роутер розгорне обидві трансляції у зворотному напрямку і передасть відповідь клієнту з очікуваної публічної адреси `203.0.113.5`.

#### Пастка 4. Протоколи прикладного рівня та шлюзи ALG (Application Layer Gateway)
Складні протоколи прикладного рівня (L7) — такі як FTP у класичному активному режимі `PORT`, SIP (Session Initiation Protocol) або H.323 — передають IP-адреси та порти всередині текстових або бінарних корисних даних пакета.
Якщо транслятор змінить лише L3/L4 заголовки, текстовий рядок `PORT 192,168,1,50,200,5` усередині тіла FTP-пакета залишиться незмінним. Сервер спробує під'єднатися до приватної адреси клієнта та зазнає збою.

Для таких протоколів рушій NAT розширюють модулями **ALG (Application Layer Gateway)**:
- Модуль ALG перехоплює пакети на портах керування (наприклад, TCP 21 для FTP);
- Парсить прикладний протокол та замінює приватну IP:порт у тексті на публічну `wan_ip:nat_port`;
- **Коригує номери послідовностей TCP (Sequence & Acknowledgment Numbers)**: якщо довжина нового текстового рядка відрізняється від старого (наприклад, `203.0.113.5,156,65` має 18 байтів, а `192.168.1.5,10,1` — 15 байтів), розмір TCP-сегмента змінюється на 3 байти. Транслятор повинен запам'ятати цей зсув дельти (`seq_offset += 3`) і коригувати поля `seq` та `ack` у всіх наступних пакетах цієї TCP-сесії!

---

### 6. Сучасне апаратне прискорення: розвантаження в eBPF/XDP та DPDK

У сучасній високопродуктивній інфраструктурі (наприклад, у балансувальниках навантаження Katran від Meta або Cilium у Kubernetes) програмний NAT переносять безпосередньо в драйвер мережевої карти за допомогою технології **eBPF (Extended Berkeley Packet Filter)** та підсистеми **XDP (eXpress Data Path)** або фреймворку **DPDK (Data Plane Development Kit)**.

#### Розвантаження через eBPF/XDP
Програма eBPF завантажується в ядро Linux і виконується на рівні мережевого кільцевого буфера DMA (Rx ring buffer) **до виділення структури ядра `sk_buff` та до входу в мережевий стек ядра**:
1. Програма XDP зчитує 5-компонентний кортеж безпосередньо з пам'яті фізичного кадру `ctx->data`;
2. Виконує пошук у BPF-карті типу `BPF_MAP_TYPE_LRU_HASH`;
3. Викликає вбудовані допоміжні функції ядра `bpf_l3_csum_replace()` та `bpf_l4_csum_replace()`, які реалізують ту саму інкрементну формулу RFC 1624;
4. Повертає вердикт `XDP_TX` (відправити пакет назад у мережевий порт) або `XDP_REDIRECT`.

Така архітектура дозволяє програмному NAT-транслятору обробляти понад 15–20 мільйонів пакетів за секунду (Mpps) на одному сервері, досягаючи повної пропускної здатності оптичних лінків 40G/100G.

#### Розвантаження через DPDK (Data Plane Development Kit)
У середовищах телекомунікаційних операторів (NFV) трансляція NAPT реалізується у просторі користувача за допомогою DPDK:
- Опитування мережевих карт виконується драйверами режиму опитування (англ. *Poll Mode Drivers, PMD*) в обхід переривань операційної системи;
- Пакети обробляються пачками (bursts) у структурах `rte_mbuf` без копіювання пам'яті між ядром та користувацьким додатком (zero-copy);
- Розрахунок контрольних сум дедегується апаратним блокам мережевого адаптера шляхом встановлення прапорців `RTE_MBUF_F_TX_IP_CKSUM` та `RTE_MBUF_F_TX_TCP_CKSUM`.

---

### 7. Інтеграція з віртуальними інтерфейсами Linux TUN/TAP

Щоб запустити цей рушій трансляції у користувацькому просторі операційної системи Linux, його під'єднують до віртуального тунельного інтерфейсу TUN (працює на рівні IP-пакетів L3):

1. Програма відкриває спеціальний пристрій `/dev/net/tun` за допомогою системного виклику `open()`.
2. За допомогою `ioctl(fd, TUNSETIFF, ...)` створюється віртуальний мережевий інтерфейс (наприклад, `tun0`) із прапорцями `IFF_TUN | IFF_NO_PI`.
3. Операційна система призначає інтерфейсу `tun0` маршрутизацію трафіку.
4. Головний цикл програми виконує `read(fd, buffer, sizeof(buffer))`, отримує сирі байти IPv4-пакетів, викликає `process_outbound` або `process_inbound` і відправляє модифіковані кадри назад у стек ядра через `write(fd, buffer, modified_len)`.

Завдяки константній складності `O(1)` для хеш-таблиць та інкрементній арифметиці контрольних сум RFC 1624 такий користувацький транслятор спроможний обробляти понад мільйон пакетів за секунду на одному ядрі сучасного процесора.

---

### 8. Масштабування та багатопотокова архітектура

В однопоточному режимі пропускна здатність програмного NAPT-рушія обмежена продуктивністю одного ядра процесора (близько 1.5–3.0 мільйонів пакетів за секунду). Спроба захистити глобальну хеш-таблицю сесій звичайним м'ютексом (`std::mutex` або `pthread_mutex_t`) під час багатопотокової обробки призводить до катастрофічного падіння швидкості через між'ядерні блокування (англ. *lock contention*).

У промислових системах (DPDK, FD.io VPP) масштабування реалізують за двома підходами:
1. **Шардування таблиці сесій (Per-Core Sharding)**: кожен потік процесора володіє власною ізольованою хеш-таблицею з'єднань та власним неперетинним діапазоном портів (наприклад, Core 0: `1024..16383`, Core 1: `16384..32767`). Завдяки апаратному механізму Receive Side Scaling (RSS) на мережевій карті вхідні пакети направляються в черги відповідних ядер без жодних блокувань.
2. **Блокування RCU (Read-Copy-Update)**: операції пошуку активних сесій (які складають 99% усіх операцій) виконуються повністю без блокувань, а додавання нових з'єднань або оновлення таймерів синхронізуються через атомарні покажчики та покоління RCU.

---

### 9. Методика компіляції, профілювання та тестування

Для перевірки коректності та вимірювання затримок програмного транслятора використовують такий стек інструментів:

#### Компіляція
Компіляція модуля виконується з максимальною оптимізацією та включенням сучасних векторних інструкцій:
```bash
# Компіляція C++ рушія
g++ -O3 -std=c++20 -march=native -Wall -Wextra -pedantic nat_engine.cpp -o nat_engine

# Компіляція C рушія
gcc -O3 -std=c11 -march=native -Wall -Wextra -pedantic nat_engine.c -o nat_engine
```

#### Синтетичне тестування за допомогою Scapy
Для верифікації інкрементного розрахунку контрольних сум створюється тестовий сценарій на мові Python з бібліотекою `scapy`:
- Генерується серія TCP SYN-пакетів із випадковими локальними портами;
- Пакети подаються на вхід `process_outbound()`;
- Перевіряється, що результуючий пакет містить коректну контрольну суму `IP.chksum` та `TCP.chksum`, яка точно збігається з повним еталонним перерахунком Scapy.

#### Профілювання продуктивності
За допомогою утиліти `perf` аналізується розподіл тактів процесора:
```bash
perf record -g ./nat_engine
perf report
```
У правильно спроєктованому NAPT-рушії понад 70% процесорного часу припадає на роботу з кеш-пам'яттю при читанні сирих байтів пакета, тоді як операція інкрементної корекції контрольної суми `csum_update` займає менше 5% тактів.
