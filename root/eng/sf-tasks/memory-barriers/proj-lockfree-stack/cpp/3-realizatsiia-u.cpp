// Ідіоматична реалізація мовою C++17 (std::atomic, RAII, std::optional)
#include <atomic>
#include <memory>
#include <optional>
#include <utility>

template <typename T>
class LockFreeStack {
private:
    struct Node {
        T data;
        Node* next{nullptr};

        explicit Node(T val) : data(std::move(val)) {}
    };

    std::atomic<Node*> top_{nullptr};

public:
    LockFreeStack() = default;
    
    ~LockFreeStack() {
        // Очищення залишкових вузлів у деструкторі (RAII)
        Node* current = top_.exchange(nullptr, std::memory_order_relaxed);
        while (current) {
            Node* next = current->next;
            delete current;
            current = next;
        }
    }

    LockFreeStack(const LockFreeStack&) = delete;
    LockFreeStack& operator=(const LockFreeStack&) = delete;

    void push(T val) {
        auto* new_node = new Node(std::move(val));
        Node* old_top = top_.load(std::memory_order_relaxed);
        
        do {
            new_node->next = old_top;
        } while (!top_.compare_exchange_weak(
                    old_top, new_node,
                    std::memory_order_release,
                    std::memory_order_relaxed));
    }

    std::optional<T> pop() {
        Node* old_top = top_.load(std::memory_order_acquire);
        
        do {
            if (!old_top) {
                return std::nullopt;
            }
        } while (!top_.compare_exchange_weak(
                    old_top, old_top->next,
                    std::memory_order_acquire,
                    std::memory_order_acquire));

        T result = std::move(old_top->data);
        delete old_top; // У продакшені рекомендується std::shared_ptr / Hazard Pointers
        return result;
    }
};
