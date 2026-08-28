/* Алгоритм роботи функції panic() у ядрі Linux */
void panic(const char *fmt, ...)
{
    // 1. Вимкнення переривань на локальному CPU
    local_irq_disable();
    
    // 2. Надсилання NMI іншим CPU для збереження їхніх регістрів
    crash_smp_send_stop();
    
    // 3. Негайне виконання kexec у Crash Kernel
    crash_kexec(NULL);
    
    // 4. Запасний нескінченний цикл, якщо kdump не налаштований
    for (;;) ;
}
