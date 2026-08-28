#include <sys/mman.h>
#include <unistd.h>
#include <stdio.h>

/* Отримання точного розміру системної сторінки пам'яті */
size_t page_size = (size_t)sysconf(_SC_PAGESIZE);

/* Отображення сторінки статусу у режим PROT_READ */
char *status_map = (char *)mmap(NULL, page_size, PROT_READ, MAP_SHARED, fd, 0);

if (status_map == MAP_FAILED) {
    perror("Помилка виконання mmap на user_events_data");
    /* Обробка помилки */
}

/* Інлайн-функція для перевірки стану в гарячому циклі */
static inline int is_user_event_enabled(const char *map, uint32_t index) {
    return map[index] != 0;
}
