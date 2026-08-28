#include <iostream>
#include <vector>
#include <memory>
#include <optional>
#include <random>
#include <functional>
#include <cstdint>
#include <utility>

template <typename Key, typename Value, typename Compare = std::less<Key>>
class SkipList {
public:
    static constexpr size_t kMaxLevel = 32;
    static constexpr double kBranchingProb = 0.25;

private:
    struct Node {
        Key key;
        Value value;
        std::vector<Node*> forward;

        Node(const Key& k, const Value& v, size_t level)
            : key(k), value(v), forward(level, nullptr) {}

        explicit Node(size_t level)
            : key{}, value{}, forward(level, nullptr) {}
    };

    size_t current_level_{1};
    size_t element_count_{0};
    std::unique_ptr<Node> head_;
    Compare comp_{};

    std::mt19937 rng_{std::random_device{}()};
    std::uniform_real_distribution<double> dist_{0.0, 1.0};

    size_t random_level() {
        size_t lvl = 1;
        while (dist_(rng_) < kBranchingProb && lvl < kMaxLevel) {
            lvl++;
        }
        return lvl;
    }

public:
    class Iterator {
    public:
        using iterator_category = std::forward_iterator_tag;
        using value_type = std::pair<const Key&, Value&>;
        using difference_type = std::ptrdiff_t;

        explicit Iterator(Node* node = nullptr) : current_(node) {}

        std::pair<const Key&, Value&> operator*() const {
            return {current_->key, current_->value};
        }

        Iterator& operator++() {
            if (current_) {
                current_ = current_->forward[0];
            }
            return *this;
        }

        Iterator operator++(int) {
            Iterator tmp = *this;
            ++(*this);
            return tmp;
        }

        bool operator==(const Iterator& other) const noexcept {
            return current_ == other.current_;
        }

        bool operator!=(const Iterator& other) const noexcept {
            return current_ != other.current_;
        }

    private:
        Node* current_;
        friend class SkipList;
    };

    SkipList() : head_(std::make_unique<Node>(kMaxLevel)) {}

    ~SkipList() {
        clear();
    }

    SkipList(const SkipList&) = delete;
    SkipList& operator=(const SkipList&) = delete;

    SkipList(SkipList&& other) noexcept
        : current_level_(other.current_level_),
          element_count_(other.element_count_),
          head_(std::move(other.head_)),
          comp_(std::move(other.comp_)),
          rng_(std::move(other.rng_)) {
        other.current_level_ = 1;
        other.element_count_ = 0;
        other.head_ = std::make_unique<Node>(kMaxLevel);
    }

    SkipList& operator=(SkipList&& other) noexcept {
        if (this != &other) {
            clear();
            current_level_ = other.current_level_;
            element_count_ = other.element_count_;
            head_ = std::move(other.head_);
            comp_ = std::move(other.comp_);
            rng_ = std::move(other.rng_);
            other.current_level_ = 1;
            other.element_count_ = 0;
            other.head_ = std::make_unique<Node>(kMaxLevel);
        }
        return *this;
    }

    [[nodiscard]] size_t size() const noexcept { return element_count_; }
    [[nodiscard]] bool empty() const noexcept { return element_count_ == 0; }

    Iterator begin() const noexcept { return Iterator(head_->forward[0]); }
    Iterator end() const noexcept { return Iterator(nullptr); }

    [[nodiscard]] std::optional<Value> find(const Key& key) const {
        const Node* curr = head_.get();

        for (int i = static_cast<int>(current_level_) - 1; i >= 0; --i) {
            while (curr->forward[i] != nullptr && comp_(curr->forward[i]->key, key)) {
                curr = curr->forward[i];
            }
        }

        curr = curr->forward[0];
        if (curr != nullptr && !comp_(key, curr->key) && !comp_(curr->key, key)) {
            return curr->value;
        }
        return std::nullopt;
    }

    bool insert(const Key& key, const Value& value) {
        std::vector<Node*> update(kMaxLevel, nullptr);
        Node* curr = head_.get();

        for (int i = static_cast<int>(current_level_) - 1; i >= 0; --i) {
            while (curr->forward[i] != nullptr && comp_(curr->forward[i]->key, key)) {
                curr = curr->forward[i];
            }
            update[i] = curr;
        }

        curr = curr->forward[0];

        if (curr != nullptr && !comp_(key, curr->key) && !comp_(curr->key, key)) {
            curr->value = value;
            return false;
        }

        size_t new_level = random_level();
        if (new_level > current_level_) {
            for (size_t i = current_level_; i < new_level; ++i) {
                update[i] = head_.get();
            }
            current_level_ = new_level;
        }

        auto* new_node = new Node(key, value, new_level);
        for (size_t i = 0; i < new_level; ++i) {
            new_node->forward[i] = update[i]->forward[i];
            update[i]->forward[i] = new_node;
        }

        element_count_++;
        return true;
    }

    bool erase(const Key& key) {
        std::vector<Node*> update(kMaxLevel, nullptr);
        Node* curr = head_.get();

        for (int i = static_cast<int>(current_level_) - 1; i >= 0; --i) {
            while (curr->forward[i] != nullptr && comp_(curr->forward[i]->key, key)) {
                curr = curr->forward[i];
            }
            update[i] = curr;
        }

        curr = curr->forward[0];

        if (curr == nullptr || comp_(key, curr->key) || comp_(curr->key, key)) {
            return false;
        }

        for (size_t i = 0; i < current_level_; ++i) {
            if (update[i]->forward[i] != curr) {
                break;
            }
            update[i]->forward[i] = curr->forward[i];
        }

        delete curr;

        while (current_level_ > 1 && head_->forward[current_level_ - 1] == nullptr) {
            current_level_--;
        }

        element_count_--;
        return true;
    }

    Iterator lower_bound(const Key& key) const {
        Node* curr = head_.get();
        for (int i = static_cast<int>(current_level_) - 1; i >= 0; --i) {
            while (curr->forward[i] != nullptr && comp_(curr->forward[i]->key, key)) {
                curr = curr->forward[i];
            }
        }
        return Iterator(curr->forward[0]);
    }

    void clear() noexcept {
        Node* curr = head_->forward[0];
        while (curr != nullptr) {
            Node* next = curr->forward[0];
            delete curr;
            curr = next;
        }
        for (size_t i = 0; i < kMaxLevel; ++i) {
            head_->forward[i] = nullptr;
        }
        current_level_ = 1;
        element_count_ = 0;
    }
};
