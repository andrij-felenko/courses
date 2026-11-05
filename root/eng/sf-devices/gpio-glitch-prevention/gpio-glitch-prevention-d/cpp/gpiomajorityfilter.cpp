#include <cstdint>

class GpioMajorityFilter {
public:
    explicit GpioMajorityFilter(bool initial_state = false)
        : history_(initial_state ? 0xFF : 0x00), debounced_state_(initial_state) {}

    // Оновлення стану фільтра під час кожного відліку таймера
    bool update(bool raw_pin_state) {
        history_ = static_cast<uint8_t>((history_ << 1) | (raw_pin_state ? 1 : 0));
        
        uint8_t ones_count = 0;
        for (uint8_t i = 0; i < 8; ++i) {
            if ((history_ >> i) & 0x01) {
                ones_count++;
            }
        }

        if (ones_count >= 6) {
            debounced_state_ = true;
        } else if (ones_count <= 2) {
            debounced_state_ = false;
        }

        return debounced_state_;
    }

    [[nodiscard]] bool state() const { return debounced_state_; }

private:
    uint8_t history_{0x00};
    bool debounced_state_{false};
};
