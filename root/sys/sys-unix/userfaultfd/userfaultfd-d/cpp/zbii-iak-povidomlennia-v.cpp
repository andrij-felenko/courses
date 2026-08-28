int uffd = ::syscall(SYS_userfaultfd, O_CLOEXEC | O_NONBLOCK);

::uffdio_api api{.api = UFFD_API, .features = 0};
::ioctl(uffd, UFFDIO_API, &api);        // api.features ← що вміє це ядро

::uffdio_register reg{
    .range = {.start = reinterpret_cast<std::uintptr_t>(area), .len = length},
    .mode  = UFFDIO_REGISTER_MODE_MISSING,
};
::ioctl(uffd, UFFDIO_REGISTER, &reg);   // reg.ioctls ← що дозволено цій ділянці
