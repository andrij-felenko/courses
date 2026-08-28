#include <vector>
#include <optional>
#include <stdexcept>
#include <utility>
#include <concepts>

template <typename Key = int, typename Compare = std::less<Key>>
class IndexedMinHeap {
public:
    struct Node {
        int id;
        Key key;
    };

    explicit IndexedMinHeap(size_t capacity, Compare comp = Compare{})
        : comp_(comp), pos_(capacity, -1) {
        data_.reserve(capacity);
    }

    [[nodiscard]] bool empty() const noexcept {
        return data_.empty();
    }

    [[nodiscard]] size_t size() const noexcept {
        return data_.size();
    }

    [[nodiscard]] size_t capacity() const noexcept {
        return pos_.size();
    }

    [[nodiscard]] bool contains(int id) const noexcept {
        if (id < 0 || static_cast<size_t>(id) >= pos_.size()) return false;
        return pos_[id] != -1;
    }

    [[nodiscard]] std::optional<Key> key_of(int id) const noexcept {
        if (!contains(id)) return std::nullopt;
        return data_[pos_[id]].key;
    }

    [[nodiscard]] std::optional<Node> top() const noexcept {
        if (empty()) return std::nullopt;
        return data_.front();
    }

    void push(int id, Key key) {
        if (id < 0 || static_cast<size_t>(id) >= pos_.size()) {
            throw std::out_of_range("ID out of indexed heap capacity");
        }
        if (contains(id)) {
            throw std::invalid_argument("ID already present in heap");
        }
        int idx = static_cast<int>(data_.size());
        data_.push_back(Node{id, std::move(key)});
        pos_[id] = idx;
        sift_up(idx);
    }

    Node pop() {
        if (empty()) {
            throw std::runtime_error("Pop from empty indexed heap");
        }
        Node root = data_.front();
        pos_[root.id] = -1;

        if (data_.size() == 1) {
            data_.pop_back();
        } else {
            data_.front() = std::move(data_.back());
            data_.pop_back();
            pos_[data_.front().id] = 0;
            sift_down(0);
        }
        return root;
    }

    void decrease_key(int id, Key new_key) {
        if (!contains(id)) {
            throw std::invalid_argument("ID not found in heap");
        }
        int idx = pos_[id];
        if (comp_(data_[idx].key, new_key)) {
            throw std::invalid_argument("New key is greater in decrease_key");
        }
        data_[idx].key = std::move(new_key);
        sift_up(idx);
    }

    void increase_key(int id, Key new_key) {
        if (!contains(id)) {
            throw std::invalid_argument("ID not found in heap");
        }
        int idx = pos_[id];
        if (comp_(new_key, data_[idx].key)) {
            throw std::invalid_argument("New key is smaller in increase_key");
        }
        data_[idx].key = std::move(new_key);
        sift_down(idx);
    }

    void erase(int id) {
        if (!contains(id)) return;
        int idx = pos_[id];
        Key old_key = data_[idx].key;
        pos_[id] = -1;

        if (idx == static_cast<int>(data_.size()) - 1) {
            data_.pop_back();
            return;
        }

        data_[idx] = std::move(data_.back());
        data_.pop_back();
        pos_[data_[idx].id] = idx;

        if (comp_(data_[idx].key, old_key)) {
            sift_up(idx);
        } else {
            sift_down(idx);
        }
    }

private:
    Compare comp_;
    std::vector<Node> data_;
    std::vector<int> pos_;

    void swap_nodes(int i, int j) noexcept {
        std::swap(data_[i], data_[j]);
        pos_[data_[i].id] = i;
        pos_[data_[j].id] = j;
    }

    void sift_up(int i) {
        while (i > 0) {
            int p = (i - 1) / 2;
            if (comp_(data_[i].key, data_[p].key)) {
                swap_nodes(i, p);
                i = p;
            } else {
                break;
            }
        }
    }

    void sift_down(int i) {
        int n = static_cast<int>(data_.size());
        while (2 * i + 1 < n) {
            int left = 2 * i + 1;
            int right = 2 * i + 2;
            int best = left;

            if (right < n && comp_(data_[right].key, data_[left].key)) {
                best = right;
            }
            if (comp_(data_[best].key, data_[i].key)) {
                swap_nodes(i, best);
                i = best;
            } else {
                break;
            }
        }
    }
};
