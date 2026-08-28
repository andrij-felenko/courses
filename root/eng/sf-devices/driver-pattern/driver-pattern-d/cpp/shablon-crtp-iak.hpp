#include <cstdint>
#include <span>

namespace driver {

template <typename Derived>
class PacketDriverBase {
public:
    Status send_with_checksum(std::span<const uint8_t> payload) noexcept {
        uint8_t crc = calculate_crc(payload);
        // Статичне приведення this до похідного класу без virtual
        return static_cast<Derived*>(this)->send_raw_packet(payload, crc);
    }

private:
    uint8_t calculate_crc(std::span<const uint8_t> data) noexcept {
        uint8_t sum = 0;
        for (auto b : data) sum ^= b;
        return sum;
    }
};

class SpiPacketDriver : public PacketDriverBase<SpiPacketDriver> {
public:
    Status send_raw_packet(std::span<const uint8_t> data, uint8_t crc) noexcept {
        (void)data; (void)crc;
        return Status::Ok;
    }
};

} // namespace driver
