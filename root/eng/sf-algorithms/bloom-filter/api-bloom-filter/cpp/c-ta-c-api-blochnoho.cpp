#include <cstdint>
#include <vector>
#include <cstddef>

namespace sys {

class alignas(64) blocked_bloom_filter {
public:
    explicit blocked_bloom_filter(std::size_t num_blocks, std::size_t k_hashes);
    ~blocked_bloom_filter() noexcept;

    blocked_bloom_filter(const blocked_bloom_filter&) = delete;
    blocked_bloom_filter& operator=(const blocked_bloom_filter&) = delete;
    blocked_bloom_filter(blocked_bloom_filter&&) noexcept = default;
    blocked_bloom_filter& operator=(blocked_bloom_filter&&) noexcept = default;

    void add_with_hashes(std::uint64_t h1, std::uint64_t h2) noexcept;
    [[nodiscard]] bool contains_with_hashes(std::uint64_t h1, std::uint64_t h2) const noexcept;

private:
    struct alignas(64) block {
        std::uint32_t words[16]{0};
    };
    
    std::size_t num_blocks_;
    std::size_t k_;
    block* blocks_{nullptr};
};

} // namespace sys
