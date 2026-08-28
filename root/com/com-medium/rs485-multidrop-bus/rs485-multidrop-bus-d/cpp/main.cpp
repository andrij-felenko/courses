// ============================================================================
// Мова C++: Ідіоматичне RAII-керування піном напрямку RS-485 із std::span
// ============================================================================
#include <cstdint>
#include <cstddef>
#include <span>

class Rs485DirectionGuard {
public:
    Rs485DirectionGuard() {
        setDeHardware(true);  // Умикаємо передавач RS-485 при створенні об'єкта
    }
    
    ~Rs485DirectionGuard() {
        waitUartTcHardware(); // Чекаємо повного виходу останнього стоп-біта (TC)
        setDeHardware(false); // Завжди відпускаємо шину в RX навіть при винятках
    }

    Rs485DirectionGuard(const Rs485DirectionGuard&) = delete;
    Rs485DirectionGuard& operator=(const Rs485DirectionGuard&) = delete;

private:
    static void setDeHardware(bool active) {
        extern void platform_set_de(bool);
        platform_set_de(active);
    }

    static void waitUartTcHardware() {
        extern void platform_wait_tc(void);
        platform_wait_tc();
    }
};

void send_telemetry_packet(std::span<const std::uint8_t> packet) {
    Rs485DirectionGuard guard; // RAII тримає шину під час роботи функції
    for (std::uint8_t byte : packet) {
        extern void platform_uart_write(std::uint8_t);
        platform_uart_write(byte);
    }
}
