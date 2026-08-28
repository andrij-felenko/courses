// xsk_app.cpp
#include <iostream>
#include <memory>
#include <vector>
#include <system_error>
#include <csignal>
#include <cstring>
#include <unistd.h>
#include <poll.h>
#include <sys/mman.h>
#include <net/if.h>
#include <linux/if_xdp.h>
#include <xdp/xsk.h>
#include <span>

static volatile std::sig_atomic_t g_running = 1;

static void handle_signal(int) {
    g_running = 0;
}

class AfXdpEchoEngine {
    static constexpr size_t kNumFrames = 4096;
    static constexpr size_t kFrameSize = 2048;
    static constexpr size_t kBatchSize = 64;

    void* buffer_{nullptr};
    size_t buffer_size_{kNumFrames * kFrameSize};
    
    struct xsk_umem* umem_{nullptr};
    struct xsk_ring_prod fill_{};
    struct xsk_ring_cons comp_{};
    struct xsk_ring_cons rx_{};
    struct xsk_ring_prod tx_{};
    struct xsk_socket* xsk_{nullptr};

public:
    AfXdpEchoEngine(std::string_view ifname, uint32_t queue_id) {
        if (posix_memalign(&buffer_, getpagesize(), buffer_size_) != 0) {
            throw std::bad_alloc();
        }

        struct xsk_umem_config umem_cfg{};
        umem_cfg.fill_size = kNumFrames;
        umem_cfg.comp_size = kNumFrames;
        umem_cfg.frame_size = kFrameSize;
        umem_cfg.frame_headroom = XSK_UMEM__DEFAULT_FRAME_HEADROOM;
        umem_cfg.flags = 0;

        if (xsk_umem__create(&umem_, buffer_, buffer_size_, &fill_, &comp_, &umem_cfg) < 0) {
            ::free(buffer_);
            throw std::system_error(errno, std::generic_category(), "xsk_umem__create failed");
        }

        struct xsk_socket_config xsk_cfg{};
        xsk_cfg.rx_size = kNumFrames;
        xsk_cfg.tx_size = kNumFrames;
        xsk_cfg.libbpf_flags = XSK_LIBBPF_FLAGS__INHIBIT_PROG_LOAD;
        xsk_cfg.xdp_flags = XDP_FLAGS_UPDATE_IF_NOEXIST;
        xsk_cfg.bind_flags = XDP_ZEROCOPY | XDP_USE_NEED_WAKEUP;

        if (xsk_socket__create(&xsk_, ifname.data(), queue_id, umem_, &rx_, &tx_, &xsk_cfg) < 0) {
            xsk_cfg.bind_flags = XDP_COPY | XDP_USE_NEED_WAKEUP;
            if (xsk_socket__create(&xsk_, ifname.data(), queue_id, umem_, &rx_, &tx_, &xsk_cfg) < 0) {
                xsk_umem__delete(umem_);
                ::free(buffer_);
                throw std::system_error(errno, std::generic_category(), "xsk_socket__create failed");
            }
        }

        // Поповнюємо Fill Ring початковими кадрами
        uint32_t idx = 0;
        if (xsk_ring_prod__reserve(&fill_, kNumFrames / 2, &idx) == kNumFrames / 2) {
            for (size_t i = 0; i < kNumFrames / 2; ++i) {
                *xsk_ring_prod__fill_addr(&fill_, idx + i) = i * kFrameSize;
            }
            xsk_ring_prod__submit(&fill_, kNumFrames / 2);
        }
    }

    ~AfXdpEchoEngine() {
        if (xsk_) xsk_socket__delete(xsk_);
        if (umem_) xsk_umem__delete(umem_);
        if (buffer_) ::free(buffer_);
    }

    AfXdpEchoEngine(const AfXdpEchoEngine&) = delete;
    AfXdpEchoEngine& operator=(const AfXdpEchoEngine&) = delete;

    void process_single_batch() {
        uint32_t rx_idx = 0, tx_idx = 0, comp_idx = 0, fill_idx = 0;

        uint32_t rcvd = xsk_ring_cons__peek(&rx_, kBatchSize, &rx_idx);
        if (!rcvd) {
            if (xsk_ring_prod__needs_wakeup(&fill_)) {
                struct pollfd pfd{.fd = xsk_socket__fd(xsk_), .events = POLLIN, .revents = 0};
                ::poll(&pfd, 1, 10);
            }
            return;
        }

        uint32_t tx_reserved = xsk_ring_prod__reserve(&tx_, rcvd, &tx_idx);
        while (tx_reserved < rcvd) {
            if (xsk_ring_prod__needs_wakeup(&tx_)) {
                xsk_socket__wakeup(xsk_, XDP_WAKEUP_TX);
            }
            tx_reserved = xsk_ring_prod__reserve(&tx_, rcvd, &tx_idx);
        }

        for (uint32_t i = 0; i < rcvd; ++i) {
            const struct xdp_desc* desc = xsk_ring_cons__rx_desc(&rx_, rx_idx + i);
            uint64_t addr = desc->addr;
            uint32_t len = desc->len;

            auto frame_data = std::span<uint8_t>(
                static_cast<uint8_t*>(xsk_umem__get_data(buffer_, addr)), len
            );

            if (frame_data.size() >= 12) {
                // L2 MAC Swap
                std::swap_ranges(frame_data.begin(), frame_data.begin() + 6, frame_data.begin() + 6);
            }

            struct xdp_desc* tx_desc = xsk_ring_prod__tx_desc(&tx_, tx_idx + i);
            tx_desc->addr = addr;
            tx_desc->len = len;
        }

        xsk_ring_cons__release(&rx_, rcvd);
        xsk_ring_prod__submit(&tx_, rcvd);

        // Повернення оброблених кадрів з Completion Ring у Fill Ring
        uint32_t completed = xsk_ring_cons__peek(&comp_, kBatchSize, &comp_idx);
        if (completed > 0) {
            if (xsk_ring_prod__reserve(&fill_, completed, &fill_idx) == completed) {
                for (uint32_t i = 0; i < completed; ++i) {
                    uint64_t freed_addr = *xsk_ring_cons__comp_addr(&comp_, comp_idx + i);
                    *xsk_ring_prod__fill_addr(&fill_, fill_idx + i) = freed_addr;
                }
                xsk_ring_prod__submit(&fill_, completed);
            }
            xsk_ring_cons__release(&comp_, completed);
        }
    }

    void run() {
        while (g_running) {
            process_single_batch();
        }
    }
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <ifname> <queue_id>\n";
        return 1;
    }

    std::signal(SIGINT, handle_signal);
    std::signal(SIGTERM, handle_signal);

    try {
        AfXdpEchoEngine engine(argv[1], std::stoul(argv[2]));
        std::cout << "C++ AF_XDP Engine running on " << argv[1] << "...\n";
        engine.run();
    } catch (const std::exception& ex) {
        std::cerr << "Fatal error: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
