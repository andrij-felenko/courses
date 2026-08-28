/* ❌ ГРУБА ПОМИЛКА: Статичне виділення структури з kobject */
static struct my_device g_dev; // НЕ РОБИТИ ЦЬОГО!

/* ❌ ГРУБА ПОМИЛКА: Звільнення пам'яті безпосередньо в коді вивантаження */
static void __exit my_module_exit(void)
{
    kobject_del(&g_dev.kobj);
    kobject_put(&g_dev.kobj);
    // Якщо тут викликати kfree() або якщо g_dev статична — ядро впаде в паніку!
}
