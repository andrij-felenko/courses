#include <cstdint>
#include <mutex>
#include <expected>
#include <span>

namespace embedded::bus {

enum class BusError : uint8_t {
    MutexTimeout,
    TransferFailed,
    HardwareDeadlock
};

template <typename LowLevelI2c, typename RecoveryStrategy>
class ThreadSafeI2cBus {
public:
    ThreadSafeI2cBus(LowLevelI2c& i2c, RecoveryStrategy& recovery) noexcept
        : m_i2c{i2c}, m_recovery{recovery} {
        // Гарантоване скидання перед стартом периферії
        m_recovery.recover();
        m_i2c.init();
    }

    [[nodiscard]] std::expected<void, BusError> transfer(
        uint8_t addr,
        std::span<const uint8_t> tx_data,
        std::span<uint8_t> rx_data,
        uint32_t timeout_ms) noexcept
    {
        std::unique_lock<std::mutex> lock(m_bus_mutex);

        // Перша спроба передачі
        if (m_i2c.transfer(addr, tx_data, rx_data, timeout_ms)) {
            return {};
        }

        // У разі помилки — автоматичне скидання 9 тактами
        auto rec_res = m_recovery.recover();
        if (!rec_res) {
            return std::unexpected(BusError::HardwareDeadlock);
        }

        m_i2c.reinit();

        // Повторна спроба після відновлення
        if (m_i2c.transfer(addr, tx_data, rx_data, timeout_ms)) {
            return {};
        }

        return std::unexpected(BusError::TransferFailed);
    }

private:
    LowLevelI2c& m_i2c;
    RecoveryStrategy& m_recovery;
    std::mutex m_bus_mutex;
};

} // namespace embedded::bus
