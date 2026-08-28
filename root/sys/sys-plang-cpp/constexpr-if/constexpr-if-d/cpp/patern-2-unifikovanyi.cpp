#include <variant>
#include <string>
#include <iostream>

struct PacketHeader { uint32_t id; };
struct PayloadData { std::string payload; };
struct DisconnectSignal { int reason_code; };

using NetworkMessage = std::variant<PacketHeader, PayloadData, DisconnectSignal>;

void handle_network_message(const NetworkMessage& msg) {
    std::visit([](const auto& item) {
        using T = std::decay_t<decltype(item)>;

        if constexpr (std::is_same_v<T, PacketHeader>) {
            std::cout << "Отримано заголовок пакету ID: " << item.id << "\n";
        } else if constexpr (std::is_same_v<T, PayloadData>) {
            std::cout << "Отримано корисне навантаження: " << item.payload << "\n";
        } else if constexpr (std::is_same_v<T, DisconnectSignal>) {
            std::cout << "Сигнал роз'єднання, код: " << item.reason_code << "\n";
        } else {
            static_assert(dependent_false<T>, "Не всі варіанти NetworkMessage покрито обробником!");
        }
    }, msg);
}
