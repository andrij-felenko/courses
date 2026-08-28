/* Знакова цифра вікна скаляра */
typedef struct {
    int32_t value;
    bool is_negative;
} signed_digit_t;

/* Вилучення знакової цифри з переносом */
signed_digit_t extract_signed_window(const fe256_t *scalar, uint32_t window_idx, uint32_t c, int32_t *carry) {
    uint32_t raw = extract_window(scalar, window_idx, c) + (uint32_t)(*carry);
    *carry = 0;

    int32_t half = 1 << (c - 1);
    int32_t max_val = 1 << c;
    signed_digit_t res;

    if ((int32_t)raw >= half) {
        res.value = max_val - (int32_t)raw;
        res.is_negative = true;
        *carry = 1;
    } else {
        res.value = (int32_t)raw;
        res.is_negative = false;
    }
    return res;
}
