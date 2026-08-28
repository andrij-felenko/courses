// mylib_export.hpp — ідіоматична версія для C++
#ifndef MYLIB_EXPORT_HPP
#define MYLIB_EXPORT_HPP

#if defined(MYLIB_STATIC_DEFINE)
    // Статичне компонування: символи лінкуються безпосередньо
    #define MYLIB_API
    #define MYLIB_LOCAL
#else
    #if defined(_WIN32) || defined(__CYGWIN__)
        #if defined(MYLIB_EXPORTS)
            #define MYLIB_API __declspec(dllexport)
        #else
            #define MYLIB_API __declspec(dllimport)
        #endif
        #define MYLIB_LOCAL
    #else
        #if defined(__GNUC__) && __GNUC__ >= 4
            #define MYLIB_API   [[gnu::visibility("default")]]
            #define MYLIB_LOCAL [[gnu::visibility("hidden")]]
        #else
            #define MYLIB_API
            #define MYLIB_LOCAL
        #endif
    #endif
#endif

#endif // MYLIB_EXPORT_HPP
