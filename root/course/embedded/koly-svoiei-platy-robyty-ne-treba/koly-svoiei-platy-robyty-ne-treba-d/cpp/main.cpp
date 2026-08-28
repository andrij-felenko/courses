// Ідіоматичний еквівалент на C++20: RAII-обгортка, безпека винятків та типізація
#include <iostream>
#include <memory>
#include <vector>
#include <expected>
#include <string_view>
#include <format>
#include <span>
#include <cstdint>
#include <modbus/modbus.h>

class ModbusClient {
public:
    struct SensorTelemetry {
        float pressure_bar;
        float temp_celsius;
    };

    enum class Error {
        ConnectionFailed,
        ReadFailed,
        InvalidContext
    };

    explicit ModbusClient(std::string_view port, int baudrate, int slave_id) {
        modbus_t* raw_ctx = modbus_new_rtu(port.data(), baudrate, 'N', 8, 1);
        if (!raw_ctx) {
            return;
        }
        ctx_.reset(raw_ctx);
        modbus_set_slave(ctx_.get(), slave_id);
        modbus_set_response_timeout(ctx_.get(), 0, 500000); // 500 мс
    }

    std::expected<SensorTelemetry, Error> read_telemetry(uint16_t start_reg) noexcept {
        if (!ctx_) {
            return std::unexpected(Error::InvalidContext);
        }

        if (modbus_connect(ctx_.get()) == -1) {
            return std::unexpected(Error::ConnectionFailed);
        }

        std::array<uint16_t, 4> raw_data{};
        int rc = modbus_read_input_registers(ctx_.get(), start_reg, 
                                             static_cast<int>(raw_data.size()), 
                                             raw_data.data());
        if (rc == -1) {
            return std::unexpected(Error::ReadFailed);
        }

        return SensorTelemetry{
            .pressure_bar = static_cast<float>(raw_data[0]) * 0.01f,
            .temp_celsius = static_cast<float>(static_cast<int16_t>(raw_data[1])) * 0.1f
        };
    }

private:
    struct ModbusDeleter {
        void operator()(modbus_t* ptr) const noexcept {
            if (ptr) {
                modbus_close(ptr);
                modbus_free(ptr);
            }
        }
    };
    std::unique_ptr<modbus_t, ModbusDeleter> ctx_;
};

int main() {
    ModbusClient client("/dev/ttyUSB0", 115200, 1);

    auto result = client.read_telemetry(0x0100);
    if (!result) {
        std::cerr << "Помилка зчитування COTS-телеметрії\n";
        return 1;
    }

    const auto& [pressure, temp] = *result;
    std::cout << std::format("Дані COTS: Тиск = {:.2f} бар, Температура = {:.1f} °C\n", 
                             pressure, temp);
    return 0;
}
