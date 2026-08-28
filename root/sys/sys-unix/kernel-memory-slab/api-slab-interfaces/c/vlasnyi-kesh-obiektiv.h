/* єдина форма до 6.12 — працює й далі */
struct kmem_cache *kmem_cache_create(const char *name, unsigned int size,
                                     unsigned int align, slab_flags_t flags,
                                     void (*ctor)(void *));

/* від 6.12 kmem_cache_create() — макрос із _Generic, тож приймає ще й таке */
struct kmem_cache *kmem_cache_create(const char *name, unsigned int object_size,
                                     struct kmem_cache_args *args,
                                     slab_flags_t flags);

void         kmem_cache_destroy(struct kmem_cache *s);
int          kmem_cache_shrink(struct kmem_cache *s);
unsigned int kmem_cache_size(struct kmem_cache *s);

#define KMEM_CACHE(__struct, __flags)   /* ім'я, розмір і вирівнювання — з типу */
