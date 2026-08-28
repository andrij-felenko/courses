#include <iostream>
#include <variant>
#include <string>

// Стани з'єднання:
struct DisconnectedState {};
struct ConnectingState { int retry_count{0}; };
struct ConnectedState { std::string session_id; };

using State = std::variant<DisconnectedState, ConnectingState, ConnectedState>;

// Вхідні події автомата:
struct ConnectCommand { std::string target_host; };
struct HandshakeOk { std::string session_id; };
struct NetworkError { std::string message; };
struct DisconnectCommand {};

using Event = std::variant<ConnectCommand, HandshakeOk, NetworkError, DisconnectCommand>;

// Функція переходу між станами:
State on_event(State current_state, Event event) {
    return std::visit(Overload{
        // 1. З Disconnected реагуємо на команду підключення:
        [](DisconnectedState, ConnectCommand cmd) -> State {
            std::cout << "Перехід: Disconnected -> Connecting до " << cmd.target_host << '\n';
            return ConnectingState{1};
        },
        // 2. З Connecting при успішному рукостисканні переходимо в Connected:
        [](ConnectingState, HandshakeOk ok) -> State {
            std::cout << "Перехід: Connecting -> Connected (ID: " << ok.session_id << ")\n";
            return ConnectedState{ok.session_id};
        },
        // 3. З Connecting при помилці повертаємося в Disconnected:
        [](ConnectingState st, NetworkError err) -> State {
            std::cout << "Помилка зв'язку (" << err.message << "), спроба #" << st.retry_count << '\n';
            return DisconnectedState{};
        },
        // 4. З Connected на команду відключення переходимо в Disconnected:
        [](ConnectedState, DisconnectCommand) -> State {
            std::cout << "Перехід: Connected -> Disconnected\n";
            return DisconnectedState{};
        },
        // 5. Усі інші комбінації стану та події ігноруються (стан не змінюється):
        [](auto state, auto) -> State {
            std::cout << "Ігнорування недоречної події для поточного стану.\n";
            return state;
        }
    }, current_state, event);
}

int main() {
    State current = DisconnectedState{};

    current = on_event(current, ConnectCommand{"api.service.internal"});
    current = on_event(current, HandshakeOk{"sess-9988"});
    current = on_event(current, ConnectCommand{"інший_сервер"}); // ігнорується
    current = on_event(current, DisconnectCommand{});

    return 0;
}
