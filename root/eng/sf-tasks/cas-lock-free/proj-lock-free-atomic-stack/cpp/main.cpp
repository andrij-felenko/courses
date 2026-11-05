#include <iostream>
#include <atomic>

template <typename T>
class LockFreeStack {
    struct Node {
        T data;
        Node* next;
        Node(T val) : data(val), next(nullptr) {}
    };

    std::atomic<Node*> head{nullptr};

public:
    void push(T val) {
        Node* new_node = new Node(val);
        new_node->next = head.load(std::memory_order_relaxed);
        while (!head.compare_exchange_weak(new_node->next, new_node,
                                          std::memory_order_release,
                                          std::memory_order_relaxed));
    }

    bool pop(T& val) {
        Node* curr_head = head.load(std::memory_order_acquire);
        while (curr_head && !head.compare_exchange_weak(curr_head, curr_head->next,
                                                       std::memory_order_release,
                                                       std::memory_order_relaxed));
        if (!curr_head) return false;
        val = curr_head->data;
        delete curr_head;
        return true;
    }
};

int main() {
    std::cout << "=== CAS Atomic Lock-Free Stack (C++) ===\n";
    LockFreeStack<int> stack;
    stack.push(1);
    stack.push(2);
    stack.push(3);

    int val;
    while (stack.pop(val)) {
        std::cout << "Popped: " << val << "\n";
    }
    return 0;
}
