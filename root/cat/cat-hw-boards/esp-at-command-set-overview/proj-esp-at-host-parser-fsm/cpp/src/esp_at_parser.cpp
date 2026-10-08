#include "esp_at_parser.hpp"
#include <algorithm>
#include <cctype>

EspAtParser::EspAtParser(DefaultUartRingBuffer& rxRing) noexcept
    : m_rxRing(rxRing) {
    m_lineBuffer.reserve(MAX_LINE_BUFFER_SIZE);
    m_accumulatedPayload.reserve(MAX_LINE_BUFFER_SIZE * 2);
}

void EspAtParser::setStatusCallback(StatusCallback cb) noexcept {
    m_statusCb = std::move(cb);
}

void EspAtParser::setUrcCallback(UrcCallback cb) noexcept {
    m_urcCb = std::move(cb);
}

void EspAtParser::sendCommand(std::string_view cmd, uint32_t timeoutMs, uint32_t currentMillis) noexcept {
    m_currentCommand = cmd;
    m_timeoutMs = timeoutMs;
    m_commandStartTimeMs = currentMillis;
    m_isWaitingResponse = true;
    m_accumulatedPayload.clear();
    m_state = ParserState::WAITING_RESPONSE;
}

void EspAtParser::reset() noexcept {
    m_state = ParserState::IDLE;
    m_isWaitingResponse = false;
    m_lineBuffer.clear();
    m_accumulatedPayload.clear();
    m_currentCommand.clear();
    m_commandStartTimeMs = 0;
    m_timeoutMs = 0;
}

void EspAtParser::update(uint32_t currentMillis) noexcept {
    // 1. Перевірка часових таймаутів при очікуванні відповіді
    checkTimeout(currentMillis);

    // 2. Вилучення байтів з кільцевого буфера та посимвольний розбір
    uint8_t byte = 0;
    while (m_rxRing.pop(byte)) {
        processByte(byte);
    }
}

void EspAtParser::processByte(uint8_t byte) noexcept {
    const char ch = static_cast<char>(byte);

    // Ігноруємо символ повернення каретки \r
    if (ch == '\r') {
        return;
    }

    // При виявленні символу переходу рядка \n обробляємо накопичений рядок
    if (ch == '\n') {
        RxBufferGuard guard(m_lineBuffer); // RAII автоматичне звільнення буфера рядка при виході з блоку

        std::string_view trimmedLine = trim(m_lineBuffer);
        if (!trimmedLine.empty()) {
            parseLine(trimmedLine);
        }

        if (!m_isWaitingResponse && m_state != ParserState::ERROR_RECOVERY) {
            m_state = ParserState::IDLE;
        }
        // Деструктор guard автоматично очищає m_lineBuffer
        return;
    }

    // Зміна стану автомата на накопичення символів, якщо він був у стані спокою
    if (m_state == ParserState::IDLE) {
        m_state = ParserState::ACCUMULATING;
    }

    // Контроль межі розміру вбудованого буфера (запобігання переповненню)
    if (m_lineBuffer.size() >= MAX_LINE_BUFFER_SIZE) {
        RxBufferGuard guard(m_lineBuffer); // Аварійне очищення буфера
        m_state = ParserState::ERROR_RECOVERY;
        if (m_statusCb) {
            m_statusCb(AtStatus::ERROR, "Переповнення вбудованого буфера рядка UART");
        }
        reset();
        return;
    }

    m_lineBuffer.push_back(ch);
}

void EspAtParser::parseLine(std::string_view line) noexcept {
    // Спершу перевіряємо, чи є рядок відомим спонтанним URC-повідомленням
    if (checkUrcLine(line)) {
        return;
    }

    // Перевіряємо статусні термінальні відповіді (OK, ERROR, BUSY)
    if (checkStatusLine(line)) {
        return;
    }

    // Якщо ми чекаємо відповіді на команду, накопичуємо проміжні дані (наприклад, інформаційні рядки)
    if (m_isWaitingResponse) {
        if (!m_accumulatedPayload.empty()) {
            m_accumulatedPayload.push_back('\n');
        }
        m_accumulatedPayload.append(line);
    }
}

bool EspAtParser::checkStatusLine(std::string_view line) noexcept {
    AtStatus status = AtStatus::UNKNOWN;
    bool isStatus = false;

    if (line == "OK") {
        status = AtStatus::OK;
        isStatus = true;
    } else if (line == "ERROR") {
        status = AtStatus::ERROR;
        isStatus = true;
    } else if (line.rfind("BUSY", 0) == 0 || line.rfind("busy", 0) == 0) {
        status = AtStatus::BUSY;
        isStatus = true;
    }

    if (isStatus) {
        m_isWaitingResponse = false;
        m_state = ParserState::IDLE;

        if (m_statusCb) {
            m_statusCb(status, m_accumulatedPayload);
        }
        m_accumulatedPayload.clear();
        return true;
    }

    return false;
}

bool EspAtParser::checkUrcLine(std::string_view line) noexcept {
    // Приклади системних та мережевих URC від ESP8266: "ready", "WIFI CONNECTED", "WIFI GOT IP", "+IPD,..."
    if (line == "ready") {
        if (m_urcCb) m_urcCb("SYSTEM", "ready");
        return true;
    }
    
    if (line == "WIFI CONNECTED") {
        if (m_urcCb) m_urcCb("WIFI", "CONNECTED");
        return true;
    }

    if (line == "WIFI DISCONNECT") {
        if (m_urcCb) m_urcCb("WIFI", "DISCONNECT");
        return true;
    }

    if (line == "WIFI GOT IP") {
        if (m_urcCb) m_urcCb("WIFI", "GOT IP");
        return true;
    }

    // Вхідні мережеві дані: +IPD,<link_id>,<len>:<data>
    if (line.rfind("+IPD,", 0) == 0) {
        if (m_urcCb) {
            std::string_view dataPart = line.substr(5);
            m_urcCb("+IPD", dataPart);
        }
        return true;
    }

    return false;
}

void EspAtParser::checkTimeout(uint32_t currentMillis) noexcept {
    if (!m_isWaitingResponse) {
        return;
    }

    if (currentMillis - m_commandStartTimeMs >= m_timeoutMs) {
        m_isWaitingResponse = false;
        m_state = ParserState::IDLE;

        if (m_statusCb) {
            m_statusCb(AtStatus::TIMEOUT, m_accumulatedPayload);
        }

        RxBufferGuard guard(m_lineBuffer); // Автоматичне очищення буфера рядка під час таймауту
        m_accumulatedPayload.clear();
    }
}

std::string_view EspAtParser::trim(std::string_view sv) noexcept {
    while (!sv.empty() && std::isspace(static_cast<unsigned char>(sv.front()))) {
        sv.remove_prefix(1);
    }
    while (!sv.empty() && std::isspace(static_cast<unsigned char>(sv.back()))) {
        sv.remove_suffix(1);
    }
    return sv;
}
