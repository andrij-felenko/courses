#include <cstdint>
#include <bit>

struct alignas(4) bloom_header {
    std::uint32_t magic{0x424C4F4F};
    std::uint32_t version{1};
    std::uint64_t num_bits{0};
    std::uint32_t num_hashes{0};
};

[[nodiscard]] inline bloom_header serialize_header(std::uint64_t m, std::uint32_t k) noexcept {
    bloom_header hdr;
    if constexpr (std::endian::native == std::endian::little) {
        hdr.magic = std::byteswap(hdr.magic);
        hdr.version = std::byteswap(hdr.version);
        hdr.num_bits = std::byteswap(m);
        hdr.num_hashes = std::byteswap(k);
    } else {
        hdr.num_bits = m;
        hdr.num_hashes = k;
    }
    return hdr;
}
