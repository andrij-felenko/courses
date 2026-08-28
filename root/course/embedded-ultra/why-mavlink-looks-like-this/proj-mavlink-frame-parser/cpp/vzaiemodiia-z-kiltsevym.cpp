// Обробка потоку з кільцевого буфера на C++
void process_telemetry_loop(FrameParser& parser, UartRingBuffer& ring) noexcept {
    uint8_t byte{0};
    while (ring.pop(byte)) {
        const uint8_t crc_extra = get_crc_extra(parser.current_msg_id());
        if (auto frame = parser.parse_byte(byte, crc_extra)) {
            handle_message(*frame);
        }
    }
}
