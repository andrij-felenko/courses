struct driver { struct side s; uint16_t free_head, num_free, last_used, kicked_idx; };

static void free_list_init(struct driver *d)
{
        for (uint16_t i = 0; i < QSZ; i++)
                d->s.desc[i].next = (uint16_t)(i + 1u);
        d->s.desc[QSZ - 1].next = NO_LINK;
        d->free_head = 0;
        d->num_free  = QSZ;
}

struct sg { uint64_t off; uint32_t len; int device_writes; };

static int vq_add(struct driver *d, const struct sg *sg, unsigned n)
{
        if (n == 0 || d->num_free < n)
                return -1;                    /* ланок немає — спершу заберіть відповіді */

        uint16_t head = d->free_head, i = head;
        for (unsigned k = 0; k < n; k++) {
                struct vring_desc *dsc = &d->s.desc[i];
                dsc->addr  = sg[k].off;
                dsc->len   = sg[k].len;
                dsc->flags = (uint16_t)((sg[k].device_writes ? DESC_F_WRITE : 0u)
                                      | (k + 1u < n ? DESC_F_NEXT : 0u));
                i = dsc->next;                /* далі списком вільних */
        }
        d->free_head = i;
        d->num_free  = (uint16_t)(d->num_free - n);

        uint16_t ai = atomic_load_explicit(&d->s.avail->idx, memory_order_relaxed);
        atomic_store_explicit(&d->s.avail->ring[ai & QMASK], head, memory_order_relaxed);

        atomic_thread_fence(memory_order_release);   /* ланки — РАНІШЕ за новий idx */
        atomic_store_explicit(&d->s.avail->idx, (uint16_t)(ai + 1u), memory_order_relaxed);
        return head;
}

static int vring_need_event(uint16_t event_idx, uint16_t new_idx, uint16_t old)
{
        return (uint16_t)(new_idx - event_idx - 1u) < (uint16_t)(new_idx - old);
}

static void vq_kick(struct driver *d)
{
        uint16_t new_idx = atomic_load_explicit(&d->s.avail->idx, memory_order_relaxed);

        atomic_thread_fence(memory_order_seq_cst);   /* наш запис — до чужого читання */
        uint16_t event = atomic_load_explicit(&d->s.used->avail_event, memory_order_relaxed);

        uint16_t old = d->kicked_idx;
        d->kicked_idx = new_idx;
        if (vring_need_event(event, new_idx, old)) {
                uint64_t one = 1;
                if (write(d->s.kickfd, &one, sizeof one) < 0) die("kickfd");
        }
}
