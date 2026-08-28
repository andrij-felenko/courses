template <typename DerivedState>
class StateBase {
public:
    template <typename Event>
    void handle_event(const Event& event) {
        DerivedState& self = *static_cast<DerivedState*>(this);
        self.on_event(event);
    }
};

struct ConnectEvent {};

class DisconnectedState : public StateBase<DisconnectedState> {
public:
    void on_event(const ConnectEvent&) {
        std::cout << "Transitioning from Disconnected to Connecting\n";
    }
};
