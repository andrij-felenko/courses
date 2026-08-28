#include <iostream>
#include <memory>
#include <vector>
#include <cstdint>

class PacketReceiver {
public:
    virtual ~PacketReceiver() = default;

    // Контракт чистої віртуальної поведінки
    virtual void process_payload(const uint8_t* data, std::size_t len) = 0;

    // Каркасний метод запуску (NVI)
    void start_receiver() {
        const uint8_t handshake[4] = {0xAA, 0x55, 0x01, 0x00};
        // Безпечно: цей метод викликається лише після повного конструювання об'єкта
        process_payload(handshake, sizeof(handshake));
    }

protected:
    // Конструктор доступний лише похідним класам
    explicit PacketReceiver(int socket_fd) : m_socket_fd(socket_fd) {}

private:
    int m_socket_fd;
};

class TelemetryReceiver final : public PacketReceiver {
public:
    // Статична фабрика повертає повністю ініціалізований розумний покажчик
    static std::unique_ptr<TelemetryReceiver> create(int socket_fd) {
        // Створюємо об'єкт: виконуються конструктори PacketReceiver і TelemetryReceiver
        auto instance = std::unique_ptr<TelemetryReceiver>(new TelemetryReceiver(socket_fd));

        // Тепер vptr гарантовано вказує на vtable for TelemetryReceiver
        instance->start_receiver();
        return instance;
    }

    void process_payload(const uint8_t* data, std::size_t len) override {
        std::cout << "Телеметрію розібрано, розмір: " << len << " байтів\n";
    }

private:
    // Конструктор приватний: створення лише через create()
    explicit TelemetryReceiver(int socket_fd) : PacketReceiver(socket_fd) {}
};
