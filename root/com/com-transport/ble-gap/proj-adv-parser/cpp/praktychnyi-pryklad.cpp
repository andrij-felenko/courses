#include <iostream>
#include <iomanip>
#include <string>

struct SensorData {
    std::string device_name;
    double      temperature_celsius{0.0};
    uint8_t     humidity_pct{0};
    uint8_t     battery_pct{0};
    bool        valid_telemetry{false};
};

class SensorAdDecoder {
public:
    static std::optional<SensorData> decode(std::span<const uint8_t> raw_payload) {
        SensorData result;

        BleAdParser::for_each(raw_payload, [&result](const BleAdElement& elem) {
            if (elem.type == BleAdType::CompleteLocalName) {
                std::string raw_name = std::string(elem.as_string_view());
                // Санітизація недрукованих символів
                for (char& c : raw_name) {
                    if (static_cast<unsigned char>(c) < 0x20) {
                        c = ' ';
                    }
                }
                result.device_name = std::move(raw_name);
            } 
            else if (elem.type == BleAdType::ManufacturerSpecific) {
                // Перевіряємо довжину: 2 байти Company ID + 4 байти корисних даних
                if (elem.data.size() >= 6) {
                    const uint16_t company_id = static_cast<uint16_t>(elem.data[0]) |
                                               (static_cast<uint16_t>(elem.data[1]) << 8);

                    if (company_id == 0x02E5) { // Espressif Systems
                        const int16_t raw_temp = static_cast<int16_t>(
                            static_cast<uint16_t>(elem.data[2]) |
                            (static_cast<uint16_t>(elem.data[3]) << 8)
                        );

                        result.temperature_celsius = raw_temp / 100.0;
                        result.humidity_pct        = elem.data[4];
                        result.battery_pct         = elem.data[5];
                        result.valid_telemetry     = true;
                    }
                }
            }
            return true; // Продовжуємо парсинг
        });

        if (result.device_name.empty() && !result.valid_telemetry) {
            return std::nullopt;
        }

        return result;
    }
};
