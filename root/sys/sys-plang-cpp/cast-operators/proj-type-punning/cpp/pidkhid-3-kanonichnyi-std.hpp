#include <cstdint>
#include <cstring>
#include <type_traits>

template <typename Target, typename Source>
Target safe_bit_cast(const Source& src) noexcept {
    static_assert(sizeof(Target) == sizeof(Source), "Розміри типів повинні збігатися");
    static_assert(std::is_trivially_copyable_v<Source>, "Source має бути trivially copyable");
    static_assert(std::is_trivially_copyable_v<Target>, "Target має бути trivially copyable");

    Target dst;
    std::memcpy(&dst, &src, sizeof(Target));
    return dst;
}

bool is_negative_memcpy(float f) noexcept {
    const auto u = safe_bit_cast<uint32_t>(f);
    return (u & 0x80000000u) != 0;
}
