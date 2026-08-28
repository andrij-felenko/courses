void panic(const char *fmt, ...)
{
    /* 1. Вимкнення локальних переривань */
    local_irq_disable();
    
    /* 2. Блокування повторного входу в panic() */
    if (old_cpu != processing_cpu)
        smp_send_stop(); /* Зупинка всіх інших ядер CPU через NMI */
        
    /* 3. Логування текстової причини Паніки */
    pr_emerg("Kernel panic - not syncing: %s\n", buf);
    
    /* 4. Запуск Kdump, якщо налаштовано */
    crash_kexec(NULL);
    
    /* 5. Апаратне перезавантаження або вічний цикл зупинки */
    if (panic_timeout > 0)
        emergency_restart();
        
    while (1)
        mdelay(1);
}
