// 1. Проста апаратна структура (тривіально копійовна)
struct SensorReading {
    std::uint32_t sensor_id;
    double temperature;
    double pressure;

    bool operator==(const SensorReading&) const = default;
};
static_assert(TriviallySerializable<SensorReading>);

// 2. Комплексний пакет телеметрії
struct TelemetryPacket {
    std::uint64_t timestamp_ns;
    std::string device_name;
    SensorReading primary_sensor;
    std::vector<SensorReading> auxiliary_sensors;

    // Власний метод серіалізації
    template<ByteStream S>
    void serialize(S& stream) const {
        BinarySerializer::serialize(stream, timestamp_ns);
        BinarySerializer::serialize(stream, device_name);
        BinarySerializer::serialize(stream, primary_sensor);
        BinarySerializer::serialize(stream, auxiliary_sensors);
    }

    // Власний метод десеріалізації
    template<ByteSource S>
    void deserialize(S& source) {
        BinaryDeserializer::deserialize(source, timestamp_ns);
        BinaryDeserializer::deserialize(source, device_name);
        BinaryDeserializer::deserialize(source, primary_sensor);
        BinaryDeserializer::deserialize(source, auxiliary_sensors);
    }

    bool operator==(const TelemetryPacket&) const = default;
};
static_assert(CustomSerializable<TelemetryPacket, MemoryBufferStream>);
static_assert(CustomDeserializable<TelemetryPacket, MemoryBufferStream>);

int main() {
    MemoryBufferStream stream;

    TelemetryPacket original_packet{
        .timestamp_ns = 1718900000123456789ULL,
        .device_name = "EdgeNode-Alpha-01",
        .primary_sensor = SensorReading{
            .sensor_id = 101,
            .temperature = 23.85,
            .pressure = 1013.25
        },
        .auxiliary_sensors = {
            SensorReading{.sensor_id = 102, .temperature = 24.10, .pressure = 1013.10},
            SensorReading{.sensor_id = 103, .temperature = 23.95, .pressure = 1013.20}
        }
    };

    // 1. Серіалізація (вектор auxiliary_sensors записується одним викликом через TriviallyContiguousRange)
    BinarySerializer::serialize(stream, original_packet);
    std::cout << "Серіалізація успішна! Записано байтів: " << stream.size() << "\n";

    // 2. Десеріалізація
    TelemetryPacket restored_packet{};
    BinaryDeserializer::deserialize(stream, restored_packet);

    // 3. Перевірка тотожності
    if (original_packet == restored_packet) {
        std::cout << "Пакет успішно відновлено без втрати даних!\n";
        std::cout << "Пристрій: " << restored_packet.device_name << "\n";
        std::cout << "Кількість допоміжних сенсорів: " 
                  << restored_packet.auxiliary_sensors.size() << "\n";
    }

    return 0;
}
