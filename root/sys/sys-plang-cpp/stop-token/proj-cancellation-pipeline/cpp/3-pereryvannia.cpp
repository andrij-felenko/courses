#include <iostream>
#include <stop_token>

#if defined(_WIN32)
#include <winsock2.h>
#else
#include <sys/socket.h>
#include <unistd.h>
#endif

// Клас-адаптер для перериваного читання з мережевого сокета
class InterruptibleSocketReader {
public:
    explicit InterruptibleSocketReader(int socket_fd)
        : socket_fd_(socket_fd) {}

    // Читання порції даних з можливістю негайного переривання
    std::size_t read_bytes(char* buffer, std::size_t max_len, std::stop_token stoken) {
        if (stoken.stop_requested()) {
            return 0;
        }

        // Реєструємо RAII-обробник: у разі надходження сигналу скасування
        // примусово перериваємо блокуючий системний виклик recv() на рівні ядра ОС
        std::stop_callback socket_canceller(stoken, [this] {
            std::cout << "[SocketReader] Переривання системного сокета через stop_callback...\n";
#if defined(_WIN32)
            ::shutdown(static_cast<SOCKET>(socket_fd_), SD_BOTH);
#else
            ::shutdown(socket_fd_, SHUT_RDWR);
#endif
        });

        // Блокуючий виклик: якщо надходить stop_token, shutdown() змушує recv()
        // негайно повернути 0 або -1 з кодом переривання (EBADF або ECONNABORTED)
#if defined(_WIN32)
        int bytes_read = ::recv(static_cast<SOCKET>(socket_fd_), buffer, static_cast<int>(max_len), 0);
#else
        ssize_t bytes_read = ::recv(socket_fd_, buffer, max_len, 0);
#endif

        if (bytes_read <= 0) {
            return 0;
        }

        return static_cast<std::size_t>(bytes_read);
    }

private:
    int socket_fd_;
};
