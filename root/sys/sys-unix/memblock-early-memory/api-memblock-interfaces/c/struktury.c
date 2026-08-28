struct memblock_region {
        phys_addr_t base;             /* початок діапазону */
        phys_addr_t size;             /* довжина в байтах */
        enum memblock_flags flags;    /* властивості діапазону */
#ifdef CONFIG_NUMA
        int nid;                      /* вузол NUMA */
#endif
};

struct memblock_type {
        unsigned long cnt;            /* скільки записів зайнято */
        unsigned long max;            /* скільки вміщає масив зараз */
        phys_addr_t total_size;       /* сума size усіх записів */
        struct memblock_region *regions;
        char *name;                   /* "memory" | "reserved" | "physmem" */
};

struct memblock {
        bool bottom_up;               /* напрям пошуку вільного вікна */
        phys_addr_t current_limit;    /* стеля адрес для виділень */
        struct memblock_type memory;  /* що взагалі існує */
        struct memblock_type reserved;/* що вже комусь належить */
};
