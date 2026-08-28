/* Постійночасове пряме теоретико-числове перетворення (NTT) */
void ct_poly_ntt(ct_pqc_poly256_t *p, const int16_t *zetas_table, int16_t q);

/* Постійночасове обернене теоретико-числове перетворення (InvNTT) */
void ct_poly_invntt(ct_pqc_poly256_t *p, const int16_t *zetas_inv_table, int16_t q);

/* Поточкове множення двох поліномів у просторі NTT */
void ct_poly_basemul(ct_pqc_poly256_t *r, const ct_pqc_poly256_t *a, const ct_pqc_poly256_t *b, int16_t q);

/* Постійночасове зведення за модулем q за алгоритмом Барретта/Монтгомері */
void ct_poly_reduce_coefficients(ct_pqc_poly256_t *p, int16_t q);
