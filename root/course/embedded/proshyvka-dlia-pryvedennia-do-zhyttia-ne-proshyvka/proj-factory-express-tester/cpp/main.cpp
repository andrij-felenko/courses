#include <array>
#include <string_view>
#include <expected>
#include <span>
#include <cstdint>

enum class TestError : uint8_t {
    Timeout,
    BusLocked,
    InvalidId,
    MemoryFault
};

struct TestResult {
    std::string_view name;
    bool passed;
    std::string_view details;
    uint32_t duration_us;
};

/* 1. Безпечний March C- тестер ОЗП з шаблонізацією розміру */
template <size_t WordCount>
class RamTester {
public:
    static constexpr std::expected<void, TestError> run(std::span<uint32_t, WordCount> buffer) noexcept {
        /* Фаза 1: ↕(w0) */
        for (auto& cell : buffer) {
            cell = 0x00000000;
        }

        /* Фаза 2: ⇑(r0, w1) */
        for (auto& cell : buffer) {
            if (cell != 0x00000000) return std::unexpected(TestError::MemoryFault);
            cell = 0xFFFFFFFF;
        }

        /* Фаза 3: ⇑(r1, w0) */
        for (auto& cell : buffer) {
            if (cell != 0xFFFFFFFF) return std::unexpected(TestError::MemoryFault);
            cell = 0x00000000;
        }

        /* Фаза 4: ⇓(r0, w1) */
        for (size_t i = buffer.size(); i > 0; --i) {
            if (buffer[i - 1] != 0x00000000) return std::unexpected(TestError::MemoryFault);
            buffer[i - 1] = 0xFFFFFFFF;
        }

        /* Фаза 5: ⇓(r1, w0) */
        for (size_t i = buffer.size(); i > 0; --i) {
            if (buffer[i - 1] != 0xFFFFFFFF) return std::unexpected(TestError::MemoryFault);
            buffer[i - 1] = 0x00000000;
        }

        /* Фаза 6: ↕(r0) */
        for (const auto& cell : buffer) {
            if (cell != 0x00000000) return std::unexpected(TestError::MemoryFault);
        }

        return {};
    }
};

/* 2. RAII-обгортка для безпечного відновлення та роботи з шиною I2C */
class I2CBusGuard {
public:
    explicit I2CBusGuard() noexcept {
        recover_bus();
    }

    ~I2CBusGuard() noexcept = default;

    [[nodiscard]] std::expected<uint8_t, TestError> read_register(uint8_t dev_addr, uint8_t reg_addr) const noexcept {
        extern bool hal_i2c_read_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t* val, uint32_t timeout);
        uint8_t val = 0;
        if (!hal_i2c_read_reg(dev_addr, reg_addr, &val, 5000)) {
            return std::unexpected(TestError::Timeout);
        }
        return val;
    }

private:
    static void recover_bus() noexcept {
        extern void gpio_set_i2c_mode_gpio();
        extern void gpio_set_i2c_scl(bool level);
        extern void gpio_set_i2c_sda(bool level);
        extern bool gpio_get_i2c_sda();
        extern void gpio_set_i2c_mode_peripheral();

        gpio_set_i2c_mode_gpio();
        gpio_set_i2c_sda(true);

        for (int i = 0; i < 9; ++i) {
            gpio_set_i2c_scl(false);
            for (volatile int d = 0; d < 20; ++d);
            gpio_set_i2c_scl(true);
            for (volatile int d = 0; d < 20; ++d);
            if (gpio_get_i2c_sda()) break;
        }

        gpio_set_i2c_scl(false);
        gpio_set_i2c_sda(false);
        for (volatile int d = 0; d < 20; ++d);
        gpio_set_i2c_scl(true);
        for (volatile int d = 0; d < 20; ++d);
        gpio_set_i2c_sda(true);

        gpio_set_i2c_mode_peripheral();
    }
};

/* 3. Модуль верифікації Flash-пам'яті */
struct JedecId {
    uint8_t manufacturer;
    uint8_t memory_type;
    uint8_t capacity;
};

class SpiFlashProbe {
public:
    [[nodiscard]] static std::expected<JedecId, TestError> read_jedec_id() noexcept {
        extern void hal_spi_cs_select(bool active);
        extern void hal_spi_transfer(const uint8_t* tx, uint8_t* rx, size_t len);

        const std::array<uint8_t, 4> tx_buf = {0x9F, 0x00, 0x00, 0x00};
        std::array<uint8_t, 4> rx_buf = {0};

        hal_spi_cs_select(true);
        hal_spi_transfer(tx_buf.data(), rx_buf.data(), tx_buf.size());
        hal_spi_cs_select(false);

        if (rx_buf[1] == 0x00 || rx_buf[1] == 0xFF) {
            return std::unexpected(TestError::BusLocked);
        }

        return JedecId{rx_buf[1], rx_buf[2], rx_buf[3]};
    }
};

/* Каркас Test Runner на основі статичних дескрипторів */
class TestRunner {
public:
    static void execute_suite() noexcept {
        extern void uart_send_string(const char* str);
        extern uint32_t timer_get_us();

        bool overall_pass = true;

        // 1. RAM Test
        std::array<uint32_t, 256> ram_buf{};
        auto ram_res = RamTester<256>::run(ram_buf);
        if (!ram_res) overall_pass = false;

        // 2. I2C Tests
        I2CBusGuard i2c_guard;
        auto imu_res = i2c_guard.read_register(0x68, 0x75);
        if (!imu_res || *imu_res != 0x47) overall_pass = false;

        auto baro_res = i2c_guard.read_register(0x77, 0x00);
        if (!baro_res || *baro_res != 0x60) overall_pass = false;

        // 3. SPI Flash Test
        auto flash_res = SpiFlashProbe::read_jedec_id();
        if (!flash_res || flash_res->manufacturer != 0xEF || flash_res->capacity != 0x18) {
            overall_pass = false;
        }

        if (overall_pass) {
            uart_send_string("{\"status\":\"PASS\",\"details\":\"All peripherals verified\"}\r\n");
        } else {
            uart_send_string("{\"status\":\"FAIL\",\"details\":\"Hardware verification error\"}\r\n");
        }
    }
};
