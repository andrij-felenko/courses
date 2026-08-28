#include <iostream>
#include <vector>
#include <ranges>
#include <concepts>
#include <cassert>
#include <type_traits>

namespace custom {

template <std::ranges::view V>
class stride_view : public std::ranges::view_interface<stride_view<V>> {
private:
    V base_ = V();
    std::ranges::range_difference_t<V> stride_ = 1;

    // Внутрішній клас ітератора
    template <bool IsConst>
    class iterator_impl {
    private:
        using BaseView = std::conditional_t<IsConst, const V, V>;
        using BaseIter = std::ranges::iterator_t<BaseView>;
        using BaseSent = std::ranges::sentinel_t<BaseView>;

        BaseIter current_ = BaseIter();
        BaseSent end_ = BaseSent();
        std::ranges::range_difference_t<V> stride_ = 1;

    public:
        using iterator_concept = std::conditional_t<
            std::ranges::random_access_range<BaseView>,
            std::random_access_iterator_tag,
            std::conditional_t<
                std::ranges::bidirectional_range<BaseView>,
                std::bidirectional_iterator_tag,
                std::forward_iterator_tag
            >
        >;
        using iterator_category = std::input_iterator_tag;
        using value_type = std::ranges::range_value_t<BaseView>;
        using difference_type = std::ranges::range_difference_t<BaseView>;
        using reference = std::ranges::range_reference_t<BaseView>;

        iterator_impl() = default;

        constexpr iterator_impl(BaseIter current, BaseSent end, difference_type stride)
            : current_(std::move(current)), end_(std::move(end)), stride_(stride) {}

        // Підтримка конверсії з non-const у const ітератор
        constexpr iterator_impl(iterator_impl<!IsConst> i)
            requires IsConst && std::convertible_to<std::ranges::iterator_t<V>, BaseIter>
            : current_(std::move(i.current_)), end_(std::move(i.end_)), stride_(i.stride_) {}

        constexpr decltype(auto) operator*() const {
            return *current_;
        }

        constexpr iterator_impl& operator++() {
            // Безпечне просування на stride_ кроків
            for (difference_type n = 0; n < stride_ && current_ != end_; ++n) {
                ++current_;
            }
            return *this;
        }

        constexpr iterator_impl operator++(int) {
            auto tmp = *this;
            ++(*this);
            return tmp;
        }

        // Оператори порівняння з ітератором та вартівником
        constexpr bool operator==(const iterator_impl& other) const {
            return current_ == other.current_;
        }

        constexpr bool operator==(const BaseSent& sent) const {
            return current_ == sent;
        }

        // Арифметика випадкового доступу для RandomAccessRange
        constexpr iterator_impl& operator+=(difference_type n)
            requires std::ranges::random_access_range<BaseView> {
            current_ += n * stride_;
            return *this;
        }

        constexpr iterator_impl& operator-=(difference_type n)
            requires std::ranges::random_access_range<BaseView> {
            current_ -= n * stride_;
            return *this;
        }

        constexpr reference operator[](difference_type n) const
            requires std::ranges::random_access_range<BaseView> {
            return *(current_ + n * stride_);
        }

        friend iterator_impl operator+(iterator_impl i, difference_type n)
            requires std::ranges::random_access_range<BaseView> {
            i += n;
            return i;
        }

        friend iterator_impl operator+(difference_type n, iterator_impl i)
            requires std::ranges::random_access_range<BaseView> {
            i += n;
            return i;
        }

        friend iterator_impl operator-(iterator_impl i, difference_type n)
            requires std::ranges::random_access_range<BaseView> {
            i -= n;
            return i;
        }

        friend difference_type operator-(const iterator_impl& x, const iterator_impl& y)
            requires std::ranges::random_access_range<BaseView> {
            return (x.current_ - y.current_) / x.stride_;
        }

        friend class iterator_impl<!IsConst>;
    };

public:
    stride_view() = default;

    constexpr explicit stride_view(V base, std::ranges::range_difference_t<V> stride)
        : base_(std::move(base)), stride_(stride) {
        assert(stride_ > 0 && "Крок stride_view повинен бути строго більшим за нуль!");
    }

    constexpr V base() const& requires std::copy_constructible<V> { return base_; }
    constexpr V base() && { return std::move(base_); }
    constexpr std::ranges::range_difference_t<V> stride() const { return stride_; }

    constexpr auto begin() {
        return iterator_impl<false>(std::ranges::begin(base_), std::ranges::end(base_), stride_);
    }

    constexpr auto begin() const requires std::ranges::range<const V> {
        return iterator_impl<true>(std::ranges::begin(base_), std::ranges::end(base_), stride_);
    }

    constexpr auto end() {
        return std::ranges::end(base_);
    }

    constexpr auto end() const requires std::ranges::range<const V> {
        return std::ranges::end(base_);
    }
};

// CTAD (Class Template Argument Deduction) guide
template <typename R>
stride_view(R&&, std::ranges::range_difference_t<R>) -> stride_view<std::views::all_t<R>>;

namespace views {

// Об'єкт замикання адаптера для підтримки pipe синтаксису
struct stride_adapter_closure {
    std::ptrdiff_t stride_ = 1;

    constexpr stride_adapter_closure(std::ptrdiff_t n) : stride_(n) {}

    template <std::ranges::viewable_range R>
    constexpr auto operator()(R&& r) const {
        return stride_view<std::views::all_t<R>>(std::forward<R>(r), stride_);
    }
};

// Оператор pipe | для зв'язування діапазону та замикання
template <std::ranges::viewable_range R>
constexpr auto operator|(R&& r, const stride_adapter_closure& closure) {
    return closure(std::forward<R>(r));
}

// Заводська функція створення адаптера
inline constexpr auto stride = [](std::ptrdiff_t n) {
    return stride_adapter_closure(n);
};

} // namespace views

} // namespace custom

int main() {
    std::vector<int> numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};

    // 1. Пряме створення вигляду
    custom::stride_view direct_view(std::views::all(numbers), 3);
    std::cout << "Прямий stride(3): ";
    for (int n : direct_view) {
        std::cout << n << " "; // Виведе: 1 4 7 10
    }
    std::cout << "\n";

    // 2. Композиція у конвеєрі через operator|
    using namespace custom::views;
    auto pipeline = numbers 
                  | std::views::filter([](int x) { return x % 2 == 0; }) // 2, 4, 6, 8, 10, 12
                  | stride(2)                                             // 2, 6, 10
                  | std::views::transform([](int x) { return x * x; });  // 4, 36, 100

    std::cout << "Конвеєр (filter -> stride(2) -> transform): ";
    for (int val : pipeline) {
        std::cout << val << " "; // Виведе: 4 36 100
    }
    std::cout << "\n";

    // Static assertions для перевірки відповідності концептам C++20
    static_assert(std::ranges::view<custom::stride_view<std::views::all_t<std::vector<int>&>>>);
    static_assert(std::ranges::random_access_range<decltype(direct_view)>);

    return 0;
}
