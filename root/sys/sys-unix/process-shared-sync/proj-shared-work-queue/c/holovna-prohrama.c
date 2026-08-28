int main(int argc, char **argv)
{
    int created; struct wq *q = wq_attach(&created);
    const char *role = argc > 1 ? argv[1] : "";

    if (!strcmp(role, "producer")) {
        long die_at = (argc > 3 && !strcmp(argv[2], "--die-at")) ? atol(argv[3]) : -1;
        for (long n = 1; n <= 10; n++) {
            char msg[WQ_PAYLOAD];
            int k = snprintf(msg, sizeof msg, "задача №%ld", n);
            if (wq_push(q, msg, (uint32_t)k + 1, n == die_at) == 0)
                printf("виробник: уклав %s\n", msg);
            usleep(200000);
        }
    } else if (!strcmp(role, "consumer")) {
        for (;;) {
            char buf[WQ_PAYLOAD]; uint32_t len;
            if (wq_pop(q, buf, &len, 2000) == 0) printf("споживач: узяв %s\n", buf);
            else                                 printf("споживач: дві секунди тиші\n");
        }
    } else { fprintf(stderr, "вжиток: %s producer|consumer [--die-at N]\n", argv[0]); return 1; }
    return 0;
}
