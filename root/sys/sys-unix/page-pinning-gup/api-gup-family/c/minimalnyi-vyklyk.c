int pin_buffer(unsigned long start, int nr_pages, struct page ***out)
{
	struct page **pages;
	int pinned, ret;

	pages = kvmalloc_array(nr_pages, sizeof(*pages), GFP_KERNEL);
	if (!pages)
		return -ENOMEM;

	ret = account_locked_vm(current->mm, nr_pages, true);
	if (ret)
		goto free_pages;

	/* FOLL_LONGTERM: пристрій триматиме буфер, доки живе реєстрація */
	pinned = pin_user_pages_fast(start, nr_pages,
				     FOLL_WRITE | FOLL_LONGTERM, pages);
	if (pinned <= 0) {
		ret = pinned ? pinned : -EFAULT;
		goto unaccount;
	}

	/* часткова вдача — норма: далі працюємо з pinned, а не з nr_pages */
	*out = pages;
	return pinned;

unaccount:
	account_locked_vm(current->mm, nr_pages, false);
free_pages:
	kvfree(pages);
	return ret;
}
