#include <memory>
#include <iostream>

class NetworkManager : public std::enable_shared_from_this<NetworkManager> {
public:
    void send_request() {
        // Захоплюємо std::weak_ptr, щоб уникнути висячого this
        auto callback = [weak_self = weak_from_this()](std::string response) {
            if (auto self = weak_self.lock()) {
                self->handle_response(response);
            } else {
                std::cout << "Об'єкт NetworkManager уже знищено, ігноруємо відповідь\n";
            }
        };
        // Реєстрація callback у мережевому циклі...
    }

    void handle_response(const std::string& r) {
        std::cout << "Отримано: " << r << '\n';
    }
};
