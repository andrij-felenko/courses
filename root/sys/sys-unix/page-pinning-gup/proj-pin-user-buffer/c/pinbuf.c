/* pinbuf.c — модуль ядра */
#include <linux/module.h>
#include <linux/miscdevice.h>
#include <linux/fs.h>
#include <linux/mm.h>
#include <linux/highmem.h>
#include <linux/io.h>
#include <linux/slab.h>
#include <linux/uaccess.h>
#include <linux/overflow.h>
#include "pinbuf.h"

#define PINBUF_MAX_PAGES 256          /* 1 МіБ за виклик — стеля навмисна */

/* Сегмент — суцільний ланцюг кадрів, який пристрій узяв би одним махом. */
struct pinbuf_seg { phys_addr_t phys; size_t len; };

static long pinbuf_xfer(void __user *uarg)
{
        struct pinbuf_req r;
        struct page **pages;
        struct pinbuf_seg *segs;
        unsigned long start, offset, span;
        int nr_pages, pinned, nseg = 0, i;
        size_t left;
        u64 sum = 0;
        long ret;

        if (copy_from_user(&r, uarg, sizeof(r)))
                return -EFAULT;
        if (r.sum || r.pages || r.segs)   /* поля ядра мусять прийти нулями */
                return -EINVAL;
        if (r.len == 0)
                return -EINVAL;

        /* 1. Байти → сторінки, від початку першої сторінки, а не від addr. */
        start  = (unsigned long)r.addr & PAGE_MASK;
        offset = (unsigned long)r.addr & ~PAGE_MASK;
        if (check_add_overflow(offset, (unsigned long)r.len, &span))
                return -EINVAL;
        if (DIV_ROUND_UP(span, PAGE_SIZE) > PINBUF_MAX_PAGES)
                return -EINVAL;
        nr_pages = DIV_ROUND_UP(span, PAGE_SIZE);

        pages = kvmalloc_array(nr_pages, sizeof(*pages), GFP_KERNEL);
        if (!pages)
                return -ENOMEM;
        segs = kvmalloc_array(nr_pages, sizeof(*segs), GFP_KERNEL);
        if (!segs) {
                kvfree(pages);
                return -ENOMEM;
        }

        /* 2. Закріплення. Може заснути: сторінок під адресою може ще не бути. */
        pinned = pin_user_pages_fast(start, nr_pages, FOLL_WRITE, pages);
        if (pinned < 0) {
                ret = pinned;
                goto out_free;
        }
        if (pinned < nr_pages) {
                unpin_user_pages(pages, pinned);  /* не писали — не бруднимо */
                ret = -EFAULT;
                goto out_free;
        }

        /* 3. Таблиця сегментів: сусідні за номером кадру сторінки зливаються. */
        left = r.len;
        for (i = 0; i < pinned; i++) {
                size_t off = i ? 0 : offset;
                size_t n   = min_t(size_t, left, PAGE_SIZE - off);

                if (nseg && page_to_pfn(pages[i]) == page_to_pfn(pages[i - 1]) + 1)
                        segs[nseg - 1].len += n;
                else {
                        segs[nseg].phys = page_to_phys(pages[i]) + off;
                        segs[nseg].len  = n;
                        nseg++;
                }
                left -= n;
        }

        /* 4. Тут у справжньому драйвері були б dma_map_sgtable() і запуск
         *    передавання. Пристрою немає — робимо те саме процесором.     */
        left = r.len;
        for (i = 0; i < pinned; i++) {
                size_t off = i ? 0 : offset;
                size_t n   = min_t(size_t, left, PAGE_SIZE - off);
                u8 *va = kmap_local_page(pages[i]);
                size_t k;

                for (k = 0; k < n; k++)
                        sum += va[off + k];
                va[off] ^= 0xff;          /* видима зміна — задля FOLL_WRITE */
                kunmap_local(va);
                left -= n;
        }

        r.sum   = sum;
        r.pages = pinned;
        r.segs  = nseg;
        ret = copy_to_user(uarg, &r, sizeof(r)) ? -EFAULT : 0;

        /* 5. Скільки закріпили — стільки й відпустили; true, бо справді писали. */
        unpin_user_pages_dirty_lock(pages, pinned, true);
out_free:
        kvfree(segs);
        kvfree(pages);
        return ret;
}

static long pinbuf_ioctl(struct file *f, unsigned int cmd, unsigned long arg)
{
        if (cmd != PINBUF_XFER)
                return -ENOTTY;
        return pinbuf_xfer((void __user *)arg);
}

static const struct file_operations pinbuf_fops = {
        .owner          = THIS_MODULE,
        .unlocked_ioctl = pinbuf_ioctl,
        .compat_ioctl   = compat_ptr_ioctl,
};

static struct miscdevice pinbuf_misc = {
        .minor = MISC_DYNAMIC_MINOR,
        .name  = "pinbuf",
        .fops  = &pinbuf_fops,
        .mode  = 0600,
};
module_misc_device(pinbuf_misc);

MODULE_DESCRIPTION("Закріплення буфера користувача через pin_user_pages_fast");
MODULE_LICENSE("GPL");
