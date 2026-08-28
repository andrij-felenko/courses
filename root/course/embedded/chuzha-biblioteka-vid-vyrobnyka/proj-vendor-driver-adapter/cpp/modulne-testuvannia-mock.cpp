#include <array>
#include <cassert>

class MockI2cBus : public II2cBus {
public:
    std::array<uint8_t, 256> registers{};
    bool fail_transactions{false};
    size_t transactions_count{0};

    bool read_registers(uint8_t dev_addr, uint8_t reg, std::span<uint8_t> buffer) override {
        (void)dev_addr;
        if (fail_transactions) return false;
        for (size_t i = 0; i < buffer.size(); ++i) {
            buffer[i] = registers[(reg + i) & 0xFF];
        }
        transactions_count++;
        return true;
    }

    bool write_registers(uint8_t dev_addr, uint8_t reg, std::span<const uint8_t> buffer) override {
        (void)dev_addr;
        if (fail_transactions) return false;
        for (size_t i = 0; i < buffer.size(); ++i) {
            registers[(reg + i) & 0xFF] = buffer[i];
        }
        transactions_count++;
        return true;
    }
};

void run_cpp_adapter_tests() {
    MockI2cBus mock;
    mock.registers[0xD0] = 0x60; // Валідний Chip ID

    // Запис сирих тестових даних відліків
    mock.registers[0xF7] = 0x50;
    mock.registers[0xF8] = 0x00;
    mock.registers[0xF9] = 0x00;
    mock.registers[0xFA] = 0x60;
    mock.registers[0xFB] = 0x00;
    mock.registers[0xFC] = 0x00;

    SensorAdapter adapter(mock, 0x76);

    // Тест 1: Ініціалізація
    auto init_res = adapter.init();
    assert(init_res.has_value());

    // Тест 2: Зчитування відліку
    auto sample_res = adapter.read_sample();
    assert(sample_res.has_value());
    assert(sample_res->temperature_celsius > 0.0f);

    // Тест 3: Fault Injection — відмова зв'язку в процесі вимірювання
    mock.fail_transactions = true;
    auto failed_sample = adapter.read_sample();
    assert(!failed_sample.has_value());
    assert(failed_sample.error() == SensorStatus::CommunicationError);
}
