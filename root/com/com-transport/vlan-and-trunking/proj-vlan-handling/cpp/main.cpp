#include <iostream>
#include <vector>
#include <span>
#include <expected>
#include <cstdint>
#include <cstring>
#include <iomanip>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <net/ethernet.h>

namespace net {

constexpr uint16_t eth_p_8021q = 0x8100;

enum class ParseError {
    FrameTooShort,
    NotVlanTagged
};

struct VlanHeaderInfo {
    uint16_t vid;
    uint8_t pcp;
    bool dei;
    uint16_t inner_ethertype;
};

// RAII обгортка для мережевого сирого сокета
class RawSocket {
    int fd_ = -1;
public:
    explicit RawSocket(uint16_t protocol) {
        fd_ = ::socket(AF_PACKET, SOCK_RAW, htons(protocol));
    }

    ~RawSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    RawSocket(const RawSocket&) = delete;
    RawSocket& operator=(const RawSocket&) = delete;

    RawSocket(RawSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    RawSocket& operator=(RawSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] bool isValid() const { return fd_ >= 0; }
    [[nodiscard]] int get() const { return fd_; }
};

class VlanFrameParser {
public:
    static std::expected<VlanHeaderInfo, ParseError> parse(std::span<const std::byte> frame) {
        constexpr size_t min_tagged_size = sizeof(ether_header) + 4;
        if (frame.size() < min_tagged_size) {
            return std::unexpected(ParseError::FrameTooShort);
        }

        const auto* eth = reinterpret_cast<const ether_header*>(frame.data());
        uint16_t ether_type = ntohs(eth->ether_type);

        if (ether_type != eth_p_8021q) {
            return std::unexpected(ParseError::NotVlanTagged);
        }

        uint16_t raw_tci;
        std::memcpy(&raw_tci, frame.data() + sizeof(ether_header) + 2, sizeof(uint16_t));
        uint16_t tci = ntohs(raw_tci);

        uint16_t raw_inner;
        std::memcpy(&raw_inner, frame.data() + sizeof(ether_header) + 4, sizeof(uint16_t));

        return VlanHeaderInfo{
            .vid = static_cast<uint16_t>(tci & 0x0FFF),
            .pcp = static_cast<uint8_t>((tci >> 13) & 0x07),
            .dei = static_cast<bool>((tci >> 12) & 0x01),
            .inner_ethertype = ntohs(raw_inner)
        };
    }
};

} // namespace net

int main() {
    net::RawSocket socket(ETH_P_ALL);
    if (!socket.isValid()) {
        std::cerr << "Помилка створення RAII raw-сокета. Перевірте root-права.\n";
        return 1;
    }

    std::vector<std::byte> buffer(2048);
    std::cout << "Запуск C++ RAII аналізатора кадрів...\n";

    for (int i = 0; i < 10; ++i) {
        ssize_t n = ::recvfrom(socket.get(), buffer.data(), buffer.size(), 0, nullptr, nullptr);
        if (n < 0) break;

        std::span<const std::byte> frame(buffer.data(), static_cast<size_t>(n));
        auto result = net::VlanFrameParser::parse(frame);

        if (result) {
            std::cout << "[VLAN TAGGED] VID: " << result->vid
                      << " | PCP: " << static_cast<int>(result->pcp)
                      << " | DEI: " << (result->dei ? "1" : "0")
                      << " | Inner Type: 0x" << std::hex << std::setw(4)
                      << std::setfill('0') << result->inner_ethertype
                      << std::dec << "\n";
        } else if (result.error() == net::ParseError::NotVlanTagged) {
            std::cout << "[UNTAGGED Frame]\n";
        }
    }

    return 0;
}
