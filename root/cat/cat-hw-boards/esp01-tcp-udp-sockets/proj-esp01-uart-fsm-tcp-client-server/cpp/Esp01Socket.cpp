#include "Esp01Socket.hpp"
#include <cstdio>
#include <cstring>

Esp01Socket::Esp01Socket(uint8_t linkId)
    : m_linkId(linkId),
      m_state(SocketState::Disconnected),
      m_type(SocketType::TCP),
      m_linePos(0),
      m_parsingIpd(false),
      m_ipdBytesRemaining(0) {
    m_lineBuffer[0] = '\0';
}

bool Esp01Socket::begin() {
    // Вмикаємо режим множинних підключень CIPMUX=1 для роботи із сокетами.
    sendAtCommand("AT+CIPMUX=1\r\n");
    m_state = SocketState::Disconnected;
    return true;
}

bool Esp01Socket::connect(SocketType type, const char* host, uint16_t port) {
    if (m_state != SocketState::Disconnected) {
        return false;
    }

    m_type = type;
    const char* typeStr = (type == SocketType::TCP) ? "TCP" : "UDP";

    char cmd[128];
    std::snprintf(cmd, sizeof(cmd), "AT+CIPSTART=%d,\"%s\",\"%s\",%d\r\n",
                  m_linkId, typeStr, host, port);

    m_state = SocketState::Connecting;
    sendAtCommand(cmd);
    return true;
}

bool Esp01Socket::disconnect() {
    if (m_state != SocketState::Connected) {
        return false;
    }

    char cmd[32];
    std::snprintf(cmd, sizeof(cmd), "AT+CIPCLOSE=%d\r\n", m_linkId);
    m_state = SocketState::Disconnecting;
    sendAtCommand(cmd);
    return true;
}

std::size_t Esp01Socket::write(const uint8_t* data, std::size_t length) {
    if (m_state != SocketState::Connected || length == 0) {
        return 0;
    }

    std::size_t written = 0;
    for (std::size_t i = 0; i < length; ++i) {
        if (!m_txBuffer.push(data[i])) {
            break; // Буфер TX заповнений
        }
        ++written;
    }
    return written;
}

std::size_t Esp01Socket::read(uint8_t* buffer, std::size_t maxLength) {
    std::size_t count = 0;
    uint8_t byte = 0;
    while (count < maxLength && m_rxBuffer.pop(byte)) {
        buffer[count++] = byte;
    }
    return count;
}

std::size_t Esp01Socket::available() const {
    return m_rxBuffer.size();
}

void Esp01Socket::onUartRxByte(uint8_t byte) {
    // Зберігаємо байт із переривання UART у сирий вхідний потік.
    m_uartRxStream.push(byte);
}

void Esp01Socket::sendAtCommand(const char* cmd) {
    std::size_t len = std::strlen(cmd);
    for (std::size_t i = 0; i < len; ++i) {
        hardwareUartWrite(static_cast<uint8_t>(cmd[i]));
    }
}

void Esp01Socket::update() {
    // 1. Обробка передачі даних із TX-буфера у разі наявності накопичених байтів.
    if (m_state == SocketState::Connected && !m_txBuffer.isEmpty()) {
        std::size_t bytesToSend = m_txBuffer.size();
        if (bytesToSend > 64) {
            bytesToSend = 64; // Відправляємо порціями до 64 байтів
        }

        char cmd[32];
        std::snprintf(cmd, sizeof(cmd), "AT+CIPSEND=%d,%d\r\n", m_linkId, static_cast<int>(bytesToSend));
        sendAtCommand(cmd);

        // Пересилаємо вміст TX-буфера в UART.
        uint8_t b = 0;
        for (std::size_t i = 0; i < bytesToSend; ++i) {
            if (m_txBuffer.pop(b)) {
                hardwareUartWrite(b);
            }
        }
    }

    // 2. Парсинг сирого вхідного потоку UART.
    parseIncomingStream();
}

void Esp01Socket::parseIncomingStream() {
    uint8_t byte = 0;
    while (m_uartRxStream.pop(byte)) {
        // Якщо триває парсинг безпосереднього бінарного тіла пакета +IPD:
        if (m_parsingIpd) {
            m_rxBuffer.push(byte);
            --m_ipdBytesRemaining;
            if (m_ipdBytesRemaining == 0) {
                m_parsingIpd = false;
            }
            continue;
        }

        // Інакше накопичуємо текстову відповідь AT-команди до символу '\n'.
        if (byte == '\n') {
            m_lineBuffer[m_linePos] = '\0';

            // Перевіряємо відповіді кінцевого автомата підключення.
            if (std::strstr(m_lineBuffer, "CONNECT") != nullptr) {
                m_state = SocketState::Connected;
            } else if (std::strstr(m_lineBuffer, "CLOSED") != nullptr) {
                m_state = SocketState::Disconnected;
            } else if (std::strstr(m_lineBuffer, "ERROR") != nullptr) {
                m_state = SocketState::Error;
            } else if (std::strncmp(m_lineBuffer, "+IPD,", 5) == 0) {
                // Формат: +IPD,<linkId>,<len>:
                int id = 0;
                int len = 0;
                if (std::sscanf(m_lineBuffer, "+IPD,%d,%d:", &id, &len) == 2) {
                    if (id == m_linkId && len > 0) {
                        m_parsingIpd = true;
                        m_ipdBytesRemaining = static_cast<std::size_t>(len);
                    }
                }
            }

            m_linePos = 0;
        } else if (byte != '\r') {
            if (m_linePos < MaxAtResponseLen - 1) {
                m_lineBuffer[m_linePos++] = static_cast<char>(byte);
            }
        }
    }
}
