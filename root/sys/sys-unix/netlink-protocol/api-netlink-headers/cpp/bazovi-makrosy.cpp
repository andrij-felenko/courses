#include <linux/netlink.h>
#include <span>
#include <cstdint>

// C++20 обгортки та constexpr-функції замість макросів препроцесора
namespace netlink {
    constexpr size_t AlignTo = 4;

    [[nodiscard]] constexpr size_t align(size_t len) noexcept {
        return (len + AlignTo - 1) & ~(AlignTo - 1);
    }

    [[nodiscard]] inline std::span<const uint8_t> payload(const nlmsghdr* nlh) noexcept {
        auto data_ptr = reinterpret_cast<const uint8_t*>(nlh) + NLMSG_HDRLEN;
        size_t data_len = nlh->nlmsg_len > NLMSG_HDRLEN ? nlh->nlmsg_len - NLMSG_HDRLEN : 0;
        return {data_ptr, data_len};
    }
}
