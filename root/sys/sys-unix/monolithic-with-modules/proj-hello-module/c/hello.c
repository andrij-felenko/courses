/* hello.c — найменший модуль, який ще має сенс */
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/init.h>
#include <linux/module.h>
#include <linux/moduleparam.h>

static char *whom = "світе";
module_param(whom, charp, 0644);
MODULE_PARM_DESC(whom, "кого вітати");

static int __init hello_init(void)
{
	pr_info("привіт, %s! мене щойно прилінкували в ядро\n", whom);
	return 0;
}

static void __exit hello_exit(void)
{
	pr_info("бувай, %s\n", whom);
}

module_init(hello_init);
module_exit(hello_exit);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Найкоротший робочий модуль");
MODULE_VERSION("0.1");
