static void pereselnyk_evict_all(struct pereselnyk *p)
{
	unsigned long npages = PHYS_PFN(resource_size(p->res));
	unsigned long start  = PHYS_PFN(p->res->start);
	unsigned long *src, *dst, i;

	src = kvcalloc(npages, sizeof(*src), GFP_KERNEL | __GFP_NOFAIL);
	dst = kvcalloc(npages, sizeof(*dst), GFP_KERNEL | __GFP_NOFAIL);

	/* Ті самі такти, але без vma: сторінки перебираємо за номерами. */
	migrate_device_range(src, start, npages);

	for (i = 0; i < npages; i++) {
		struct page *spage = migrate_pfn_to_page(src[i]);
		struct page *dpage;

		if (!spage || !(src[i] & MIGRATE_PFN_MIGRATE))
			continue;

		/* Відступати нікуди: дані з плати мусять доїхати. */
		dpage = alloc_page(GFP_HIGHUSER | __GFP_NOFAIL);
		lock_page(dpage);
		dma_copy_to_host(p, dpage, spage);
		dst[i] = migrate_pfn(page_to_pfn(dpage));
	}

	migrate_device_pages(src, dst, npages);
	migrate_device_finalize(src, dst, npages);
	kvfree(src);
	kvfree(dst);
}

static void pereselnyk_shutdown(struct pereselnyk *p)
{
	pereselnyk_evict_all(p);
	memunmap_pages(&p->pagemap);      /* аж тепер він не повисне */
	release_mem_region(p->res->start, resource_size(p->res));
}
