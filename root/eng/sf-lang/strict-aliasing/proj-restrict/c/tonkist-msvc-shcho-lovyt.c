// portable_restrict.h — один макрос RESTRICT на всі компілятори й обидві мови
#if defined(__cplusplus)
    #if defined(_MSC_VER)
        #define RESTRICT __restrict
    #elif defined(__GNUC__) || defined(__clang__)
        #define RESTRICT __restrict__
    #else
        #define RESTRICT            /* невідомий компілятор — просто прибрати */
    #endif
#else                                /* чистий C */
    #if __STDC_VERSION__ >= 199901L  /* C99 і новіші — є справжнє restrict */
        #define RESTRICT restrict
    #elif defined(_MSC_VER)
        #define RESTRICT __restrict
    #else
        #define RESTRICT
    #endif
#endif
