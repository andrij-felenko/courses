// Консольна реалізація інтерфейсу протоколювання
class StdoutLogger final : public ILogger {
public:
    void log_info(std::string_view message) override {
        std::cout << "[INFO] " << message << "\n";
    }
    void log_error(std::string_view message) override {
        std::cerr << "[ERROR] " << message << "\n";
    }
};

int main() {
    StdoutLogger logger_instance;
    gsl::not_null<ILogger*> logger = &logger_instance;

    std::cout << "--- Сценарій 1: Обробка коректного повного кадру ---\n";
    // Пакет: "TELM" (4B) + SensorID(1) (2B) + PayloadLen(16B) (2B) + Time(0x1000) (4B) + 2x double + CRC(4B)
    std::vector<uint8_t> packet_buffer = {
        'T', 'E', 'L', 'M',
        0x01, 0x00,
        0x10, 0x00,
        0x00, 0x10, 0x00, 0x00
    };

    double temperature = 36.6;
    double pressure = 101.3;
    const uint8_t* p_temp = reinterpret_cast<const uint8_t*>(&temperature);
    const uint8_t* p_press = reinterpret_cast<const uint8_t*>(&pressure);

    packet_buffer.insert(packet_buffer.end(), p_temp, p_temp + sizeof(double));
    packet_buffer.insert(packet_buffer.end(), p_press, p_press + sizeof(double));

    // Додаємо 4 байти контрольної суми CRC32
    uint32_t dummy_crc = 0xDEADBEEF;
    const uint8_t* p_crc = reinterpret_cast<const uint8_t*>(&dummy_crc);
    packet_buffer.insert(packet_buffer.end(), p_crc, p_crc + sizeof(uint32_t));

    // Створюємо безпечний gsl::span
    auto valid_span = gsl::as_bytes(gsl::make_span(packet_buffer));
    auto decode_result = SafeTelemetryDecoder::decode_packet(valid_span, logger);

    assert(decode_result.has_value());
    assert(decode_result->sensor_id == 1);
    assert(decode_result->readings.size() == 2);
    std::cout << "Отримані вимірювання: Temp = " << decode_result->readings[0] 
              << ", Pressure = " << decode_result->readings[1] << "\n\n";

    std::cout << "--- Сценарій 2: Атака переповнення (Malicious Length Overflow) ---\n";
    // Зловмисник підробляє розмір payload: 0xFFFF (65535 байтів) при реальному буфері 36 байтів
    std::vector<uint8_t> overflow_packet = packet_buffer;
    overflow_packet[6] = 0xFF;
    overflow_packet[7] = 0xFF;

    auto overflow_span = gsl::as_bytes(gsl::make_span(overflow_packet));
    auto overflow_result = SafeTelemetryDecoder::decode_packet(overflow_span, logger);
    assert(!overflow_result.has_value());
    std::cout << "Атаку успішно відхилено без читання за межами пам'яті.\n\n";

    std::cout << "--- Сценарій 3: Атака усіченого пакета (Truncated Header) ---\n";
    // Передаємо лише перші 6 байтів кадру
    auto truncated_span = valid_span.first(6);
    auto truncated_result = SafeTelemetryDecoder::decode_packet(truncated_span, logger);
    assert(!truncated_result.has_value());
    std::cout << "Усічений пакет коректно відхилено перевіркою мінімального розміру.\n\n";

    std::cout << "--- Сценарій 4: Статичний захист від передачі nullptr ---\n";
    // Наступний виклик буде заблоковано компілятором:
    // SafeTelemetryDecoder::decode_packet(valid_span, nullptr); // ПОМИЛКА КОМПІЛЯЦІЇ: call to deleted constructor

    std::cout << "Усі тести валідації безпеки GSL виконано успішно.\n";
    return 0;
}
