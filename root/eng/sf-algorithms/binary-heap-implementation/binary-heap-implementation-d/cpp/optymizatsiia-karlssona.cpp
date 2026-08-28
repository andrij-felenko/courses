#include <vector>
#include <optional>
#include <stdexcept>
#include <utility>
#include <concepts>

template <typename T, typename Compare = std::less<T>>
class MinHeap {
public:
    explicit MinHeap(Compare comp = Compare{}) : comp_(comp) {}

    [[nodiscard]] bool empty() const noexcept { return data_.empty(); }
    [[nodiscard]] size_t size() const noexcept { return data_.size(); }

    [[nodiscard]] std::optional<T> top() const noexcept {
        if (empty()) return std::nullopt;
        return data_.front();
    }

    void push(T value) {
        data_.push_back(std::move(value));
        sift_up(static_cast<int>(data_.size()) - 1);
    }

    T pop() {
        if (empty()) {
            throw std::runtime_error("Pop called on empty MinHeap");
        }
        T root = std::move(data_.front());
        if (data_.size() == 1) {
            data_.pop_back();
        } else {
            data_.front() = std::move(data_.back());
            data_.pop_back();
            sift_down(0);
        }
        return root;
    }

private:
    Compare comp_;
    std::vector<T> data_;

    void sift_up(int i) {
        while (i > 0) {
            int parent = (i - 1) / 2;
            if (comp_(data_[i], data_[parent])) {
                std::swap(data_[i], data_[parent]);
                i = parent;
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

            if (right < n && comp_(data_[right], data_[left])) {
                best = right;
            }
            if (comp_(data_[best], data_[i])) {
                std::swap(data_[i], data_[best]);
                i = best;
            } else {
                break;
            }
        }
    }
};
