#include <iostream>
#include <atomic>
#include <cstdint>

template <typename T>
class TaggedTreiberStack {
    struct Node {
        T data;
        Node* next;
        Node(T val) : data(val), next(nullptr) {}
    };

    struct TaggedPtr {
        Node* ptr{nullptr};
        uint64_t tag{0};
    };

    std::atomic<TaggedPtr> head{TaggedPtr{nullptr, 0}};

public:
    void push(T val) {
        Node* new_node = new Node(val);
        TaggedPtr old_head = head.load(std::memory_order_relaxed);
        TaggedPtr new_head;
        do {
            new_node->next = old_head.ptr;
            new_head.ptr = new_node;
            new_head.tag = old_head.tag + 1;
        } while (!head.compare_exchange_weak(old_head, new_head,
                                           std::memory_order_release,
                                           std::memory_order_relaxed));
    }

    bool pop(T& val) {
        TaggedPtr old_head = head.load(std::memory_order_acquire);
        TaggedPtr new_head;
        do {
            if (!old_head.ptr) return false;
            new_head.ptr = old_head.ptr->next;
            new_head.tag = old_head.tag + 1;
        } while (!head.compare_exchange_weak(old_head, new_head,
                                           std::memory_order_release,
                                           std::memory_order_relaxed));
        val = old_head.ptr->data;
        delete old_head.ptr;
        return true;
    }
};

int main() {
    std::cout << "=== Treiber Stack ABA Tagged Pointer (C++) ===\n";
    TaggedTreiberStack<int> stack;
    stack.push(10);
    stack.push(20);
    int val;
    if (stack.pop(val)) std::cout << "Popped: " << val << "\n";
    if (stack.pop(val)) std::cout << "Popped: " << val << "\n";
    return 0;
}
