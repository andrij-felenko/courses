// Кросплатформний шаблон макроса
#if defined(_MSC_VER) && !defined(__clang__)
    #define COURSES_NO_UNIQUE_ADDRESS [[msvc::no_unique_address]]
#else
    #define COURSES_NO_UNIQUE_ADDRESS [[no_unique_address]]
#endif

struct PortableHolder {
    int* ptr;
    COURSES_NO_UNIQUE_ADDRESS Empty deleter;
};
