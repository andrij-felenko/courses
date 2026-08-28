// прочитати рівно need байтів у buf (TCP може віддавати частинами)
static int recv_exact(int sock, uint8_t *buf, int need) {
    int got = 0;
    while (got < need) {
        int n = recv(sock, buf + got, need - got, 0);
        if (n <= 0) return n;     // 0 — інший бік закрив; <0 — помилка
        got += n;                 // докладаємо, доки не зберемо все
    }
    return got;
}
