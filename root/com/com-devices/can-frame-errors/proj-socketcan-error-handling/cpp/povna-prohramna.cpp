#include <iostream>
#include <string_view>
#include <expected>
#include <span>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <linux/can.h>
#include <linux/can/raw.h>
#include <linux/can/error.h>

class CanSocket {
    int fd_{-1};

public:
    explicit CanSocket(int fd) noexcept : fd_{fd} {}
    ~CanSocket() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    CanSocket(const CanSocket &) = delete;
    CanSocket &operator=(const CanSocket &) = delete;

    CanSocket(CanSocket &&other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }

    CanSocket &operator=(CanSocket &&other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }

    static std::expected<CanSocket, std::error_code> open(std::string_view ifname, can_err_mask_t err_mask) {
        int sock = ::socket(PF_CAN, SOCK_RAW, CAN_RAW);
        if (sock < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        struct ifreq ifr{};
        std::strncpy(ifr.ifr_name, ifname.data(), IFNAMSIZ - 1);
        if (::ioctl(sock, SIOCGIFINDEX, &ifr) < 0) {
            auto ec = std::error_code(errno, std::generic_category());
            ::close(sock);
            return std::unexpected(ec);
        }

        if (::setsockopt(sock, SOL_CAN_RAW, CAN_RAW_ERR_FILTER, &err_mask, sizeof(err_mask)) < 0) {
            auto ec = std::error_code(errno, std::generic_category());
            ::close(sock);
            return std::unexpected(ec);
        }

        struct sockaddr_can addr{};
        addr.can_family = AF_CAN;
        addr.can_ifindex = ifr.ifr_ifindex;

        if (::bind(sock, reinterpret_cast<struct sockaddr *>(&addr), sizeof(addr)) < 0) {
            auto ec = std::error_code(errno, std::generic_category());
            ::close(sock);
            return std::unexpected(ec);
        }

        return CanSocket{sock};
    }

    std::expected<struct can_frame, std::error_code> read_frame() const {
        struct can_frame frame{};
        ssize_t n = ::read(fd_, &frame, sizeof(frame));
        if (n < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return frame;
    }
};

void decode_error_frame(const struct can_frame &frame) {
    if (!(frame.can_id & CAN_ERR_FLAG)) return;

    const uint32_t err_class = frame.can_id & CAN_ERR_MASK;
    std::cout << "[CAN++ ERROR] Клас: 0x" << std::hex << err_class << std::dec;

    if (err_class & CAN_ERR_TX_TIMEOUT) std::cout << " | TX-Timeout";
    if (err_class & CAN_ERR_LOSTARB)    std::cout << " | Втрата арбітражу біт #" << static_cast<int>(frame.data[0]);
    if (err_class & CAN_ERR_ACK)        std::cout << " | ACK Error (відсутня відповідь)";
    if (err_class & CAN_ERR_BUSOFF)     std::cout << " | АВАРІЯ: BUS-OFF (ізоляція)";
    if (err_class & CAN_ERR_BUSERROR)   std::cout << " | Bus-Error (лінія)";
    if (err_class & CAN_ERR_RESTARTED)  std::cout << " | Авто-перезапуск";

    if (err_class & CAN_ERR_CRTL) {
        std::cout << " | Стан контролера:";
        const uint8_t ctrl = frame.data[1];
        if (ctrl & CAN_ERR_CRTL_RX_WARNING) std::cout << " RxWarn(REC>=96)";
        if (ctrl & CAN_ERR_CRTL_TX_WARNING) std::cout << " TxWarn(TEC>=96)";
        if (ctrl & CAN_ERR_CRTL_RX_PASSIVE) std::cout << " RxPassive(REC>=128)";
        if (ctrl & CAN_ERR_CRTL_TX_PASSIVE) std::cout << " TxPassive(TEC>=128)";
        if (ctrl & CAN_ERR_CRTL_ACTIVE)     std::cout << " Error-Active";
    }

    if (err_class & CAN_ERR_PROT) {
        std::cout << " | Порушення протоколу:";
        const uint8_t prot = frame.data[2];
        if (prot & CAN_ERR_PROT_BIT)   std::cout << " BitError";
        if (prot & CAN_ERR_PROT_FORM)  std::cout << " FormError";
        if (prot & CAN_ERR_PROT_STUFF) std::cout << " StuffError";
        std::cout << ((prot & CAN_ERR_PROT_TX) ? " (при передачі)" : " (при прийомі)");
    }

    if (frame.data[6] != 0 || frame.data[7] != 0) {
        std::cout << " | TEC=" << static_cast<int>(frame.data[6])
                  << ", REC=" << static_cast<int>(frame.data[7]);
    }
    std::cout << std::endl;
}

int main(int argc, char *argv[]) {
    const std::string_view ifname = (argc > 1) ? argv[1] : "can0";
    auto sock_res = CanSocket::open(ifname, CAN_ERR_MASK);
    if (!sock_res) {
        std::cerr << "Не вдалося відкрити CAN інтерфейс: " << sock_res.error().message() << std::endl;
        return 1;
    }

    const auto &can = *sock_res;
    std::cout << "C++ діагностику запущено на " << ifname << std::endl;

    while (true) {
        auto frame_res = can.read_frame();
        if (!frame_res) {
            std::cerr << "Помилка читання: " << frame_res.error().message() << std::endl;
            break;
        }
        if (frame_res->can_id & CAN_ERR_FLAG) {
            decode_error_frame(*frame_res);
        }
    }
    return 0;
}
