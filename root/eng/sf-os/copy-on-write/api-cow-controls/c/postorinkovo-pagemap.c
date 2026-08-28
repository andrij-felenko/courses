#include <fcntl.h>
#include <stdint.h>
#include <unistd.h>

#define PM_SOFT_DIRTY  (1ULL << 55)
#define PM_EXCLUSIVE   (1ULL << 56)
#define PM_PRESENT     (1ULL << 63)

/* Стан однієї сторінки: чи вона належить процесові одноосібно
   й чи в неї писали від останнього скидання soft-dirty. */
int page_state(int pagemap_fd, const void *addr, long page_size,
               int *exclusive, int *soft_dirty)
{
        uint64_t entry;
        off_t off = (off_t)((uintptr_t)addr / page_size) * (off_t)sizeof(entry);

        if (pread(pagemap_fd, &entry, sizeof(entry), off) != (ssize_t)sizeof(entry))
                return -1;

        if (!(entry & PM_PRESENT)) {
                *exclusive = *soft_dirty = 0;   /* кадру ще немає взагалі */
                return 0;
        }
        *exclusive  = (entry & PM_EXCLUSIVE)  ? 1 : 0;
        *soft_dirty = (entry & PM_SOFT_DIRTY) ? 1 : 0;
        return 0;
}

/* Відкривати так: open("/proc/self/pagemap", O_RDONLY),
   page_size брати з sysconf(_SC_PAGESIZE). */
