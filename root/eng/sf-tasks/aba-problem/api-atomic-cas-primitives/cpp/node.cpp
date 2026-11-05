#include <atomic>
#include <cstdint>

struct Node {
    int value;
    Node* next;
};

class LockFreeHead {
private:
    std::atomic<Node*> head_{nullptr};

public:
    // Безблокувальне встановлення нового значення голови списку
    bool try_update_head(Node* old_head, Node* new_head) noexcept {
        Node* expected = old_head;
        
        // Використання std::atomic::compare_exchange_weak з явним оновленням expected
        return head_.compare_exchange_weak(expected, new_head,
                                           std::memory_order_release,
                                           std::memory_order_relaxed);
    }
};
