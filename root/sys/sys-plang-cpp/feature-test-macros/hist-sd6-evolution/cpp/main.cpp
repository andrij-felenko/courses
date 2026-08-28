#if defined(__clang__)
    #if __has_feature(cxx_rvalue_references)
        #define HAS_MOVE_SEMANTICS 1
    #endif
#elif defined(__GNUC__)
    #if (__GNUC__ > 4 || (__GNUC__ == 4 && __GNUC_MINOR__ >= 3)) && defined(__GXX_EXPERIMENTAL_CXX0X__)
        #define HAS_MOVE_SEMANTICS 1
    #endif
#elif defined(_MSC_VER)
    #if _MSC_VER >= 1600
        #define HAS_MOVE_SEMANTICS 1
    #endif
#endif
