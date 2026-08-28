// r[0..na+nb−1] := a·b;  r НЕ може збігатися з a чи b
static void mul_basecase(limb *r, const limb *a, size_t na,
                                  const limb *b, size_t nb) {
    memset(r, 0, (na + nb) * sizeof *r);
    for (size_t j = 0; j < nb; j++) {
        limb bj = b[j], carry = 0;
        for (size_t i = 0; i < na; i++) {
            dlimb t  = (dlimb)a[i] * bj + r[i + j] + carry;
            r[i + j] = (limb)t;
            carry    = (limb)(t >> LIMB_BITS);
        }
        r[j + na] = carry;
    }
}
