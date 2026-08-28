/* mylib_export.h — версія для мови C */
#ifndef MYLIB_EXPORT_H
#define MYLIB_EXPORT_H

#if defined(MYLIB_STATIC_DEFINE)
    /* Для статичної бібліотеки атрибути експорту не потрібні */
    #define MYLIB_API
    #define MYLIB_LOCAL
#else
    #if defined(_WIN32) || defined(__CYGWIN__)
        #if defined(MYLIB_EXPORTS)
            /* Збірка DLL під Windows: експортуємо символи у EAT */
            #define MYLIB_API __declspec(dllexport)
        #else
            /* Споживання DLL під Windows: імпортуємо символи через IAT */
            #define MYLIB_API __declspec(dllimport)
        #endif
        #define MYLIB_LOCAL
    #else
        #if defined(__GNUC__) && __GNUC__ >= 4
            #define MYLIB_API   __attribute__((visibility("default")))
            #define MYLIB_LOCAL __attribute__((visibility("hidden")))
        #else
            #define MYLIB_API
            #define MYLIB_LOCAL
        #endif
    #endif
#endif

#endif /* MYLIB_EXPORT_H */
