#include <iostream>
#include <memory>
#include <vector>
#include <cstdint>

class PacketReceiver {
public:
    explicit PacketReceiver(int socket_fd) : m_socket_fd(socket_fd) {
        // Конструктор базового класу кличе допоміжний метод конфігурації
        setup_subsystem();
    }

    virtual ~PacketReceiver() = default;

    // Контракт обробки корисного навантаження
    virtual void process_payload(const uint8_t* data, std::size_t len) = 0;

private:
    void setup_subsystem() {
        const uint8_t handshake[4] = {0xAA, 0x55, 0x01, 0x00};
        // НЕБЕЗПЕКА: непрямий віртуальний виклик під час виконання конструктора предка!
        process_payload(handshake, sizeof(handshake));
    }

    int m_socket_fd;
};

class TelemetryReceiver : public PacketReceiver {
public:
    explicit TelemetryReceiver(int socket_fd) : PacketReceiver(socket_fd) {}

    void process_payload(const uint8_t* data, std::size_t len) override {
        std::cout << "Успішна обробка телеметрії, розмір: " << len << " байтів\n";
    }
};
