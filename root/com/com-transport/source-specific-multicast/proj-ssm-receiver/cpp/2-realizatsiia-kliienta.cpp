#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <array>
#include <stdexcept>
#include <system_error>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>

class SsmReceiver {
public:
    SsmReceiver(std::string_view mcast_group,
                std::string_view source_ip,
                std::string_view iface_ip,
                uint16_t port)
        : m_port(port) {
        m_fd = ::socket(AF_INET, SOCK_DGRAM, 0);
        if (m_fd < 0) {
            throw std::system_error(errno, std::generic_category(), "socket() failed");
        }

        int reuse = 1;
        if (::setsockopt(m_fd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)) < 0) {
            ::close(m_fd);
            throw std::system_error(errno, std::generic_category(), "SO_REUSEADDR failed");
        }

        sockaddr_in bind_addr{};
        bind_addr.sin_family = AF_INET;
        bind_addr.sin_port = htons(port);
        bind_addr.sin_addr.s_addr = htonl(INADDR_ANY);

        if (::bind(m_fd, reinterpret_cast<sockaddr*>(&bind_addr), sizeof(bind_addr)) < 0) {
            ::close(m_fd);
            throw std::system_error(errno, std::generic_category(), "bind() failed");
        }

        m_mreq = {};
        if (::inet_pton(AF_INET, mcast_group.data(), &m_mreq.imr_multiaddr) <= 0 ||
            ::inet_pton(AF_INET, source_ip.data(), &m_mreq.imr_sourceaddr) <= 0 ||
            ::inet_pton(AF_INET, iface_ip.data(), &m_mreq.imr_interface) <= 0) {
            ::close(m_fd);
            throw std::invalid_argument("Некоректний формат IP-адрес для SSM");
        }

        if (::setsockopt(m_fd, IPPROTO_IP, IP_ADD_SOURCE_MEMBERSHIP, &m_mreq, sizeof(m_mreq)) < 0) {
            ::close(m_fd);
            throw std::system_error(errno, std::generic_category(), "IP_ADD_SOURCE_MEMBERSHIP failed");
        }

        std::cout << "C++ SSM Receiver підписано на (" << source_ip << ", "
                  << mcast_group << ") порт " << port << '\n';
    }

    ~SsmReceiver() noexcept {
        if (m_fd >= 0) {
            ::setsockopt(m_fd, IPPROTO_IP, IP_DROP_SOURCE_MEMBERSHIP, &m_mreq, sizeof(m_mreq));
            ::close(m_fd);
        }
    }

    SsmReceiver(const SsmReceiver&) = delete;
    SsmReceiver& operator=(const SsmReceiver&) = delete;

    SsmReceiver(SsmReceiver&& other) noexcept
        : m_fd(other.m_fd), m_mreq(other.m_mreq), m_port(other.m_port) {
        other.m_fd = -1;
    }

    void run() {
        std::vector<char> buffer(4096);
        while (true) {
            sockaddr_in sender_addr{};
            socklen_t addr_len = sizeof(sender_addr);

            ssize_t bytes = ::recvfrom(m_fd, buffer.data(), buffer.size() - 1, 0,
                                       reinterpret_cast<sockaddr*>(&sender_addr), &addr_len);
            if (bytes < 0) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "recvfrom() failed");
            }

            buffer[bytes] = '\0';
            std::array<char, INET_ADDRSTRLEN> ip_buf{};
            ::inet_ntop(AF_INET, &sender_addr.sin_addr, ip_buf.data(), ip_buf.size());

            std::cout << "[Отримано " << bytes << " Б від " << ip_buf.data()
                      << ":" << ntohs(sender_addr.sin_port) << "] "
                      << std::string_view(buffer.data(), static_cast<size_t>(bytes)) << '\n';
        }
    }

private:
    int m_fd{-1};
    ip_mreq_source m_mreq{};
    uint16_t m_port{0};
};

int main() {
    try {
        SsmReceiver receiver("232.1.1.1", "198.51.100.1", "192.0.2.50", 5004);
        receiver.run();
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
