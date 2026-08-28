// Сучасний надійний шаблон сумісності
#if defined(__has_include)
    #if __has_include(<version>)
        #include <version>
    #endif
#endif

#if defined(__cpp_lib_string_view) && (__cpp_lib_string_view >= 201606L)
    #include <string_view>
    namespace compat {
        using string_view = std::string_view;
    }
#else
    #include "compat/fallback_string_view.hpp"
    namespace compat {
        using string_view = compat::fallback_string_view;
    }
#endif
