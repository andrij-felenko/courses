struct HardwareFrame {
    std::uint32_t packet_id;
    std::uint16_t payload_crc;
    double timestamp;

    HardwareFrame(std::uint32_t id, std::uint16_t crc, double ts)
        : packet_id(id), payload_crc(crc), timestamp(ts) {}

    // operator<< свідомо ВІДСУТНІЙ!
};
