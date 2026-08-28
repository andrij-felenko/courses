/* ipi_lat.c — ціна smp_call_function_single у тактах TSC */
#include <linux/module.h>
#include <linux/kthread.h>
#include <linux/slab.h>
#include <linux/smp.h>
#include <linux/sort.h>
#include <linux/topology.h>
#include <asm/msr.h>
#include <asm/hardirq.h>

static int src = -1, dst = -1, runs = 4000, burst = 32;
module_param(src, int, 0444);
module_param(dst, int, 0444);
module_param(runs, int, 0444);
module_param(burst, int, 0444);

struct probe { u64 t0, t1; };

/* виконується НА ЦІЛІ, у контексті переривання: одна дія й нічого більше */
static void stamp(void *arg)
{
	((struct probe *)arg)->t1 = rdtsc_ordered();
}

static void noop(void *unused) { }

static unsigned int cal(int cpu)        /* той самий лічильник, що й рядок CAL */
{
	return per_cpu(irq_stat, cpu).irq_call_count;
}

static int cmp_u64(const void *a, const void *b)
{
	u64 x = *(const u64 *)a, y = *(const u64 *)b;
	return (x > y) - (x < y);
}

static void report(const char *what, u64 *v, int n)
{
	sort(v, n, sizeof(*v), cmp_u64, NULL);
	pr_info("ipi_lat: %-14s min=%llu med=%llu p99=%llu тактів (медіана %llu нс)\n",
		what, v[0], v[n / 2], v[n / 100 * 99],
		div64_u64(v[n / 2] * 1000000ull, tsc_khz));
}

static int measure(void *unused)
{
	bool same_die = topology_physical_package_id(src) ==
			topology_physical_package_id(dst);
	u64 *rt, *one, *snd, a;
	unsigned int c0, c1;
	struct probe p;
	int i;

	rt  = kmalloc_array(runs, sizeof(u64), GFP_KERNEL);
	one = kmalloc_array(runs, sizeof(u64), GFP_KERNEL);
	snd = kmalloc_array(runs, sizeof(u64), GFP_KERNEL);
	if (!rt || !one || !snd)
		goto out;

	for (i = 0; i < 200; i++)               /* прогрів: холодні кеші брешуть */
		smp_call_function_single(dst, noop, NULL, 1);

	c0 = cal(dst);
	for (i = 0; i < runs; i++) {
		p.t0 = rdtsc_ordered();
		smp_call_function_single(dst, stamp, &p, 1);
		rt[i]  = rdtsc_ordered() - p.t0;
		one[i] = p.t1 - p.t0;

		a = rdtsc_ordered();                    /* те саме, але без очікування */
		smp_call_function_single(dst, noop, NULL, 0);
		snd[i] = rdtsc_ordered() - a;
		smp_call_function_single(dst, noop, NULL, 1);  /* осісти, поза виміром */
	}
	c1 = cal(dst);

	pr_info("ipi_lat: %d→%d, один кристал: %s, tsc_khz=%u\n",
		src, dst, same_die ? "так" : "ні", tsc_khz);
	report("надсилання", snd, runs);
	report("повний оберт", rt, runs);
	if (same_die)
		report("одностороння", one, runs);
	pr_info("ipi_lat: %d запитів → CAL на ядрі %d виріс на %u\n",
		runs * 3, dst, c1 - c0);

	if (burst > 0) {
		call_single_data_t *csd = kcalloc(burst, sizeof(*csd), GFP_KERNEL);

		if (csd) {
			for (i = 0; i < burst; i++)
				csd[i].func = noop;
			c0 = cal(dst);
			for (i = 0; i < burst; i++)
				smp_call_function_single_async(dst, &csd[i]);
			smp_call_function_single(dst, noop, NULL, 1);
			c1 = cal(dst);
			pr_info("ipi_lat: %d незалежних запитів поспіль → CAL +%u\n",
				burst, c1 - c0);
			kfree(csd);
		}
	}
out:
	kfree(rt); kfree(one); kfree(snd);
	while (!kthread_should_stop())
		schedule_timeout_interruptible(HZ / 5);
	return 0;
}

static struct task_struct *th;

static int __init ipi_lat_init(void)
{
	if (src < 0 || dst < 0 || src == dst || runs < 100 ||
	    !cpu_online(src) || !cpu_online(dst))
		return -EINVAL;

	th = kthread_create(measure, NULL, "ipi_lat");
	if (IS_ERR(th))
		return PTR_ERR(th);
	kthread_bind(th, src);            /* ініціатор більше нікуди не поїде */
	wake_up_process(th);
	return 0;
}

static void __exit ipi_lat_exit(void) { kthread_stop(th); }

module_init(ipi_lat_init);
module_exit(ipi_lat_exit);
MODULE_LICENSE("GPL");
