static size_t N;
static struct duplex ME;
static struct chan  *CH;
static uint64_t     *SAMP;

static void echo_side(unsigned char *buf, uint64_t rounds)
{
        for (uint64_t i = 1; i <= rounds; i++) {
                if (CH) {
                        await_val(&CH->to_b, (uint32_t)i);
                        sink += sum(CH->data, N);
                        fill(CH->data, N, i);
                        publish(&CH->to_a, (uint32_t)i);
                } else {
                        if (xfer_recv(ME.rx, buf, N)) return;
                        sink += sum(buf, N);
                        fill(buf, N, i);
                        if (xfer_send(ME.tx, buf, N)) return;
                }
        }
}

static void bench_side(unsigned char *buf, uint64_t warm, uint64_t iters)
{
        for (uint64_t i = 1; i <= warm + iters; i++) {
                uint64_t t0 = now_ns();

                if (CH) {
                        fill(CH->data, N, i);
                        publish(&CH->to_b, (uint32_t)i);
                        await_val(&CH->to_a, (uint32_t)i);
                        sink += sum(CH->data, N);
                } else {
                        fill(buf, N, i);
                        if (xfer_send(ME.tx, buf, N)) return;
                        if (xfer_recv(ME.rx, buf, N)) return;
                        sink += sum(buf, N);
                }

                if (i > warm)
                        SAMP[i - warm - 1] = now_ns() - t0;
        }
}
