struct migrate_vma args = {
        .vma    = vma,
        .start  = addr,
        .end    = addr + len,
        .src    = src_pfns,     /* що знайшлося й чи можна його рухати */
        .dst    = dst_pfns,     /* куди драйвер його кладе */
        .flags  = MIGRATE_VMA_SELECT_SYSTEM,
};

migrate_vma_setup(&args);       /* такт перший */
device_alloc_and_copy(&args);   /* робота драйвера: свої кадри й копіювання */
migrate_vma_pages(&args);       /* такт другий */
device_install_entries(&args);
migrate_vma_finalize(&args);    /* такт третій */
