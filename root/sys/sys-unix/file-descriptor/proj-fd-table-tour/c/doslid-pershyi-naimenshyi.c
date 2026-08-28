static void demo_lowest(void)
{
    banner("Найменший вільний номер");
    dump_fds("на старті");

    int a = open("/dev/null", O_RDONLY);
    if (a < 0) die("open /dev/null");
    int b = open("/dev/null", O_RDONLY);
    if (b < 0) die("open /dev/null");
    int c = open("/dev/null", O_RDONLY);
    if (c < 0) die("open /dev/null");
    printf("три open      -> %d, %d, %d\n", a, b, c);

    if (close(b) < 0) die("close");
    printf("close(%d)      -> у таблиці дірка\n", b);

    int again = open("/dev/null", O_RDONLY);
    if (again < 0) die("open /dev/null");
    printf("ще один open  -> %d  (дірку залатано, %d не видали)\n", again, c + 1);

    if (close(a) < 0 || close(again) < 0 || close(c) < 0) die("close");
}
