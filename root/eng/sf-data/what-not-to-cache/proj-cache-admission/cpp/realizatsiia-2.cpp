#include <cstdint>
#include <cstddef>
#include <string_view>
#include <array>
#include <algorithm>

class SegmentedBloomAdmissionFilter {
public:
    static constexpr size_t Bits = 65536;
    static constexpr size_t Words = Bits / 64;
    static constexpr size_t Mask = Bits - 1;
    static constexpr size_t RotationThreshold = 8000;

    SegmentedBloomAdmissionFilter() noexcept {
        reset();
    }

    void reset() noexcept {
        active_.fill(0);
        previous_.fill(0);
        insert_count_ = 0;
    }

    // Повертає true, якщо ключ зустрічався раніше (друге звернення -> допуск)
    [[nodiscard]] bool check_and_record(std::string_view key) noexcept {
        const auto [idx1, idx2] = compute_indices(key);

        const bool in_active = test_bit(active_, idx1) && test_bit(active_, idx2);
        const bool in_prev   = test_bit(previous_, idx1) && test_bit(previous_, idx2);

        set_bit(active_, idx1);
        set_bit(active_, idx2);

        if (++insert_count_ >= RotationThreshold) {
            previous_ = active_;
            active_.fill(0);
            insert_count_ = 0;
        }

        return in_active || in_prev;
    }

private:
    std::array<uint64_t, Words> active_{};
    std::array<uint64_t, Words> previous_{};
    size_t insert_count_{0};

    [[nodiscard]] static std::pair<uint32_t, uint32_t> compute_indices(std::string_view key) noexcept {
        uint64_t h1 = 0x100000001b3ULL ^ (key.size() * 0x517cc1b727220a95ULL);
        uint64_t h2 = 0xcbf29ce484222325ULL ^ key.size();
        for (const unsigned char c : key) {
            h1 = (h1 ^ static_cast<uint64_t>(c)) * 0x5bd1e9955bd1e995ULL;
            h2 = (h2 ^ static_cast<uint64_t>(c)) * 0x9e3779b97f4a7c15ULL;
        }
        return { static_cast<uint32_t>(h1 & Mask), static_cast<uint32_t>(h2 & Mask) };
    }

    [[nodiscard]] static bool test_bit(const std::array<uint64_t, Words>& table, uint32_t idx) noexcept {
        return (table[idx / 64] & (1ULL << (idx % 64))) != 0;
    }

    static void set_bit(std::array<uint64_t, Words>& table, uint32_t idx) noexcept {
        table[idx / 64] |= (1ULL << (idx % 64));
    }
};
