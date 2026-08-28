#include <gsl/gsl>
#include <cstdint>
#include <vector>
#include <string_view>
#include <iostream>
#include <iomanip>
#include <stdexcept>
#include <optional>
#include <cstring>
#include <cassert>

// Абстрактний інтерфейс системи протоколювання подій
class ILogger {
public:
    virtual ~ILogger() = default;
    virtual void log_info(std::string_view message) = 0;
    virtual void log_error(std::string_view message) = 0;
};

// Типобезпечна модель результату декодування телеметрії
struct SafeTelemetryRecord {
    uint16_t            sensor_id{};
    uint32_t            timestamp{};
    std::vector<double> readings{};
};

// Клас високопродуктивного та безпечного декодера телеметричних пакетів
class SafeTelemetryDecoder {
public:
    // Константи протоколу
    static constexpr uint32_t MAGIC_MARKER = 0x54454C4D; // ASCII "TELM"
    static constexpr std::ptrdiff_t HEADER_BYTE_SIZE = 12;
    static constexpr std::ptrdiff_t CHECKSUM_BYTE_SIZE = 4;

    // Головний метод розбору пакета
    [[nodiscard]] static std::optional<SafeTelemetryRecord> decode_packet(
        gsl::span<const gsl::byte> buffer,
        gsl::not_null<ILogger*> logger) noexcept
    {
        // 1. Охоронець області видимості: фіксація завершення аналізу кадру
        auto session_guard = gsl::finally([logger] {
            logger->log_info("Діагностика: завершено цикл оброблення мережевого кадру.");
        });

        // 2. Перевірка мінімально необхідного розміру заголовка та контрольної суми
        const std::ptrdiff_t min_packet_size = HEADER_BYTE_SIZE + CHECKSUM_BYTE_SIZE;
        if (buffer.size() < min_packet_size) {
            logger->log_error("Помилка: буфер менший за мінімальний розмір заголовка протоколу.");
            return std::nullopt;
        }

        // 3. Безпечне зчитування магічного маркера без порушення Strict Aliasing
        uint32_t magic_val = 0;
        auto magic_slice = buffer.first<4>();
        std::memcpy(&magic_val, magic_slice.data(), sizeof(magic_val));

        if (magic_val != MAGIC_MARKER) {
            logger->log_error("Помилка: невалідний магічний маркер початку кадру (Invalid Magic).");
            return std::nullopt;
        }

        // 4. Вилучення полів заголовка за допомогою типізованих зрізів subspan
        uint16_t raw_sensor_id = 0;
        std::memcpy(&raw_sensor_id, buffer.subspan<4, 2>().data(), sizeof(raw_sensor_id));

        uint16_t raw_payload_len = 0;
        std::memcpy(&raw_payload_len, buffer.subspan<6, 2>().data(), sizeof(raw_payload_len));

        uint32_t raw_timestamp = 0;
        std::memcpy(&raw_timestamp, buffer.subspan<8, 4>().data(), sizeof(raw_timestamp));

        // 5. Контроль звуження числових типів та верифікація меж корисного навантаження
        const std::ptrdiff_t payload_length = gsl::narrow_cast<std::ptrdiff_t>(raw_payload_len);
        const std::ptrdiff_t full_expected_packet_size = HEADER_BYTE_SIZE + payload_length + CHECKSUM_BYTE_SIZE;

        if (buffer.size() < full_expected_packet_size) {
            logger->log_error("Помилка: заявлена довжина навантаження перевищує фізичний розмір пакета.");
            return std::nullopt;
        }

        // 6. Формування вихідного запису та копіювання даних вимірювань
        SafeTelemetryRecord record;
        record.sensor_id = raw_sensor_id;
        record.timestamp = raw_timestamp;

        // Зріз виключно корисного навантаження
        auto payload_slice = buffer.subspan(HEADER_BYTE_SIZE, payload_length);
        const std::ptrdiff_t element_size = gsl::narrow<std::ptrdiff_t>(sizeof(double));
        const std::ptrdiff_t element_count = payload_slice.size() / element_size;

        if (element_count > 0) {
            record.readings.resize(gsl::narrow<std::size_t>(element_count));
            std::memcpy(record.readings.data(), 
                        payload_slice.data(), 
                        gsl::narrow<std::size_t>(element_count * element_size));
        }

        logger->log_info("Успіх: телеметричний кадр валідовано та успішно декодовано.");
        return record;
    }
};
