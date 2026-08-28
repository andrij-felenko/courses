#include <cstdint>
#include <span>

/* Безпечний підхід: буфер передається ззовні або належить структурі адаптера */
class SensorFrameParser {
public:
    int8_t parse_data(struct VendorSensorDev* dev, std::span<uint8_t> buffer) {
        if (buffer.size() < 1024) return -1;
        return dev->read(0x00, buffer.data(), static_cast<uint32_t>(buffer.size()), dev->intf_ptr);
    }
};
