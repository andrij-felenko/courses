static void probe_locks(void)
{
    char         name[64], path[PATH_MAX];
    struct flock fl;
    int          fd, rc;

    snprintf(name, sizeof name, "lock-%ld", (long) getpid());
    snprintf(path, sizeof path, "%s/%s", share, name);

    if (rpc("OPEN 0 rw %s", name) < 0) { puts("4. створити не вдалося"); return; }
    if (rpc("FLOCK 0") < 0)            { puts("4. чужий flock не взявся"); return; }

    fd = open(path, O_RDWR);
    if (fd < 0) { perror("4. open"); return; }

    rc = flock(fd, LOCK_EX | LOCK_NB);
    printf("4a. flock проти чужого flock: %s\n",
           rc == 0 ? "НЕ виключає — замок не долає межі машини"
                   : "виключає, як і має бути");
    if (rc == 0) flock(fd, LOCK_UN);

    memset(&fl, 0, sizeof fl);
    fl.l_type = F_WRLCK;
    fl.l_whence = SEEK_SET;
    rc = fcntl(fd, F_SETLK, &fl);
    printf("4b. fcntl проти чужого flock: %s\n",
           rc == 0 ? "не виключає — як локально"
                   : "ВИКЛЮЧАЄ — flock зведено до POSIX-замка на весь файл");
    if (rc == 0) { fl.l_type = F_UNLCK; fcntl(fd, F_SETLK, &fl); }

    rpc("CLOSE 0");                                /* закриття зняло чужий flock */
    if (rpc("OPEN 0 rw %s", name) >= 0) {
        if (rpc("FCNTL 0") < 0) puts("4c. чужий fcntl-замок не взявся взагалі");
        else {
            memset(&fl, 0, sizeof fl);
            fl.l_type = F_WRLCK;
            fl.l_whence = SEEK_SET;
            rc = fcntl(fd, F_SETLK, &fl);
            printf("4c. fcntl проти чужого fcntl: %s\n",
                   rc == 0 ? "НЕ виключає — замки лишилися локальними"
                           : "виключає, як і має бути");
            if (rc == 0) { fl.l_type = F_UNLCK; fcntl(fd, F_SETLK, &fl); }
        }
        rpc("CLOSE 0");
    }

    close(fd);
    rpc("UNLINK %s", name);
}
