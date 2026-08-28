// compat/utilities.hpp
#pragma once

#include <type_traits>
#include <cstring>

#include "version_check.hpp"

namespace compat {

#if defined(__cpp_lib_to_underlying) && (__cpp_lib_to_underlying >= 202102L)
    using std::to_underlying;
#else
    template <typename Enum>
    constexpr std::underlying_type_t<Enum> to_underlying(Enum e) noexcept {
        return static_cast<std::underlying_type_t<Enum>>(e);
    }
#endif

#if defined(__cpp_lib_bit_cast) && (__cpp_lib_bit_cast >= 201806L)
    using std::bit_cast;
#else
    template <typename To, typename From>
    To bit_cast(const From& src) noexcept {
        static_assert(sizeof(To) == sizeof(From), "bit_cast types must have identical size");
        static_assert(std::is_trivially_copyable<To>::value, "To type must be trivially copyable");
        static_assert(std::is_trivially_copyable<From>::value, "From type must be trivially copyable");

        To dst;
        std::memcpy(&dst, &src, sizeof(To));
        return dst;
    }
#endif

} // namespace compat
