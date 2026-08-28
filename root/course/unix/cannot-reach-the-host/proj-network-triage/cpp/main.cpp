#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <expected>
#include <chrono>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <netdb.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>

namespace net_probe {

using namespace std::chrono_literals;

enum class StageError {
    DnsResolution,
    RoutingOrTransport,
    BannerRead
};

struct DiagnosticReport {
    std::string resolved_ip;
    std::string ip_family;
    bool port_open{false};
    std::string banner;
};

struct DiagnosticFailure {
    StageError stage;
    int error_code{0};
    std::string message;
    std::string target_ip;
};

class SocketHandle {
public:
    explicit SocketHandle(int fd = -1) noexcept : m_fd(fd) {}
    ~SocketHandle() noexcept {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
    }

    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;

    SocketHandle(SocketHandle&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }

    SocketHandle& operator=(SocketHandle&& other) noexcept {
        if (this != &other) {
            if (m_fd >= 0) ::close(m_fd);
            m_fd = other.m_fd;
            other.m_fd = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }

    bool set_nonblocking() noexcept {
        const int flags = ::fcntl(m_fd, F_GETFL, 0);
        if (flags == -1) return false;
        return ::fcntl(m_fd, F_SETFL, flags | O_NONBLOCK) != -1;
    }

private:
    int m_fd{-1};
};

class NetworkProber {
public:
    static std::expected<DiagnosticReport, DiagnosticFailure> probe(
        std::string_view host,
        std::string_view port,
        std::chrono::milliseconds timeout = 3000ms) 
    {
        DiagnosticReport report;

        // Крок 1: Розв'язання імені в IP-адреси
        addrinfo hints{};
        hints.ai_family = AF_UNSPEC;
        hints.ai_socktype = SOCK_STREAM;
        hints.ai_protocol = IPPROTO_TCP;

        addrinfo* raw_list = nullptr;
        const int gai_rc = ::getaddrinfo(host.data(), port.data(), &hints, &raw_list);
        if (gai_rc != 0) {
            return std::unexpected(DiagnosticFailure{
                .stage = StageError::DnsResolution,
                .error_code = gai_rc,
                .message = ::gai_strerror(gai_rc)
            });
        }

        // Автоматичне звільнення списку addrinfo
        struct AddrInfoGuard {
            addrinfo* ptr;
            ~AddrInfoGuard() { if (ptr) ::freeaddrinfo(ptr); }
        } guard{raw_list};

        int last_connect_error = 0;
        std::string candidate_ip;

        for (auto* rp = raw_list; rp != nullptr; rp = rp->ai_next) {
            char ip_buffer[INET6_ADDRSTRLEN]{};
            const void* addr_src = (rp->ai_family == AF_INET)
                ? static_cast<const void*>(&reinterpret_cast<const sockaddr_in*>(rp->ai_addr)->sin_addr)
                : static_cast<const void*>(&reinterpret_cast<const sockaddr_in6*>(rp->ai_addr)->sin6_addr);

            ::inet_ntop(rp->ai_family, addr_src, ip_buffer, sizeof(ip_buffer));
            candidate_ip = ip_buffer;
            report.resolved_ip = candidate_ip;
            report.ip_family = (rp->ai_family == AF_INET) ? "IPv4" : "IPv6";

            SocketHandle sock(::socket(rp->ai_family, rp->ai_socktype, rp->ai_protocol));
            if (!sock.valid()) {
                last_connect_error = errno;
                continue;
            }

            if (!sock.set_nonblocking()) {
                last_connect_error = errno;
                continue;
            }

            // Крок 2 та 3: Неблокуюче підключення TCP
            const int rc = ::connect(sock.get(), rp->ai_addr, rp->ai_addrlen);
            if (rc == 0) {
                report.port_open = true;
                return inspect_application_layer(std::move(sock), std::move(report));
            }

            if (errno == EINPROGRESS) {
                pollfd pfd{};
                pfd.fd = sock.get();
                pfd.events = POLLOUT | POLLERR | POLLHUP;

                int poll_rc;
                do {
                    poll_rc = ::poll(&pfd, 1, static_cast<int>(timeout.count()));
                } while (poll_rc < 0 && errno == EINTR);

                if (poll_rc > 0) {
                    int sock_err = 0;
                    socklen_t opt_len = sizeof(sock_err);
                    if (::getsockopt(sock.get(), SOL_SOCKET, SO_ERROR, &sock_err, &opt_len) < 0) {
                        last_connect_error = errno;
                    } else if (sock_err != 0) {
                        last_connect_error = sock_err; // ECONNREFUSED / ETIMEDOUT / EHOSTUNREACH
                    } else {
                        report.port_open = true;
                        return inspect_application_layer(std::move(sock), std::move(report));
                    }
                } else if (poll_rc == 0) {
                    last_connect_error = ETIMEDOUT;
                } else {
                    last_connect_error = errno;
                }
            } else {
                last_connect_error = errno;
            }
        }

        return std::unexpected(DiagnosticFailure{
            .stage = StageError::RoutingOrTransport,
            .error_code = last_connect_error,
            .message = std::strerror(last_connect_error),
            .target_ip = candidate_ip
        });
    }

private:
    static std::expected<DiagnosticReport, DiagnosticFailure> inspect_application_layer(
        SocketHandle sock, DiagnosticReport report) 
    {
        pollfd pfd_read{};
        pfd_read.fd = sock.get();
        pfd_read.events = POLLIN;

        // Очікування банера до 2000 мс
        int poll_rc;
        do {
            poll_rc = ::poll(&pfd_read, 1, 2000);
        } while (poll_rc < 0 && errno == EINTR);

        if (poll_rc > 0 && (pfd_read.revents & POLLIN)) {
            char buffer[512]{};
            const ssize_t bytes = ::read(sock.get(), buffer, sizeof(buffer) - 1);
            if (bytes > 0) {
                std::string banner_str(buffer, static_cast<size_t>(bytes));
                const auto pos = banner_str.find_first_of("\r\n");
                if (pos != std::string::npos) {
                    banner_str.resize(pos);
                }
                report.banner = std::move(banner_str);
            }
        } else {
            report.banner = "(сервер мовчить, немає стартового банера)";
        }

        return report;
    }
};

} // namespace net_probe

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <host> <port>\n";
        return 1;
    }

    const std::string_view target_host = argv[1];
    const std::string_view target_port = argv[2];

    std::cout << "=== ДІАГНОСТИКА ЗВ'ЯЗКУ: " << target_host << ":" << target_port << " ===\n";

    auto result = net_probe::NetworkProber::probe(target_host, target_port);
    if (result.has_value()) {
        const auto& rep = result.value();
        std::cout << "[+] Рівень 1 (DNS):   Успіх -> IP-адреса " << rep.resolved_ip << " (" << rep.ip_family << ")\n";
        std::cout << "[+] Рівень 2-3 (TCP): З'єднання встановлено (порт " << target_port << " відкритий)\n";
        std::cout << "[+] Рівень 4 (L7):    Банер служби: \"" << rep.banner << "\"\n";
        std::cout << "\nРЕЗУЛЬТАТ: Вузол повністю доступний.\n";
        return 0;
    }

    const auto& fail = result.error();
    std::cout << "[-] Відмова на стадії ";
    switch (fail.stage) {
        case net_probe::StageError::DnsResolution:
            std::cout << "1 (Розпізнавання імені DNS/NSS):\n"
                      << "    Код помилки: " << fail.message << "\n"
                      << "    Рекомендація: Перевірте DNS-сервер та файл /etc/hosts.\n";
            break;
        case net_probe::StageError::RoutingOrTransport:
            std::cout << "2-3 (Маршрутизація / TCP Транспорт):\n"
                      << "    Цільова IP-адреса: " << fail.target_ip << "\n"
                      << "    Системна помилка errno " << fail.error_code << ": " << fail.message << "\n";
            if (fail.error_code == ECONNREFUSED) {
                std::cout << "    Аналіз: Отримано TCP RST. Процес не слухає порт або фаєрвол REJECT.\n";
            } else if (fail.error_code == ETIMEDOUT) {
                std::cout << "    Аналіз: Мовчазний DROP пакета SYN. Перевірте nftables або хмарні фаєрволи.\n";
            } else if (fail.error_code == ENETUNREACH || fail.error_code == EHOSTUNREACH) {
                std::cout << "    Аналіз: Немає маршруту в таблиці FIB або збій виявлення L2-сусідів (ARP).\n";
            }
            break;
        default:
            std::cout << "невідомій стадії.\n";
            break;
    }

    return 2;
}
