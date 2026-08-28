/* rb_test.c */
#include "tinytest.h"
#include "rb.h"
#include <stdlib.h>
#include <string.h>

static void new_buffer_is_empty(void) {
    rb_t rb; rb_init(&rb);
    int  x = -1;
    CHECK_EQ_INT(rb_count(&rb), 0);
    CHECK(rb_pop(&rb, &x) == false);
    CHECK_EQ_INT(x, -1);                       /* відмова нічого не пише */
}

static void fifo_order(void) {
    rb_t rb; rb_init(&rb);
    int  x = 0;
    CHECK(rb_push(&rb, 10));
    CHECK(rb_push(&rb, 20));
    CHECK(rb_push(&rb, 30));
    CHECK(rb_pop(&rb, &x));  CHECK_EQ_INT(x, 10);
    CHECK(rb_pop(&rb, &x));  CHECK_EQ_INT(x, 20);
    CHECK(rb_pop(&rb, &x));  CHECK_EQ_INT(x, 30);
    CHECK_EQ_INT(rb_count(&rb), 0);
}

static void holds_exactly_cap(void) {
    rb_t rb; rb_init(&rb);
    for (int i = 0; i < (int)RB_CAP; i++)
        CHECK(rb_push(&rb, i));
    CHECK_EQ_INT(rb_count(&rb), RB_CAP);
}

static void push_on_full_is_rejected(void) {
    rb_t rb; rb_init(&rb);
    for (int i = 0; i < (int)RB_CAP; i++) rb_push(&rb, i);
    CHECK(rb_push(&rb, 99) == false);
    CHECK_EQ_INT(rb_count(&rb), RB_CAP);
}

static void rejected_push_keeps_contents(void) {
    rb_t rb; rb_init(&rb);
    int  x = 0;
    for (int i = 0; i < (int)RB_CAP; i++) rb_push(&rb, 10 * (i + 1));
    rb_push(&rb, 99);                          /* мусить бути відкинутий */
    for (int i = 0; i < (int)RB_CAP; i++) {
        CHECK(rb_pop(&rb, &x));
        CHECK_EQ_INT(x, 10 * (i + 1));
    }
    CHECK(rb_pop(&rb, &x) == false);
}

static void pop_on_empty_writes_nothing(void) {
    rb_t rb; rb_init(&rb);
    int  x = 777;
    CHECK(rb_pop(&rb, &x) == false);
    CHECK_EQ_INT(x, 777);
}

static void pop_frees_a_slot(void) {
    rb_t rb; rb_init(&rb);
    int  x = 0;
    for (int i = 0; i < (int)RB_CAP; i++) rb_push(&rb, i);
    CHECK(rb_pop(&rb, &x));  CHECK_EQ_INT(x, 0);
    CHECK(rb_push(&rb, 42));                   /* місце звільнилося */
    CHECK_EQ_INT(rb_count(&rb), RB_CAP);
}

static const tt_case CASES[] = {
    { "новий буфер порожній",             new_buffer_is_empty },
    { "віддає в порядку надходження",     fifo_order },
    { "вміщає рівно RB_CAP елементів",    holds_exactly_cap },
    { "push у повний буфер відмовляє",    push_on_full_is_rejected },
    { "відмова не псує вмісту",           rejected_push_keeps_contents },
    { "pop із порожнього нічого не пише", pop_on_empty_writes_nothing },
    { "після pop звільняється місце",     pop_frees_a_slot },
};

int main(int argc, char **argv) {
    uint32_t seed = 0;                         /* 0 — не перемішувати */
    if (argc == 3 && strcmp(argv[1], "--shuffle") == 0)
        seed = (uint32_t)strtoul(argv[2], NULL, 10);
    return tt_run(CASES, sizeof CASES / sizeof CASES[0], seed);
}
