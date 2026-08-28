#include <linux/netlink.h>
#include <string_view>
#include <span>
#include <cstdint>

// Безпечний парсинг NLA-атрибутів у C++20 через std::string_view та std::span
namespace netlink {
    [[nodiscard]] inline std::string_view get_string_attr(const nlattr* nla) noexcept {
        auto data = reinterpret_cast<const char*>(nla) + NLA_HDRLEN;
        auto len = static_cast<size_t>(NLA_PAYLOAD(nla));
        if (len > 0 && data[len - 1] == '\0') --len; // відкидаємо термінатор null
        return {data, len};
    }
}
