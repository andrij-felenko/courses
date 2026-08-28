#include <iostream>
#include <string_view>
#include <chrono>
#include <expected>
#include <system_error>
#include <array>
#include <cmath>
#include <cstring>
#include <netdb.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/time.h>

class SocketHandle {
    int fd_{-1};
public:
    explicit SocketHandle(int fd) noexcept : fd_(fd) {}
    ~SocketHandle() noexcept {
        if (fd_ >= 0) ::close(fd_);
    }
    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;
    SocketHandle(SocketHandle&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    SocketHandle& operator=(SocketHandle&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

struct NtpMeasurement {
    double offset_seconds{0.0};
    double delay_seconds{0.0};
    uint8_t stratum{0};
    uint8_t leap_indicator{0};
};

class SntpClient {
public:
    static constexpr uint16_t DefaultPort = 123;
    static constexpr uint32_t NtpEpochDelta = 2208988800ULL;
    static constexpr double NtpFracDivisor = 4294967296.0;

    static constexpr double StepThreshold = 0.128;   // 128 мс
    static constexpr double PanicThreshold = 1000.0; // 1000 с

#pragma pack(push, 1)
    struct Packet {
        uint8_t  li_vn_mode{0};
        uint8_t  stratum{0};
        int8_t   poll{0};
        int8_t   precision{0};
        uint32_t root_delay{0};
        uint32_t root_dispersion{0};
        uint32_t ref_id{0};
        uint32_t ref_sec{0};
        uint32_t ref_frac{0};
        uint32_t orig_sec{0};
        uint32_t orig_frac{0};
        uint32_t rx_sec{0};
        uint32_t rx_frac{0};
        uint32_t tx_sec{0};
        uint32_t tx_frac{0};
    };
#pragma pack(pop)

    static double to_unix_seconds(uint32_t be_sec, uint32_t be_frac) noexcept {
        const uint32_t s = ntohl(be_sec);
        const uint32_t f = ntohl(be_frac);
        if (s == 0 && f == 0) return 0.0;
        return static_cast<double>(s - NtpEpochDelta) + (static_cast<double>(f) / NtpFracDivisor);
    }

    static void to_ntp_timestamp(double unix_sec, uint32_t& out_sec, uint32_t& out_frac) noexcept {
        double int_part{0.0};
        const double frac_part = std::modf(unix_sec, &int_part);
        out_sec = htonl(static_cast<uint32_t>(int_part + NtpEpochDelta));
        out_frac = htonl(static_cast<uint32_t>(frac_part * NtpFracDivisor));
    }

    static double current_realtime_seconds() noexcept {
        struct timespec ts{};
        ::clock_gettime(CLOCK_REALTIME, &ts);
        return static_cast<double>(ts.tv_sec) + (static_cast<double>(ts.tv_nsec) / 1e9);
    }

    static std::expected<NtpMeasurement, std::string> query(std::string_view host, std::chrono::seconds timeout = std::chrono::seconds{3}) {
        struct addrinfo hints{};
        hints.ai_family = AF_INET;
        hints.ai_socktype = SOCK_DGRAM;

        struct addrinfo* res{nullptr};
        if (const int rc = ::getaddrinfo(host.data(), "123", &hints, &res); rc != 0) {
            return std::unexpected(std::string("getaddrinfo failed: ") + ::gai_strerror(rc));
        }

        SocketHandle sock(::socket(res->ai_family, res->ai_socktype, res->ai_protocol));
        if (!sock.valid()) {
            ::freeaddrinfo(res);
            return std::unexpected("Failed to create UDP socket");
        }

        struct timeval tv{};
        tv.tv_sec = timeout.count();
        tv.tv_usec = 0;
        ::setsockopt(sock.get(), SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

        Packet req{};
        req.li_vn_mode = (0 << 6) | (4 << 3) | 3; // LI=0, VN=4, Mode=3 (Client)

        const double t1 = current_realtime_seconds();
        to_ntp_timestamp(t1, req.tx_sec, req.tx_frac);

        if (::sendto(sock.get(), &req, sizeof(req), 0, res->ai_addr, res->ai_addrlen) < 0) {
            ::freeaddrinfo(res);
            return std::unexpected("sendto failed: " + std::string(std::strerror(errno)));
        }

        Packet resp{};
        struct sockaddr_storage src_addr{};
        socklen_t src_len = sizeof(src_addr);

        const ssize_t bytes = ::recvfrom(sock.get(), &resp, sizeof(resp), 0,
                                        reinterpret_cast<struct sockaddr*>(&src_addr), &src_len);
        const double t4 = current_realtime_seconds();

        ::freeaddrinfo(res);

        if (bytes < static_cast<ssize_t>(sizeof(Packet))) {
            return std::unexpected("Invalid packet size or timeout occurred");
        }

        const uint8_t li = (resp.li_vn_mode >> 6) & 0x03;
        const uint8_t mode = resp.li_vn_mode & 0x07;
        const uint8_t stratum = resp.stratum;

        if (mode != 4 && mode != 5) {
            return std::unexpected("Invalid server mode: " + std::to_string(mode));
        }

        if (stratum == 0) {
            char kod[5] = {0};
            std::memcpy(kod, &resp.ref_id, 4);
            return std::unexpected("Received Kiss-o'-Death code: [" + std::string(kod) + "]");
        }

        if (li == 3 || stratum >= 16) {
            return std::unexpected("Server is unsynchronized");
        }

        if (resp.orig_sec != req.tx_sec || resp.orig_frac != req.tx_frac) {
            return std::unexpected("Origin timestamp mismatch (possible replay attack)");
        }

        const double t2 = to_unix_seconds(resp.rx_sec, resp.rx_frac);
        const double t3 = to_unix_seconds(resp.tx_sec, resp.tx_frac);

        const double delay = (t4 - t1) - (t3 - t2);
        const double offset = ((t2 - t1) + (t3 - t4)) / 2.0;

        if (delay < 0.0) {
            return std::unexpected("Negative round-trip delay detected");
        }

        return NtpMeasurement{
            .offset_seconds = offset,
            .delay_seconds = delay,
            .stratum = stratum,
            .leap_indicator = li
        };
    }

    static std::expected<void, std::string> adjust_clock(double offset) noexcept {
        const double abs_offset = std::abs(offset);

        if (abs_offset >= PanicThreshold) {
            return std::unexpected("Offset exceeds panic threshold (1000s)");
        }

        if (abs_offset < StepThreshold) {
            struct timeval adj{};
            adj.tv_sec = static_cast<time_t>(offset);
            adj.tv_usec = static_cast<suseconds_t>((offset - static_cast<double>(adj.tv_sec)) * 1e6);

            if (::adjtime(&adj, nullptr) != 0) {
                return std::unexpected(std::string("adjtime failed: ") + std::strerror(errno));
            }
            std::cout << "Discipline: Applied clock slew: " << offset << " s (monotonic)\n";
        } else {
            struct timespec now{};
            ::clock_gettime(CLOCK_REALTIME, &now);
            const double target_sec = (static_cast<double>(now.tv_sec) + (static_cast<double>(now.tv_nsec) / 1e9)) + offset;

            struct timespec target{};
            target.tv_sec = static_cast<time_t>(target_sec);
            target.tv_nsec = static_cast<long>((target_sec - static_cast<double>(target.tv_sec)) * 1e9);

            if (::clock_settime(CLOCK_REALTIME, &target) != 0) {
                return std::unexpected(std::string("clock_settime failed: ") + std::strerror(errno));
            }
            std::cout << "Discipline: Applied clock step: " << offset << " s\n";
        }
        return {};
    }
};
