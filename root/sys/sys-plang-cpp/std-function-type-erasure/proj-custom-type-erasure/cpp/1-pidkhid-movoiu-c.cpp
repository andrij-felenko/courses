#include <iostream>
#include <memory>
#include <string>
#include <utility>

// Ідіоматичний еквівалент C++: Використання RAII та поліморфного класу
class CppEventHandler {
public:
    virtual ~CppEventHandler() = default;
    virtual void invoke(int event_id) = 0;
};

class SimpleHandler : public CppEventHandler {
public:
    void invoke(int event_id) override {
        std::cout << "[C++ Simple] Received event: " << event_id << '\n';
    }
};

class LoggerHandler : public CppEventHandler {
private:
    std::string prefix_;
    int counter_{0};

public:
    explicit LoggerHandler(std::string prefix) : prefix_(std::move(prefix)) {}

    void invoke(int event_id) override {
        counter_++;
        std::cout << "[C++ Logger " << prefix_ << " #" << counter_ << "] Event ID: " << event_id << '\n';
    }
};

int main() {
    std::unique_ptr<CppEventHandler> h1 = std::make_unique<SimpleHandler>();
    std::unique_ptr<CppEventHandler> h2 = std::make_unique<LoggerHandler>("NetworkSubsystem");

    h1->invoke(101);
    h2->invoke(202);
    h2->invoke(203);
}
