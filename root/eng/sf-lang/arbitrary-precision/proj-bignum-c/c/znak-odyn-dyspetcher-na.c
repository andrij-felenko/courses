static void add_signed(big *r, const big *a, const big *b, int bneg) {
    if (a->neg == bneg) {                    // однакові знаки — модулі складаємо
        const big *x = a, *y = b;
        if (x->n < y->n) { const big *t = x; x = y; y = t; }
        big_reserve(r, x->n + 1);
        r->n   = add_abs(r->d, x->d, x->n, y->d, y->n);
        r->neg = a->neg;
    } else {                                 // різні — менший модуль віднімаємо
        int c = cmp_abs(a, b);
        if (c == 0) { r->n = 0; r->neg = 0; return; }
        const big *x = (c > 0) ? a : b;      // більший модуль
        const big *y = (c > 0) ? b : a;
        int sign = (c > 0) ? a->neg : bneg;  // знак більшого модуля
        big_reserve(r, x->n);
        r->n   = sub_abs(r->d, x->d, x->n, y->d, y->n);
        r->neg = sign;
    }
    if (r->n == 0) r->neg = 0;               // єдиний нуль, без «мінус нуля»
}

void big_add(big *r, const big *a, const big *b) { add_signed(r, a, b,  b->neg); }
void big_sub(big *r, const big *a, const big *b) { add_signed(r, a, b, !b->neg); }
