struct device { struct side s; uint16_t last_avail; unsigned served, todo; };
struct req_hdr { uint32_t seq, fill; };

static uint32_t serve_chain(struct device *v, uint16_t head)
{
        struct req_hdr hdr = { 0, 0 };
        uint32_t written = 0;
        unsigned nwr = 0, hops = 0;
        uint16_t i = head;

        for (;;) {
                if (i >= QSZ) die("номер ланки поза таблицею");
                struct vring_desc *dsc = &v->s.desc[i];
                uint32_t len = dsc->len;
                void *buf = xlate(&v->s, dsc->addr, len);
                if (!buf) die("буфер поза ділянкою");

                if (!(dsc->flags & DESC_F_WRITE)) {
                        if (len == sizeof hdr) memcpy(&hdr, buf, sizeof hdr);
                } else if (nwr++ == 0) {
                        memset(buf, (int)hdr.fill, len);   /* тіло відповіді */
                        written += len;
                } else {
                        *(uint8_t *)buf = 0;               /* байт статусу: гаразд */
                        written += 1;
                }

                if (!(dsc->flags & DESC_F_NEXT)) break;
                i = dsc->next;
                if (++hops >= QSZ) die("ланцюг довший за таблицю");
        }
        return written;
}

static void *device_thread(void *arg)
{
        struct device *v = arg;

        while (v->served < v->todo) {
                uint16_t avail_idx = atomic_load_explicit(&v->s.avail->idx,
                                                          memory_order_relaxed);
                if (v->last_avail == avail_idx) {           /* порожньо — замовляємо кік */
                        atomic_store_explicit(&v->s.used->avail_event, v->last_avail,
                                              memory_order_relaxed);
                        atomic_thread_fence(memory_order_seq_cst);
                        if (atomic_load_explicit(&v->s.avail->idx,
                                                 memory_order_relaxed) == v->last_avail) {
                                uint64_t ev;
                                if (read(v->s.kickfd, &ev, sizeof ev) != sizeof ev)
                                        die("kickfd");
                        }
                        continue;
                }

                atomic_thread_fence(memory_order_acquire);  /* idx прочитано — ТЕПЕР ланки */

                uint16_t head = atomic_load_explicit(&v->s.avail->ring[v->last_avail & QMASK],
                                                     memory_order_relaxed);
                v->last_avail++;
                uint32_t written = serve_chain(v, head);

                uint16_t ui = atomic_load_explicit(&v->s.used->idx, memory_order_relaxed);
                v->s.used->ring[ui & QMASK].id  = head;     /* ГОЛОВА ланцюга, не позиція */
                v->s.used->ring[ui & QMASK].len = written;
                atomic_thread_fence(memory_order_release);
                atomic_store_explicit(&v->s.used->idx, (uint16_t)(ui + 1u),
                                      memory_order_relaxed);
                v->served++;

                atomic_thread_fence(memory_order_seq_cst);
                uint16_t ev_idx = atomic_load_explicit(&v->s.avail->used_event,
                                                       memory_order_relaxed);
                if (vring_need_event(ev_idx, (uint16_t)(ui + 1u), ui)) {
                        uint64_t one = 1;
                        if (write(v->s.callfd, &one, sizeof one) < 0) die("callfd");
                }
        }
        return NULL;
}
