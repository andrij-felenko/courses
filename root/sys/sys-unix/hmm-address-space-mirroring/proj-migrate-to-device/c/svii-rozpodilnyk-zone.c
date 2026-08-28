static struct page *devpage_alloc(struct pereselnyk *p)
{
	struct page *pg;

	spin_lock(&p->lock);
	pg = p->free_list;
	if (pg) {
		p->free_list = pg->zone_device_data;
		p->nfree--;
	}
	spin_unlock(&p->lock);
	if (!pg)
		return NULL;

	/* Оце — і є «взяти кадр»: лічильник з нуля стає одиницею, сторінка
	   ЗАМИКАЄТЬСЯ, а pagemap дістає посилання, яке потім не дасть
	   згортанню пройти повз живий кадр.                              */
	zone_device_page_init(pg);
	return pg;
}

/* Ядро кличе це, коли лічильник кадру впав до нуля. Спати не можна:
   останнє посилання цілком може віддати хтось із контексту, де сон
   заборонений, — звідси spinlock, а не мутекс.                      */
static void pereselnyk_page_free(struct page *pg)
{
	struct pereselnyk *p = pg->pgmap->owner;

	spin_lock(&p->lock);
	pg->zone_device_data = p->free_list;
	p->free_list = pg;
	p->nfree++;
	spin_unlock(&p->lock);
}
