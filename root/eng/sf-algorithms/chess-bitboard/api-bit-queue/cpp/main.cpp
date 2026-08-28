#include <cstdint>
#include <cstddef>
#include <array>
#include <bit>
#include <optional>

struct alignas(64) BitQueue64 {
    uint64_t mask{0};
    size_t   count{0};
};

struct alignas(64) BitQueue128 {
    std::array<uint64_t, 2> words{0, 0};
    size_t                  count{0};
};
