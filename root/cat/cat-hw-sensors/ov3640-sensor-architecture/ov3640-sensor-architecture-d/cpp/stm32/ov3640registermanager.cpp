#include <cstdint>
#include <cstddef>
#include <array>

class Ov3640RegisterManager {
public:
    struct RegisterConfig {
        uint8_t bank;
        uint8_t reg;
        uint8_t val;
    };

    using WriteFn = bool (*)(uint8_t reg, uint8_t val);
    using DelayFn = void (*)(uint32_t ms);

    explicit Ov3640RegisterManager(WriteFn write_fn, DelayFn delay_fn)
        : m_write(write_fn), m_delay(delay_fn), m_active_bank(0xFF) {}

    bool selectBank(uint8_t bank) {
        if (m_active_bank == bank) {
            return true; // Пропуск зайвого виклику шини SCCB
        }
        if (m_write(0xFF, bank)) {
            m_active_bank = bank;
            return true;
        }
        return false;
    }

    bool writeRegister(uint8_t bank, uint8_t reg, uint8_t val) {
        if (!selectBank(bank)) {
            return false;
        }
        return m_write(reg, val);
    }

    template <size_t N>
    bool loadConfigurationTable(const std::array<RegisterConfig, N>& table) {
        for (const auto& entry : table) {
            if (entry.reg == 0xFF && entry.bank == 0xFF) {
                m_delay(entry.val);
                continue;
            }
            if (!writeRegister(entry.bank, entry.reg, entry.val)) {
                return false;
            }
        }
        return true;
    }

private:
    WriteFn m_write{nullptr};
    DelayFn m_delay{nullptr};
    uint8_t m_active_bank{0xFF};
};
