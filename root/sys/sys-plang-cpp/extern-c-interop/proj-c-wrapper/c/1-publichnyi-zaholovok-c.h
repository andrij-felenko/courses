#ifndef ENGINE_API_H
#define ENGINE_API_H

#include <stddef.h>
#include <stdint.h>

/* Макрос експорту символів для динамічних бібліотек */
#if defined(_WIN32) || defined(__CYGWIN__)
  #if defined(ENGINE_EXPORTS)
    #define ENGINE_API __declspec(dllexport)
  #else
    #define ENGINE_API __declspec(dllimport)
  #endif
#else
  #if defined(__GNUC__) && __GNUC__ >= 4
    #define ENGINE_API __attribute__((visibility("default")))
  #else
    #define ENGINE_API
  #endif
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* Статусні коди операцій */
typedef enum engine_status_t {
    ENGINE_STATUS_OK               =  0,
    ENGINE_STATUS_ERR_INVALID_ARG  = -1,
    ENGINE_STATUS_ERR_OUT_OF_MEMORY= -2,
    ENGINE_STATUS_ERR_PROCESSING   = -3,
    ENGINE_STATUS_ERR_UNKNOWN      = -4
} engine_status_t;

/* Непрозорий дескриптор (Opaque Handle / Incomplete Type) */
typedef struct engine_ctx_t engine_ctx_t;

/* Сигнатура функції зворотного виклику */
typedef void (*engine_progress_cb)(size_t bytes_processed, void* user_data);

/* Сигнатура функції звільнення користувацького контексту */
typedef void (*engine_cleanup_cb)(void* user_data);

/* Створення нового екземпляра рушія */
ENGINE_API engine_status_t engine_create(const char* algorithm_name, engine_ctx_t** out_ctx);

/* Безпечне знищення екземпляра рушія */
ENGINE_API void            engine_destroy(engine_ctx_t* ctx);

/* Потокова обробка блоку пам'яті */
ENGINE_API engine_status_t engine_process(engine_ctx_t* ctx,
                                          const uint8_t* input,
                                          size_input_len,
                                          uint8_t* output,
                                          size_t* inout_output_len);

/* Реєстрація функції зворотного виклику з користувацьким контекстом */
ENGINE_API engine_status_t engine_set_progress_callback(engine_ctx_t* ctx,
                                                        engine_progress_cb cb,
                                                        void* user_data,
                                                        engine_cleanup_cb cleanup);

/* Отримання тексту останньої помилки для поточного потоку */
ENGINE_API const char*     engine_get_last_error(void);

#ifdef __cplusplus
}
#endif

#endif /* ENGINE_API_H */
