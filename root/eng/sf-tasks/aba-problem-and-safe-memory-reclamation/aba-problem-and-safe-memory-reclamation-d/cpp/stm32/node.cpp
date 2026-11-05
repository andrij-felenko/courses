#include <atomic>
#include <cstdint>
#include <cstddef>

template <typename T>
struct Node {
    T data;
    Node* next;
};

/* 8-байтове вирівнювання тегованої структури у C++11 */
template <typename T>
struct alignas(8) TaggedPtr {
    Node<T>* ptr;
    uint32_t tag;

    bool operator==(const TaggedPtr& other) const noexcept {
        return ptr == other.ptr && tag == other.tag;
    }
};

template <typename T, size_t Capacity>
class LockFreeStack {
private:
    std::atomic<TaggedPtr<T>> head;
    Node<T> node_pool[Capacity];
    std::atomic<TaggedPtr<T>> free_list;

public:
    LockFreeStack() {
        TaggedPtr<T> initial_head{nullptr, 0};
        head.store(initial_head, std::memory_order_relaxed);

        /* Ініціалізація статичного пулу пам'яті */
        TaggedPtr<T> initial_free{&node_pool[0], 0};
        for (size_t i = 0; i < Capacity - 1; ++i) {
            node_pool[i].next = &node_pool[i + 1];
        }
        node_pool[Capacity - 1].next = nullptr;
        free_list.store(initial_free, std::memory_order_relaxed);
    }

    Node<T>* allocate_node() {
        TaggedPtr<T> old_free = free_list.load(std::memory_order_acquire);
        TaggedPtr<T> new_free;
        do {
            if (old_free.ptr == nullptr) {
                return nullptr; /* Пул вичерпано */
            }
            new_free.ptr = old_free.ptr->next;
            new_free.tag = old_free.tag + 1;
        } while (!free_list.compare_exchange_weak(
            old_free, new_free,
            std::memory_order_release,
            std::memory_order_acquire));

        return old_free.ptr;
    }

    void free_node(Node<T>* node) {
        TaggedPtr<T> old_free = free_list.load(std::memory_order_acquire);
        TaggedPtr<T> new_free;
        do {
            node->next = old_free.ptr;
            new_free.ptr = node;
            new_free.tag = old_free.tag + 1;
        } while (!free_list.compare_exchange_weak(
            old_free, new_free,
            std::memory_order_release,
            std::memory_order_acquire));
    }

    void push(const T& value) {
        Node<T>* node = allocate_node();
        if (!node) return;
        node->data = value;

        TaggedPtr<T> old_head = head.load(std::memory_order_acquire);
        TaggedPtr<T> new_head;
        do {
            node->next = old_head.ptr;
            new_head.ptr = node;
            new_head.tag = old_head.tag + 1;
        } while (!head.compare_exchange_weak(
            old_head, new_head,
            std::memory_order_release,
            std::memory_order_acquire));
    }

    bool pop(T& result) {
        TaggedPtr<T> old_head = head.load(std::memory_order_acquire);
        TaggedPtr<T> new_head;
        do {
            if (old_head.ptr == nullptr) {
                return false;
            }
            new_head.ptr = old_head.ptr->next;
            new_head.tag = old_head.tag + 1;
        } while (!head.compare_exchange_weak(
            old_head, new_head,
            std::memory_order_release,
            std::memory_order_acquire));

        result = old_head.ptr->data;
        free_node(old_head.ptr);
        return true;
    }
};
