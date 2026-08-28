static void copy_to_device(struct migrate_vma *args, struct pereselnyk *p)
{
	unsigned long i;

	for (i = 0; i < args->npages; i++) {
		struct page *spage = migrate_pfn_to_page(args->src[i]);
		struct page *dpage;
		int ret;

		/* Ядро вже вирішило, що цю сторінку рухати не можна. Єдина
		   правильна відповідь — лишити dst нулем і не чіпати нічого. */
		if (!(args->src[i] & MIGRATE_PFN_MIGRATE))
			continue;

		dpage = devpage_alloc(p);
		if (!dpage)
			continue;          /* кадри скінчилися — теж просто пропуск */

		/* spage == NULL при виставленій позначці — не помилка, а дірка:
		   сторінки ще не існує, бо процес її не торкався. Переселяємо
		   порожнечу, і перший дотик станеться вже на платі.           */
		if (spage)
			ret = dma_copy_to_device(p, dpage, spage);
		else
			ret = dma_zero_device_page(p, dpage);

		if (ret) {
			/* Кадр наш і лише наш: у dst його не буде, отже ядро про
			   нього не дізнається. Розмикаємо самі — це нас замкнув
			   zone_device_page_init().                              */
			unlock_page(dpage);
			put_page(dpage);
			continue;
		}

		args->dst[i] = migrate_pfn(page_to_pfn(dpage));
		if ((args->src[i] & MIGRATE_PFN_WRITE) ||
		    (!spage && (args->vma->vm_flags & VM_WRITE)))
			args->dst[i] |= MIGRATE_PFN_WRITE;
	}
}
