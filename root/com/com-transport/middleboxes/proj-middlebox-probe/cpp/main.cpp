#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <expected>
#include <span>
#include <cstring>
#include <cstdint>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <sys/socket.h>
#include <sys/time.h>

namespace netprobe {

constexpr size_t kPacketBufferSize = 4096;
constexpr uint16_t kTestMss = 1460;
constexpr uint8_t kExperimentalOptKind = 30; // MPTCP Kind

struct PseudoHeader {
    uint32_t src_ip{0};
    uint32_t dst_ip{0};
    uint8_t  placeholder{0};
    uint8_t  protocol{IPPROTO_TCP};
    uint16_t tcp_length{0};
};

enum class ProbeError {
    SocketCreationFailed,
    OptionSetFailed,
    SendFailed,
    Timeout,
    InvalidPacket
};

class UniqueSocket {
public:
    explicit UniqueSocket(int fd) : fd_(fd) {}
    ~UniqueSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    UniqueSocket(const UniqueSocket&) = delete;
    UniqueSocket& operator=(const UniqueSocket&) = delete;
    UniqueSocket(UniqueSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    UniqueSocket& operator=(UniqueSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

private:
    int fd_{-1};
};

[[nodiscard]] uint16_t calculate_checksum(std::span<const uint8_t> data) noexcept {
    uint32_t sum = 0;
    size_t count = data.size();
    const auto* ptr = reinterpret_cast<const uint16_t*>(data.data());

    while (count > 1) {
        sum += *ptr++;
        count -= 2;
    }
    if (count > 0) {
        sum += *reinterpret_cast<const uint8_t*>(ptr);
    }
    while (sum >> 16) {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }
    return static_cast<uint16_t>(~sum);
}

class MiddleboxScanner {
public:
    static std::expected<UniqueSocket, ProbeError> create_raw_socket(int protocol, bool ip_hdrincl = false) {
        int fd = ::socket(AF_INET, SOCK_RAW, protocol);
        if (fd < 0) {
            return std::unexpected(ProbeError::SocketCreationFailed);
        }
        if (ip_hdrincl) {
            int one = 1;
            if (::setsockopt(fd, IPPROTO_IP, IP_HDRINCL, &one, sizeof(one)) < 0) {
                ::close(fd);
                return std::unexpected(ProbeError::OptionSetFailed);
            }
        }
        return UniqueSocket(fd);
    }

    static std::expected<void, ProbeError> send_probe(
        const UniqueSocket& sock,
        std::string_view src_ip,
        std::string_view dst_ip,
        uint16_t src_port,
        uint16_t dst_port,
        uint32_t isn)
    {
        std::vector<uint8_t> packet(kPacketBufferSize, 0);

        auto* iph = reinterpret_cast<struct iphdr*>(packet.data());
        auto* tcph = reinterpret_cast<struct tcphdr*>(packet.data() + sizeof(struct iphdr));
        uint8_t* options = packet.data() + sizeof(struct iphdr) + sizeof(struct tcphdr);

        size_t opt_idx = 0;
        // MSS Option
        options[opt_idx++] = 2;
        options[opt_idx++] = 4;
        options[opt_idx++] = (kTestMss >> 8) & 0xFF;
        options[opt_idx++] = kTestMss & 0xFF;

        // Experimental MPTCP Option
        options[opt_idx++] = kExperimentalOptKind;
        options[opt_idx++] = 4;
        options[opt_idx++] = 0xDE;
        options[opt_idx++] = 0xAD;

        // Padding
        options[opt_idx++] = 1; // NOP
        options[opt_idx++] = 0; // EOL
        while (opt_idx % 4 != 0) {
            options[opt_idx++] = 0;
        }

        const size_t tcp_hdr_len = sizeof(struct tcphdr) + opt_idx;
        const size_t total_len = sizeof(struct iphdr) + tcp_hdr_len;

        // IP Header
        iph->ihl = 5;
        iph->version = 4;
        iph->tos = 0;
        iph->tot_len = htons(static_cast<uint16_t>(total_len));
        iph->id = htons(54321);
        iph->frag_off = htons(0x4000); // DF
        iph->ttl = 64;
        iph->protocol = IPPROTO_TCP;
        iph->saddr = ::inet_addr(src_ip.data());
        iph->daddr = ::inet_addr(dst_ip.data());
        iph->check = calculate_checksum(std::span<const uint8_t>(packet.data(), sizeof(struct iphdr)));

        // TCP Header
        tcph->source = htons(src_port);
        tcph->dest = htons(dst_port);
        tcph->seq = htonl(isn);
        tcph->ack_seq = 0;
        tcph->doff = static_cast<uint8_t>(tcp_hdr_len / 4);
        tcph->syn = 1;
        tcph->window = htons(65535);
        tcph->check = 0;
        tcph->urg_ptr = 0;

        // TCP Checksum calculation with PseudoHeader
        PseudoHeader psh{};
        psh.src_ip = iph->saddr;
        psh.dst_ip = iph->daddr;
        psh.placeholder = 0;
        psh.protocol = IPPROTO_TCP;
        psh.tcp_length = htons(static_cast<uint16_t>(tcp_hdr_len));

        std::vector<uint8_t> pseudo_block(sizeof(PseudoHeader) + tcp_hdr_len);
        std::memcpy(pseudo_block.data(), &psh, sizeof(PseudoHeader));
        std::memcpy(pseudo_block.data() + sizeof(PseudoHeader), tcph, tcp_hdr_len);

        tcph->check = calculate_checksum(pseudo_block);

        sockaddr_in sin{};
        sin.sin_family = AF_INET;
        sin.sin_port = htons(dst_port);
        sin.sin_addr.s_addr = iph->daddr;

        if (::sendto(sock.get(), packet.data(), total_len, 0,
                     reinterpret_cast<sockaddr*>(&sin), sizeof(sin)) < 0) {
            return std::unexpected(ProbeError::SendFailed);
        }

        std::cout << "[PROBE C++] SYN надіслано до " << dst_ip << ":" << dst_port
                  << " (ISN=" << isn << ", MSS=" << kTestMss << ")\n";
        return {};
    }

    static std::expected<void, ProbeError> receive_and_inspect(
        const UniqueSocket& sock,
        std::string_view expected_src,
        uint16_t expected_port,
        uint32_t sent_isn)
    {
        std::vector<uint8_t> buffer(kPacketBufferSize);
        timeval tv{ .tv_sec = 3, .tv_usec = 0 };
        ::setsockopt(sock.get(), SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

        while (true) {
            ssize_t len = ::recvfrom(sock.get(), buffer.data(), buffer.size(), 0, nullptr, nullptr);
            if (len < 0) {
                return std::unexpected(ProbeError::Timeout);
            }

            const auto* iph = reinterpret_cast<const struct iphdr*>(buffer.data());
            if (iph->protocol != IPPROTO_TCP) continue;

            const size_t ip_hdr_len = iph->ihl * 4;
            if (static_cast<size_t>(len) < ip_hdr_len + sizeof(struct tcphdr)) continue;

            const auto* tcph = reinterpret_cast<const struct tcphdr*>(buffer.data() + ip_hdr_len);
            in_addr src_addr{ .s_addr = iph->saddr };
            std::string_view src_ip_str(::inet_ntoa(src_addr));

            if (src_ip_str == expected_src && ntohs(tcph->source) == expected_port) {
                std::cout << "\n--- АНАЛІЗ РЕЗУЛЬТАТІВ ЗОНДУВАННЯ (C++) ---\n";
                std::cout << "Отримано прапорці: " << (tcph->syn ? "SYN " : "")
                          << (tcph->ack ? "ACK " : "") << "\n";

                uint32_t recv_ack = ntohl(tcph->ack_seq);
                std::cout << "Ack Seq: " << recv_ack << " (Очікувано: " << sent_isn + 1 << ")\n";

                if (recv_ack != sent_isn + 1) {
                    std::cout << "  [!] ВИЯВЛЕНО ПІДМІНУ ISN / СЕКВЕНЦІЇ!\n";
                } else {
                    std::cout << "  [OK] Послідовність підтверджень збережена.\n";
                }

                const size_t tcp_hdr_len = tcph->doff * 4;
                if (tcp_hdr_len > sizeof(struct tcphdr)) {
                    const size_t opt_len = tcp_hdr_len - sizeof(struct tcphdr);
                    std::span<const uint8_t> opts(buffer.data() + ip_hdr_len + sizeof(struct tcphdr), opt_len);

                    size_t i = 0;
                    bool found_opt = false;
                    while (i < opts.size()) {
                        uint8_t kind = opts[i];
                        if (kind == 0) break;
                        if (kind == 1) { i++; continue; }
                        if (i + 1 >= opts.size()) break;
                        uint8_t opt_sz = opts[i + 1];
                        if (opt_sz < 2 || i + opt_sz > opts.size()) break;

                        if (kind == 2 && opt_sz == 4) {
                            uint16_t mss = (opts[i + 2] << 8) | opts[i + 3];
                            std::cout << "Опція MSS сервера: " << mss << "\n";
                        } else if (kind == kExperimentalOptKind) {
                            found_opt = true;
                            std::cout << "  [OK] Експериментальна опція Kind=" << static_cast<int>(kind)
                                      << " успішно пройшла шлях без видалення!\n";
                        }
                        i += opt_sz;
                    }
                    if (!found_opt) {
                        std::cout << "  [!] Опцію Kind=" << static_cast<int>(kExperimentalOptKind)
                                  << " вирізано проміжним вузлом (Option Stripping).\n";
                    }
                }
                return {};
            }
        }
    }
};

} // namespace netprobe

int main(int argc, char* argv[]) {
    if (argc < 5) {
        std::cerr << "Використання: %s <src_ip> <dst_ip> <src_port> <dst_port>\n";
        return 1;
    }

    auto raw_sock = netprobe::MiddleboxScanner::create_raw_socket(IPPROTO_RAW, true);
    if (!raw_sock) {
        std::cerr << "Помилка створення сирого сокета (потрібен root / sudo)\n";
        return 1;
    }

    const uint16_t src_port = static_cast<uint16_t>(std::stoi(argv[3]));
    const uint16_t dst_port = static_cast<uint16_t>(std::stoi(argv[4]));
    constexpr uint32_t kProbeIsn = 0xABCDEF01;

    auto send_res = netprobe::MiddleboxScanner::send_probe(*raw_sock, argv[1], argv[2], src_port, dst_port, kProbeIsn);
    if (!send_res) {
        std::cerr << "Помилка відправки SYN-пакета\n";
        return 1;
    }

    auto recv_sock = netprobe::MiddleboxScanner::create_raw_socket(IPPROTO_TCP, false);
    if (recv_sock) {
        auto recv_res = netprobe::MiddleboxScanner::receive_and_inspect(*recv_sock, argv[2], dst_port, kProbeIsn);
        if (!recv_res) {
            std::cout << "[ЗБІЙ] Тайм-аут отримання відповіді.\n";
        }
    }

    return 0;
}
