#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <concepts>

enum class DataRate : uint8_t {
    Rate250kbps = 0x20,
    Rate1Mbps   = 0x00,
    Rate2Mbps   = 0x08
};

enum class PowerLevel : uint8_t {
    Min18dBm = 0x00,
    Low12dBm = 0x02,
    Mid6dBm  = 0x04,
    Max0dBm  = 0x06
};

/* Концепт апаратного адаптера для вбудованих платформ */
template <typename T>
concept SpiDriver = requires(T hal, std::span<const uint8_t> tx, std::span<uint8_t> rx, bool level, uint32_t us) {
    { hal.spiTransfer(tx, rx) } -> std::same_as<void>;
    { hal.setCsPin(level) }     -> std::same_as<void>;
    { hal.setCePin(level) }     -> std::same_as<void>;
    { hal.delayUs(us) }         -> std::same_as<void>;
};

template <SpiDriver Hal>
class Nrf24Radio {
public:
    explicit Nrf24Radio(Hal hal, uint8_t channel = 76) 
        : hal_{hal}, channel_{channel} {}

    void init(DataRate rate = DataRate::Rate2Mbps, PowerLevel pwr = PowerLevel::Max0dBm) {
        hal_.setCePin(false);
        hal_.setCsPin(true);
        hal_.delayUs(5000);

        writeRegister(0x03, 0x03); /* 5-байтова адресація */
        writeRegister(0x04, 0x5A); /* ARD 1500 мкс, 10 спроб */
        writeRegister(0x05, channel_);

        uint8_t setup_val = static_cast<uint8_t>(rate) | static_cast<uint8_t>(pwr);
        writeRegister(0x06, setup_val);

        writeRegister(0x1D, 0x04); /* EN_DPL = 1 */
        writeRegister(0x1C, 0x01); /* DPL Pipe 0 */
        writeRegister(0x01, 0x01); /* Auto-ACK Pipe 0 */
        writeRegister(0x02, 0x01); /* Enable RX Pipe 0 */

        writeRegister(0x07, 0x70); /* Clear IRQ flags */
        flushTx();
        flushRx();

        writeRegister(0x00, 0x0C); /* PWR_UP, CRC 2-byte */
        hal_.delayUs(1500);
    }

    bool transmit(std::span<const uint8_t, 5> address, std::span<const uint8_t> data) {
        writeAddress(0x10, address); /* TX_ADDR */
        writeAddress(0x0A, address); /* RX_ADDR_P0 для Auto-ACK */

        writeRegister(0x00, 0x0E);   /* TX mode */

        {
            SpiGuard guard(hal_);
            uint8_t cmd = 0xA0;      /* W_TX_PAYLOAD */
            hal_.spiTransfer(std::span(&cmd, 1), {});
            hal_.spiTransfer(data, {});
        }

        hal_.setCePin(true);
        hal_.delayUs(15);
        hal_.setCePin(false);

        while (true) {
            uint8_t status = readRegister(0x07);
            if (status & (1 << 5)) { /* TX_DS */
                writeRegister(0x07, (1 << 5));
                return true;
            }
            if (status & (1 << 4)) { /* MAX_RT */
                writeRegister(0x07, (1 << 4));
                flushTx();
                return false;
            }
            hal_.delayUs(50);
        }
    }

    void startListening(std::span<const uint8_t, 5> address) {
        writeAddress(0x0A, address);
        writeRegister(0x00, 0x0F);   /* PRIM_RX = 1, PWR_UP = 1 */
        hal_.setCePin(true);
        hal_.delayUs(130);
    }

    bool receive(std::span<uint8_t> outBuffer, size_t& bytesRead) {
        uint8_t status = readRegister(0x07);
        if (!(status & (1 << 6))) {  /* RX_DR */
            return false;
        }

        uint8_t payloadWidth = 0;
        {
            SpiGuard guard(hal_);
            std::array<uint8_t, 2> tx = { 0x60, 0xFF }; /* R_RX_PL_WID */
            std::array<uint8_t, 2> rx = {};
            hal_.spiTransfer(tx, rx);
            payloadWidth = rx[1];
        }

        if (payloadWidth > 32) {
            flushRx();
            writeRegister(0x07, (1 << 6));
            return false;
        }

        size_t count = std::min(static_cast<size_t>(payloadWidth), outBuffer.size());
        {
            SpiGuard guard(hal_);
            uint8_t cmd = 0x61;      /* R_RX_PAYLOAD */
            hal_.spiTransfer(std::span(&cmd, 1), {});
            hal_.spiTransfer({}, outBuffer.subspan(0, count));
        }

        bytesRead = count;
        writeRegister(0x07, (1 << 6));
        return true;
    }

private:
    class SpiGuard {
    public:
        explicit SpiGuard(Hal& hal) : hal_{hal} { hal_.setCsPin(false); }
        ~SpiGuard() { hal_.setCsPin(true); }
    private:
        Hal& hal_;
    };

    uint8_t readRegister(uint8_t reg) {
        std::array<uint8_t, 2> tx = { static_cast<uint8_t>(reg & 0x1F), 0xFF };
        std::array<uint8_t, 2> rx = {};
        SpiGuard guard(hal_);
        hal_.spiTransfer(tx, rx);
        return rx[1];
    }

    void writeRegister(uint8_t reg, uint8_t val) {
        std::array<uint8_t, 2> tx = { static_cast<uint8_t>(0x20 | (reg & 0x1F)), val };
        SpiGuard guard(hal_);
        hal_.spiTransfer(tx, {});
    }

    void writeAddress(uint8_t reg, std::span<const uint8_t, 5> addr) {
        uint8_t cmd = static_cast<uint8_t>(0x20 | (reg & 0x1F));
        SpiGuard guard(hal_);
        hal_.spiTransfer(std::span(&cmd, 1), {});
        hal_.spiTransfer(addr, {});
    }

    void flushTx() {
        uint8_t cmd = 0xE1;
        SpiGuard guard(hal_);
        hal_.spiTransfer(std::span(&cmd, 1), {});
    }

    void flushRx() {
        uint8_t cmd = 0xE2;
        SpiGuard guard(hal_);
        hal_.spiTransfer(std::span(&cmd, 1), {});
    }

    Hal hal_;
    uint8_t channel_;
};
