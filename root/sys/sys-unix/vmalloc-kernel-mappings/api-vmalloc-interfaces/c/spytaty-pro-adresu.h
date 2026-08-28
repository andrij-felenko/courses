static inline bool is_vmalloc_addr(const void *x);     /* просте порівняння меж */
int   is_vmalloc_or_module_addr(const void *x);
struct page   *vmalloc_to_page(const void *addr);      /* обхід таблиць */
unsigned long  vmalloc_to_pfn(const void *addr);

struct vm_struct *get_vm_area(unsigned long size, unsigned long flags);
struct vm_struct *find_vm_area(const void *addr);
struct vm_struct *remove_vm_area(const void *addr);

/* лише для ділянок із VM_SPARSE, від 6.9 */
int  vm_area_map_pages(struct vm_struct *area, unsigned long start,
                       unsigned long end, struct page **pages);
void vm_area_unmap_pages(struct vm_struct *area, unsigned long start,
                         unsigned long end);
