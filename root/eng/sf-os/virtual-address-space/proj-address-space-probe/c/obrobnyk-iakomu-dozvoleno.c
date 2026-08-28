static sigjmp_buf back;
static volatile sig_atomic_t repair;   /* 1 — полагодити сторінку й повернутися */

static void on_segv(int sig, siginfo_t *si, void *uc)
{
    (void) sig; (void) uc;

    /* stdio тут заборонено — складаємо рядок самі й віддаємо одним write */
    const char *tag = si->si_code == SEGV_ACCERR ? "  ACCERR @ 0x" :
                      si->si_code == SEGV_MAPERR ? "  MAPERR @ 0x" :
                                                   "  ?????? @ 0x";
    char out[40];
    int n = 0;
    while (tag[n]) { out[n] = tag[n]; n++; }
    unsigned long a = (unsigned long) si->si_addr;
    for (int sh = 44; sh >= 0; sh -= 4)          /* 12 шістнадцяткових цифр */
        out[n++] = "0123456789abcdef"[(a >> sh) & 0xf];
    out[n++] = '\n';
    ssize_t w = write(1, out, n); (void) w;

    if (repair) {
        /* повернути права саме тій сторінці — і вийти з обробника звичайно:
           апаратура повторить ту саму команду, і цього разу вона пройде */
        mprotect((void *) (a & ~(PAGE - 1)), PAGE, PROT_READ | PROT_WRITE);
        return;
    }
    siglongjmp(back, 1);
}

/* Одна проба: звернутися за адресою й вижити, хоч би що там було. */
static void probe(char *addr)
{
    if (sigsetjmp(back, 1) == 0) {          /* 1 — зберегти маску сигналів */
        volatile char c = *addr;
        printf("  читання пройшло: %d\n", (int) c);
    }
}
