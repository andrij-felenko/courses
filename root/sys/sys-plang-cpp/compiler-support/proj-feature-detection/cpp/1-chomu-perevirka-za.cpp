// Антипатерн: крихка перевірка за версіями трансляторів
#if defined(__clang__) && (__clang_major__ >= 13)
    #define USE_CONCEPTS 1
#elif defined(__GNUC__) && (__GNUC__ >= 10)
    #define USE_CONCEPTS 1
#elif defined(_MSC_VER) && (_MSC_VER >= 1928)
    #define USE_CONCEPTS 1
#else
    #define USE_CONCEPTS 0
#endif
