void __iomem *ioremap(phys_addr_t offset, size_t size);
void __iomem *ioremap_wc(phys_addr_t offset, size_t size);
void __iomem *ioremap_wt(phys_addr_t offset, size_t size);
void __iomem *ioremap_np(phys_addr_t offset, size_t size);
void __iomem *ioremap_uc(phys_addr_t offset, size_t size);
void          iounmap(volatile void __iomem *addr);

void *memremap(resource_size_t offset, size_t size, unsigned long flags);
void  memunmap(void *addr);

/* з прив'язкою до життя пристрою — знімаються самі */
void __iomem *devm_ioremap(struct device *dev, resource_size_t offset,
                           resource_size_t size);
void __iomem *devm_ioremap_resource(struct device *dev, const struct resource *res);
void __iomem *devm_platform_ioremap_resource(struct platform_device *pdev,
                                             unsigned int index);
