#include <iostream>

template <typename T>
class BaseProcessor {
public:
    void initialize_hardware() {
        std::cout << "BaseProcessor: Hardware initialized\n";
    }

protected:
    int status_code = 200;
};

template <typename T>
class NetworkProcessor : public BaseProcessor<T> {
public:
    void process_packet(const T& packet) {
        // ПОМИЛКА КОМПІЛЯЦІЇ під час Фази 1 на GCC / Clang / MSVC /permissive-:
        // 'initialize_hardware' was not declared in this scope
        initialize_hardware();

        // ПОМИЛКА КОМПІЛЯЦІЇ під час Фази 1:
        // 'status_code' was not declared in this scope
        std::cout << "Packet status: " << status_code << "\n";
    }
};
