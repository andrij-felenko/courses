static int migrate_range_to_device(struct pereselnyk *p, struct mm_struct *mm,
				   unsigned long start, unsigned long len)
{
	unsigned long npages = len >> PAGE_SHIFT, i;
	unsigned long *src, *dst;
	struct migrate_vma args;
	struct vm_area_struct *vma;
	int ret;

	src = kvcalloc(npages, sizeof(*src), GFP_KERNEL);
	dst = kvcalloc(npages, sizeof(*dst), GFP_KERNEL);
	if (!src || !dst) {
		ret = -ENOMEM;
		goto out;
	}

	mmap_read_lock(mm);
	vma = vma_lookup(mm, start);
	if (!vma || start + len > vma->vm_end) {
		ret = -EINVAL;
		goto out_unlock;
	}

	args = (struct migrate_vma){
		.vma		= vma,
		.start		= start,
		.end		= start + len,
		.src		= src,
		.dst		= dst,
		.flags		= MIGRATE_VMA_SELECT_SYSTEM,
		.pgmap_owner	= p,   /* щоб скасування від ЦЬОГО переселення
					  наш власний сповіщувач упізнав і
					  не викидав свої ж таблиці            */
	};

	ret = migrate_vma_setup(&args);
	if (ret)
		goto out_unlock;

	copy_to_device(&args, p);      /* довга частина: рушій прямого доступу */
	migrate_vma_pages(&args);

	/* Другий такт міг не вдатися ПОСТОРІНКОВО: комусь із сусідів
	   пощастило торкнутися адреси раніше, і позначку погашено вже тут.
	   Такий кадр у таблицю процесу не потрапив — вписати його в
	   апаратуру означало б дати платі писати в нічию пам'ять.
	   Прибирати його самим НЕ треба: третій такт розімкне й віддасть
	   посилання за нас, а зайвий put_page() віддав би в пул кадр,
	   який ще комусь належить.                                        */
	for (i = 0; i < npages; i++) {
		struct page *dpage = migrate_pfn_to_page(dst[i]);

		if (dpage && (src[i] & MIGRATE_PFN_MIGRATE))
			device_pt_install(p, start + (i << PAGE_SHIFT), dpage);
	}

	migrate_vma_finalize(&args);
	ret = 0;
out_unlock:
	mmap_read_unlock(mm);
out:
	kvfree(src);
	kvfree(dst);
	return ret;
}
