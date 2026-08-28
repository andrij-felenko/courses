// freeze_cost.c — один виклик stop_machine(), зміряний зсередини й ззовні
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/stop_machine.h>
#include <linux/timekeeping.h>
#include <linux/delay.h>
#include <linux/slab.h>
#include <linux/sort.h>
#include <linux/math64.h>
#include <linux/smp.h>

static int reps = 25;
module_param(reps, int, 0444);
MODULE_PARM_DESC(reps, "скільки разів зупиняти машину");

static unsigned int busy_ns;
module_param(busy_ns, uint, 0444);
MODULE_PARM_DESC(busy_ns, "штучна робота всередині вікна тиші, нс");

struct probe {
	u64 in, out;	/* час, знятий усередині вікна тиші */
	int cpu;	/* яке ядро процесора виконувало fn */
};

/* Виконується з вимкненими перериваннями, поки решта ядер процесора стоять.
 * Дозволено рівно те, що не вміє заснути: прочитати годинник, записати в пам'ять.
 */
static int freeze_probe(void *arg)
{
	struct probe *p = arg;

	p->cpu = smp_processor_id();
	p->in  = ktime_get_mono_fast_ns();

	if (busy_ns) {
		u64 until = p->in + busy_ns;

		while (ktime_get_mono_fast_ns() < until)
			cpu_relax();
	}

	p->out = ktime_get_mono_fast_ns();
	return 0;
}

static int cmp_u64(const void *a, const void *b)
{
	u64 x = *(const u64 *)a, y = *(const u64 *)b;

	return (x > y) - (x < y);
}

static void report(const char *what, u64 *v, int n)
{
	u64 sum = 0;
	int i;

	sort(v, n, sizeof(*v), cmp_u64, NULL);
	for (i = 0; i < n; i++)
		sum += v[i];

	pr_info("%s min %llu, med %llu, max %llu, avg %llu (нс)\n",
		what, v[0], v[n / 2], v[n - 1], div_u64(sum, n));
}

static int __init freeze_cost_init(void)
{
	u64 *head, *work, *tail, *outer;
	struct probe p = { };
	int i, err = -ENOMEM;

	reps = clamp(reps, 1, 1000);

	head  = kcalloc(reps, sizeof(u64), GFP_KERNEL);
	work  = kcalloc(reps, sizeof(u64), GFP_KERNEL);
	tail  = kcalloc(reps, sizeof(u64), GFP_KERNEL);
	outer = kcalloc(reps, sizeof(u64), GFP_KERNEL);
	if (!head || !work || !tail || !outer)
		goto out;

	for (i = 0; i < reps; i++) {
		u64 t0, t1;

		t0 = ktime_get_ns();
		stop_machine(freeze_probe, &p, NULL);	/* NULL: fn виконає одне ядро */
		t1 = ktime_get_ns();

		head[i]  = p.in  - t0;		/* зібрати всіх і вимкнути переривання */
		work[i]  = p.out - p.in;	/* власне робота                       */
		tail[i]  = t1    - p.out;	/* розійтися й повернути процесор      */
		outer[i] = t1    - t0;

		msleep(20);	/* тут спати можна: ми в контексті modprobe */
	}

	pr_info("ядер онлайн %u, повторів %d, fn виконувало ядро %d\n",
		num_online_cpus(), reps, p.cpu);
	report("зібратися:     ", head,  reps);
	report("робота fn:     ", work,  reps);
	report("розійтися:     ", tail,  reps);
	report("усього, ззовні:", outer, reps);
	err = 0;
out:
	kfree(head); kfree(work); kfree(tail); kfree(outer);
	return err;
}

static void __exit freeze_cost_exit(void) { }

module_init(freeze_cost_init);
module_exit(freeze_cost_exit);
MODULE_LICENSE("GPL");	/* stop_machine() віддано модулям як EXPORT_SYMBOL_GPL */
MODULE_DESCRIPTION("Вимір тривалості паузи stop_machine()");
