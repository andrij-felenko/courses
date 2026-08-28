// main.cpp — Ідіоматична реалізація мовою C++20
#include <iostream>
#include <iomanip>
#include <memory>
#include <string_view>
#include <csignal>
#include <atomic>
#include <bpf/libbpf.h>
#include "packet_probe.skel.h"

namespace {
    std::atomic<bool> g_exiting{false};

    void sig_handler(int) {
        g_exiting.store(true, std::memory_order_relaxed);
    }

    struct alignas(8) Event {
        std::uint64_t skb_addr;
        std::uint64_t latency_softirq_us;
        std::uint64_t latency_netfilter_us;
        std::uint64_t latency_total_us;
        std::uint32_t src_ip;
        std::uint32_t dst_ip;
        std::uint16_t src_port;
        std::uint16_t dst_port;
        std::uint16_t protocol;
        std::uint32_t drop_reason;
        char ifname[16];
    };

    [[nodiscard]] constexpr std::string_view get_drop_reason(std::uint32_t reason) noexcept {
        switch (reason) {
        case 0:  return "DELIVERED_OK";
        case 1:  return "NOT_SPECIFIED";
        case 2:  return "NO_SOCKET";
        case 3:  return "PKT_TOO_SMALL";
        case 4:  return "TCP_CSUM";
        case 5:  return "SOCKET_RCVBUFF";
        case 8:  return "NETFILTER_DROP";
        case 10: return "IP_INADDRERRORS";
        case 32: return "XDP_DROP";
        case 36: return "TC_INGRESS_DROP";
        default: return "OTHER_REASON";
        }
    }

    int handle_event(void*, void* data, std::size_t size) {
        if (size < sizeof(Event)) return 0;
        const auto* e = static_cast<const Event*>(data);

        std::cout << "[SKB 0x" << std::hex << e->skb_addr << std::dec << "] "
                  << "Total Latency: " << std::setw(6) << e->latency_total_us << " us | "
                  << "Status: " << std::setw(16) << std::left << get_drop_reason(e->drop_reason) << " | "
                  << "DropCode: " << e->drop_reason << "\n";
        return 0;
    }

    // RAII-обгортка для керування життєвим циклом BPF-скелета
    struct SkeletonDeleter {
        void operator()(packet_probe_bpf* s) const noexcept {
            packet_probe_bpf__destroy(s);
        }
    };
    using SkeletonPtr = std::unique_ptr<packet_probe_bpf, SkeletonDeleter>;

    // RAII-обгортка для BPF Ring Buffer
    struct RingBufferDeleter {
        void operator()(ring_buffer* rb) const noexcept {
            ring_buffer__free(rb);
        }
    };
    using RingBufferPtr = std::unique_ptr<ring_buffer, RingBufferDeleter>;
}

int main() {
    std::signal(SIGINT, sig_handler);
    std::signal(SIGTERM, sig_handler);

    SkeletonPtr skel{packet_probe_bpf__open_and_load()};
    if (!skel) {
        std::cerr << "Помилка завантаження BPF скелета в ядро\n";
        return 1;
    }

    if (const int err = packet_probe_bpf__attach(skel.get()); err != 0) {
        std::cerr << "Помилка прикріплення BPF програм: " << err << "\n";
        return 1;
    }

    RingBufferPtr rb{ring_buffer__new(bpf_map__fd(skel->maps.events), handle_event, nullptr, nullptr)};
    if (!rb) {
        std::cerr << "Помилка ініціалізації кільцевого буфера подій\n";
        return 1;
    }

    std::cout << std::left << std::setw(20) << "SKB Pointer"
              << std::setw(24) << "Total Traversal Time"
              << std::setw(20) << "Kernel Verdict"
              << "Reason ID\n";
    std::cout << std::string(80, '-') << "\n";

    while (!g_exiting.load(std::memory_order_relaxed)) {
        if (const int err = ring_buffer__poll(rb.get(), 100); err < 0 && err != -EINTR) {
            std::cerr << "Помилка опитування Ring Buffer: " << err << "\n";
            break;
        }
    }

    std::cout << "\nТрасування завершено безпечно.\n";
    return 0;
}
