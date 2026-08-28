// один розряд АЛП: повертає біт результату y і перенос-вихід cout
// op: 00=ADD, 01=AND, 10=OR
uint8_t alu_bit(uint8_t a, uint8_t b, uint8_t cin, uint8_t op, uint8_t *cout) {
    uint8_t sum  = a ^ b ^ cin;             // біт суми: непарність трьох входів
    uint8_t cout_add = (a & b) | (cin & (a ^ b));  // перенос: «більшість»
    uint8_t and_ = a & b;                   // a AND b
    uint8_t or_  = a | b;                    // a OR b

    *cout = (op == 0) ? cout_add : 0;        // перенос має сенс лише для ADD
    if (op == 0) return sum;                 // мультиплексор «3-в-1»
    if (op == 1) return and_;                // обирає один із трьох
    return or_;                              // op == 2 → OR
}
