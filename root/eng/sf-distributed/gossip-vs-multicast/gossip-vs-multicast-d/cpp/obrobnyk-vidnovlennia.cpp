#include <cstdint>
#include <expected>
#include <system_error>
#include <bit>
#include <endian.h>
#include <sys/socket.h>
#include <netinet/in.h>

#pragma pack(push, 1)
struct BwpRepairHeader {
    uint8_t  type{0x03};
    uint8_t  flags{0};
    uint16_t reserved{0};
    uint64_t missing_seq{0};
    uint32_t sender_node_id{0};
};
#pragma pack(pop)

[[nodiscard]] std::expected<void, std::error_code>
send_gossip_repair_request(int unicast_fd, const sockaddr_in& peer_addr,
                           uint64_t seq, uint32_t my_id) noexcept {
    BwpRepairHeader req{
        .type = 0x03,
        .flags = 0,
        .reserved = 0,
        .missing_seq = htobe64(seq),
        .sender_node_id = htonl(my_id)
    };

    const auto* buf = reinterpret_cast<const char*>(&req);
    ssize_t sent = ::sendto(unicast_fd, buf, sizeof(req), 0,
                            reinterpret_cast<const sockaddr*>(&peer_addr),
                            sizeof(peer_addr));

    if (sent < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    if (static_cast<size_t>(sent) != sizeof(req)) {
        return std::unexpected(std::make_error_code(std::errc::message_size));
    }

    return {};
}
