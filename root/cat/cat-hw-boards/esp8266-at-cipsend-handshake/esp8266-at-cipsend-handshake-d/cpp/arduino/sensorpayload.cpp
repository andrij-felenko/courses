struct SensorPayload {
    uint16_t sensor_id;
    float temperature;
    uint8_t flags;
} __attribute__((packed));

void demonstrateBinaryHazard(const SensorPayload& data) {
    const uint8_t* rawBytes = reinterpret_cast<const uint8_t*>(&data);
    size_t size = sizeof(SensorPayload);

    for (size_t i = 0; i < size - 1; i++) {
        if (rawBytes[i] == 0x0D && rawBytes[i + 1] == 0x0A) {
            Serial.print(F("[ЗБОЙ PARSER] Хибний термінатор CRLF на зсуві: "));
            Serial.println(i);
            return;
        }
    }
}
