struct mem_section {
        unsigned long section_mem_map;
        struct mem_section_usage *usage;
#ifdef CONFIG_PAGE_EXTENSION
        struct page_ext *page_ext;
        unsigned long pad;
#endif
};

struct mem_section_usage {
        struct rcu_head rcu;
#ifdef CONFIG_SPARSEMEM_VMEMMAP
        DECLARE_BITMAP(subsection_map, SUBSECTIONS_PER_SECTION);
#endif
        unsigned long pageblock_flags[0];
};
