#include <iostream>
#include <vector>
#include <string_view>
#include <chrono>
#include <span>
#include <memory>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/udp.h>
#include <arpa/inet.h>

constexpr uint16_t kSegmentSize = 1472;
constexpr size_t kNumSegments = 44;
constexpr size_t kTotalPayload = kSegmentSize * kNumSegments; // 64768 bytes
constexpr size_t kIterations = 20000;

class UdpBenchmark {
    int fd_{-1};
    sockaddr_in dst_addr_{};
public:
    UdpBenchmark(std::string_view ip, uint16_t port) {
        fd_ = ::socket(AF_INET, SOCK_DGRAM, 0);
        if (fd_ < 0) throw std::system_error(errno, std::generic_category(), "socket error");

        dst_addr_.sin_family = AF_INET;
        dst_addr_.sin_port = htons(port);
        ::inet_pton(AF_INET, ip.data(), &dst_addr_.sin_addr);
    }

    ~UdpBenchmark() {
        if (fd_ >= 0) ::close(fd_);
    }

    void run_gso_test(std::span<const std::byte> payload) {
        ::iovec iov{};
        iov.iov_base = const_cast<void*>(static_cast<const void*>(payload.data()));
        iov.iov_len = payload.size();

        alignas(struct cmsghdr) char cbuf[CMSG_SPACE(sizeof(uint16_t))]{};

        ::msghdr msg{};
        msg.msg_name = &dst_addr_;
        msg.msg_namelen = sizeof(dst_addr_);
        msg.msg_iov = &iov;
        msg.msg_iovlen = 1;
        msg.msg_control = cbuf;
        msg.msg_controllen = sizeof(cbuf);

        ::cmsghdr* cmsg = CMSG_FIRSTHDR(&msg);
        cmsg->cmsg_level = SOL_UDP;
        cmsg->cmsg_type = UDP_SEGMENT;
        cmsg->cmsg_len = CMSG_LEN(sizeof(uint16_t));
        *reinterpret_cast<uint16_t*>(CMSG_DATA(cmsg)) = kSegmentSize;

        for (size_t i = 0; i < kIterations; ++i) {
            if (::sendmsg(fd_, &msg, 0) < 0) {
                throw std::system_error(errno, std::generic_category(), "sendmsg failed");
            }
        }
    }

    void run_standard_test(std::span<const std::byte> payload) {
        for (size_t i = 0; i < kIterations; ++i) {
            for (size_t j = 0; j < kNumSegments; ++j) {
                ssize_t ret = ::sendto(
                    fd_,
                    payload.data() + (j * kSegmentSize),
                    kSegmentSize,
                    0,
                    reinterpret_cast<const sockaddr*>(&dst_addr_),
                    sizeof(dst_addr_)
                );
                if (ret < 0) throw std::system_error(errno, std::generic_category(), "sendto failed");
            }
        }
    }
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <IP> <PORT> [gso|std]\n";
        return 1;
    }

    bool use_gso = (argc >= 4 && std::string_view(argv[3]) == "gso");
    std::vector<std::byte> payload(kTotalPayload, std::byte{'X'});

    try {
        UdpBenchmark bench(argv[1], static_cast<uint16_t>(std::atoi(argv[2])));
        
        auto t0 = std::chrono::high_resolution_clock::now();
        if (use_gso) {
            bench.run_gso_test(payload);
        } else {
            bench.run_standard_test(payload);
        }
        auto t1 = std::chrono::high_resolution_clock::now();

        std::chrono::duration<double> diff = t1 - t0;
        double total_bytes = static_cast<double>(kTotalPayload * kIterations);
        double mbits = (total_bytes * 8.0) / (diff.count() * 1e6);

        std::cout << "Режим: " << (use_gso ? "UDP-GSO" : "Стандартний UDP") << "\n";
        std::cout << "Час: " << diff.count() << " сек, Пропускна здатність: " << mbits << " Mbit/s\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
