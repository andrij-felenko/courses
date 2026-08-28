#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Коди статусу валідатора */
typedef enum {
    ZC_OK = 0,
    ZC_ERR_BUFFER_TRUNCATED     = -1,
    ZC_ERR_INVALID_ROOT_OFFSET  = -2,
    ZC_ERR_INVALID_VTABLE       = -3,
    ZC_ERR_TABLE_OUT_OF_BOUNDS  = -4,
    ZC_ERR_FIELD_OUT_OF_BOUNDS  = -5,
    ZC_ERR_CYCLE_DETECTED       = -6,
    ZC_ERR_ALIGNMENT_VIOLATION  = -7
} zc_status_t;

/* Контекст верифікатора меж */
typedef struct {
    const uint8_t *buffer;
    size_t size;
    size_t max_depth;
    size_t bytes_budget;
} zc_verifier_t;

/* Ініціалізація та запуск повного валідатора */
zc_status_t zc_verify_buffer(const uint8_t *buf, size_t size, size_t max_depth);

/* Перевірка валідності скалярного діапазону */
bool zc_verify_range(const zc_verifier_t *v, const void *ptr, size_t len, size_t alignment);

/* Безпечний доступ до скалярного поля */
zc_status_t zc_read_field_u32(const uint8_t *table_ptr, const uint8_t *vtable_ptr,
                              uint16_t field_idx, uint32_t default_val, uint32_t *out_val);

/* Безпечний доступ до рядка */
zc_status_t zc_read_field_str(const uint8_t *buf, size_t buf_size,
                              const uint8_t *table_ptr, const uint8_t *vtable_ptr,
                              uint16_t field_idx, const char **out_str, size_t *out_len);
