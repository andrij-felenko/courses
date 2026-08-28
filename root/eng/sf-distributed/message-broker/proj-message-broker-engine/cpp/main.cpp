#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <memory>
#include <queue>
#include <chrono>
#include <optional>
#include <sstream>

namespace message_broker {

constexpr uint32_t MAX_DELIVERY_ATTEMPTS = 3;
constexpr std::chrono::seconds LEASE_TIMEOUT{5};

struct Message {
    uint64_t id;
    std::string routing_key;
    std::string payload;
    uint32_t delivery_count{0};
};

class Queue {
public:
    explicit Queue(std::string name, bool is_dlq = false)
        : name_(std::move(name)), is_dlq_(is_dlq) {}

    void push(Message msg) {
        storage_.push(std::move(msg));
    }

    std::optional<Message> pop() {
        if (storage_.empty()) return std::nullopt;
        Message front = std::move(storage_.front());
        storage_.pop();
        return front;
    }

    [[nodiscard]] size_t size() const noexcept { return storage_.size(); }
    [[nodiscard]] const std::string& name() const noexcept { return name_; }

private:
    std::string name_;
    bool is_dlq_;
    std::queue<Message> storage_;
};

class TopicNode {
public:
    explicit TopicNode(std::string token = "") : token_(std::move(token)) {}

    void add_binding(const std::shared_ptr<Queue>& q) {
        bound_queues_.push_back(q);
    }

    TopicNode* get_or_create_child(std::string_view token) {
        auto it = children_.find(std::string(token));
        if (it != children_.end()) {
            return it->second.get();
        }
        auto node = std::make_unique<TopicNode>(std::string(token));
        TopicNode* raw_ptr = node.get();
        children_.emplace(std::string(token), std::move(node));
        return raw_ptr;
    }

    void match(const std::vector<std::string>& tokens, size_t idx,
               std::vector<std::shared_ptr<Queue>>& matched) const {
        if (idx == tokens.size()) {
            for (const auto& q : bound_queues_) {
                matched.push_back(q);
            }
        }

        for (const auto& [child_token, child_node] : children_) {
            if (child_token == "#") {
                for (size_t k = idx; k <= tokens.size(); ++k) {
                    child_node->match(tokens, k, matched);
                }
            } else if (idx < tokens.size() && (child_token == "*" || child_token == tokens[idx])) {
                child_node->match(tokens, idx + 1, matched);
            }
        }
    }

private:
    std::string token_;
    std::vector<std::shared_ptr<Queue>> bound_queues_;
    std::unordered_map<std::string, std::unique_ptr<TopicNode>> children_;
};

struct InFlightEntry {
    uint64_t delivery_tag;
    Message message;
    std::chrono::steady_clock::time_point dispatched_at;
};

class Consumer {
public:
    Consumer(uint32_t id, int prefetch) : id_(id), prefetch_credits_(prefetch) {}

    [[nodiscard]] uint32_t id() const noexcept { return id_; }
    [[nodiscard]] int credits() const noexcept { return prefetch_credits_; }

    bool can_receive() const noexcept { return prefetch_credits_ > 0; }

    void record_dispatch(uint64_t tag, Message msg) {
        in_flight_.emplace(tag, InFlightEntry{tag, std::move(msg), std::chrono::steady_clock::now()});
        --prefetch_credits_;
    }

    std::optional<Message> complete(uint64_t tag) {
        auto it = in_flight_.find(tag);
        if (it == in_flight_.end()) return std::nullopt;
        Message msg = std::move(it->second.message);
        in_flight_.erase(it);
        ++prefetch_credits_;
        return msg;
    }

    std::vector<uint64_t> collect_expired_tags(std::chrono::seconds timeout) const {
        std::vector<uint64_t> expired;
        auto now = std::chrono::steady_clock::now();
        for (const auto& [tag, entry] : in_flight_) {
            if (now - entry.dispatched_at >= timeout) {
                expired.push_back(tag);
            }
        }
        return expired;
    }

private:
    uint32_t id_;
    int prefetch_credits_;
    std::unordered_map<uint64_t, InFlightEntry> in_flight_;
};

class BrokerEngine {
public:
    BrokerEngine()
        : root_(std::make_unique<TopicNode>()),
          dlq_(std::make_shared<Queue>("dead_letter_queue", true)) {}

    void bind(const std::string& pattern, const std::shared_ptr<Queue>& q) {
        auto tokens = split_key(pattern);
        TopicNode* curr = root_.get();
        for (const auto& tok : tokens) {
            curr = curr->get_or_create_child(tok);
        }
        curr->add_binding(q);
    }

    void publish(const std::string& routing_key, const std::string& payload) {
        auto tokens = split_key(routing_key);
        std::vector<std::shared_ptr<Queue>> matched_queues;
        root_->match(tokens, 0, matched_queues);

        Message msg{next_msg_id_++, routing_key, payload, 0};
        for (const auto& q : matched_queues) {
            q->push(msg);
            std::cout << "[BROKER] Повідомлення '" << payload << "' (Key: "
                      << routing_key << ") додано в чергу '" << q->name() << "'\n";
        }
    }

    bool dispatch(const std::shared_ptr<Queue>& q, Consumer& consumer) {
        if (!consumer.can_receive()) return false;

        auto opt_msg = q->pop();
        if (!opt_msg.has_value()) return false;

        Message msg = std::move(*opt_msg);
        ++msg.delivery_count;
        uint64_t tag = ++next_delivery_tag_;

        consumer.record_dispatch(tag, msg);
        std::cout << "[DISPATCH] Споживачу #" << consumer.id() << " видано msg_id="
                  << msg.id << " (Tag: " << tag << ", Спроба: " << msg.delivery_count
                  << "). Залишок кредитів: " << consumer.credits() << "\n";
        return true;
    }

    void ack(Consumer& consumer, uint64_t tag) {
        if (consumer.complete(tag).has_value()) {
            std::cout << "[ACK] Підтверджено Tag: " << tag << " від споживача #"
                      << consumer.id() << ". Кредити: " << consumer.credits() << "\n";
        }
    }

    void nack(const std::shared_ptr<Queue>& q, Consumer& consumer, uint64_t tag, bool requeue) {
        auto opt_msg = consumer.complete(tag);
        if (!opt_msg.has_value()) return;

        Message msg = std::move(*opt_msg);
        if (requeue && msg.delivery_count < MAX_DELIVERY_ATTEMPTS) {
            q->push(msg);
            std::cout << "[NACK] Tag: " << tag << " повернено в чергу '" << q->name()
                      << "' (Спроба " << msg.delivery_count << "/" << MAX_DELIVERY_ATTEMPTS << ")\n";
        } else {
            dlq_->push(msg);
            std::cout << "[DLQ] Tag: " << tag << " перевищив ліміт спроб! Скеровано в DLQ\n";
        }
    }

    void check_timeouts(const std::shared_ptr<Queue>& q, Consumer& consumer) {
        auto expired_tags = consumer.collect_expired_tags(LEASE_TIMEOUT);
        for (uint64_t tag : expired_tags) {
            std::cout << "[TIMEOUT] Оренда для Tag: " << tag << " минула!\n";
            nack(q, consumer, tag, true);
        }
    }

    [[nodiscard]] std::shared_ptr<Queue> dlq() const noexcept { return dlq_; }

private:
    static std::vector<std::string> split_key(std::string_view key) {
        std::vector<std::string> tokens;
        std::stringstream ss{std::string(key)};
        std::string item;
        while (std::getline(ss, item, '.')) {
            if (!item.empty()) tokens.push_back(std::move(item));
        }
        return tokens;
    }

    std::unique_ptr<TopicNode> root_;
    std::shared_ptr<Queue> dlq_;
    uint64_t next_msg_id_{1};
    uint64_t next_delivery_tag_{100};
};

} // namespace message_broker
