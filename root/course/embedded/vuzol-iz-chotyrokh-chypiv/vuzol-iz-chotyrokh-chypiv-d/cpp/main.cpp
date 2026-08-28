#pragma pack(push, 1)
struct TelemetryRecord {
    uint32_t timestamp{0};     // 4 байти: секунди Unix Epoch від DS3231
    int32_t  temperature{0};   // 4 байти: соті частки °C (23.45°C -> 2345)
    uint32_t pressure{0};      // 4 байти: соті частки Паскаля
    uint32_t humidity{0};      // 4 байти: вологість у форматі Q22.10
    uint16_t sequenceId{0};    // 2 байти: монотонний лічильник зрізів
    uint16_t statusFlags{0};   // 2 байти: бітові прапорці стану
    uint16_t crc16{0};         // 2 байти: контрольна сума CRC-16 Modbus
};
#pragma pack(pop)
