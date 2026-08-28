#include <cstdint>
#include <vector>
#include <cstddef>

class fast_bloom_filter {
public:
    fast_bloom_filter(std::size_t num_bits, std::size_t num_hashes)
        : num_bits_(num_bits), k_(num_hashes), bits_((num_bits + 7) / 8, 0) {}

    void add_hashes(std::uint64_t h1, std::uint64_t h2) noexcept {
        for (std::size_t i = 0; i < k_; ++i) {
            std::size_t bit_index = (h1 + i * h2) % num_bits_;
            bits_[bit_index >> 3] |= static_cast<std::uint8_t>(1u << (bit_index & 7));
        }
    }

    [[nodiscard]] bool check_hashes(std::uint64_t h1, std::uint64_t h2) const noexcept {
        for (std::size_t i = 0; i < k_; ++i) {
            std::size_t bit_index = (h1 + i * h2) % num_bits_;
            std::uint8_t byte = bits_[bit_index >> 3];
            if ((byte & (1u << (bit_index & 7))) == 0) {
                return false;
            }
        }
        return true;
    }

private:
    std::size_t num_bits_;
    std::size_t k_;
    std::vector<std::uint8_t> bits_;
};
