// Тегований CAS мовою C++17
#include <atomic>
#include <cstdint>

template <typename T>
struct TaggedPointer {
    T* ptr{nullptr};
    std::uintptr_t tag{0};
};

template <typename T>
class TaggedLockFreeStack {
private:
    struct Node {
        T data;
        Node* next{nullptr};
        explicit Node(T val) : data(std::move(val)) {}
    };

    alignas(16) std::atomic<TaggedPointer<Node>> top_{TaggedPointer<Node>{nullptr, 0}};

public:
    void push(T val) {
        auto* new_node = new Node(std::move(val));
        TaggedPointer<Node> old_top = top_.load(std::memory_order_relaxed);
        TaggedPointer<Node> new_top;

        do {
            new_node->next = old_top.ptr;
            new_top.ptr = new_node;
            new_top.tag = old_top.tag + 1;
        } while (!top_.compare_exchange_weak(
                    old_top, new_top,
                    std::memory_order_release,
                    std::memory_order_relaxed));
    }
};
