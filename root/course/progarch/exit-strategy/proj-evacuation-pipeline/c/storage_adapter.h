/* storage_adapter.h — Портативний C-інтерфейс сховища об'єктів */
#ifndef STORAGE_ADAPTER_H
#define STORAGE_ADAPTER_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct storage_adapter storage_adapter_t;

/* Коди помилок адаптера сховища */
typedef enum {
    STORAGE_OK = 0,
    STORAGE_ERR_NOT_FOUND = -1,
    STORAGE_ERR_ACCESS_DENIED = -2,
    STORAGE_ERR_NETWORK = -3,
    STORAGE_ERR_IO = -4,
    STORAGE_ERR_INVALID_PARAM = -5
} storage_err_t;

/* Таблиця віртуальних методів (VTable) для C-адаптера */
struct storage_adapter_ops {
    storage_err_t (*write_object)(storage_adapter_t *self, const char *key, const void *buf, size_t len);
    storage_err_t (*read_object)(storage_adapter_t *self, const char *key, void *buf, size_t max_len, size_t *out_len);
    storage_err_t (*delete_object)(storage_adapter_t *self, const char *key);
    void (*destroy)(storage_adapter_t *self);
};

struct storage_adapter {
    const struct storage_adapter_ops *ops;
    void *ctx; /* Приватний контекст реалізації (креденціали, fd, сокети) */
};

/* Фабричні функції для створення конкретних адаптерів */
storage_adapter_t *storage_adapter_create_posix(const char *base_dir);
storage_adapter_t *storage_adapter_create_cloud(const char *endpoint, const char *bucket, const char *access_key);

#ifdef __cplusplus
}
#endif

#endif /* STORAGE_ADAPTER_H */
