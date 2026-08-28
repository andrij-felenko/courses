/* Витяг із логіки drivers/virtio/virtio_balloon.c */
static unsigned int fill_balloon(struct virtio_balloon *vb, size_t num)
{
    unsigned int num_allocated_pages = 0;

    while (num_allocated_pages < num) {
        /* Прапорці виділення: не спати довго, не шуміти в dmesg, не панікувати */
        struct page *page = alloc_pages(GFP_HIGHUSER | __GFP_NOWARN | 
                                        __GFP_NORETRY | __GFP_NOMEMALLOC, 0);
        if (!page) {
            /* Пам'ять гостя вичерпано — зупиняємо надування */
            break;
        }

        /* Ізолюємо сторінку від механізму компактизації ядра */
        balloon_page_enqueue(&vb->vb_dev_info, page);
        vb->pfns[vb->num_pfns++] = page_to_pfn(page);
        num_allocated_pages++;

        /* Буфер заповнено (256 сторінок = 1 МіБ) — скидаємо у віртчергу */
        if (vb->num_pfns == VIRTIO_BALLOON_ARRAY_PFNS_SIZE)
            tell_host(vb, vb->inflate_vq);
    }

    if (vb->num_pfns > 0)
        tell_host(vb, vb->inflate_vq);

    return num_allocated_pages;
}
