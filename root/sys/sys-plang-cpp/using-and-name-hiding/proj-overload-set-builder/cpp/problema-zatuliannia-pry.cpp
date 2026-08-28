#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <span>
#include <cstdint>

// Міксин 1: експорт у потік std::ostream через CRTP
template <typename Derived>
struct StreamExportable {
    void export_to(std::ostream& os) const {
        static_cast<const Derived*>(this)->format_stream(os);
    }
};

// Міксин 2: експорт у бінарний вектор байтів
template <typename Derived>
struct BinaryExportable {
    void export_to(std::vector<uint8_t>& buffer) const {
        static_cast<const Derived*>(this)->format_binary(buffer);
    }
};

// Міксин 3: експорт у рядок для швидкого логування
template <typename Derived>
struct TextExportable {
    void export_to(std::string& output) const {
        std::ostringstream ss;
        static_cast<const Derived*>(this)->format_stream(ss);
        output = ss.str();
    }
};

// Цільовий клас доменної сутності
class TelemetryFrame : public StreamExportable<TelemetryFrame>,
                       public BinaryExportable<TelemetryFrame>,
                       public TextExportable<TelemetryFrame> {
private:
    uint64_t timestamp_ns_;
    double temperature_;
    double pressure_;

public:
    TelemetryFrame(uint64_t ts, double temp, double press)
        : timestamp_ns_(ts), temperature_(temp), pressure_(press) {}

    // ОБ'ЄДНАННЯ ПЕРЕВАНТАЖЕНЬ: втягуємо всі export_to з усіх трьох міксинів:
    using StreamExportable<TelemetryFrame>::export_to;
    using BinaryExportable<TelemetryFrame>::export_to;
    using TextExportable<TelemetryFrame>::export_to;

    // Внутрішні методи реалізації, які викликаються міксинами через CRTP:
    void format_stream(std::ostream& os) const {
        os << "[Telemetry] ts=" << timestamp_ns_ 
           << " temp=" << temperature_ << "C press=" << pressure_ << "hPa";
    }

    void format_binary(std::vector<uint8_t>& buffer) const {
        auto append_pod = [&buffer](const auto& val) {
            const uint8_t* ptr = reinterpret_cast<const uint8_t*>(&val);
            buffer.insert(buffer.end(), ptr, ptr + sizeof(val));
        };
        append_pod(timestamp_ns_);
        append_pod(temperature_);
        append_pod(pressure_);
    }
};

int main() {
    TelemetryFrame frame{1718000000000ULL, 23.5, 1013.25};

    // 1. Експорт у консоль через StreamExportable
    std::cout << "1. Потік: ";
    frame.export_to(std::cout);
    std::cout << '\n';

    // 2. Експорт у бінарний вектор через BinaryExportable
    std::vector<uint8_t> bin_data;
    frame.export_to(bin_data);
    std::cout << "2. Бінарний буфер: " << bin_data.size() << " байтів.\n";

    // 3. Експорт у рядок через TextExportable
    std::string text_str;
    frame.export_to(text_str);
    std::cout << "3. Рядок: " << text_str << '\n';

    return 0;
}
