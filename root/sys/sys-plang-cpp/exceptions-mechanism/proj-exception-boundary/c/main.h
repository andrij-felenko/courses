#ifndef PARSER_H
#define PARSER_H

/* Експорт. Решта бібліотеки збирається з -fvisibility=hidden. */
#if defined(_WIN32)
#  ifdef PARSER_BUILDING
#    define PARSER_API __declspec(dllexport)
#  else
#    define PARSER_API __declspec(dllimport)
#  endif
#else
#  define PARSER_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
#  define PARSER_NOEXCEPT noexcept   /* з C++17 — частина типу функції */
#else
#  define PARSER_NOEXCEPT
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef enum parser_status {
    PARSER_OK          = 0,
    PARSER_E_ARG       = 1,   /* викличник передав дурницю */
    PARSER_E_SYNTAX    = 2,   /* зіпсовані вхідні дані */
    PARSER_E_IO        = 3,   /* не дочиталися */
    PARSER_E_NO_MEMORY = 4,   /* пам'ять скінчилася */
    PARSER_E_INTERNAL  = 5    /* усе інше — це наша провина */
} parser_status;

/* Неповний тип: назовні є вказівник, розміру й розкладки немає. */
typedef struct parser_ctx parser_ctx;

PARSER_API parser_status parser_create (parser_ctx** out)                 PARSER_NOEXCEPT;
PARSER_API parser_status parser_close  (parser_ctx* ctx)                  PARSER_NOEXCEPT;
PARSER_API void          parser_destroy(parser_ctx* ctx)                  PARSER_NOEXCEPT;

PARSER_API parser_status parser_load   (parser_ctx* ctx, const char* path) PARSER_NOEXCEPT;
PARSER_API parser_status parser_get_int(parser_ctx* ctx, const char* key,
                                        long* out)                        PARSER_NOEXCEPT;

/* Опис останнього збою. Ніколи не NULL; чинний до наступного виклику з цим ctx. */
PARSER_API const char*   parser_last_error(const parser_ctx* ctx)          PARSER_NOEXCEPT;

#ifdef __cplusplus
}
#endif
#endif /* PARSER_H */
