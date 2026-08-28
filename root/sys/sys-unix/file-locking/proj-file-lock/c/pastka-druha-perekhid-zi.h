/* upgrade-window.c — вікно робимо видимим навмисне.
   Уривок із main; fd уже відкрито, read_counter — це pread_all
   плюс strtoull, write_counter — snprintf плюс pwrite_all.
   Запустіть два примірники одночасно.                              */
    flock(fd, LOCK_SH);                       /* читаємо стан */
    a = read_counter(fd);

    sleep(1);                                 /* даємо другому дійти сюди ж */

    flock(fd, LOCK_EX);                       /* ← ядро зняло SH і аж потім дало EX */
    b = read_counter(fd);                     /* саме в тому проміжку стан і міняється */
    write_counter(fd, b + 1);                 /* пишемо вже під виключним замком */

    printf("до переходу %llu, після переходу %llu%s\n", a, b,
           a == b ? "" : "   ← стан змінився під час переходу");
