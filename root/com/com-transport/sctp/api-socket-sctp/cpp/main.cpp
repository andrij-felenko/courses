// Ідіоматичний еквівалент налаштування SCTP-сервера на C++20 (RAII, expected, span)
#include <iostream>
#include <string_view>
#include <array>
#include <span>
#include <expected>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/sctp.h>
#include <arpa/inet.h>

class SctpServerSocket {
public:
    explicit SctpServerSocket(int fd) noexcept : fd_(fd) {}
    ~SctpServerSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    SctpServerSocket(const SctpServerSocket&) = delete;
    SctpServerSocket& operator=(const SctpServerSocket&) = delete;

    SctpServerSocket(SctpServerSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    SctpServerSocket& operator=(SctpServerSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }

    static std::expected<SctpServerSocket, std::error_code> create(
        std::string_view ip1, std::string_view ip2, uint16_t port) 
    {
        int sd = ::socket(AF_INET, SOCK_STREAM, IPPROTO_SCTP);
        if (sd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        SctpServerSocket server(sd);

        // 1. Конфігурація кількості потоків
        sctp_initmsg initmsg{};
        initmsg.sinit_num_ostreams = 10;
        initmsg.sinit_max_instreams = 10;
        initmsg.sinit_max_attempts = 4;
        initmsg.sinit_max_init_timeo = 5000;
        if (::setsockopt(sd, IPPROTO_SCTP, SCTP_INITMSG, &initmsg, sizeof(initmsg)) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        // 2. Підписка на події ядра
        sctp_event_subscribe events{};
        events.sctp_data_io_event = 1;
        events.sctp_association_event = 1;
        events.sctp_address_event = 1;
        events.sctp_shutdown_event = 1;
        if (::setsockopt(sd, IPPROTO_SCTP, SCTP_EVENTS, &events, sizeof(events)) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        // 3. Прив'язка двох IP-адрес для мультихоумінгу
        std::array<sockaddr_in, 2> addrs{};
        addrs[0].sin_family = AF_INET;
        addrs[0].sin_port = htons(port);
        if (::inet_pton(AF_INET, ip1.data(), &addrs[0].sin_addr) <= 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        addrs[1].sin_family = AF_INET;
        addrs[1].sin_port = htons(port);
        if (::inet_pton(AF_INET, ip2.data(), &addrs[1].sin_addr) <= 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::sctp_bindx(sd, reinterpret_cast<sockaddr*>(addrs.data()), 
                         static_cast<int>(addrs.size()), SCTP_BINDX_ADD_ADDR) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::listen(sd, 10) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return server;
    }

private:
    int fd_{-1};
};
