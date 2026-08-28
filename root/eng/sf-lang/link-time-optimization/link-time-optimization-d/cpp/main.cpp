// Поліморфізм через віртуальні класи (C++)
class IHandler {
public:
    virtual ~IHandler() = default;
    virtual int handle(int event) const = 0;
};

class FastHandler final : public IHandler {
private:
    int multiplier_;
public:
    explicit FastHandler(int multiplier) noexcept : multiplier_(multiplier) {}
    int handle(int event) const noexcept override {
        return event * multiplier_;
    }
};

int dispatch_event(const IHandler& handler, int event) {
    // Віртуальний виклик через vtable
    return handler.handle(event);
}
