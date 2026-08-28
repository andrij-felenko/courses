#include <cstdint>
#include <span>
#include <expected>
#include "driver/uart.h"
#include "driver/gpio.h"
#include "esp_err.h"

namespace hardware_fix {

enum class UartError {
    ConfigFailed,
    PinSetFailed,
    DriverInstallFailed
};

class RemappedUart {
public:
    static constexpr uart_port_t Port = UART_NUM_1;
    static constexpr int BaudRate = 115200;

    /* Програмний обхід дефекту трасування ревізії Rev A */
    static constexpr gpio_num_t SwappedTxPin = GPIO_NUM_18;
    static constexpr gpio_num_t SwappedRxPin = GPIO_NUM_17;

    [[nodiscard]] static std::expected<void, UartError> init() noexcept {
        const uart_config_t config = {
            .baud_rate = BaudRate,
            .data_bits = UART_DATA_8_BITS,
            .parity    = UART_PARITY_DISABLE,
            .stop_bits = UART_STOP_BITS_1,
            .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
            .source_clk = UART_SCLK_DEFAULT,
        };

        if (uart_param_config(Port, &config) != ESP_OK) {
            return std::unexpected(UartError::ConfigFailed);
        }

        /* Задіюємо матрицю комутації виводів кристала */
        if (uart_set_pin(Port, SwappedTxPin, SwappedRxPin, 
                         UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE) != ESP_OK) {
            return std::unexpected(UartError::PinSetFailed);
        }

        constexpr int RxBufferSize = 1024;
        if (uart_driver_install(Port, RxBufferSize, 0, 0, nullptr, 0) != ESP_OK) {
            return std::unexpected(UartError::DriverInstallFailed);
        }

        return {};
    }
};

} // namespace hardware_fix
