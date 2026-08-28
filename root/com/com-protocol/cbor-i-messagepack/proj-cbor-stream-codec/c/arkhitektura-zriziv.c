#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef enum {
    CBOR_OK = 0,
    CBOR_ERR_BUFFER_OVERFLOW,
    CBOR_ERR_UNEXPECTED_EOF,
    CBOR_ERR_INVALID_HEADER,
    CBOR_ERR_UNSUPPORTED_TYPE
} cbor_error_t;

typedef enum {
    CBOR_TYPE_UINT,
    CBOR_TYPE_NINT,
    CBOR_TYPE_BSTR,
    CBOR_TYPE_TSTR,
    CBOR_TYPE_ARRAY,
    CBOR_TYPE_MAP,
    CBOR_TYPE_TAG,
    CBOR_TYPE_BOOL,
    CBOR_TYPE_NULL,
    CBOR_TYPE_FLOAT16,
    CBOR_TYPE_FLOAT32,
    CBOR_TYPE_FLOAT64
} cbor_item_type_t;

typedef struct {
    const uint8_t *ptr;
    size_t len;
} cbor_slice_t;

typedef struct {
    cbor_item_type_t type;
    union {
        uint64_t uint_val;
        int64_t  nint_val;
        cbor_slice_t slice;
        size_t container_len;
        uint64_t tag_val;
        bool bool_val;
        float float_val;
        double double_val;
    } as;
} cbor_value_t;

typedef struct {
    const uint8_t *data;
    size_t size;
    size_t offset;
} cbor_reader_t;

typedef struct {
    uint8_t *data;
    size_t capacity;
    size_t offset;
} cbor_writer_t;
