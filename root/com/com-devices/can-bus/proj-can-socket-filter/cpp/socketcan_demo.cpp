// Файл: socketcan_demo.cpp
// Компіляція: g++ -std=c++20 -Wall -Wextra socketcan_demo.cpp -o socketcan_demo

#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <optional>
#include <system_error>
#include <cstring>
#include <cstdint>
#include <unistd.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <linux/can.h>
#include <linux/can/raw.h>
#include <linux/can/error.h>

namespace can {

enum class FrameType {
    Standard11Bit,
    Extended29Bit,
    RemoteRequest,
    ErrorFrame
};

struct Message {
    uint32_t id{0};
    FrameType type{FrameType::Standard11Bit};
    std::vector<uint8_t> data;
};

// RAII обгортка для управління файловим дескриптором сокета CAN
class Socket {
public:
    explicit Socket(std::string_view interface_name) {
        fd_ = ::socket(PF_CAN, SOCK_RAW, CAN_RAW);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити сокет CAN");
        }

        struct ifreq ifr{};
        std::strncpy(ifr.ifr_name, interface_name.data(), IFNAMSIZ - 1);
        if (::ioctl(fd_, SIOCGIFINDEX, &ifr) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "Не вдалося отримати індекс інтерфейсу");
        }

        struct sockaddr_can addr{};
        addr.can_family = AF_CAN;
        addr.can_ifindex = ifr.ifr_ifindex;

        if (::bind(fd_, reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "Не вдалося прив'язати сокет");
        }
    }

    ~Socket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    // Заборона копіювання (RAII ресурс)
    Socket(const Socket&) = delete;
    Socket& operator=(const Socket&) = delete;

    // Дозвіл переміщення
    Socket(Socket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    Socket& operator=(Socket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    void set_filters(std::span<const struct can_filter> filters) {
        if (::setsockopt(fd_, SOL_CAN_RAW, CAN_RAW_FILTER, filters.data(), filters.size_bytes()) < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося встановити маску фільтрації");
        }
    }

    void set_error_filter(can_err_mask_t err_mask) {
        if (::setsockopt(fd_, SOL_CAN_RAW, CAN_RAW_ERR_FILTER, &err_mask, sizeof(err_mask)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося встановити маску кадрів помилок");
        }
    }

    std::optional<Message> receive() {
        struct can_frame frame{};
        ssize_t nbytes = ::read(fd_, &frame, sizeof(struct can_frame));

        if (nbytes < static_cast<ssize_t>(sizeof(struct can_frame))) {
            return std::nullopt;
        }

        Message msg;
        const can_id_t raw_id = frame.can_id;

        if (raw_id & CAN_ERR_FLAG) {
            msg.type = FrameType::ErrorFrame;
            msg.id = raw_id & CAN_ERR_MASK;
        } else if (raw_id & CAN_RTR_FLAG) {
            msg.type = FrameType::RemoteRequest;
            msg.id = (raw_id & CAN_EFF_FLAG) ? (raw_id & CAN_EFF_MASK) : (raw_id & CAN_SFF_MASK);
        } else if (raw_id & CAN_EFF_FLAG) {
            msg.type = FrameType::Extended29Bit;
            msg.id = raw_id & CAN_EFF_MASK;
        } else {
            msg.type = FrameType::Standard11Bit;
            msg.id = raw_id & CAN_SFF_MASK;
        }

        if (msg.type != FrameType::RemoteRequest) {
            const uint8_t dlc = std::min<uint8_t>(frame.can_dlc, 8);
            msg.data.assign(frame.data, frame.data + dlc);
        }

        return msg;
    }

private:
    int fd_{-1};
};

} // namespace can

int main() {
    try {
        can::Socket can_sock("vcan0");

        // Налаштування фільтрів
        std::vector<struct can_filter> filters(2);
        filters[0] = {.can_id = 0x123, .can_mask = CAN_SFF_MASK};
        filters[1] = {.can_id = 0x200, .can_mask = 0x7F0};
        can_sock.set_filters(filters);
        can_sock.set_error_filter(CAN_ERR_CRIT | CAN_ERR_BUSOFF);

        std::cout << "C++ SocketCAN слухач активовано. Очікування повідомлень...\n";

        for (int i = 0; i < 5; ++i) {
            auto msg_opt = can_sock.receive();
            if (!msg_opt) continue;

            const auto& msg = *msg_opt;
            std::cout << "Отримано ID: 0x" << std::hex << msg.id << std::dec;

            switch (msg.type) {
                case can::FrameType::Standard11Bit: std::cout << " [11-bit Std]"; break;
                case can::FrameType::Extended29Bit: std::cout << " [29-bit Ext]"; break;
                case can::FrameType::RemoteRequest: std::cout << " [RTR Request]"; break;
                case can::FrameType::ErrorFrame:    std::cout << " [Error Frame]"; break;
            }

            std::cout << " | Байт: " << msg.data.size() << " | Дані: ";
            for (uint8_t b : msg.data) {
                std::cout << std::hex << (int)b << " ";
            }
            std::cout << std::dec << "\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
