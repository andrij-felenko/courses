static int vdec_open(struct inode *ino, struct file *f)
{
        /* Ядро вже поклало сюди вказівник на miscdevice — від нього
           дістаємося свого стану, а далі підмінюємо на нього ж. */
        struct vdec *v = container_of(f->private_data, struct vdec, misc);
        int ret = 0;

        mutex_lock(&v->lock);
        if (!v->refs) {
                /* GFP_KERNEL тут обов'язковий: перенос мешканців області
                   спить, і без права спати CMA навіть не пробують.       */
                v->cpu = dma_alloc_attrs(v->dev, VDEC_BUF_SIZE, &v->dma,
                                         GFP_KERNEL, VDEC_ATTRS);
                if (!v->cpu) {
                        dev_warn(v->dev,
                                 "немає суцільних %u КіБ; подивіться maxchunk у /sys/kernel/debug/cma/\n",
                                 VDEC_BUF_SIZE >> 10);
                        ret = -ENOMEM;
                        goto out;
                }
        }
        v->refs++;
        f->private_data = v;
out:
        mutex_unlock(&v->lock);
        return ret;
}

static void vdec_put(struct vdec *v)
{
        mutex_lock(&v->lock);
        if (!--v->refs) {
                dma_free_attrs(v->dev, VDEC_BUF_SIZE, v->cpu, v->dma, VDEC_ATTRS);
                v->cpu = NULL;
        }
        mutex_unlock(&v->lock);
}
