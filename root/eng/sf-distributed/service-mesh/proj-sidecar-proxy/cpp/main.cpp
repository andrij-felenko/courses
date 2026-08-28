#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <chrono>
#include <optional>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

namespace mesh {

using Clock = std::chrono::steady_clock;
using TimePoint = std::chrono::time_point<Clock>;

struct UpstreamNode {
    std::string host;
    int port;
    int consecutive_5xx{0};
    TimePoint ejected_until{TimePoint::min()};

    [[nodiscard]] bool is_healthy(TimePoint now) const {
        return now >= ejected_until;
    }
};

class SocketGuard {
    int fd_{-1};
public:
    explicit SocketGuard(int fd) : fd_(fd) {}
    ~SocketGuard() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    SocketGuard(const SocketGuard&) = delete;
    SocketGuard& operator=(const SocketGuard&) = delete;
    SocketGuard(SocketGuard&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    SocketGuard& operator=(SocketGuard&& o) noexcept {
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

class OutlierDetector {
    std::vector<UpstreamNode> nodes_;
    size_t rr_index_{0};
    const int max_consecutive_5xx_{3};
    const std::chrono::seconds ejection_duration_{10};

public:
    void add_upstream(std::string host, int port) {
        nodes_.push_back(UpstreamNode{std::move(host), port, 0, TimePoint::min()});
    }

    [[nodiscard]] std::optional<size_t> select_healthy_node() {
        if (nodes_.empty()) return std::nullopt;
        const auto now = Clock::now();
        
        for (size_t checked = 0; checked < nodes_.size(); ++checked) {
            size_t idx = rr_index_ % nodes_.size();
            rr_index_ = (rr_index_ + 1) % nodes_.size();

            auto& node = nodes_[idx];
            if (node.is_healthy(now)) {
                if (node.ejected_until != TimePoint::min()) {
                    /* Відновлення після завершення тайм-ауту охолодження */
                    node.ejected_until = TimePoint::min();
                    node.consecutive_5xx = 0;
                    std::cout << "[CB] Відновлено вузол " << node.host << ":" << node.port << "\n";
                }
                return idx;
            }
        }
        return std::nullopt;
    }

    void record_status(size_t idx, int status_code) {
        if (idx >= nodes_.size()) return;
        auto& node = nodes_[idx];

        if (status_code >= 500 && status_code <= 599) {
            node.consecutive_5xx++;
            std::cout << "[OUTLIER] Вузол " << node.host << ":" << node.port
                      << " статус " << status_code << " (невдач: "
                      << node.consecutive_5xx << "/" << max_consecutive_5xx_ << ")\n";

            if (node.consecutive_5xx >= max_consecutive_5xx_) {
                node.ejected_until = Clock::now() + ejection_duration_;
                std::cout << "[CIRCUIT_BREAKER] Вузол " << node.host << ":" << node.port
                          << " ізольовано на " << ejection_duration_.count() << "s!\n";
            }
        } else if (status_code >= 200 && status_code < 500) {
            node.consecutive_5xx = 0;
        }
    }

    [[nodiscard]] const UpstreamNode& get_node(size_t idx) const {
        return nodes_.at(idx);
    }
};

class SidecarProxy {
    int port_;
    OutlierDetector detector_;

    static std::optional<SocketGuard> create_upstream_socket(const std::string& host, int port) {
        int fd = ::socket(AF_INET, SOCK_STREAM, 0);
        if (fd < 0) return std::nullopt;

        SocketGuard guard(fd);
        sockaddr_in serv_addr{};
        serv_addr.sin_family = AF_INET;
        serv_addr.sin_port = htons(port);

        if (::inet_pton(AF_INET, host.c_str(), &serv_addr.sin_addr) <= 0) {
            return std::nullopt;
        }

        timeval tv{ .tv_sec = 2, .tv_usec = 0 };
        ::setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
        ::setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));

        if (::connect(fd, reinterpret_cast<sockaddr*>(&serv_addr), sizeof(serv_addr)) < 0) {
            return std::nullopt;
        }
        return guard;
    }

    static int parse_status_code(std::string_view response) {
        if (response.size() < 12 || !response.starts_with("HTTP/1.")) return 0;
        auto pos = response.find(' ');
        if (pos == std::string_view::npos) return 0;
        while (pos < response.size() && response[pos] == ' ') ++pos;
        if (pos + 3 <= response.size()) {
            return std::stoi(std::string(response.substr(pos, 3)));
        }
        return 0;
    }

public:
    explicit SidecarProxy(int port) : port_(port) {}

    void add_backend(std::string host, int port) {
        detector_.add_upstream(std::move(host), port);
    }

    void handle_connection(SocketGuard client) {
        std::vector<char> buffer(16384);
        ssize_t bytes = ::read(client.get(), buffer.data(), buffer.size() - 1);
        if (bytes <= 0) return;

        std::string_view request(buffer.data(), static_cast<size_t>(bytes));
        auto upstream_idx = detector_.select_healthy_node();

        if (!upstream_idx) {
            std::string_view err_503 = 
                "HTTP/1.1 503 Service Unavailable\r\n"
                "Content-Length: 38\r\n\r\n"
                "Mesh: No healthy upstreams available\n";
            ::write(client.get(), err_503.data(), err_503.size());
            return;
        }

        const auto& node = detector_.get_node(*upstream_idx);
        auto upstream_sock = create_upstream_socket(node.host, node.port);

        if (!upstream_sock) {
            detector_.record_status(*upstream_idx, 503);
            std::string_view err_502 = 
                "HTTP/1.1 502 Bad Gateway\r\n"
                "Content-Length: 29\r\n\r\n"
                "Mesh: Connection to host failed\n";
            ::write(client.get(), err_502.data(), err_502.size());
            return;
        }

        /* Додавання службових заголовків трейсингу */
        std::string enriched_req;
        auto header_end = request.find("\r\n\r\n");
        if (header_end != std::string_view::npos) {
            enriched_req.append(request.substr(0, header_end));
            enriched_req.append("\r\nx-mesh-envoy: sidecar-cpp-v2\r\nx-request-id: req-cpp-trace\r\n\r\n");
            enriched_req.append(request.substr(header_end + 4));
        } else {
            enriched_req = std::string(request);
        }

        ::write(upstream_sock->get(), enriched_req.data(), enriched_req.size());

        ssize_t up_bytes = ::read(upstream_sock->get(), buffer.data(), buffer.size() - 1);
        if (up_bytes > 0) {
            std::string_view resp(buffer.data(), static_cast<size_t>(up_bytes));
            int status = parse_status_code(resp);
            detector_.record_status(*upstream_idx, status);
            ::write(client.get(), buffer.data(), static_cast<size_t>(up_bytes));
        } else {
            detector_.record_status(*upstream_idx, 504);
        }
    }

    void run() {
        int sfd = ::socket(AF_INET, SOCK_STREAM, 0);
        if (sfd < 0) throw std::runtime_error("socket creation failed");
        SocketGuard server_guard(sfd);

        int opt = 1;
        ::setsockopt(sfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(port_);

        if (::bind(sfd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            throw std::runtime_error("bind failed");
        }
        if (::listen(sfd, 64) < 0) {
            throw std::runtime_error("listen failed");
        }

        std::cout << "=== L7 Сайдкар-проксі (C++20) запущено на порті " << port_ << " ===\n";

        while (true) {
            sockaddr_in client_addr{};
            socklen_t len = sizeof(client_addr);
            int cfd = ::accept(sfd, reinterpret_cast<sockaddr*>(&client_addr), &len);
            if (cfd >= 0) {
                handle_connection(SocketGuard(cfd));
            }
        }
    }
};

} // namespace mesh

int main() {
    mesh::SidecarProxy proxy(15001);
    proxy.add_backend("127.0.0.1", 8081);
    proxy.add_backend("127.0.0.1", 8082);
    proxy.add_backend("127.0.0.1", 8083);
    proxy.run();
    return 0;
}
