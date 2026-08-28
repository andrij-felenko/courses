#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#if defined(_WIN32)
#include <windows.h>
#define SECURE_ZERO(ptr, sz) SecureZeroMemory((ptr), (sz))
#else
#define SECURE_ZERO(ptr, sz) explicit_bzero((ptr), (sz))
#endif

typedef enum {
    SASL_OK = 0,
    SASL_CONTINUE = 1,
    SASL_ERR_AUTH = -1,
    SASL_ERR_SYNTAX = -2,
    SASL_ERR_NOMEM = -3
} sasl_result_t;

typedef enum {
    SASL_STATE_INIT = 0,
    SASL_STATE_STEP,
    SASL_STATE_DONE,
    SASL_STATE_FAIL
} sasl_state_t;

/* Безпечний буфер для передавання бінарних блоків SASL */
typedef struct {
    uint8_t *data;
    size_t len;
} sasl_buffer_t;

/* Структура облікових даних клієнта */
typedef struct {
    const char *authzid;  /* Ідентифікатор авторизації (може бути NULL) */
    const char *authcid;  /* Логін користувача (обов'язковий) */
    const char *password; /* Пароль користувача (обов'язковий) */
} sasl_credentials_t;

/* Інтерфейс під'єднуваного криптографічного механізму */
struct sasl_mech_s;
typedef struct sasl_mech_s sasl_mech_t;

struct sasl_mech_s {
    const char *name;
    sasl_result_t (*client_start)(void **ctx, const sasl_credentials_t *cred, sasl_buffer_t *out);
    sasl_result_t (*client_step)(void *ctx, const sasl_buffer_t *in, sasl_buffer_t *out);
    void (*client_destroy)(void *ctx);

    sasl_result_t (*server_start)(void **ctx, sasl_buffer_t *out);
    sasl_result_t (*server_step)(void *ctx, const sasl_buffer_t *in, sasl_buffer_t *out,
                                char *auth_user, size_t user_max);
    void (*server_destroy)(void *ctx);
};

/* Контекст клієнтської сесії */
typedef struct {
    const sasl_mech_t *mech;
    void *mech_ctx;
    sasl_state_t state;
    sasl_credentials_t cred;
} sasl_client_session_t;

/* Звільнення буфера з обов'язковим зануленням пам'яті */
void sasl_buffer_free(sasl_buffer_t *buf) {
    if (buf && buf->data) {
        SECURE_ZERO(buf->data, buf->len);
        free(buf->data);
        buf->data = NULL;
        buf->len = 0;
    }
}
