#include <mutex>
#include <string>
#include <iostream>
#include <stdexcept>
#include <thread>
#include <chrono>

class ResilientNetworkClient {
private:
    std::string session_token_;
    std::once_flag auth_flag_;
    int attempt_count_ = 0;

    void authenticate_rpc() {
        ++attempt_count_;
        std::cout << "[Спроба " << attempt_count_ << "] Спроба авторизації на сервері...\n";
        
        if (attempt_count_ == 1) {
            // Імітація первинного збою мережі
            std::cout << "[Збій] Сервер недоступний (таймаут). Кидаємо виняток.\n";
            throw std::runtime_error("Network timeout on auth endpoint");
        }

        session_token_ = "TOKEN_SECURE_ABC_123_XYZ";
        std::cout << "[Успіх] Авторизацію пройдено, токен отримано!\n";
    }

public:
    void send_request(const std::string& payload) {
        // Якщо ініціалізатор кидає виняток, стан auth_flag_ скидається назад!
        std::call_once(auth_flag_, &ResilientNetworkClient::authenticate_rpc, this);
        
        std::cout << "Відправка даних '" << payload << "' з токеном " << session_token_ << "\n";
    }
};

int main() {
    ResilientNetworkClient client;

    // Перший запит зазнає невдачі через збій мережі
    try {
        client.send_request("Payload #1");
    } catch (const std::exception& e) {
        std::cout << "Клієнт перехопив помилку: " << e.what() << "\n";
    }

    // Другий запит успішно повторює ініціалізацію завдяки транзакційному скиданню прапорця!
    try {
        std::cout << "\nПовторна спроба відправки...\n";
        client.send_request("Payload #2");
    } catch (const std::exception& e) {
        std::cout << "Несподівана помилка: " << e.what() << "\n";
    }

    return 0;
}
