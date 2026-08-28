static int custom_cache_trigger = 0;

static int custom_trigger_handler(const struct ctl_table *table, int write,
                                  void *buffer, size_t *lenp, loff_t *ppos)
{
    int old_val = custom_cache_trigger;
    int ret;

    /* 1. Делегуємо базову обробку цілого числа стандартній функції */
    ret = proc_dointvec(table, write, buffer, lenp, ppos);
    if (ret || !write)
        return ret;

    /* 2. Виконуємо реакцію на зміну значення */
    if (custom_cache_trigger != old_val) {
        pr_info("sysctl_demo: значення змінилося з %d на %d\n", old_val, custom_cache_trigger);
        
        if (custom_cache_trigger == 1) {
            pr_info("sysctl_demo: тригер активовано, виконуємо скидання внутрішнього кешу...\n");
            /* Код очищення ресурсів ядра */
            custom_cache_trigger = 0; /* Автоматично скидаємо прапорець */
        }
    }

    return 0;
}
