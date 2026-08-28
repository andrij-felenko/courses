#pragma once

// 1. Безпечне підключення заголовка версій стандарту
#if defined(__has_include)
    #if __has_include(<version>)
        #include <version>
    #else
        #include <cstddef>
    #endif
#endif

// 2. Атрибути безпеки та діагностики
#if defined(__has_cpp_attribute)
    #if __has_cpp_attribute(nodiscard) >= 201603L
        #define COMPAT_NODISCARD [[nodiscard]]
    #else
        #define COMPAT_NODISCARD
    #endif

    #if __has_cpp_attribute(maybe_unused) >= 201603L
        #define COMPAT_UNUSED [[maybe_unused]]
    #elif defined(__GNUC__) || defined(__clang__)
        #define COMPAT_UNUSED __attribute__((unused))
    #else
        #define COMPAT_UNUSED
    #endif

    #if __has_cpp_attribute(fallthrough) >= 201603L
        #define COMPAT_FALLTHROUGH [[fallthrough]]
    #elif defined(__clang__)
        #define COMPAT_FALLTHROUGH [[clang::fallthrough]]
    #elif defined(__GNUC__) && (__GNUC__ >= 7)
        #define COMPAT_FALLTHROUGH __attribute__((fallthrough))
    #else
        #define COMPAT_FALLTHROUGH ((void)0)
    #endif
#else
    #define COMPAT_NODISCARD
    #define COMPAT_UNUSED
    #define COMPAT_FALLTHROUGH ((void)0)
#endif

// 3. Аліаси та резервні реалізації для std::string_view
#if defined(__cpp_lib_string_view) && (__cpp_lib_string_view >= 201606L)
    #include <string_view>
    namespace compat {
        using string_view = std::string_view;
    }
#else
    #include <string>
    namespace compat {
        // Резервна спрощена реалізація неволодіючого рядка для C++11/14
        class string_view {
            const char* data_;
            std::size_t size_;
        public:
            constexpr string_view() noexcept : data_(nullptr), size_(0) {}
            constexpr string_view(const char* str, std::size_t len) noexcept : data_(str), size_(len) {}
            string_view(const std::string& str) noexcept : data_(str.data()), size_(str.size()) {}
            constexpr const char* data() const noexcept { return data_; }
            constexpr std::size_t size() const noexcept { return size_; }
            constexpr bool empty() const noexcept { return size_ == 0; }
        };
    }
#endif
