#include <iostream>
#include <vector>

namespace {

#pragma pack(push, 1)
struct TelemetryPayload {
    float    battery_voltage{0.0f};
    float    motor_current{0.0f};
    int16_t  temperature_c{0};
};
#pragma pack(pop)

// Формування кадру у вихідний вектор
std::vector<uint8_t> build_tx_frame(
    uint8_t msg_id, 
    uint8_t seq, 
    std::span<const uint8_t> payload) 
{
    std::array<uint8_t, protocol::MaxPacketSize> raw_buf{};
    protocol::FrameHeader hdr{
        .msg_id = msg_id,
        .seq_num = seq,
        .payload_len = static_cast<uint16_t>(payload.size())
    };

    std::memcpy(raw_buf.data(), &hdr, sizeof(protocol::FrameHeader));
    std::memcpy(raw_buf.data() + sizeof(protocol::FrameHeader), payload.data(), payload.size());

    size_t raw_len = sizeof(protocol::FrameHeader) + payload.size();
    uint16_t crc = protocol::crc16_calculate(
        std::span<const uint8_t>(raw_buf.data(), raw_len)
    );

    raw_buf[raw_len++] = static_cast<uint8_t>(crc & 0xFF);
    raw_buf[raw_len++] = static_cast<uint8_t>((crc >> 8) & 0xFF);

    std::vector<uint8_t> wire(raw_len + (raw_len / 254) + 2);
    auto enc_res = protocol::cobs_encode(
        std::span<const uint8_t>(raw_buf.data(), raw_len),
        std::span<uint8_t>(wire.data(), wire.size())
    );

    if (!enc_res) return {};
    wire.resize(*enc_res);
    wire.push_back(0x00); // Додаємо кінцевий розділювач
    return wire;
}

} // namespace

int main() {
    protocol::PacketParser parser([](const protocol::FrameHeader& hdr, std::span<const uint8_t> payload) {
        if (hdr.msg_id == 0x01 && payload.size() == sizeof(TelemetryPayload)) {
            TelemetryPayload telem{};
            std::memcpy(&telem, payload.data(), sizeof(TelemetryPayload));
            std::cout << "<- [RX OK] Seq=" << static_cast<int>(hdr.seq_num)
                      << ": V=" << telem.battery_voltage 
                      << "V, I=" << telem.motor_current 
                      << "A, T=" << telem.temperature_c << " C\n";
        }
    });

    TelemetryPayload telem_out{14.85f, 2.34f, 42};
    std::span<const uint8_t> payload_span(
        reinterpret_cast<const uint8_t*>(&telem_out), 
        sizeof(TelemetryPayload)
    );

    auto wire_frame = build_tx_frame(0x01, 42, payload_span);
    std::cout << "-> [TX] Сформовано кадр довжиною " << wire_frame.size() << " байтів.\n";

    // Симуляція завади та брязкоту на лінії
    std::array<uint8_t, 6> noise{ 0xFF, 0x55, 0xAA, 0x00, 0x12, 0x00 };
    parser.feed_span(noise);

    // Передача корисного кадру
    parser.feed_span(wire_frame);

    std::cout << "Підсумок парсера: прийнято=" << parser.frames_received()
              << ", помилок CRC=" << parser.crc_errors()
              << ", переповнень=" << parser.overflow_errors() << "\n";

    return 0;
}
