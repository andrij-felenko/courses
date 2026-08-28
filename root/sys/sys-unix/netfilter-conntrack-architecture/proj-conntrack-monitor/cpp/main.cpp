#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <format>
#include <csignal>
#include <atomic>
#include <expected>
#include <arpa/inet.h>
#include <libnetfilter_conntrack/libnetfilter_conntrack.h>

namespace {

std::atomic<bool> g_stop{false};

void signal_handler(int) noexcept {
    g_stop.store(true, std::memory_order_relaxed);
}

struct NfctHandleDeleter {
    void operator()(nfct_handle* h) const noexcept {
        if (h) {
            nfct_close(h);
        }
    }
};

using UniqueNfctHandle = std::unique_ptr<nfct_handle, NfctHandleDeleter>;

std::string format_ip(uint32_t net_ip) {
    char buf[INET_ADDRSTRLEN]{};
    in_addr addr{.s_addr = net_ip};
    inet_ntop(AF_INET, &addr, buf, sizeof(buf));
    return std::string(buf);
}

std::string_view get_event_type_name(enum nfct_msg_type type) noexcept {
    switch (type) {
        case NFCT_T_NEW:     return "NEW    ";
        case NFCT_T_UPDATE:  return "UPDATE ";
        case NFCT_T_DESTROY: return "DESTROY";
        default:             return "UNKNOWN";
    }
}

int conntrack_event_callback(enum nfct_msg_type type,
                             struct nf_conntrack* ct,
                             void* /*data*/) noexcept {
    try {
        uint8_t proto = nfct_get_attr_u8(ct, ATTR_L4PROTO);
        uint32_t src_ip = nfct_get_attr_u32(ct, ATTR_ORIG_IPV4_SRC);
        uint32_t dst_ip = nfct_get_attr_u32(ct, ATTR_ORIG_IPV4_DST);
        uint16_t src_port = ntohs(nfct_get_attr_u16(ct, ATTR_ORIG_PORT_SRC));
        uint16_t dst_port = ntohs(nfct_get_attr_u16(ct, ATTR_ORIG_PORT_DST));
        uint32_t status = nfct_get_attr_u32(ct, ATTR_STATUS);

        std::string_view proto_str = (proto == IPPROTO_TCP) ? "TCP" :
                                     (proto == IPPROTO_UDP) ? "UDP" : "OTHER";

        bool is_assured = (status & IPS_ASSURED) != 0;

        std::cout << std::format("[{}] {} {}:{} -> {}:{} (status=0x{:08x}{})\n",
                                  get_event_type_name(type),
                                  proto_str,
                                  format_ip(src_ip), src_port,
                                  format_ip(dst_ip), dst_port,
                                  status,
                                  is_assured ? " [ASSURED]" : "");
    } catch (...) {
        // Запобігаємо поширенню винятків через межу C-виклику
    }
    return NFCT_CB_CONTINUE;
}

std::expected<UniqueNfctHandle, std::string> create_monitored_handle() {
    nfct_handle* raw_handle = nfct_open(NFNL_SUBSYS_CTNETLINK, NFCT_ALL_SYS_GROUP);
    if (!raw_handle) {
        return std::unexpected("Failed to open Netfilter Netlink socket");
    }

    UniqueNfctHandle handle(raw_handle);

    if (nfct_callback_register(handle.get(), NFCT_T_ALL, conntrack_event_callback, nullptr) < 0) {
        return std::unexpected("Failed to register conntrack event callback");
    }

    return handle;
}

} // namespace

int main() {
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    auto handle_result = create_monitored_handle();
    if (!handle_result) {
        std::cerr << "Initialization error: " << handle_result.error() << '\n';
        return EXIT_FAILURE;
    }

    const UniqueNfctHandle& handle = handle_result.value();
    std::cout << "Starting C++ Netfilter Conntrack Monitor... Press Ctrl+C to exit.\n";

    while (!g_stop.load(std::memory_order_relaxed)) {
        if (nfct_catch(handle.get()) < 0) {
            std::cerr << "Netfilter socket event error encountered.\n";
            break;
        }
    }

    std::cout << "Monitor stopped gracefully.\n";
    return EXIT_SUCCESS;
}
