#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <array>
#include <concepts>

enum class ModbusError : uint8_t {
    Timeout,
    CrcMismatch,
    DeviceException,
    InvalidSlaveAddress,
    InvalidFunctionCode,
    BufferOverflow
};

struct ModbusConfig {
    uint8_t slave_address;
    uint16_t start_register;
    uint16_t register_count;
    uint32_t timeout_ms{200};
};

/* Концепт апаратного рівня зв'язку */
template <typename T>
concept SerialBusHal = requires(T hal, bool state, std::span<const uint8_t> tx, std::span<uint8_t> rx, uint32_t ms) {
    { hal.set_driver_enable(state) } -> std::same_as<void>;
    { hal.transmit(tx) } -> std::same_as<void>;
    { hal.wait_tx_complete() } -> std::same_as<void>;
    { hal.receive(rx, ms) } -> std::same_as<size_t>;
    { hal.delay_us(ms) } -> std::same_as<void>;
};

/* RAII-вартовий напрямку трансивера DE/RE */
template <SerialBusHal Hal>
class TransceiverDirectionGuard {
public:
    explicit TransceiverDirectionGuard(Hal& hal) : hal_(hal) {
        hal_.set_driver_enable(true);
        hal_.delay_us(50);
    }
    ~TransceiverDirectionGuard() {
        hal_.wait_tx_complete();
        hal_.set_driver_enable(false);
    }
    TransceiverDirectionGuard(const TransceiverDirectionGuard&) = delete;
    TransceiverDirectionGuard& operator=(const TransceiverDirectionGuard&) = delete;
private:
    Hal& hal_;
};

/* Обчислення CRC16 Modbus на етапі компіляції (constexpr) */
class ModbusCrc {
public:
    static constexpr auto Table = []() constexpr {
        std::array<uint16_t, 256> tbl{};
        for (size_t i = 0; i < 256; ++i) {
            uint16_t crc = static_cast<uint16_t>(i);
            for (size_t j = 0; j < 8; ++j) {
                if (crc & 0x0001) {
                    crc = (crc >> 1) ^ 0xA001;
                } else {
                    crc >>= 1;
                }
            }
            tbl[i] = crc;
        }
        return tbl;
    }();

    static constexpr uint16_t calculate(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFF;
        for (uint8_t byte : data) {
            uint8_t idx = static_cast<uint8_t>(crc ^ byte);
            crc = static_cast<uint16_t>((crc >> 8) ^ Table[idx]);
        }
        return crc;
    }
};

template <SerialBusHal Hal>
class ModbusMasterClient {
public:
    explicit ModbusMasterClient(Hal& hal) : hal_(hal) {}

    std::expected<size_t, ModbusError> read_input_registers(
        const ModbusConfig& config,
        std::span<uint16_t> output_registers
    ) {
        if (config.register_count == 0 || config.register_count > output_registers.size()) {
            return std::unexpected(ModbusError::BufferOverflow);
        }

        std::array<uint8_t, 8> tx_frame{
            config.slave_address,
            0x04, // Read Input Registers
            static_cast<uint8_t>(config.start_register >> 8),
            static_cast<uint8_t>(config.start_register & 0xFF),
            static_cast<uint8_t>(config.register_count >> 8),
            static_cast<uint8_t>(config.register_count & 0xFF),
            0x00, 0x00
        };

        uint16_t tx_crc = ModbusCrc::calculate(std::span{tx_frame.data(), 6});
        tx_frame[6] = static_cast<uint8_t>(tx_crc & 0xFF);
        tx_frame[7] = static_cast<uint8_t>((tx_crc >> 8) & 0xFF);

        /* Безпечна передача з автоперемиканням шини по завершенню через RAII */
        {
            TransceiverDirectionGuard<Hal> guard(hal_);
            hal_.transmit(tx_frame);
        }

        std::array<uint8_t, 256> rx_buffer{};
        const size_t expected_payload_bytes = config.register_count * 2;
        const size_t expected_total_bytes = 1 + 1 + 1 + expected_payload_bytes + 2;

        size_t received_len = hal_.receive(rx_buffer, config.timeout_ms);
        if (received_len < 5) {
            return std::unexpected(ModbusError::Timeout);
        }

        uint16_t rx_crc = static_cast<uint16_t>(
            rx_buffer[received_len - 2] | (rx_buffer[received_len - 1] << 8)
        );
        uint16_t calculated_crc = ModbusCrc::calculate(
            std::span{rx_buffer.data(), received_len - 2}
        );

        if (rx_crc != calculated_crc) {
            return std::unexpected(ModbusError::CrcMismatch);
        }

        if (rx_buffer[0] != config.slave_address) {
            return std::unexpected(ModbusError::InvalidSlaveAddress);
        }

        if (rx_buffer[1] == (0x04 | 0x80)) {
            return std::unexpected(ModbusError::DeviceException);
        }

        if (rx_buffer[1] != 0x04 || rx_buffer[2] != expected_payload_bytes || received_len != expected_total_bytes) {
            return std::unexpected(ModbusError::InvalidFunctionCode);
        }

        for (size_t i = 0; i < config.register_count; ++i) {
            size_t offset = 3 + i * 2;
            output_registers[i] = static_cast<uint16_t>(
                (rx_buffer[offset] << 8) | rx_buffer[offset + 1]
            );
        }

        return config.register_count;
    }

private:
    Hal& hal_;
};
