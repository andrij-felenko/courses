#include <cstdint>
#include <array>
#include <span>

namespace embedded::filter {

/**
 * @brief Векторний 32-канальний паралельний фільтр N-з-M на C++20
 */
class VectorFilter32Channels final {
public:
    static constexpr std::size_t WindowSize = 8;

    constexpr explicit VectorFilter32Channels(uint32_t initial_state = 0) noexcept
        : output_mask_(initial_state) {
        slices_.fill(initial_state);
    }

    /**
     * @brief Паралельний крок фільтрації для всіх 32 входів одночасно
     * @param raw_inputs Стан 32 пінів у єдиному машинному слові
     * @return 32 відфільтровані вихідні біти
     */
    [[nodiscard]] uint32_t Update(uint32_t raw_inputs) noexcept {
        slices_[write_index_] = raw_inputs;
        write_index_ = (write_index_ + 1) % WindowSize;

        uint32_t s0 = 0;
        uint32_t s1 = 0;
        uint32_t s2 = 0;

        // Розгортання паралельного біт-слайс суматора
        for (uint32_t slice : slices_) {
            const uint32_t carry0 = s0 & slice;
            s0 ^= slice;

            const uint32_t carry1 = s1 & carry0;
            s1 ^= carry0;

            s2 ^= carry1;
        }

        // Паралельні умови гістерезису: N_on >= 6 (s2 & s1), N_off <= 2
        const uint32_t set_mask   = s2 & s1;
        const uint32_t reset_mask = (~s2 & ~s1) | (~s2 & ~s0);

        output_mask_ = (output_mask_ | set_mask) & ~reset_mask;
        return output_mask_;
    }

    [[nodiscard]] uint32_t GetStates() const noexcept {
        return output_mask_;
    }

private:
    std::array<uint32_t, WindowSize> slices_{};
    std::size_t                      write_index_{0};
    uint32_t                         output_mask_{0};
};

} // namespace embedded::filter
