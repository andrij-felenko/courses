/* Створення замаскованого представлення секретного байта */
int ct_mask_byte_create(ct_masked_byte_t *dst, uint8_t secret, size_t order, ct_rng_fn rng);

/* Відновлення відкритого байта з часток: secret = share_0 ^ share_1 ^ ... ^ share_d */
uint8_t ct_mask_byte_reconstruct(const ct_masked_byte_t *src);

/* Безпечне почасткове додавання за модулем 2 (XOR): z = x ^ y */
void ct_mask_byte_xor(ct_masked_byte_t *z, const ct_masked_byte_t *x, const ct_masked_byte_t *y);

/* Безпечне нелінійне множення ISW: z = x & y */
int ct_mask_byte_and_isw(ct_masked_byte_t *z, const ct_masked_byte_t *x, const ct_masked_byte_t *y, ct_rng_fn rng);
