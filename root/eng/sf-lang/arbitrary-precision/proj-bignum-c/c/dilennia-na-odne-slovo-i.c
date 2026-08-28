// x := x / v; повертає залишок. Вимога: v ≠ 0
static limb div_limb(big *x, limb v) {
    dlimb rem = 0;
    for (size_t i = x->n; i-- > 0; ) {
        dlimb cur = (rem << LIMB_BITS) | x->d[i];
        x->d[i]   = (limb)(cur / v);
        rem       = cur % v;
    }
    big_trim(x);
    return (limb)rem;
}
