#include <iostream>
#include <variant>
#include <string>
#include <string_view>
#include <vector>
#include <cstdint>
#include <type_traits>

// 1. Структура Overload успадковує всі передані функціональні об'єкти (лямбди)
template <typename... Ts>
struct Overload : Ts... {
    // Втягуємо всі operator() з кожного базового типу в область видимості Overload:
    using Ts::operator()...;
};

// 2. Deduction Guide для автоматичного виведення типів аргументів шаблону (CTAD):
template <typename... Ts>
Overload(Ts...) -> Overload<Ts...>;

// Допоміжний трейт для статичної перевірки вичерпності (Exhaustiveness Check)
template <typename T>
struct always_false : std::false_type {};

// Приклад предметної області: події мережевого стека
struct ConnectionEvent {
    std::string peer_ip;
    uint16_t port;
};

struct DataPacketEvent {
    std::vector<uint8_t> payload;
    bool is_encrypted;
};

struct HeartbeatEvent {
    uint64_t sequence_number;
};

struct DisconnectEvent {
    std::string reason;
};

// Тип суми для всіх можливих мережевих повідомлень:
using NetworkMessage = std::variant<ConnectionEvent, DataPacketEvent, HeartbeatEvent, DisconnectEvent>;

// Функція диспетчеризації повідомлень
void handle_network_message(const NetworkMessage& message) {
    std::visit(Overload{
        [](const ConnectionEvent& ev) {
            std::cout << "[З'єднання] Вузол " << ev.peer_ip << ":" << ev.port << " підключено.\n";
        },
        [](const DataPacketEvent& ev) {
            std::cout << "[Дані] Отримано пакет на " << ev.payload.size() 
                      << " байтів (шифрування: " << (ev.is_encrypted ? "так" : "ні") << ").\n";
        },
        [](const HeartbeatEvent& ev) {
            std::cout << "[Heartbeat] Пульс #" << ev.sequence_number << " підтверджено.\n";
        },
        [](const DisconnectEvent& ev) {
            std::cout << "[Відключення] Причина: " << ev.reason << '\n';
        }
    }, message);
}
