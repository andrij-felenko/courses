static int vdec_probe(struct platform_device *pdev)
{
        struct device *dev = &pdev->dev;
        struct vdec *v;
        int ret;

        v = devm_kzalloc(dev, sizeof(*v), GFP_KERNEL);
        if (!v)
                return -ENOMEM;
        v->dev = dev;
        mutex_init(&v->lock);

        /* Без цього рядка dev->cma_area лишиться порожнім, і виділення
           піде в загальну область — тихо й успішно, доки не почне падати. */
        ret = of_reserved_mem_device_init(dev);
        if (ret && ret != -ENODEV)              /* -ENODEV: memory-region у дереві немає */
                return dev_err_probe(dev, ret, "не вдалося взяти memory-region\n");

        /* Досяжність оголошують до першого виділення: розподільник
           мусить знати, у які фізичні адреси пристрій уміє дотягтися. */
        ret = dma_set_mask_and_coherent(dev, DMA_BIT_MASK(32));
        if (ret)
                return ret;

        v->misc.minor  = MISC_DYNAMIC_MINOR;
        v->misc.name   = "vdec";
        v->misc.fops   = &vdec_fops;
        v->misc.parent = dev;
        platform_set_drvdata(pdev, v);
        return misc_register(&v->misc);
}
