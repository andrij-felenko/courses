/* CONFIG_FLATMEM */
#define __pfn_to_page(pfn)   (mem_map + ((pfn) - ARCH_PFN_OFFSET))
#define __page_to_pfn(page)  ((unsigned long)((page) - mem_map) + ARCH_PFN_OFFSET)

/* CONFIG_SPARSEMEM_VMEMMAP */
#define __pfn_to_page(pfn)   (vmemmap + (pfn))
#define __page_to_pfn(page)  (unsigned long)((page) - vmemmap)

/* CONFIG_SPARSEMEM — обидва напрямки складніші за один вираз, тому це
   інструкції-вирази GCC; тут наведено те, що вони роблять по суті */
#define __pfn_to_page(pfn)   ({ struct mem_section *__s = __pfn_to_section(pfn); \
                                __section_mem_map_addr(__s) + (pfn); })
#define __page_to_pfn(pg)    ({ int __sec = memdesc_section((pg)->flags);        \
                                (unsigned long)((pg) - __section_mem_map_addr(   \
                                        __nr_to_section(__sec))); })
