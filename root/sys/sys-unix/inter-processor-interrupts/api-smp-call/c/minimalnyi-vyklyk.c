#include <linux/smp.h>

static void say_where(void *info)
{
        pr_info("виконано на ядрі %d, аргумент %lu\n",
                smp_processor_id(), (unsigned long)info);
}

static void poke_cpu3(void)
{
        /* синхронно: повернеться, коли say_where() уже відпрацювала на ядрі 3 */
        int err = smp_call_function_single(3, say_where, (void *)42UL, 1);

        if (err)
                pr_warn("ядро 3 недосяжне: %d\n", err);
}
