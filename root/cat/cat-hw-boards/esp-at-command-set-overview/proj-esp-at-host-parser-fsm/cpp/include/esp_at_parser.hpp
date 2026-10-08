#ifndef ESP_AT_PARSER_HPP
#define ESP_AT_PARSER_HPP

#include "uart_ring_buffer.hpp"
#include <string>
#include <string_view>
#include <functional>
#include <cstdint>

/**
 * @brief Перелічення статусів виконання AT-команд модулем ESP8266.
 */
enum class AtStatus {
    OK,       ///< Команда успішно виконана ("OK")
    ERROR,    ///< Помилка синтаксису або виконання ("ERROR")
    BUSY,     ///< Модуль виконує іншу операцію ("BUSY")
    TIMEOUT,  ///< Час очікування відповіді вичерпано
    UNKNOWN   ///< Невідомий стан або неочікувана відповідь
};

/**
 * @brief Стани скінченного автомата (FSM) неблокуючого парсера.
 */
enum class ParserState {
    IDLE,             ///< Стан спокою / очікування даних
    ACCUMULATING,     ///< Накопичення символів поточного рядка
    WAITING_RESPONSE, ///< Очікування термінального статусу (OK/ERROR/BUSY) для команди
    ERROR_RECOVERY    ///< Відновлення після помилки розбору чи таймауту
};

/**
 * @brief RAII-обгортка для автоматичного керування життєвим циклом вбудованого буфера прийому.
 * 
 * Гарантує автоматичне очищення накопичувального рядкового буфера при виході з області
 * видимості або при виникненні виключних ситуацій під час розбору.
 */
class RxBufferGuard {
public:
    explicit RxBufferGuard(std::string& buffer) noexcept
        : m_buffer(buffer), m_dismissed(false) {}

    ~RxBufferGuard() {
        if (!m_dismissed) {
            m_buffer.clear();
        }
    }

    RxBufferGuard(const RxBufferGuard&) = delete;
    RxBufferGuard& operator=(const RxBufferGuard&) = delete;

    RxBufferGuard(RxBufferGuard&& other) noexcept
        : m_buffer(other.m_buffer), m_dismissed(other.m_dismissed) {
        other.m_dismissed = true;
    }

    /**
     * @brief Скасовує автоматичне очищення буфера деструктором.
     */
    void dismiss() noexcept {
        m_dismissed = true;
    }

    /**
     * @brief Примусово очищає буфер і повертає охоронця у стан активного захисту.
     */
    void reset() noexcept {
        m_buffer.clear();
        m_dismissed = false;
    }

private:
    std::string& m_buffer;
    bool m_dismissed;
};

/**
 * @brief ООП драйвер-парсер відповідей ESP-AT на основі скінченного автомата (FSM).
 */
class EspAtParser {
public:
    /// Тип функціонального колбеку для обробки результату виконання команди
    using StatusCallback = std::function<void(AtStatus status, std::string_view responsePayload)>;

    /// Тип функціонального колбеку для обробки асинхронних URC-повідомлень (+IPD, ready, тощо)
    using UrcCallback = std::function<void(std::string_view tag, std::string_view data)>;

    /**
     * @brief Конструктор парсера ESP-AT.
     * @param rxRing Посилання на кільцевий буфер UART.
     */
    explicit EspAtParser(DefaultUartRingBuffer& rxRing) noexcept;

    /**
     * @brief Реєстрація обробника подій статусів відповідей.
     */
    void setStatusCallback(StatusCallback cb) noexcept;

    /**
     * @brief Реєстрація обробника спонтанних URC-сповіщень.
     */
    void setUrcCallback(UrcCallback cb) noexcept;

    /**
     * @brief Ініціалізує очікування відповіді на надіслану AT-команду.
     * @param cmd Текст надісланої команди.
     * @param timeoutMs Таймаут очікування у мілісекундах.
     * @param currentMillis Поточний системний час у мілісекундах.
     */
    void sendCommand(std::string_view cmd, uint32_t timeoutMs, uint32_t currentMillis) noexcept;

    /**
     * @brief Головна неблокуюча функція оновлення стану FSM.
     * Викликається в кожній ітерації основного циклу мікроконтролера.
     * @param currentMillis Поточний системний час у мілісекундах.
     */
    void update(uint32_t currentMillis) noexcept;

    /**
     * @brief Скидає стан FSM та очищує вбудовані буфери розбору.
     */
    void reset() noexcept;

    /**
     * @brief Повертає поточний стан FSM-автомата.
     */
    ParserState getState() const noexcept { return m_state; }

    /**
     * @brief Перевіряє, чи перебуває парсер у стані очікування відповіді на команду.
     */
    bool isWaitingForResponse() const noexcept { return m_isWaitingResponse; }

private:
    static constexpr std::size_t MAX_LINE_BUFFER_SIZE = 256;

    void processByte(uint8_t byte) noexcept;
    void parseLine(std::string_view line) noexcept;
    bool checkStatusLine(std::string_view line) noexcept;
    bool checkUrcLine(std::string_view line) noexcept;
    void checkTimeout(uint32_t currentMillis) noexcept;

    static std::string_view trim(std::string_view sv) noexcept;

    DefaultUartRingBuffer& m_rxRing;
    ParserState m_state{ParserState::IDLE};
    
    std::string m_lineBuffer{};         ///< Буфер поточного рядка
    std::string m_accumulatedPayload{}; ///< Буфер накопичених даних відповіді
    
    StatusCallback m_statusCb{nullptr};
    UrcCallback m_urcCb{nullptr};

    bool m_isWaitingResponse{false};
    uint32_t m_commandStartTimeMs{0};
    uint32_t m_timeoutMs{0};
    std::string m_currentCommand{};
};

#endif // ESP_AT_PARSER_HPP
