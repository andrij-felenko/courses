#include <iostream>
#include <array>
#include <optional>

template <typename T, size_t Capacity>
class CircularDeque {
private:
    std::array<T, Capacity> data_;
    size_t head_ = 0;
    size_t tail_ = 0;
    size_t count_ = 0;

public:
    CircularDeque() = default;

    [[nodiscard]] bool is_full() const noexcept { return count_ == Capacity; }
    [[nodiscard]] bool is_empty() const noexcept { return count_ == 0; }
    [[nodiscard]] size_t size() const noexcept { return count_; }

    // Додавання на початок (голова рухається ліворуч)
    bool push_front(const T& value) {
        if (is_full()) return false;
        
        if (!is_empty()) {
            head_ = (head_ - 1 + Capacity) % Capacity;
        }
        
        data_[head_] = value;
        count_++;
        return true;
    }

    // Додавання в кінець (хвіст рухається праворуч)
    bool push_back(const T& value) {
        if (is_full()) return false;
        
        if (!is_empty()) {
            tail_ = (tail_ + 1) % Capacity;
        }
        
        data_[tail_] = value;
        count_++;
        return true;
    }

    // Вилучення з початку (голова рухається праворуч)
    std::optional<T> pop_front() {
        if (is_empty()) return std::nullopt;
        
        T value = data_[head_];
        count_--;
        
        if (!is_empty()) {
            head_ = (head_ + 1) % Capacity;
        }
        return value;
    }

    // Вилучення з кінця (хвіст рухається ліворуч)
    std::optional<T> pop_back() {
        if (is_empty()) return std::nullopt;
        
        T value = data_[tail_];
        count_--;
        
        if (!is_empty()) {
            tail_ = (tail_ - 1 + Capacity) % Capacity;
        }
        return value;
    }
};

int main() {
    CircularDeque<int, 8> dq;

    dq.push_back(10);
    dq.push_back(20);
    dq.push_front(5);  // Стан черги: [5, 10, 20]

    std::cout << "Елементи черги з початку: ";
    while (auto val = dq.pop_front()) {
        std::cout << *val << " ";  // Виведе: 5 10 20
    }
    std::cout << "\n";
    return 0;
}
