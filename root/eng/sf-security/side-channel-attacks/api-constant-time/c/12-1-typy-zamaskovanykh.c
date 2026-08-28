#define CT_MAX_MASKING_SHARES 8

typedef struct {
    uint8_t shares[CT_MAX_MASKING_SHARES];
    size_t order; /* Порядок маскування d (кількість часток = d + 1) */
} ct_masked_byte_t;

typedef struct {
    uint32_t shares[CT_MAX_MASKING_SHARES];
    size_t order;
} ct_masked_word32_t;
