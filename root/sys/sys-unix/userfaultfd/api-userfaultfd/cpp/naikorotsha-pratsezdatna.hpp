int uffd = ::syscall(SYS_userfaultfd, O_CLOEXEC | O_NONBLOCK);

::uffdio_api api{.api = UFFD_API, .features = 0};
::ioctl(uffd, UFFDIO_API, &api);

void* area = ::mmap(nullptr, len, PROT_READ | PROT_WRITE,
                    MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);

::uffdio_register reg{
    .range = {.start = reinterpret_cast<std::uintptr_t>(area), .len = len},
    .mode  = UFFDIO_REGISTER_MODE_MISSING,
};
::ioctl(uffd, UFFDIO_REGISTER, &reg);
// перевірити: reg.ioctls & ((__u64)1 << _UFFDIO_COPY)

// у потоці-наглядачі:
::pollfd pf{.fd = uffd, .events = POLLIN};
::poll(&pf, 1, -1);

::uffd_msg m{};
::read(uffd, &m, sizeof(m));

auto page = m.arg.pagefault.address & ~(pagesize - 1);
fetch(page, buf);                                  // буфер ПОЗА area

::uffdio_copy c{.dst = page, .src = reinterpret_cast<std::uintptr_t>(buf),
                .len = pagesize, .mode = 0};
::ioctl(uffd, UFFDIO_COPY, &c);
