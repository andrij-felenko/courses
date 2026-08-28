#include <atomic>
#include <memory>
#include <optional>

template <typename T>
class TreiberStack {
public:
    TreiberStack() : head_(nullptr) {}

    ~TreiberStack() {
        Node* current = head_.load(std::memory_order_relaxed);
        while (current != nullptr) {
            Node* next = current->next;
            delete current;
            current = next;
        }
    }

    TreiberStack(const TreiberStack&) = delete;
    TreiberStack& operator=(const TreiberStack&) = delete;

    void push(T value) {
        auto* new_node = new Node(std::move(value));
        Node* old_head = head_.load(std::memory_order_relaxed);

        // Оптимістична публікація з семантикою release
        while (!head_.compare_exchange_weak(
            old_head,
            new_node,
            std::memory_order_release,
            std::memory_order_relaxed)) {
            new_node->next = old_head;
        }
    }

    std::optional<T> pop() {
        Node* old_head = head_.load(std::memory_order_acquire);

        while (old_head != nullptr) {
            Node* next_node = old_head->next;

            if (head_.compare_exchange_weak(
                    old_head,
                    next_node,
                    std::memory_order_acquire,
                    std::memory_order_relaxed)) {
                T result = std::move(old_head->value);
                delete old_head;
                return result;
            }
        }
        return std::nullopt;
    }

private:
    struct Node {
        T value;
        Node* next{nullptr};
        explicit Node(T val) : value(std::move(val)) {}
    };

    std::atomic<Node*> head_;
};
