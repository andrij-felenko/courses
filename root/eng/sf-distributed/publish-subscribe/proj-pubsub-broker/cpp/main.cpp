#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <memory>
#include <mutex>
#include <queue>
#include <thread>
#include <chrono>
#include <functional>
#include <sstream>
#include <atomic>
#include <optional>

// Повідомлення в системі Pub/Sub
struct Message {
    std::string topic;
    std::string payload;
    uint64_t sequence_id;
};

// Політика поведінки при переповненні буфера
enum class OverflowPolicy {
    DropOldest,
    RejectNewest
};

// Черга підписника з обмеженою ємністю
class SubscriberQueue {
public:
    SubscriberQueue(std::string id, size_t capacity, OverflowPolicy policy)
        : id_(std::move(id)), capacity_(capacity), policy_(policy), dropped_count_(0) {}

    bool push(const Message& msg) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (queue_.size() >= capacity_) {
            if (policy_ == OverflowPolicy::DropOldest) {
                queue_.pop();
                dropped_count_++;
                queue_.push(msg);
                return true;
            } else {
                dropped_count_++;
                return false;
            }
        }
        queue_.push(msg);
        return true;
    }

    std::optional<Message> pop() {
        std::lock_guard<std::mutex> lock(mutex_);
        if (queue_.empty()) {
            return std::nullopt;
        }
        Message msg = queue_.front();
        queue_.pop();
        return msg;
    }

    std::string id() const { return id_; }
    size_t dropped_count() const { return dropped_count_.load(); }
    size_t size() {
        std::lock_guard<std::mutex> lock(mutex_);
        return queue_.size();
    }

private:
    std::string id_;
    size_t capacity_;
    OverflowPolicy policy_;
    std::queue<Message> queue_;
    std::atomic<size_t> dropped_count_;
    std::mutex mutex_;
};

// Вузол дерева префіксів тем (Topic Trie)
class TrieNode {
public:
    std::unordered_map<std::string, std::unique_ptr<TrieNode>> children;
    std::vector<std::shared_ptr<SubscriberQueue>> subscribers;

    // Рекурсивне додавання підписки на шаблон теми
    void insert(const std::vector<std::string>& tokens, size_t index, 
                std::shared_ptr<SubscriberQueue> sub) {
        if (index == tokens.size()) {
            subscribers.push_back(sub);
            return;
        }

        const std::string& token = tokens[index];
        if (children.find(token) == children.end()) {
            children[token] = std::make_unique<TrieNode>();
        }
        children[token]->insert(tokens, index + 1, sub);
    }

    // Рекурсивний пошук усіх підписників, що відповідають опублікованій темі
    void match(const std::vector<std::string>& tokens, size_t index,
               std::vector<std::shared_ptr<SubscriberQueue>>& result) const {
        // Якщо на цьому рівні є підписка на всі наступні рівні ('>')
        auto multi_it = children.find(">");
        if (multi_it != children.end()) {
            for (const auto& sub : multi_it->second->subscribers) {
                result.push_back(sub);
            }
        }

        if (index == tokens.size()) {
            for (const auto& sub : subscribers) {
                result.push_back(sub);
            }
            return;
        }

        const std::string& token = tokens[index];

        // 1. Точний збіг токена
        auto exact_it = children.find(token);
        if (exact_it != children.end()) {
            exact_it->second->match(tokens, index + 1, result);
        }

        // 2. Однорівнева маска ('*')
        auto single_it = children.find("*");
        if (single_it != children.end()) {
            single_it->second->match(tokens, index + 1, result);
        }
    }
};

// Центральний Pub/Sub Брокер
class PubSubBroker {
public:
    PubSubBroker() : seq_counter_(0), root_(std::make_unique<TrieNode>()) {}

    // Допоміжна функція розбиття теми на токени
    static std::vector<std::string> tokenize(std::string_view topic) {
        std::vector<std::string> tokens;
        size_t start = 0;
        while (start < topic.size()) {
            size_t end = topic.find('/', start);
            if (end == std::string_view::npos) {
                tokens.emplace_back(topic.substr(start));
                break;
            }
            tokens.emplace_back(topic.substr(start, end - start));
            start = end + 1;
        }
        return tokens;
    }

    // Підписка на тему
    void subscribe(std::string_view pattern, std::shared_ptr<SubscriberQueue> sub) {
        std::lock_guard<std::mutex> lock(trie_mutex_);
        auto tokens = tokenize(pattern);
        root_->insert(tokens, 0, sub);
    }

    // Публікація повідомлення в тему
    size_t publish(std::string_view topic, std::string payload) {
        Message msg;
        msg.topic = std::string(topic);
        msg.payload = std::move(payload);
        msg.sequence_id = ++seq_counter_;

        std::vector<std::shared_ptr<SubscriberQueue>> targets;
        {
            std::lock_guard<std::mutex> lock(trie_mutex_);
            auto tokens = tokenize(topic);
            root_->match(tokens, 0, targets);
        }

        // Доставка в буфери знайдених підписників (fan-out)
        size_t delivered = 0;
        for (auto& queue : targets) {
            if (queue->push(msg)) {
                delivered++;
            }
        }
        return delivered;
    }

private:
    std::atomic<uint64_t> seq_counter_;
    std::unique_ptr<TrieNode> root_;
    std::mutex trie_mutex_;
};

int main() {
    PubSubBroker broker;

    // Створюємо два підписники з обмеженими буферами
    // Клієнт 1: Швидкий аналітик з буфером 1000
    auto fast_sub = std::make_shared<SubscriberQueue>("FastAnalytics", 1000, OverflowPolicy::DropOldest);
    // Клієнт 2: Повільний експортер у PDF з малим буфером 5
    auto slow_sub = std::make_shared<SubscriberQueue>("SlowPDFExporter", 5, OverflowPolicy::DropOldest);

    // Підписка за шаблонами
    broker.subscribe("orders/eu/*", fast_sub); // Ловить orders/eu/ua, orders/eu/de
    broker.subscribe("orders/>", slow_sub);    // Ловить orders/eu/ua, orders/us/ny/vip тощо

    std::cout << "[Broker] Запуск демонстрації публікації...\n";

    // Видавець надсилає 20 повідомлень поспіль
    for (int i = 1; i <= 20; ++i) {
        std::string payload = "OrderData_#" + std::to_string(i);
        broker.publish("orders/eu/ua", payload);
    }

    std::cout << "\n[Результати доставки]:\n";
    std::cout << "FastAnalytics черга: " << fast_sub->size() 
              << " msg, скинуто: " << fast_sub->dropped_count() << "\n";
    std::cout << "SlowPDFExporter черга: " << slow_sub->size() 
              << " msg (макс 5), скинуто через повільність: " << slow_sub->dropped_count() << "\n";

    // Демонстрація вичитування
    std::cout << "\n[SlowPDFExporter] Зміст збережених повідомлень (найновіші):\n";
    while (auto msg = slow_sub->pop()) {
        std::cout << "  -> seq=" << msg->sequence_id << " payload=" << msg->payload << "\n";
    }

    return 0;
}
