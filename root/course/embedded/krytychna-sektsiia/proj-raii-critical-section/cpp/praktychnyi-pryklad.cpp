#include "critical_section.hpp"
#include <optional>

struct NavigationData {
    std::int32_t  latitude{0};
    std::int32_t  longitude{0};
    std::int32_t  altitude_mm{0};
    std::uint64_t timestamp_us{0};
};

class NavigationManager {
public:
    void update(std::int32_t lat, std::int32_t lon, std::int32_t alt, std::uint64_t ts) noexcept {
        // RAII-вартовий: автоматично знімає блокування при виході з методу
        const embedded::sync::IrqGuard lock;
        
        data_.latitude = lat;
        data_.longitude = lon;
        data_.altitude_mm = alt;
        data_.timestamp_us = ts;
    }

    [[nodiscard]] NavigationData get_snapshot() const noexcept {
        const embedded::sync::IrqGuard lock;
        return data_; // Повернення захищеної копії об'єкта
    }

private:
    NavigationData data_{};
};
