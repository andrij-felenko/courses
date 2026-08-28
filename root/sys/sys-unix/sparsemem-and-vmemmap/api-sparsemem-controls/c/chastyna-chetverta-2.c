static inline int pfn_valid(unsigned long pfn)
{
        struct mem_section *ms;
        int ret;

        if (PHYS_PFN(PFN_PHYS(pfn)) != pfn)          /* номер не влазить у фізичну адресу */
                return 0;
        if (pfn_to_section_nr(pfn) >= NR_MEM_SECTIONS)
                return 0;
        ms = __pfn_to_section(pfn);
        rcu_read_lock_sched();
        if (!valid_section(ms)) {
                rcu_read_unlock_sched();
                return 0;
        }
        /* рання секція заповнена цілком; у пізньої питаємо конкретну підсекцію */
        ret = early_section(ms) || pfn_section_valid(ms, pfn);
        rcu_read_unlock_sched();
        return ret;
}
