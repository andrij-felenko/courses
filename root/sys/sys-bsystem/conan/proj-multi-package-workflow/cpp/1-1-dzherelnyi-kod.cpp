#include "telemetry/telemetry.hpp"

#include <cstring>
#include <stdexcept>

namespace telemetry {

PacketEncoder::PacketEncoder(std::string_view channel_name)
    : channel_name_(channel_name) {
    if (channel_name_.empty()) {
        throw std::invalid_argument("Назва каналу телеметрії не може бути порожньою");
    }
}

std::string_view PacketEncoder::channel_name() const noexcept {
    return channel_name_;
}

std::vector<uint8_t> PacketEncoder::encode(std::span<const SensorRecord> records) const {
    const uint32_t record_count = static_cast<uint32_t>(records.size());
    const uint32_t name_len = static_cast<uint32_t>(channel_name_.size());
    
    // Розрахунок точного розміру буфера без проміжних алокацій
    const size_t total_size = sizeof(uint32_t) + name_len + 
                              sizeof(uint32_t) + (records.size() * sizeof(SensorRecord));
    
    std::vector<uint8_t> buffer(total_size);
    uint8_t* ptr = buffer.data();

    // Запис префікса назви каналу
    std::memcpy(ptr, &name_len, sizeof(name_len));
    ptr += sizeof(name_len);
    std::memcpy(ptr, channel_name_.data(), name_len);
    ptr += name_len;

    // Запис кількості записів та бінарного масиву
    std::memcpy(ptr, &record_count, sizeof(record_count));
    ptr += sizeof(record_count);

    if (!records.empty()) {
        const size_t payload_bytes = records.size_bytes();
        std::memcpy(ptr, records.data(), payload_bytes);
    }

    return buffer;
}

} // namespace telemetry
