#include <variant>
#include <cstdint>

struct PacketData { uint8_t payload[16]; };
struct PacketError { uint32_t error_code; };
struct PacketPing { uint32_t sequence_id; };

using Event = std::variant<PacketData, PacketError, PacketPing>;

// Патерн Overload для зіставлення типів
template<class... Ts> struct Overload : Ts... { using Ts::operator()...; };
template<class... Ts> Overload(Ts...) -> Overload<Ts...>;

void dispatch_event(const Event& ev) {
    std::visit(Overload{
        [](const PacketData& d) { /* Обробка даних */ (void)d; },
        [](const PacketError& e) { /* Обробка помилки */ (void)e; },
        [](const PacketPing& p) { /* Відповідь на Ping */ (void)p; }
    }, ev);
}
