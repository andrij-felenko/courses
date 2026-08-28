// compat/expected.hpp
#pragma once

#include "version_check.hpp"

#if defined(__cpp_lib_expected) && (__cpp_lib_expected >= 202202L)

    #include <expected>

    namespace compat {
        template <typename T, typename E>
        using expected = std::expected<T, E>;

        template <typename E>
        using unexpected = std::unexpected<E>;
    }

#else

    #include <variant>
    #include <utility>
    #include <stdexcept>

    namespace compat {

        template <typename E>
        class unexpected {
        public:
            constexpr explicit unexpected(const E& e) : error_(e) {}
            constexpr explicit unexpected(E&& e) : error_(std::move(e)) {}
            constexpr const E& error() const noexcept { return error_; }
            constexpr E& error() noexcept { return error_; }
        private:
            E error_;
        };

        template <typename T, typename E>
        class expected {
        public:
            constexpr expected(const T& val) : storage_(val) {}
            constexpr expected(T&& val) : storage_(std::move(val)) {}
            constexpr expected(const unexpected<E>& unexp) : storage_(unexp) {}
            constexpr expected(unexpected<E>&& unexp) : storage_(std::move(unexp)) {}

            constexpr bool has_value() const noexcept {
                return std::holds_alternative<T>(storage_);
            }

            constexpr explicit operator bool() const noexcept {
                return has_value();
            }

            constexpr const T& value() const {
                if (!has_value()) {
                    throw std::runtime_error("Attempt to access value of unexpected result");
                }
                return std::get<T>(storage_);
            }

            constexpr const E& error() const {
                return std::get<unexpected<E>>(storage_).error();
            }

            constexpr const T& value_or(const T& default_val) const noexcept {
                return has_value() ? std::get<T>(storage_) : default_val;
            }

        private:
            std::variant<T, unexpected<E>> storage_;
        };

    } // namespace compat

#endif
