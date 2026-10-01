#ifndef CH340_BRIDGE_HPP
#define CH340_BRIDGE_HPP

#include <cstdint>
#include <cstddef>
#include <array>

namespace ch340 {

/// @brief Конфігураційні параметри для апаратного послідовного інтерфейсу UART.
struct UartConfig {
    uint32_t baud_rate{115200};       ///< Швидкість передачі даних у бодах (наприклад, 9600, 115200)
    int rx_pin{16};                   ///< Номер виводу RX мікроконтролера (підключається до TXD CH340)
    int tx_pin{17};                   ///< Номер виводу TX мікроконтролера (підключається до RXD CH340)
    int uart_port{1};                 ///< Апаратний номер UART (0, 1, 2)
    std::size_t rx_buffer_size{1024}; ///< Розмір буфера прийому у байтах
    std::size_t tx_buffer_size{1024}; ///< Розмір буфера передачі у байтах
};

/// @brief Налаштування світлодіодного індикатора активності послідовного зв'язку.
struct IndicatorConfig {
    int led_pin{2};                    ///< GPIO вивід для світлодіода (наприклад, LED_BUILTIN)
    bool active_high{true};            ///< true — логічна 1 вмикає світлодіод; false — логічний 0
    uint32_t activity_timeout_ms{100}; ///< Тривалість світіння світлодіода після останнього байта (мс)
};

/// @brief Стан послідовного з'єднання через CH340.
enum class ConnectionState {
    IDLE,   ///< Простій: дані не передаються, порт готовий
    ACTIVE, ///< Активність: відбувається прийом або ретрансляція байтів
    ERROR   ///< Помилка ініціалізації або апаратного буфера UART
};

/// @brief Клас для керування двостороннім обміном даними через USB-UART міст CH340.
///
/// Інкапсулює ініціалізацію апаратного UART, прийом байтів від host-системи,
/// автоматичну відправку ехо-відповіді та індикацію активності за допомогою LED.
class Ch340Bridge {
public:
    /// @brief Конструктор із конфігураційними параметрами.
    /// @param uart_cfg Налаштування послідовного порту UART
    /// @param ind_cfg Налаштування світлодіода індикації
    explicit Ch340Bridge(const UartConfig& uart_cfg = UartConfig{},
                         const IndicatorConfig& ind_cfg = IndicatorConfig{});

    /// @brief Деструктор для безпечного звільнення апаратних ресурсів UART.
    ~Ch340Bridge();

    // Заборона копіювання для запобігання дублюванню апаратного ресурсу UART
    Ch340Bridge(const Ch340Bridge&) = delete;
    Ch340Bridge& operator=(const Ch340Bridge&) = delete;

    // Дозвіл переміщення
    Ch340Bridge(Ch340Bridge&&) noexcept;
    Ch340Bridge& operator=(Ch340Bridge&&) noexcept;

    /// @brief Ініціалізує периферію UART та GPIO індикатора.
    /// @return true, якщо ініціалізація успішна, інакше false.
    bool begin();

    /// @brief Оновлює стан обробки потоку даних та керує індикатором активності.
    /// Має регулярно викликатися в головному циклі (loop / main task).
    void update();

    /// @brief Виконує вибірку вхідного потоку і негайно відправляє ехо-байти назад.
    /// @return Кількість байтів, прийнятих та відправлених у цій ітерації.
    std::size_t processEcho();

    /// @brief Повертає поточний стан з'єднання.
    [[nodiscard]] ConnectionState getState() const noexcept { return state_; }

    /// @brief Повертає загальну кількість оброблених (ехогованих) байтів.
    [[nodiscard]] uint64_t getTotalBytesProcessed() const noexcept { return total_bytes_processed_; }

    /// @brief Перевіряє, чи активна зараз передача даних.
    [[nodiscard]] bool isTransferActive() const noexcept { return state_ == ConnectionState::ACTIVE; }

private:
    /// @brief Встановлює стан світлодіода індикатора.
    /// @param turn_on true — увімкнути, false — вимкнути.
    void setLedState(bool turn_on);

    /// @brief Отримує поточний системний час у мілісекундах.
    [[nodiscard]] uint32_t getCurrentMillis() const noexcept;

    UartConfig uart_cfg_;
    IndicatorConfig ind_cfg_;
    ConnectionState state_{ConnectionState::IDLE};

    uint32_t last_activity_timestamp_{0};
    uint64_t total_bytes_processed_{0};
    bool initialized_{false};

    static constexpr std::size_t INTERNAL_CHUNK_SIZE = 256;
    std::array<uint8_t, INTERNAL_CHUNK_SIZE> rx_chunk_buffer_{};
};

} // namespace ch340

#endif // CH340_BRIDGE_HPP
