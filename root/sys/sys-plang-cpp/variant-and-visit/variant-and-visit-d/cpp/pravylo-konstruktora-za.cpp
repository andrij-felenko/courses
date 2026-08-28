#include <variant>
#include <string>
#include <iostream>

struct ConnectionConfig {
    std::string address;
    uint16_t port;
    
    // Відсутній конструктор за замовчуванням!
    ConnectionConfig(std::string addr, uint16_t p)
        : address(std::move(addr)), port(p) {}
};

int main() {
    // std::variant<ConnectionConfig, int> v1; // ПОМИЛКА КОМПІЛЯЦІЇ: ConnectionConfig не можна створити без аргументів!

    // Коректне рішення: std::monostate як перша альтернатива
    std::variant<std::monostate, ConnectionConfig, int> v2;
    
    if (std::holds_alternative<std::monostate>(v2)) {
        std::cout << "Варіант ініціалізовано порожнім станом monostate (index = 0)\n";
    }
}
