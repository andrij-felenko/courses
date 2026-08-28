#pragma once

#include "compat/config.hpp"
#include <cstddef>
#include <type_traits>

#if defined(__cpp_lib_span) && __cpp_lib_span >= 202002L
    #include <span>
    namespace compat {
        using std::span;
        inline constexpr std::size_t dynamic_extent = std::dynamic_extent;
    }
#else
    namespace compat {
        inline constexpr std::size_t dynamic_extent = static_cast<std::size_t>(-1);

        template <typename T, std::size_t Extent = dynamic_extent>
        class span {
        public:
            using element_type = T;
            using value_type = std::remove_cv_t<T>;
            using size_type = std::size_t;
            using pointer = T*;
            using reference = T&;
            using iterator = T*;

            constexpr span() noexcept : ptr_(nullptr), size_(0) {}
            constexpr span(pointer ptr, size_type count) noexcept : ptr_(ptr), size_(count) {}
            constexpr span(pointer first, pointer last) noexcept 
                : ptr_(first), size_(static_cast<size_type>(last - first)) {}

            template <std::size_t N>
            constexpr span(element_type (&arr)[N]) noexcept : ptr_(arr), size_(N) {}

            [[nodiscard]] constexpr pointer data() const noexcept { return ptr_; }
            [[nodiscard]] constexpr size_type size() const noexcept { return size_; }
            [[nodiscard]] constexpr size_type size_bytes() const noexcept { return size_ * sizeof(T); }
            [[nodiscard]] constexpr bool empty() const noexcept { return size_ == 0; }

            constexpr reference operator[](size_type idx) const noexcept { return ptr_[idx]; }
            constexpr iterator begin() const noexcept { return ptr_; }
            constexpr iterator end() const noexcept { return ptr_ + size_; }

        private:
            pointer ptr_;
            size_type size_;
        };
    }
#endif
