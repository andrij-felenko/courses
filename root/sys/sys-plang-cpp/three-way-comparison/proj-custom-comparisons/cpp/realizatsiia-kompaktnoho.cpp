#include <iterator>
#include <compare>
#include <cstddef>
#include <type_traits>

template <class T>
class CompactSpanIterator {
    T* ptr{nullptr};

public:
    using iterator_concept  = std::contiguous_iterator_tag;
    using iterator_category = std::random_access_iterator_tag;
    using value_type        = std::remove_cv_t<T>;
    using difference_type   = std::ptrdiff_t;
    using pointer           = T*;
    using reference         = T&;

    constexpr CompactSpanIterator() noexcept = default;
    constexpr explicit CompactSpanIterator(T* p) noexcept : ptr(p) {}

    // Конвертація з non-const у const ітератор
    template <class U>
        requires std::is_convertible_v<U*, T*>
    constexpr CompactSpanIterator(const CompactSpanIterator<U>& other) noexcept
        : ptr(other.base()) {}

    constexpr T* base() const noexcept { return ptr; }
    constexpr reference operator*() const noexcept { return *ptr; }
    constexpr pointer operator->() const noexcept { return ptr; }

    constexpr CompactSpanIterator& operator++() noexcept { ++ptr; return *this; }
    constexpr CompactSpanIterator operator++(int) noexcept { auto tmp = *this; ++ptr; return tmp; }
    constexpr CompactSpanIterator& operator--() noexcept { --ptr; return *this; }
    constexpr CompactSpanIterator operator--(int) noexcept { auto tmp = *this; --ptr; return tmp; }

    constexpr CompactSpanIterator& operator+=(difference_type n) noexcept { ptr += n; return *this; }
    constexpr CompactSpanIterator& operator-=(difference_type n) noexcept { ptr -= n; return *this; }
    constexpr reference operator[](difference_type n) const noexcept { return ptr[n]; }

    friend constexpr difference_type operator-(const CompactSpanIterator& a, const CompactSpanIterator& b) noexcept {
        return a.ptr - b.ptr;
    }
    friend constexpr CompactSpanIterator operator+(CompactSpanIterator it, difference_type n) noexcept {
        return it += n;
    }
    friend constexpr CompactSpanIterator operator+(difference_type n, CompactSpanIterator it) noexcept {
        return it += n;
    }
    friend constexpr CompactSpanIterator operator-(CompactSpanIterator it, difference_type n) noexcept {
        return it -= n;
    }

    // Усі 6 операторів порівняння синтезуються з цих двох рядків!
    friend constexpr std::strong_ordering operator<=>(
        const CompactSpanIterator& a, const CompactSpanIterator& b) noexcept
    {
        return a.ptr <=> b.ptr;
    }

    friend constexpr bool operator==(
        const CompactSpanIterator& a, const CompactSpanIterator& b) noexcept
    {
        return a.ptr == b.ptr;
    }
};
