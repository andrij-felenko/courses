#include <iostream>
#include <cstddef>
#include <utility>

// Шаблонний круговий двозв'язний список з вартовим вузлом
template <typename T>
class SentinelList {
    struct NodeBase {
        NodeBase* prev{nullptr};
        NodeBase* next{nullptr};
    };

    struct Node : public NodeBase {
        T value;
        template <typename... Args>
        explicit Node(Args&&... args) : value(std::forward<Args>(args)...) {}
    };

    NodeBase sentinel_{};
    std::size_t size_{0};

    void reset_sentinel() noexcept {
        sentinel_.next = &sentinel_;
        sentinel_.prev = &sentinel_;
        size_ = 0;
    }

public:
    SentinelList() noexcept {
        reset_sentinel();
    }

    ~SentinelList() {
        clear();
    }

    SentinelList(const SentinelList&) = delete;
    SentinelList& operator=(const SentinelList&) = delete;

    SentinelList(SentinelList&& other) noexcept {
        if (other.empty()) {
            reset_sentinel();
        } else {
            sentinel_.next = other.sentinel_.next;
            sentinel_.prev = other.sentinel_.prev;
            sentinel_.next->prev = &sentinel_;
            sentinel_.prev->next = &sentinel_;
            size_ = other.size_;
            other.reset_sentinel();
        }
    }

    [[nodiscard]] bool empty() const noexcept { return size_ == 0; }
    [[nodiscard]] std::size_t size() const noexcept { return size_; }

    template <typename... Args>
    void emplace_back(Args&&... args) {
        // Вставка в кінець — це вставка перед sentinel_
        insert_before(&sentinel_, std::forward<Args>(args)...);
    }

    template <typename... Args>
    void emplace_front(Args&&... args) {
        // Вставка на початок — це вставка перед першим елементом
        insert_before(sentinel_.next, std::forward<Args>(args)...);
    }

    void pop_front() noexcept {
        if (!empty()) {
            remove_node(static_cast<Node*>(sentinel_.next));
        }
    }

    void pop_back() noexcept {
        if (!empty()) {
            remove_node(static_cast<Node*>(sentinel_.prev));
        }
    }

    void clear() noexcept {
        NodeBase* curr = sentinel_.next;
        while (curr != &sentinel_) {
            NodeBase* next = curr->next;
            delete static_cast<Node*>(curr);
            curr = next;
        }
        reset_sentinel();
    }

    void print() const {
        std::cout << "List (size=" << size_ << "): [ ";
        for (NodeBase* curr = sentinel_.next; curr != &sentinel_; curr = curr->next) {
            std::cout << static_cast<Node*>(curr)->value << " ";
        }
        std::cout << "]\n";
    }

private:
    template <typename... Args>
    void insert_before(NodeBase* pos, Args&&... args) {
        auto* new_node = new Node(std::forward<Args>(args)...);
        new_node->next = pos;
        new_node->prev = pos->prev;

        pos->prev->next = new_node;
        pos->prev = new_node;

        ++size_;
    }

    void remove_node(Node* node) noexcept {
        node->prev->next = node->next;
        node->next->prev = node->prev;
        delete node;
        --size_;
    }
};

int main() {
    SentinelList<int> list;
    list.emplace_back(100);
    list.emplace_back(200);
    list.emplace_front(50);
    list.print(); // [ 50 100 200 ]

    list.pop_front();
    list.print(); // [ 100 200 ]

    return 0;
}
