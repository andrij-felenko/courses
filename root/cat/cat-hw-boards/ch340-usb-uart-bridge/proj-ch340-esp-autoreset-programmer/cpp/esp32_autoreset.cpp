#include "esp32_autoreset.hpp"
#include <iostream>
#include <thread>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <sys/ioctl.h>
#include <cerrno>

Esp32AutoReset::Esp32AutoReset(std::string_view port_path)
    : m_port_path(port_path) {
    m_fd = ::open(m_port_path.c_str(), O_RDWR | O_NOCTTY | O_NDELAY);
    if (m_fd < 0) {
        throw std::system_error(errno, std::generic_category(), 
            "Помилка відкриття послідовного порту: " + m_port_path);
    }

    /* Скидання неблокуючого прапорця */
    ::fcntl(m_fd, F_SETFL, 0);

    configure_port();
}

Esp32AutoReset::~Esp32AutoReset() {
    if (m_fd >= 0) {
        try {
            set_lines(false, false);
        } catch (...) {
            // Захист від винятків у деструкторі
        }
        ::close(m_fd);
        m_fd = -1;
    }
}

Esp32AutoReset::Esp32AutoReset(Esp32AutoReset&& other) noexcept
    : m_fd(other.m_fd), m_port_path(std::move(other.m_port_path)) {
    other.m_fd = -1;
}

Esp32AutoReset& Esp32AutoReset::operator=(Esp32AutoReset&& other) noexcept {
    if (this != &other) {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
        m_fd = other.m_fd;
        m_port_path = std::move(other.m_port_path);
        other.m_fd = -1;
    }
    return *this;
}

void Esp32AutoReset::configure_port() {
    struct termios options{};
    if (::tcgetattr(m_fd, &options) < 0) {
        throw std::system_error(errno, std::generic_category(), "Помилка tcgetattr");
    }

    ::cfsetispeed(&options, B115200);
    ::cfsetospeed(&options, B115200);

    options.c_cflag &= ~PARENB;
    options.c_cflag &= ~CSTOPB;
    options.c_cflag &= ~CSIZE;
    options.c_cflag |= CS8;
    options.c_cflag &= ~CRTSCTS;
    options.c_cflag |= CREAD | CLOCAL;

    options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
    options.c_iflag &= ~(IXON | IXOFF | IXANY | IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL);
    options.c_oflag &= ~OPOST;

    options.c_cc[VMIN] = 0;
    options.c_cc[VTIME] = 10;

    if (::tcsetattr(m_fd, TCSANOW, &options) < 0) {
        throw std::system_error(errno, std::generic_category(), "Помилка tcsetattr");
    }
}

void Esp32AutoReset::set_lines(bool dtr, bool rts) {
    if (m_fd < 0) {
        throw std::runtime_error("Спроба роботи із закритим дескриптором порту");
    }

    int dtr_bit = TIOCM_DTR;
    int rts_bit = TIOCM_RTS;

    if (dtr) {
        if (::ioctl(m_fd, TIOCMBIS, &dtr_bit) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка встановлення DTR");
        }
    } else {
        if (::ioctl(m_fd, TIOCMBIC, &dtr_bit) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка скидання DTR");
        }
    }

    if (rts) {
        if (::ioctl(m_fd, TIOCMBIS, &rts_bit) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка встановлення RTS");
        }
    } else {
        if (::ioctl(m_fd, TIOCMBIC, &rts_bit) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка скидання RTS");
        }
    }
}

void Esp32AutoReset::enter_bootloader(std::chrono::milliseconds delay_ms) {
    std::cout << "[Esp32AutoReset] Формування послідовності входу у Bootloader...\n";

    /* Крок 1: Початковий стан (DTR=0, RTS=0) -> EN=1, IO0=1 */
    set_lines(false, false);
    std::this_thread::sleep_for(delay_ms);

    /* Крок 2: Притискання IO0 до GND (DTR=0, RTS=1) -> EN=1, IO0=0 */
    set_lines(false, true);
    std::this_thread::sleep_for(delay_ms);

    /* Крок 3: Імпульс скидання EN у GND (DTR=1, RTS=0) -> EN=0, IO0=1 */
    set_lines(true, false);
    std::this_thread::sleep_for(delay_ms);

    /* Крок 4: Завершення скидання, IO0 підтягнутий (DTR=0, RTS=0) -> EN=1, IO0=1 */
    set_lines(false, false);
    std::this_thread::sleep_for(delay_ms);

    std::cout << "[Esp32AutoReset] ESP32 успішно переведено у режим Bootloader.\n";
}

void Esp32AutoReset::hard_reset(std::chrono::milliseconds reset_hold_ms) {
    std::cout << "[Esp32AutoReset] Виконання апаратного перезапуску (Hard Reset)...\n";

    /* Активація скидання EN (DTR=1, RTS=0) -> EN=0 */
    set_lines(true, false);
    std::this_thread::sleep_for(reset_hold_ms);

    /* Відпускання лінії EN (DTR=0, RTS=0) -> EN=1 */
    set_lines(false, false);
    std::this_thread::sleep_for(reset_hold_ms);

    std::cout << "[Esp32AutoReset] Перезапуск завершено.\n";
}
