static void usage(void)
{
    fputs("вжиток:\n"
          "  slabwatch report [скільки рядків]\n"
          "  slabwatch grow <тека> <скільки пошуків>\n"
          "  slabwatch squeeze <МіБ>\n"
          "  slabwatch drop\n"
          "  slabwatch scatter <тека> <негативних> <закріпити>\n", stderr);
}

int main(int argc, char **argv)
{
    PAGE = (unsigned long)sysconf(_SC_PAGESIZE);
    if (argc < 2) { usage(); return 2; }
    if (!strcmp(argv[1], "report"))
        return cmd_report(argc > 2 ? atoi(argv[2]) : 12);
    if (!strcmp(argv[1], "grow") && argc > 3)
        return cmd_grow(argv[2], strtoul(argv[3], NULL, 10));
    if (!strcmp(argv[1], "squeeze") && argc > 2)
        return cmd_squeeze(strtoul(argv[2], NULL, 10));
    if (!strcmp(argv[1], "drop")) {
        snapshot("до", "dentry");
        if (drop_slab() != 0) return 1;
        snapshot("після", "dentry");
        return 0;
    }
    if (!strcmp(argv[1], "scatter") && argc > 4)
        return cmd_scatter(argv[2], strtoul(argv[3], NULL, 10),
                           strtoul(argv[4], NULL, 10));
    usage();
    return 2;
}
