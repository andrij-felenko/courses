#pragma once

#include "compat/config.hpp"
#include <utility>
#include <type_traits>

#if defined(__cpp_lib_expected) && __cpp_lib_expected >= 202202L
    #include <expected>
    namespace compat {
        using std::expected;
        using std::unexpected;
        using std::unexpect;
        using std::unexpect_t;
    }
#else
    namespace compat {
        template <typename E>
        class unexpected {
        public:
            constexpr explicit unexpected(const E& e) : error_(e) {}
            constexpr explicit unexpected(E&& e) : error_(std::move(e)) {}
            [[nodiscard]] constexpr const E& error() const& noexcept { return error_; }
            [[nodiscard]] constexpr E& error() & noexcept { return error_; }
            [[nodiscard]] constexpr E&& error() && noexcept { return std::move(error_); }
        private:
            E error_;
        };

        template <typename E>
        unexpected(E) -> unexpected<E>;

        struct unexpect_t { explicit unexpect_t() = default; };
        inline constexpr unexpect_t unexpect{};

        template <typename T, typename E>
        class expected {
        public:
            using value_type = T;
            using error_type = E;
            using unexpected_type = unexpected<E>;

            constexpr expected(const T& val) : has_val_(true), val_(val) {}
            constexpr expected(T&& val) : has_val_(true), val_(std::move(val)) {}
            constexpr expected(const unexpected<E>& unexp) : has_val_(false), err_(unexp.error()) {}
            constexpr expected(unexpected<E>&& unexp) : has_val_(false), err_(std::move(unexp.error())) {}

            ~expected() {
                if (has_val_) { val_.~T(); } else { err_.~E(); }
            }

            [[nodiscard]] constexpr bool has_value() const noexcept { return has_val_; }
            constexpr explicit operator bool() const noexcept { return has_val_; }

            constexpr const T& value() const& { return val_; }
            constexpr T& value() & { return val_; }
            constexpr const T* operator->() const noexcept { return &val_; }
            constexpr T* operator->() noexcept { return &val_; }

            constexpr const E& error() const& noexcept { return err_; }
            constexpr E& error() & noexcept { return err_; }

        private:
            bool has_val_;
            union {
                T val_;
                E err_;
            };
        };
    }
#endif
