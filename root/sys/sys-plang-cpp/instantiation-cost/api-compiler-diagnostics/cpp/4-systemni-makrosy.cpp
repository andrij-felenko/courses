// Перевірка підтримки явного контролю інстанціації (C++11 extern template)
#if __cplusplus >= 201103L
    #define HAS_EXTERN_TEMPLATE 1
#endif

// Перевірка підтримки C++20 Concepts для скорочення вартості SFINAE
#if defined(__cpp_concepts) && __cpp_concepts >= 201907L
    #define HAS_CPP20_CONCEPTS 1
#endif

// Перевірка підтримки модулів C++20
#if defined(__cpp_modules) && __cpp_modules >= 201907L
    #define HAS_CPP20_MODULES 1
#endif
