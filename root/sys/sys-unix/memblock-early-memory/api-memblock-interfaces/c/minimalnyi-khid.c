/* 1. перекласти карту прошивки в memory */
for (i = 0; i < e820_table->nr_entries; i++) {
        struct e820_entry *e = &e820_table->entries[i];

        if (e->type == E820_TYPE_RAM)
                memblock_add(e->addr, e->size);
}

/* 2. назвати вголос усе зайняте */
memblock_reserve(__pa_symbol(_text), __pa_symbol(_end) - __pa_symbol(_text));

/* 3. підняти стелю до реально відображеної пам'яті й дозволити ріст масивів */
memblock_set_current_limit(max_pfn_mapped << PAGE_SHIFT);
memblock_allow_resize();

/* 4. виділяти */
u32 *tbl = memblock_alloc(nr * sizeof(*tbl), SMP_CACHE_BYTES);
if (!tbl)
        panic("немає ранньої пам'яті під таблицю\n");
