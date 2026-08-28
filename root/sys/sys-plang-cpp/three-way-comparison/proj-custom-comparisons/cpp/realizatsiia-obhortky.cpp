#include <iostream>
#include <memory>
#include <compare>

template <class T>
class DeepPtr {
    std::unique_ptr<T> ptr;

public:
    DeepPtr() = default;
    explicit DeepPtr(T* p) : ptr(p) {}
    explicit DeepPtr(std::unique_ptr<T> p) : ptr(std::move(p)) {}

    T* get() const noexcept { return ptr.get(); }
    T& operator*() const noexcept { return *ptr; }
    T* operator->() const noexcept { return ptr.get(); }
    explicit operator bool() const noexcept { return static_cast<bool>(ptr); }

    // Глибоке тричленне порівняння з коректною обробкою nullptr
    friend auto operator<=>(const DeepPtr& a, const DeepPtr& b) noexcept(
        noexcept(std::declval<const T&>() <=> std::declval<const T&>()))
    {
        if (a.ptr == b.ptr) return std::strong_ordering::equal;
        if (!a.ptr) return std::strong_ordering::less;
        if (!b.ptr) return std::strong_ordering::greater;
        return *a.ptr <=> *b.ptr;
    }

    friend bool operator==(const DeepPtr& a, const DeepPtr& b) noexcept(
        noexcept(std::declval<const T&>() == std::declval<const T&>()))
    {
        if (a.ptr == b.ptr) return true;
        if (!a.ptr || !b.ptr) return false;
        return *a.ptr == *b.ptr;
    }
};
