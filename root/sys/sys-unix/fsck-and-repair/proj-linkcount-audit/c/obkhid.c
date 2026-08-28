#define MAX_DEPTH 256

struct ctx {
    dev_t         dev;      /* пристрій кореня: за його межі не виходимо */
    unsigned long dirs, entries, crossed, deep, errors;
};

/* dfd переходить у власність walk(): його закриє closedir(). */
static void walk(int dfd, const char *path, unsigned depth, struct ctx *c)
{
    DIR *d = fdopendir(dfd);
    if (!d) {
        fprintf(stderr, "%s: fdopendir: %s\n", path, strerror(errno));
        close(dfd);
        c->errors++;
        return;
    }
    c->dirs++;

    for (;;) {
        errno = 0;
        struct dirent *e = readdir(d);
        if (!e) {
            /* readdir повертає NULL і на кінці, і на помилці; розрізняє
               їх лише errno, тому його обнуляють перед викликом. */
            if (errno) {
                fprintf(stderr, "%s: readdir: %s\n", path, strerror(errno));
                c->errors++;
            }
            break;
        }

        /* Запис каталогу — це і є одна згадка номера. Рахуємо ВСІ,
           разом із «.» та «..»: саме вони дають каталогам ті дві
           одиниці, яких у файлів немає. */
        c->entries++;
        struct rec *r = find((ino_t)e->d_ino);
        if (!r) { c->errors++; continue; }   /* нульовий номер — запис нечитний */
        r->seen++;

        if (!strcmp(e->d_name, ".") || !strcmp(e->d_name, ".."))
            continue;                        /* полічили — і досить */

        struct stat st;
        if (fstatat(dirfd(d), e->d_name, &st, AT_SYMLINK_NOFOLLOW) != 0) {
            fprintf(stderr, "%s/%s: fstatat: %s\n", path, e->d_name,
                    strerror(errno));
            c->errors++;
            continue;
        }

        /* Межа монтування. Назва і inode, який вона називає, опинилися
           на різних томах: у каталозі записано номер накритої теки,
           а stat повертає корінь змонтованої системи. Дві нумерації
           зшити нічим — далі не йдемо й нічого не судимо. */
        if (st.st_dev != c->dev || (ino_t)e->d_ino != st.st_ino) {
            c->crossed++;
            continue;
        }

        r->nlink = st.st_nlink;
        r->mode  = st.st_mode;
        r->known = 1;

        if (!S_ISDIR(st.st_mode))
            continue;
        if (depth + 1 >= MAX_DEPTH) { c->deep++; continue; }

        /* O_NOFOLLOW тут не зайвий: між fstatat і openat назву могли
           підмінити символьним посиланням. */
        int fd = openat(dirfd(d), e->d_name,
                        O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
        if (fd < 0) {
            fprintf(stderr, "%s/%s: openat: %s\n", path, e->d_name,
                    strerror(errno));
            c->errors++;
            continue;
        }

        char *sub;
        if (asprintf(&sub, "%s/%s", path, e->d_name) < 0) sub = NULL;
        walk(fd, sub ? sub : e->d_name, depth + 1, c);
        free(sub);
    }

    closedir(d);
}
