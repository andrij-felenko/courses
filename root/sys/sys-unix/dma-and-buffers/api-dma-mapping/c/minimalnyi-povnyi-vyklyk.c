/* один раз, при під'єднанні */
if (dma_set_mask_and_coherent(dev, DMA_BIT_MASK(64)))
        return -EIO;

/* на кожну передачу */
dma_addr_t da = dma_map_single(dev, buf, len, DMA_TO_DEVICE);
if (dma_mapping_error(dev, da))
        return -ENOMEM;

start_transfer(dev, da, len);           /* адресу — в регістр пристрою */
wait_for_completion(&done);             /* прокидається обробник переривання */

dma_unmap_single(dev, da, len, DMA_TO_DEVICE);   /* аргументи ті самі, що при map */
