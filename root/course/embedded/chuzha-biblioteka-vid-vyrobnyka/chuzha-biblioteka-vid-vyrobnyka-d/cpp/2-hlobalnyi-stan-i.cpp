#include <cstdint>
#include <array>

/* Безпечний підхід: стан інкапсульовано всередині екземпляра класу */
class SafeSensorDevice {
public:
    void set_mode(uint8_t mode) {
        operating_mode_ = mode;
        tx_buffer_[0] = 0xF4;
        tx_buffer_[1] = operating_mode_;
        // Відправка через контекст конкретного екземпляра
    }

private:
    uint8_t operating_mode_{0};
    std::array<uint8_t, 64> tx_buffer_{};
};
