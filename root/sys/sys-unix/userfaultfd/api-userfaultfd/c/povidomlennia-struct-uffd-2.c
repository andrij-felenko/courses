struct uffd_msg m;
ssize_t n = read(uffd, &m, sizeof m);   /* після poll(POLLIN) на uffd */

if (m.event == UFFD_EVENT_PAGEFAULT) {
    if (m.arg.pagefault.flags & UFFD_PAGEFAULT_FLAG_WP)
        clear_write_protect(m.arg.pagefault.address);      /* UFFDIO_WRITEPROTECT */
    else if (m.arg.pagefault.flags & UFFD_PAGEFAULT_FLAG_MINOR)
        map_existing(m.arg.pagefault.address);             /* UFFDIO_CONTINUE     */
    else
        fill_missing(m.arg.pagefault.address);             /* UFFDIO_COPY         */
}
