#include <atomic>
#include <cstdint>
#include <cstddef>

template<typename T>
class LockFreeStack {
private:
    struct Node {
        T data;
        Node* next;

        Node(const T& val) : data(val), next(nullptr) {}
    };

    struct TaggedPointer {
        Node* ptr;
        uint32_t tag;
    };

    /* Атомарне 64-бітне слово для подвійного CAS у C++11/17 */
    alignas(8) std::atomic<TaggedPointer> head;

public:
    LockFreeStack() {
        head.store(TaggedPointer{nullptr, 0}, std::memory_order_relaxed);
    }

    void push(const T& value) {
        Node* new_node = new Node(value);
        TaggedPointer old_head = head.load(std::memory_order_relaxed);
        TaggedPointer new_head;

        do {
            new_node->next = old_head.ptr;
            new_head.ptr = new_node;
            new_head.tag = old_head.tag + 1; /* Монотонне збільшення версії */
        } while (!head.compare_exchange_weak(
            old_head, 
            new_head, 
            std::memory_order_release, 
            std::memory_order_relaxed));
    }

    bool pop(T& result) {
        TaggedPointer old_head = head.load(std::memory_order_acquire);
        TaggedPointer new_head;

        do {
            if (old_head.ptr == nullptr) {
                return false; /* Стек порожній */
            }
            new_head.ptr = old_head.ptr->next;
            new_head.tag = old_head.tag + 1; /* Захист від ABA за допомогою унікального тегу */
        } while (!head.compare_exchange_weak(
            old_head, 
            new_head, 
            std::memory_order_acquire, 
            std::memory_order_relaxed));

        result = old_head.ptr->data;
        delete old_head.ptr; /* Примітка: у реальному RTOS тут використовується Hazard Pointers */
        return true;
    }
};
