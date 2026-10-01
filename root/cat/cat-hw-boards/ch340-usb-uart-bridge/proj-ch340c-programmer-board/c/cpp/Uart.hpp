#ifndef UART_HPP
#define UART_HPP

#include <cstdint>
#include <cstddef>
#include <string_view>

/**
 * @class Uart
 * @brief Клас для інкапсуляції апаратного модуля UART мікроконтролера.
 * 
 * Забезпечує RAII-управління периферійним модулем UART для взаємодії
 * з комп'ютером через мікросхему-міст CH340 USB-UART.
 */
class Uart {
public:
    /**
     * @brief Конструктор із автоматичною ініціалізацією апаратного UART.
     * @param baud_rate Швидкість обміну даними у бодах (за замовчуванням 9600).
     */
    explicit Uart(uint32_t baud_rate = 9600);

    /**
     * @brief Деструктор, що безпечно деактивує модуль UART.
     */
    ~Uart();

    /* Видалення копіювання для запобігання конфліктам доступу до апаратних регістрів */
    Uart(const Uart&) = delete;
    Uart& operator=(const Uart&) = delete;

    /* Дозвіл переміщення об'єкта */
    Uart(Uart&&) noexcept = default;
    Uart& operator=(Uart&&) noexcept = default;

    /**
     * @brief Конфігурує параметри швидкості та кадру апаратного UART.
     * @param baud_rate Швидкість обміну в бодах.
     */
    void init(uint32_t baud_rate) noexcept;

    /**
     * @brief Перевіряє наявність нових даних у приймальному буфері.
     * @return true, якщо є байт для зчитування.
     */
    [[nodiscard]] bool is_data_available() const noexcept;

    /**
     * @brief Блокуюче зчитування байта з приймача UART.
     * @return Зчитаний байт.
     */
    [[nodiscard]] uint8_t receive_byte() const noexcept;

    /**
     * @brief Неблокуюча спроба прочитати байт.
     * @param out_data Посилання на змінну для запису байта.
     * @return true у разі успішного зчитання, false якщо даних немає.
     */
    [[nodiscard]] bool receive_byte_nonblocking(uint8_t& out_data) const noexcept;

    /**
     * @brief Відправляє один байт у порт.
     * @param data Байт для відправки.
     */
    void send_byte(uint8_t data) const noexcept;

    /**
     * @brief Відправляє текстовий рядок або зріз пам'яті через std::string_view.
     * @param str Рядок для відправлення.
     */
    void send_string(std::string_view str) const noexcept;
};

#endif // UART_HPP
