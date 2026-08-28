void parse_network_frame(std::span<const uint8_t> frame) {
    if (frame.size() < 30) return; // Захист від некоректного розміру пакета

    // 1. Перші 4 байти — заголовок
    std::span<const uint8_t> header = frame.first(4);

    // 2. Наступні 24 байти — корисні дані (payload)
    std::span<const uint8_t> payload = frame.subspan(4, 24);

    // 3. Останні 2 байти — контрольна сума
    std::span<const uint8_t> checksum = frame.last(2);
}
