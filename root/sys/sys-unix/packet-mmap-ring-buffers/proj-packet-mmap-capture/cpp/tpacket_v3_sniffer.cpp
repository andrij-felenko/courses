// tpacket_v3_sniffer.cpp — Ідіоматична реалізація C++20 з RAII
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <memory>
#include <system_error>
#include <atomic>
#include <csignal>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/mman.h>
#include <sys/poll.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <netinet/if_ether.h>
#include <netinet/ip.h>
#include <linux/if_packet.h>

namespace net {

static std::atomic<bool> g_running{true};

void signal_handler(int) {
    g_running.store(false, std::memory_order_relaxed);
}

// RAII-обгортка для керування сокетом
class SocketFd {
    int m_fd{-1};
public:
    explicit SocketFd(int fd) : m_fd(fd) {}
    ~SocketFd() {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
    }
    SocketFd(const SocketFd&) = delete;
    SocketFd& operator=(const SocketFd&) = delete;
    SocketFd(SocketFd&& other) noexcept : m_fd(other.m_fd) { other.m_fd = -1; }
    
    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }
};

// RAII-обгортка для змонтованої пам'яті mmap
class MmappedRing {
    std::span<std::byte> m_region;
public:
    MmappedRing(void* addr, size_t size) 
        : m_region(static_cast<std::byte*>(addr), size) {}
    
    ~MmappedRing() {
        if (!m_region.empty() && m_region.data() != MAP_FAILED) {
            ::munmap(m_region.data(), m_region.size());
        }
    }

    MmappedRing(const MmappedRing&) = delete;
    MmappedRing& operator=(const MmappedRing&) = delete;
    
    [[nodiscard]] std::span<std::byte> get() const noexcept { return m_region; }
    [[nodiscard]] std::byte* data() const noexcept { return m_region.data(); }
};

class PacketSnifferV3 {
    SocketFd m_sock;
    tpacket_req3 m_req{};
    std::unique_ptr<MmappedRing> m_ring;
    std::string m_ifname;

public:
    explicit PacketSnifferV3(std::string_view ifname) 
        : m_sock(::socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL))), m_ifname(ifname) 
    {
        if (!m_sock.valid()) {
            throw std::system_error(errno, std::generic_category(), "Помилка створення AF_PACKET сокета");
        }

        // Встановлення версії TPACKET_V3
        int version = TPACKET_V3;
        if (::setsockopt(m_sock.get(), SOL_PACKET, PACKET_VERSION, &version, sizeof(version)) < 0) {
            throw std::system_error(errno, std::generic_category(), "setsockopt PACKET_VERSION");
        }

        m_req.tp_block_size = 1024 * 1024; // 1 MB
        m_req.tp_block_nr = 64;            // 64 MB всього
        m_req.tp_frame_size = 2048;
        m_req.tp_frame_nr = (m_req.tp_block_size * m_req.tp_block_nr) / m_req.tp_frame_size;
        m_req.tp_retire_blk_tov = 10;      // 10 мс timeout
        m_req.tp_feature_req_word = TP_FT_REQ_FILL_RXHASH;

        if (::setsockopt(m_sock.get(), SOL_PACKET, PACKET_RX_RING, &m_req, sizeof(m_req)) < 0) {
            throw std::system_error(errno, std::generic_category(), "setsockopt PACKET_RX_RING");
        }

        size_t total_bytes = static_cast<size_t>(m_req.tp_block_size) * m_req.tp_block_nr;
        void* addr = ::mmap(nullptr, total_bytes, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_LOCKED, m_sock.get(), 0);
        if (addr == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "mmap ring buffer");
        }
        m_ring = std::make_unique<MmappedRing>(addr, total_bytes);

        sockaddr_ll sll{};
        sll.sll_family = AF_PACKET;
        sll.sll_protocol = htons(ETH_P_ALL);
        sll.sll_ifindex = ::if_nametoindex(m_ifname.c_str());
        if (sll.sll_ifindex == 0) {
            throw std::runtime_error("Мережевий інтерфейс " + m_ifname + " не знайдено");
        }

        if (::bind(m_sock.get(), reinterpret_cast<sockaddr*>(&sll), sizeof(sll)) < 0) {
            throw std::system_error(errno, std::generic_category(), "bind socket");
        }
    }

    void run() {
        unsigned int block_idx = 0;
        uint64_t packet_count = 0;
        pollfd pfd{.fd = m_sock.get(), .events = POLLIN | POLLERR, .revents = 0};

        while (g_running.load(std::memory_order_relaxed)) {
            auto* block_ptr = m_ring->data() + (block_idx * m_req.tp_block_size);
            auto* pbd = reinterpret_cast<block_desc*>(block_ptr);

            if ((pbd->h1.block_status & TP_STATUS_USER) == 0) {
                ::poll(&pfd, 1, 10);
                continue;
            }

            uint32_t num_pkts = pbd->h1.num_pkts;
            auto* pkt_ptr = reinterpret_cast<uint8_t*>(pbd) + pbd->h1.offset_to_first_pkt;

            for (uint32_t i = 0; i < num_pkts; ++i) {
                auto* hdr = reinterpret_cast<tpacket3_hdr*>(pkt_ptr);
                auto* eth = reinterpret_cast<ethhdr*>(pkt_ptr + hdr->tp_mac);

                if (ntohs(eth->h_proto) == ETH_P_IP) {
                    // Витягнення IPv4 пакету у C++20 span
                    std::span<const std::byte> pkt_span(
                        reinterpret_cast<const std::byte*>(pkt_ptr + hdr->tp_net), 
                        hdr->tp_snaplen
                    );
                    (void)pkt_span;
                }

                packet_count++;
                pkt_ptr += hdr->tp_next_offset;
            }

            pbd->h1.block_status = TP_STATUS_KERNEL;
            block_idx = (block_idx + 1) % m_req.tp_block_nr;
        }

        std::cout << "\nЗупинено. Оброблено пакетів: " << packet_count << std::endl;
    }
};

} // namespace net

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <мережевий_інтерфейс>\n";
        return EXIT_FAILURE;
    }

    std::signal(SIGINT, net::signal_handler);
    std::signal(SIGTERM, net::signal_handler);

    try {
        net::PacketSnifferV3 sniffer(argv[1]);
        std::cout << "Сніфер C++ TPACKET_V3 запущено на " << argv[1] << "...\n";
        sniffer.run();
    } catch (const std::exception& ex) {
        std::cerr << "Фатальна помилка: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
