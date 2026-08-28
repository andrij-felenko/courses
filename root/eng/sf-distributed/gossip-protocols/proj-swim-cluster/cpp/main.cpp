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
