static int val_min = 0;
static int val_max = 100;

static struct ctl_table example_table[] = {
    {
        .procname     = "percent_limit",
        .data         = &my_percentage,
        .maxlen       = sizeof(int),
        .mode         = 0644,
        .proc_handler = proc_dointvec_minmax,
        .extra1       = &val_min,
        .extra2       = &val_max,
    },
};
