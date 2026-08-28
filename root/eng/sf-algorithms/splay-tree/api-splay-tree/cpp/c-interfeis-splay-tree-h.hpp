#pragma once

#include <optional>
#include <functional>
#include <memory>
#include <utility>
#include <cstddef>

template <
    typename Key,
    typename Value,
    typename Compare = std::less<Key>,
    typename Allocator = std::allocator<std::pair<const Key, Value>>
>
class SplayTree {
public:
    using key_type = Key;
    using mapped_type = Value;
    using value_type = std::pair<const Key, Value>;
    using size_type = std::size_t;
    using key_compare = Compare;

    struct Node {
        Key key;
        Value value;
        std::unique_ptr<Node> left{nullptr};
        std::unique_ptr<Node> right{nullptr};

        Node(Key k, Value v) : key(std::move(k)), value(std::move(v)) {}
    };

    // Створення та життєвий цикл
    SplayTree() = default;
    ~SplayTree() = default;

    SplayTree(const SplayTree&) = delete;
    SplayTree& operator=(const SplayTree&) = delete;

    SplayTree(SplayTree&&) noexcept = default;
    SplayTree& operator=(SplayTree&&) noexcept = default;

    // Стан контейнера
    [[nodiscard]] size_type size() const noexcept;
    [[nodiscard]] bool empty() const noexcept;
    void clear() noexcept;

    // Модифікатори та пошук
    bool insert(Key key, Value value);
    bool erase(const Key& key);
    
    [[nodiscard]] std::optional<Value> find(const Key& key);
    [[nodiscard]] bool contains(const Key& key);
    [[nodiscard]] std::optional<std::pair<Key, Value>> min();
    [[nodiscard]] std::optional<std::pair<Key, Value>> max();

    // Операції розрізання та злиття
    std::pair<SplayTree, SplayTree> split(const Key& key);
    static SplayTree join(SplayTree left_tree, SplayTree right_tree);
};
