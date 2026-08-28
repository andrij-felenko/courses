/* конструктор: РАЗ перетворює сиру памʼять на готовий інод */
static int
inode_ctor(void *buf, void *arg, int kmflags)
{
    struct inode *ip = buf;
    mutex_init(&ip->i_lock, NULL, MUTEX_DEFAULT, NULL);  /* дорого — але раз */
    list_create(&ip->i_pages, sizeof (page_t), 0);
    ip->i_refcnt = 0;
    return (0);
}

/* деструктор: РАЗ розбирає інод назад у сиру памʼять */
static void
inode_dtor(void *buf, void *arg)
{
    struct inode *ip = buf;
    mutex_destroy(&ip->i_lock);
    list_destroy(&ip->i_pages);
}

/* оголошуємо кеш інодів — один раз на весь час роботи системи */
kmem_cache_t *inode_cache = kmem_cache_create(
    "rt_inode_cache",         /* назва — видно у статистиці ядра */
    sizeof (struct inode),    /* усі обʼєкти цього кеша однакові завбільшки */
    0,                        /* вирівнювання */
    inode_ctor, inode_dtor,   /* побудова / розбирання — раз на буфер */
    inode_reclaim,            /* про це нижче: віддача памʼяті під тиском */
    NULL, NULL, 0);
