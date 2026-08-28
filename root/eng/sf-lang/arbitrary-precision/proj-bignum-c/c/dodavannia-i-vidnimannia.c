// r[0..na] := a[0..na−1] + b[0..nb−1],  вимога na ≥ nb
// у r має бути місце на na+1 лімб; повертає довжину результату
static size_t add_abs(limb *r, const limb *a, size_t na,
                               const limb *b, size_t nb) {
    limb carry = 0;
    for (size_t i = 0; i < nb; i++) {
        limb ai = a[i], bi = b[i];
        limb s  = ai + bi;
        limb c  = (s < ai);        // загорнулося на a+b
        s += carry;
        c |= (s < carry);          // або вже на додаванні переносу
        r[i]  = s;
        carry = c;
    }
    for (size_t i = nb; i < na; i++) {   // хвіст довшого числа
        limb s = a[i] + carry;
        carry  = (s < carry);
        r[i]   = s;
    }
    r[na] = carry;
    return carry ? na + 1 : na;
}
