#include <cstdint>
#include <atomic>
#include <optional>

struct SeqlockVehicleState {
    std::atomic<uint32_t> sequence{0};
    VehicleState          state{};

    // Атомарне зчитування стану без блокування потоку
    [[nodiscard]] std::optional<VehicleState> read_atomic() const noexcept {
        for (uint32_t retries = 0; retries < 10; ++retries) {
            const uint32_t s1 = sequence.load(std::memory_order_acquire);
            if (s1 & 1U) {
                continue; // Запис у процесі
            }
            const VehicleState snapshot = state;
            const uint32_t s2 = sequence.load(std::memory_order_acquire);
            if (s1 == s2 && !(s1 & 1U)) {
                return snapshot;
            }
        }
        return std::nullopt; // Перевищено кількість спроб через високу активність запису
    }
};
