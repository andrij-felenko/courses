#include <cstdint>
#include <span>

class RdcTransceiver {
public:
    struct Telemetry {
        uint16_t angle{0};
        int16_t  velocity{0};
        uint8_t  faultStatus{0};
    };

    explicit RdcTransceiver(uint32_t csPin) : m_csPin(csPin) {}

    bool readTelemetry(Telemetry& outData) {
        const uint8_t txCmd[4] = {0x80, 0x00, 0x00, 0x00};
        uint8_t rxBuf[4] = {0};

        setCsState(false);
        spiExchange(txCmd, rxBuf);
        setCsState(true);

        outData.angle = (static_cast<uint16_t>(rxBuf[0]) << 8) | rxBuf[1];
        outData.velocity = (static_cast<int16_t>(rxBuf[2]) << 8) | rxBuf[3];

        if ((rxBuf[3] & 0x01) != 0) {
            outData.faultStatus = readFaultRegister();
            return false;
        }

        outData.faultStatus = 0;
        return true;
    }

private:
    uint32_t m_csPin;

    void setCsState(bool high) {
        // Управління лінією CS
    }

    void spiExchange(const uint8_t* tx, uint8_t* rx) {
        // Послідовний обмін по інтерфейсу SPI
    }

    uint8_t readFaultRegister() {
        // Зчитування регістра помилок
        return 0xFF;
    }
};
