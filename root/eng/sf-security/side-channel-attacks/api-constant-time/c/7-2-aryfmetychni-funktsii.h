/* Додавання двох 256-бітних чисел із поверненням біта перенесення */
uint64_t ct_bn256_add(ct_bn256_t *r, const ct_bn256_t *a, const ct_bn256_t *b);

/* Віднімання двох 256-бітних чисел із поверненням біта позики */
uint64_t ct_bn256_sub(ct_bn256_t *r, const ct_bn256_t *a, const ct_bn256_t *b);

/* Модульне додавання r = (a + b) mod p */
void ct_bn256_mod_add(ct_bn256_t *r, const ct_bn256_t *a, const ct_bn256_t *b, const ct_bn256_t *p);

/* Модульне віднімання r = (a - b) mod p */
void ct_bn256_mod_sub(ct_bn256_t *r, const ct_bn256_t *a, const ct_bn256_t *b, const ct_bn256_t *p);

/* Умовний вибір 256-бітного числа */
void ct_bn256_select(ct_choice_t c, ct_bn256_t *r, const ct_bn256_t *a, const ct_bn256_t *b);

/* Умовна перестановка двох 256-бітних чисел */
void ct_bn256_cswap(ct_choice_t c, ct_bn256_t *a, ct_bn256_t *b);
