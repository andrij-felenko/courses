#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <memory>
#include <thread>
#include <atomic>
#include <chrono>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <span>

// Безпечна RAII-обгортка для системного файлового дескриптора сокета
class SocketHandle {
    int fd_{-1};
public:
    explicit SocketHandle(int fd = -1) noexcept : fd_(fd) {}
    ~SocketHandle() noexcept { if (fd_ >= 0) ::close(fd_); }
    
    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;
    
    SocketHandle(SocketHandle&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    SocketHandle& operator=(SocketHandle&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
    
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

// Формат бінарного повідомлення шини
struct BusMessage {
    std::string topic;
    std::string payload;
};

// Вузол безброкерної шини повідомлень
class PeerBusNode {
public:
    PeerBusNode(std::string node_id, uint16_t data_port, uint16_t discovery_port)
        : node_id_(std::move(node_id)), data_port_(data_port), discovery_port_(discovery_port) {}

    ~PeerBusNode() {
        stop();
    }

    bool start() {
        running_ = true;
        
        // 1. Створення сокета для прийому прямих повідомлень (TCP)
        data_sock_ = SocketHandle(::socket(AF_INET, SOCK_STREAM, 0));
        if (!data_sock_.valid()) return false;

        int opt = 1;
        ::setsockopt(data_sock_.get(), SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

        sockaddr_in data_addr{};
        data_addr.sin_family = AF_INET;
        data_addr.sin_addr.s_addr = INADDR_ANY;
        data_addr.sin_port = htons(data_port_);

        if (::bind(data_sock_.get(), reinterpret_cast<sockaddr*>(&data_addr), sizeof(data_addr)) < 0) {
            return false;
        }
        ::listen(data_sock_.get(), 16);

        // 2. Створення сокета для UDP-виявлення (Discovery Beacon)
        disc_sock_ = SocketHandle(::socket(AF_INET, SOCK_DGRAM, 0));
        if (!disc_sock_.valid()) return false;
        ::setsockopt(disc_sock_.get(), SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
        ::setsockopt(disc_sock_.get(), SOL_SOCKET, SO_BROADCAST, &opt, sizeof(opt));

        sockaddr_in disc_addr{};
        disc_addr.sin_family = AF_INET;
        disc_addr.sin_addr.s_addr = INADDR_ANY;
        disc_addr.sin_port = htons(discovery_port_);

        if (::bind(disc_sock_.get(), reinterpret_cast<sockaddr*>(&disc_addr), sizeof(disc_addr)) < 0) {
            return false;
        }

        // Запуск фонових потоків обслуговування шини
        discovery_thread_ = std::jthread([this](std::stop_token st) { discovery_loop(st); });
        beacon_thread_ = std::jthread([this](std::stop_token st) { beacon_loop(st); });
        accept_thread_ = std::jthread([this](std::stop_token st) { accept_loop(st); });

        return true;
    }

    void stop() {
        running_ = false;
        if (discovery_thread_.joinable()) discovery_thread_.request_stop();
        if (beacon_thread_.joinable()) beacon_thread_.request_stop();
        if (accept_thread_.joinable()) accept_thread_.request_stop();
    }

    // Підписка на префікс теми (наприклад, "telemetry.")
    void subscribe(std::string topic_prefix) {
        subscriptions_.push_back(std::move(topic_prefix));
    }

    // Публікація повідомлення прямо всім знайденим пірам
    void publish(std::string_view topic, std::string_view payload) {
        std::string packet = std::string(topic) + "|" + std::string(payload) + "\n";
        
        for (const auto& [peer_id, endpoint] : known_peers_) {
            SocketHandle client(::socket(AF_INET, SOCK_STREAM, 0));
            if (!client.valid()) continue;

            sockaddr_in peer_addr{};
            peer_addr.sin_family = AF_INET;
            peer_addr.sin_addr.s_addr = inet_addr(endpoint.ip.c_str());
            peer_addr.sin_port = htons(endpoint.port);

            // Таймаут на з'єднання для запобігання блокуванню
            timeval tv{.tv_sec = 0, .tv_usec = 100000}; // 100 ms
            ::setsockopt(client.get(), SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));

            if (::connect(client.get(), reinterpret_cast<sockaddr*>(&peer_addr), sizeof(peer_addr)) == 0) {
                ::send(client.get(), packet.data(), packet.size(), 0);
            }
        }
    }

private:
    struct PeerEndpoint {
        std::string ip;
        uint16_t port;
        std::chrono::steady_clock::time_point last_seen;
    };

    std::string node_id_;
    uint16_t data_port_;
    uint16_t discovery_port_;
    std::atomic<bool> running_{false};

    SocketHandle data_sock_;
    SocketHandle disc_sock_;

    std::vector<std::string> subscriptions_;
    std::unordered_map<std::string, PeerEndpoint> known_peers_;

    std::jthread discovery_thread_;
    std::jthread beacon_thread_;
    std::jthread accept_thread_;

    // Періодичне розсилання маячка про себе
    void beacon_loop(std::stop_token st) {
        sockaddr_in bcast{};
        bcast.sin_family = AF_INET;
        bcast.sin_addr.s_addr = inet_addr("255.255.255.255");
        bcast.sin_port = htons(discovery_port_);

        std::string msg = "PEER:" + node_id_ + ":" + std::to_string(data_port_);

        while (!st.stop_requested() && running_) {
            ::sendto(disc_sock_.get(), msg.data(), msg.size(), 0,
                     reinterpret_cast<sockaddr*>(&bcast), sizeof(bcast));
            std::this_thread::sleep_for(std::chrono::milliseconds(1000));
        }
    }

    // Прийом маячків від сусідів
    void discovery_loop(std::stop_token st) {
        char buf[256];
        sockaddr_in sender{};
        socklen_t slen = sizeof(sender);

        while (!st.stop_requested() && running_) {
            ssize_t n = ::recvfrom(disc_sock_.get(), buf, sizeof(buf) - 1, 0,
                                   reinterpret_cast<sockaddr*>(&sender), &slen);
            if (n > 0) {
                buf[n] = '\0';
                std::string raw(buf);
                if (raw.rfind("PEER:", 0) == 0) {
                    size_t p1 = raw.find(':', 5);
                    if (p1 != std::string::npos) {
                        std::string p_id = raw.substr(5, p1 - 5);
                        uint16_t p_port = static_cast<uint16_t>(std::stoi(raw.substr(p1 + 1)));
                        
                        if (p_id != node_id_) {
                            char ip_str[INET_ADDRSTRLEN];
                            inet_ntop(AF_INET, &sender.sin_addr, ip_str, sizeof(ip_str));
                            known_peers_[p_id] = PeerEndpoint{ip_str, p_port, std::chrono::steady_clock::now()};
                        }
                    }
                }
            }
        }
    }

    // Прийом вхідних повідомлень від інших пірів
    void accept_loop(std::stop_token st) {
        while (!st.stop_requested() && running_) {
            sockaddr_in client_addr{};
            socklen_t clen = sizeof(client_addr);
            int client_fd = ::accept(data_sock_.get(), reinterpret_cast<sockaddr*>(&client_addr), &clen);
            if (client_fd >= 0) {
                char buf[1024];
                ssize_t n = ::recv(client_fd, buf, sizeof(buf) - 1, 0);
                if (n > 0) {
                    buf[n] = '\0';
                    std::string raw(buf);
                    size_t sep = raw.find('|');
                    if (sep != std::string::npos) {
                        std::string topic = raw.substr(0, sep);
                        std::string payload = raw.substr(sep + 1);
                        if (!payload.empty() && payload.back() == '\n') payload.pop_back();

                        // Локальна фільтрація за підписками
                        for (const auto& sub : subscriptions_) {
                            if (topic.rfind(sub, 0) == 0) {
                                std::cout << "[" << node_id_ << " RX] Тема: " << topic 
                                          << " | Дані: " << payload << std::endl;
                                break;
                            }
                        }
                    }
                }
                ::close(client_fd);
            }
        }
    }
};
