#include <cstdint>
#include <span>

namespace secure_boot {

enum class AuthStatus : uint32_t {
    Success       = 0x5555AAAAU,
    Failure       = 0xAAAA5555U,
    Uninitialized = 0x00000000U
};

/* Асемблерний бар'єр пам'яті */
inline void compiler_barrier() noexcept {
    asm volatile("" ::: "memory");
}

/* Клас контролю цілісності ланцюга виконання */
class FlowTracker {
public:
    constexpr explicit FlowTracker(uint32_t initial_seed) noexcept 
        : current_token_(initial_seed), seed_(initial_seed) {}

    void step(uint32_t signature) noexcept {
        compiler_barrier();
        current_token_ ^= signature;
        compiler_barrier();
    }

    [[nodiscard]] bool is_flow_intact(uint32_t combined_signature) const noexcept {
        compiler_barrier();
        const uint32_t expected = seed_ ^ combined_signature;
        const uint32_t actual = current_token_;
        compiler_barrier();
        return (actual == expected) && ((actual ^ ~expected) == 0xFFFFFFFFU);
    }

private:
    volatile uint32_t current_token_;
    uint32_t seed_;
};

/* Прототипи системних функцій */
AuthStatus crypto_rsa_verify_hardened(std::span<const uint8_t> image) noexcept;
[[noreturn]] void emergency_lockup() noexcept;
void boot_kernel() noexcept;

void hardened_bootloader_main(std::span<const uint8_t> firmware_image) {
    FlowTracker tracker(0x1A2B3C4DU);
    constexpr uint32_t Step1Sign = 0x5E6F7A8BU;
    constexpr uint32_t Step2Sign = 0x9C8D7E6FU;

    compiler_barrier();

    /* Етап 1: Первинна криптографічна перевірка */
    const auto res1 = crypto_rsa_verify_hardened(firmware_image);
    compiler_barrier();

    if (res1 != AuthStatus::Success) {
        emergency_lockup();
    }

    tracker.step(Step1Sign);

    /* Етап 2: Повторна криптографічна перевірка */
    const auto res2 = crypto_rsa_verify_hardened(firmware_image);
    compiler_barrier();

    if (res2 == AuthStatus::Failure || res2 == AuthStatus::Uninitialized) {
        emergency_lockup();
    }

    tracker.step(Step2Sign);

    /* Етап 3: Перевірка ідентичності результатів */
    if (static_cast<uint32_t>(res1) != static_cast<uint32_t>(res2)) {
        emergency_lockup();
    }
    compiler_barrier();

    /* Етап 4: Перевірка проходження всіх контрольних точок */
    if (!tracker.is_flow_intact(Step1Sign ^ Step2Sign)) {
        emergency_lockup();
    }

    boot_kernel();
}

} // namespace secure_boot
