static struct klp_func funcs[] = {
        {
                .old_name = "cmdline_proc_show",
                .new_func = livepatch_cmdline_proc_show,
        }, { }
};

static struct klp_object objs[] = {
        {
                /* .name = NULL означає саме ядро, а не якийсь модуль */
                .funcs = funcs,
        }, { }
};

static struct klp_patch patch = {
        .mod    = THIS_MODULE,
        .objs   = objs,
        .replace = true,
};

static int __init livepatch_init(void)
{
        return klp_enable_patch(&patch);
}
