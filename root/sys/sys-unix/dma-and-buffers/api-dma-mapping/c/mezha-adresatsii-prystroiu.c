int dma_set_mask(struct device *dev, u64 mask);            /* потокові відображення */
int dma_set_coherent_mask(struct device *dev, u64 mask);   /* узгоджені виділення */
u64 dma_get_required_mask(struct device *dev);             /* яка маска покрила б усю пам'ять */

static inline int dma_set_mask_and_coherent(struct device *dev, u64 mask)
{
        int rc = dma_set_mask(dev, mask);
        if (rc == 0)
                dma_set_coherent_mask(dev, mask);
        return rc;
}
