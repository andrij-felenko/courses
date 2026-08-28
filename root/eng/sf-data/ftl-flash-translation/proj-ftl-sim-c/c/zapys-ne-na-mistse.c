void ftl_write(uint32_t lpn, const void *data) {
    (void)data;                          // модель: самі байти не тримаємо
    while (freetop <= GC_LOW) gc_run();  // спершу подбали про запас

    uint32_t old = map[lpn];             // ⚠ читати ТІЛЬКИ після GC
    uint32_t new_ppn = alloc_page();
    pstate[new_ppn] = P_VALID;
    powner[new_ppn] = lpn;               // підписали сторінку в OOB
    map[lpn] = new_ppn;
    host_w++; flash_w++;                 // хост попросив — флеш зробив

    if (old != NONE) {                   // стара версія стала сміттям
        pstate[old] = P_INVALID;
        invalid_cnt[old / PPB]++;
    }
}

uint32_t ftl_read(uint32_t lpn) { return map[lpn]; }   // PPN або NONE
