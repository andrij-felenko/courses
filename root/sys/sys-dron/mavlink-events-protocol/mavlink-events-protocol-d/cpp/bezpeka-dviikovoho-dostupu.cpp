#include <cstdint>
#include <cstring>
#include <span>
#include <bit>

// Безпечне пакування аргументів події в буфер за допомогою std::span (C++20)
void pack_event_args(std::span<uint8_t> dest_buf, uint8_t sensor_id, float deviation) noexcept {
    if (dest_buf.size() >= sizeof(uint8_t) + sizeof(float)) {
        dest_buf[0] = sensor_id;
        std::memcpy(dest_buf.data() + 1, &deviation, sizeof(float));
    }
}

// Безпечне розпакування аргументів із двійкового буфера
struct CompassCalArgs {
    uint8_t sensor_id{0};
    float   deviation{0.0f};
};

CompassCalArgs unpack_event_args(std::span<const uint8_t> src_buf) noexcept {
    CompassCalArgs args{};
    if (src_buf.size() >= sizeof(uint8_t) + sizeof(float)) {
        args.sensor_id = src_buf[0];
        std::memcpy(&args.deviation, src_buf.data() + 1, sizeof(float));
    }
    return args;
}
