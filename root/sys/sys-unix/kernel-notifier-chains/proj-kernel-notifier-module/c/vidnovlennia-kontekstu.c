struct my_device_priv {
    int device_id;
    void __iomem *io_base;
    struct mutex lock;
    struct notifier_block reboot_nb;    /* Вбудований блок сповіщення */
};

static int my_reboot_callback(struct notifier_block *nb,
                              unsigned long action,
                              void *data)
{
    /*
     * Отримуємо вказівник на структуру пристрою за адресою її внутрішнього поля reboot_nb.
     * Макрос обчислює зміщення поля reboot_nb відносно початку struct my_device_priv
     * і повертає коректну базову адресу об'єкта.
     */
    struct my_device_priv *priv = container_of(nb, struct my_device_priv, reboot_nb);

    pr_info("[my_device_%d] Зупинка пристрою перед вимкненням системи...\n",
            priv->device_id);

    /* Виконуємо операції з апаратурою */
    iowrite32(0, priv->io_base + 0x04);

    return NOTIFY_OK;
}
