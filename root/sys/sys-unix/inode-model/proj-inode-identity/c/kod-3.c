static void walk(int dfd, struct pathbuf *p, struct ctx *c)
{
    DIR *d = fdopendir(dfd);            /* DIR забирає дескриптор собі */
    if (d == NULL) {
        warn_at(c, p->s, "fdopendir");
        close(dfd);
        return;
    }

    /* 1. Знімок імен. Каталог живий, поки ми по ньому ходимо; знімок
     *    звужує вікно, у якому чужі зміни плутають нам перелік. */
    struct namelist names;
    memset(&names, 0, sizeof names);

    for (;;) {
        errno = 0;                      /* інакше NULL не відрізнити від кінця */
        struct dirent *e = readdir(d);
        if (e == NULL) {
            if (errno != 0) warn_at(c, p->s, "readdir");
            break;
        }
        if (e->d_name[0] == '.' && (e->d_name[1] == '\0' ||
            (e->d_name[1] == '.' && e->d_name[2] == '\0')))
            continue;                   /* "." і ".." — ми вже тут */
        if (!names_push(&names, e->d_name)) {
            warn_at(c, p->s, "malloc");
            break;
        }
    }

    /* Упорядкування дає передбачуваний вивід і дозволяє викинути сусідні
     * однакові імена: у каталозі на хеш-дереві поняття «зсуву» умовне, тож
     * getdents на каталозі, який змінюють просто зараз, може віддати той
     * самий запис двічі. */
    qsort(names.v, names.n, sizeof *names.v, cmp_name);

    int fd = dirfd(d);                  /* потрібен для fstatat/openat */

    for (size_t i = 0; i < names.n; i++) {
        if (i > 0 && strcmp(names.v[i], names.v[i - 1]) == 0)
            continue;

        const char *name = names.v[i];
        size_t saved = p->len;
        if (!path_push(p, name)) { warn_at(c, p->s, "realloc"); break; }

        struct stat st;
        /* 2. Саме lstat-семантика: символьне посилання описуємо як
         *    посилання. Інакше ціль порахувалася б удруге, а посилання на
         *    каталог відправило б обхід у нескінченну петлю. */
        if (fstatat_retry(fd, name, &st, AT_SYMLINK_NOFOLLOW) != 0) {
            if (errno == ENOENT) c->vanished++;   /* зникло між знімком і stat */
            else                 warn_at(c, p->s, "fstatat");
            goto next;
        }

        account(c, &st, p->s);

        if (S_ISDIR(st.st_mode)) {
            if (c->one_fs && st.st_dev != c->root_dev) {
                c->crossings++;
                goto next;
            }

            int sub = openat_retry(fd, name,
                                   O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
            if (sub < 0) { warn_at(c, p->s, "openat"); goto next; }

            /* 3. Те саме питання тотожності, тільки в ролі охорони: чи це
             *    той самий об'єкт, який ми щойно розглядали? Між fstatat і
             *    openat ім'я могли перевісити на інший каталог. */
            struct stat sst;
            if (fstat(sub, &sst) != 0 ||
                sst.st_dev != st.st_dev || sst.st_ino != st.st_ino) {
                fprintf(stderr, "inodesum: %s: підмінено між stat і open\n", p->s);
                c->errors++;
                close(sub);
                goto next;
            }

            walk(sub, p, c);            /* walk забирає дескриптор собі */
        }
    next:
        p->len = saved;                 /* вихід із підкаталогу */
        p->s[saved] = '\0';
    }

    names_free(&names);
    closedir(d);                        /* закриває й сам дескриптор */
}
