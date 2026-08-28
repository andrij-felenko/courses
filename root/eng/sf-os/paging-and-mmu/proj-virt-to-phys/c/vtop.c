/* vtop.c — надрукувати фізичні адреси кількох змінних */
#include "pagemap.h"
#include <sys/mman.h>

static int global_var = 0xC0FFEE;

int main(void)
{
    long     ps  = pm_page_size();
    int      fd  = pm_open();
    int      local = 1;
    uint64_t w;

    printf("розмір сторінки: %ld байтів\n\n", ps);

    if (pm_read(fd, &global_var, &w) == 0)
        pm_print("глобальна (.data)", &global_var, w);
    if (pm_read(fd, &local, &w) == 0)
        pm_print("локальна (стек)", &local, w);
    if (pm_read(fd, (void *)(uintptr_t)&main, &w) == 0)
        pm_print("код (.text)", (void *)(uintptr_t)&main, w);

    /* свіжа приватна анонімна ділянка: жодної сторінки в ній ще не чіпали */
    char *area = mmap(NULL, 16 * ps, PROT_READ | PROT_WRITE,
                      MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (area == MAP_FAILED) { perror("mmap"); exit(1); }

    char *page = area + 8 * ps;
    if (pm_read(fd, page, &w) == 0)
        pm_print("свіжий mmap до дотику", page, w);

    *page = 1;                       /* саме тут стається збій сторінки */

    if (pm_read(fd, page, &w) == 0)
        pm_print("свіжий mmap після дотику", page, w);

    close(fd);
    return 0;
}
