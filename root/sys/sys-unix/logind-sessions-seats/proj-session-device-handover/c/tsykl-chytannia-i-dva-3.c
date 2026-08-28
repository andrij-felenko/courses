static int on_resume(sd_bus_message *m, void *userdata, sd_bus_error *e) {
    Ctx *c = userdata;
    uint32_t maj, min;
    int fd;

    int r = sd_bus_message_read(m, "uuh", &maj, &min, &fd);
    if (r < 0 || maj != c->major || min != c->minor)
        return r < 0 ? r : 0;

    int keep = fcntl(fd, F_DUPFD_CLOEXEC, 3);     /* власна копія, не з повідомлення */
    if (keep < 0)
        return -errno;
    fcntl(keep, F_SETFL, O_NONBLOCK);

    if (c->fd >= 0)
        close(c->fd);                             /* для evdev він уже ні на що не годен */
    c->fd = keep;
    printf("ResumeDevice: новий дескриптор\n");
    return arm(c);
}
