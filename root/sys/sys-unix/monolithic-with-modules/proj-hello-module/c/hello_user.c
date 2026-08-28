/* hello_user.c */
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/init.h>
#include <linux/module.h>

extern int hello_ping(void);   /* у справжньому коді — спільний заголовок */

static int __init user_init(void)
{
	pr_info("hello_ping() повернув %d\n", hello_ping());
	return 0;
}

static void __exit user_exit(void) { }

module_init(user_init);
module_exit(user_exit);
MODULE_LICENSE("GPL");
