void __iomem *ioremap(phys_addr_t offset, size_t size);
void          iounmap(volatile void __iomem *addr);

void __iomem *devm_ioremap(struct device *dev, resource_size_t offset,
                           resource_size_t size);
void __iomem *devm_ioremap_resource(struct device *dev,
                                    const struct resource *res);
void __iomem *devm_platform_ioremap_resource(struct platform_device *pdev,
                                             unsigned int index);
void __iomem *devm_platform_ioremap_resource_byname(struct platform_device *pdev,
                                                    const char *name);
void __iomem *devm_platform_get_and_ioremap_resource(struct platform_device *pdev,
                                                     unsigned int index,
                                                     struct resource **res);
void __iomem *devm_of_iomap(struct device *dev, struct device_node *node,
                            int index, resource_size_t *size);
void __iomem *of_iomap(struct device_node *np, int index);

void __iomem *pci_iomap(struct pci_dev *dev, int bar, unsigned long max);
void          pci_iounmap(struct pci_dev *dev, void __iomem *addr);
