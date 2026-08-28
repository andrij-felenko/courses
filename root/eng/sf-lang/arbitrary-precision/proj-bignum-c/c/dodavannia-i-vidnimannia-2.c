// r[0..na−1] := a − b, вимога |a| ≥ |b|; повертає довжину після зрізання
static size_t sub_abs(limb *r, const limb *a, size_t na,
                               const limb *b, size_t nb) {
    limb borrow = 0;
    for (size_t i = 0; i < nb; i++) {
        limb ai = a[i], bi = b[i];
        limb t  = ai - bi;
        limb br = (ai < bi);
        limb u  = t - borrow;
        br |= (t < borrow);
        r[i]   = u;
        borrow = br;
    }
    for (size_t i = nb; i < na; i++) {
        limb ai = a[i];
        r[i]   = ai - borrow;
        borrow = (ai < borrow);
    }
    size_t n = na;              // позики назовні бути не може: |a| ≥ |b|
    while (n > 0 && r[n - 1] == 0) n--;
    return n;
}
