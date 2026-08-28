unsigned long free_reserved_area(void *start, void *end, int poison, const char *s)
{
    void *pos;
    unsigned long pages = 0;

    /* Безпечне вирівнювання адрес до меж сторінок */
    start = (void *)PAGE_ALIGN((unsigned long)start);
    end = (void *)((unsigned long)end & PAGE_MASK);

    /* Цикл проходить по кожній фізичній сторінці в діапазоні */
    for (pos = start; pos < end; pos += PAGE_SIZE, pages++) {
        
        /* Крок 1: Отруєння пам'яті (за наявності прапорця) */
        if (poison)
            memset(pos, POISON_FREE_INITMEM, PAGE_SIZE);

        /* Крок 2: Фізичне звільнення сторінки */
        free_reserved_page(virt_to_page(pos));
    }

    if (pages && s)
        pr_info("Freeing %s: %ldK\n", s, pages << (PAGE_SHIFT - 10));

    return pages;
}
