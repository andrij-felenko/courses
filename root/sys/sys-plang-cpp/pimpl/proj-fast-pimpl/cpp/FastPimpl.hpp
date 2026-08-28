// ==================== Сучасний C++ (FastPimpl Wrapper) ====================
// FastPimpl.hpp — Загальний шаблонний контейнер буфера
#ifndef FAST_PIMPL_HPP
#define FAST_PIMPL_HPP

#include <cstddef>
#include <new>
#include <utility>

template <typename T, std::size_t Size, std::size_t Alignment = alignof(std::max_align_t)>
class FastPimpl {
    // Вирівняне сире сховище байтів
    alignas(Alignment) std::byte storage_[Size];

    T* ptr() noexcept {
        return std::launder(reinterpret_cast<T*>(storage_));
    }

    const T* ptr() const noexcept {
        return std::launder(reinterpret_cast<const T*>(storage_));
    }

public:
    template <typename... Args>
    explicit FastPimpl(Args&&... args) {
        validate();
        ::new (static_cast<void*>(storage_)) T(std::forward<Args>(args)...);
    }

    ~FastPimpl() {
        validate();
        ptr()->~T();
    }

    FastPimpl(FastPimpl&& other) noexcept {
        validate();
        ::new (static_cast<void*>(storage_)) T(std::move(*other.ptr()));
    }

    FastPimpl& operator=(FastPimpl&& other) noexcept {
        if (this != &other) {
            validate();
            ptr()->~T();
            ::new (static_cast<void*>(storage_)) T(std::move(*other.ptr()));
        }
        return *this;
    }

    FastPimpl(const FastPimpl& other) {
        validate();
        ::new (static_cast<void*>(storage_)) T(*other.ptr());
    }

    FastPimpl& operator=(const FastPimpl& other) {
        if (this != &other) {
            validate();
            *ptr() = *other.ptr();
        }
        return *this;
    }

    T* operator->() noexcept { return ptr(); }
    const T* operator->() const noexcept { return ptr(); }
    T& operator*() noexcept { return *ptr(); }
    const T& operator*() const noexcept { return *ptr(); }

private:
    static void validate() noexcept {
        static_assert(sizeof(T) <= Size, "Розмір буфера FastPimpl менший за sizeof(T)");
        static_assert(alignof(T) <= Alignment, "Вимоги вирівнювання T перевищують Alignment");
    }
};

#endif // FAST_PIMPL_HPP
