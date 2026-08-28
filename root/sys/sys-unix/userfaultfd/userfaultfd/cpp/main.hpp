// Створення дескриптора та реєстрація ділянки
int uffd = ::syscall(SYS_userfaultfd, O_CLOEXEC | O_NONBLOCK | UFFD_USER_MODE_ONLY);
::uffdio_api api{.api = UFFD_API, .features = 0};
::ioctl(uffd, UFFDIO_API, &api);

::uffdio_register reg{
    .range = {.start = reinterpret_cast<std::uintptr_t>(area), .len = length},
    .mode  = UFFDIO_REGISTER_MODE_MISSING,
};
::ioctl(uffd, UFFDIO_REGISTER, &reg);

// Наглядач: читання збою та неподільне заповнення
::uffd_msg msg{};
::read(uffd, &msg, sizeof(msg));
auto page = msg.arg.pagefault.address & ~(pagesize - 1);
fetch_page(page, buf);

::uffdio_copy copy{
    .dst = page, .src = reinterpret_cast<std::uintptr_t>(buf.data()), .len = pagesize, .mode = 0,
};
::ioctl(uffd, UFFDIO_COPY, &copy);
