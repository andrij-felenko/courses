/* Заголовки старої системи можуть не знати номера. Номер СВІЙ на кожній
   архітектурі: на mips до нього ще додається 4000 (o32), 5000 (n64)
   або 6000 (n32) — звіряйтеся з таблицею своєї, не переписуйте наосліп. */
#ifndef __NR_openat2
#  if defined(__x86_64__) || defined(__i386__) || \
      defined(__aarch64__) || defined(__riscv)
#    define __NR_openat2 437
#  endif
#endif

static int probe_openat2(void)
{
#ifdef __NR_openat2
    /* Дескриптора -1 не існує, а розмір 0 менший за будь-яку відому версію
       struct open_how — ядро, яке знає виклик, відкине це з EINVAL, ще
       нічого не прочитавши з нашої пам'яті й нічого не відкривши. */
    long r = syscall(__NR_openat2, -1, "", (void *) 0, (size_t) 0);
    return !(r == -1 && errno == ENOSYS);
#else
    return 0;
#endif
}

static int slot_openat2;
int have_openat2(void) { return probe_once(&slot_openat2, probe_openat2); }
