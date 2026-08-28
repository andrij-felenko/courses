/* категорія: скільки значущих бітів у |v| (для нуля — нуль) */
static int category(int v) {
    int a = abs(v), s = 0;
    while (a) { s++; a >>= 1; }
    return s;
}

/* біти амплітуди в size розрядах: додатні — як є; від'ємні — (v−1) */
static unsigned amplitude(int v, int size) {
    if (v < 0) v -= 1;
    return (unsigned) v & ((1u << size) - 1);
}
