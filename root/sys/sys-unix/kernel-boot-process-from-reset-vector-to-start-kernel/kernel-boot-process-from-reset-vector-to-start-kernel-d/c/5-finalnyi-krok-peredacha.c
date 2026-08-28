asmlinkage __visible void __init x86_64_start_kernel(char *realmode_data)
{
    /* 1. Очистити секцію BSS (Uninitialized Data) */
    memset(__bss_start, 0, __bss_stop - __bss_start);

    /* 2. Скопіювати boot_params із низької пам'яті у безпечну область ядра */
    copy_bootdata((char *)realmode_data);

    /* 3. Налаштувати ранню глобальну таблицю дескрипторів (GDT) та IDT */
    switch_to_new_gdt(0);

    /* 4. Передати керування в архітектурно-незалежну функцію start_kernel() */
    start_kernel();
}
