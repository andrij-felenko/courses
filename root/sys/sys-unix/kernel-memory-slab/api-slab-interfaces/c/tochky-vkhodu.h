/* безтипові запити за розміром */
void  *kmalloc(size_t size, gfp_t flags);
void  *kzalloc(size_t size, gfp_t flags);                    /* + __GFP_ZERO */
void  *kmalloc_array(size_t n, size_t size, gfp_t flags);    /* ловить переповнення n·size */
void  *kcalloc(size_t n, size_t size, gfp_t flags);          /* те саме + нуль */
void  *krealloc(const void *p, size_t new_size, gfp_t flags);
void   kfree(const void *object);
void   kfree_sensitive(const void *object);                  /* затерти нулями, тоді звільнити */
size_t kmalloc_size_roundup(size_t size);                    /* скільки насправді дадуть */

/* запити з іменованого кеша */
void  *kmem_cache_alloc(struct kmem_cache *s, gfp_t flags);
void  *kmem_cache_zalloc(struct kmem_cache *s, gfp_t flags);
void   kmem_cache_free(struct kmem_cache *s, void *x);

/* «дай як вийде»: спершу суцільно, при невдачі — розрізнено */
void  *kvmalloc(size_t size, gfp_t flags);
void  *kvmalloc_node(size_t size, gfp_t flags, int node);
void   kvfree(const void *addr);
