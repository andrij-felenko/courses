/* оголошення області — лише на етапі завантаження, звідси __init */
int cma_declare_contiguous_nid(phys_addr_t base, phys_addr_t size,
                               phys_addr_t limit, phys_addr_t alignment,
                               unsigned int order_per_bit, bool fixed,
                               const char *name, struct cma **res_cma, int nid);
int cma_init_reserved_mem(phys_addr_t base, phys_addr_t size,
                          unsigned int order_per_bit, const char *name,
                          struct cma **res_cma);

/* робота з готовою областю */
struct page *cma_alloc(struct cma *cma, unsigned long count,
                       unsigned int align, bool no_warn);
bool         cma_release(struct cma *cma, const struct page *pages,
                         unsigned long count);
