/* Пакетне обернення масиву елементів поля за методом Монтгомері */
void batch_invert(fe256_t *inverses, const fe256_t *inputs, size_t count) {
    if (count == 0) return;

    fe256_t *prefix_prod = (fe256_t*)malloc(count * sizeof(fe256_t));
    if (!prefix_prod) return;

    prefix_prod[0] = inputs[0];
    for (size_t i = 1; i < count; ++i) {
        fe256_mul(&prefix_prod[i], &prefix_prod[i - 1], &inputs[i]);
    }

    /* Єдина інверсія спільного добутку всіх елементів */
    fe256_t all_inv;
    fe256_inv(&all_inv, &prefix_prod[count - 1]);

    /* Зворотний прохід для відновлення окремих інверсій */
    for (size_t i = count - 1; i > 0; --i) {
        fe256_mul(&inverses[i], &all_inv, &prefix_prod[i - 1]);
        fe256_mul(&all_inv, &all_inv, &inputs[i]);
    }
    inverses[0] = all_inv;

    free(prefix_prod);
}
