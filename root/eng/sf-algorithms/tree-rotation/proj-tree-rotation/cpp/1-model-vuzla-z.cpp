#include <iostream>
#include <memory>
#include <algorithm>
#include <cassert>

template <typename T>
struct Node {
    T key;
    int height{1};
    Node* left{nullptr};
    Node* right{nullptr};
    Node* parent{nullptr};

    explicit Node(T val) : key(std::move(val)) {}
};

template <typename T>
int get_height(const Node<T>* node) noexcept {
    return node ? node->height : 0;
}

template <typename T>
int get_balance_factor(const Node<T>* node) noexcept {
    return node ? get_height(node->right) - get_height(node->left) : 0;
}

template <typename T>
void update_height(Node<T>* node) noexcept {
    if (node) {
        node->height = std::max(get_height(node->left), get_height(node->right)) + 1;
    }
}
