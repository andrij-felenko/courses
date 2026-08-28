#if defined(__has_include)
    #if __has_include(<version>)
        #include <version>
    #endif
#endif

// Чиста перевірка наявності std::expected
#if defined(__cpp_lib_expected) && (__cpp_lib_expected >= 202202L)
    #include <expected>
    template <typename T, typename E>
    using Result = std::expected<T, E>;
#else
    #include "compat/expected_polyfill.hpp"
    template <typename T, typename E>
    using Result = compat::expected<T, E>;
#endif
