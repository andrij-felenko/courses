#define PAGE_SIZE  4096u
#define PAGE_MASK  (PAGE_SIZE - 1u)

// Адреса кадру, у який відображено сторінку page_vaddr (у житті — virt_to_phys(),
// або те, що поверне шар DMA-відображення разом із програмуванням IOMMU).
typedef uintptr_t (*page_phys_fn)(uintptr_t page_vaddr, void *ctx);

// Побудувати список ФІЗИЧНИХ сегментів із суцільного ВІРТУАЛЬНОГО буфера.
// store/cap — памʼять під сегменти (виклик — власник).
// Повертає кількість сегментів або -1, якщо не влізло в cap.
int sg_build(struct sg_list *sg, struct sg_seg *store, int cap,
             uintptr_t vaddr, size_t len,
             page_phys_fn page_phys, void *ctx)
{
    sg->seg = store;
    sg->n   = 0;

    uintptr_t v    = vaddr;
    size_t    left = len;

    while (left > 0) {
        size_t off   = (size_t)(v & PAGE_MASK);   // зсув усередині сторінки
        size_t chunk = PAGE_SIZE - off;           // скільки лишилось до кінця сторінки
        if (chunk > left) chunk = left;           // ...або до кінця буфера

        uintptr_t phys = page_phys(v - off, ctx) + off;

        // ЗЛИТТЯ: чи продовжує цей шматок попередній сегмент ФІЗИЧНО?
        if (sg->n > 0) {
            struct sg_seg *last = &store[sg->n - 1];
            if (last->addr + last->len == phys) {
                last->len += chunk;               // ростимо той самий сегмент
                v += chunk; left -= chunk;
                continue;                         // слот не потрібен
            }
        }

        if (sg->n == cap) return -1;              // стеля списку
        store[sg->n].addr = phys;
        store[sg->n].len  = chunk;
        sg->n++;
        v += chunk; left -= chunk;
    }
    return sg->n;
}
