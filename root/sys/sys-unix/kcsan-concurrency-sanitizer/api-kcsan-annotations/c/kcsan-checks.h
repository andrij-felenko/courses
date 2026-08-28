#include <linux/kcsan-checks.h>

/* Явна перевірка діапазону пам'яті на читання або запис */
void kcsan_check_read(const volatile void *ptr, size_t size);
void kcsan_check_write(const volatile void *ptr, size_t size);

/* Тимчасово вимикає перевірки KCSAN для поточного потоку/контексту */
void kcsan_disable_current(void);

/* Відновлює перевірки KCSAN для поточного потоку/контексту */
void kcsan_enable_current(void);

/* Початок та кінець атомарної зони для вкладених операцій */
void kcsan_nestable_atomic_begin(void);
void kcsan_nestable_atomic_end(void);
