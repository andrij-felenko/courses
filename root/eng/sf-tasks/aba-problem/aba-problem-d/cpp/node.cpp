#include <atomic>
#include <cstdint>

template <typename T>
struct Node {
    T data;
    Node* next;
    explicit Node(const T& val) : data(val), next(nullptr) {}
};

template <typename T>
class TaggedPointerStack {
private:
    struct TaggedNodePtr {
        Node<T>* ptr;
        uint64_t tag;
    };

    // DW-CAS вимагає 16-байтового атомарного контейнера
    alignas(16) std::atomic<TaggedNodePtr> head;

public:
    TaggedPointerStack() {
        head.store({nullptr, 0}, std::memory_order_relaxed);
    }

    void push(const T& val) {
        Node<T>* new_node = new Node<T>(val);
        TaggedNodePtr current = head.load(std::memory_order_relaxed);
        TaggedNodePtr next_tagged;

        do {
            new_node->next = current.ptr;
            next_tagged.ptr = new_node;
            next_tagged.tag = current.tag + 1; // Монотонне збільшення тегу
        } while (!head.compare_exchange_weak(
            current, next_tagged,
            std::memory_order_release,
            std::memory_order_relaxed));
    }

    bool pop(T& result) {
        TaggedNodePtr current = head.load(std::memory_order_acquire);
        TaggedNodePtr next_tagged;

        do {
            if (current.ptr == nullptr) {
                return false; // Стек порожній
            }
            next_tagged.ptr = current.ptr->next;
            next_tagged.tag = current.tag + 1; // Оновлення версії під час Pop
        } while (!head.compare_exchange_weak(
            current, next_tagged,
            std::memory_order_acq_rel,
            std::memory_order_acquire));

        result = current.ptr->data;
        // УВАГА: Безпечне вилучення пам'яті current.ptr вимагає додаткових механізмів!
        return true;
    }
};
