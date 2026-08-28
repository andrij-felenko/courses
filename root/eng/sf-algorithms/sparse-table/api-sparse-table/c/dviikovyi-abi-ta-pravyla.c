/* Макроси експорту двійкових символів для мови C */
#if defined(_WIN32) || defined(__CYGWIN__)
    #if defined(SPARSE_TABLE_BUILD_DLL)
        #define SPARSE_TABLE_API __declspec(dllexport)
    #else
        #define SPARSE_TABLE_API __declspec(dllimport)
    #endif
#elif defined(__GNUC__) && __GNUC__ >= 4
    #define SPARSE_TABLE_API __attribute__((visibility("default")))
#else
    #define SPARSE_TABLE_API
#endif

SPARSE_TABLE_API sparse_table_t *st_create_api(const int32_t *arr, size_t n);
