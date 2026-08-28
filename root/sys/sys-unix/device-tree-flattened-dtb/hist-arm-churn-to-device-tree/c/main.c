/* Типовий C-код з епохи board-файлів ядра Linux 2.6 (до 2011 року) */
static struct resource i2c_resources[] = {
    [0] = {
        .start = 0x48070000,
        .end   = 0x48070000 + 0x75,
        .flags = IORESOURCE_MEM,
    },
    [1] = {
        .start = 56, /* IRQ number */
        .end   = 56,
        .flags = IORESOURCE_IRQ,
    },
};

static struct platform_device omap_i2c_device1 = {
    .name          = "omap_i2c",
    .id            = 1,
    .num_resources = ARRAY_SIZE(i2c_resources),
    .resource      = i2c_resources,
};
