struct platform_driver {
        int  (*probe)(struct platform_device *);
        void (*remove)(struct platform_device *);
        void (*shutdown)(struct platform_device *);
        int  (*suspend)(struct platform_device *, pm_message_t state);
        int  (*resume)(struct platform_device *);
        struct device_driver driver;
        const struct platform_device_id *id_table;
        bool prevent_deferred_probe;
        bool driver_managed_dma;
};
