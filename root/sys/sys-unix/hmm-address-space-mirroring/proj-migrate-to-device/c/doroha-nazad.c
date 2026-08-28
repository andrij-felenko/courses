static vm_fault_t pereselnyk_migrate_to_ram(struct vm_fault *vmf)
{
	struct pereselnyk *p = vmf->page->pgmap->owner;
	unsigned long addr = vmf->address & PAGE_MASK;
	unsigned long src_pfn = 0, dst_pfn = 0;
	struct page *spage, *dpage;
	struct migrate_vma args = {
		.vma		= vmf->vma,
		.start		= addr,
		.end		= addr + PAGE_SIZE,
		.src		= &src_pfn,
		.dst		= &dst_pfn,
		.flags		= MIGRATE_VMA_SELECT_DEVICE_PRIVATE,
		.pgmap_owner	= p,
		/* Сторінка, на якій стався збій, УЖЕ замкнена й УЖЕ має зайве
		   посилання — від збою. Без цього поля перевірка «чи ніхто її
		   не тримає» побачила б це посилання й відмовилася рухати
		   сторінку, а збій повторювався б вічно.                    */
		.fault_page	= vmf->page,
	};

	if (migrate_vma_setup(&args))
		return VM_FAULT_SIGBUS;
	if (!args.cpages)
		return 0;   /* хтось випередив: сторінка вже в пам'яті, збій повторять */

	spage = migrate_pfn_to_page(src_pfn);
	dpage = alloc_page_vma(GFP_HIGHUSER, vmf->vma, addr);
	if (!dpage)
		goto fail;
	lock_page(dpage);
	if (dma_copy_to_host(p, dpage, spage)) {
		unlock_page(dpage);
		put_page(dpage);
		goto fail;
	}
	dst_pfn = migrate_pfn(page_to_pfn(dpage));

	migrate_vma_pages(&args);
	device_pt_drop(p, addr);       /* плата сюди більше не ходить */
	migrate_vma_finalize(&args);
	return 0;

fail:
	/* dst порожній: третій такт просто поверне на місце те, що було. */
	migrate_vma_finalize(&args);
	return VM_FAULT_SIGBUS;
}
