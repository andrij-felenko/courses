static void demo_two_levels(void)
{
    banner("F_GETFD і F_GETFL: два рівні на одному номері");

    int fd = open("/dev/null", O_WRONLY | O_APPEND | O_NONBLOCK);
    if (fd < 0) die("open /dev/null");
    int twin = dup(fd);                 /* інший номер, ТОЙ САМИЙ опис */
    if (twin < 0) die("dup");
    printf("одразу після dup:\n");
    show_fd(fd);
    show_fd(twin);

    /* F_SETFD править комірку таблиці — сусідній номер не чіпає */
    if (fcntl(fd, F_SETFD, FD_CLOEXEC) < 0) die("F_SETFD");
    printf("ставимо FD_CLOEXEC на номер %d:\n", fd);
    show_fd(fd);
    show_fd(twin);

    /* F_SETFL править опис — а він у них спільний */
    int fl = fcntl(fd, F_GETFL);
    if (fl < 0) die("F_GETFL");
    if (fcntl(fd, F_SETFL, fl & ~O_NONBLOCK) < 0) die("F_SETFL");
    printf("знімаємо O_NONBLOCK з номера %d:\n", fd);
    show_fd(fd);
    show_fd(twin);

    /* dup прапорця дескриптора не копіює: новий номер завжди успадковуваний */
    int third = dup(fd);
    if (third < 0) die("dup");
    printf("копія номера %d, на якому стоїть FD_CLOEXEC:\n", fd);
    show_fd(third);

    if (close(fd) < 0 || close(twin) < 0 || close(third) < 0) die("close");
}
