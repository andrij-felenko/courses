// Ігнорування сигналу SIGPIPE на рівні ініціалізації середовища
#include <csignal>

void configureProcessSignals() noexcept {
    std::signal(SIGPIPE, SIG_IGN);
}

// Передача прапорця MSG_NOSIGNAL при відправленні даних
ssize_t sendDataSafely(int fd, std::string_view data) noexcept {
    return ::send(fd, data.data(), data.size(), MSG_NOSIGNAL);
}
