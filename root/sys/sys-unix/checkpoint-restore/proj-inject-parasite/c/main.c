#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <signal.h>
#include <unistd.h>
#include <sys/ptrace.h>
#include <sys/wait.h>
#include <sys/uio.h>        /* struct iovec */
#include <sys/user.h>       /* struct user_regs_struct */
#include <sys/syscall.h>    /* SYS_getpid */
#include <elf.h>            /* NT_PRSTATUS */

/* Прочитати/записати ВЕСЬ набір регістрів. GETREGSET переносний між
   архітектурами: iovec каже, скільки байтів набору ми готові взяти. */
static int get_regs(pid_t pid, struct user_regs_struct *r) {
    struct iovec io = { .iov_base = r, .iov_len = sizeof(*r) };
    return ptrace(PTRACE_GETREGSET, pid, (void *)NT_PRSTATUS, &io);
}
static int set_regs(pid_t pid, struct user_regs_struct *r) {
    struct iovec io = { .iov_base = r, .iov_len = sizeof(*r) };
    return ptrace(PTRACE_SETREGSET, pid, (void *)NT_PRSTATUS, &io);
}

int main(int argc, char **argv) {
    if (argc != 2) { fprintf(stderr, "вжиток: %s <pid>\n", argv[0]); return 2; }
    pid_t pid = (pid_t)atoi(argv[1]);
    int status;

    /* 1. Приєднатися БЕЗ видимої зупинки. SEIZE не шле сигналу й не лишає
          на задачі стану «зупинена сигналом», який побачив би хтось інший. */
    if (ptrace(PTRACE_SEIZE, pid, 0, 0) == -1) { perror("PTRACE_SEIZE"); return 1; }
    printf("приєднано до %d через PTRACE_SEIZE\n", pid);

    /* 2. Зупинити окремою командою — теж без сигналу — і дочекатися стопу. */
    if (ptrace(PTRACE_INTERRUPT, pid, 0, 0) == -1) { perror("PTRACE_INTERRUPT"); return 1; }
    waitpid(pid, &status, 0);

    /* 3. Зберегти регістри: saved — недоторканний зліпок, work — робоча копія. */
    struct user_regs_struct saved, work;
    if (get_regs(pid, &saved) == -1) { perror("GETREGSET"); return 1; }
    work = saved;
    unsigned long long pc = saved.rip;   /* точка, куди підсунемо syscall */

    /* 4. Зберегти слово коду за лічильником і підмінити молодші 2 байти на
          інструкцію `syscall` (0f 05). PEEK/POKE ходять словом по 8 байтів;
          решту 6 байтів лишаємо як були. errno-протокол: -1 — легітимне
          значення даних, тому помилку впізнаємо лише за errno. */
    errno = 0;
    long orig = ptrace(PTRACE_PEEKTEXT, pid, (void *)pc, 0);
    if (orig == -1 && errno) { perror("PEEKTEXT"); return 1; }

    long patched = (orig & ~0xffffL) | 0x050f;   /* у пам'яті: байт 0f, потім 05 */
    if (ptrace(PTRACE_POKETEXT, pid, (void *)pc, (void *)patched) == -1) {
        perror("POKETEXT"); return 1;
    }
    printf("за rip=0x%llx підмінено 2 байти на syscall (0f 05)\n", pc);

    /* 5. Поставити регістри так, ніби задача сама викликає getpid():
          номер — у rax, лічильник — на нашу інструкцію. getpid не має
          ні аргументів, ні побічних дій — ідеальна безпечна проба. */
    work.rip = pc;
    work.rax = SYS_getpid;               /* 39 на x86-64 */
    if (set_regs(pid, &work) == -1) { perror("SETREGSET"); return 1; }

    /* 6. Виконати РІВНО одну інструкцію. syscall входить у ядро й повертається;
          single-step ставить пастку на поверненні в user mode. */
    if (ptrace(PTRACE_SINGLESTEP, pid, 0, 0) == -1) { perror("SINGLESTEP"); return 1; }
    waitpid(pid, &status, 0);
    if (!WIFSTOPPED(status) || WSTOPSIG(status) != SIGTRAP) {
        /* Не наша пастка, а сигнал жертві. Реальний інструмент запам'ятав би
           сигнал, дозволив крок ще раз і повторив; тут просто чесно виходимо. */
        fprintf(stderr, "крок перервано сигналом %d\n", WSTOPSIG(status));
        set_regs(pid, &saved);
        ptrace(PTRACE_POKETEXT, pid, (void *)pc, (void *)orig);
        ptrace(PTRACE_DETACH, pid, 0, 0);
        return 1;
    }

    /* 7. Результат — у rax, як велить x86-64 ABI. */
    if (get_regs(pid, &work) == -1) { perror("GETREGSET"); return 1; }
    long long ret = (long long)work.rax;
    printf("getpid() у контексті жертви повернув %lld\n", ret);

    /* 8. Повернути ВСЕ точно як було: спершу байти коду, тоді регістри. */
    if (ptrace(PTRACE_POKETEXT, pid, (void *)pc, (void *)orig) == -1) { perror("restore code"); return 1; }
    if (set_regs(pid, &saved) == -1) { perror("restore regs"); return 1; }

    /* 9. Від'єднатися — задача біжить далі з тієї самої інструкції. */
    ptrace(PTRACE_DETACH, pid, 0, 0);
    printf("код і регістри повернено, від'єднано — жертва нічого не помітила\n");
    return 0;
}
