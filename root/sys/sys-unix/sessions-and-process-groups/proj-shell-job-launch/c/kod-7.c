static void do_fg(struct job *j)
{
    for (int i = 0; i < j->n; i++)
        if (j->st[i] == 's') j->st[i] = 'r';

    give_terminal(j->pgid, &j->tmodes);    /* спершу режим термінала, який був до Ctrl+Z */
    kill(-j->pgid, SIGCONT);               /* і аж тоді будимо — ВСЮ групу, не лідера */
    take_terminal(j, wait_job(j));
}

static void do_bg(struct job *j)
{
    for (int i = 0; i < j->n; i++)
        if (j->st[i] == 's') j->st[i] = 'r';

    kill(-j->pgid, SIGCONT);               /* термінала не даємо — хай працює у фоні */
    printf("[1]+ %s &\n", j->cmd);
}
