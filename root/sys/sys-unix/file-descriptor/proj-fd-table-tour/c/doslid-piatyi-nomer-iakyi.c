static void demo_reuse(void)
{
    banner("Номер після close уже не ваш");

    int a = open("fdtour-a.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (a < 0) die("open fdtour-a.txt");
    printf("fdtour-a.txt дістав номер %d\n", a);
    if (close(a) < 0) die("close");
    /* змінна a досі тримає число — саме це нас і погубить */

    int b = open("fdtour-b.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (b < 0) die("open fdtour-b.txt");
    printf("fdtour-b.txt дістав номер %d%s\n",
           b, (a == b) ? "  — те саме число" : "");

    static const char msg[] = "рядок, призначений файлові A\n";
    ssize_t k = write(a, msg, sizeof msg - 1);
    printf("write(%d, ...) повернув %zd — жодної помилки\n", a, k);

    if (close(b) < 0) die("close");
    printf("а лежить він у fdtour-b.txt:\n");
    show_file("fdtour-b.txt");

    /* Як не наступити: число знищують тієї ж миті, що й об'єкт. */
    int c = open("/dev/null", O_RDONLY);
    if (c < 0) die("open /dev/null");
    if (close(c) < 0) die("close");
    c = -1;
    errno = 0;
    if (write(c, msg, 1) < 0)
        printf("write(-1, ...): %s — помилка на місці, а не за три модулі звідси\n",
               strerror(errno));
}
