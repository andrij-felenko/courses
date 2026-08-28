#include <cstdint>
#include <cstddef>
#include <array>
#include <new>

template <typename T, size_t Capacity>
class StaticObjectPool {
public:
    constexpr StaticObjectPool() noexcept {
        for (size_t i = 0; i < Capacity; ++i) {
            auto* node = reinterpret_cast<Node*>(&m_storage[i]);
            node->next = m_free_head;
            m_free_head = node;
        }
    }

    template <typename... Args>
    [[nodiscard]] T* create(Args&&... args) noexcept {
        if (m_free_head == nullptr) return nullptr;
        Node* node = m_free_head;
        m_free_head = node->next;
        return ::new (static_cast<void*>(node)) T(std::forward<Args>(args)...);
    }

    void destroy(T* obj) noexcept {
        if (obj == nullptr) return;
        obj->~T();
        auto* node = reinterpret_cast<Node*>(obj);
        node->next = m_free_head;
        m_free_head = node;
    }

private:
    union Node {
        Node* next;
        alignas(T) std::byte storage[sizeof(T)];
    };

    std::array<Node, Capacity> m_storage{};
    Node* m_free_head{nullptr};
};
