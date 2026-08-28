static int pl011_probe(struct platform_device *pdev)
{
    struct device_node *np = pdev->dev.of_node;
    struct resource res;
    u32 bus_width;
    int irq;

    /* Вилучення фізичних адрес MMIO з властивості reg */
    if (of_address_to_resource(np, 0, &res)) {
        dev_err(&pdev->dev, "Failed to get MMIO resource\n");
        return -EINVAL;
    }

    /* Вилучення системного номера переривання з interrupts */
    irq = irq_of_parse_and_map(np, 0);

    /* Зчитування опціональної числової властивості */
    if (of_property_read_u32(np, "reg-io-width", &bus_width))
        bus_width = 1; /* значення за замовчуванням */

    /* Відображення MMIO регістрів у віртуальний простір ядра */
    void __iomap *base = devm_ioremap_resource(&pdev->dev, &res);

    return 0;
}
