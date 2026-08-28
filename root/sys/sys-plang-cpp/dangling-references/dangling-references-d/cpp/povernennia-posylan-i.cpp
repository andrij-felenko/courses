struct DataPacket {
    int header;
    double payload[8];
};

const DataPacket& parse_packet(const char* raw_bytes) {
    DataPacket packet;
    packet.header = static_cast<int>(raw_bytes[0]);
    // Заповнення пакету...
    return packet; // Помилка: повернення посилання на локальну змінну!
}
