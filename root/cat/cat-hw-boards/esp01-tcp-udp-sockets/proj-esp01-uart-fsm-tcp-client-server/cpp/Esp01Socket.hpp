#ifndef ESP01_SOCKET_HPP
#define ESP01_SOCKET_HPP

#include "RingBuffer.hpp"
#include <cstddef>
#include <cstdint>

// Типи мережевих протоколів сокета.
enum class SocketType {
    TCP,
    UDP
};

// Стан кінцевого автомата з'єднання сокета.
enum class SocketState {
    Disconnected,
    Connecting,
    Connected,
    Disconnecting,
    Error
};

// Клас неблокуючого драйвера мережевого сокета ESP-01 через UART.
class Esp01Socket {
public:
    static constexpr std::size_t RxBufferSize = 512;
    static constexpr std::size_t TxBufferSize = 256;
    static constexpr std::size_t MaxAtResponseLen = 64;

    Esp01Socket(uint8_t linkId = 0);

    // Ініціалізує налаштування модема (режим MUX=1 для підтримки кількох з'єднань).
    bool begin();

    // Запускає асинхронний процес підключення до хоста.
    bool connect(SocketType type, const char* host, uint16_t port);

    // Запускає розрив з'єднання.
    bool disconnect();

    // Записує дані в вихідний кільцевий буфер для відправки.
    std::size_t write(const uint8_t* data, std::size_t length);

    // Зчитує накопичені дані з вхідного кільцевого буфера.
    std::size_t read(uint8_t* buffer, std::size_t maxLength);

    // Повертає кількість доступних для читання байтів у RX-буфері.
    std::size_t available() const;

    // Головний неблокуючий метод обробки (викликається в періодичному циклі loop).
    void update();

    // Зчитує поточний стан сокета.
    SocketState state() const { return m_state; }

    // Метод передачі байта через UART (імітація апаратного UART для прикладу).
    virtual void hardwareUartWrite(uint8_t byte) = 0;

    // Отримує новий символ із приймача UART.
    void onUartRxByte(uint8_t byte);

protected:
    virtual ~Esp01Socket() = default;

private:
    // Парсер вхідного текстового потоку UART та відповідних кадрів +IPD.
    void parseIncomingStream();
    void sendAtCommand(const char* cmd);

    uint8_t m_linkId;
    SocketState m_state;
    SocketType m_type;

    RingBuffer<uint8_t, RxBufferSize> m_rxBuffer;
    RingBuffer<uint8_t, TxBufferSize> m_txBuffer;
    RingBuffer<uint8_t, 128> m_uartRxStream;

    char m_lineBuffer[MaxAtResponseLen];
    std::size_t m_linePos;

    // Параметри парсингу пакета +IPD,<linkId>,<len>:
    bool m_parsingIpd;
    std::size_t m_ipdBytesRemaining;
};

#endif // ESP01_SOCKET_HPP
