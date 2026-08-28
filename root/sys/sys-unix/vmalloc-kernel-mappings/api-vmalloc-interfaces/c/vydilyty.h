/* базові */
void *vmalloc(unsigned long size);
void *vzalloc(unsigned long size);                      /* + занулення */
void *vmalloc_node(unsigned long size, int node);
void *vzalloc_node(unsigned long size, int node);

/* масиви — з перевіркою переповнення добутку n · size */
void *vmalloc_array(size_t n, size_t size);
void *vcalloc(size_t n, size_t size);                   /* те саме + занулення */

/* особливі призначення */
void *vmalloc_user(unsigned long size);                 /* під віддачу в простір користувача */
void *vmalloc_32(unsigned long size);                   /* кадри, адресовані 32 бітами */
void *vmalloc_32_user(unsigned long size);

/* зі своїми прапорцями й параметрами */
void *__vmalloc(unsigned long size, gfp_t gfp_mask);
void *vmalloc_huge_node(unsigned long size, gfp_t gfp_mask, int node);  /* від 6.16 */
void *__vmalloc_node_range(unsigned long size, unsigned long align,
                           unsigned long start, unsigned long end,
                           gfp_t gfp_mask, pgprot_t prot,
                           unsigned long vm_flags, int node, const void *caller);

/* змінити розмір, зберігши вміст (від 6.12) */
void *vrealloc(const void *p, size_t size, gfp_t flags);

void vfree(const void *addr);
