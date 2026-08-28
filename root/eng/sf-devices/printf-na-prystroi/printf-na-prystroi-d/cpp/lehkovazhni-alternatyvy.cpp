#include <cstdint>
#include <cstddef>
#include <string_view>
#include <span>
#include <array>

class MiniFormatter {
public:
    static size_t format_u32(uint32_t val, std::span<char> dest) noexcept {
        if (dest.empty()) return 0;
        if (val == 0) {
            dest[0] = '0';
            return 1;
        }

        std::array<char, 11> temp{};
        size_t digits = 0;
        while (val > 0 && digits < temp.size()) {
            temp[digits++] = static_cast<char>('0' + (val % 10U));
            val /= 10U;
        }

        const size_t count = (digits < dest.size()) ? digits : dest.size();
        for (size_t i = 0; i < count; ++i) {
            dest[i] = temp[digits - 1U - i];
        }
        return count;
    }

    static size_t append_str(std::string_view sv, std::span<char> dest) noexcept {
        const size_t count = (sv.size() < dest.size()) ? sv.size() : dest.size();
        for (size_t i = 0; i < count; ++i) {
            dest[i] = sv[i];
        }
        return count;
    }
};
