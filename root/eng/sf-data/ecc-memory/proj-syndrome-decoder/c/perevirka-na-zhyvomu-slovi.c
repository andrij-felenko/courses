static word72 flip(word72 cw, unsigned p) { return cw ^ ((word72)1 << p); }

int main(void) {
    uint64_t data = 0xDEADBEEF12345678ULL;
    word72   code = ecc_encode(data);

    ecc_result a = ecc_decode(code);                       /* 0 помилок */
    ecc_result b = ecc_decode(flip(code, 40));             /* 1 биток: позиція 40 */
    ecc_result c = ecc_decode(flip(flip(code, 40), 9));    /* 2 битки: 40 і 9 */

    printf("ціле  : status=%d  data=%016llx  (%s)\n", a.status,
           (unsigned long long)a.data, a.data == data ? "збіг" : "РОЗБІЖНІСТЬ");
    printf("1 биток: status=%d  pos=%u  data=%016llx  (%s)\n", b.status, b.pos,
           (unsigned long long)b.data, b.data == data ? "збіг" : "РОЗБІЖНІСТЬ");
    printf("2 битки: status=%d  (виявлено подвійну — дані не довіряти)\n", c.status);
    return 0;
}
