/* Пакетне модульне обернення k елементів: out[i] = in[i]^-1 mod N */
void mont_batch_invert64(const mont_ctx64_t *ctx, const uint64_t *in, uint64_t *out, size_t k) {
    if (k == 0) return;
    if (k == 1) {
        /* Одне число: піднесення до степеня N - 2 за малою теоремою Ферма */
        out[0] = mont_pow_ladder64(ctx, in[0], ctx->n - 2);
        return;
    }

    /* 1. Виділяємо масив для префіксних добутків у просторі Монтгомері */
    uint64_t prod[k];
    uint64_t in_bar[k];
    for (size_t i = 0; i < k; ++i) {
        in_bar[i] = mont_to_domain64(ctx, in[i]);
    }

    prod[0] = in_bar[0];
    for (size_t i = 1; i < k; ++i) {
        prod[i] = mont_mul64(ctx, prod[i - 1], in_bar[i]);
    }

    /* 2. Обчислюємо єдине обернене значення для повного добутку */
    uint64_t full_inv_normal = mont_pow_ladder64(ctx, mont_from_domain64(ctx, prod[k - 1]), ctx->n - 2);
    uint64_t inv = mont_to_domain64(ctx, full_inv_normal);

    /* 3. Зворотний прохід для відновлення окремих обернених */
    for (size_t i = k - 1; i > 0; --i) {
        out[i] = mont_from_domain64(ctx, mont_mul64(ctx, inv, prod[i - 1]));
        inv = mont_mul64(ctx, inv, in_bar[i]);
    }
    out[0] = mont_from_domain64(ctx, inv);
}
