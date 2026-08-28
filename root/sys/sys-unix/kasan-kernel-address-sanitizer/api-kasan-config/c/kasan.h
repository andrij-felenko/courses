#include <linux/kasan.h>

/*
 * kasan_poison_shadow - позначає регіон пам'яті як недоступний (poisoned).
 * @addr: початкова віртуальна адреса (мусить бути вирівняна)
 * @size: розмір регіону в байтах
 * @value: код отруєння (наприклад, KASAN_SLAB_FREE або власний тег)
 */
void kasan_poison_shadow(const void *addr, size_t size, u8 value);

/*
 * kasan_unpoison_shadow - позначає регіон пам'яті як доступний (valid).
 * @addr: початкова віртуальна адреса
 * @size: розмір регіону в байтах
 */
void kasan_unpoison_shadow(const void *addr, size_t size);
