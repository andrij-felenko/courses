#include <iostream>
#include <string>
#include <string_view>
#include <system_error>
#include <array>
#include <cstdint>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

class TcpSocket {
public:
    TcpSocket() {
        fd_ = ::socket(AF_INET, SOCK_STREAM, 0);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to create TCP socket");
        }
    }

    ~TcpSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    TcpSocket(const TcpSocket&) = delete;
    TcpSocket& operator=(const TcpSocket&) = delete;

    TcpSocket(TcpSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    TcpSocket& operator=(TcpSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    void set_congestion_algorithm(std::string_view name) {
        if (::setsockopt(fd_, IPPROTO_TCP, TCP_CONGESTION, name.data(), name.size() + 1) != 0) {
            throw std::system_error(errno, std::generic_category(), "setsockopt(TCP_CONGESTION) failed");
        }
    }

    [[nodiscard]] std::string get_congestion_algorithm() const {
        std::array<char, 32> buf{};
        socklen_t len = buf.size();
        if (::getsockopt(fd_, IPPROTO_TCP, TCP_CONGESTION, buf.data(), &len) != 0) {
            throw std::system_error(errno, std::generic_category(), "getsockopt(TCP_CONGESTION) failed");
        }
        return std::string(buf.data());
    }

    [[nodiscard]] ::tcp_info get_info() const {
        ::tcp_info info{};
        socklen_t len = sizeof(info);
        if (::getsockopt(fd_, IPPROTO_TCP, TCP_INFO, &info, &len) != 0) {
            throw std::system_error(errno, std::generic_category(), "getsockopt(TCP_INFO) failed");
        }
        return info;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }

private:
    int fd_{-1};
};

int main() {
    try {
        TcpSocket sock;
        sock.set_congestion_algorithm("cubic");

        std::cout << "Заданий алгоритм: " << sock.get_congestion_algorithm() << "\n";

        auto info = sock.get_info();
        std::cout << "Поточний cwnd: " << info.tcpi_snd_cwnd << " MSS\n";
        std::cout << "Поточний RTT:  " << (info.tcpi_rtt / 1000.0) << " ms\n";
        std::cout << "Min RTT:       " << (info.tcpi_min_rtt / 1000.0) << " ms\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
