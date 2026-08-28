#include <iostream>
#include <memory>
#include <optional>
#include <stdexcept>
#include <utility>

namespace ds {

template <typename T>
class BinomialHeap {
private:
    struct Node {
        T key;
        int degree{0};
        Node* parent{nullptr};
        Node* child{nullptr};
        Node* sibling{nullptr};

        explicit Node(T val) : key(std::move(val)) {}
    };

    Node* head_{nullptr};

    static void link_trees(Node* y, Node* z) {
        y->parent = z;
        y->sibling = z->child;
        z->child = y;
        z->degree++;
    }

    static Node* merge_root_lists(Node* h1, Node* h2) {
        if (!h1) return h2;
        if (!h2) return h1;

        Node* head = nullptr;
        Node** tail = &head;

        while (h1 && h2) {
            if (h1->degree <= h2->degree) {
                *tail = h1;
                h1 = h1->sibling;
            } else {
                *tail = h2;
                h2 = h2->sibling;
            }
            tail = &((*tail)->sibling);
        }
        *tail = h1 ? h1 : h2;
        return head;
    }

    static Node* union_heaps(Node* h1, Node* h2) {
        Node* head = merge_root_lists(h1, h2);
        if (!head) return nullptr;

        Node* prev = nullptr;
        Node* curr = head;
        Node* next = curr->sibling;

        while (next) {
            if ((curr->degree != next->degree) ||
                (next->sibling && next->sibling->degree == curr->degree)) {
                prev = curr;
                curr = next;
            } else {
                if (curr->key <= next->key) {
                    curr->sibling = next->sibling;
                    link_trees(next, curr);
                } else {
                    if (!prev) {
                        head = next;
                    } else {
                        prev->sibling = next;
                    }
                    link_trees(curr, next);
                    curr = next;
                }
            }
            next = curr->sibling;
        }
        return head;
            }

    static Node* reverse_list(Node* node) {
        Node* prev = nullptr;
        Node* curr = node;
        while (curr) {
            Node* next = curr->sibling;
            curr->sibling = prev;
            curr->parent = nullptr;
            prev = curr;
            curr = next;
        }
        return prev;
    }

    static void destroy_tree(Node* node) {
        while (node) {
            Node* next = node->sibling;
            if (node->child) {
                destroy_tree(node->child);
            }
            delete node;
            node = next;
        }
    }

public:
    using NodeHandle = Node*;

    BinomialHeap() = default;
    
    ~BinomialHeap() {
        destroy_tree(head_);
    }

    BinomialHeap(const BinomialHeap&) = delete;
    BinomialHeap& operator=(const BinomialHeap&) = delete;

    BinomialHeap(BinomialHeap&& other) noexcept : head_(other.head_) {
        other.head_ = nullptr;
    }

    BinomialHeap& operator=(BinomialHeap&& other) noexcept {
        if (this != &other) {
            destroy_tree(head_);
            head_ = other.head_;
            other.head_ = nullptr;
        }
        return *this;
    }

    [[nodiscard]] bool empty() const noexcept {
        return head_ == nullptr;
    }

    NodeHandle insert(T key) {
        auto* node = new Node(std::move(key));
        head_ = union_heaps(head_, node);
        return node;
    }

    void merge(BinomialHeap& other) {
        if (this == &other) return;
        head_ = union_heaps(head_, other.head_);
        other.head_ = nullptr;
    }

    [[nodiscard]] std::optional<T> find_min() const {
        if (!head_) return std::nullopt;
        Node* min_node = head_;
        Node* curr = head_->sibling;
        while (curr) {
            if (curr->key < min_node->key) {
                min_node = curr;
            }
            curr = curr->sibling;
        }
        return min_node->key;
    }

    T extract_min() {
        if (!head_) {
            throw std::underflow_error("BinomialHeap is empty");
        }

        Node* min_node = head_;
        Node* min_prev = nullptr;
        Node* curr = head_;
        Node* prev = nullptr;

        while (curr) {
            if (curr->key < min_node->key) {
                min_node = curr;
                min_prev = prev;
            }
            prev = curr;
            curr = curr->sibling;
        }

        if (min_prev) {
            min_prev->sibling = min_node->sibling;
        } else {
            head_ = min_node->sibling;
        }

        Node* child_heap = reverse_list(min_node->child);
        T min_val = std::move(min_node->key);
        delete min_node;

        head_ = union_heaps(head_, child_heap);
        return min_val;
    }

    void decrease_key(NodeHandle handle, T new_key) {
        if (!handle || new_key > handle->key) {
            throw std::invalid_argument("New key must be smaller than current key");
        }

        handle->key = std::move(new_key);
        Node* curr = handle;
        Node* parent = curr->parent;

        while (parent && curr->key < parent->key) {
            std::swap(curr->key, parent->key);
            curr = parent;
            parent = curr->parent;
        }
    }
};

} // namespace ds
