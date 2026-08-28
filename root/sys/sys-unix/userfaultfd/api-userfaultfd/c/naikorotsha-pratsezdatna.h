int uffd = syscall(SYS_userfaultfd, O_CLOEXEC | O_NONBLOCK);

struct uffdio_api api = { .api = UFFD_API, .features = 0 };
ioctl(uffd, UFFDIO_API, &api);

void *area = mmap(NULL, len, PROT_READ | PROT_WRITE,
                  MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);

struct uffdio_register reg = {
    .range = { .start = (unsigned long)area, .len = len },
    .mode  = UFFDIO_REGISTER_MODE_MISSING,
};
ioctl(uffd, UFFDIO_REGISTER, &reg);
/* перевірити: reg.ioctls & ((__u64)1 << _UFFDIO_COPY) */

/* у потоці-наглядачі: */
struct pollfd pf = { .fd = uffd, .events = POLLIN };
poll(&pf, 1, -1);

struct uffd_msg m;
read(uffd, &m, sizeof m);

unsigned long page = m.arg.pagefault.address & ~(pagesize - 1);
fetch(page, buf);                                  /* буфер ПОЗА area */

struct uffdio_copy c = { .dst = page, .src = (unsigned long)buf,
                         .len = pagesize, .mode = 0 };
ioctl(uffd, UFFDIO_COPY, &c);
