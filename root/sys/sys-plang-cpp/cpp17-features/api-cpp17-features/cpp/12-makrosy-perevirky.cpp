#include <version> // C++20, або відповідний заголовок у C++17

#if defined(__cpp_structured_bindings) && __cpp_structured_bindings >= 201606L
    auto [first, second] = get_pair();
#endif

#if defined(__cpp_if_constexpr) && __cpp_if_constexpr >= 201606L
    if constexpr (std::is_integral_v<T>) { ... }
#endif

#if __has_include(<filesystem>)
    #include <filesystem>
    namespace fs = std::filesystem;
#elif __has_include(<experimental/filesystem>)
    #include <experimental/filesystem>
    namespace fs = std::experimental::filesystem;
#endif
