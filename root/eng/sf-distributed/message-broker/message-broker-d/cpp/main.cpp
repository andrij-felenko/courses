#include <iostream>
#include <string>
#include <queue>
#include <optional>
#include <memory>

namespace broker {

struct Message {
    uint64_t id;
    std::string key;
    std::string payload;
    uint32_t attempts{0};
};

class Queue {
public:
    explicit Queue(std::string name) : name_(std::move(name)) {}

    bool push(Message msg) {
        if (storage_.size() >= 64) return false;
        storage_.push(std::move(msg));
        return true;
    }

    std::optional<Message> pop() {
        if (storage_.empty()) return std::nullopt;
        Message msg = std::move(storage_.front());
        storage_.pop();
        return msg;
    }

    [[nodiscard]] size_t size() const noexcept { return storage_.size(); }
    [[nodiscard]] const std::string& name() const noexcept { return name_; }

private:
    std::string name_;
    std::queue<Message> storage_;
};

class Consumer {
public:
    Consumer(uint32_t id, int prefetch) : id_(id), prefetch_credits_(prefetch) {}

    [[nodiscard]] uint32_t id() const noexcept { return id_; }
    [[nodiscard]] int credits() const noexcept { return prefetch_credits_; }
    [[nodiscard]] bool can_receive() const noexcept { return prefetch_credits_ > 0 && !active_lease_.has_value(); }

    void record_dispatch(uint64_t tag, Message msg) {
        active_lease_ = {tag, std::move(msg)};
        --prefetch_credits_;
    }

    std::optional<Message> ack(uint64_t tag) {
        if (active_lease_ && active_lease_->first == tag) {
            Message completed = std::move(active_lease_->second);
            active_lease_.reset();
            ++prefetch_credits_;
            return completed;
        }
        return std::nullopt;
    }

private:
    uint32_t id_;
    int prefetch_credits_;
    std::optional<std::pair<uint64_t, Message>> active_lease_;
};

} // namespace broker
