#ifndef UART_HPP
#define UART_HPP

#include <cstdint>
#include <string_view>

namespace mcu {

/**
 * @brief Клас Uart для інкапсуляції периферійного модуля послідовного інтерфейсу ARM Cortex-M.
 * Забезпечує апаратне налаштування тактування, GPIO та передачу діагностичних логів
 * через віртуальний COM-порт (VCP) зневаджувача WeAct Mini Debugger.
 */
class Uart {
public:
    /**
     * @brief Структура регістрів периферійного модуля USART (ARM Cortex-M / STM32)
     */
    struct Registers {
        volatile uint32_t SR;   ///< Регістр стану (Status Register)
        volatile uint32_t DR;   ///< Регістр даних (Data Register)
        volatile uint32_t BRR;  ///< Регістр обчислення швидкості (Baud Rate Register)
        volatile uint32_t CR1;  ///< Регістр керування 1 (Control Register 1)
        volatile uint32_t CR2;  ///< Регістр керування 2 (Control Register 2)
        volatile uint32_t CR3;  ///< Регістр керування 3 (Control Register 3)
        volatile uint32_t GTPR; ///< Регістр захисного часу та дільника (Guard Time and Prescaler)
    };

    /**
     * @brief Конструктор обгортки UART.
     * @param instance Вказівник на базову адресу регістрів периферійного модуля (наприклад, USART2)
     */
    explicit Uart(Registers* instance) noexcept;

    /**
     * @brief Апаратна ініціалізація UART та пов'язаних виводів GPIO.
     * @param pclk_freq Швидкість тактування шини периферії (Гц)
     * @param baud_rate Бажана швидкість передачі даних (бод, наприклад 115200)
     */
    void init(uint32_t pclk_freq, uint32_t baud_rate) noexcept;

    /**
     * @brief Передача одного символу (байта) через UART з очікуванням готовності буфера (TXE).
     * @param ch Символ для відправки
     */
    void write_char(char ch) noexcept;

    /**
     * @brief Передача текстового рядка без завершення (std::string_view для оптимізації без виділення пам'яті).
     * @param str Рядок або зріз пам'яті для передачі
     */
    void write(std::string_view str) noexcept;

    /**
     * @brief Передача текстового рядка з автоматичним додаванням символу переведення рядка (\r\n).
     * @param str Рядок для виводу в консоль зневаджувача
     */
    void println(std::string_view str) noexcept;

    /**
     * @brief Очікування повного завершення передачі останнього байта (перевірка прапорця TC).
     */
    void flush() noexcept;

private:
    Registers* m_usart; ///< Вказівник на апаратні регістри модуля

    // Прапорці регістру стану SR
    static constexpr uint32_t SR_TXE = (1U << 7);  ///< Буфер даних порожній (Transmit Data Register Empty)
    static constexpr uint32_t SR_TC  = (1U << 6);  ///< Передачу повністю завершено (Transmission Complete)

    // Біти регістру керування CR1
    static constexpr uint32_t CR1_UE = (1U << 13); ///< Увімкнення USART (USART Enable)
    static constexpr uint32_t CR1_TE = (1U << 3);  ///< Увімкнення передавача (Transmitter Enable)
    static constexpr uint32_t CR1_RE = (1U << 2);  ///< Увімкнення приймача (Receiver Enable)
};

} // namespace mcu

#endif // UART_HPP
