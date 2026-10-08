#include <cstdint>
#include <array>

enum class VoltageRange : uint8_t {
    Range200mV = 0,
    Range2V,
    Range20V,
    Range200V,
    Range1000V,
    Count
};

class AutoRanger {
public:
    explicit AutoRanger(uint16_t max_counts = 1999, uint16_t min_counts = 180)
        : max_counts_(max_counts), min_counts_(min_counts), current_range_(VoltageRange::Range2V) {}

    VoltageRange update(uint16_t raw_counts) {
        if (raw_counts >= max_counts_ && current_range_ < VoltageRange::Range1000V) {
            current_range_ = static_cast<VoltageRange>(static_cast<uint8_t>(current_range_) + 1);
        } else if (raw_counts < min_counts_ && current_range_ > VoltageRange::Range200mV) {
            current_range_ = static_cast<VoltageRange>(static_cast<uint8_t>(current_range_) - 1);
        }
        return current_range_;
    }

    VoltageRange getCurrentRange() const { return current_range_; }

private:
    uint16_t max_counts_;
    uint16_t min_counts_;
    VoltageRange current_range_;
};
