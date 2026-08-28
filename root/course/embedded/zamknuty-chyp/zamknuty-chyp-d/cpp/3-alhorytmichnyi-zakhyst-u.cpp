// Захищена перевірка стану безпеки з подвійним комплементарним кодуванням на C++20
#include <cstdint>
#include <concepts>

namespace security {

class HardenedSecurityState {
public:
    static constexpr uint32_t StateLocked    = 0x5AA55AA5U;
    static constexpr uint32_t StateInvLocked = 0xA55AA55AU;

    [[nodiscard]] static bool is_valid_and_locked() noexcept {
        const uint32_t direct = marker_;
        const uint32_t inverse = marker_inv_;

        if (direct != StateLocked || inverse != StateInvLocked || ((direct ^ inverse) != 0xFFFFFFFFU)) {
            trigger_tamper_wipe();
            return false;
        }
        return true;
    }

private:
    static inline volatile uint32_t marker_{StateLocked};
    static inline volatile uint32_t marker_inv_{StateInvLocked};

    static void trigger_tamper_wipe() noexcept;
};

} // namespace security
