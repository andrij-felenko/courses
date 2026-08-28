void free_initmem(void)
{
    /* Отримуємо числові значення фізичних адрес із глобальних символів лінкера */
    unsigned long start = (unsigned long)(&__init_begin);
    unsigned long end = (unsigned long)(&__init_end);

    /* 
     * Архітектурно-специфічний захист пам'яті: 
     * Переконуємося, що сторінки доступні для запису та читання (RW)
     * перед тим як віддати їх процесам користувача.
     */
    set_memory_rw(start, (end - start) >> PAGE_SHIFT);

    /* Викликаємо загальносистемну функцію звільнення зарезервованої пам'яті */
    free_initmem_default(POISON_FREE_INITMEM);

    /* Виводимо інформаційне повідомлення в лог ядра (dmesg) */
    printk(KERN_INFO "Freeing unused kernel image (initmem) memory: %luk freed\n",
           (end - start) >> 10);
}
