#ifndef TREE_ROTATION_HPP
#define TREE_ROTATION_HPP

#include <utility>
#include <algorithm>
#include <cstddef>
#include <cassert>

template <typename T>
struct Node {
    T key;
    int height{1};
    std::size_t size{1};
    Node* left{nullptr};
    Node* right{nullptr};
    Node* parent{nullptr};

    explicit Node(T val) : key(std::move(val)) {}
};

template <typename T>
Node<T>* rotate_right(Node<T>* x, Node<T>*& root) noexcept;

template <typename T>
Node<T>* rotate_left(Node<T>* x, Node<T>*& root) noexcept;

template <typename T>
Node<T>* rotate_left_right(Node<T>* z, Node<T>*& root) noexcept;

template <typename T>
Node<T>* rotate_right_left(Node<T>* z, Node<T>*& root) noexcept;

#endif /* TREE_ROTATION_HPP */
