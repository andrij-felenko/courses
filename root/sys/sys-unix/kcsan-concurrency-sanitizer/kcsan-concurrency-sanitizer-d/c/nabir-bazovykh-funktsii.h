/* Функції перехоплення звичайного читання */
void __tsan_read1(void *ptr);
void __tsan_read2(void *ptr);
void __tsan_read4(void *ptr);
void __tsan_read8(void *ptr);
void __tsan_read16(void *ptr);

/* Функції перехоплення звичайного запису */
void __tsan_write1(void *ptr);
void __tsan_write2(void *ptr);
void __tsan_write4(void *ptr);
void __tsan_write8(void *ptr);
void __tsan_write16(void *ptr);

/* Обробники невирівняного або довільного за довжиною доступу */
void __tsan_read_range(void *ptr, size_t size);
void __tsan_write_range(void *ptr, size_t size);
