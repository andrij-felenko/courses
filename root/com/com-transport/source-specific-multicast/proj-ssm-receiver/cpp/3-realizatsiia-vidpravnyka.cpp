#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <thread>
#include <system_error>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>

class SsmSender {
public:
    SsmSender(std::string_view mcast_group, std::string_view iface_ip, uint16_t port, uint8_t ttl = 16) {
        m_fd = ::socket(AF_INET, SOCK_DGRAM, 0);
        if (m_fd < 0) {
            throw std::system_error(errno, std::generic_category(), "socket() failed");
        }

        in_addr iface{};
        if (::inet_pton(AF_INET, iface_ip.data(), &iface) <= 0) {
            ::close(m_fd);
            throw std::invalid_argument("Некоректний IP інтерфейсу");
        }

        if (::setsockopt(m_fd, IPPROTO_IP, IP_MULTICAST_IF, &iface, sizeof(iface)) < 0) {
            ::close(m_fd);
            throw std::system_error(errno, std::generic_category(), "IP_MULTICAST_IF failed");
        }

        if (::setsockopt(m_fd, IPPROTO_IP, IP_MULTICAST_TTL, &ttl, sizeof(ttl)) < 0) {
            ::close(m_fd);
            throw std::system_error(errno, std::generic_category(), "IP_MULTICAST_TTL failed");
        }

        m_target = {};
        m_target.sin_family = AF_INET;
        m_target.sin_port = htons(port);
        if (::inet_pton(AF_INET, mcast_group.data(), &m_target.sin_addr) <= 0) {
            ::close(m_fd);
            throw std::invalid_argument("Некоректна групова адреса SSM");
        }
    }

    ~SsmSender() noexcept {
        if (m_fd >= 0) ::close(m_fd);
    }

    SsmSender(const SsmSender&) = delete;
    SsmSender& operator=(const SsmSender&) = delete;

    void send_loop(std::chrono::milliseconds interval) {
        uint64_t seq = 0;
        while (true) {
            std::string msg = "SSM_DATA_SEQ=" + std::to_string(++seq);
            ssize_t sent = ::sendto(m_fd, msg.data(), msg.size(), 0,
                                    reinterpret_cast<const sockaddr*>(&m_target), sizeof(m_target));
            if (sent < 0) {
                throw std::system_error(errno, std::generic_category(), "sendto() failed");
            }

            std::cout << "C++ SSM Sender відправив пакет #" << seq << " (" << sent << " байтів)\n";
            std::this_thread::sleep_for(interval);
        }
    }

private:
    int m_fd{-1};
    sockaddr_in m_target{};
};

int main() {
    try {
        SsmSender sender("232.1.1.1", "198.51.100.1", 5004, 16);
        sender.send_loop(std::chrono::milliseconds(1000));
    } catch (const std::exception& ex) {
        std::cerr << "Помилка відправника: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
