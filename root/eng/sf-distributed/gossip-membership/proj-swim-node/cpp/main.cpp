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
