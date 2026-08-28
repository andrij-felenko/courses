static void probe_excl_race(void)
{
    enum { ROUNDS = 400 };
    char prefix[64], req[128], mine[ROUNDS + 1], theirs[ROUNDS + 8];
    int  i, mine_won = 0, their_won = 0, both = 0, none = 0;

    snprintf(prefix, sizeof prefix, "race-%ld", (long) getpid());
    snprintf(req, sizeof req, "RACE %s %d", prefix, (int) ROUNDS);
    if (send_line(req) < 0) return;               /* відповіді НЕ чекаємо */

    for (i = 0; i < ROUNDS; i++) {
        char name[PATH_MAX];
        int  fd;
        snprintf(name, sizeof name, "%s/%s-%d", share, prefix, i);
        fd = open(name, O_WRONLY | O_CREAT | O_EXCL, 0644);
        if (fd >= 0) { mine[i] = '1'; close(fd); }
        else           mine[i] = '0';
    }
    mine[ROUNDS] = '\0';

    if (recv_line(theirs, sizeof theirs) < 0) return;
    if (strlen(theirs) != (size_t) ROUNDS) { puts("6. мапа не тієї довжини"); return; }

    for (i = 0; i < ROUNDS; i++) {
        int m = (mine[i] == '1'), t = (theirs[i] == '1');
        mine_won += m;
        their_won += t;
        both += (m && t);
        none += (!m && !t);
    }

    printf("6.  O_EXCL, %d кіл: наших %d, чужих %d, ПОДВІЙНИХ %d, нічиїх %d\n",
           (int) ROUNDS, mine_won, their_won, both, none);
    if (both)
        puts("    подвійна перемога = створення НЕ атомарне між машинами");
    if (mine_won == 0 || their_won == 0)
        puts("    забіги не перетнулися в часі — проба нічого не перевірила");

    for (i = 0; i < ROUNDS; i++) {
        char name[PATH_MAX];
        snprintf(name, sizeof name, "%s/%s-%d", share, prefix, i);
        unlink(name);
    }
}

int main(int argc, char **argv)
{
    if (argc == 4 && strcmp(argv[1], "writer") == 0) {
        snprintf(share, sizeof share, "%s", argv[2]);
        ctl = tcp_accept(argv[3]);
        if (ctl < 0) { perror("accept"); return 1; }
        serve();
        return 0;
    }
    if (argc == 5 && strcmp(argv[1], "reader") == 0) {
        snprintf(share, sizeof share, "%s", argv[2]);
        ctl = tcp_connect(argv[3], argv[4]);
        if (ctl < 0) { perror("connect"); return 1; }
        probe_visibility();
        probe_open_file();
        probe_write_path();
        probe_locks();
        probe_open_unlink();
        probe_excl_race();
        send_line("BYE");
        return 0;
    }
    fprintf(stderr,
            "вжиток:\n"
            "  %s writer <спільний-каталог> <порт>\n"
            "  %s reader <спільний-каталог> <хост-письменника> <порт>\n",
            argv[0], argv[0]);
    return 1;
}
