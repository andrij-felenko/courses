static int my_sdio_suspend(struct device *dev)
{
    struct sdio_func *func = dev_to_sdio_func(dev);
    mmc_pm_flag_t pm_flags = 0;

    /* Перевіряємо, чи підтримує хост збереження живлення слота */
    pm_flags = sdio_get_host_pm_caps(func);
    if (!(pm_flags & MMC_PM_KEEP_POWER))
        return -ENOTSUPP;

    /* Залишаємо живлення модуля та дозволяємо асинхронне пробудження по DAT1 */
    if (sdio_set_host_pm_flags(func, MMC_PM_KEEP_POWER | MMC_PM_WAKE_SDIO_IRQ))
        return -EBUSY;

    return 0;
}
