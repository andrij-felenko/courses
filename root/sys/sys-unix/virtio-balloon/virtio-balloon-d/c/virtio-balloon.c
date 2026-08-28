/* Спрощена логіка hw/virtio/virtio-balloon.c у QEMU */
static void virtio_balloon_handle_inflate(VirtIODevice *vdev, VirtQueue *vq)
{
    VirtQueueElement *elem;

    while ((elem = virtqueue_pop(vq, sizeof(VirtQueueElement)))) {
        size_t pfn_count = elem->out_sg[0].iov_len / sizeof(uint32_t);
        uint32_t *pfns = (uint32_t *)elem->out_sg[0].iov_base;

        for (size_t i = 0; i < pfn_count; i++) {
            /* 1. Обчислюємо гостьову фізичну адресу (GPA) */
            hwaddr gpa = (hwaddr)virtio_ldl_p(vdev, &pfns[i]) << VIRTIO_BALLOON_PFN_SHIFT;

            /* 2. Знаходимо MemoryRegionSection хоста за адресою GPA */
            MemoryRegionSection section = memory_region_find(get_system_memory(), gpa, 4096);
            if (!section.mr) continue;

            /* 3. Отримуємо віртуальну адресу хоста (HVA) всередині процесу QEMU */
            void *hva = qemu_map_ram_ptr(section.mr->ram_block, 
                                         section.offset_within_region);

            /* 4. Скидаємо фізичну пам'ять ядра хоста */
            qemu_madvise(hva, 4096, QEMU_MADV_DONTNEED);

            memory_region_unref(section.mr);
        }
        virtqueue_push(vq, elem, 0);
        virtio_notify(vdev, vq);
    }
}
