#include <sys/socket.h>
#include <cerrno>
#include <iostream>
#include <system_error>

// Безпечна відправка в C++ із захистом від SIGPIPE та перевіркою кодів відмов
void safe_channel_write(int channel_fd, const void *buf, size_t len) {
    while (true) {
        ssize_t sent = ::send(channel_fd, buf, len, MSG_NOSIGNAL);
        if (sent >= 0) {
            if (static_cast<size_t>(sent) != len) {
                throw std::runtime_error("Неповна відправка даних у канал");
            }
            return;
        }

        if (errno == EINTR) {
            continue; // Перервано сигналом — повторюємо
        }

        // Трансформуємо системні коди обриву межі у типізовані помилки
        if (errno == EPIPE || errno == ECONNRESET) {
            throw std::system_error(errno, std::generic_category(), "Партнерський процес впав (EPIPE/ECONNRESET)");
        }
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            throw std::system_error(errno, std::generic_category(), "Таймаут каналу зв'язку");
        }

        throw std::system_error(errno, std::generic_category(), "Помилка передачі в сокетний канал");
    }
}
