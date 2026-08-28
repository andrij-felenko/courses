class Subscription {
public:
    Subscription() = default;
    Subscription(EventBus& bus, EventBus::Id id) : bus_(&bus), id_(id) {}

    Subscription(const Subscription&) = delete;
    Subscription& operator=(const Subscription&) = delete;

    Subscription(Subscription&& other) noexcept
        : bus_(other.bus_), id_(other.id_) { other.bus_ = nullptr; }

    Subscription& operator=(Subscription&& other) noexcept {
        if (this != &other) {
            reset();
            bus_ = other.bus_;
            id_  = other.id_;
            other.bus_ = nullptr;
        }
        return *this;
    }

    ~Subscription() { reset(); }

    void reset() {
        if (bus_) { bus_->unsubscribe(id_); bus_ = nullptr; }
    }

private:
    EventBus* bus_ = nullptr;
    EventBus::Id id_ = 0;
};

inline Subscription EventBus::connect(Handler h) {
    return Subscription(*this, subscribe(std::move(h)));
}
