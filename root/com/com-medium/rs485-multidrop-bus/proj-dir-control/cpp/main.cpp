// ============================================================================
// Мова C++: Ідіоматичний RAII-драйвер RS-485 із підтримкою std::span
// ============================================================================
#include <cstdint>
#include <cstddef>
#include <span>
#include <system_error>

class Rs485Bus {
public:
    enum class Direction {
        Receive,
        Transmit
    };

    // Конструктор приймає функціональний вказівник на керування піном DE
    explicit Rs485Bus(void (*set_dir_fn)(Direction)) 
        : set_direction_cb_(set_dir_fn) {
        setDirection(Direction::Receive); // За замовчуванням слухаємо шину
    }

    // RAII-клас для гарантованого автоматичного відпускання шини
    class ScopedTransmitter {
    public:
        explicit ScopedTransmitter(Rs485Bus& bus) : bus_(bus) {
            bus_.setDirection(Direction::Transmit);
        }
        
        ~ScopedTransmitter() {
            bus_.flushHardwareTx(); // Дочекатися прапорця TC перед відпусканням
            bus_.setDirection(Direction::Receive); // Гарантовано відпустити шину
        }

        ScopedTransmitter(const ScopedTransmitter&) = delete;
        ScopedTransmitter& operator=(const ScopedTransmitter&) = delete;

    private:
        Rs485Bus& bus_;
    };

    // Синхронна передача блоку даних через безпечний константний span
    std::error_code send(std::span<const std::uint8_t> data) {
        if (data.empty()) {
            return std::make_error_code(std::errc::invalid_argument);
        }

        // RAII-об'єкт автоматично захоплює шину і опускає DE при виході з зони видимості
        ScopedTransmitter tx_guard(*this);

        for (std::uint8_t byte : data) {
            sendHardwareByte(byte);
        }

        return {}; // Передачу виконано успішно
    }

private:
    void setDirection(Direction dir) {
        if (set_direction_cb_) {
            set_direction_cb_(dir);
        }
    }

    void sendHardwareByte(std::uint8_t byte) {
        extern void platform_uart_write(std::uint8_t);
        platform_uart_write(byte);
    }

    void flushHardwareTx() {
        // Очікування прапорця TC (Transmission Complete) на рівні периферії
        extern void platform_uart_wait_tc(void);
        platform_uart_wait_tc();
    }

    void (*set_direction_cb_)(Direction);
};
