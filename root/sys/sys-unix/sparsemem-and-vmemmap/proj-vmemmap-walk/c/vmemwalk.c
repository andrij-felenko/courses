// vmemwalk.c — де живуть описувачі кадрів на цій машині
#define pr_fmt(fmt) "vmemwalk: " fmt

#include <linux/module.h>
#include <linux/mm.h>
#include <linux/mmzone.h>
#include <linux/memory_hotplug.h>
#include <linux/sched.h>

#if !defined(CONFIG_SPARSEMEM)
#error "модуль про SPARSEMEM; на FLATMEM секцій немає й показувати нема чого"
#endif

static unsigned long target_pfn = 0x100000;      /* кадр за адресою 4 ГіБ */
static unsigned long top_pfn = 4UL << 20;        /* межа обходу: 4М кадрів = 16 ГіБ */

module_param(top_pfn, ulong, 0444);
MODULE_PARM_DESC(top_pfn, "верхня межа обходу в кадрах (max_pfn модулям не видно)");

/* повний розбір одного номера кадру */
static void report_pfn(unsigned long pfn)
{
	struct page *page;

	if (!pfn_valid(pfn)) {                   /* СПЕРШУ спитати, потім рахувати */
		pr_info("pfn %#lx: описувача немає (секція %lu порожня)\n",
			pfn, pfn_to_section_nr(pfn));
		return;
	}

	page = pfn_to_page(pfn);
	pr_info("pfn %#lx = секція %lu + зсув %lu\n",
		pfn, pfn_to_section_nr(pfn), pfn & ~PAGE_SECTION_MASK);
	pr_info("  описувач  %px\n", page);      /* %px — без хешування, свідомо */
	pr_info("  назад     page_to_pfn() = %#lx\n", page_to_pfn(page));
	pr_info("  flags     %#lx  вузол %d, зона %u, посилань %d\n",
		page->flags, page_to_nid(page),
		(unsigned)page_zonenum(page), page_ref_count(page));
	pr_info("  онлайн    %s\n", pfn_to_online_page(pfn) ? "так" : "ні");
}

/* запис у /sys/module/vmemwalk/parameters/pfn дає новий звіт */
static int pfn_set(const char *val, const struct kernel_param *kp)
{
	int err = param_set_ulong(val, kp);      /* приймає й 0x…, і десяткове */

	if (err)
		return err;
	report_pfn(target_pfn);
	return 0;
}
static const struct kernel_param_ops pfn_ops = {
	.set = pfn_set,
	.get = param_get_ulong,
};
module_param_cb(pfn, &pfn_ops, &target_pfn, 0644);

/* база масиву за першим дійсним кадром: page − pfn */
static struct page *derive_base(unsigned long *first)
{
	unsigned long pfn;

	for (pfn = 0; pfn < top_pfn; pfn++)
		if (pfn_valid(pfn)) {
			*first = pfn;
			return pfn_to_page(pfn) - pfn;
		}
	return NULL;
}

static void draw_map(void)
{
	unsigned long sec, last = pfn_to_section_nr(top_pfn - 1);
	unsigned long row_first = 0;
	char row[65];
	int col = 0;

	for (sec = 0; sec <= last; sec++) {
		unsigned long base = section_nr_to_pfn(sec), pfn, n = 0;

		for (pfn = base; pfn < base + PAGES_PER_SECTION; pfn++)
			if (pfn_valid(pfn))
				n++;

		if (col == 0)
			row_first = sec;
		row[col] = (n == PAGES_PER_SECTION) ? '#' : n ? '+' : '.';

		if (++col == 64) {
			row[64] = '\0';
			pr_info("  %5lu..%5lu  %s\n", row_first, sec, row);
			col = 0;
		}
		cond_resched();                  /* мільйони перевірок — не тримати процесор */
	}
	if (col) {
		row[col] = '\0';
		pr_info("  %5lu..%5lu  %s\n", row_first, last, row);
	}
}

static int __init vw_init(void)
{
	unsigned long first = 0, pfn, live = 0, bad = 0;
	struct page *base = derive_base(&first);

	pr_info("sizeof(struct page)     %zu Б\n", sizeof(struct page));
	pr_info("SECTION_SIZE_BITS       %d → секція %lu МіБ\n",
		SECTION_SIZE_BITS, 1UL << (SECTION_SIZE_BITS - 20));
	pr_info("PFN_SECTION_SHIFT       %d → кадрів у секції %lu\n",
		PFN_SECTION_SHIFT, PAGES_PER_SECTION);
	pr_info("масив однієї секції     %lu КіБ\n",
		(PAGES_PER_SECTION * sizeof(struct page)) >> 10);
	pr_info("NR_MEM_SECTIONS         %lu (MAX_PHYSMEM_BITS = %d)\n",
		NR_MEM_SECTIONS, MAX_PHYSMEM_BITS);
	pr_info("модель                  %s\n",
		IS_ENABLED(CONFIG_SPARSEMEM_VMEMMAP) ? "SPARSEMEM_VMEMMAP"
						    : "SPARSEMEM без vmemmap");
	if (!base) {
		pr_warn("до кадру %#lx жодного дійсного — підніміть top_pfn\n", top_pfn);
		return -ENODEV;
	}
	pr_info("база масиву             %px (перший дійсний кадр %#lx)\n", base, first);

	/* чи справді описувач = база + номер, для КОЖНОГО дійсного кадру */
	for (pfn = 0; pfn < top_pfn; pfn++) {
		if (!pfn_valid(pfn))
			continue;
		live++;
		if (pfn_to_page(pfn) != base + pfn && ++bad <= 3)
			pr_warn("  розбіг на %#lx: %px замість %px\n",
				pfn, pfn_to_page(pfn), base + pfn);
	}
	pr_info("описано кадрів          %lu (%lu МіБ), розбігів %lu\n",
		live, (live << PAGE_SHIFT) >> 20, bad);

	draw_map();
	report_pfn(target_pfn);
	return 0;
}

static void __exit vw_exit(void) { }

module_init(vw_init);
module_exit(vw_exit);

MODULE_DESCRIPTION("Walk the SPARSEMEM section map and the page descriptor array");
MODULE_LICENSE("GPL");
