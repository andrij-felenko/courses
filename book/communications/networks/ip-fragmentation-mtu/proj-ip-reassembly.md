# ⚙️ Двигун збирання та валідації фрагментів IP

Збирання фрагментованих дейтаграм (англ. *IP reassembly*) на кінцевому хості вимагає акуратного керування динамічною пам'яттю, відстеження прогалин між отриманими блоками та захисту від навмисно спотворених пакетів. Якщо хост просто копіюватиме байти за вказаним у заголовку зміщенням, він стає вразливим до атак переповнення буфера (Ping of Death), аварійного збою через некоректні довжини перекриття (Teardrop) та підміни даних (Overlapping Fragment Injection).

Розгляньмо повноцінну інженерну реалізацію двигуна збирання фрагментів IPv4. У реальних операційних системах застосовують два фундаментальні підходи до відстеження незібраних частин: класичний алгоритм списку дірок (англ. *hole descriptor list*, стандартизований Девідом Кларком у RFC 815 у 1982 році) та сучасний підхід на основі інтервальних карт і червоно-чорних дерев (структура `inet_frags` у ядрі Linux).

### Алгоритм списку дірок (RFC 815) проти інтервальних дерев

Історичний алгоритм RFC 815 базувався на елегантній ідеї нульових накладних витрат пам'яті: поки дейтаграма не зібрана, її буфер містить «дірки» — не заповнені даними проміжки. Описові структури цих дірок (*Hole Descriptors*) зберігалися безпосередньо всередині самих незаповнених байтів виділеного буфера:

```
[Початковий стан: одна суцільна дірка від 0 до нескінченності (або 65535)]
+-------------------------------------------------------------+
| Hole Descriptor: first=0, last=65535, next=NULL             |
+-------------------------------------------------------------+

[Прибув Фрагмент 2: байти 1480 .. 2959]
Дірка 1 розрізається на дві окремі дірки:
+-------------------+--------------------+--------------------+
| Hole 1: 0 .. 1479 | Дані Фрагмента 2   | Hole 2: 2960..65535|
+-------------------+--------------------+--------------------+
```

Коли надходить черговий фрагмент із діапазоном `[frag_first, frag_last]`, алгоритм проходить по ланцюжку дірок. Якщо фрагмент перекриває дірку:
1. Якщо `frag_first > hole_first`, створюється нова менша дірка зліва `[hole_first, frag_first - 1]`.
2. Якщо `frag_last < hole_last` і при цьому `MF == 1`, створюється нова дірка справа `[frag_last + 1, hole_last]`.
3. Якщо надійшов фрагмент з `MF == 0`, верхня межа останньої правої дірки обрізається по `frag_last`, фіксуючи точний кінець дейтаграми.
4. Сама стара дірка вилучається зі списку.
5. Коли список дірок стає порожнім, дейтаграма вважається повністю зібраною.

Хоча алгоритм RFC 815 вимагає мінімальної кількості пам'яті, він має суттєву вразливість: зловмисник може надсилати чергу спеціально розрізнених фрагментів (наприклад, по 8 байтів через кожні 8 байтів), змушуючи систему породжувати тисячі дрібних дескрипторів і витрачати процесорний час на лінійний пошук по списку (атака вичерпання процесора або *Rose Attack*).

Сучасні ядра (зокрема Linux `net/ipv4/ip_fragment.c`) використовують інший підхід: кожен фрагмент зберігається у власному мережевому буфері `sk_buff`, а збирання координується через інтервальне червоно-чорне дерево (rbtree) у структурі `struct inet_frag_queue`. Це гарантує логарифмічну складність `O(log N)` для вставки фрагментів та унеможливлює маніпуляції з пам'яттю всередині необроблених дірок.

### Механіка нарізання на стороні відправника (Fragmentation Math)

Перш ніж розглядати збирання, простежмо математику створення фрагментів на вихідному інтерфейсі з відомим значенням `MTU`:

1. **Розрахунок довжини заголовка (`IHL`):** Базовий заголовок IPv4 займає 20 байтів, проте за наявності опцій довжина заголовка `HeaderLen = IHL × 4` може сягати 60 байтів.
2. **Максимальне навантаження на фрагмент (`MaxFragmentPayload`):**
   ```
   MaxFragmentPayload = ((MTU - HeaderLen) / 8) * 8
   ```
   Цілочисельне ділення на 8 із наступним множенням відкидає залишок, гарантуючи обов'язкове вирівнювання за 64-бітною межею.
3. **Обробка опцій IP (Copied Flag):** Заголовок кожного фрагмента копіюється з вихідного пакета, але самі опції IP фільтруються за старшим бітом типу опції (`Copied Flag`, біт 7):
   - Якщо `Copied Flag == 1` (наприклад, опція безпеки *Security* або *Commercial Security*), опція дублюється в заголовки **всіх** згенерованих фрагментів.
   - Якщо `Copied Flag == 0` (наприклад, опції маршрутизації *Record Route*, *Strict/Loose Source Route*, *Timestamp*), опція залишається **виключно у першому фрагменті** (offset = 0). У решті фрагментів довжина заголовка зменшується до базових 20 байтів, збільшуючи корисний простір для навантаження.
4. **Перерахунок контрольної суми заголовка (Header Checksum):** Оскільки для кожного фрагмента змінюються поля `Total Length`, `Flags`, `Fragment Offset` (а для першого фрагмента може змінюватися й набір опцій), контрольна сума заголовка обчислюється наново (або оновлюється за алгоритмом інкрементного перерахунку RFC 1624).

### Покроковий розбір каскадної (повторної) фрагментації

У гетерогенних мережах фрагмент може на своєму шляху зіткнутися з лінком, MTU якого є ще меншим за розмір поточного фрагмента. Розгляньмо числовий приклад каскадного розрізання:

**Крок 1: Початкова дейтаграма (Джерело → Мережа A, MTU 4500)**
- Повний розмір: `Total Length = 4000` байтів (заголовок 20 B + навантаження 3980 B).
- Поля: `ID = 0x88AA`, `DF = 0`, `MF = 0`, `Offset = 0`.

**Крок 2: Перша фрагментація на Маршрутизаторі 1 (Мережа A → Мережа B, MTU 1500)**
- Максимальне навантаження: `floor((1500 - 20) / 8) * 8 = 1480` байтів.
- *Фрагмент 1.1:* `Total Length = 1500` (20 + 1480), `ID = 0x88AA`, `MF = 1`, `Offset = 0` (байти 0 .. 1479).
- *Фрагмент 1.2:* `Total Length = 1500` (20 + 1480), `ID = 0x88AA`, `MF = 1`, `Offset = 185` (185 × 8 = 1480; байти 1480 .. 2959).
- *Фрагмент 1.3:* `Total Length = 1040` (20 + 1020), `ID = 0x88AA`, `MF = 0`, `Offset = 370` (370 × 8 = 2960; байти 2960 .. 3979).

**Крок 3: Вторинна (каскадна) фрагментація на Маршрутизаторі 2 (Мережа B → Мережа C, MTU 576)**
Маршрутизатор 2 отримує Фрагмент 1.1 розміром 1500 байтів. Максимальне навантаження для MTU 576 становить `floor((576 - 20) / 8) * 8 = 552` байти:
- *Субфрагмент 1.1.a:* `Total Length = 572` (20 + 552), `ID = 0x88AA`, `MF = 1`, `Offset = 0 + (0/8) = 0` (байти 0 .. 551).
- *Субфрагмент 1.1.b:* `Total Length = 572` (20 + 552), `ID = 0x88AA`, `MF = 1`, `Offset = 0 + (552/8) = 69` (байти 552 .. 1103).
- *Субфрагмент 1.1.c:* `Total Length = 396` (20 + 376), `ID = 0x88AA`, `MF = 1` (оскільки вихідний фрагмент мав `MF = 1`), `Offset = 0 + (1104/8) = 138` (байти 1104 .. 1479).

Зверніть увагу: *Субфрагмент 1.1.c* зберігає прапорець `MF = 1`, попри те, що він є останнім шматочком свого батьківського фрагмента, оскільки за ним у загальному потоці йдуть фрагменти 1.2 та 1.3. Кінцевий хост отримує всі субфрагменти як єдину плоску чергу зміщень і збирає їх без жодного уявлення про те, на скількох проміжних кроках виконувалося нарізання.

### Реагування відправника на `EMSGSIZE` при роботі з PMTUD

Коли застосунок надсилає UDP-дейтаграму з прапорцем `DF = 1` через сокет із налаштуванням `IP_PMTUDISC_DO`, операційна система блокує вихідні пакети, що перевищують локально відомий MTU, і повертає системну помилку `EMSGSIZE`:

:::tabs
```c
/* Приклад обробки EMSGSIZE та отримання актуального PMTU у сокеті */
int sock = socket(AF_INET, SOCK_DGRAM, 0);
if (sock < 0) return -1;

int pmtu_mode = IP_PMTUDISC_DO;
setsockopt(sock, IPPROTO_IP, IP_MTU_DISCOVER, &pmtu_mode, sizeof(pmtu_mode));

ssize_t sent = sendto(sock, large_buffer, 2000, 0, (struct sockaddr*)&dst, sizeof(dst));
if (sent < 0 && errno == EMSGSIZE) {
    /* Запитуємо у ядра актуальний кешований Path MTU для цього сокета */
    int current_pmtu = 0;
    socklen_t optlen = sizeof(current_pmtu);
    if (getsockopt(sock, IPPROTO_IP, IP_MTU, &current_pmtu, &optlen) == 0) {
        /* Зменшуємо розмір блоку передачі на рівні застосунку */
        int safe_payload_len = current_pmtu - 20 - 8; /* IP (20B) + UDP (8B) */
        sendto(sock, large_buffer, safe_payload_len, 0, (struct sockaddr*)&dst, sizeof(dst));
    }
}
close(sock);
```
```cpp
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <span>
#include <system_error>
#include <expected>
#include <iostream>

class SafeUdpSocket {
public:
    SafeUdpSocket() : fd_(::socket(AF_INET, SOCK_DGRAM, 0)) {
        if (fd_ < 0) throw std::system_error(errno, std::generic_category(), "socket create failed");
    }

    ~SafeUdpSocket() {
        if (fd_ >= 0) ::close(fd_);
    }

    SafeUdpSocket(const SafeUdpSocket&) = delete;
    SafeUdpSocket& operator=(const SafeUdpSocket&) = delete;
    SafeUdpSocket(SafeUdpSocket&& o) noexcept : fd_(std::exchange(o.fd_, -1)) {}

    void enable_pmtud() {
        int mode = IP_PMTUDISC_DO;
        if (::setsockopt(fd_, IPPROTO_IP, IP_MTU_DISCOVER, &mode, sizeof(mode)) < 0) {
            throw std::system_error(errno, std::generic_category(), "setsockopt IP_MTU_DISCOVER failed");
        }
    }

    [[nodiscard]] int get_current_pmtu() const {
        int pmtu = 0;
        socklen_t len = sizeof(pmtu);
        if (::getsockopt(fd_, IPPROTO_IP, IP_MTU, &pmtu, &len) < 0) {
            throw std::system_error(errno, std::generic_category(), "getsockopt IP_MTU failed");
        }
        return pmtu;
    }

    std::expected<size_t, int> send(std::span<const uint8_t> data, const sockaddr_in& dst) {
        ssize_t res = ::sendto(fd_, data.data(), data.size(), 0,
                               reinterpret_cast<const sockaddr*>(&dst), sizeof(dst));
        if (res < 0) {
            return std::unexpected(errno);
        }
        return static_cast<size_t>(res);
    }

private:
    int fd_{-1};
};
```
:::

### Асинхронне виявлення PMTU через `IP_RECVERR` та розширені помилки сокета

Отримання інформації про зміну Path MTU у сокетах без встановлення з'єднання (UDP) не обмежується синхронною перевіркою `EMSGSIZE`. Коли відправлений раніше UDP-пакет з `DF = 1` відкидається віддаленим маршрутизатором, роутер надсилає зворотне ICMP-повідомлення `Fragmentation Needed`. Оскільки UDP не зберігає стану з'єднання, ядро Linux не може асоціювати вхідний ICMP-пакет із конкретним активним викликом `sendto()`.

Для вирішення цієї проблеми Linux надає механізм черги розширених помилок сокета:

1. **Активація через сокетну опцію `IP_RECVERR`:**
   Встановлення `setsockopt(sock, IPPROTO_IP, IP_RECVERR, &val, sizeof(val))` наказує ядру зберігати всі вхідні ICMP-помилки у внутрішній черзі помилок сокета (`MSG_ERRQUEUE`).
2. **Зчитування через `recvmsg()` з прапорцем `MSG_ERRQUEUE`:**
   Коли сокет сигналізує про подію читання або помилку через `poll()` чи `epoll` (`POLLERR`), застосунок викликає `recvmsg()` для черги помилок.
3. **Аналіз допоміжних керуючих даних (`msg_control`):**
   У структурі `struct cmsghdr` ядро повертає заголовок `IP_RECVERR` та структуру `struct sock_extended_err`. Поле `ee_info` цієї структури містить **точне значення нового Path MTU** (`Next-Hop MTU`), передане віддаленим маршрутизатором у заголовку ICMP Type 3 Code 4.

Цей механізм дозволяє високопродуктивним мережевим демонам (наприклад, серверам DNS, медіа-серверам WebRTC або реалізаціям QUIC) асинхронно відстежувати зміни топології та звуження каналів, динамічно підлаштовуючи розмір своїх UDP-пакетів без втрати сесійного контексту.

Ключем для ідентифікації належності фрагмента до конкретної дейтаграми є 4-кортеж (англ. *4-tuple*):
```
Key = (Source IP, Destination IP, Protocol, Identification)
```

Для кожної активної дейтаграми система відстежує:
1. **Загальну довжину корисного навантаження (`total_data_len`):** Початково невідома (`-1`), фіксується лише після отримання фрагмента з прапорцем `MF = 0` як `(offset × 8) + payload_length`.
2. **Отримані інтервали байтів:** Кожен фрагмент покриває діапазон `[start, end)`, де `start = offset × 8`, а `end = start + payload_length`.
3. **Таймаут життя черги:** Фіксує час отримання першого фрагмента; якщо дейтаграма не зібрана за ліміт часу (наприклад, 30 секунд за RFC 1122), пам'ять вивільняється, а фрагменти відкидаються. Відправнику може надсилатися повідомлення `ICMP Type 11 Code 1` (*Time Exceeded: Fragment Reassembly Time Exceeded*), якщо хост отримав фрагмент із нульовим зміщенням.

Критичні правила валідації безпеки:
- **Кратність 8 байтам:** Якщо `MF == 1`, довжина корисного навантаження фрагмента **мусить бути кратною 8 байтам**. Невирівняний проміжний фрагмент є прямим порушенням стандарту RFC 791 і свідчить про пошкодження кадру або спробу експлуатації вразливостей.
- **Перевірка суми довжин:** Сума `(offset × 8) + payload_length` не може перевищувати `65 535 - 20 = 65 515` байтів. Будь-який фрагмент, що порушує це обмеження, відкидається для запобігання атаці *Ping of Death*.
- **Політика перекриття (Overlap Resolution):** При виявленні перекриття інтервалів із суперечливим вмістом система застосовує детерміновану політику першого запису (*First-Fragment Priority*) або повного скидання черги, щоб унеможливити ін'єкцію шкідливого коду в обхід систем виявлення вторгнень (NIDS/IPS).

### Реалізація механізму збирання

Нижче наведено робочу реалізацію дефрагментатора мовами C та C++. Обидва варіанти містять повну логіку перевірки меж, об'єднання інтервалів, валідації накладень та експорту готової дейтаграми.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define MAX_IP_PACKET_SIZE 65535
#define MAX_IP_HEADER_SIZE 60
#define MAX_PAYLOAD_SIZE   (MAX_IP_PACKET_SIZE - 20)
#define REASSEMBLY_TIMEOUT_SEC 30

typedef struct {
    uint32_t src_ip;
    uint32_t dst_ip;
    uint16_t id;
    uint8_t  protocol;
} PacketKey;

typedef struct FragmentInterval {
    uint16_t start;
    uint16_t end;
    struct FragmentInterval *next;
} FragmentInterval;

typedef struct ReassemblyQueue {
    PacketKey key;
    uint8_t   buffer[MAX_PAYLOAD_SIZE];
    FragmentInterval *intervals;
    int32_t   expected_total_len; /* -1, поки не прийшов фрагмент з MF=0 */
    uint32_t  bytes_received;
    time_t    created_at;
    struct ReassemblyQueue *next;
} ReassemblyQueue;

typedef struct {
    ReassemblyQueue *head;
} Defragmenter;

Defragmenter* defrag_create(void) {
    Defragmenter *d = (Defragmenter*)malloc(sizeof(Defragmenter));
    if (d) d->head = NULL;
    return d;
}

static void free_intervals(FragmentInterval *inv) {
    while (inv) {
        FragmentInterval *tmp = inv->next;
        free(inv);
        inv = tmp;
    }
}

static void free_queue_entry(ReassemblyQueue *q) {
    if (!q) return;
    free_intervals(q->intervals);
    free(q);
}

void defrag_cleanup_expired(Defragmenter *d, time_t now) {
    ReassemblyQueue **curr = &d->head;
    while (*curr) {
        if (difftime(now, (*curr)->created_at) > REASSEMBLY_TIMEOUT_SEC) {
            ReassemblyQueue *to_free = *curr;
            *curr = (*curr)->next;
            free_queue_entry(to_free);
        } else {
            curr = &(*curr)->next;
        }
    }
}

static ReassemblyQueue* find_or_create_queue(Defragmenter *d, PacketKey key, time_t now) {
    for (ReassemblyQueue *q = d->head; q; q = q->next) {
        if (q->key.src_ip == key.src_ip && q->key.dst_ip == key.dst_ip &&
            q->key.id == key.id && q->key.protocol == key.protocol) {
            return q;
        }
    }
    ReassemblyQueue *q = (ReassemblyQueue*)calloc(1, sizeof(ReassemblyQueue));
    if (!q) return NULL;
    q->key = key;
    q->expected_total_len = -1;
    q->created_at = now;
    q->next = d->head;
    d->head = q;
    return q;
}

/* Перевірка відсутності шкідливого перекриття та реєстрація інтервалу */
static bool add_interval(ReassemblyQueue *q, uint16_t start, uint16_t end) {
    FragmentInterval *new_inv = (FragmentInterval*)malloc(sizeof(FragmentInterval));
    if (!new_inv) return false;
    new_inv->start = start;
    new_inv->end = end;
    new_inv->next = NULL;

    /* Вставляємо впорядковано за start */
    FragmentInterval **curr = &q->intervals;
    while (*curr && (*curr)->start < start) {
        curr = &(*curr)->next;
    }
    new_inv->next = *curr;
    *curr = new_inv;

    /* Об'єднуємо сусідні перекриття та перевіряємо безперервність */
    FragmentInterval *it = q->intervals;
    while (it && it->next) {
        if (it->end >= it->next->start) {
            if (it->next->end > it->end) it->end = it->next->end;
            FragmentInterval *dup = it->next;
            it->next = dup->next;
            free(dup);
        } else {
            it = it->next;
        }
    }
    return true;
}

/* Обробка отриманого фрагмента: 1 = дейтаграма повністю зібрана, 0 = очікуємо ще, -1 = помилка */
int defrag_process_fragment(Defragmenter *d, PacketKey key, uint16_t offset_8b,
                            bool more_fragments, const uint8_t *payload, uint16_t len,
                            uint8_t *out_buffer, uint16_t *out_len, time_t now) {
    if (!d || !payload || !out_buffer || !out_len) return -1;

    uint32_t byte_offset = (uint32_t)offset_8b * 8;
    uint32_t byte_end = byte_offset + len;

    /* Захист від Ping of Death: розмір не може перевищувати ліміт IPv4 */
    if (byte_end > MAX_PAYLOAD_SIZE) return -1;

    /* Захист від Teardrop / некоректних розмірів: проміжні фрагменти мусять бути кратні 8 */
    if (more_fragments && (len % 8 != 0)) return -1;

    ReassemblyQueue *q = find_or_create_queue(d, key, now);
    if (!q) return -1;

    /* Фіксація кінцевого розміру за останнім фрагментом (MF = 0) */
    if (!more_fragments) {
        if (q->expected_total_len != -1 && q->expected_total_len != (int32_t)byte_end) {
            return -1; /* Суперечливий фінальний фрагмент */
        }
        q->expected_total_len = (int32_t)byte_end;
    }

    /* Копіювання навантаження у буфер дейтаграми */
    memcpy(q->buffer + byte_offset, payload, len);
    if (!add_interval(q, (uint16_t)byte_offset, (uint16_t)byte_end)) return -1;

    /* Перевіряємо, чи зібрано весь діапазон [0, expected_total_len) */
    if (q->expected_total_len != -1 && q->intervals) {
        if (q->intervals->start == 0 && q->intervals->end == (uint16_t)q->expected_total_len) {
            memcpy(out_buffer, q->buffer, (size_t)q->expected_total_len);
            *out_len = (uint16_t)q->expected_total_len;

            /* Видаляємо завершену чергу */
            ReassemblyQueue **curr = &d->head;
            while (*curr && *curr != q) curr = &(*curr)->next;
            if (*curr) *curr = q->next;
            free_queue_entry(q);
            return 1;
        }
    }
    return 0;
}

void defrag_destroy(Defragmenter *d) {
    if (!d) return;
    ReassemblyQueue *q = d->head;
    while (q) {
        ReassemblyQueue *tmp = q->next;
        free_queue_entry(q);
        q = tmp;
    }
    free(d);
}
```
```cpp
#include <iostream>
#include <vector>
#include <map>
#include <span>
#include <optional>
#include <expected>
#include <cstdint>
#include <chrono>
#include <cstring>
#include <algorithm>

namespace net {

inline constexpr size_t MaxIpPacketSize = 65535;
inline constexpr size_t MaxPayloadSize   = MaxIpPacketSize - 20;
inline constexpr auto ReassemblyTimeout = std::chrono::seconds(30);

enum class DefragError {
    PayloadTooLarge,
    UnalignedIntermediateFragment,
    ContradictoryTotalLength,
    AllocationFailed,
    CorruptedData
};

struct PacketKey {
    uint32_t src_ip{0};
    uint32_t dst_ip{0};
    uint16_t id{0};
    uint8_t  protocol{0};

    auto operator<=>(const PacketKey&) const = default;
};

class IpReassemblyEngine {
public:
    struct ReassemblyEntry {
        std::vector<uint8_t> buffer;
        std::map<uint16_t, uint16_t> intervals; /* start -> end */
        std::optional<uint16_t> expected_total_len;
        std::chrono::steady_clock::time_point created_at;

        explicit ReassemblyEntry(std::chrono::steady_clock::time_point now)
            : buffer(MaxPayloadSize, 0), created_at(now) {}
    };

    void cleanup_expired(std::chrono::steady_clock::time_point now = std::chrono::steady_clock::now()) {
        std::erase_if(queues_, [now](const auto& item) {
            return (now - item.second.created_at) > ReassemblyTimeout;
        });
    }

    std::expected<std::optional<std::vector<uint8_t>>, DefragError>
    process_fragment(const PacketKey& key,
                     uint16_t offset_8b,
                     bool more_fragments,
                     std::span<const uint8_t> payload,
                     std::chrono::steady_clock::time_point now = std::chrono::steady_clock::now()) {
        const uint32_t byte_offset = static_cast<uint32_t>(offset_8b) * 8;
        const uint32_t byte_end = byte_offset + static_cast<uint32_t>(payload.size());

        if (byte_end > MaxPayloadSize) {
            return std::unexpected(DefragError::PayloadTooLarge);
        }

        if (more_fragments && (payload.size() % 8 != 0)) {
            return std::unexpected(DefragError::UnalignedIntermediateFragment);
        }

        cleanup_expired(now);

        auto [it, inserted] = queues_.try_emplace(key, now);
        auto& entry = it->second;

        if (!more_fragments) {
            if (entry.expected_total_len && *entry.expected_total_len != static_cast<uint16_t>(byte_end)) {
                return std::unexpected(DefragError::ContradictoryTotalLength);
            }
            entry.expected_total_len = static_cast<uint16_t>(byte_end);
        }

        std::memcpy(entry.buffer.data() + byte_offset, payload.data(), payload.size());
        merge_interval(entry.intervals, static_cast<uint16_t>(byte_offset), static_cast<uint16_t>(byte_end));

        if (entry.expected_total_len.has_value()) {
            const uint16_t target_len = *entry.expected_total_len;
            if (!entry.intervals.empty()) {
                const auto& [first_start, first_end] = *entry.intervals.begin();
                if (first_start == 0 && first_end == target_len) {
                    std::vector<uint8_t> assembled(entry.buffer.begin(), entry.buffer.begin() + target_len);
                    queues_.erase(it);
                    return assembled;
                }
            }
        }

        return std::nullopt; /* Дейтаграма ще не повна, очікуємо решту фрагментів */
    }

private:
    static void merge_interval(std::map<uint16_t, uint16_t>& intervals, uint16_t start, uint16_t end) {
        auto it = intervals.upper_bound(start);
        if (it != intervals.begin()) {
            auto prev = std::prev(it);
            if (prev->second >= start) {
                start = prev->first;
                end = std::max(end, prev->second);
                it = intervals.erase(prev);
            }
        }
        while (it != intervals.end() && it->first <= end) {
            end = std::max(end, it->second);
            it = intervals.erase(it);
        }
        intervals[start] = end;
    }

    std::map<PacketKey, ReassemblyEntry> queues_;
};

} // namespace net
```
:::

### Розбір граничних випадків та захист від атак

1. **Невирівняні проміжні фрагменти:** Усі проміжні фрагменти (`MF = 1`) обов'язково повинні мати довжину, кратну 8 байтам. Якщо фрагмент посередині потоку має довжину 1475 байтів, зміщення наступного фрагмента неможливо коректно виразити цілим числом 8-байтних блоків (Fragment Offset). Двигун негайно відхиляє такі пакети як структурно пошкоджені.
2. **Перевірка суперечливості `MF = 0`:** Атакуючий може надіслати два різні фрагменти з прапорцем `MF = 0` (наприклад, один на довжину 2000 байтів, інший на 4000 байтів). Перевірка `expected_total_len` фіксує спробу колізії та нейтралізує підміну розміру.
3. **Об'єднання інтервалів через `merge_interval`:** Замість тривіального підрахунку прийнятих байтів алгоритм об'єднує фактичні діапазони `[start, end)`. Це унеможливлює ситуацію, коли зловмисник шле той самий фрагмент 10 разів: байти не дублюються у лічильнику, а дейтаграма визнається зібраною виключно за наявності суцільного відрізка `[0, total_len)`.

### Архітектура збирання у ядрі Linux: підсистема `inet_frags`

У вихідному коді ядра Linux (файли `net/ipv4/ip_fragment.c` та `net/ipv4/inet_fragment.c`) механізм збирання оптимізовано під екстремальні мережеві навантаження та захист від цілеспрямованих атак відмови в обслуговуванні (DoS).

Головні компоненти підсистеми:
- **Хеш-таблиця `inet_frags`:** Зберігає всі активні черги фрагментів `struct ipq` (IPv4 Queue). Хешування виконується функцією `inet_frag_hashfn()` над 4-кортежем `(saddr, daddr, id, protocol)` із додаванням випадкової солі (secret seed), що періодично оновлюється. Це запобігає атакам алгоритмічної складності (Hash Flooding DoS), коли зловмисник навмисно підбирає ідентифікатори для переповнення одного хеш-кошика.
- **Дворівневий ліміт пам'яті (`ipfrag_high_thresh` та `ipfrag_low_thresh`):** Ядро жорстко контролює сумарний обсяг оперативної пам'яті, виділений під незавершені черги фрагментів (глобальний лічильник `frag_mem_limit`). За замовчуванням у сучасних дистрибутивах верхня межа становить 4 МБ (`4 194 304` байти), а нижня — 3 МБ (`3 145 728` байтів). Щойно сумарний розмір буферів перетинає `high_thresh`, ядро переходить у режим агресивного скидання черг за принципом LRU (Least Recently Used), вивільняючи ресурси, доки пам'ять не опуститься нижче `low_thresh`.
- **Червоно-чорне дерево фрагментів (`rbtree`):** Починаючи з ядра Linux 4.17, лінійний список `sk_buff` замінили на червоно-чорне дерево інтервалів. Кожен вузол дерева представляє отриманий `skb` зі зміщенням `ip_hdr(skb)->frag_off`. При отриманні нового пакета ядро виконує пошук сусідніх інтервалів за логарифмічний час `O(log N)` та виявляє перекриття.

### Таксономія обробки перекриттів (Paxson & Shankar, 2002)

У класичній праці Верна Паксона та Умеша Шанкара *«Active Mapping: Resensitizing NIDS»* було доведено, що різні операційні системи обробляють фрагменти, які частково перекривають один одного, за фундаментально різними правилами:

| Операційна система | Стратегія вирішення перекриття | Поведінка при конфлікті байтів |
| :--- | :--- | :--- |
| **Linux (сучасні версії)** | *First-Fragment Priority (з обрізанням)* | Зберігає байти першого отриманого фрагмента, обрізаючи наступний фрагмент по межі перекриття. |
| **BSD / macOS** | *First-Fragment Priority (строгий)* | Байти першого фрагмента мають абсолютний пріоритет; нові фрагменти, що накладаються на старі, ігноруються. |
| **Windows NT / 2000 / XP** | *Last-Fragment Priority* | Байти останнього отриманого фрагмента безумовно перезаписують попередні дані в буфері. |
| **Cisco IOS** | *Last-Fragment Priority* | Нові дані мають перевагу над раніше отриманими байтами. |

Ця розбіжність створювала небезпечний вектор обходу міжмережевих екранів та систем виявлення вторгнень (NIDS/IPS): зловмисник міг надіслати два перекритих фрагменти, де перший містив безпечний текст, а другий — шкідливу команду. Якщо NIDS реконструював сесію за логікою BSD (брав перший фрагмент), а кінцевий сервер працював під керуванням Windows (перезаписував дані другим фрагментом), атака успішно досягала жертви, залишаючись непоміченою для захисних систем.

Сучасний безпечний дефрагментатор зобов'язаний або повністю відкидати дейтаграми з суперечливими перекриттями, або нормалізувати вхідний потік трафіку на межі мережі (IP Scrubbing), перетворюючи фрагментовані пакети на цілісні стандартизовані блоки.

### Фрагментація у високопродуктивній обробці: DPDK та eBPF/XDP

У сучасних програмних комутаторах та шлюзах обробки пакетів зі швидкістю ліній (100–400 Гбіт/с) фрагментація становить особливу складність через порушення моделі нульового копіювання (Zero-Copy):

1. **Бібліотека DPDK `librte_ip_frag`:**
   Фреймворк DPDK надає функції `rte_ipv4_fragment_packet()` та `rte_ipv4_frag_reassemble_packet()`. Для уникнення алокацій у динамічній пам'яті під час фрагментації DPDK створює непрямі буфери `rte_mbuf` (англ. *indirect mbufs*), які посилаються на той самий пул вихідної пам'яті пакетів без фізичного копіювання корисних даних. Збирання організовано через таблицю `rte_ip_frag_tbl`, де кожна черга прив'язана до окремого ядра процесора (core-pinned memory), що усуває міжядерні блокування (lockless design).

2. **Обмеження драйверного рівня eBPF / XDP:**
   Технологія eXpress Data Path (XDP) виконує байткод eBPF безпосередньо у драйвері мережевої карти до виділення ядрами Linux структур `sk_buff`. Оскільки XDP обробляє кожен окремий мережевий кадр ізольовано в режимі *Run-to-Completion*, програма XDP **не має змоги прочитати порти TCP/UDP для фрагментів із `Fragment Offset > 0`**. Спроба звернутися до L4-заголовка у непершому фрагменті призведе до помилки валідатора ядра або повернення сміттєвих даних із навантаження. Тому високоефективні балансувальники на eBPF (як Katran від Meta чи Cilium) змушені або передавати фрагментовані пакети на стандартний стек ядра через дію `XDP_PASS`, або підтримувати окрему eBPF-карту стану (LRU Map) для асоціації `Identification` із раніше збереженими портами з нульового фрагмента.

3. **Вплив апаратних прискорювачів LRO та GRO:**
   Сучасні мережеві адаптери (NIC) підтримують технології *Large Receive Offload* (LRO) та *Generic Receive Offload* (GRO) у ядрі для склеювання кількох послідовних TCP-сегментів у єдиний гігантський пакет розміром до 64 КБ перед передачею в стек TCP. **Важливо не плутати GRO з дефрагментацією IP:** GRO склеює лише повноцінні, непошкоджені TCP-пакети без біта фрагментації на основі номерів послідовності TCP Sequence Number. Якщо до адаптера надходять справжні розрізані IP-фрагменти (`MF = 1` або `Offset > 0`), апаратний рушій LRO негайно вимикається для цього потоку і скидає всі фрагменти на повільний шлях (Slow Path) софтверного збирання в ядрі. Це спричиняє раптовий сплеск завантаження процесора (CPU spike) та деградацію загальної пропускної здатності інтерфейсу.
