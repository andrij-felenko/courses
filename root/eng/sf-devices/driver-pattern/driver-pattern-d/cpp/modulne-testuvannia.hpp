namespace driver::test {

struct MockI2cRegs {
    uint32_t CR1{0};
    uint32_t CR2{0};
    uint32_t DR{0};
    uint32_t SR1{0};
    uint32_t SR2{0};
};

inline void run_mock_test() noexcept {
    MockI2cRegs mock_hardware{};
    I2cConfig cfg{.clock_speed_hz = 100'000, .timeout_ms = 10};
    
    // Передаємо адресу мок-структури як uintptr_t
    I2cDriver driver{reinterpret_cast<std::uintptr_t>(&mock_hardware), cfg};
    auto init_st = driver.init();
    (void)init_st;

    // Симулюємо апаратний NACK
    mock_hardware.SR1 = (1 << 10);
    uint8_t data[2] = {0xAA, 0xBB};
    auto res = driver.master_write(0x3C, data);
    (void)res;
}

} // namespace driver::test
