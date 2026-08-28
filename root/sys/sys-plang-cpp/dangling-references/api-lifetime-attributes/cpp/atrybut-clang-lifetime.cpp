#include <vector>
#include <string_view>

struct EventSink {
    std::vector<std::string_view> subscribers;

    // Вказує, що метод зберігає view всередині об'єкта 'this'
    void subscribe(std::string_view sv [[clang::lifetime_capture_by(this)]]) {
        subscribers.push_back(sv);
    }
};

void register_events(EventSink& sink) {
    std::string temp_event = "on_network_timeout";
    sink.subscribe(temp_event); 
    // warning: object backing 'temp_event' captured by 'sink' will be destroyed on scope exit, leaving dangling view in 'sink'
}
