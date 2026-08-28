#include <variant>
#include <string>
#include <iostream>

// Опис станів системи
struct DisconnectedState {};

struct ConnectingState {
    std::string endpoint_address;
    int attempt_count;
};

struct ConnectedState {
    uint32_t session_id;
    size_t bytes_transferred;
};

struct ErrorState {
    std::string error_message;
};

using State = std::variant<DisconnectedState, ConnectingState, ConnectedState, ErrorState>;

// Опис подій системи
struct ConnectEvent {
    std::string address;
};

struct ConnectedSuccessEvent {
    uint32_t session_id;
};

struct DataPacketEvent {
    size_t packet_size;
};

struct ErrorOccurredEvent {
    std::string message;
};

using Event = std::variant<ConnectEvent, ConnectedSuccessEvent, DataPacketEvent, ErrorOccurredEvent>;

// Двовимірний відвідувач для реакції на пару (State, Event)
struct TransitionHandler {

    // 1. З DisconnectedState + ConnectEvent -> ConnectingState
    State operator()(DisconnectedState, const ConnectEvent& evt) const {
        std::cout << "[FSM] Спроба підключення до: " << evt.address << "\n";
        return ConnectingState{evt.address, 1};
    }

    // 2. З ConnectingState + ConnectedSuccessEvent -> ConnectedState
    State operator()(const ConnectingState& st, const ConnectedSuccessEvent& evt) const {
        std::cout << "[FSM] Успішно підключено до " << st.endpoint_address 
                  << ", session_id: " << evt.session_id << "\n";
        return ConnectedState{evt.session_id, 0};
    }

    // 3. З ConnectedState + DataPacketEvent -> ConnectedState (оновлення перерахованих байтів)
    State operator()(ConnectedState st, const DataPacketEvent& evt) const {
        st.bytes_transferred += evt.packet_size;
        std::cout << "[FSM] Отримано пакет " << evt.packet_size 
                  << " байт. Всього передано: " << st.bytes_transferred << "\n";
        return st;
    }

    // 4. Будь-який стан + ErrorOccurredEvent -> ErrorState
    template <typename CurrentState>
    State operator()(const CurrentState&, const ErrorOccurredEvent& evt) const {
        std::cout << "[FSM] Критична помилка: " << evt.message << "\n";
        return ErrorState{evt.message};
    }

    // 5. Непідтримувані переходи (fallback rule)
    template <typename CurrentState, typename IncomingEvent>
    State operator()(const CurrentState& st, const IncomingEvent&) const {
        std::cout << "[FSM] Ігнорування невалідної події для даного стану.\n";
        return st;
    }
};

class NetworkSocketFSM {
    State current_state_;

public:
    NetworkSocketFSM() : current_state_(DisconnectedState{}) {}

    void dispatch(const Event& event) {
        // Статична двовимірна диспетчеризація пари (current_state_, event)
        current_state_ = std::visit(TransitionHandler{}, current_state_, event);
    }

    void print_status() const {
        std::visit(overloaded{
            [](DisconnectedState) { std::cout << "Статус: Відключено\n"; },
            [](const ConnectingState& st) { std::cout << "Статус: В процесі підключення до " << st.endpoint_address << "\n"; },
            [](const ConnectedState& st) { std::cout << "Статус: Підключено (сесія " << st.session_id << ")\n"; },
            [](const ErrorState& st) { std::cout << "Статус: Помилка (" << st.error_message << ")\n"; }
        }, current_state_);
    }
};

int main() {
    NetworkSocketFSM fsm;
    fsm.print_status();

    // Симуляція життєвого циклу мережевого з'єднання
    fsm.dispatch(ConnectEvent{"192.168.1.100:8080"});
    fsm.print_status();

    fsm.dispatch(ConnectedSuccessEvent{42});
    fsm.print_status();

    fsm.dispatch(DataPacketEvent{512});
    fsm.dispatch(DataPacketEvent{1024});
    fsm.print_status();

    fsm.dispatch(ErrorOccurredEvent{"Мережевий таймаут"});
    fsm.print_status();
}
