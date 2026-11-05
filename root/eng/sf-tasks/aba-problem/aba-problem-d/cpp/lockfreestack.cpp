#include <atomic>

template <typename T>
class LockFreeStack {
    struct Node {
        T data;
        Node* next;
        Node(const T& val) : data(val), next(nullptr) {}
    };

    std::atomic<Node*> top{nullptr};

public:
    void push(const T& val) {
        Node* new_node = new Node(val);
        new_node->next = top.load(std::memory_order_relaxed);
        while (!top.compare_exchange_weak(new_node->next, new_node,
                                          std::memory_order_release,
                                          std::memory_order_relaxed));
    }

    bool pop(T& result) {
        Node* old_top = top.load(std::memory_order_acquire);
        while (old_top != nullptr) {
            // КРОК 1: Зчитування вказівника на наступний елемент.
            // Якщо потік призупиниться тут, виникає вразливість ABA!
            Node* next_node = old_top->next;

            if (top.compare_exchange_weak(old_top, next_node,
                                          std::memory_order_release,
                                          std::memory_order_acquire)) {
                result = old_top->data;
                delete old_top; // Фізичне звільнення пам'яті
                return true;
            }
        }
        return false;
    }
};
