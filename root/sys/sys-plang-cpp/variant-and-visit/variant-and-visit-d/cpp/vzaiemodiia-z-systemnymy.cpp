#include <variant>
#include <cstdint>
#include <cstring>
#include <iostream>

struct Header {
    uint8_t packet_type;
    uint16_t payload_len;
};

struct PingPacket {
    Header head;
    uint64_t timestamp;
};

struct DataPacket {
    Header head;
    uint32_t sequence_id;
    char payload[64];
};

using NetworkPacket = std::variant<PingPacket, DataPacket>;

void send_packet_over_network(const NetworkPacket& pkt) {
    std::visit([](const auto& concrete_pkt) {
        // Отримання сирого вказівника на пам'ять об'єкта для виклику POSIX send()
        const void* raw_bytes = static_cast<const void*>(&concrete_pkt);
        size_t bytes_len = sizeof(concrete_pkt);
        
        // Симуляція виклику POSIX send(socket_fd, raw_bytes, bytes_len, 0)
        std::cout << "[Network] Відправка пакета розміром: " << bytes_len << " байт\n";
    }, pkt);
}
