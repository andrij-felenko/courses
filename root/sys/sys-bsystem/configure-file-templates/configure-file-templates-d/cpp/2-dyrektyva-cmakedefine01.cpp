// C++20 код із виразом if constexpr
#include <cstdint>
#include <span>
#include "app/config.h"

auto compress_payload(std::span<const std::uint8_t> src, std::span<std::uint8_t> dst) {
    if constexpr (HAVE_ZSTD) {
        return zstd_compress(src, dst);
    } else {
        return raw_copy(src, dst);
    }
}
