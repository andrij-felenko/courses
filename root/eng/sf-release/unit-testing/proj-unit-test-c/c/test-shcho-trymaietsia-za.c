/* ТАК РОБИТИ НЕ ТРЕБА */
static void internals_after_wraparound(void) {
    rb_t rb; rb_init(&rb);
    int i, x;
    for (i = 0; i < (int)RB_CAP; i++) rb_push(&rb, i);
    for (i = 0; i < (int)RB_CAP; i++) rb_pop(&rb, &x);
    rb_push(&rb, 7);
    rb_push(&rb, 8);
    CHECK_EQ_INT(rb.head,  2);
    CHECK_EQ_INT(rb.tail,  0);
    CHECK_EQ_INT(rb.count, 2);
}
