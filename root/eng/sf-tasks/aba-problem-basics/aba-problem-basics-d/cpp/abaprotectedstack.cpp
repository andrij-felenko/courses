// Реалізація безблокувального стеку із захистом від ABA на C++11 / C++17
#include <atomic>
#include <cstdint>
#include <cstddef>
#include <utility>

template <typename T>
class ABAProtectedStack {
private:
    struct Node {
        T data;
        Node* next;
        Node(T val) : data(std::move(val)), next(nullptr) {}
    };

    // Вирівнювання структури для забезпечення атомарності 128-бітного CAS
    struct alignas(16) TaggedPointer {
        Node* ptr{nullptr};
        std::uintptr_t tag{0};
    };

    std::atomic<TaggedPointer> head_;

public:
    ABAProtectedStack() {
        head_.store(TaggedPointer{nullptr, 0}, std::memory_order_relaxed);
    }

    ~ABAProtectedStack() {
        TaggedPointer current = head_.load(std::memory_order_relaxed);
        while (current.ptr != nullptr) {
            Node* next = current.ptr->next;
            delete current.ptr;
            current.ptr = next;
        }
    }

    void push(T value) {
        Node* new_node = new Node(std::move(value));
        TaggedPointer old_head = head_.load(std::memory_order_relaxed);
        TaggedPointer new_head;

        do {
            new_node->next = old_head.ptr;
            new_head.ptr = new_node;
            new_head.tag = old_head.tag + 1; // Захист від повторного збігу адреси
        } while (!head_.compare_exchange_weak(
            old_head, 
            new_head, 
            std::memory_order_release, 
            std::memory_order_relaxed));
    }

    bool pop(T& result) {
        TaggedPointer old_head = head_.load(std::memory_order_acquire);
        TaggedPointer new_head;

        do {
            if (old_head.ptr == nullptr) {
                return false;
            }
            new_head.ptr = old_head.ptr->next;
            new_head.tag = old_head.tag + 1; // Оновлення тегу версії
        } while (!head_.compare_exchange_weak(
            old_head, 
            new_head, 
            std::memory_order_acq_rel, 
            std::memory_order_acquire));

        result = std::move(old_head.ptr->data);
        delete old_head.ptr;
        return true;
    }
};
