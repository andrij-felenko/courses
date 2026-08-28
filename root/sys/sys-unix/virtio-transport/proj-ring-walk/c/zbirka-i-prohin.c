#define ROUNDS 100000u

static void driver_loop(struct driver *d, unsigned rounds)
{
        unsigned sent = 0, got = 0;

        while (got < rounds) {
                while (sent < rounds && d->num_free >= 3) {
                        uint64_t slot = POOL_OFF + (uint64_t)d->free_head * SLOT;
                        struct req_hdr *h = (struct req_hdr *)(d->s.base + slot);
                        h->seq  = sent;
                        h->fill = 0x30u + (sent % 10u);

                        struct sg sg[3] = {
                                { slot,       (uint32_t)sizeof *h, 0 },  /* читає пристрій */
                                { slot + 64,  256,                 1 },  /* пише пристрій  */
                                { slot + 448, 1,                   1 },  /* байт статусу   */
                        };
                        if (vq_add(d, sg, 3) < 0) break;
                        sent++;
                }
                vq_kick(d);

                uint32_t len;
                while (vq_get(d, &len) >= 0)
                        got++;

                if (got == rounds)
                        break;
                if (sent == rounds || d->num_free < 3)   /* слати більше нічого — чекаємо */
                        driver_wait(d);
        }
}

int main(void)
{
        void *base = mmap(NULL, REGION, PROT_READ | PROT_WRITE,
                          MAP_SHARED | MAP_ANONYMOUS, -1, 0);
        if (base == MAP_FAILED) die("mmap");
        memset(base, 0, REGION);

        int kickfd = eventfd(0, 0), callfd = eventfd(0, 0);
        if (kickfd < 0 || callfd < 0) die("eventfd");

        static struct driver drv;
        static struct device dev;
        vring_place(&drv.s, base); drv.s.kickfd = kickfd; drv.s.callfd = callfd;
        vring_place(&dev.s, base); dev.s.kickfd = kickfd; dev.s.callfd = callfd;
        free_list_init(&drv);
        dev.todo = ROUNDS;

        pthread_t th;
        if (pthread_create(&th, NULL, device_thread, &dev) != 0) die("pthread_create");
        driver_loop(&drv, ROUNDS);
        pthread_join(th, NULL);
        puts("усі запити пройшли чергу й повернулися");
        return 0;
}
