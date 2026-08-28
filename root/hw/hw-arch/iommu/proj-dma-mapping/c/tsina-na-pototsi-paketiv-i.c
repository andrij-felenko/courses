/* Старт: замапити КОЖЕН буфер кільця РАЗ і тримати замапленим. */
for (i = 0; i < RING_N; i++) {
    buf[i] = kmalloc(BUF_SZ, GFP_KERNEL);
    dma[i] = dma_map_single(dev, buf[i], BUF_SZ, DMA_FROM_DEVICE);
    if (dma_mapping_error(dev, dma[i]))
        goto unwind;
    desc[i].addr = cpu_to_le64(dma[i]);   /* IOVA у дескриптор кільця */
}

/* Гарячий шлях: на кожен прийнятий пакет — БЕЗ map/unmap, лише sync. */
static void rx_one(int i)
{
    dma_sync_single_for_cpu(dev, dma[i], BUF_SZ, DMA_FROM_DEVICE); /* забрати собі */
    process_packet(buf[i], le32_to_cpu(desc[i].len));
    dma_sync_single_for_device(dev, dma[i], BUF_SZ, DMA_FROM_DEVICE); /* вернути карті */
    desc[i].status = cpu_to_le32(DESC_OWN_NIC);
}

/* Зупинка: зняти кожен буфер — тепер уже раз. */
for (i = 0; i < RING_N; i++)
    dma_unmap_single(dev, dma[i], BUF_SZ, DMA_FROM_DEVICE);
