void telemetry_example_cpp() {
    std::array<uint8_t, 64> buffer{};
    cbor::Writer writer(buffer);

    // Серіалізація словника
    cbor::Encoder::write_map_header(writer, 3).value();
    cbor::Encoder::write_uint(writer, 1).value();
    cbor::Encoder::write_uint(writer, 1714560000ULL).value();

    cbor::Encoder::write_uint(writer, 2).value();
    cbor::Encoder::write_text(writer, "DHT22").value();

    cbor::Encoder::write_uint(writer, 3).value();
    cbor::Encoder::write_bool(writer, true).value();

    // Десеріалізація через Zero-Copy Decoder
    cbor::Reader reader(writer.written_data());
    auto root = cbor::Decoder::read_next(reader);

    if (root && std::holds_alternative<cbor::MapHeader>(*root)) {
        const size_t pairs = std::get<cbor::MapHeader>(*root).pairs_count;
        for (size_t i = 0; i < pairs; ++i) {
            auto key = cbor::Decoder::read_next(reader);
            auto val = cbor::Decoder::read_next(reader);

            if (key && std::holds_alternative<uint64_t>(*key) && std::get<uint64_t>(*key) == 2) {
                if (val && std::holds_alternative<std::string_view>(*val)) {
                    std::string_view name = std::get<std::string_view>(*val);
                    (void)name; // name посилається прямо на пам'ять buffer
                }
            }
        }
    }
}
