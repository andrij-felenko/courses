#include <cstdint>
#include <cstddef>
#include <vector>
#include <string_view>
#include <optional>
#include <span>
#include <memory>

namespace filters {

class QuotientFilter {
public:
    struct Slot {
        uint8_t is_occupied : 1 = 0;
        uint8_t is_continuation : 1 = 0;
        uint8_t is_shifted : 1 = 0;
        uint8_t remainder : 5 = 0;
    };

    static constexpr double kDefaultMaxLoadFactor = 0.85;

    explicit QuotientFilter(size_t q_bits, size_t r_bits);
    ~QuotientFilter() = default;

    QuotientFilter(const QuotientFilter&) = delete;
    QuotientFilter& operator=(const QuotientFilter&) = delete;
    QuotientFilter(QuotientFilter&&) noexcept = default;
    QuotientFilter& operator=(QuotientFilter&&) noexcept = default;

    [[nodiscard]] bool contains(std::string_view key) const noexcept;
    bool insert(std::string_view key);
    bool remove(std::string_view key) noexcept;

    [[nodiscard]] size_t size() const noexcept;
    [[nodiscard]] size_t capacity() const noexcept;
    [[nodiscard]] double load_factor() const noexcept;
    [[nodiscard]] bool empty() const noexcept;
    void clear() noexcept;

private:
    size_t q_bits_;
    size_t r_bits_;
    size_t num_slots_;
    size_t slot_mask_;
    size_t count_ = 0;
    std::vector<Slot> table_;
};

} // namespace filters
