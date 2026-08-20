# 📋 Інтерфейс конфігурації L4-балансувальника Katran та структури eBPF

Ця довідка містить специфікацію структур даних площини керування (Control Plane) та площини даних (Data Plane) L4-балансувальника Katran, розбір форматів eBPF-карт пам'яті ядра Linux, правила конфігурації віртуальних IP-адрес (VIP), програмний C++ інтерфейс бібліотеки та специфікацію утиліти командного рядка `katran_ctl`.

---

### 1. Структури даних площини даних (Data Plane eBPF)

Драйвер XDP виконує BPF-програму на найранішому етапі отримання пакета мережевою картою, до створення важкої структури ядра `sk_buff`. Для обробки потоків використовуються бінарні структури з фіксованим вирівнюванням пам'яті, сумісні як із C, так і з сучасним C++.

:::tabs
```c
#include <linux/types.h>

/* Ідентифікатор віртуального сервісу (VIP Key) */
struct vip_definition {
    __u32 vip;          /* IPv4-адреса або префікс IPv6 у мережевому порядку байтів */
    __u16 port;         /* Порт сервісу (наприклад, 80, 443) */
    __u8  proto;        /* Протокол транспортного рівня (IPPROTO_TCP або IPPROTO_UDP) */
    __u8  flags;        /* Прапорці поведінки (VIP_FLAG_QUIC, VIP_FLAG_DSR) */
};

/* Метадані віртуального сервісу (VIP Value) */
struct vip_meta {
    __u32 flags;        /* Режими маршрутизації: DSR, GUE, IPIP */
    __u32 table_size;   /* Розмір активної таблиці Maglev (зазвичай 65537) */
    __u32 vip_num;      /* Внутрішній числовий ідентифікатор VIP */
};

/* Дескриптор цільового сервера (Real Backend Definition) */
struct real_definition {
    __u32 address;      /* IPv4/IPv6-адреса реального сервера */
    __u32 flags;        /* Прапорці доступності та типу тунелювання */
    __u16 port;         /* Цільовий порт на бекенді */
    __u8  weight;       /* Відносна вага сервера в таблиці Maglev */
    __u8  pad;
};

/* Ключ потоку для таблиці сесій (Flow Key) */
struct flow_key {
    __u32 src;          /* IP-адреса клієнта */
    __u32 dst;          /* VIP-адреса балансувальника */
    __u16 src_port;     /* Порт клієнта */
    __u16 dst_port;     /* Порт сервісу */
    __u8  proto;        /* TCP / UDP */
    __u8  pad[3];
};

/* Запис у таблиці активних сесій (Flow Value) */
struct flow_value {
    __u32 backend_idx;  /* Індекс сервера в масиві реальних серверів */
    __u64 last_seen;    /* Часова мітка останнього пакета в наносекундах */
};
```
```cpp
#include <cstdint>
#include <string>
#include <string_view>
#include <array>

namespace katran {

enum class Protocol : uint8_t {
    Tcp = 6,
    Udp = 17
};

enum class VipFlags : uint32_t {
    DirectServerReturn = 1 << 0,
    GenericUdpEncapsulation = 1 << 1,
    IpInIp = 2 << 2,
    QuicConnectionIdRouting = 1 << 3
};

struct VipDefinition {
    uint32_t vip{0};
    uint16_t port{0};
    Protocol proto{Protocol::Tcp};
    uint8_t flags{0};
};

struct VipMeta {
    VipFlags flags{VipFlags::DirectServerReturn};
    uint32_t table_size{65537};
    uint32_t vip_num{0};
};

struct RealDefinition {
    uint32_t address{0};
    uint32_t flags{0};
    uint16_t port{0};
    uint8_t weight{1};
    uint8_t pad{0};
};

struct FlowKey {
    uint32_t src{0};
    uint32_t dst{0};
    uint16_t src_port{0};
    uint16_t dst_port{0};
    Protocol proto{Protocol::Tcp};
    std::array<uint8_t, 3> pad{};
};

struct FlowValue {
    uint32_t backend_idx{0};
    uint64_t last_seen_ns{0};
};

} // namespace katran
```
:::

---

### 2. Специфікація eBPF-карт пам'яті (BPF Maps)

Балансувальник Katran створює та адмініструє п'ять спеціалізованих карт пам'яті BPF у ядрі Linux. Кожна карта оптимізована під конкретний шаблон доступу під час обробки пакетів:

| Назва карти BPF | Тип карти ядра | Тип ключа | Тип значення | Макс. елементів | Призначення |
|---|---|---|---|---|---|
| `vip_map` | `BPF_MAP_TYPE_HASH` | `struct vip_definition` | `struct vip_meta` | `512` | Зіставлення вхідного трафіку з зареєстрованими сервісами |
| `lut_ring` | `BPF_MAP_TYPE_ARRAY` | `__u32` (Індекс слота) | `__u32` (Backend ID) | `65537` | Статична таблиця пошуку Maglev (`M = 65537`) |
| `lru_cache` | `BPF_MAP_TYPE_LRU_HASH` | `struct flow_key` | `struct flow_value` | `10 000 000` | Кеш відкритих TCP/UDP сесій з автоматичним витісненням |
| `reals_map` | `BPF_MAP_TYPE_ARRAY` | `__u32` (Backend ID) | `struct real_definition` | `4096` | Таблиця IP-адрес і MAC-адрес реальних серверів |
| `stats_map` | `BPF_MAP_TYPE_PERCPU_ARRAY`| `__u32` (Тип метрики) | `__u64` (Лічильник) | `64` | Поядерна статистика оброблених пакетів та помилок |

#### Механіка взаємодії карт під час обробки трафіку

1. **Карта відповідності сервісів (`vip_map`):**
   Карта типу `BPF_MAP_TYPE_HASH` містить перелік усіх зареєстрованих віртуальних IP-адрес та портів. Коли пакет надходить на мережеву карту, BPF-програма формує ключ пошуку з адреси призначення, порту та протоколу. Якщо запис знайдено, програма отримує числовий номер `vip_num` та прапорці тунелювання. Якщо адреси немає в карті, пакет вважається призначеним локальному стеку операційної системи (наприклад, SSH або протокол BGP) і передається ядру без змін (`XDP_PASS`).

2. **Таблиця підстановки Maglev (`lut_ring`):**
   Карта типу `BPF_MAP_TYPE_ARRAY` розміром `65537` комірок зберігає цілочисельні індекси цільових бекендів. Доступ до карти здійснюється за фіксованим зсувом пам'яті без прорахунку хеш-ланцюжків. Оскільки розмір карти зафіксовано на етапі ініціалізації, верифікатор BPF гарантує повну безпеку доступу до пам'яті через маскування індексу.

3. **Кеш активних потоків (`lru_cache`):**
   Карта типу `BPF_MAP_TYPE_LRU_HASH` реалізує автоматичне видалення найстаріших з'єднань за алгоритмом LRU (англ. *Least Recently Used*). Кожне нове TCP-з'єднання додається в кеш після первинного обчислення Maglev. Це дозволяє наступним пакетам з'єднання проходити диспетчеризацію без повторного виклику хеш-функції. Якщо кластер зазнає масованої атаки SYN-Flood, карта не переповнюється з аварійною зупинкою: старі незавершені сесії плавно витісняються новими, а легітимні потоки утримуються завдяки регулярному оновленню поля `last_seen`.

4. **Масив дескрипторів бекендів (`reals_map`):**
   Карта зберігає фізичні IP-адреси серверів-обробників, порти призначення та прапорці доступності. Після того як алгоритм визначив індекс сервера `backend_idx`, BPF-програма вичитує структуру `real_definition` для підготовки заголовка інкапсуляції.

5. **Поядерні лічильники продуктивності (`stats_map`):**
   Використання типу `BPF_MAP_TYPE_PERCPU_ARRAY` гарантує, що кожне процесорне ядро оновлює власну копію лічильників у локальній пам'яті без застосування атомарних інструкцій процесора `LOCK XADD`. Це усуває паразитний трафік шини між процесорами під час зняття метрик на швидкостях 100 Gbps.

---

### 3. Програмний інтерфейс бібліотеки `KatranLb` (C++)

Площина керування реалізована у вигляді C++ бібліотеки, яка керує життєвим циклом BPF-програм через інтерфейс системного виклику `bpf()`.

:::tabs
```cpp
#include <string>
#include <vector>
#include <cstdint>
#include <optional>
#include <string_view>

namespace katran {

enum class ForwardingMode : uint32_t {
    DirectServerReturn = 0,
    GenericUdpEncapsulation = 1,
    IpInIp = 2
};

struct VipConfig {
    std::string vip_address;
    uint16_t port{443};
    uint8_t protocol{6}; // TCP
    ForwardingMode mode{ForwardingMode::GenericUdpEncapsulation};
    uint32_t ring_size{65537};
};

struct BackendConfig {
    std::string address;
    uint16_t port{443};
    uint32_t weight{1};
    bool enabled{true};
};

class KatranLb {
public:
    KatranLb() = default;
    ~KatranLb() = default;

    // Завантаження скомпільованого eBPF байткоду в драйвер мережевої карти
    bool attach_to_interface(std::string_view ifname);

    // Від'єднання BPF програми та очищення карт пам'яті
    bool detach_from_interface(std::string_view ifname);

    // Реєстрація нового віртуального сервісу (VIP)
    bool add_vip(const VipConfig& vip);

    // Видалення віртуального сервісу та звільнення пов'язаних таблиць
    bool remove_vip(const VipConfig& vip);

    // Додавання реального сервера до пулу зазначеного VIP
    bool add_backend_to_vip(const VipConfig& vip, const BackendConfig& backend);

    // Видалення сервера з пулу VIP
    bool remove_backend_from_vip(const VipConfig& vip, const BackendConfig& backend);

    // Зміна відносної ваги сервера на льоту
    bool modify_backend_weight(const VipConfig& vip, std::string_view backend_addr, uint32_t new_weight);

    // Примусова перебудова таблиці Maglev та оновлення BPF Array Map
    bool recalculate_maglev_ring(const VipConfig& vip);

    // Зчитування лічильників продуктивності з BPF Per-CPU Map
    [[nodiscard]] uint64_t get_total_packets_forwarded() const noexcept;
    [[nodiscard]] uint64_t get_lru_miss_count() const noexcept;
    [[nodiscard]] uint64_t get_lru_hit_count() const noexcept;
};

} // namespace katran
```
```c
#include <stdint.h>
#include <stdbool.h>

/* C-сумісний процедурний інтерфейс для інтеграції з FFI та системними демонами */

typedef struct katran_handle katran_handle_t;

katran_handle_t* katran_create(void);
void katran_destroy(katran_handle_t *h);

bool katran_attach_interface(katran_handle_t *h, const char *ifname);
bool katran_detach_interface(katran_handle_t *h, const char *ifname);

bool katran_add_vip_raw(katran_handle_t *h, uint32_t vip, uint16_t port, uint8_t proto, uint32_t mode);
bool katran_remove_vip_raw(katran_handle_t *h, uint32_t vip, uint16_t port, uint8_t proto);

bool katran_add_backend_raw(katran_handle_t *h, uint32_t vip, uint16_t port, uint8_t proto,
                            uint32_t backend_ip, uint16_t backend_port, uint32_t weight);
bool katran_rebuild_maglev_table(katran_handle_t *h, uint32_t vip, uint16_t port, uint8_t proto);
```
:::

---

### 4. Інтерфейс утиліти командного рядка `katran_ctl`

Утиліта `katran_ctl` призначена для системного адміністрування, автоматизації релізів, динамічного зняття метрик та інтеграції з демонами перевірки стану вузлів (Health Checkers).

#### Керування віртуальними сервісами (VIP)

```bash
# Додавання нового віртуального сервісу HTTPS з режимом GUE
katran_ctl vip add --ip 198.51.100.1 --port 443 --proto tcp --mode gue

# Перегляд списку зареєстрованих сервісів
katran_ctl vip list
```

Зразок виводу списку VIP:
```text
VIP Address      Port  Proto  Mode  Ring Size  Active Reals
198.51.100.1     443   TCP    GUE   65537      12
198.51.100.2     80    TCP    DSR   65537      8
```

#### Керування пулом серверів та плавне виведення (Graceful Drain)

Коли бекенд потребує перезавантаження або оновлення ПЗ, його статус змінюється на вимкнений (`disable`). Алгоритм Maglev негайно перераховує таблицю `lut_ring` без цього сервера. Проте наявні TCP-сесії в таблиці `lru_cache` продовжують надсилатися на цей бекенд до їхнього природного завершення (обміну пакетами `FIN`/`ACK`), що запобігає обриву з'єднань користувачів:

```bash
# Додавання сервера з вагою 2 до пулу сервісу
katran_ctl real add --vip 198.51.100.1:443:tcp --ip 10.0.1.10 --weight 2

# Плавне виведення сервера з експлуатації (Drain traffic)
katran_ctl real disable --vip 198.51.100.1:443:tcp --ip 10.0.1.10

# Зміна ваги сервера без переривання трафіку
katran_ctl real set-weight --vip 198.51.100.1:443:tcp --ip 10.0.1.10 --weight 4
```

#### Моніторинг та зняття телеметрії

```bash
# Перегляд детальної статистики продуктивності в реальному часі
katran_ctl stats show
```

Зразок виводу телеметрії:
```text
XDP Interface: eth0 (Driver Native Mode)
Packets/sec: 38,420,110 pkts/s (38.42 Mpps)
Throughput: 94.8 Gbps
LRU Flow Cache Hit Rate: 91.4%
Maglev Table Lookups (Cache Miss): 8.6%
Packet Drops (Malformed / No VIP): 0
```

---

### 5. Інтеграція з демонами BGP Anycast та Health Checking

Для запобігання ситуації «чорної діри» (коли L4-балансувальник приваблює трафік на VIP, для якого немає живих бекендів), керівний демон Katran інтегрується з демоном динамічної маршрутизації BGP (наприклад, BIRD або FRRouting):

1. **Моніторинг сумарної ваги сервісу:**
   Якщо сумарна вага доступних серверів `∑ W[i]` для певного VIP опускається нижче заданого порогу (наприклад, менше 20% від номінальної місткості), площина керування автоматично видаляє префікс цієї IP-адреси з локального анонсу BGP Anycast.
2. **Перенаправлення на рівні глобальної мережі:**
   Прикордонні маршрутизатори Інтернету фіксують відкликання маршруту через BGP і плавно перенаправляють нові з'єднання користувачів на сусідній найближчий дата-центр компанії, де сервіс має достатню кількість працездатних серверів.

---

### 6. Коди помилок та інваріанти конфігурації

1. `ERR_INVALID_M_SIZE`: розмір таблиці `table_size` обов'язково має бути простим числом. Спроба передати парне або складене число відхиляється валідатором площини керування, оскільки це порушує теорему про взаємну простоту кроку й модуля.
2. `ERR_NO_ACTIVE_REALS`: якщо всі сервери у пулі позначені як вимкнені (`enabled = false`), BPF-програма не відкидає пакети мовчки, а передає їх у локальний стек ядра Linux (`XDP_PASS`) або надсилає клієнту ICMP-повідомлення про недосяжність порту.
3. `ERR_REALS_OVERFLOW`: кількість реальних серверів для одного VIP не може перевищувати `4096` через фіксований розмір масиву дескрипторів `reals_map`.
4. `ERR_BPF_VERIFIER_FAILURE`: при завантаженні нових версій BPF-програм верифікатор ядра Linux перевіряє гарантію обмеженості всіх циклів та відсутність виходу за межі пам'яті пакетного буфера.
5. `ERR_MAP_LOOKUP_FAILED`: повертається у разі спроби зчитування даних неіснуючого VIP або некоректного дескриптора файлу BPF-карти.
6. `ERR_NUMA_NODE_MISMATCH`: виникає, якщо пам'ять карти `lut_ring` алокована на іншій NUMA-ноді, ніж мережевий адаптер, що призводить до падіння пропускної здатності на 15–20%.
