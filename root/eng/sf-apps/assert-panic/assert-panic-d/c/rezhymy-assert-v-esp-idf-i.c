// Інваріант, що лишається й у релізі (не залежить від NDEBUG)
#define ASSERT_ALWAYS(expr) \
    do { if (!(expr)) esp_system_abort("invariant: " #expr); } while (0)

void tick(critical_state_t *s) {
    ASSERT_ALWAYS(s->magic == STATE_MAGIC);   // дешево, тримаємо завжди
#ifdef DEBUG
    assert(crc32_ok(s));                       // дорого — лише в debug
#endif
    /* ... гарячий шлях ... */
}
