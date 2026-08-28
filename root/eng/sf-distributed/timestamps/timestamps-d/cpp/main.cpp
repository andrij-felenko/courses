#include <iostream>
#include <string_view>
#include <vector>
#include <array>
#include <span>
#include <expected>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <linux/net_tstamp.h>
#include <linux/sockios.h>
#include <linux/errqueue.h>
#include <poll.h>

class SafeSocket {
    int fd_{-1};
public:
    explicit SafeSocket(int fd) noexcept : fd_(fd) {}
    ~SafeSocket() {
        if (fd_ >= 0) ::close(fd_);
    }
    SafeSocket(const SafeSocket&) = delete;
    SafeSocket& operator=(const SafeSocket&) = delete;
    SafeSocket(SafeSocket&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    SafeSocket& operator=(SafeSocket&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

struct HardwareTimestampResult {
    timespec kernel_sw_ts{};
    timespec hardware_raw_ts{};
};

class HardwareTimestampSocket {
    SafeSocket sock_;

public:
    static std::expected<HardwareTimestampSocket, std::error_code> create(std::string_view ifname) {
        int fd = ::socket(AF_INET, SOCK_DGRAM, 0);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        SafeSocket safe_sock(fd);

        // Спроба налаштувати фільтр карти
        struct ifreq ifr{};
        std::strncpy(ifr.ifr_name, ifname.data(), sizeof(ifr.ifr_name) - 1);
        struct hwtstamp_config hw_cfg{};
        hw_cfg.tx_type = HWTSTAMP_TX_ON;
        hw_cfg.rx_filter = HWTSTAMP_FILTER_ALL;
        ifr.ifr_data = reinterpret_cast<char*>(&hw_cfg);

        if (::ioctl(safe_sock.get(), SIOCSHWTSTAMP, &ifr) < 0) {
            std::cerr << "Попередження: SIOCSHWTSTAMP не підтримується для " << ifname << "\n";
        }

        int flags = SOF_TIMESTAMPING_TX_HARDWARE |
                    SOF_TIMESTAMPING_TX_SOFTWARE |
                    SOF_TIMESTAMPING_RX_HARDWARE |
                    SOF_TIMESTAMPING_RAW_HARDWARE |
                    SOF_TIMESTAMPING_OPT_ID |
                    SOF_TIMESTAMPING_OPT_TSONLY;

        if (::setsockopt(safe_sock.get(), SOL_SOCKET, SO_TIMESTAMPING, &flags, sizeof(flags)) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return HardwareTimestampSocket(std::move(safe_sock));
    }

    explicit HardwareTimestampSocket(SafeSocket sock) : sock_(std::move(sock)) {}

    std::expected<void, std::error_code> send(std::span<const std::byte> payload, const sockaddr_in& dest) {
        ssize_t res = ::sendto(sock_.get(), payload.data(), payload.size(), 0,
                               reinterpret_cast<const sockaddr*>(&dest), sizeof(dest));
        if (res < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }

    std::expected<HardwareTimestampResult, std::error_code> wait_tx_timestamp(int timeout_ms = 1000) {
        pollfd pfd{.fd = sock_.get(), .events = POLLERR, .revents = 0};
        int p_res = ::poll(&pfd, 1, timeout_ms);
        if (p_res <= 0) {
            return std::unexpected(std::make_error_code(std::errc::timed_out));
        }

        std::array<char, 512> ctrl_buf{};
        msghdr msg{};
        msg.msg_control = ctrl_buf.data();
        msg.msg_controllen = ctrl_buf.size();

        if (::recvmsg(sock_.get(), &msg, MSG_ERRQUEUE | MSG_DONTWAIT) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        HardwareTimestampResult result{};
        for (auto* cmsg = CMSG_FIRSTHDR(&msg); cmsg != nullptr; cmsg = CMSG_NXTHDR(&msg, cmsg)) {
            if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_TIMESTAMPING) {
                auto* ts = reinterpret_cast<struct scm_timestamping*>(CMSG_DATA(cmsg));
                result.kernel_sw_ts = ts->ts[0];
                result.hardware_raw_ts = ts->ts[2];
            }
        }
        return result;
    }
};

int main(int argc, char* argv[]) {
    std::string_view ifname = (argc > 1) ? argv[1] : "eth0";

    auto sock_res = HardwareTimestampSocket::create(ifname);
    if (!sock_res) {
        std::cerr << "Помилка відкриття сокета: " << sock_res.error().message() << "\n";
        return 1;
    }

    sockaddr_in dest{};
    dest.sin_family = AF_INET;
    dest.sin_port = htons(319);
    ::inet_pton(AF_INET, "127.0.0.1", &dest.sin_addr);

    std::string_view msg_text = "IEEE1588_SYNC_CPP_PACKET";
    auto data_span = std::as_bytes(std::span(msg_text.data(), msg_text.size()));

    if (auto send_res = sock_res->send(data_span, dest); !send_res) {
        std::cerr << "Помилка надсилання: " << send_res.error().message() << "\n";
        return 1;
    }
    std::cout << "Пакет надіслано. Очікування мітки з дескриптора...\n";

    auto ts_res = sock_res->wait_tx_timestamp();
    if (!ts_res) {
        std::cerr << "Не вдалося отримати мітку: " << ts_res.error().message() << "\n";
        return 1;
    }

    std::cout << "Отримано мітку:\n"
              << "  Програмний час ядра: " << ts_res->kernel_sw_ts.tv_sec << "."
              << ts_res->kernel_sw_ts.tv_nsec << " с\n"
              << "  Апаратний час PHC:   " << ts_res->hardware_raw_ts.tv_sec << "."
              << ts_res->hardware_raw_ts.tv_nsec << " с\n";
    return 0;
}
