/* Ядра до 5.8: те саме, але не за один раз. */
static int loop_attach_legacy(int fd_dev, const struct attach_req *r)
{
    if (ioctl(fd_dev, LOOP_SET_FD, r->fd_img) < 0)
        return -1;              /* пристрій уже живий — і вже неправильний */

    struct loop_info64 info;
    memset(&info, 0, sizeof info);
    info.lo_offset    = r->offset;
    info.lo_sizelimit = r->sizelimit;
    snprintf((char *) info.lo_file_name, LO_NAME_SIZE, "%s", r->img_path);

    int err = 0;
    if (r->block_size &&
        ioctl(fd_dev, LOOP_SET_BLOCK_SIZE, (unsigned long) r->block_size) < 0)
        err = errno;
    else if (ioctl(fd_dev, LOOP_SET_STATUS64, &info) < 0)
        err = errno;
    else if (r->direct_io && ioctl(fd_dev, LOOP_SET_DIRECT_IO, 1UL) < 0)
        err = errno;

    if (err) {                  /* прибираємо за собою недоналаштований пристрій */
        ioctl(fd_dev, LOOP_CLR_FD);
        errno = err;
        return -1;
    }
    return 0;
}
