# ⚙️ Реалізація SWIM-протоколу: детектування збоїв та поширення членства

Реалізація стійкого до збоїв детектора членства вимагає суворого дотримання часових інтервалів, коректної серіалізації бінарних дейтаграм поверх UDP та детермінованого автомата станів підозри. У реальних розподілених мережах затримки комутації, короткочасні втрати окремих пакетів та сплески завантаження процесора через збирання сміття не повинні призводити до каскадного викидання працездатних серверів із робочого кластера.

---

## 1. Архітектура вузла SWIM та модель виконання

Вузол SWIM функціонує як децентралізований демон, що об'єднує три взаємопов'язані функціональні блоки:

```
                  ┌──────────────────────────────────────────────┐
                  │                 Вузол SWIM                   │
                  │                                              │
                  │  ┌──────────────┐          ┌──────────────┐  │
                  │  │ UDP Listener │          │  Probe Loop  │  │
                  │  └──────┬───────┘          └──────┬───────┘  │
                  │         │                         │          │
                  │         ▼                         ▼          │
                  │  ┌────────────────────────────────────────┐  │
                  │  │      Таблиця членства (NodeTable)      │  │
                  │  │  [ID | IP:Port | Incarnation | State]  │  │
                  │  └───────────────────┬────────────────────┘  │
                  │                      │                       │
                  │                      ▼                       │
                  │          ┌──────────────────────┐            │
                  │          │  Suspicion Manager   │            │
                  │          └──────────────────────┘            │
                  └──────────────────────────────────────────────┘
```

1. **Асинхронний приймач дейтаграм (UDP Listener):**
   Обробляє вхідний потік UDP-пакетів на виділеному порту (зазвичай порт 7946 для Serf/Memberlist). Виконує парсинг заголовків, перевіряє цілісність, зіставляє ідентифікатори послідовностей `seq` та оновлює локальну таблицю членства.
2. **Протокольний зондувальник (Probe Loop):**
   Ініціює періодичні перевірки живості з інтервалом `ProbeInterval` (типово 1000 мс). Обирає цільовий вузол із таблиці відомих пірів за алгоритмом Round-Robin із попереднім випадковим перемішуванням списку (Randomized Round-Robin).
3. **Диспетчер підозр та дедлайнів (Suspicion Manager):**
   Контролює таймери перебування вузлів у проміжному стані `SUSPECT`. Якщо підозра не спростовується цільовим вузлом протягом інтервалу `T_suspect`, статус переводиться в `DEAD`, а інформація про виключення вузла передається на рівень прикладного застосунку.

---

## 2. Покроковий життєвий цикл зондування

Процедура перевірки доступності виконується в чотири послідовні фази:

```
1. Фаза прямого опитування (Direct Ping):
   • Відправник A надсилає пакет PING вузлу B з унікальним seq = S.
   • Відправник запускає очікування відповіді на сокеті через select()/poll() з таймаутом 500 мс.
   • Якщо ACK(seq=S) отримано вчасно, стан вузла B підтверджується як ALIVE, раунд завершено.

2. Фаза непрямого опитування (Indirect Ping-Req):
   • Якщо прямий таймаут вичерпано, вузол A обирає k = 3 випадкових посередників (наприклад, вузли C, D, E).
   • Вузол A надсилає кожному з них пакет PING_REQ, що містить мережеву адресу та порт вузла B.
   • Посередник C після отримання PING_REQ надсилає PING на адресу B від власного імені.
   • Якщо B живий і відповідає посереднику C пакетом ACK, посередник негайно пересилає цей ACK вузлу A.

3. Фаза переходу в підозру (Suspicion Transition):
   • Якщо за час додаткового таймауту жоден із k посередників не зміг доставити ACK від B,
     вузол A фіксує перехід: B.state = SUSPECT.
   • Фіксується монотонна мітка часу старту підозри: B.suspect_started_at = steady_clock::now().
   • Вузол A формує плітку SUSPECT(target=B, inc=B.incarnation) для підсаджування в наступні дейтаграми.

4. Фаза самоспростування (Self-Refutation):
   • Вузол B, отримавши плітку про свою підозру від будь-якого іншого вузла, виявляє конфлікт:
     pkt.target_id == Self.id && pkt.incarnation >= Self.incarnation.
   • Вузол B збільшує свій лічильник: Self.incarnation = pkt.incarnation + 1.
   • Вузол B розсилає кластером спростування ALIVE(target=B, inc=Self.incarnation),
     яке безумовно скасовує статус підозри в усіх відомих таблицях членства.
```

---

## 3. Стратегія Randomized Round-Robin та підсаджування пліток

У наївній реалізації вузол на кожному кроці обирає випадкового сусіда через `rand() % N`. Проте за чисто випадкового вибору виникає класична математична проблема купонів: деякі вузли опитуватимуться тричі за хвилину, тоді як окремі сервери можуть залишатися неопитаними протягом десятків раундів, що створює затримку у виявленні збоїв.

Для розв'язання цієї проблеми протокол SWIM застосовує алгоритм **Randomized Round-Robin**:
1. Локальний список відомих пірів випадково перемішується (алгоритм тасування Фішера — Єйтса).
2. Зондувальник послідовно проходить по перемішаному списку індекс за індексом.
3. Коли список вичерпується (після `N` раундів), масив перемішується знову.
Це гарантує сувору верхню межу: **кожен вузол кластера буде опитаний щонайменше один раз за `N` інтервалів перевірки**.

Одночасно з цим вузол підтримує чергу повідомлень для підсаджування (Gossip Piggyback Queue). Коли генерується нова подія (`ALIVE`, `SUSPECT` або `DEAD`), вона поміщається в чергу з лічильником передач `retransmit_limit = k · log10(N + 1)`. Під час кожного відправлення `PING`, `ACK` або `PING_REQ` вільний простір дейтаграми заповнюється подіями з черги. Кожне відправлення зменшує лічильник події на одиницю; коли лічильник досягає нуля, подія витісняється з черги.

---

## 4. Робоча реалізація: ядро протоколу SWIM

Нижче наведено повну, компільовану реалізацію ядра протоколу SWIM мовами C та C++ з підтримкою прямого та непрямого зондування, розв'язання конфліктів поколінь та автоматичного спростування підозр.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/select.h>

#define MAX_NODES 64
#define INDIRECT_K 3
#define PROBE_TIMEOUT_MS 500
#define SUSPECT_TIMEOUT_MS 3000

typedef enum {
    MSG_PING = 1,
    MSG_ACK = 2,
    MSG_PING_REQ = 3,
    MSG_SUSPECT = 4,
    MSG_ALIVE = 5,
    MSG_DEAD = 6
} MessageType;

typedef enum {
    STATE_ALIVE = 0,
    STATE_SUSPECT = 1,
    STATE_DEAD = 2
} NodeState;

#pragma pack(push, 1)
typedef struct {
    uint8_t  type;
    uint16_t seq;
    uint32_t from_id;
    uint32_t incarnation;
    uint32_t target_id;       /* Використовується для PING_REQ */
    uint32_t target_ip;
    uint16_t target_port;
} SwimPacket;
#pragma pack(pop)

typedef struct {
    uint32_t id;
    struct sockaddr_in addr;
    uint32_t incarnation;
    NodeState state;
    time_t suspect_started_at;
} NodeInfo;

typedef struct {
    uint32_t self_id;
    uint32_t self_incarnation;
    int socket_fd;
    NodeInfo nodes[MAX_NODES];
    size_t node_count;
    uint16_t next_seq;
} SwimCluster;

void swim_init(SwimCluster *cluster, uint32_t id, uint16_t port) {
    cluster->self_id = id;
    cluster->self_incarnation = 0;
    cluster->node_count = 0;
    cluster->next_seq = 1;

    cluster->socket_fd = socket(AF_INET, SOCK_DGRAM, 0);
    struct sockaddr_in bind_addr = {
        .sin_family = AF_INET,
        .sin_addr.s_addr = INADDR_ANY,
        .sin_port = htons(port)
    };
    bind(cluster->socket_fd, (struct sockaddr *)&bind_addr, sizeof(bind_addr));
}

void swim_add_node(SwimCluster *cluster, uint32_t id, const char *ip, uint16_t port) {
    if (cluster->node_count >= MAX_NODES) return;
    NodeInfo *n = &cluster->nodes[cluster->node_count++];
    n->id = id;
    n->incarnation = 0;
    n->state = STATE_ALIVE;
    n->suspect_started_at = 0;
    n->addr.sin_family = AF_INET;
    n->addr.sin_port = htons(port);
    inet_pton(AF_INET, ip, &n->addr.sin_addr);
}

void swim_send_packet(SwimCluster *cluster, const SwimPacket *pkt, const struct sockaddr_in *dest) {
    sendto(cluster->socket_fd, pkt, sizeof(*pkt), 0,
           (const struct sockaddr *)dest, sizeof(*dest));
}

/* Обробка отриманого пакету */
void swim_handle_packet(SwimCluster *cluster, const SwimPacket *pkt, const struct sockaddr_in *from) {
    /* Якщо хтось оголосив нас підозрілим або мертвим, негайно спростовуємо */
    if (pkt->target_id == cluster->self_id &&
        (pkt->type == MSG_SUSPECT || pkt->type == MSG_DEAD)) {
        if (pkt->incarnation >= cluster->self_incarnation) {
            cluster->self_incarnation = pkt->incarnation + 1;
            SwimPacket alive_pkt = {
                .type = MSG_ALIVE,
                .seq = cluster->next_seq++,
                .from_id = cluster->self_id,
                .incarnation = cluster->self_incarnation,
                .target_id = cluster->self_id
            };
            swim_send_packet(cluster, &alive_pkt, from);
        }
        return;
    }

    switch (pkt->type) {
        case MSG_PING: {
            SwimPacket ack_pkt = {
                .type = MSG_ACK,
                .seq = pkt->seq,
                .from_id = cluster->self_id,
                .incarnation = cluster->self_incarnation,
                .target_id = pkt->from_id
            };
            swim_send_packet(cluster, &ack_pkt, from);
            break;
        }
        case MSG_PING_REQ: {
            /* Посередник пінгує цільовий вузол */
            struct sockaddr_in target_addr = {
                .sin_family = AF_INET,
                .sin_port = pkt->target_port,
                .sin_addr.s_addr = pkt->target_ip
            };
            SwimPacket fwd_ping = {
                .type = MSG_PING,
                .seq = pkt->seq,
                .from_id = cluster->self_id,
                .incarnation = cluster->self_incarnation,
                .target_id = pkt->target_id
            };
            swim_send_packet(cluster, &fwd_ping, &target_addr);
            break;
        }
        case MSG_ALIVE: {
            for (size_t i = 0; i < cluster->node_count; ++i) {
                if (cluster->nodes[i].id == pkt->target_id) {
                    if (pkt->incarnation > cluster->nodes[i].incarnation) {
                        cluster->nodes[i].incarnation = pkt->incarnation;
                        cluster->nodes[i].state = STATE_ALIVE;
                        cluster->nodes[i].suspect_started_at = 0;
                    }
                    break;
                }
            }
            break;
        }
        default:
            break;
    }
}

/* Виконання одного раунду зондування */
void swim_probe_round(SwimCluster *cluster) {
    if (cluster->node_count == 0) return;

    size_t target_idx = rand() % cluster->node_count;
    NodeInfo *target = &cluster->nodes[target_idx];
    if (target->state == STATE_DEAD) return;

    uint16_t seq = cluster->next_seq++;
    SwimPacket ping_pkt = {
        .type = MSG_PING,
        .seq = seq,
        .from_id = cluster->self_id,
        .incarnation = cluster->self_incarnation,
        .target_id = target->id
    };

    swim_send_packet(cluster, &ping_pkt, &target->addr);

    /* Очікування прямого підтвердження через select() */
    fd_set fds;
    FD_ZERO(&fds);
    FD_SET(cluster->socket_fd, &fds);
    struct timeval tv = { .tv_sec = 0, .tv_usec = PROBE_TIMEOUT_MS * 1000 };

    int res = select(cluster->socket_fd + 1, &fds, NULL, NULL, &tv);
    if (res > 0) {
        SwimPacket ack;
        struct sockaddr_in from;
        socklen_t from_len = sizeof(from);
        recvfrom(cluster->socket_fd, &ack, sizeof(ack), 0, (struct sockaddr *)&from, &from_len);
        if (ack.type == MSG_ACK && ack.seq == seq) {
            target->state = STATE_ALIVE;
            return;
        }
    }

    /* Прямий пінг не вдався -> Непряме зондування через k посередників */
    for (size_t i = 0; i < INDIRECT_K && i < cluster->node_count; ++i) {
        size_t helper_idx = rand() % cluster->node_count;
        if (helper_idx == target_idx) continue;

        SwimPacket ping_req = {
            .type = MSG_PING_REQ,
            .seq = seq,
            .from_id = cluster->self_id,
            .incarnation = cluster->self_incarnation,
            .target_id = target->id,
            .target_ip = target->addr.sin_addr.s_addr,
            .target_port = target->addr.sin_port
        };
        swim_send_packet(cluster, &ping_req, &cluster->nodes[helper_idx].addr);
    }

    /* Якщо відповіді немає, переводимо ціль у підозру */
    if (target->state == STATE_ALIVE) {
        target->state = STATE_SUSPECT;
        target->suspect_started_at = time(NULL);
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <unordered_map>
#include <random>
#include <chrono>
#include <memory>
#include <span>
#include <optional>
#include <cstring>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <unistd.h>

namespace swim {

enum class MessageType : uint8_t {
    Ping = 1,
    Ack = 2,
    PingReq = 3,
    Suspect = 4,
    Alive = 5,
    Dead = 6
};

enum class NodeState : uint8_t {
    Alive = 0,
    Suspect = 1,
    Dead = 2
};

struct [[gnu::packed]] Packet {
    MessageType type;
    uint16_t    seq;
    uint32_t    from_id;
    uint32_t    incarnation;
    uint32_t    target_id;
    uint32_t    target_ip;
    uint16_t    target_port;
};

struct NodeInfo {
    uint32_t id;
    sockaddr_in addr;
    uint32_t incarnation{0};
    NodeState state{NodeState::Alive};
    std::chrono::steady_clock::time_point suspect_started_at{};
};

class SocketHandle {
    int fd_{-1};
public:
    explicit SocketHandle(uint16_t port) {
        fd_ = ::socket(AF_INET, SOCK_DGRAM, 0);
        if (fd_ < 0) throw std::runtime_error("Не вдалося створити UDP-сокет");

        sockaddr_in bind_addr{};
        bind_addr.sin_family = AF_INET;
        bind_addr.sin_addr.s_addr = INADDR_ANY;
        bind_addr.sin_port = htons(port);
        if (::bind(fd_, reinterpret_cast<sockaddr*>(&bind_addr), sizeof(bind_addr)) < 0) {
            ::close(fd_);
            throw std::runtime_error("Помилка прив'язки порту сокета");
        }
    }

    ~SocketHandle() {
        if (fd_ >= 0) ::close(fd_);
    }

    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;
    SocketHandle(SocketHandle&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }

    [[nodiscard]] int get() const noexcept { return fd_; }
};

class ClusterNode {
    uint32_t self_id_;
    uint32_t self_incarnation_{0};
    uint16_t next_seq_{1};
    SocketHandle socket_;
    std::vector<NodeInfo> membership_list_;
    std::mt19937 rng_{std::random_device{}()};

    static constexpr auto ProbeTimeout = std::chrono::milliseconds(500);
    static constexpr auto SuspectTimeout = std::chrono::milliseconds(3000);
    static constexpr size_t IndirectCount = 3;

public:
    ClusterNode(uint32_t id, uint16_t port)
        : self_id_(id), socket_(port) {}

    void add_peer(uint32_t id, std::string_view ip, uint16_t port) {
        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port);
        ::inet_pton(AF_INET, ip.data(), &addr.sin_addr);
        membership_list_.push_back(NodeInfo{
            .id = id,
            .addr = addr,
            .incarnation = 0,
            .state = NodeState::Alive
        });
    }

    void send_packet(const Packet& pkt, const sockaddr_in& dest) {
        ::sendto(socket_.get(), &pkt, sizeof(pkt), 0,
                 reinterpret_cast<const sockaddr*>(&dest), sizeof(dest));
    }

    void handle_incoming_packet(const Packet& pkt, const sockaddr_in& from) {
        if (pkt.target_id == self_id_ &&
            (pkt.type == MessageType::Suspect || pkt.type == MessageType::Dead)) {
            if (pkt.incarnation >= self_incarnation_) {
                self_incarnation_ = pkt.incarnation + 1;
                Packet alive_pkt{
                    .type = MessageType::Alive,
                    .seq = next_seq_++,
                    .from_id = self_id_,
                    .incarnation = self_incarnation_,
                    .target_id = self_id_
                };
                send_packet(alive_pkt, from);
            }
            return;
        }

        switch (pkt.type) {
            case MessageType::Ping: {
                Packet ack{
                    .type = MessageType::Ack,
                    .seq = pkt.seq,
                    .from_id = self_id_,
                    .incarnation = self_incarnation_,
                    .target_id = pkt.from_id
                };
                send_packet(ack, from);
                break;
            }
            case MessageType::PingReq: {
                sockaddr_in target_addr{};
                target_addr.sin_family = AF_INET;
                target_addr.sin_port = pkt.target_port;
                target_addr.sin_addr.s_addr = pkt.target_ip;
                Packet fwd{
                    .type = MessageType::Ping,
                    .seq = pkt.seq,
                    .from_id = self_id_,
                    .incarnation = self_incarnation_,
                    .target_id = pkt.target_id
                };
                send_packet(fwd, target_addr);
                break;
            }
            case MessageType::Alive: {
                for (auto& node : membership_list_) {
                    if (node.id == pkt.target_id && pkt.incarnation > node.incarnation) {
                        node.incarnation = pkt.incarnation;
                        node.state = NodeState::Alive;
                        break;
                    }
                }
                break;
            }
            default:
                break;
        }
    }

    void run_probe_cycle() {
        if (membership_list_.empty()) return;

        std::uniform_int_distribution<size_t> dist(0, membership_list_.size() - 1);
        auto& target = membership_list_[dist(rng_)];
        if (target.state == NodeState::Dead) return;

        uint16_t seq = next_seq_++;
        Packet ping{
            .type = MessageType::Ping,
            .seq = seq,
            .from_id = self_id_,
            .incarnation = self_incarnation_,
            .target_id = target.id
        };
        send_packet(ping, target.addr);

        fd_set fds;
        FD_ZERO(&fds);
        FD_SET(socket_.get(), &fds);
        timeval tv{
            .tv_sec = 0,
            .tv_usec = static_cast<suseconds_t>(ProbeTimeout.count() * 1000)
        };

        if (::select(socket_.get() + 1, &fds, nullptr, nullptr, &tv) > 0) {
            Packet ack{};
            sockaddr_in from{};
            socklen_t len = sizeof(from);
            ::recvfrom(socket_.get(), &ack, sizeof(ack), 0,
                       reinterpret_cast<sockaddr*>(&from), &len);
            if (ack.type == MessageType::Ack && ack.seq == seq) {
                target.state = NodeState::Alive;
                return;
            }
        }

        /* Непряме зондування через K посередників */
        for (size_t i = 0; i < IndirectCount && i < membership_list_.size(); ++i) {
            size_t helper_idx = dist(rng_);
            if (membership_list_[helper_idx].id == target.id) continue;

            Packet ping_req{
                .type = MessageType::PingReq,
                .seq = seq,
                .from_id = self_id_,
                .incarnation = self_incarnation_,
                .target_id = target.id,
                .target_ip = target.addr.sin_addr.s_addr,
                .target_port = target.addr.sin_port
            };
            send_packet(ping_req, membership_list_[helper_idx].addr);
        }

        if (target.state == NodeState::Alive) {
            target.state = NodeState::Suspect;
            target.suspect_started_at = std::chrono::steady_clock::now();
        }
    }

    void sweep_suspects() {
        const auto now = std::chrono::steady_clock::now();
        for (auto& node : membership_list_) {
            if (node.state == NodeState::Suspect &&
                (now - node.suspect_started_at) > SuspectTimeout) {
                node.state = NodeState::Dead;
                std::cout << "[SWIM] Вузол " << node.id << " визнано DEAD\n";
            }
        }
    }
};

} // namespace swim
```
:::

---

## 5. Виробничі підводні камені та налаштування мережевого стека

Під час експлуатації вузлів SWIM у високопродуктивних виробничих середовищах інженери повинні враховувати такі системні фактори:

1. **Монотонний час проти системного годинника:**
   Використання `gettimeofday()` або `time(NULL)` у розподілених таймерах категорично неприпустиме через корекції часу демонами NTP або переходи на літній час. Раптовий стрибок системного часу назад на 1 секунду призведе до зависання таймерів підозри, а стрибок уперед — до миттєвого оголошення половини кластера мертвими. Слід використовувати виключно `clock_gettime(CLOCK_MONOTONIC)` у мові C або `std::chrono::steady_clock` у C++.
2. **Переповнення черги UDP-сокетів ядра (Socket Buffer Dropping):**
   Коли розмір кластера досягає кількох тисяч серверів, на вузол можуть одночасно приходити десятки дейтаграм `PING_REQ`. Якщо системний буфер прийому сокета малий (дефолтні 212 КБ у Linux), ядро операційної системи мовчки відкидатиме вхідні пакети без надсилання ICMP-помилок. Це викликає каскадний ефект, коли здоровий вузол не встигає відповісти на зонди й помилково визнається несправним.
   *Рішення:* Під час ініціалізації сокета обов'язково збільшуйте розмір системного буфера прийому до 2–4 МБ:

:::tabs
```c
int rcvbuf = 4 * 1024 * 1024;
setsockopt(cluster->socket_fd, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf));
```
```cpp
int rcvbuf = 4 * 1024 * 1024;
::setsockopt(socket_.get(), SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf));
```
:::
3. **Вирівнювання структур та порядок байтів (Endianness):**
   Двійкові структури пакетів повинні мати директиву упаковки `#pragma pack(push, 1)` або атрибут `[[gnu::packed]]`, щоб компілятор не додавав невидимі байти вирівнювання (padding). Усі багатобайтові цілі поля (`seq`, `incarnation`, `port`) повинні серіалізуватися функціями `htons()` / `htonl()` перед відправленням у мережу та розпаковуватися через `ntohs()` / `ntohl()` при отриманні.
4. **Контрольований вихід із кластера (Graceful Leave):**
   Якщо вузол зупиняється штатно (наприклад, під час оновлення версії сервісу), неприпустимо просто закривати процес. Вузол повинен надіслати повідомлення `DEAD` або `LEAVE` із максимальною інкарнацією до кількох випадкових сусідів. Це дозволяє кластеру миттєво зняти трафік із сервера без очікування 3–15 секунд таймауту підозри.
5. **Динамічні IP-адреси та перезапуск контейнерів:**
   У середовищах Kubernetes або Nomad контейнери часто перезапускаються на нових IP-адресах із збереженням логічного ідентифікатора сервісу. Якщо таблиця членства індексується за IP-адресою, перезапуск створить у кластері дублікат вузла. Тому таблиця пірів повинна однозначно індексуватися постійним UUID вузла (`node_id`), а пара IP-адреси та порту має динамічно оновлюватися в мапі при отриманні пакета `ALIVE` зі старшим номером інкарнації.
