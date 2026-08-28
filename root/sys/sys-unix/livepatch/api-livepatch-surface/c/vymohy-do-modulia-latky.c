#include <linux/module.h>
#include <linux/seq_file.h>
#include <linux/livepatch.h>

static int lp_cmdline_proc_show(struct seq_file *m, void *v)
{
        seq_printf(m, "%s\n", "залатано");
        return 0;
}

static void lp_post_patch(struct klp_object *obj) { /* ремонт стану */ }

static struct klp_func funcs[] = {
        { .old_name = "cmdline_proc_show", .new_func = lp_cmdline_proc_show },
        { }
};

static struct klp_object objs[] = {
        { .funcs = funcs, .callbacks = { .post_patch = lp_post_patch } },
        { }
};

static struct klp_patch patch = {
        .mod = THIS_MODULE, .objs = objs, .replace = true,
};

static int __init lp_init(void) { return klp_enable_patch(&patch); }
static void __exit lp_exit(void) { }

module_init(lp_init);
module_exit(lp_exit);
MODULE_LICENSE("GPL");
MODULE_INFO(livepatch, "Y");
