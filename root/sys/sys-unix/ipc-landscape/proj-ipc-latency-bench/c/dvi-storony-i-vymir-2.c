static int cmp_u64(const void *a, const void *b)
{
        uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b;
        return (x > y) - (x < y);
}

static double at(uint64_t *v, size_t n, double p)       /* нс → мкс */
{
        return v[(size_t)(p * (double)(n - 1) + 0.5)] / 1000.0;
}

static void drop(struct duplex d)
{
        close(d.tx);
        if (d.rx != d.tx) close(d.rx);
}

int main(int argc, char **argv)
{
        const char *what = argc > 1 ? argv[1] : "pipe";
        uint64_t iters   = argc > 3 ? strtoull(argv[3], NULL, 10) : 200000;
        int cpu_a = argc > 4 ? atoi(argv[4]) : 2;
        int cpu_b = argc > 5 ? atoi(argv[5]) : 4;
        uint64_t warm = iters / 10 < 1000 ? 1000 : iters / 10;
        struct duplex A, B;
        unsigned char *buf = NULL;
        pid_t kid;

        N = argc > 2 ? strtoul(argv[2], NULL, 10) : 64;
        MODE = !strcmp(what, "seqpacket") ? M_SEQ :
               !strcmp(what, "shm")       ? M_SHM :
               !strcmp(what, "spin")      ? M_SPIN : M_PIPE;

        SAMP = malloc(iters * sizeof *SAMP);
        if (MODE == M_SHM || MODE == M_SPIN) {
                /* MAP_SHARED|MAP_ANONYMOUS переживає fork; для чужих
                   процесів те саме дає shm_open плюс mmap. */
                CH = mmap(NULL, sizeof *CH + N, PROT_READ | PROT_WRITE,
                          MAP_SHARED | MAP_ANONYMOUS, -1, 0);
                if (CH == MAP_FAILED) { perror("mmap"); return 1; }
        } else {
                int rc = (MODE == M_SEQ) ? open_socket_pair(&A, &B, N)
                                         : open_pipe_pair(&A, &B, N);
                if (rc != 0) { perror("канал або сокет"); return 1; }
                buf = malloc(N);
        }

        kid = fork();
        if (kid == 0) {
                pin(cpu_b);
                if (!CH) { drop(A); ME = B; }
                echo_side(buf, warm + iters);
                _exit(0);
        }
        pin(cpu_a);
        if (!CH) { drop(B); ME = A; }

        bench_side(buf, warm, iters);
        waitpid(kid, NULL, 0);

        qsort(SAMP, iters, sizeof *SAMP, cmp_u64);

        /* Пропускну здатність рахуємо теж із медіани, а не з середнього:
           хвости зсувають середнє й описували б не обмін, а витіснення. */
        double med = at(SAMP, iters, 0.5);              /* мкс на оберт */
        printf("%-10s %8zu Б   медіана %8.2f   p99 %8.2f   p99.9 %8.2f   "
               "мін %7.2f мкс   %6.2f ГБ/с\n",
               what, N, med, at(SAMP, iters, 0.99),
               at(SAMP, iters, 0.999), at(SAMP, iters, 0.0),
               2.0 * (double)N / (med * 1000.0));
        return 0;
}
