// Критичний інваріант — лишається й у релізі, не залежить від NDEBUG.
#define ASSERT_ALWAYS(expr) \
    do { if (!(expr)) controlled_reset("invariant: " #expr); } while (0)

void protocol_tick(proto_t *fsm) {
    ASSERT_ALWAYS(fsm->state < ST_COUNT);     // дешево й критично → завжди
    assert(fsm->pending <= fsm->capacity);    // звичайна передумова → лише debug
#ifdef DEBUG
    assert(proto_deep_check(fsm));            // дорого → лише під прапором
#endif
    /* ... гарячий шлях обробки ... */
}
