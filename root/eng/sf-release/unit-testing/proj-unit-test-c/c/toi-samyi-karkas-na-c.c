/* C: свіжий стан — змінна на стеку, помирає сама */
static void push_on_full_is_rejected(void) {
    rb_t rb; rb_init(&rb);
    for (int i = 0; i < (int)RB_CAP; i++) rb_push(&rb, i);
    CHECK(rb_push(&rb, 99) == false);
    CHECK_EQ_INT(rb_count(&rb), RB_CAP);
}

/* реєстрація — масив, який пишуть руками, після всіх тіл */
static const tt_case CASES[] = {
    { "новий буфер порожній",          new_buffer_is_empty },
    { "push у повний буфер відмовляє", push_on_full_is_rejected },
};

/* вихід із провалу — нелокальний перехід */
_Noreturn void tt_fail(const char *file, int line) {
    tt_file = file; tt_line = line;
    longjmp(tt_abort, 1);
}
