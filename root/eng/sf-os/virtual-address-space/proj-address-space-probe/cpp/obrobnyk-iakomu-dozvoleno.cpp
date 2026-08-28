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
    auto a = reinterpret_cast<std::uintptr_t>(si->si_addr);
    for (int sh = 44; sh >= 0; sh -= 4)          /* 12 шістнадцяткових цифр */
        out[n++] = "0123456789abcdef"[(a >> sh) & 0xf];
    out[n++] = '\n';
    [[maybe_unused]] auto w = ::write(1, out, n);

    if (repair) {
        /* повернути права саме тій сторінці — і вийти з обробника звичайно */
        ::mprotect(reinterpret_cast<void*>(a & ~(PAGE - 1)), PAGE, PROT_READ | PROT_WRITE);
        return;
    }
    siglongjmp(back, 1);
}

static void probe(char *addr)
{
    if (sigsetjmp(back, 1) == 0) {          /* 1 — зберегти маску сигналів */
        volatile char c = *addr;
        std::cout << "  читання пройшло: " << static_cast<int>(c) << '\n';
    }
}
