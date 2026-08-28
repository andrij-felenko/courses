struct ConnectionState {
    virtual void handle_packet(const char* data) = 0;
    virtual ~ConnectionState() = default;
};

struct HandshakeState : ConnectionState {
    void handle_packet(const char* data) override {
        std::cout << "Обробка рукостискання: " << data << '\n';
    }
};

struct EstablishedState : ConnectionState {
    void handle_packet(const char* data) override {
        std::cout << "Обробка даних сесії: " << data << '\n';
    }
};

class Connection {
    alignas(HandshakeState) alignas(EstablishedState)
    std::byte state_buffer_[sizeof(EstablishedState)];
    
    ConnectionState* current_state() noexcept {
        return std::launder(reinterpret_cast<ConnectionState*>(state_buffer_));
    }

public:
    Connection() {
        ::new (static_cast<void*>(state_buffer_)) HandshakeState();
    }

    ~Connection() {
        current_state()->~ConnectionState();
    }

    void transition_to_established() {
        current_state()->~ConnectionState();
        ::new (static_cast<void*>(state_buffer_)) EstablishedState();
    }

    void process(const char* payload) {
        current_state()->handle_packet(payload);
    }
};
