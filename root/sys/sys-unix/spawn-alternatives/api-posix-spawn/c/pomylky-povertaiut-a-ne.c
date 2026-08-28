int rc = posix_spawnp(&pid, prog, &fa, &at, argv, environ);
if (rc != 0) {
    /* дитини або немає, або її вже прибрано — waitpid тут НЕ кличуть */
    fprintf(stderr, "%s: %s\n", prog, strerror(rc));
    return -1;
}
int st;
waitpid(pid, &st, 0);
if (WIFEXITED(st) && WEXITSTATUS(st) == 127)
    fprintf(stderr, "%s: схоже, запустити не вдалося\n", prog);
