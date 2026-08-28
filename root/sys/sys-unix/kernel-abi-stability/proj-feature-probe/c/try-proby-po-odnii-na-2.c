#ifndef MFD_HUGETLB
#  define MFD_HUGETLB 0x0004U       /* з'явився в ядрі 4.14 */
#endif

static int probe_memfd_hugetlb(void)
{
    /* memfd_create перевіряє прапорці ДО того, як читати ім'я, тож нульовий
       вказівник гарантує: файлового об'єкта не виникне за жодних обставин. */
    int fd = memfd_create(NULL, MFD_CLOEXEC | MFD_HUGETLB);
    if (fd >= 0) { close(fd); return 1; }   /* не станеться, але хай буде */
    if (errno == ENOSYS)
        return 0;                  /* виклику немає взагалі — прапорця й поготів */
    return errno != EINVAL;        /* EINVAL = біта не знають; решта = знають */
}
