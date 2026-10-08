#include <cstdint>

class Ov3640Scaler {
public:
    static constexpr uint8_t REG_BANK_SEL = 0xFF;

    enum class Bank : uint8_t {
        System = 0x00,
        ISP    = 0x01,
        Scaler = 0x02,
        Jpeg   = 0x03
    };

    explicit Ov3640Scaler(bool (*sccb_write_fn)(uint8_t, uint8_t))
        : m_sccb_write(sccb_write_fn) {}

    bool selectBank(Bank bank) const {
        return m_sccb_write(REG_BANK_SEL, static_cast<uint8_t>(bank));
    }

    bool writeReg(Bank bank, uint8_t reg, uint8_t val) const {
        if (!selectBank(bank)) {
            return false;
        }
        return m_sccb_write(reg, val);
    }

    bool configureJpegOutput(uint16_t targetWidth, uint16_t targetHeight) const {
        // Увімкнення тактування JPEG у банку ISP
        if (!writeReg(Bank::ISP, 0x12, 0x10)) {
            return false;
        }
        // Запис роздільної здатності у банк скалера
        writeReg(Bank::Scaler, 0x90, static_cast<uint8_t>(targetWidth >> 8));
        writeReg(Bank::Scaler, 0x91, static_cast<uint8_t>(targetWidth & 0xFF));
        writeReg(Bank::Scaler, 0x92, static_cast<uint8_t>(targetHeight >> 8));
        writeReg(Bank::Scaler, 0x93, static_cast<uint8_t>(targetHeight & 0xFF));
        return true;
    }

private:
    bool (*m_sccb_write)(uint8_t, uint8_t){nullptr};
};
