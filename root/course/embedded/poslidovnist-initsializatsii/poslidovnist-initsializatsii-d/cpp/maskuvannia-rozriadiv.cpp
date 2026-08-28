#include <cstdint>
#include <expected>

struct RegVerifyEntry {
    uint8_t reg_addr;
    uint8_t target_val;
    uint8_t care_mask; // Маска лише R/W бітів конфігурації
};

enum class VerifyError {
    WriteFailed,
    ReadFailed,
    Mismatch
};

class RegisterVerifier {
public:
    std::expected<void, VerifyError> write_and_verify(uint8_t dev_addr, const RegVerifyEntry &entry) {
        // 1. Записуємо значення по шині
        if (!i2c_write_reg(dev_addr, entry.reg_addr, entry.target_val)) {
            return std::unexpected(VerifyError::WriteFailed);
        }

        // 2. Зчитуємо значення назад із мікросхеми
        uint8_t read_val = 0;
        if (!i2c_read_reg(dev_addr, entry.reg_addr, read_val)) {
            return std::unexpected(VerifyError::ReadFailed);
        }

        // 3. Порівнюємо значення ТІЛЬКИ у значущих бітах
        const uint8_t target_masked = entry.target_val & entry.care_mask;
        const uint8_t read_masked = read_val & entry.care_mask;

        if (target_masked != read_masked) {
            return std::unexpected(VerifyError::Mismatch);
        }

        return {}; // Верифікація успішна
    }

private:
    bool i2c_write_reg(uint8_t addr, uint8_t reg, uint8_t val);
    bool i2c_read_reg(uint8_t addr, uint8_t reg, uint8_t &val);
};
