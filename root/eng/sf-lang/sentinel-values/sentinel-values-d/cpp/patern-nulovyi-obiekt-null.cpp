#include <iostream>
#include <memory>
#include <string_view>

class IEventSink {
public:
    virtual ~IEventSink() = default;
    virtual void on_event(std::string_view text) = 0;
};

class StdoutSink : public IEventSink {
public:
    void on_event(std::string_view text) override {
        std::cout << "[EVENT]: " << text << "\n";
    }
};

class NullEventSink : public IEventSink {
public:
    void on_event(std::string_view /*text*/) noexcept override {
        // Нейтральна поведінка без побічних ефектів
    }
};

class EventManager {
    std::shared_ptr<IEventSink> sink_;
public:
    explicit EventManager(std::shared_ptr<IEventSink> sink)
        : sink_(sink ? std::move(sink) : std::make_shared<NullEventSink>()) {}

    void trigger(std::string_view message) {
        sink_->on_event(message); // Безпечний виклик без if (sink_)
    }
};

int main() {
    EventManager mgr(nullptr); // Передано nullptr — використовується NullEventSink
    mgr.trigger("Системна подія");
    return 0;
}
