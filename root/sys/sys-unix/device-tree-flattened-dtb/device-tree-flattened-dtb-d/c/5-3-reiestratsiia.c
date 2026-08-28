static const struct of_device_id pl011_dt_ids[] = {
    { .compatible = "arm,pl011", },
    { .compatible = "arm,primecell", },
    { /* sentinel */ }
};
MODULE_DEVICE_TABLE(of, pl011_dt_ids);

static struct platform_driver pl011_driver = {
    .probe  = pl011_probe,
    .remove = pl011_remove,
    .driver = {
        .name = "uart-pl011",
        .of_match_table = pl011_dt_ids,
    },
};
