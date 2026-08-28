/*
 * kasan_reset_tag - скидає тег вказівника (встановлює старший байт у 0xFF)
 * Повертає чисту канонічну віртуальну адресу ядра.
 */
void *kasan_reset_tag(const void *addr);

/*
 * kasan_random_tag - генерує новий випадковий тег для об'єкта
 */
u8 kasan_random_tag(void);

/*
 * kasan_init_object_tags - призначає тег об'єкту та записує його в тіньову пам'ять/MTE
 */
void kasan_init_object_tags(struct kmem_cache *cache, void *object);
