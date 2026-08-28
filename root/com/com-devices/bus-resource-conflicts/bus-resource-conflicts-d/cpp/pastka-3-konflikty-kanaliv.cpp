#include <cstdint>
#include <mutex>
#include <expected>
#include <span>

namespace embedded::bus {

enum class SpiError : uint8_t {
    BusBusyTimeout,
    DmaTimeout,
    HardwareFault
};

template <typename LowLevelSpiDma, typename OsPrimitives>
class SafeSpiBusManager {
public:
    SafeSpiBusManager(LowLevelSpiDma& dma_driver, OsPrimitives& os) noexcept
        : m_driver{dma_driver}, m_os{os} {}

    [[nodiscard]] std::expected<void, SpiError> transmit(
        std::span<const uint8_t> data,
        uint32_t timeout_ms) noexcept
    {
        // 1. Захоплення м'ютекса шини через RAII
        std::unique_lock<std::mutex> lock(m_bus_mutex);

        // 2. Старт апаратного DMA
        if (!m_driver.start_dma_tx(data.data(), static_cast<uint16_t>(data.size()))) {
            return std::unexpected(SpiError::HardwareFault);
        }

        // 3. Очікування події від ISR завершення DMA
        if (!m_os.wait_dma_complete_flag(timeout_ms)) {
            m_driver.abort_dma();
            return std::unexpected(SpiError::DmaTimeout);
        }

        return {};
    }

private:
    LowLevelSpiDma& m_driver;
    OsPrimitives& m_os;
    std::mutex m_bus_mutex;
};

} // namespace embedded::bus
