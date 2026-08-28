// Свій контракт: рівно те, що потрібно системі.
// Жодних типів вендора тут немає — це і є шов.
class MessageQueue {
public:
    virtual ~MessageQueue() = default;

    virtual bool publish(const std::string& topic,
                         const std::string& payload) = 0;

    // повертає false, якщо за timeout нічого не прийшло
    virtual bool consume(std::string& out, int timeout_ms) = 0;
};
