#include <memory>
#include <iostream>

struct Connection {
    int socket_fd;
    Connection(int fd) : socket_fd(fd) { std::cout << "Підключено fd=" << fd << "\n"; }
    ~Connection() { std::cout << "Закрито fd=" << socket_fd << "\n"; }
};

void process_request(std::unique_ptr<Connection> conn) {
    // Володіння передано всередину функції; при виході з'єднання закриється автоматично
}

void demo_unique() {
    // Безпечне створення без явного new (C++14)
    auto conn = std::make_unique<Connection>(42);

    // Помилка компіляції: копіювання заборонено!
    // auto copy_conn = conn; 

    // Явна передача прав володіння через переміщення
    process_request(std::move(conn));

    // Тут conn == nullptr, ресурси вже звільнено
}
