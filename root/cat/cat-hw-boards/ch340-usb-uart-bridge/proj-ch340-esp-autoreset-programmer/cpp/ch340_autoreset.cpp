#include "ch340_autoreset.hpp"
#include <iostream>
#include <thread>

#ifndef _WIN32
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#endif

Ch340AutoReset::Ch340AutoReset(std::string_view portName)
    : m_portName(portName) {}

Ch340AutoReset::~Ch340AutoReset() {
    close();
}

Ch340AutoReset::Ch340AutoReset(Ch340AutoReset&& other) noexcept
    : m_portName(std::move(other.m_portName)) {
#ifdef _WIN32
    m_handle = other.m_handle;
    other.m_handle = INVALID_HANDLE_VALUE;
#else
    m_fd = other.m_fd;
    other.m_fd = -1;
#endif
}

Ch340AutoReset& Ch340AutoReset::operator=(Ch340AutoReset&& other) noexcept {
    if (this != &other) {
        close();
        m_portName = std::move(other.m_portName);
#ifdef _WIN32
        m_handle = other.m_handle;
        other.m_handle = INVALID_HANDLE_VALUE;
#else
        m_fd = other.m_fd;
        other.m_fd = -1;
#endif
    }
    return *this;
}

bool Ch340AutoReset::open(unsigned int baudRate) {
    close();

#ifdef _WIN32
    std::string formattedName = "\\\\.\\" + m_portName;
    m_handle = CreateFileA(formattedName.c_str(),
                           GENERIC_READ | GENERIC_WRITE,
                           0, NULL, OPEN_EXISTING, 0, NULL);

    if (m_handle == INVALID_HANDLE_VALUE) {
        std::cerr << "Помилка: не вдалося відкрити порт " << m_portName << std::endl;
        return false;
    }

    DCB dcb = {0};
    dcb.DCBlength = sizeof(dcb);
    if (!GetCommState(m_handle, &dcb)) {
        close();
        return false;
    }

    dcb.BaudRate = baudRate;
    dcb.ByteSize = 8;
    dcb.StopBits = ONESTOPBIT;
    dcb.Parity = NOPARITY;

    if (!SetCommState(m_handle, &dcb)) {
        close();
        return false;
    }
#else
    m_fd = ::open(m_portName.c_str(), O_RDWR | O_NOCTTY | O_NDELAY);
    if (m_fd < 0) {
        std::cerr << "Помилка: не вдалося відкрити порт " << m_portName << std::endl;
        return false;
    }

    struct termios options;
    tcgetattr(m_fd, &options);

    speed_t speed = B115200;
    if (baudRate == 9600) speed = B9600;
    else if (baudRate == 57600) speed = B57600;
    else if (baudRate == 115200) speed = B115200;
    else if (baudRate == 230400) speed = B230400;

    cfsetispeed(&options, speed);
    cfsetospeed(&options, speed);

    options.c_cflag &= ~PARENB;
    options.c_cflag &= ~CSTOPB;
    options.c_cflag &= ~CSIZE;
    options.c_cflag |= CS8 | CLOCAL | CREAD;

    tcsetattr(m_fd, TCSANOW, &options);
#endif

    return true;
}

void Ch340AutoReset::close() {
#ifdef _WIN32
    if (m_handle != INVALID_HANDLE_VALUE) {
        CloseHandle(m_handle);
        m_handle = INVALID_HANDLE_VALUE;
    }
#else
    if (m_fd >= 0) {
        ::close(m_fd);
        m_fd = -1;
    }
#endif
}

bool Ch340AutoReset::isOpen() const {
#ifdef _WIN32
    return m_handle != INVALID_HANDLE_VALUE;
#else
    return m_fd >= 0;
#endif
}

bool Ch340AutoReset::setDTR(bool active) {
    if (!isOpen()) return false;
#ifdef _WIN32
    return EscapeCommFunction(m_handle, active ? SETDTR : CLRDTR) != 0;
#else
    int flags = TIOCM_DTR;
    return ioctl(m_fd, active ? TIOCMBIS : TIOCMBIC, &flags) == 0;
#endif
}

bool Ch340AutoReset::setRTS(bool active) {
    if (!isOpen()) return false;
#ifdef _WIN32
    return EscapeCommFunction(m_handle, active ? SETRTS : CLRRTS) != 0;
#else
    int flags = TIOCM_RTS;
    return ioctl(m_fd, active ? TIOCMBIS : TIOCMBIC, &flags) == 0;
#endif
}

bool Ch340AutoReset::enterBootloader(std::chrono::milliseconds holdTime) {
    if (!isOpen()) return false;

    // Схема двотранзисторного автоскидання NodeMCU/ESP32:
    // 1. Подаємо RTS (EN = LOW, скидання мікроконтролера) та скидаємо DTR
    if (!setRTS(true) || !setDTR(false)) return false;
    std::this_thread::sleep_for(std::chrono::milliseconds(50));

    // 2. Подаємо DTR (GPIO0 = LOW, підготовка до завантажувача)
    if (!setDTR(true)) return false;
    std::this_thread::sleep_for(holdTime);

    // 3. Відпускаємо RTS (EN = HIGH, старт мікроконтролера під керуванням GPIO0=0)
    if (!setRTS(false)) return false;
    std::this_thread::sleep_for(std::chrono::milliseconds(50));

    // 4. Відпускаємо DTR (GPIO0 повертається у вихідний стан)
    if (!setDTR(false)) return false;

    return true;
}

bool Ch340AutoReset::reset(std::chrono::milliseconds pulseTime) {
    if (!isOpen()) return false;

    // Коротка пульсація лінії RTS для перезапуску процесора
    if (!setRTS(true)) return false;
    std::this_thread::sleep_for(pulseTime);
    if (!setRTS(false)) return false;

    return true;
}
