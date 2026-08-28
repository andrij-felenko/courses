// SPDX-License-Identifier: GPL-2.0
#include <linux/hmm.h>
#include <linux/ioport.h>
#include <linux/memremap.h>
#include <linux/migrate.h>
#include <linux/mm.h>
#include <linux/module.h>

struct pereselnyk {
	struct dev_pagemap  pagemap;
	struct resource    *res;
	spinlock_t          lock;
	struct page        *free_list;   /* однозв'язний список вільних кадрів */
	unsigned long       nfree;
};

static void pereselnyk_page_free(struct page *pg);
static vm_fault_t pereselnyk_migrate_to_ram(struct vm_fault *vmf);

static const struct dev_pagemap_ops pereselnyk_pagemap_ops = {
	.page_free	= pereselnyk_page_free,
	.migrate_to_ram	= pereselnyk_migrate_to_ram,
};

static int pereselnyk_reserve(struct pereselnyk *p, unsigned long size)
{
	unsigned long pfn, first, last;
	void *addr;

	/* Просимо ДІРУ у фізичному просторі адрес: місце, де немає ні
	   оперативної пам'яті, ні вікон інших пристроїв. Байтів нам звідти
	   не треба — треба номери, на які ядро заведе описувачі.          */
	p->res = request_free_mem_region(&iomem_resource, size, "pereselnyk");
	if (IS_ERR(p->res))
		return PTR_ERR(p->res);

	p->pagemap.type        = MEMORY_DEVICE_PRIVATE;
	p->pagemap.range.start = p->res->start;
	p->pagemap.range.end   = p->res->end;
	p->pagemap.nr_range    = 1;
	p->pagemap.ops         = &pereselnyk_pagemap_ops;
	p->pagemap.owner       = p;   /* «ці кадри мої» — на цьому полі тримається
					 половина правильної поведінки, див. нижче */

	addr = memremap_pages(&p->pagemap, numa_node_id());
	if (IS_ERR(addr)) {
		release_mem_region(p->res->start, resource_size(p->res));
		return PTR_ERR(addr);
	}

	/* Описувачі вже є, і всі — з НУЛЬОВИМ лічильником посилань.
	   Складаємо їх у свій вільний список: розподільник цієї пам'яті — ми. */
	first = PHYS_PFN(p->res->start);
	last  = PHYS_PFN(p->res->end);
	spin_lock(&p->lock);
	for (pfn = first; pfn <= last; pfn++) {
		struct page *pg = pfn_to_page(pfn);

		pg->zone_device_data = p->free_list;
		p->free_list = pg;
		p->nfree++;
	}
	spin_unlock(&p->lock);
	return 0;
}
