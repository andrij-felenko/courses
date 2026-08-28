#include <string_view>

template <class T>
constexpr const char* raw_name() {
#if defined(__clang__) || defined(__GNUC__)
    return __PRETTY_FUNCTION__;
#elif defined(_MSC_VER)
    return __FUNCSIG__;
#else
    return "?";
#endif
}

// g++ дає:   constexpr const char* raw_name() [with T = double]
// clang дає: const char *raw_name() [T = double]
// MSVC дає:  const char *__cdecl raw_name<double>(void)
inline constexpr std::string_view kMark   = "double";
inline constexpr std::string_view kSample = raw_name<double>();
inline constexpr std::size_t      kHead   = kSample.find(kMark);
inline constexpr std::size_t      kTail   = kSample.size() - kHead - kMark.size();

template <class T>
constexpr std::string_view type_name() {
    const std::string_view s = raw_name<T>();
    return s.substr(kHead, s.size() - kHead - kTail);
}
