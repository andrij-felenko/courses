static int my_framebuffer_mmap(struct file *filp, struct vm_area_struct *vma)
{
    unsigned long size = vma->vm_end - vma->vm_start;
    unsigned long pfn = my_dev->fb_phys_addr >> PAGE_SHIFT;

    /* 1. Забороняємо вивантаження в swap, розширення та включення в core dump */
    vm_flags_set(vma, VM_IO | VM_DONTEXPAND | VM_DONTDUMP);

    /* 2. Призначаємо сторінкам атрибут Write-Combining */
    vma->vm_page_prot = pgprot_writecombine(vma->vm_page_prot);

    /* 3. Будуємо записи таблиць сторінок процесу */
    if (remap_pfn_range(vma, vma->vm_start, pfn, size, vma->vm_page_prot))
        return -EAGAIN;

    return 0;
}
