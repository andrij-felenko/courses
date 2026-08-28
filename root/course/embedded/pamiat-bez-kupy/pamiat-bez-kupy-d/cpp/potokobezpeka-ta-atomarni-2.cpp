/* C++20 Lock-free атомарний блоковий пул на базі std::atomic */
template <typename T, std::size_t N>
class AtomicFixedPool {
public:
    [[nodiscard]] T* allocate() noexcept {
        Node* old_head = head_.load(std::memory_order_relaxed);
        while (old_head != nullptr) {
            Node* next_node = old_head->next;
            if (head_.compare_exchange_weak(old_head, next_node,
                                            std::memory_order_acquire,
                                            std::memory_order_relaxed)) {
                return reinterpret_cast<T*>(old_head);
            }
        }
        return nullptr; /* Пул вичерпано */
    }

private:
    struct Node { Node* next; };
    std::atomic<Node*> head_{nullptr};
    alignas(T) std::byte storage_[N * sizeof(T)];
};
