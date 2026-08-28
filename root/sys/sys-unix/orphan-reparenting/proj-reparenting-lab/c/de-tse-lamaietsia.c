int main(int argc, char **argv)
{
    setvbuf(stdout, NULL, _IOLBF, 0);   /* рядок — і одразу у вивід */

    if (argc >= 2 && strcmp(argv[1], "reparent") == 0)
        return lab_reparent();
    if (argc >= 2 && strcmp(argv[1], "subreaper") == 0)
        return lab_subreaper();
    if (argc >= 2 && strcmp(argv[1], "pdeathsig") == 0)
        return lab_pdeathsig(PD_NORMAL);
    if (argc >= 2 && strcmp(argv[1], "pdeathsig-race") == 0)
        return lab_pdeathsig(PD_RACE);
    if (argc >= 2 && strcmp(argv[1], "pdeathsig-guard") == 0)
        return lab_pdeathsig(PD_GUARD);

    fprintf(stderr, "вжиток: %s reparent|subreaper|pdeathsig"
                    "|pdeathsig-race|pdeathsig-guard\n", argv[0]);
    return 2;
}
