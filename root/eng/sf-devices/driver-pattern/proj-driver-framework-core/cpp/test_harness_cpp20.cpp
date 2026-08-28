/* ============================================================================
 * ФАЙЛ: test_harness_cpp20.cpp - Юніт-тестування драйвера на C++20
 * ============================================================================ */
#include "driver_core_impl.hpp"
#include <iostream>
#include <cassert>

using namespace embed::driver;

class MockHardwareBus {
public:
    void write_data(uint8_t byte) noexcept { last_tx_ = byte; tx_empty_ = true; }
    [[nodiscard]] uint8_t read_data() noexcept { rx_ready_ = false; return mock_rx_; }
    [[nodiscard]] bool is_tx_empty() const noexcept { return tx_empty_; }
    [[nodiscard]] bool is_rx_ready() const noexcept { return rx_ready_; }
    void generate_start() noexcept { start_generated_ = true; tx_empty_ = true; }
    void generate_stop() noexcept { stop_generated_ = true; }
    [[nodiscard]] bool is_nack() const noexcept { return nack_asserted_; }

    uint8_t last_tx_{0};
    uint8_t mock_rx_{0x42};
    bool tx_empty_{true};
    bool rx_ready_{false};
    bool start_generated_{false};
    bool stop_generated_{false};
    bool nack_asserted_{false};
};

int main() {
    std::cout << "=== Запуск тестування C++20 драйвера ===\n";

    MockHardwareBus mock_hw{};
    StaticI2cDriver<MockHardwareBus> driver{mock_hw};

    assert(driver.init() == Status::Ok);

    const std::array<uint8_t, 2> tx_data{0x01, 0x02};
    Transaction t1{
        .dev_addr = 0x48,
        .op_type = OpType::Write,
        .tx_data = tx_data
    };

    assert(driver.submit(t1) == Status::Ok);
    assert(mock_hw.start_generated_);

    // Проганяємо обробку байтів
    driver.poll_isr(); // Відправка першого байта
    driver.poll_isr(); // Відправка другого байта

    auto st = driver.stats();
    assert(st.total_transfers == 1);
    assert(st.successful_transfers == 1);

    std::cout << "✓ Усі тести C++20 драйвера пройдено успішно!\n";
    return 0;
}
