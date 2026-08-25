# ⚙️ Реалізація децентралізованого вузла SWIM та буфера пліток

У розподілених системах без централізованого координатора кожен сервер повинен самостійно відстежувати стан найближчого оточення, підтримувати актуальний перелік доступних учасників і поширювати метадані про збої без створення надлишкового навантаження на мережеву інфраструктуру.

Наведена нижче реалізація демонструє ядро протоколу SWIM: пряме зондування випадкових сусідів, маршрутизацію непрямих запитів через посередників, обробку стану підозри з монотонними інкарнаціями для спростування помилкових спрацьовувань та чергу розповсюдження пліток із лічильником залишкових ретрансляцій.

---

## Архітектурні компоненти реалізації

Програмна модель вузла складається з трьох ключових структур:
1. **Реєстр членства (Membership Table)** — таблиця всіх відомих учасників кластера з їхніми IP-адресами, портами, поточним статусом (`ALIVE`, `SUSPECT`, `DEAD`) та номером інкарнації.
2. **Черга розповсюдження пліток (Broadcast Queue)** — буфер подій зміни стану з лічильником залишкових відправлень `retransmits_left`. При формуванні будь-якої вихідної дейтаграми найсвіжіші події з цієї черги автоматично упаковуються в буфер пакету («наїздом» або *piggybacking*).
3. **Диспетчер зондувань та таймерів (Probe Scheduler)** — періодичний цикл, який обирає випадковий вузол із переліку, відправляє дейтаграму `PING`, відстежує таймаут `T_ack`, за потреби ініціює непрямі перевірки через `k` вузлів-посередників та переводить вузли зі стану `SUSPECT` у `DEAD` після вичерпання ліміту часу.

---

## Повний робочий код вузла SWIM

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/time.h>

#define SWIM_MAGIC 0x5357
#define MAX_MEMBERS 256
#define MAX_GOSSIP_ITEMS 16
#define PING_INTERVAL_MS 1000
#define ACK_TIMEOUT_MS 200
#define SUSPECT_TIMEOUT_MS 4000
#define RETRANSMIT_COUNT 3
#define INDIRECT_K 3

typedef enum {
    MSG_PING     = 0x01,
    MSG_ACK      = 0x02,
    MSG_PING_REQ = 0x03,
    MSG_SUSPECT  = 0x04,
    MSG_ALIVE    = 0x05,
    MSG_DEAD     = 0x06
} swim_msg_type_t;

typedef enum {
    STATE_ALIVE   = 0,
    STATE_SUSPECT = 1,
    STATE_DEAD    = 2
} swim_state_t;

#pragma pack(push, 1)
typedef struct {
    uint16_t magic;
    uint8_t  msg_type;
    uint8_t  flags;
    uint64_t seq_no;
    uint32_t target_ip;
    uint16_t target_port;
} probe_header_t;

typedef struct {
    uint8_t  state;
    uint32_t ip;
    uint16_t port;
    uint64_t incarnation;
} gossip_payload_t;

typedef struct {
    probe_header_t header;
    uint8_t        gossip_count;
    gossip_payload_t gossip[MAX_GOSSIP_ITEMS];
} swim_packet_t;
#pragma pack(pop)

typedef struct {
    uint32_t     ip;
    uint16_t     port;
    swim_state_t state;
    uint64_t     incarnation;
    uint64_t     state_change_time_ms;
} member_node_t;

typedef struct {
    gossip_payload_t payload;
    uint8_t          retransmits_left;
} broadcast_event_t;

typedef struct {
    int               sockfd;
    uint32_t          self_ip;
    uint16_t          self_port;
    uint64_t          self_incarnation;
    uint64_t          seq_counter;
    
    member_node_t     members[MAX_MEMBERS];
    size_t            member_count;
    
    broadcast_event_t bcast_queue[64];
    size_t            bcast_count;
    
    /* Стан активного прямого зонду */
    bool              probe_in_flight;
    uint64_t          probe_seq;
    size_t            probe_target_idx;
    uint64_t          probe_start_ms;
    bool              indirect_sent;
} swim_node_t;

static uint64_t current_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000 + (uint64_t)ts.tv_nsec / 1000000;
}

static void queue_broadcast(swim_node_t *node, uint8_t state, uint32_t ip, uint16_t port, uint64_t inc) {
    if (node->bcast_count < 64) {
        broadcast_event_t *ev = &node->bcast_queue[node->bcast_count++];
        ev->payload.state = state;
        ev->payload.ip = ip;
        ev->payload.port = port;
        ev->payload.incarnation = inc;
        ev->retransmits_left = RETRANSMIT_COUNT;
    }
}

static member_node_t* find_member(swim_node_t *node, uint32_t ip, uint16_t port) {
    for (size_t i = 0; i < node->member_count; ++i) {
        if (node->members[i].ip == ip && node->members[i].port == port) {
            return &node->members[i];
        }
    }
    return NULL;
}

static void apply_member_state(swim_node_t *node, uint8_t state, uint32_t ip, uint16_t port, uint64_t inc) {
    /* Перевірка на самого себе: чи оголосили нас підозрілими? */
    if (ip == node->self_ip && port == node->self_port) {
        if (state == STATE_SUSPECT && inc >= node->self_incarnation) {
            /* Спростування (Refutation) */
            node->self_incarnation = inc + 1;
            queue_broadcast(node, STATE_ALIVE, node->self_ip, node->self_port, node->self_incarnation);
            printf("[SWIM] Спростування підозри на себе! Нова інкарнація: %lu\n", (unsigned long)node->self_incarnation);
        }
        return;
    }

    member_node_t *m = find_member(node, ip, port);
    if (!m) {
        if (node->member_count < MAX_MEMBERS && state != STATE_DEAD) {
            m = &node->members[node->member_count++];
            m->ip = ip;
            m->port = port;
            m->state = (swim_state_t)state;
            m->incarnation = inc;
            m->state_change_time_ms = current_time_ms();
            printf("[SWIM] Новий вузол зареєстровано: %u:%u (стан=%d, inc=%lu)\n",
                   ip, ntohs(port), state, (unsigned long)inc);
            queue_broadcast(node, state, ip, port, inc);
        }
        return;
    }

    /* Матриця вирішення конфліктів */
    if (inc > m->incarnation) {
        m->incarnation = inc;
        m->state = (swim_state_t)state;
        m->state_change_time_ms = current_time_ms();
        queue_broadcast(node, state, ip, port, inc);
    } else if (inc == m->incarnation) {
        if (m->state == STATE_ALIVE && state == STATE_SUSPECT) {
            m->state = STATE_SUSPECT;
            m->state_change_time_ms = current_time_ms();
            queue_broadcast(node, state, ip, port, inc);
            printf("[SWIM] Вузол %u перейшов у SUSPECT (inc=%lu)\n", ip, (unsigned long)inc);
        } else if (m->state == STATE_SUSPECT && state == STATE_DEAD) {
            m->state = STATE_DEAD;
            m->state_change_time_ms = current_time_ms();
            queue_broadcast(node, state, ip, port, inc);
            printf("[SWIM] Вузол %u перейшов у DEAD (inc=%lu)\n", ip, (unsigned long)inc);
        }
    }
}

static void pack_and_send(swim_node_t *node, uint8_t msg_type, uint64_t seq,
                          uint32_t dest_ip, uint16_t dest_port,
                          uint32_t target_ip, uint16_t target_port) {
    swim_packet_t pkt;
    memset(&pkt, 0, sizeof(pkt));
    pkt.header.magic = htons(SWIM_MAGIC);
    pkt.header.msg_type = msg_type;
    pkt.header.seq_no = htobe64(seq);
    pkt.header.target_ip = target_ip;
    pkt.header.target_port = target_port;

    /* Пакуємо плітки з черги */
    uint8_t count = 0;
    for (size_t i = 0; i < node->bcast_count && count < MAX_GOSSIP_ITEMS; ++i) {
        if (node->bcast_queue[i].retransmits_left > 0) {
            pkt.gossip[count] = node->bcast_queue[i].payload;
            pkt.gossip[count].incarnation = htobe64(pkt.gossip[count].incarnation);
            node->bcast_queue[i].retransmits_left--;
            count++;
        }
    }
    pkt.gossip_count = count;

    struct sockaddr_in dst;
    memset(&dst, 0, sizeof(dst));
    dst.sin_family = AF_INET;
    dst.sin_addr.s_addr = dest_ip;
    dst.sin_port = dest_port;

    size_t send_len = sizeof(probe_header_t) + 1 + count * sizeof(gossip_payload_t);
    sendto(node->sockfd, &pkt, send_len, 0, (struct sockaddr*)&dst, sizeof(dst));
}

void swim_tick(swim_node_t *node) {
    uint64_t now = current_time_ms();

    /* 1. Перевірка активного прямого зондування */
    if (node->probe_in_flight) {
        if (now - node->probe_start_ms > ACK_TIMEOUT_MS && !node->indirect_sent) {
            /* Відправляємо непрямі запити PING_REQ через k випадкових вузлів */
            member_node_t *target = &node->members[node->probe_target_idx];
            size_t sent_k = 0;
            for (size_t i = 0; i < node->member_count && sent_k < INDIRECT_K; ++i) {
                if (i != node->probe_target_idx && node->members[i].state == STATE_ALIVE) {
                    pack_and_send(node, MSG_PING_REQ, node->probe_seq,
                                  node->members[i].ip, node->members[i].port,
                                  target->ip, target->port);
                    sent_k++;
                }
            }
            node->indirect_sent = true;
        } else if (now - node->probe_start_ms > PING_INTERVAL_MS) {
            /* Повний таймаут раунду: переводимо ціль у SUSPECT */
            member_node_t *target = &node->members[node->probe_target_idx];
            if (target->state == STATE_ALIVE) {
                apply_member_state(node, STATE_SUSPECT, target->ip, target->port, target->incarnation);
            }
            node->probe_in_flight = false;
        }
    } else if (node->member_count > 0) {
        /* Запуск нового раунду прямого зондування */
        node->probe_target_idx = (size_t)rand() % node->member_count;
        member_node_t *target = &node->members[node->probe_target_idx];
        if (target->state != STATE_DEAD) {
            node->probe_seq = ++node->seq_counter;
            node->probe_start_ms = now;
            node->probe_in_flight = true;
            node->indirect_sent = false;
            pack_and_send(node, MSG_PING, node->probe_seq, target->ip, target->port, 0, 0);
        }
    }

    /* 2. Перевірка таймаутів підозри (Suspect -> Dead) */
    for (size_t i = 0; i < node->member_count; ++i) {
        if (node->members[i].state == STATE_SUSPECT) {
            if (now - node->members[i].state_change_time_ms > SUSPECT_TIMEOUT_MS) {
                apply_member_state(node, STATE_DEAD, node->members[i].ip,
                                   node->members[i].port, node->members[i].incarnation);
            }
        }
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <unordered_map>
#include <chrono>
#include <random>
#include <memory>
#include <optional>
#include <expected>
#include <span>
#include <cstring>
#include <cstdint>
#include <unistd.h>
#include <fcntl.h>
#include <arpa/inet.h>
#include <sys/socket.h>

namespace swim {

constexpr uint16_t kMagic = 0x5357;
constexpr size_t kMaxGossipItems = 16;
constexpr auto kPingInterval = std::chrono::milliseconds(1000);
constexpr auto kAckTimeout = std::chrono::milliseconds(200);
constexpr auto kSuspectTimeout = std::chrono::milliseconds(4000);
constexpr uint8_t kRetransmitMultiplier = 3;
constexpr size_t kIndirectK = 3;

enum class MsgType : uint8_t {
    Ping    = 0x01,
    Ack     = 0x02,
    PingReq = 0x03,
    Suspect = 0x04,
    Alive   = 0x05,
    Dead    = 0x06
};

enum class NodeState : uint8_t {
    Alive   = 0,
    Suspect = 1,
    Dead    = 2
};

struct Endpoint {
    uint32_t ip{0};
    uint16_t port{0};

    bool operator==(const Endpoint &other) const = default;
};

struct EndpointHash {
    size_t operator()(const Endpoint &ep) const noexcept {
        return (static_cast<size_t>(ep.ip) << 16) ^ ep.port;
    }
};

struct GossipItem {
    NodeState state{NodeState::Alive};
    Endpoint  endpoint;
    uint64_t  incarnation{0};
};

struct MemberInfo {
    Endpoint  endpoint;
    NodeState state{NodeState::Alive};
    uint64_t  incarnation{0};
    std::chrono::steady_clock::time_point last_state_change;
};

struct BroadcastEvent {
    GossipItem item;
    uint8_t    retransmits_left{kRetransmitMultiplier};
};

class UniqueSocket {
public:
    explicit UniqueSocket(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueSocket() { if (fd_ >= 0) ::close(fd_); }

    UniqueSocket(const UniqueSocket &) = delete;
    UniqueSocket &operator=(const UniqueSocket &) = delete;

    UniqueSocket(UniqueSocket &&other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    UniqueSocket &operator=(UniqueSocket &&other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

private:
    int fd_{-1};
};

class SwimNode {
public:
    static std::expected<std::unique_ptr<SwimNode>, std::string> Create(uint32_t bind_ip, uint16_t bind_port) {
        int fd = ::socket(AF_INET, SOCK_DGRAM | SOCK_NONBLOCK, 0);
        if (fd < 0) {
            return std::unexpected("Не вдалося створити UDP сокет");
        }

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = bind_ip;
        addr.sin_port = bind_port;

        if (::bind(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            ::close(fd);
            return std::unexpected("Помилка прив'язки bind() до адреси");
        }

        return std::unique_ptr<SwimNode>(new SwimNode(UniqueSocket(fd), bind_ip, bind_port));
    }

    void Tick() {
        const auto now = std::chrono::steady_clock::now();

        // 1. Зондування
        if (probe_in_flight_) {
            if (now - probe_start_time_ > kAckTimeout && !indirect_sent_) {
                SendIndirectProbes();
            } else if (now - probe_start_time_ > kPingInterval) {
                HandleProbeTimeout();
            }
        } else if (!members_.empty()) {
            StartDirectProbe(now);
        }

        // 2. Перевірка таймерів підозри
        for (auto &[ep, member] : members_) {
            if (member.state == NodeState::Suspect) {
                if (now - member.last_state_change > kSuspectTimeout) {
                    ApplyState(GossipItem{NodeState::Dead, ep, member.incarnation});
                }
            }
        }
    }

    void ApplyState(const GossipItem &item) {
        if (item.endpoint == self_endpoint_) {
            if (item.state == NodeState::Suspect && item.incarnation >= self_incarnation_) {
                self_incarnation_ = item.incarnation + 1;
                QueueBroadcast(GossipItem{NodeState::Alive, self_endpoint_, self_incarnation_});
                std::cout << "[SWIM C++] Спростування власної підозри! Нова інкарнація: "
                          << self_incarnation_ << "\n";
            }
            return;
        }

        auto it = members_.find(item.endpoint);
        if (it == members_.end()) {
            if (item.state != NodeState::Dead) {
                members_[item.endpoint] = MemberInfo{
                    .endpoint = item.endpoint,
                    .state = item.state,
                    .incarnation = item.incarnation,
                    .last_state_change = std::chrono::steady_clock::now()
                };
                QueueBroadcast(item);
            }
            return;
        }

        MemberInfo &m = it->second;
        if (item.incarnation > m.incarnation) {
            m.incarnation = item.incarnation;
            m.state = item.state;
            m.last_state_change = std::chrono::steady_clock::now();
            QueueBroadcast(item);
        } else if (item.incarnation == m.incarnation) {
            if (m.state == NodeState::Alive && item.state == NodeState::Suspect) {
                m.state = NodeState::Suspect;
                m.last_state_change = std::chrono::steady_clock::now();
                QueueBroadcast(item);
            } else if (m.state == NodeState::Suspect && item.state == NodeState::Dead) {
                m.state = NodeState::Dead;
                m.last_state_change = std::chrono::steady_clock::now();
                QueueBroadcast(item);
            }
        }
    }

private:
    SwimNode(UniqueSocket sock, uint32_t ip, uint16_t port)
        : socket_(std::move(sock)), self_endpoint_{ip, port}, rng_(std::random_device{}()) {}

    void QueueBroadcast(const GossipItem &item) {
        broadcast_queue_.push_back(BroadcastEvent{.item = item});
    }

    void StartDirectProbe(std::chrono::steady_clock::time_point now) {
        std::vector<Endpoint> active_keys;
        for (const auto &[ep, info] : members_) {
            if (info.state != NodeState::Dead) active_keys.push_back(ep);
        }
        if (active_keys.empty()) return;

        std::uniform_int_distribution<size_t> dist(0, active_keys.size() - 1);
        active_target_ = active_keys[dist(rng_)];

        probe_seq_ = ++seq_counter_;
        probe_start_time_ = now;
        probe_in_flight_ = true;
        indirect_sent_ = false;

        SendPacket(MsgType::Ping, probe_seq_, *active_target_, {});
    }

    void SendIndirectProbes() {
        if (!active_target_) return;
        size_t sent = 0;
        for (const auto &[ep, info] : members_) {
            if (ep != *active_target_ && info.state == NodeState::Alive && sent < kIndirectK) {
                SendPacket(MsgType::PingReq, probe_seq_, ep, *active_target_);
                sent++;
            }
        }
        indirect_sent_ = true;
    }

    void HandleProbeTimeout() {
        if (active_target_) {
            auto it = members_.find(*active_target_);
            if (it != members_.end() && it->second.state == NodeState::Alive) {
                ApplyState(GossipItem{NodeState::Suspect, *active_target_, it->second.incarnation});
            }
        }
        probe_in_flight_ = false;
        active_target_.reset();
    }

    void SendPacket(MsgType type, uint64_t seq, Endpoint dest, std::optional<Endpoint> target) {
        std::vector<uint8_t> buffer(sizeof(probe_header_t) + 1 + kMaxGossipItems * sizeof(gossip_payload_t));
        auto *hdr = reinterpret_cast<probe_header_t*>(buffer.data());
        hdr->magic = htons(kMagic);
        hdr->msg_type = static_cast<uint8_t>(type);
        hdr->seq_no = htobe64(seq);
        hdr->target_ip = target ? target->ip : 0;
        hdr->target_port = target ? target->port : 0;

        uint8_t count = 0;
        auto *payload_ptr = reinterpret_cast<gossip_payload_t*>(buffer.data() + sizeof(probe_header_t) + 1);

        for (auto &ev : broadcast_queue_) {
            if (ev.retransmits_left > 0 && count < kMaxGossipItems) {
                payload_ptr[count].state = static_cast<uint8_t>(ev.item.state);
                payload_ptr[count].ip = ev.item.endpoint.ip;
                payload_ptr[count].port = ev.item.endpoint.port;
                payload_ptr[count].incarnation = htobe64(ev.item.incarnation);
                ev.retransmits_left--;
                count++;
            }
        }
        buffer[sizeof(probe_header_t)] = count;

        sockaddr_in dst{};
        dst.sin_family = AF_INET;
        dst.sin_addr.s_addr = dest.ip;
        dst.sin_port = dest.port;

        size_t total_size = sizeof(probe_header_t) + 1 + count * sizeof(gossip_payload_t);
        ::sendto(socket_.get(), buffer.data(), total_size, 0,
                 reinterpret_cast<sockaddr*>(&dst), sizeof(dst));
    }

    UniqueSocket socket_;
    Endpoint self_endpoint_;
    uint64_t self_incarnation_{0};
    uint64_t seq_counter_{0};

    std::unordered_map<Endpoint, MemberInfo, EndpointHash> members_;
    std::vector<BroadcastEvent> broadcast_queue_;

    bool probe_in_flight_{false};
    uint64_t probe_seq_{0};
    std::optional<Endpoint> active_target_;
    std::chrono::steady_clock::time_point probe_start_time_;
    bool indirect_sent_{false};
    std::mt19937 rng_;
};

} // namespace swim
```
:::

---

## Детальний розбір реалізації та ліквідація пасток

### 1. Неблокуючий ввід-вивід та ізоляція циклу опитування
Обидві версії використовують неблокуючий режим UDP-сокета (`SOCK_NONBLOCK`). Виклик `swim_tick()` (у мові C) або `SwimNode::Tick()` (у C++) виконується в головному циклі подій або за спрацьовуванням таймера. Це гарантує, що процес ні за яких обставин не зависне в системному виклику очікування відповіді від мертвого або відключеного вузла.

Усі часові інтервали вимірюються виключно через монотонні таймери (`CLOCK_MONOTONIC` у POSIX C або `std::chrono::steady_clock` у C++). Використання астрономічного системного часу (`gettimeofday` або `CLOCK_REALTIME`) суворо заборонено, оскільки синхронізація через NTP або переведення годинників уперед/назад здатні миттєво зламати перевірку таймаутів та викликати передчасне оголошення всього кластера мертвим.

### 2. Спростування помилкових підозр (Self-Refutation)
Коли сервер виявляє у вхідному буфері пліток запис про самого себе зі станом `SUSPECT`, функція `apply_member_state` (у C) або `ApplyState` (у C++) миттєво піднімає лічильник інкарнацій `self_incarnation = inc + 1` та додає оновлення `ALIVE` до черги відправлення.

Це розв'язує фундаментальну проблему хибного детектування під час короткочасних пауз збирача сміття GC чи сплесків навантаження на процесор: щойно вузол відновлює працездатність, він сповіщає всіх сусідів про свою живість з більшим номером інкарнації.

### 3. Автоматичне очищення буфера ретрансляцій (Piggybacking Lifecycle)
Кожна подія в черзі має лічильник `retransmits_left`, який ініціалізується значенням `RETRANSMIT_COUNT = 3`. Після трьох успішних відправок у складі вихідних пакетів подія припиняє передаватися.

Таке обмеження життєвого циклу повідомлень у черзі запобігає лавиноподібному накопиченню застарілих даних у пам'яті та гарантує, що обсяг корисного навантаження в UDP-пакетах завжди вкладається у встановлені ліміти MTU.

### 4. Обробка черги вхідних пакетів та маршрутизація PING_REQ
При отриманні дейтаграми на мережевому сокеті обробник виконує такі кроки:
* Перевіряє магічне число `magic == SWIM_MAGIC` та довжину пакета. Будь-які пошкоджені або сторонні дейтаграми негайно відкидаються.
* Якщо тип повідомлення `MSG_PING`, вузол негайно формує відповідь `MSG_ACK` з тим самим `seq_no` та пакує в неї актуальні плітки зі своєї черги.
* Якщо тип `MSG_PING_REQ`, вузол-посередник дістає адресу цілі `target_ip:target_port` із заголовка, відправляє короткий `MSG_PING` цільовому серверу, а після отримання відповіді пересилає `MSG_ACK` вузлу-ініціатору.
* Незалежно від типу вхідного зонда, вузол ітерується по масиву `gossip[MAX_GOSSIP_ITEMS]` і для кожного елемента викликає функцію оновлення стану `apply_member_state`.

### 5. Мережеві крайові випадки та налаштування сокета
У високонавантажених кластерах типовою проблемою є переповнення черги отримання сокета ядра Linux (`SO_RCVBUF`). Коли тисячі серверів надсилають пакети одночасно, ядро може відкинути вхідні `ACK`, що призведе до хибного запуску процедури підозри.

Щоб уникнути цього:
* Розмір буфера сокета збільшується за допомогою `setsockopt(sockfd, SOL_SOCKET, SO_RCVBUF, &buf_size, sizeof(buf_size))` до 4–8 МБ.
* Обробка вхідних повідомлень організовується в циклі `while (recvfrom(...) > 0)` до повного вичитування черги сокета на кожному кроці диспетчера.

### 6. Покрокове простеження життєвого циклу кластера
Розглянемо послідовність подій у мінімальному кластері з трьох вузлів `A`, `B` та `C`:
1. Вузол `A` стартує першим із початковою інкарнацією `inc = 0`. Вузол `B` запускається та викликає функцію приєднання до `A`. Вузол `A` додає запис `ALIVE(B, 0)` до своєї таблиці та вміщує подію до черги `bcast_queue`.
2. Вузол `C` стартує та підключається до `A`. Під час чергового раунду зондування `A` надсилає дейтаграму `PING` до `C`, прикріплюючи в буфері плітку `ALIVE(B, 0)`. Отримавши цей пакет, `C` автоматично дізнається про існування `B`, хоча прямих пакетів між `B` і `C` ще не надсилалося.
3. Якщо на сервері `B` виникає апаратна аварія або раптова зупинка процесу, вузол `A` під час чергового пінгу не отримує `ACK` протягом 200 мс. `A` надсилає запит `PING_REQ` вузлу `C`. Вузол `C` також не отримує відповіді від `B`. Через 1000 мс `A` переводить `B` у статус `SUSPECT(B, 0)` і пакує це оновлення в наступні дейтаграми.
4. Оскільки вузол `B` справді мертвий і не може згенерувати спростування `ALIVE(B, 1)`, через 4000 мс таймер підозри на `A` та `C` спливає. Обидва сервери переводять `B` у стан `DEAD` і вилучають його з пулу маршрутизації трафіку.

### 7. Відмінності та ідіоматичні переваги реалізації мовою C++
Порівняння двох варіантів коду чітко демонструє переваги сучасних стандартів C++ для розподілених систем:
* **Керування ресурсами через RAII**: Клас `UniqueSocket` гарантує автоматичне закриття файлового дескриптора сокета навіть у разі виникнення помилок ініціалізації чи виходу з області видимості, усуваючи ризик витоку дескрипторів.
* **Строга типізація та енуми**: Використання `enum class MsgType` та `NodeState` запобігає випадковому змішуванню типів повідомлень із числовими прапорцями або станами членства на етапі компіляції.
* **Типобезпечна обробка помилок**: Метод `Create` повертає `std::expected`, що вимагає від клієнтського коду явної перевірки результату створення сокета без використання магічних кодів помилок `NULL` чи глобальної змінної `errno`.
