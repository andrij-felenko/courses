static int demo_mmap(struct file *f, struct vm_area_struct *vma)
{
    struct demo *d = f->private_data;    /* d->buf узято через vmalloc_user() */

    if (vma->vm_pgoff)                   /* зсув усередині буфера не підтримуємо */
        return -EINVAL;
    if (vma->vm_end - vma->vm_start > d->size)
        return -EINVAL;

    return remap_vmalloc_range(vma, d->buf, 0);
}
