#include <utility>

struct NodeBase {
    NodeBase* prev{nullptr};
    NodeBase* next{nullptr};
};

template <typename T>
struct ListNode : public NodeBase {
    T data;
};

// Видалення вузла в списку з вартовим складається з двох переприв'язок
inline void unlink_sentinel_node(NodeBase* node) noexcept {
    node->prev->next = node->next;
    node->next->prev = node->prev;
}
