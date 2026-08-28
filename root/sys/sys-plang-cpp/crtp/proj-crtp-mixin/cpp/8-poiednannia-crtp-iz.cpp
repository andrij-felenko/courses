#include <variant>
#include <vector>

using PacketVariant = std::variant<OrderSingle>;

void process_packets_statically(const std::vector<PacketVariant>& packets, uint8_t* out_buffer) {
    for (const auto& packet : packets) {
        std::visit([out_buffer](const auto& p) {
            if (p.validate()) {
                p.serialize_to(out_buffer);
            }
        }, packet);
    }
}
