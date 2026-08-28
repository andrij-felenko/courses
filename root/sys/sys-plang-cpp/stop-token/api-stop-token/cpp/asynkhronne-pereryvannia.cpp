#include <stop_token>
#include <iostream>

struct SocketHandler {
    int socket_fd = 42;

    void shutdown_socket() {
        std::cout << "Виклик shutdown() для сокета " << socket_fd << "\n";
    }
};

void handle_network_stream(std::stop_token stoken) {
    SocketHandler handler;

    // Реєстрація зворотного виклику: якщо надійде сигнал зупинки,
    // сокет буде переведено в стан shutdown, що миттєво розблокує системний виклик read()
    std::stop_callback callback(stoken, [&handler] {
        handler.shutdown_socket();
    });

    // Блокуюче читання з дескриптора
}
