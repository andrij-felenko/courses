/* Створення дескриптора та реєстрація ділянки */
int uffd = syscall(SYS_userfaultfd, O_CLOEXEC | O_NONBLOCK | UFFD_USER_MODE_ONLY);
struct uffdio_api api = { .api = UFFD_API, .features = 0 };
ioctl(uffd, UFFDIO_API, &api);

struct uffdio_register reg = {
    .range = { .start = (unsigned long)area, .len = length },
    .mode  = UFFDIO_REGISTER_MODE_MISSING,
};
ioctl(uffd, UFFDIO_REGISTER, &reg);

/* Наглядач: читання збою та неподільне заповнення */
struct uffd_msg msg;
read(uffd, &msg, sizeof(msg));
unsigned long page = msg.arg.pagefault.address & ~(pagesize - 1);
fetch_page(page, buf);

struct uffdio_copy copy = {
    .dst = page, .src = (unsigned long)buf, .len = pagesize, .mode = 0,
};
ioctl(uffd, UFFDIO_COPY, &copy);
