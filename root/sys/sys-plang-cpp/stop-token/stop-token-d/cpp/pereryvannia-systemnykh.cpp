#include <stop_token>
#include <iostream>

#if defined(_WIN32)
#include <winsock2.h>
#else
#include <sys/socket.h>
#endif

void read_from_network(int socket_fd, std::stop_token stoken) {
    // Реєструємо зворотний виклик для розриву блокуючого системного виклику
    std::stop_callback socket_canceller(stoken, [socket_fd] {
        std::cout << "Примусове розблокування сокета...\n";
#if defined(_WIN32)
        ::shutdown(static_cast<SOCKET>(socket_fd), SD_BOTH);
#else
        ::shutdown(socket_fd, SHUT_RDWR);
#endif
    });

    char buffer[1024];
    // Якщо приходить request_stop(), shutdown() змушує recv() негайно повернути помилку
    auto bytes = ::recv(socket_fd, buffer, sizeof(buffer), 0);
    if (bytes <= 0 && stoken.stop_requested()) {
        std::cout << "Читання з сокета успішно перервано сигналом скасування.\n";
    }
}
