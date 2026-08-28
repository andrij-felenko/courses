int main(int argc, char **argv)
{
    const char *root = (argc > 1) ? argv[1] : ".";

    /* Корінь обходу назвав користувач — за ним іти можна. Усередині
       дерева іменам уже не довіряємо: там O_NOFOLLOW. */
    int rfd = open(root, O_RDONLY | O_DIRECTORY | O_CLOEXEC);
    if (rfd < 0) { perror(root); return 8; }

    struct stat rst;
    if (fstat(rfd, &rst) != 0) { perror("fstat"); return 8; }

    struct ctx c = { .dev = rst.st_dev };

    /* Чи має корінь обходу запис у батьківському каталозі, якого ми
       НЕ прочитаємо? Ні, коли він сам є коренем файлової системи:
       тоді «..» указує на нього ж, а якщо систему змонтовано в чуже
       дерево, шлях «..» виводить уже на інший том. */
    struct stat up;
    int fsroot = (fstatat(rfd, "..", &up, 0) != 0)
                 || (up.st_dev != rst.st_dev)
                 || (up.st_ino == rst.st_ino);

    struct rec *r = find(rst.st_ino);
    r->seen  = fsroot ? 0 : 1;
    r->nlink = rst.st_nlink;
    r->mode  = rst.st_mode;
    r->known = 1;

    walk(rfd, root, 0, &c);

    unsigned long judged = 0, bad = 0;
    for (size_t i = 0; i < cap; i++) {
        struct rec *v = &tab[i];

        if (v->ino == 0 || !v->known)
            continue;               /* про цей inode ми знаємо замало */
        if (S_ISDIR(v->mode) && v->nlink == 1)
            continue;               /* «кількість невідома» — див. нижче */

        judged++;
        if ((uint64_t)v->nlink == v->seen)
            continue;

        printf("inode %10ju  %c  st_nlink=%-4ju  записів=%-4ju  різниця %+jd\n",
               (uintmax_t)v->ino,
               S_ISDIR(v->mode) ? 'd' : '-',
               (uintmax_t)v->nlink, (uintmax_t)v->seen,
               (intmax_t)v->seen - (intmax_t)v->nlink);
        bad++;
    }

    fprintf(stderr, "\nкаталогів %lu, записів %lu, різних inode %zu, "
                    "меж монтування %lu, задалеко %lu, помилок %lu\n",
            c.dirs, c.entries, used, c.crossed, c.deep, c.errors);
    fprintf(stderr, "звірено inode %lu, розбіжностей %lu\n", judged, bad);

    free(tab);
    return bad ? 4 : (c.errors ? 8 : 0);
}
