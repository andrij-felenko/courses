#include <iostream>
#include <vector>
#include <iterator>
#include <concepts>
#include <ranges>
#include <cassert>

// Узагальнений кроковий ітератор C++20
template<std::random_access_iterator UnderlyingIt>
class StrideIterator {
public:
    using iterator_concept  = std::random_access_iterator_tag;
    using iterator_category = std::random_access_iterator_tag;
    using value_type        = std::iter_value_t<UnderlyingIt>;
    using difference_type   = std::iter_difference_t<UnderlyingIt>;
    using pointer           = UnderlyingIt;
    using reference         = std::iter_reference_t<UnderlyingIt>;

    // Конструктор за замовчуванням (вимога концепту std::regular)
    StrideIterator() default = default;

    constexpr StrideIterator(UnderlyingIt current, difference_type stride)
        : current_(current), stride_(stride) {
        assert(stride > 0 && "Крок ітератора має бути строго додатним");
    }

    // Операції розіменування
    [[nodiscard]] constexpr reference operator*() const {
        return *current_;
    }

    [[nodiscard]] constexpr pointer operator->() const {
        return current_;
    }

    // Навігація вперед / назад
    constexpr StrideIterator& operator++() {
        current_ += stride_;
        return *this;
    }

    constexpr StrideIterator operator++(int) {
        StrideIterator temp = *this;
        ++(*this);
        return temp;
    }

    constexpr StrideIterator& operator--() {
        current_ -= stride_;
        return *this;
    }

    constexpr StrideIterator operator--(int) {
        StrideIterator temp = *this;
        --(*this);
        return temp;
    }

    // Арифметика довільного доступу
    constexpr StrideIterator& operator+=(difference_type n) {
        current_ += n * stride_;
        return *this;
    }

    constexpr StrideIterator& operator-=(difference_type n) {
        current_ -= n * stride_;
        return *this;
    }

    [[nodiscard]] friend constexpr StrideIterator operator+(StrideIterator it, difference_type n) {
        it += n;
        return it;
    }

    [[nodiscard]] friend constexpr StrideIterator operator+(difference_type n, StrideIterator it) {
        it += n;
        return it;
    }

    [[nodiscard]] friend constexpr StrideIterator operator-(StrideIterator it, difference_type n) {
        it -= n;
        return it;
    }

    [[nodiscard]] friend constexpr difference_type operator-(const StrideIterator& lhs, const StrideIterator& rhs) {
        assert(lhs.stride_ == rhs.stride_ && "Порівняння ітераторів з різним кроком неможливе");
        return (lhs.current_ - rhs.current_) / lhs.stride_;
    }

    // Доступ за індексом
    [[nodiscard]] constexpr reference operator[](difference_type n) const {
        return *(*this + n);
    }

    // Порівняння рівності та порядку
    [[nodiscard]] friend constexpr bool operator==(const StrideIterator& lhs, const StrideIterator& rhs) {
        return lhs.current_ == rhs.current_;
    }

    [[nodiscard]] friend constexpr auto operator<=>(const StrideIterator& lhs, const StrideIterator& rhs) {
        return lhs.current_ <=> rhs.current_;
    }

private:
    UnderlyingIt current_{};
    difference_type stride_{1};
};

int main() {
    std::vector<int> data = {10, 20, 30, 40, 50, 60, 70, 80, 90};

    // Створення крокових ітераторів для зчитування кожного 2-го елемента
    StrideIterator begin(data.begin(), 2);
    StrideIterator end(data.begin() + 8, 2); // Вказує на 90

    std::cout << "C++20 StrideIterator traversal: ";
    for (auto it = begin; it != end; ++it) {
        std::cout << *it << " ";
    }
    std::cout << "\n";

    // Перевірка відповідності концептам C++20 під час компіляції
    static_assert(std::random_access_iterator<StrideIterator<std::vector<int>::iterator>>);
    return 0;
}
