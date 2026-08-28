// sctp_server.cpp — Ідіоматичний еквівалент сервера на C++20 (RAII, string_view, std::expected)
#include <iostream>
#include <string_view>
#include <format>
#include <array>
#include <expected>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/sctp.h>
#include <arpa/inet.h>

namespace sctp {

constexpr uint16_t ServerPort = 9899;
constexpr size_t BufferSize = 2048;
constexpr uint16_t StreamControl = 0;
constexpr uint16_t StreamTelemetry = 1;
constexpr uint32_t PpidControl = 0x0100;
constexpr uint32_t PpidTelemetry = 0x0200;

class Socket {
public:
    explicit Socket(int fd = -1) noexcept : fd_(fd) {}
    ~Socket() {
        if (fd_ >= 0) ::close(fd_);
    }

    Socket(const Socket&) = delete;
    Socket& operator=(const Socket&) = delete;

    Socket(Socket&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    Socket& operator=(Socket&& other) noexcept {
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

void log_notification(const union sctp_notification* notif) {
    if (!notif) return;
    switch (notif->sn_header.sn_type) {
        case SCTP_ASSOC_CHANGE: {
            const auto& sac = notif->sn_assoc_change;
            if (sac.sac_state == SCTP_COMM_UP) {
                std::cout << std::format("[ПОДІЯ] Асоціацію встановлено (ID: {}, In: {}, Out: {})\n",
                                         sac.sac_assoc_id, sac.sac_inbound_streams, sac.sac_outbound_streams);
            } else if (sac.sac_state == SCTP_COMM_LOST) {
                std::cout << std::format("[ПОДІЯ] Асоціацію втрачено (ID: {})\n", sac.sac_assoc_id);
            }
            break;
        }
        case SCTP_PEER_ADDR_CHANGE: {
            const auto& spc = notif->sn_paddr_change;
            std::array<char, INET_ADDRSTRLEN> ip_buf{};
            const auto* sin = reinterpret_cast<const sockaddr_in*>(&spc->spc_aaddr);
            ::inet_ntop(AF_INET, &sin->sin_addr, ip_buf.data(), ip_buf.size());
            std::cout << std::format("[ПОДІЯ] Зміна стану адреси піра {}: стан = {}\n", ip_buf.data(), spc->spc_state);
            break;
        }
        case SCTP_SHUTDOWN_EVENT:
            std::cout << "[ПОДІЯ] Пір ініціював плавне закриття (Shutdown)\n";
            break;
        default:
            break;
    }
}

std::expected<Socket, std::error_code> create_server(uint16_t port) {
    int fd = ::socket(AF_INET, SOCK_STREAM, IPPROTO_SCTP);
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    Socket server_sock(fd);

    // 1. Конфігурація кількості потоків
    sctp_initmsg initmsg{};
    initmsg.sinit_num_ostreams = 5;
    initmsg.sinit_max_instreams = 5;
    initmsg.sinit_max_attempts = 4;
    if (::setsockopt(fd, IPPROTO_SCTP, SCTP_INITMSG, &initmsg, sizeof(initmsg)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    // 2. Підписка на події ядра
    sctp_event_subscribe events{};
    events.sctp_data_io_event = 1;
    events.sctp_association_event = 1;
    events.sctp_address_event = 1;
    events.sctp_shutdown_event = 1;
    if (::setsockopt(fd, IPPROTO_SCTP, SCTP_EVENTS, &events, sizeof(events)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    // 3. Прив'язка та прослуховування
    sockaddr_in servaddr{};
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port = htons(port);

    if (::bind(fd, reinterpret_cast<sockaddr*>(&servaddr), sizeof(servaddr)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    if (::listen(fd, 5) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return server_sock;
}

} // namespace sctp

int main() {
    auto server = sctp::create_server(sctp::ServerPort);
    if (!server) {
        std::cerr << "Помилка запуску сервера: " << server.error().message() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << std::format("SCTP Сервер запущено на порту {}. Очікування клієнтів...\n", sctp::ServerPort);

    sockaddr_in cliaddr{};
    socklen_t clilen = sizeof(cliaddr);
    int client_raw = ::accept(server->get(), reinterpret_cast<sockaddr*>(&cliaddr), &clilen);
    if (client_raw < 0) {
        std::cerr << "Помилка accept: " << std::generic_category().message(errno) << '\n';
        return EXIT_FAILURE;
    }
    sctp::Socket client_sock(client_raw);

    std::array<char, INET_ADDRSTRLEN> client_ip{};
    ::inet_ntop(AF_INET, &cliaddr.sin_addr, client_ip.data(), client_ip.size());
    std::cout << std::format("Клієнт підключився: {}:{}\n", client_ip.data(), ntohs(cliaddr.sin_port));

    std::array<char, sctp::BufferSize> buffer{};
    sctp_sndrcvinfo sinfo{};
    int flags = 0;

    while (true) {
        buffer.fill(0);
        std::memset(&sinfo, 0, sizeof(sinfo));
        flags = 0;

        ssize_t bytes = ::sctp_recvmsg(client_sock.get(), buffer.data(), buffer.size() - 1,
                                       nullptr, 0, &sinfo, &flags);
        if (bytes <= 0) {
            std::cout << "З'єднання закрито або виникла помилка.\n";
            break;
        }

        if (flags & MSG_NOTIFICATION) {
            sctp::log_notification(reinterpret_cast<const union sctp_notification*>(buffer.data()));
            continue;
        }

        std::string_view msg(buffer.data(), static_cast<size_t>(bytes));
        uint32_t ppid = ntohl(sinfo.sinfo_ppid);

        if (sinfo.sinfo_stream == sctp::StreamControl) {
            std::cout << std::format("[КОМАНДА] Потік: {}, SSN: {}, TSN: {}, PPID: 0x{:04X} | Вміст: {}\n",
                                     sinfo.sinfo_stream, sinfo.sinfo_ssn, sinfo.sinfo_tsn, ppid, msg);
            std::string ack = std::format("ACK-CMD:{}", msg);
            ::sctp_sendmsg(client_sock.get(), ack.data(), ack.size(), nullptr, 0,
                           htonl(sctp::PpidControl), 0, sctp::StreamControl, 0, 0);
        } else if (sinfo.sinfo_stream == sctp::StreamTelemetry) {
            std::cout << std::format("[ТЕЛЕМЕТРІЯ] Потік: {}, SSN: {} (Unordered), TSN: {} | Дані: {}\n",
                                     sinfo.sinfo_stream, sinfo.sinfo_ssn, sinfo.sinfo_tsn, msg);
        }
    }

    return EXIT_SUCCESS;
}
