#include <iostream>
#include <cstdint>
#include <iterator>
#include <utility>

struct Fraction {
    int32_t num{0};
    int32_t den{1};

    constexpr bool operator==(const Fraction& rhs) const noexcept {
        return num == rhs.num && den == rhs.den;
    }
    constexpr bool operator!=(const Fraction& rhs) const noexcept {
        return !(*this == rhs);
    }
};

/* C++20 ForwardIterator для лінивої обробки послідовності Фарея.
   Не виділяє динамічної пам'яті, підтримує range-based for та алгоритми STL. */
class FareyGenerator {
public:
    explicit FareyGenerator(int32_t order) noexcept : n_(order) {}

    class Iterator {
    public:
        using iterator_category = std::forward_iterator_tag;
        using value_type = Fraction;
        using difference_type = std::ptrdiff_t;
        using pointer = const Fraction*;
        using reference = const Fraction&;

        Iterator(int32_t n, Fraction curr, Fraction next) noexcept
            : n_(n), curr_(curr), next_(next) {}

        reference operator*() const noexcept { return curr_; }
        pointer operator->() const noexcept { return &curr_; }

        Iterator& operator++() noexcept {
            if (curr_.num == 1 && curr_.den == 1) {
                curr_ = {0, 0}; // Сигнальний маркер кінця обходу
                return *this;
            }
            int32_t k = (n_ + curr_.den) / next_.den;
            Fraction step{k * next_.num - curr_.num, k * next_.den - curr_.den};

            curr_ = next_;
            next_ = step;
            return *this;
        }

        Iterator operator++(int) noexcept {
            Iterator tmp = *this;
            ++(*this);
            return tmp;
        }

        bool operator==(const Iterator& rhs) const noexcept {
            return curr_ == rhs.curr_;
        }
        bool operator!=(const Iterator& rhs) const noexcept {
            return !(*this == rhs);
        }

    private:
        int32_t n_;
        Fraction curr_;
        Fraction next_;
    };

    [[nodiscard]] Iterator begin() const noexcept {
        if (n_ < 1) return end();
        return Iterator(n_, {0, 1}, {1, n_});
    }

    [[nodiscard]] Iterator end() const noexcept {
        return Iterator(n_, {0, 0}, {0, 0});
    }

private:
    int32_t n_;
};
