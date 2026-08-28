static void free_chain(struct driver *d, uint16_t head)
{
        uint16_t i = head, n = 1;
        while (d->s.desc[i].flags & DESC_F_NEXT) {
                i = d->s.desc[i].next;
                if (i >= QSZ || ++n > QSZ) die("зіпсований ланцюг");
        }
        d->s.desc[i].next = d->free_head;     /* хвіст чіпляємо до списку вільних */
        d->free_head = head;
        d->num_free  = (uint16_t)(d->num_free + n);
}

static int vq_get(struct driver *d, uint32_t *len_out)
{
        uint16_t ui = atomic_load_explicit(&d->s.used->idx, memory_order_relaxed);
        if (d->last_used == ui)
                return -1;                    /* нічого нового */

        atomic_thread_fence(memory_order_acquire);   /* idx прочитано — ТЕПЕР елемент */

        struct vring_used_elem *e = &d->s.used->ring[d->last_used & QMASK];
        uint32_t id = e->id;
        *len_out = e->len;
        d->last_used++;

        if (id >= QSZ) die("пристрій повернув неіснуючу ланку");
        free_chain(d, (uint16_t)id);
        return (int)id;
}

static void driver_wait(struct driver *d)
{
        atomic_store_explicit(&d->s.avail->used_event, d->last_used, memory_order_relaxed);
        atomic_thread_fence(memory_order_seq_cst);
        if (atomic_load_explicit(&d->s.used->idx, memory_order_relaxed) != d->last_used)
                return;                       /* поки писали позначку — уже приїхало */
        uint64_t ev;
        if (read(d->s.callfd, &ev, sizeof ev) != sizeof ev) die("callfd");
}
