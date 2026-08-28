#define _GNU_SOURCE
#include <sys/mman.h>

/* створити ділянку й прибрати її */
void *mmap(void *addr, size_t length, int prot, int flags, int fd, off_t offset);
int   munmap(void *addr, size_t length);

/* змінити права вже наявної */
int   mprotect(void *addr, size_t length, int prot);
int   pkey_mprotect(void *addr, size_t length, int prot, int pkey);   /* Linux 4.9 */

/* пересунути або змінити розмір */
void *mremap(void *old_address, size_t old_size, size_t new_size, int flags,
             ... /* void *new_address — лише зі MREMAP_FIXED */);

/* винести зміни на пристрій і підказати ядру, як ділянкою користуватимуться */
int   msync(void *addr, size_t length, int flags);
int   madvise(void *addr, size_t length, int advice);

/* заборонити витіснення */
int   mlock(const void *addr, size_t length);
int   mlock2(const void *addr, size_t length, unsigned int flags);    /* Linux 4.4 */
int   munlock(const void *addr, size_t length);
int   mlockall(int flags);
int   munlockall(void);
