#include <cstdint>

struct PositionData {
    double latitude{0.0};
    double longitude{0.0};
    std::uint64_t timestamp{0};
};

// Небезпечне читання монолітної структури
PositionData unsafe_read(const PositionData& shared_data) noexcept {
    PositionData local_copy;
    // Неатомне копіювання полів може бути перерване потоком-письменником
    local_copy.latitude = shared_data.latitude;
    local_copy.longitude = shared_data.longitude;
    local_copy.timestamp = shared_data.timestamp;
    return local_copy;
}
