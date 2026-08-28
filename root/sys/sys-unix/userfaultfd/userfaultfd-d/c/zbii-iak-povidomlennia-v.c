int uffd = syscall(SYS_userfaultfd, O_CLOEXEC | O_NONBLOCK);

struct uffdio_api api = { .api = UFFD_API, .features = 0 };
ioctl(uffd, UFFDIO_API, &api);        /* api.features ← що вміє це ядро */

struct uffdio_register reg = {
    .range = { .start = (unsigned long)area, .len = length },
    .mode  = UFFDIO_REGISTER_MODE_MISSING,
};
ioctl(uffd, UFFDIO_REGISTER, &reg);   /* reg.ioctls ← що дозволено цій ділянці */
