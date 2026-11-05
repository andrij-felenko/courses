#include <iostream>
#include <atomic>
#include <vector>
#include <thread>
#include <array>

template <typename T>
class HazardPointerStack {
    struct Node {
        T data;
        Node* next;
        Node(T val) : data(val), next(nullptr) {}
    };

    std::atomic<Node*> head{nullptr};
    static constexpr size_t MAX_THREADS = 16;
    inline static std::array<std::atomic<Node*>, MAX_THREADS> hazard_pointers{};

public:
    void push(T val) {
        Node* new_node = new Node(val);
        new_node->next = head.load(std::memory_order_relaxed);
        while (!head.compare_exchange_weak(new_node->next, new_node,
                                          std::memory_order_release,
                                          std::memory_order_relaxed));
    }

    bool pop(size_t thread_id, T& val) {
        Node* curr_head = nullptr;
        do {
            curr_head = head.load(std::memory_order_acquire);
            if (!curr_head) return false;
            hazard_pointers[thread_id].store(curr_head, std::memory_order_release);
            if (head.load(std::memory_order_acquire) != curr_head) {
                hazard_pointers[thread_id].store(nullptr, std::memory_order_release);
                continue;
            }
            Node* next = curr_head->next;
            if (head.compare_exchange_weak(curr_head, next,
                                          std::memory_order_release,
                                          std::memory_order_relaxed)) {
                val = curr_head->data;
                hazard_pointers[thread_id].store(nullptr, std::memory_order_release);
                delete curr_head;
                return true;
            }
            hazard_pointers[thread_id].store(nullptr, std::memory_order_release);
        } while (true);
    }
};

int main() {
    std::cout << "=== Lock-Free Stack with Hazard Pointers (C++) ===\n";
    HazardPointerStack<int> stack;
    stack.push(100);
    stack.push(200);

    int val;
    if (stack.pop(0, val)) std::cout << "Popped: " << val << "\n";
    if (stack.pop(0, val)) std::cout << "Popped: " << val << "\n";
    return 0;
}
