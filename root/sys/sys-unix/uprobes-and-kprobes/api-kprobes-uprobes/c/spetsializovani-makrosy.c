/* Автоматичне розпакування аргументів функції ядра */
SEC("kprobe/do_sys_openat2")
int BPF_KPROBE(trace_openat2, int dfd, const char *filename, struct open_how *how) {
    /* Доступ до аргументів dfd, filename, how здійснюється як у звичайній C-функції */
    return 0;
}

/* Отримання результату повернення з kretprobe */
SEC("kretprobe/do_sys_openat2")
int BPF_KRETPROBE(trace_openat2_ret, int ret) {
    /* ret містить значення RAX / retval */
    return 0;
}
