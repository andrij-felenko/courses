// knobdemo.c — власний вузол у /proc/sys/kernel/knobdemo
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/sysctl.h>
#include <linux/slab.h>
#include <linux/mutex.h>
#include <linux/rcupdate.h>
#include <linux/workqueue.h>
#include <linux/random.h>
#include <linux/overflow.h>

/* Крутилка 1: період відліку. Звичайна змінна — свого коду не треба. */
static int interval_ms = 200;
static int interval_min = 10;
static int interval_max = 60000;

/* Крутилка 2: скільки комірок. Самого числа замало — треба масив. */
static int slots = 16;
static int slots_min = 1;
static int slots_max = 4096;

/* Скільки разів гістограму перебудовували — видно в журналі ядра. */
static int rebuilds;

/* Довжина живе всередині знімка, а не поруч із ним. */
struct bins {
	struct rcu_head rcu;
	int n;
	atomic_t hit[];
};

static struct bins __rcu *cur_bins;
static DEFINE_MUTEX(bins_lock);		/* серіалізує перебудову */
static struct delayed_work tick_work;

static struct bins *bins_alloc(int n)
{
	struct bins *b = kvzalloc(struct_size(b, hit, n), GFP_KERNEL);

	if (b)
		b->n = n;
	return b;
}
