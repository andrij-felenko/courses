static struct resource myuart_resources[] = {
        {
                .start = 0xe0001000,
                .end   = 0xe0001fff,
                .flags = IORESOURCE_MEM,
        },
        {
                .start = 59,
                .end   = 59,
                .flags = IORESOURCE_IRQ,
        },
};

static struct platform_device myuart_device = {
        .name          = "myuart",
        .id            = 0,
        .resource      = myuart_resources,
        .num_resources = ARRAY_SIZE(myuart_resources),
};

/* десь у коді ініціалізації плати */
platform_device_register(&myuart_device);
