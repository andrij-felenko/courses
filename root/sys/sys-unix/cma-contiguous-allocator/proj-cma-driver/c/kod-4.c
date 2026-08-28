static void vdec_vm_open(struct vm_area_struct *vma)
{
        struct vdec *v = vma->vm_private_data;

        mutex_lock(&v->lock);
        v->refs++;                              /* відображення пережило fork */
        mutex_unlock(&v->lock);
}

static void vdec_vm_close(struct vm_area_struct *vma) { vdec_put(vma->vm_private_data); }

static const struct vm_operations_struct vdec_vm_ops = {
        .open  = vdec_vm_open,
        .close = vdec_vm_close,
};

static int vdec_mmap(struct file *f, struct vm_area_struct *vma)
{
        struct vdec *v = f->private_data;
        int ret;

        mutex_lock(&v->lock);
        ret = dma_mmap_attrs(v->dev, vma, v->cpu, v->dma, VDEC_BUF_SIZE, VDEC_ATTRS);
        if (!ret) {
                v->refs++;                      /* відображення тримає буфер нарівні з fd */
                vma->vm_private_data = v;
                vma->vm_ops = &vdec_vm_ops;
        }
        mutex_unlock(&v->lock);
        return ret;
}

static int vdec_release(struct inode *ino, struct file *f)
{
        vdec_put(f->private_data);
        return 0;
}

static const struct file_operations vdec_fops = {
        .owner   = THIS_MODULE,
        .open    = vdec_open,
        .release = vdec_release,
        .mmap    = vdec_mmap,
};

static void vdec_remove(struct platform_device *pdev)
{
        struct vdec *v = platform_get_drvdata(pdev);

        misc_deregister(&v->misc);
        of_reserved_mem_device_release(&pdev->dev);
}

static const struct of_device_id vdec_of_match[] = {
        { .compatible = "acme,vdec" },
        { }
};
MODULE_DEVICE_TABLE(of, vdec_of_match);

static struct platform_driver vdec_driver = {
        .driver = { .name = "vdec", .of_match_table = vdec_of_match },
        .probe  = vdec_probe,
        .remove = vdec_remove,
};
module_platform_driver(vdec_driver);
MODULE_LICENSE("GPL");
