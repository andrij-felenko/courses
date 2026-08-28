int main(void)
{
    char line[512], shown[512];
    static char *slot[MAXP][16];
    struct job cur;
    memset(&cur, 0, sizeof cur);

    shell_init();
    for (;;) {
        printf("mysh$ ");
        fflush(stdout);
        if (!fgets(line, sizeof line, stdin)) break;
        line[strcspn(line, "\n")] = '\0';
        if (!*line)              continue;
        if (!strcmp(line, "exit")) break;
        if (!strcmp(line, "fg")) { if (job_stopped(&cur)) do_fg(&cur); continue; }
        if (!strcmp(line, "bg")) { if (job_stopped(&cur)) do_bg(&cur); continue; }

        snprintf(shown, sizeof shown, "%s", line);
        int background = 0;
        size_t len = strlen(line);
        if (len && line[len - 1] == '&') { background = 1; line[len - 1] = '\0'; }

        char *part[MAXP];
        int n = 0;
        for (char *s = strtok(line, "|"); s && n < MAXP; s = strtok(NULL, "|"))
            part[n++] = s;

        char **argvv[MAXP];
        for (int i = 0; i < n; i++) {
            int k = 0;
            for (char *w = strtok(part[i], " \t"); w && k < 15; w = strtok(NULL, " \t"))
                slot[i][k++] = w;
            slot[i][k] = NULL;
            argvv[i] = slot[i];
        }
        if (n == 0 || argvv[0][0] == NULL) continue;

        memset(&cur, 0, sizeof cur);
        snprintf(cur.cmd, sizeof cur.cmd, "%s", shown);
        launch_job(&cur, argvv, n, !background);
    }
    return 0;
}
